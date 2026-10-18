"""Small numpy-only mesh toolkit: polygon triangulation (ear clipping with holes),
extrusion, star-shaped extrusions, cylinders, boxes, torus, STL/3MF export, checks."""
import numpy as np, struct, zipfile, math

# ---------------------------------------------------------------- 2D helpers
def area2(p):
    x, y = p[:, 0], p[:, 1]
    return np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def ccw(p):  return p if area2(p) > 0 else p[::-1]
def cw(p):   return p if area2(p) < 0 else p[::-1]

def circle(cx, cy, r, n=48, start=0.0):
    a = start + np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[cx + r * np.cos(a), cy + r * np.sin(a)]

def rounded_rect(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a0 in [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
        for a in np.linspace(math.radians(a0), math.radians(a0 + 90), n):
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts)

def seg_intersect(p, q, A, B):
    """Does segment p-q properly intersect any segment A[i]-B[i]? (vectorised)"""
    def orient(a, b, c):
        return (b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (b[..., 1] - a[..., 1]) * (c[..., 0] - a[..., 0])
    d1 = orient(A, B, p); d2 = orient(A, B, q); d3 = orient(p, q, A); d4 = orient(p, q, B)
    hit = (d1 * d2 < -1e-12) & (d3 * d4 < -1e-12)
    return hit.any()

def bridge_holes(outer, holes):
    """Merge holes into the outer ring with zero-width bridges (earcut-style)."""
    poly = [tuple(v) for v in ccw(np.asarray(outer, float))]
    holes = [cw(np.asarray(h, float)) for h in holes]
    holes.sort(key=lambda h: -h[:, 0].max())
    all_rings = [np.array(poly)] + holes
    for h in holes:
        i_m = int(np.argmax(h[:, 0])); M = h[i_m]
        P = np.array(poly)
        # all edges currently present (merged polygon + remaining holes)
        edgesA, edgesB = [], []
        for ring in [P] + [hh for hh in holes]:
            edgesA.append(ring); edgesB.append(np.roll(ring, -1, axis=0))
        A = np.vstack(edgesA); Bv = np.vstack(edgesB)
        order = np.argsort(np.hypot(P[:, 0] - M[0], P[:, 1] - M[1]))
        chosen = None
        for j in order:
            V = P[j]
            if np.allclose(V, M): continue
            # exclude edges touching V or M (shared endpoints are fine)
            mask = ~(np.all(np.isclose(A, V), axis=1) | np.all(np.isclose(Bv, V), axis=1) |
                     np.all(np.isclose(A, M), axis=1) | np.all(np.isclose(Bv, M), axis=1))
            if not seg_intersect(M, V, A[mask], Bv[mask]):
                chosen = j; break
        if chosen is None: raise RuntimeError('no bridge found')
        hole_seq = [tuple(v) for v in np.roll(h, -i_m, axis=0)] + [tuple(M)]
        poly = poly[:chosen + 1] + hole_seq + [poly[chosen]] + poly[chosen + 1:]
    return np.array(poly)

def earclip(poly):
    """Triangulate a simple (possibly bridged) CCW polygon. Returns index triples into poly."""
    P = np.asarray(poly, float); n = len(P)
    prv = np.roll(np.arange(n), 1); nxt = np.roll(np.arange(n), -1)
    active = np.ones(n, bool); count = n; tris = []; i = 0; fails = 0
    def is_ear(a, b, c, strict=True):
        A, B, C = P[a], P[b], P[c]
        cr = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
        if cr <= (1e-12 if strict else -1e-9): return False
        idx = np.nonzero(active)[0]
        idx = idx[(idx != a) & (idx != b) & (idx != c)]
        o = P[idx]
        if not len(o): return True
        dup = (np.all(np.abs(o - A) < 1e-9, 1) | np.all(np.abs(o - B) < 1e-9, 1) | np.all(np.abs(o - C) < 1e-9, 1))
        o = o[~dup]
        if not len(o): return True
        d1 = (B[0] - A[0]) * (o[:, 1] - A[1]) - (B[1] - A[1]) * (o[:, 0] - A[0])
        d2 = (C[0] - B[0]) * (o[:, 1] - B[1]) - (C[1] - B[1]) * (o[:, 0] - B[0])
        d3 = (A[0] - C[0]) * (o[:, 1] - C[1]) - (A[1] - C[1]) * (o[:, 0] - C[0])
        return not ((d1 >= -1e-12) & (d2 >= -1e-12) & (d3 >= -1e-12)).any()
    strict = True
    while count > 3:
        a, c = prv[i], nxt[i]
        if is_ear(a, i, c, strict):
            tris.append((a, i, c)); nxt[a] = c; prv[c] = a; active[i] = False; count -= 1
            i = a; fails = 0; strict = True
        else:
            i = c; fails += 1
            if fails > count:
                if not strict: raise RuntimeError(f'earclip failed with {count} vertices left')
                strict = False; fails = 0
    rest = np.nonzero(active)[0]
    a = rest[0]; tris.append((prv[nxt[a]], nxt[a], nxt[nxt[a]]) if False else (a, nxt[a], nxt[nxt[a]]))
    return np.array(tris)

# ---------------------------------------------------------------- 3D meshes
class Mesh:
    def __init__(self, v, f):
        self.v = np.asarray(v, float); self.f = np.asarray(f, int)
    def copy(self): return Mesh(self.v.copy(), self.f.copy())
    def translate(self, d): m = self.copy(); m.v += np.asarray(d, float); return m
    def transform(self, R, t=(0, 0, 0)): m = self.copy(); m.v = m.v @ np.asarray(R).T + np.asarray(t); return m
    def bounds(self): return self.v.min(0), self.v.max(0)

def concat(meshes):
    vs, fs, off = [], [], 0
    for m in meshes:
        vs.append(m.v); fs.append(m.f + off); off += len(m.v)
    return Mesh(np.vstack(vs), np.vstack(fs))

def rot_x(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def rot_y(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rot_z(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def _walls(ring_idx_bottom, ring_idx_top, outward_ccw=True):
    f = []
    n = len(ring_idx_bottom)
    for i in range(n):
        a, b = ring_idx_bottom[i], ring_idx_bottom[(i + 1) % n]
        c, d = ring_idx_top[(i + 1) % n], ring_idx_top[i]
        if outward_ccw: f += [(a, b, c), (a, c, d)]
        else: f += [(a, c, b), (a, d, c)]
    return f

def extrude(outer, holes, z0, z1):
    """Extrude a polygon with holes between z0 and z1 (watertight)."""
    outer = ccw(np.asarray(outer, float)); holes = [cw(np.asarray(h, float)) for h in holes]
    merged = bridge_holes(outer, holes) if holes else outer
    tris = earclip(merged)
    # unique vertex list: map merged points to ring vertices
    rings = [outer] + holes
    pts = np.vstack(rings)
    key = {tuple(np.round(p, 9)): i for i, p in enumerate(pts)}
    mi = np.array([key[tuple(np.round(p, 9))] for p in merged])
    n = len(pts)
    v = np.vstack([np.c_[pts, np.full(n, z0)], np.c_[pts, np.full(n, z1)]])
    f = []
    for a, b, c in tris:
        A, B, C = mi[a], mi[b], mi[c]
        if A in (B, C) or B == C: continue
        f.append((n + A, n + B, n + C))      # top, CCW from above
        f.append((A, C, B))                  # bottom
    off = 0
    for r in rings:
        k = len(r); bot = list(range(off, off + k)); top = [i + n for i in bot]
        f += _walls(bot, top, True)          # outer CCW / holes CW both give outward normals
        off += k
    return Mesh(v, f)

def extrude_star(outer, inner, z0, z1):
    """Annulus extrusion where outer and inner have the same vertex count (matched by angle).
    inner=None gives a solid (fan to the centre)."""
    outer = np.asarray(outer, float); k = len(outer)
    if area2(outer) < 0:
        outer = outer[::-1]
        if inner is not None: inner = np.asarray(inner, float)[::-1]
    if inner is None:
        v = np.vstack([np.c_[outer, np.full(k, z0)], np.c_[outer, np.full(k, z1)], [[0, 0, z0], [0, 0, z1]]])
        cb, ct = 2 * k, 2 * k + 1
        f = []
        for i in range(k):
            j = (i + 1) % k
            f += [(cb, j, i), (ct, k + i, k + j)]
        f += _walls(list(range(k)), list(range(k, 2 * k)), True)
        return Mesh(v, f)
    inner = np.asarray(inner, float)
    v = np.vstack([np.c_[outer, np.full(k, z0)], np.c_[outer, np.full(k, z1)],
                   np.c_[inner, np.full(k, z0)], np.c_[inner, np.full(k, z1)]])
    O0, O1, I0, I1 = 0, k, 2 * k, 3 * k
    f = []
    for i in range(k):
        j = (i + 1) % k
        f += [(O1 + i, O1 + j, I1 + j), (O1 + i, I1 + j, I1 + i)]   # top
        f += [(O0 + i, I0 + j, O0 + j), (O0 + i, I0 + i, I0 + j)]   # bottom
    f += _walls(list(range(O0, O0 + k)), list(range(O1, O1 + k)), True)
    f += _walls(list(range(I0, I0 + k)), list(range(I1, I1 + k)), False)
    return Mesh(v, f)

def ray_contour(shape_fn, angles):
    """Sample a star-shaped contour r(theta) given as a function."""
    r = shape_fn(angles)
    return np.c_[r * np.cos(angles), r * np.sin(angles)]

def cylinder(r, z0, z1, n=64, cx=0, cy=0):
    return extrude_star(circle(0, 0, r, n), None, z0, z1).translate((cx, cy, 0))

def tube(ro, ri, z0, z1, n=96):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return extrude_star(np.c_[ro * np.cos(a), ro * np.sin(a)], np.c_[ri * np.cos(a), ri * np.sin(a)], z0, z1)

def box(x0, y0, z0, x1, y1, z1):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return Mesh(v, f)

def torus(R, r, n=120, m=24):
    u = np.linspace(0, 2 * np.pi, n, endpoint=False); w = np.linspace(0, 2 * np.pi, m, endpoint=False)
    U, W = np.meshgrid(u, w, indexing='ij')
    x = (R + r * np.cos(W)) * np.cos(U); y = (R + r * np.cos(W)) * np.sin(U); z = r * np.sin(W)
    v = np.c_[x.ravel(), y.ravel(), z.ravel()]
    f = []
    for i in range(n):
        for j in range(m):
            a = i * m + j; b = ((i + 1) % n) * m + j; c = ((i + 1) % n) * m + (j + 1) % m; d = i * m + (j + 1) % m
            f += [(a, b, c), (a, c, d)]
    return Mesh(v, f)

# ---------------------------------------------------------------- checks + export
def edge_check(m):
    e = np.sort(np.vstack([m.f[:, [0, 1]], m.f[:, [1, 2]], m.f[:, [2, 0]]]), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    return int((counts != 2).sum())

def volume(m):
    a, b, c = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)

def winding(points, m, chunk=4000):
    """Generalised winding number of points w.r.t. a closed mesh (≈1 inside, 0 outside)."""
    out = np.zeros(len(points))
    A, B, C = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
    for s in range(0, len(points), 256):
        p = points[s:s + 256][:, None, :]
        a, b, c = A[None] - p, B[None] - p, C[None] - p
        la, lb, lc = [np.linalg.norm(x, axis=2) for x in (a, b, c)]
        det = np.einsum('ijk,ijk->ij', a, np.cross(b, c))
        den = la * lb * lc + np.einsum('ijk,ijk->ij', a, b) * lc + np.einsum('ijk,ijk->ij', b, c) * la + np.einsum('ijk,ijk->ij', c, a) * lb
        out[s:s + 256] = (2 * np.arctan2(det, den)).sum(1) / (4 * np.pi)
    return out

def write_stl(m, path, name='part'):
    a, b, c = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
    n = np.cross(b - a, c - a); ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1; n = n / ln
    with open(path, 'wb') as fh:
        fh.write(name.encode()[:80].ljust(80, b' ')); fh.write(struct.pack('<I', len(m.f)))
        data = np.zeros(len(m.f), dtype=[('n', '<f4', 3), ('a', '<f4', 3), ('b', '<f4', 3), ('c', '<f4', 3), ('attr', '<u2')])
        data['n'] = n; data['a'] = a; data['b'] = b; data['c'] = c
        fh.write(data.tobytes())

def write_3mf(objects, path):
    """objects: list of (name, Mesh) already placed in bed coordinates (mm)."""
    res, items = [], []
    for i, (name, m) in enumerate(objects, start=1):
        vs = ''.join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.v)
        ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.f)
        res.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(res)}</resources><build>{"".join(items)}</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels); z.writestr('3D/3dmodel.model', model)

"""3D check of the 70% model: exported files, interference and clearance between every pair of parts,
at all 4 selector positions and several gear angles."""
import os, sys, math, struct, json, itertools, numpy as np
from scipy.spatial import cKDTree
import geom as g, parts as p, build_asm as B
S = p.S; assert S != 1
STL_DIR = sys.argv[1]
# ---------------------------------------------------------------- 1. exported STLs == the parts we check
def read_stl(path):
    d = open(path, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    a = np.frombuffer(d[84:84 + n * 50], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('x', '<u2')])
    return a['v'].astype(float)
bad = []
for name, (m, q) in B.P.items():
    tri = read_stl(f'{STL_DIR}/{name}.stl')
    if tri.shape[0] != len(m.f) or np.abs(tri - m.v[m.f]).max() > 1e-3: bad.append(name)
    if g.edge_check(m): bad.append(name + ' (not watertight)')
print('1. exported STL files match the checked parts:', 'yes, all %d' % len(B.P) if not bad else bad)
# ---------------------------------------------------------------- assembly at 70%
src = open('build_asm.py').read()
asm_src = src[src.index('def assembly(pos):'):src.index('    return A\n') + len('    return A\n')]
asm_src = asm_src.replace('def assembly(pos):', 'def assembly(pos, thA=0.0):').replace('    thA = 0.0\n', '')
asm_src = asm_src.replace("dang = {'A': 0.0,", "dang = {'A': thA,").replace("at(P['pulley_66T_dog'][0], X['A'], p.L2[0])", "at(P['pulley_66T_dog'][0], X['A'], p.L2[0], thA)")
ns = dict(B.__dict__); ns['P'] = {n: (m.transform(np.eye(3) / S), q) for n, (m, q) in B.P.items()}   # back to the 1:1 frame
exec(asm_src, ns)
def assembly(pos, thA): return [(n, m.transform(np.eye(3) * S)) for n, m in ns['assembly'](pos, thA)]
# ---------------------------------------------------------------- geometry helpers
rng = np.random.default_rng(1)
def sample(m, spacing=0.3):
    tri = m.v[m.f]; ar = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    k = np.maximum(1, np.ceil(ar / spacing ** 2 * 1.2)).astype(int)
    idx = np.repeat(np.arange(len(tri)), k)
    u, v = rng.random(len(idx)), rng.random(len(idx)); fl = u + v > 1; u[fl], v[fl] = 1 - u[fl], 1 - v[fl]
    t = tri[idx]; pts = t[:, 0] + u[:, None] * (t[:, 1] - t[:, 0]) + v[:, None] * (t[:, 2] - t[:, 0])
    return np.vstack([pts, tri.reshape(-1, 3)]), np.r_[idx, np.repeat(np.arange(len(tri)), 3)]
def pt_tri(p_, a, b, c):
    """exact distance from points p_ to triangles (a, b, c), row-wise (Ericson, Real-Time Collision Detection 5.1.5)."""
    ab, ac, ap = b - a, c - a, p_ - a
    d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
    bp = p_ - b; d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
    cp = p_ - c; d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
    va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
    den = va + vb + vc; den[den == 0] = 1e-12
    v = vb / den; w = vc / den; q = a + ab * v[:, None] + ac * w[:, None]
    m = (d1 <= 0) & (d2 <= 0); q[m] = a[m]
    m = (d3 >= 0) & (d4 <= d3); q[m] = b[m]
    m = (d6 >= 0) & (d5 <= d6); q[m] = c[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.where(d1 - d3 == 0, 1e-12, d1 - d3); q[m] = (a + ab * t[:, None])[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.where(d2 - d6 == 0, 1e-12, d2 - d6); q[m] = (a + ac * t[:, None])[m]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); t = (d4 - d3) / np.where((d4 - d3) + (d5 - d6) == 0, 1e-12, (d4 - d3) + (d5 - d6)); q[m] = (b + (c - b) * t[:, None])[m]
    return np.linalg.norm(p_ - q, axis=1)
class Part:
    def __init__(s, name, m):
        s.name, s.m = name, m; s.lo, s.hi = m.bounds()
        s.pts, s.tri = sample(m); s.tree = cKDTree(s.pts)
def pair(A, Bp, reach=1.0):
    """(min gap, max penetration) between two parts, both measured in mm. Gap is +inf if > reach."""
    lo = np.maximum(A.lo, Bp.lo) - reach; hi = np.minimum(A.hi, Bp.hi) + reach
    if np.any(lo > hi): return math.inf, 0.0
    best, depth = math.inf, 0.0
    for X, Y in ((A, Bp), (Bp, A)):
        sel = np.all((X.pts > lo) & (X.pts < hi), axis=1)
        if not sel.any(): continue
        P = X.pts[sel]
        d, j = Y.tree.query(P, k=6, distance_upper_bound=reach + 0.6)
        keep = np.isfinite(d[:, 0])
        if not keep.any(): continue
        P, j = P[keep], j[keep]
        cand = np.unique(np.c_[np.repeat(np.arange(len(P)), j.shape[1]), Y.tri[np.minimum(j, len(Y.tri) - 1)].ravel()], axis=0)
        tri = Y.m.v[Y.m.f[cand[:, 1]]]
        dist = pt_tri(P[cand[:, 0]], tri[:, 0], tri[:, 1], tri[:, 2])
        dmin = np.full(len(P), np.inf); np.minimum.at(dmin, cand[:, 0], dist)
        near = dmin < reach
        if near.any():
            w = g.winding(P[near], Y.m)
            inside = w > 0.5
            if inside.any(): depth = max(depth, dmin[near][inside].max())
            out = dmin[near][~inside]
            if len(out): best = min(best, out.min())
    return best, depth
# ---------------------------------------------------------------- pair classes
def kind(n):
    for k in ('plate', 'pillar', 'bridge', 'shaft', 'axle', 'disc', 'pinion', 'g42', 'g40', 'g14', 'dog40', 'pulley', 'collar', 'fork', 'selector', 'flywheel', 'spacer', 'spool', 'cap', 'washer'):
        if n.startswith(k): return k
    return n
ROT = {'shaft', 'axle'}
FIT = {  # (kind, kind): what the contact is
 frozenset(['pillar', 'plate']): 'peg in plate hole', frozenset(['bridge', 'plate']): 'bridge leg pin in plate hole',
 frozenset(['fork', 'collar']): 'fork in collar groove', frozenset(['fork', 'selector']): 'fork peg in bar slot',
 frozenset(['disc', 'axle']): 'crank disc on axle', frozenset(['pinion', 'axle']): 'pinion on axle (glue)',
 frozenset(['collar', 'shaft']): 'collar slides on shaft', frozenset(['cap', 'shaft']): 'end cap on shaft',
 frozenset(['spacer', 'shaft']): 'spacer spins on shaft', frozenset(['dog40', 'shaft']): 'dog gear spins on shaft',
 frozenset(['pulley', 'shaft']): 'pulley on shaft', frozenset(['spool', 'shaft']): 'spool on shaft (glue)',
 frozenset(['flywheel', 'shaft']): 'flywheel on shaft (glue)', frozenset(['g42', 'shaft']): 'gear on shaft (glue)',
 frozenset(['g40', 'shaft']): 'gear on shaft (glue)', frozenset(['g14', 'shaft']): 'gear on shaft (glue)',
 frozenset(['shaft', 'plate']): 'shaft in plate hole', frozenset(['axle', 'plate']): 'axle in plate hole', frozenset(['shaft', 'bridge']): 'shaft in bridge hole',
 frozenset(['dog40', 'collar']): 'dog lugs', frozenset(['pulley', 'collar']): 'dog lugs',
 frozenset(['spacer', 'plate']): 'spacer thrust face', frozenset(['spacer', 'bridge']): 'spacer thrust face',
 frozenset(['spacer', 'pulley']): 'spacer thrust face', frozenset(['spacer', 'dog40']): 'spacer thrust face',
 frozenset(['selector', 'plate']): 'bar sliding on plate edges', frozenset(['cap', 'plate']): 'end cap (set by hand)', frozenset(['cap', 'bridge']): 'end cap (set by hand)',
 frozenset(['pinion', 'g42']): 'gear mesh', frozenset(['g14', 'g40']): 'gear mesh', frozenset(['g14', 'dog40']): 'gear mesh',
 frozenset(['disc', 'plate']): 'crank disc face', frozenset(['washer', 'shaft']): 'washer on shaft (glue)',
 frozenset(['washer', 'dog40']): 'washer thrust face', frozenset(['washer', 'pulley']): 'washer thrust face', frozenset(['washer', 'collar']): 'washer inside collar lugs (turn together)', frozenset(['cap', 'pulley']): 'end cap (set by hand)', frozenset(['cap', 'dog40']): 'end cap (set by hand)',
}
def same_body(a, b, pos):
    """parts fixed to each other (glued/pressed) never move relative to each other."""
    return False
results = {}
phases = [float(os.environ.get('VPH', 0))]
for pos, label in [(int(os.environ.get('VPOS', 0)), os.environ.get('VLABEL', 'Output 1'))]:
    for ph in phases:
        raw = assembly(pos, ph); only = tuple(os.environ.get('VONLY', '').split(',')) if os.environ.get('VONLY') else None
        cache = {}
        def get(n, m):
            if n not in cache: cache[n] = Part(n, m)
            return cache[n]
        bb = {n: m.bounds() for n, m in raw}
        for (na, ma), (nb, mb) in itertools.combinations(raw, 2):
            if only and not (na.startswith(only) or nb.startswith(only)): continue
            (la, ha), (lb, hb) = bb[na], bb[nb]
            if np.any(np.maximum(la, lb) - 1.0 > np.minimum(ha, hb) + 1.0): continue
            A, Bq = get(na, ma), get(nb, mb)
            gp, dp = pair(A, Bq)
            if gp == math.inf and dp == 0: continue
            key = tuple(sorted([A.name, Bq.name]))
            r = results.setdefault(key, dict(gap=math.inf, pen=0.0, where=''))
            if gp < r['gap']: r['gap'] = gp
            if dp > r['pen']: r['pen'], r['where'] = dp, f'{label}, gear angle {math.degrees(ph):.1f} deg'
        print('checked', label, f'angle {math.degrees(ph):.1f}', flush=True)
rows = []
for (a, b), r in results.items():
    what = FIT.get(frozenset([kind(a), kind(b)]), 'separate parts')
    rows.append(dict(a=a, b=b, what=what, gap=None if r['gap'] == math.inf else round(r['gap'], 3), pen=round(r['pen'], 3), where=r['where']))
json.dump(rows, open(os.environ.get('VJSON', 'v1.json'), 'w'), indent=1)
print('pairs within 1 mm of each other:', len(rows))

"""Pack the print parts onto 350 x 350 mm beds (Creality K2 Plus) and write one 3MF per bed + previews."""
import math, json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
import geom as g
import build_asm as B

BED = 350.0; EDGE = 8.0; GAP = 5.0
parts = B.P

def footprint(m):
    lo, hi = m.bounds(); return hi[0] - lo[0], hi[1] - lo[1]

def placed(m, x, y, ang=0.0):
    """Rotate about Z, drop to z=0 and move so the bounding box's min corner sits at (x, y)."""
    r = m.transform(g.rot_z(ang)); lo, _ = r.bounds(); return r.translate((x - lo[0], y - lo[1], -lo[2]))

def rect_poly(x, y, w, h): return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])

def sat_overlap(P, Q):
    for poly in (P, Q):
        for i in range(len(poly)):
            e = poly[(i + 1) % len(poly)] - poly[i]; n = np.array([-e[1], e[0]])
            a, b = P @ n, Q @ n
            if a.max() <= b.min() or b.max() <= a.min(): return False
    return True

from matplotlib.path import Path
N = int(BED)
def pack(items, forbidden):
    """items: list of (name, mesh). Bottom-left fill on a 1 mm occupancy grid. Returns placed, leftover."""
    occ = np.zeros((N, N), bool)
    occ[:int(EDGE), :] = occ[-int(EDGE):, :] = True; occ[:, :int(EDGE)] = occ[:, -int(EDGE):] = True
    cy, cx = np.mgrid[0:N, 0:N] + 0.5
    pts = np.c_[cx.ravel(), cy.ravel()]
    for f in forbidden:
        occ |= Path(f).contains_points(pts).reshape(N, N)
    out, left = [], []
    for name, m in sorted(items, key=lambda it: -np.prod(footprint(it[1]))):
        best = None
        for rot in (0.0, math.pi / 2):
            w, h = footprint(m.transform(g.rot_z(rot)))
            W, H = int(math.ceil(w + GAP)), int(math.ceil(h + GAP))
            if W >= N or H >= N: continue
            S = np.pad(occ.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
            win = S[H:, W:] - S[:-H, W:] - S[H:, :-W] + S[:-H, :-W]       # occupied cells in each H x W window
            free = np.argwhere(win == 0)                                  # (row=y, col=x) of window corners
            if not len(free): continue
            y0, x0 = free[np.lexsort((free[:, 1], free[:, 0]))[0]]
            if best is None or (y0, x0) < (best[0], best[1]): best = (y0, x0, rot, W, H)
        if best is None: left.append((name, m)); continue
        y0, x0, rot, W, H = best
        occ[y0:y0 + H, x0:x0 + W] = True
        out.append((name, placed(m, x0 + GAP / 2, y0 + GAP / 2, rot), None))
    return out, left

def diag_plate(m, margin=4.0):
    """Place a long plate along the bed diagonal, centred. Returns (mesh, footprint polygon with margin)."""
    r = m.transform(g.rot_z(math.radians(45)))
    lo, hi = r.bounds(); c = (lo + hi) / 2
    r = r.translate((BED / 2 - c[0], BED / 2 - c[1], -lo[2]))
    w, h = footprint(m)
    corners = np.array([[-w / 2 - margin, -h / 2 - margin], [w / 2 + margin, -h / 2 - margin], [w / 2 + margin, h / 2 + margin], [-w / 2 - margin, h / 2 + margin]])
    R = np.array([[math.cos(math.pi / 4), -math.sin(math.pi / 4)], [math.sin(math.pi / 4), math.cos(math.pi / 4)]])
    return r, corners @ R.T + BED / 2

def expand(names):
    items = []
    for n in names:
        m, q = parts[n]
        items += [(f'{n}_{i + 1}' if q > 1 else n, m) for i in range(q)]
    return items

small = expand([n for n in parts if n not in ('plate_front', 'plate_middle', 'plate_back', 'selector_bar', 'belt_ring_TPU')])
beds = []
# bed 1 and 2: one long plate on the diagonal each, small parts in the corners
queue = small
for big in ('plate_back', 'plate_middle'):
    pm, poly = diag_plate(parts[big][0])
    got, queue = pack(queue, [poly])
    beds.append([(big, pm, poly)] + got)
# bed 3: front plate + selector bar side by side, rest around them
fp = placed(parts['plate_front'][0], EDGE, EDGE); fw, fh = footprint(parts['plate_front'][0])
bp = placed(parts['selector_bar'][0], EDGE, EDGE + fh + GAP + 2); bw, bh = footprint(parts['selector_bar'][0])
fixed = [rect_poly(EDGE, EDGE, fw, fh), rect_poly(EDGE, EDGE + fh + GAP + 2, bw, bh)]
got, queue = pack(queue, [rect_poly(f[0, 0] - GAP / 2, f[0, 1] - GAP / 2, f[1, 0] - f[0, 0] + GAP, f[2, 1] - f[0, 1] + GAP) for f in fixed])
beds.append([('plate_front', fp, fixed[0]), ('selector_bar', bp, fixed[1])] + got)
while queue:
    got, queue = pack(queue, [])
    beds.append(got)
tpu = [('belt_ring_TPU', placed(parts['belt_ring_TPU'][0], BED / 2 - 50, BED / 2 - 50), None)]

summary = []
def save(bed, path, title):
    g.write_3mf([(n, m) for n, m, _ in bed], path + '.3mf')
    fig, ax = plt.subplots(figsize=(6, 6), dpi=110)
    ax.add_patch(MPoly(rect_poly(0, 0, BED, BED), closed=True, fill=False, ec='#555', lw=1.2))
    for n, m, _ in bed:
        v = m.v[m.f][:, :, :2]
        col = '#2f9e44' if n.startswith('selector') else '#b9c3cc' if n.startswith('plate') else '#d9480f' if any(k in n for k in ('gear', 'pinion', 'pulley')) else '#1971c2' if any(k in n for k in ('collar', 'fork')) else '#868e96'
        from matplotlib.collections import PolyCollection
        ax.add_collection(PolyCollection(v, facecolor=col, edgecolor='none', alpha=0.9))
    ax.set_xlim(-5, BED + 5); ax.set_ylim(-5, BED + 5); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=11)
    fig.savefig(path + '.png', bbox_inches='tight'); plt.close(fig)

for i, bed in enumerate(beds, start=1):
    names = [n for n, _, _ in bed]
    for n, m, _ in bed:
        lo, hi = m.bounds(); assert lo[0] >= 0 and lo[1] >= 0 and hi[0] <= BED and hi[1] <= BED, (n, lo, hi)
    save(bed, f'out/bed_{i}_PLA', f'Bed {i} (PLA) - {len(bed)} parts')
    summary.append(dict(bed=i, parts=names))
save(tpu, 'out/bed_TPU_belt', 'Optional: belt ring (TPU)')
json.dump(summary, open('out/beds.json', 'w'), indent=1)
for s in summary: print('bed', s['bed'], len(s['parts']), 'parts:', ', '.join(sorted(set(n.rsplit('_', 1)[0] if n[-1].isdigit() else n for n in s['parts']))))

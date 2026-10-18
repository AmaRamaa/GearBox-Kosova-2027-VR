"""2D gear mesh check on the real tooth outlines at 70% scale: interference through a full tooth cycle, backlash, depth, contact ratio."""
import math, numpy as np, parts as p
from matplotlib.path import Path
S = p.S
def outline(z, x=0.0, tip_r=None, backlash=None, n=9):
    kw = dict(x=x, tip_r=tip_r, nf=25)
    if backlash is not None: kw['backlash'] = backlash
    return p.involute_outline(z, **kw) * S
G = {  # name: (teeth, kwargs) as used in parts.py
 'pinion14': (14, dict(backlash=p.c(0.25))), '42T': (42, {}), '40T': (40, {}),
 '14T_shift': (14, dict(x=1.0, tip_r=11.0, backlash=p.c(0.1))),
}
def rot(P, a): c, s = math.cos(a), math.sin(a); return P @ np.array([[c, s], [-s, c]])
def dense(P, step=0.02):
    out = []
    for a, b in zip(P, np.roll(P, -1, 0)):
        k = max(1, int(np.linalg.norm(b - a) / step)); out.append(a + (b - a) * np.linspace(0, 1, k, endpoint=False)[:, None])
    return np.vstack(out)
def mesh_angle(a1, n1, n2):  # gear 2 to the +X of gear 1
    k = n1 / n2; return -k * a1 + math.pi + 0 - math.pi / n2
def pen(P1, P2):
    """max penetration depth (mm) of outline P2's points inside polygon P1 and vice versa (0 = no interference)."""
    d = 0.0
    for A, B in ((P1, P2), (P2, P1)):
        ins = Path(A).contains_points(B)
        if ins.any():
            pts = B[ins]
            # depth = distance to A's boundary
            dd = np.min(np.linalg.norm(pts[:, None, :] - A[None, ::3, :], axis=2), axis=1)
            d = max(d, dd.max())
    return d
def gap(P1, P2):
    from scipy.spatial import cKDTree
    return cKDTree(P1).query(P2)[0].min()
def check(name, g1, g2, cd_full):
    n1, k1 = G[g1]; n2, k2 = G[g2]
    cd = cd_full * S
    O1 = dense(outline(n1, **k1)); O2 = dense(outline(n2, **k2))
    r1 = np.linalg.norm(O1, axis=1); r2 = np.linalg.norm(O2, axis=1)
    depth = r1.max() + r2.max() - cd                       # how deep the teeth reach into each other
    rootgap = min(cd - r1.max() - r2.min(), cd - r2.max() - r1.min())   # tip-to-root clearance
    pitch1 = 2 * math.pi / n1
    worst_pen, bl_min, bl_max = 0.0, 1e9, 0.0
    ncontact = []
    from scipy.spatial import cKDTree
    for a1 in np.linspace(0, pitch1, 24, endpoint=False):
        A = rot(O1, a1)
        a2 = mesh_angle(a1, n1, n2)
        Bc = rot(O2, a2) + [cd, 0]
        worst_pen = max(worst_pen, pen(A, Bc))
        # angular backlash: rotate gear 2 each way until it touches
        lim = []
        for sgn in (1, -1):
            lo, hi = 0.0, 0.2
            for _ in range(22):
                mid = (lo + hi) / 2
                if pen(A, rot(O2, a2 + sgn * mid) + [cd, 0]) > 0.005: hi = mid
                else: lo = mid
            lim.append(lo)
        bl = sum(lim) * (n2 * p.M * S / 2)                  # free play at the pitch circle of gear 2, mm
        bl_min = min(bl_min, bl); bl_max = max(bl_max, bl)
        # contact count when gear 2 is pushed against gear 1 (drive flank): tooth pairs within 0.03 mm
        Bd = rot(O2, a2 + lim[0]) + [cd, 0]
        t = cKDTree(Bd); dd, _ = t.query(A)
        near = A[dd < 0.03]
        if len(near):
            ang = np.arctan2(near[:, 1], near[:, 0]) - a1
            teeth = np.unique(np.round(np.mod(ang, 2 * math.pi) / pitch1).astype(int) % n1)
            ncontact.append(len(teeth))
        else: ncontact.append(0)
    cr = np.mean(ncontact)
    ok = worst_pen < 0.01 and bl_min > 0.03 and depth > 1.2 * p.M * S and rootgap > 0.1 and min(ncontact) >= 1
    print(f"{name:26s} cd {cd:6.2f}  teeth reach {depth:4.2f} mm  tip-root gap {rootgap:4.2f}  interference {worst_pen:5.3f}  "
          f"backlash {bl_min:4.2f}-{bl_max:4.2f} mm  teeth in contact {min(ncontact)}-{max(ncontact)} (avg {cr:.2f})  {'OK' if ok else 'PROBLEM'}")
    return ok
IN = 25.4
res = [check('pinion 14T - 42T (x6)', 'pinion14', '42T', 1.4 * IN),
       check('shifted 14T - 40T (x3)', '14T_shift', '40T', 1.4 * IN)]
print('ALL GEAR MESHES OK' if all(res) else 'GEAR PROBLEM')

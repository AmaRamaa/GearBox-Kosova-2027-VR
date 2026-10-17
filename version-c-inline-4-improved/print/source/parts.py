"""Version C (inline-4) hand-turned demonstrator, 1:1 scale, all dimensions in mm.
Assembly frame: X along the shaft line, Y up, Z from the front plate's inner face toward the back."""
import math, numpy as np
import geom as g

IN = 25.4
M = IN / 20                       # 20DP module = 1.27 mm
PA = math.radians(20)
X = {k: v * IN for k, v in dict(F=-2.0, M1=0, A=1.4, M2=2.8, O2=2.8, B=4.2, M3=5.6, C=7.0, M4=8.4, I=8.4, O3=9.8).items()}

# --- fits (tuned for FDM, 0.4 mm nozzle)
SHAFT_AF, SHAFT_RC = 12.5, 6.9          # printed rounded-hex shaft: across flats, corner radius
BORE_FIX = (12.9, 7.05)                 # fixed gears: slip fit, glue
BORE_SLIDE = (13.0, 7.1)                # collars slide along the shaft
BORE_CAP = (12.65, 6.95)                # end caps: snug
ROUND_BORE = 7.2                        # free-spinning dog gears / plate holes (radius)
D_R, D_FLAT = 4.0, 3.3                  # pinion D-axle
D_BORE = (4.2, 3.5)

# --- Z stations (mm from front plate inner face)
FRONT = (-6.35, 0.0); MIDDLE = (21.59, 24.765); BACK = (91.44, 97.79)
L1 = (5.08, 17.78); L2 = (30.48, 43.18); L3 = (63.5, 76.2)
LUG_H = 2.0; LUG_OVERLAP = 1.6; TRAVEL = 2.4
COLLAR_BODY = 8.6; GROOVE_C = 3.7          # groove centre measured from the collar's far (non-lug) end
FORK_T = 3.0
def _zl(dog_top): return dog_top - LUG_OVERLAP + LUG_H   # collar lug-base Z when engaged
ZL = {'A': _zl(L2[1] + LUG_H), 'O2': _zl(L3[1] + LUG_H), 'O3': _zl(L3[1] + LUG_H)}
Z_LUGBASE = {k: (v, v + TRAVEL) for k, v in ZL.items()}                       # (in, out)
Z_GROOVE = {k: (v + COLLAR_BODY - GROOVE_C, v + TRAVEL + COLLAR_BODY - GROOVE_C) for k, v in ZL.items()}
PLATE_TOP = 1.45 * IN
BAR_T = 5.0
PITCH = 0.45 * IN
BRIDGE = (50.8, 55.88)

# ------------------------------------------------------------------ profiles
def rhex_r(theta, af, rc, rot=0.0):
    h = af / 2
    t = np.mod(theta - rot, np.pi / 3) - np.pi / 6
    return np.minimum(h / np.cos(t), rc)

def d_r(theta, R, flat):
    c = np.cos(theta + np.pi / 2)            # flat on the -Y side
    with np.errstate(divide='ignore'):
        lim = np.where(c > 1e-9, flat / c, np.inf)
    return np.minimum(R, lim)

def involute_outline(z, m=M, x=0.0, backlash=0.15, tip_r=None, nf=9):
    rp = z * m / 2; rb = rp * math.cos(PA)
    ra = tip_r if tip_r else rp + m * (1 + x)
    rf = rp - m * (1.25 - x)
    psi = math.pi / (2 * z) + 2 * x * math.tan(PA) / z - backlash / (2 * rp)
    inv = lambda a: math.tan(a) - a
    r0 = max(rb, rf)
    rs = np.linspace(r0, ra, nf)
    half = np.array([psi + inv(PA) - inv(math.acos(min(1.0, rb / r))) for r in rs])
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z
        if rf < r0: pts.append((rf, c - half[0]))
        pts += [(r, c - h) for r, h in zip(rs, half)]
        pts += [(r, c + h) for r, h in zip(rs[::-1], half[::-1])]
        if rf < r0: pts.append((rf, c + half[0]))
        nxt = 2 * math.pi * (k + 1) / z
        a0, a1 = c + half[0], nxt - half[0]
        for a in np.linspace(a0, a1, 4)[1:-1]: pts.append((rf, a))
    P = np.array([(r * math.cos(a), r * math.sin(a)) for r, a in pts])
    return P

def star_part(outer_pts, inner_fn, z0, z1):
    th = np.arctan2(outer_pts[:, 1], outer_pts[:, 0])
    if inner_fn is None: return g.extrude_star(outer_pts, None, z0, z1)
    r = inner_fn(th)
    return g.extrude_star(outer_pts, np.c_[r * np.cos(th), r * np.sin(th)], z0, z1)

def ring_pts(fn, n=360):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False); r = fn(th)
    return np.c_[r * np.cos(th), r * np.sin(th)]

FIX = lambda th: rhex_r(th, *BORE_FIX)
SLIDE = lambda th: rhex_r(th, *BORE_SLIDE)
CAPB = lambda th: rhex_r(th, *BORE_CAP)
ROUND = lambda th: np.full_like(th, ROUND_BORE)
DBORE = lambda th: d_r(th, *D_BORE)

def lugs(z0, z1, start=0.0):
    """3 dog lugs, 30 degrees wide, in the band r 8.4..12.2 mm."""
    out = []
    for i in range(3):
        a = start + i * 2 * np.pi / 3
        arc = np.linspace(a - np.radians(15), a + np.radians(15), 8)
        poly = np.r_[np.c_[12.2 * np.cos(arc), 12.2 * np.sin(arc)], np.c_[8.4 * np.cos(arc[::-1]), 8.4 * np.sin(arc[::-1])]]
        out.append(g.extrude(poly, [], z0, z1))
    return out

# ------------------------------------------------------------------ parts (print orientation unless noted)
def gear(z, bore, x=0.0, tip_r=None, backlash=0.15, width=12.7, dog=False):
    body = star_part(involute_outline(z, x=x, tip_r=tip_r, backlash=backlash), bore, 0, width)
    return g.concat([body] + lugs(width, width + LUG_H)) if dog else body

def pinion():           return gear(14, DBORE, backlash=0.25)
def gear42():           return gear(42, FIX)
def gear40():           return gear(40, FIX)
def gear40_dog():       return gear(40, ROUND, dog=True)
def gear14_shift():     return gear(14, FIX, x=1.0, tip_r=11.0, backlash=0.1)

def pulley(teeth, bore, dog=False, width=12.7):
    rp = teeth * 3 / math.pi / 2
    rf, rg = rp + 2.0, rp - 1.5
    prof = [(0, 1.5, rf)] + chamfer(1.5, 5.0, rf, rg) + [(5.0, width - 5.0, rg)] + chamfer(width - 5.0, width - 1.5, rg, rf) + [(width - 1.5, width, rf)]
    parts = stack(prof, bore, 160)
    if dog: parts += lugs(width, width + LUG_H)
    return g.concat(parts)

def stack(profile, bore, n=120):
    """Stack thin rings following r(z) so overhangs stay at 45 degrees. profile: list of (z0, z1, r)."""
    return [star_part(g.circle(0, 0, r, n), bore, z0, z1) for z0, z1, r in profile]

def chamfer(z0, z1, r0, r1, step=0.4):
    n = max(1, int(round((z1 - z0) / step))); zs = np.linspace(z0, z1, n + 1)
    return [(zs[i], zs[i + 1], r0 + (r1 - r0) * (i + 1) / n) for i in range(n)]

def collar():           # printed lugs-up; in the assembly the lugs face the dog gear (toward -Z)
    prof = [(0, 2, 12.7), (2, 5.4, 9.5)] + chamfer(5.4, 8.6, 9.5, 12.7)
    return g.concat(stack(prof, SLIDE) + lugs(COLLAR_BODY, COLLAR_BODY + LUG_H, start=np.pi / 3))

def shaft(length):      # lying on a flat
    prof = ring_pts(lambda th: rhex_r(th, SHAFT_AF, SHAFT_RC, rot=np.pi / 6), 240)   # flats at top/bottom
    m = g.extrude_star(prof, None, 0, length)                      # axis along Z
    m = m.transform(g.rot_y(np.pi / 2))                            # axis along X
    lo, _ = m.bounds(); return m.translate(-lo)

def d_axle(length):     # lying on its flat
    prof = ring_pts(lambda th: d_r(th, D_R, D_FLAT), 240)
    m = g.extrude_star(prof, None, 0, length).transform(g.rot_y(np.pi / 2))
    lo, _ = m.bounds(); return m.translate(-lo)

def end_cap():          return star_part(g.circle(0, 0, 10, 120), CAPB, 0, 6)

def spacer(length):     return g.tube(10, 7.25, 0, length, 96)   # round bore: slides over the hex corners
SPACER_A = L2[0] - MIDDLE[1] - 0.15
SPACER_O = L3[0] - BRIDGE[1] - 0.15

def crank_disc(handle):
    parts = [star_part(g.circle(0, 0, 30, 180), DBORE, 0, 4), star_part(g.circle(0, 0, 9, 120), DBORE, 4, 9)]
    if handle: parts.append(g.cylinder(4.5, 4, 34, 48, cx=22, cy=0))
    else: parts.append(g.tube(29, 26, 4, 6))         # ring: the motor's 60 mm outline
    return g.concat(parts)

def flywheel():
    hexb = ring_pts(lambda th: rhex_r(th, *BORE_FIX), 120)
    holes = [hexb] + [g.circle(32 * math.cos(a), 32 * math.sin(a), 11, 48) for a in np.linspace(0, 2 * np.pi, 5, endpoint=False)]
    wheel = g.extrude(g.circle(0, 0, 50.8, 200), holes, 0, 15)
    mark = g.box(44, -3, 15, 50, 3, 16.5)
    return g.concat([wheel, mark])

def spool():
    hexb = ring_pts(lambda th: rhex_r(th, *BORE_FIX), 120)
    fl_holes = [hexb, g.circle(0, 19, 1.6, 24), g.circle(0, -19, 1.6, 24)]
    return g.concat([g.extrude(g.circle(0, 0, 22.86, 120), fl_holes, 0, 2.5),
                     star_part(g.circle(0, 0, 15.875, 120), FIX, 2.5, 18.5)] +
                    stack(chamfer(18.5, 25.5, 15.875, 22.86), FIX) +
                    [g.extrude(g.circle(0, 0, 22.86, 120), fl_holes, 25.5, 27)])

def belt_ring():        # TPU: square 3 mm section, ~5 % shorter than the 310 mm belt path
    R = 0.95 * 309.8 / (2 * math.pi)
    return g.tube(R + 1.5, R - 1.5, 0, 3, n=240)

# ---- frame
FRONT_PILLARS = [(x * IN, s * 1.05 * IN) for x in (-1.0, 2.8, 5.6, 9.6) for s in (-1, 1)]
BACK_PILLARS = [(x * IN, s * 1.2 * IN) for x in (-2.3, -0.6, 7.0, 10.8) for s in (-1, 1)]
BRIDGE_LEGS = [(X[o] + dx * IN, s * 0.85 * IN) for o in ('O2', 'O3') for dx in (-0.2, 0.55) for s in (-1, 1)]

def pillar(length, peg0, peg1, lying=True):
    """9 mm square standoff with 3.6 mm square pegs (fit the 5.2 mm round plate holes)."""
    m = g.concat([g.box(-1.8, -1.8, 0, 1.8, 1.8, peg0), g.box(-4.5, -4.5, peg0, 4.5, 4.5, peg0 + length),
                  g.box(-1.8, -1.8, peg0 + length, 1.8, 1.8, peg0 + length + peg1)])
    if not lying: return m
    m = m.transform(g.rot_y(np.pi / 2)); lo, _ = m.bounds(); return m.translate(-lo)
def front_pillar(lying=True): return pillar(MIDDLE[0] - FRONT[1], 4, 2.8, lying)
def back_pillar(lying=True):  return pillar(BACK[0] - MIDDLE[1], 2.8, 4, lying)

def bridge():           # printed plate-down, legs up
    x0, x1, y0, y1 = -0.40 * IN, 0.75 * IN, -1.0 * IN, 1.0 * IN
    plate = g.extrude(g.rounded_rect(x0, y0, x1, y1, 4), [g.circle(0, 0, ROUND_BORE, 64)], 0, BRIDGE[1] - BRIDGE[0])
    t = BRIDGE[1] - BRIDGE[0]; leg_len = BRIDGE[0] - MIDDLE[1]
    legs = []
    for dx in (-0.2, 0.55):
        for s in (-1, 1):
            legs += [g.cylinder(3, t, t + leg_len, 40, cx=dx * IN, cy=s * 0.85 * IN),
                     g.cylinder(1.5, t + leg_len, t + leg_len + 2.8, 24, cx=dx * IN, cy=s * 0.85 * IN)]
    return g.concat([plate] + legs)

def fork():             # flat; in the assembly the slab is centred on the collar groove
    t = FORK_T
    arc = np.radians(np.linspace(25, 155, 30))
    yoke = np.r_[np.c_[12.2 * np.cos(arc), 12.2 * np.sin(arc)], np.c_[10.0 * np.cos(arc[::-1]), 10.0 * np.sin(arc[::-1])]]
    return g.concat([g.extrude(yoke, [], 0, t), g.box(-4, 10.5, 0, 4, PLATE_TOP - 1.0, t),
                     g.box(-1.8, PLATE_TOP - 1.2, 0, 1.8, PLATE_TOP + BAR_T - 0.6, t)])

ENG = {'A': [1, 0, 0, 0], 'O2': [0, 0, 1, 0], 'O3': [0, 0, 0, 1]}            # bar positions: O1, N, O2, O3
SLOT_Z = {k: [Z_GROOVE[k][0] if e else Z_GROOVE[k][1] for e in ENG[k]] for k in ENG}
LUG_Z = {k: [Z_LUGBASE[k][0] if e else Z_LUGBASE[k][1] for e in ENG[k]] for k in ENG}
BAR_X = (12.0, 293.0); BAR_Z = (MIDDLE[0] - 3.6, BACK[1] + 3.2)

def slot_outline(pts, w=2.8, cap=10):
    pts = np.asarray(pts, float); left, right = [], []
    for i in range(len(pts)):
        dirs = []
        if i > 0: dirs.append(pts[i] - pts[i - 1])
        if i < len(pts) - 1: dirs.append(pts[i + 1] - pts[i])
        nrm = []
        for d in dirs: d = d / np.linalg.norm(d); nrm.append(np.array([-d[1], d[0]]))
        n = sum(nrm); n = n / np.linalg.norm(n)
        scale = w / max(0.5, float(np.dot(n, nrm[0])))
        left.append(pts[i] + n * scale); right.append(pts[i] - n * scale)
    d0 = pts[1] - pts[0]; a0 = math.atan2(d0[1], d0[0]); d1 = pts[-1] - pts[-2]; a1 = math.atan2(d1[1], d1[0])
    end = [pts[-1] + w * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(a1 + np.pi / 2, a1 - np.pi / 2, cap)[1:-1]]
    start = [pts[0] + w * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(a0 - np.pi / 2, a0 - 3 * np.pi / 2, cap)[1:-1]]
    return np.array(left + end + right[::-1] + start)

def selector_bar_local():
    """Bar in assembly-local coords: polygon in (x, z), thickness along Y above the plate tops."""
    outer = np.array([[BAR_X[0], BAR_Z[0]], [BAR_X[1], BAR_Z[0]], [BAR_X[1], BAR_Z[1]], [BAR_X[0], BAR_Z[1]],
                      [BAR_X[0], 80.0], [-8.0, 80.0], [-8.0, 40.0], [BAR_X[0], 40.0]])
    slots = [slot_outline([(X[k] + i * PITCH, SLOT_Z[k][i]) for i in range(4)]) for k in ('A', 'O2', 'O3')]
    return outer, slots

def selector_bar():     # printed top-face-down: (x, z) -> (X, Y), lips point up
    outer, slots = selector_bar_local()
    body = g.extrude(outer, slots, 0, BAR_T)
    lips = [g.box(BAR_X[0], BAR_Z[0], BAR_T, BAR_X[1], MIDDLE[0] - 0.3, BAR_T + 3),
            g.box(BAR_X[0], BACK[1] + 0.3, BAR_T, BAR_X[1], BAR_Z[1], BAR_T + 3)]
    return g.concat([body] + lips)

def pocket_list(holes, x0, x1):
    pk = []
    for cx in np.arange(x0 + 25, x1 - 20, 17.8):
        for cy in (-0.9 * IN, 0.9 * IN):
            rect = (cx - 7, cy - 3.8, cx + 7, cy + 3.8)
            ok = all(math.hypot(max(rect[0] - hx, 0, hx - rect[2]), max(rect[1] - hy, 0, hy - rect[3])) > hr + 3.0 for hx, hy, hr in holes)
            if ok: pk.append(g.rounded_rect(*rect, 2.5, 5))
    return pk

def plate(which):
    H = PLATE_TOP
    if which == 'front':
        x0, x1 = -1.45 * IN, 9.9 * IN
        holes = [(X[k], 0, ROUND_BORE) for k in ('A', 'B', 'C')] + [(X[k], 0, D_R + 0.25) for k in ('M1', 'M2', 'M3', 'M4')]
        holes += [(x, y, 2.6) for x, y in FRONT_PILLARS]
        pockets = []
    else:
        x0, x1 = -2.65 * IN, 11.1 * IN
        if which == 'middle':
            holes = [(X[k], 0, ROUND_BORE) for k in ('F', 'A', 'B', 'C', 'I')] + [(X[k], 0, D_R + 0.25) for k in ('M1', 'M2', 'M3')]
            holes += [(x, y, 2.6) for x, y in FRONT_PILLARS + BACK_PILLARS] + [(x, y, 1.75) for x, y in BRIDGE_LEGS]
        else:
            holes = [(X[k], 0, ROUND_BORE) for k in ('F', 'A', 'O2', 'B', 'C', 'I', 'O3')] + [(x, y, 2.6) for x, y in BACK_PILLARS]
        pockets = pocket_list(holes + [(X[k], 0, 13.0) for k in ('O2', 'O3', 'M2')], x0, x1)
    t = {'front': FRONT, 'middle': MIDDLE, 'back': BACK}[which]
    rings = [g.circle(x, y, r, 64 if r > 4 else 28) for x, y, r in holes] + pockets
    return g.extrude(g.rounded_rect(x0, -H, x1, H, 12.7), rings, 0, t[1] - t[0])

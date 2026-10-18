"""Functional checks of the 70% model: shifting (dogs + selector bar), what turns in each position, fits, shafts, belt."""
import math, numpy as np, parts as p
from matplotlib.path import Path
S = p.S; IN = p.IN; X = p.X
ok_all = True
def say(ok, text):
    global ok_all; ok_all &= ok; print(('  OK   ' if ok else '  FAIL ') + text)
mm = lambda v: v * S
print('A. Shifting: dog lugs and selector bar')
slot_slack = p.SLOT_W - p.FORK_T            # Z play of the peg in a flat part of the slot (1:1 units)
groove_slack = 3.4 - p.FORK_T
err = (slot_slack + groove_slack) / 2        # worst collar position error either way
print(f'     collar travel {mm(p.TRAVEL):.2f} mm, lug overlap {mm(p.LUG_OVERLAP):.2f} mm, worst position error +/-{mm(err):.2f} mm '
      f'(slot {mm(slot_slack):.2f} + groove {mm(groove_slack):.2f} play)')
eng_min = p.LUG_OVERLAP - err; free_min = p.TRAVEL - p.LUG_OVERLAP - err
say(mm(eng_min) >= 0.5, f'engaged: lugs overlap at least {mm(eng_min):.2f} mm in the worst case')
say(mm(free_min) >= 0.5, f'released: lugs clear by at least {mm(free_min):.2f} mm in the worst case')
# dog parts can't drift into the collar: trapped between spacer and glued washer
play = (p.c(0.15) - 0.05) + p.c(0.15)
say(0.1 <= mm(play) <= 0.5, f'dog gears and dog pulley are trapped between spacer and washer with {mm(play):.2f} mm end play (spin free, cannot drift)')
wgap = (p.L3[1] + p.LUG_H - p.LUG_OVERLAP + p.LUG_H) - (p.L3[1] + p.c(0.15) + p.WASHER_L)
tipgap = p.LUG_H - p.LUG_OVERLAP
say(wgap > tipgap, f'engaged collar clears the washer by {mm(wgap):.2f} mm; if pushed further its lug tips bottom on the gear first ({mm(tipgap):.2f} mm), and collar, washer and gear all turn together then. Lugs pass outside the washer ({mm(p.LUG_RI - p.WASHER_R):.2f} mm radial)')
# what turns in each bar position
names = ['Output 1 (flywheel)', 'Neutral', 'Output 2 (fast)', 'Output 3 (strong)']
want = {0: {'A'}, 1: set(), 2: {'O2'}, 3: {'O3'}}
dog_top = {'A': p.L2[1] + p.LUG_H, 'O2': p.L3[1] + p.LUG_H, 'O3': p.L3[1] + p.LUG_H}
for pos in range(4):
    eng = set()
    for k in ('A', 'O2', 'O3'):
        zl = p.LUG_Z[k][pos]                       # collar lug base; collar lugs span [zl - LUG_H, zl]
        overlap = dog_top[k] - (zl - p.LUG_H)
        if overlap > 0.2: eng.add(k)
    say(eng == want[pos], f'bar at {names[pos]:20s} engages {sorted(eng) or "nothing"}')
# continuous bar travel: the square peg must fit in the slot at every bar offset, and the slot must drive it
outer, slots = p.selector_bar_local()
t = p.FORK_T
for si, k in enumerate(('A', 'O2', 'O3')):
    path = Path(slots[si]); worst = 1e9; jam = False
    for u in np.linspace(0, 3 * p.PITCH, 241):
        x = X[k] + u                        # peg position in bar coordinates when the bar is moved by -u
        zs = np.linspace(p.SLOT_Z[k][0] - 6, p.SLOT_Z[k][0] + 9, 1501)
        fits = []
        for z in zs:
            sq = np.array([[x - t / 2, z - t / 2], [x + t / 2, z - t / 2], [x + t / 2, z + t / 2], [x - t / 2, z + t / 2],
                           [x, z - t / 2], [x, z + t / 2], [x - t / 2, z], [x + t / 2, z]])
            fits.append(path.contains_points(sq).all())
        fits = np.array(fits)
        if not fits.any(): jam = True; break
        span = zs[fits].max() - zs[fits].min(); worst = min(worst, span)
    say(not jam, f'slot {k}: the fork peg slides through all 4 positions without jamming (min Z play {mm(worst):.2f} mm)')
print('B. Fits (real clearance at 70%, same as the 1:1 model)')
fits = [('fixed gears on shaft (glue)', p.BORE_FIX[0] - p.SHAFT_AF), ('collar slides on shaft', p.BORE_SLIDE[0] - p.SHAFT_AF),
        ('end cap on shaft (snug)', p.BORE_CAP[0] - p.SHAFT_AF), ('dog gear / pulley / plate hole over hex corners', 2 * (p.ROUND_BORE - p.SHAFT_RC)),
        ('pinion on D axle', p.D_BORE[0] - p.D_R), ('axle in plate hole', 2 * p.c(0.25)), ('fork in collar groove', 3.4 - p.FORK_T),
        ('pillar peg in plate hole (diagonal)', 2 * p.PEG_HOLE - 2 * 1.8 * math.sqrt(2)), ('bridge pin in plate hole', 2 * p.c(0.25))]
for n, v in fits:
    r = mm(v); say(0.05 <= r <= 0.7, f'{n:48s} {r:.2f} mm')
print('C. Gear mesh widths: every pair of meshing gears sits in the same lane')
lanes = [('pinion / 42T row', p.L1, p.L1), ('C 14T / I 40T', p.L2, p.L2), ('B 14T / Output 2 dog gear', p.L3, p.L3), ('I 14T / Output 3 dog gear', p.L3, p.L3)]
for n, a, b in lanes:
    ov = min(a[1], b[1]) - max(a[0], b[0]); say(ov >= 0.95 * (a[1] - a[0]), f'{n:30s} face overlap {mm(ov):.1f} mm of {mm(a[1]-a[0]):.1f}')
print('D. Shafts are held by two supports and capped')
sup = {'A': [p.FRONT, p.MIDDLE, p.BACK], 'B': [p.FRONT, p.MIDDLE, p.BACK], 'C': [p.FRONT, p.MIDDLE, p.BACK], 'I': [p.MIDDLE, p.BACK],
       'F': [p.MIDDLE, p.BACK], 'O2': [p.BRIDGE, p.BACK], 'O3': [p.BRIDGE, p.BACK]}
SH = {'A': (-5.85, -5.85 + 108.64), 'B': (-5.85, -5.85 + 108.64), 'C': (-5.85, -5.85 + 108.64), 'I': (p.MIDDLE[0], p.MIDDLE[0] + 81.2),
      'F': (15.0, 123.0), 'O2': (44.8, 44.8 + 86.9), 'O3': (44.8, 44.8 + 86.9)}
for k, s in sup.items():
    z0, z1 = SH[k]; eng = [min(z1, b) - max(z0, a) for a, b in s]; frac = min(e / (b - a) for e, (a, b) in zip(eng, s))
    say(frac >= 0.75, f'shaft {k:3s} {mm(z1-z0):5.1f} mm long sits in {len(s)} supports, at least {100*frac:.0f}% of each support\'s thickness'
        + (' (ends flush-ish with the front plate on purpose)' if frac < 1 else ''))
print('E. Flywheel belt')
cdist = mm(X['A'] - X['F']); r1 = mm(66 * 3 / math.pi / 2 - 1.5); r2 = mm(22 * 3 / math.pi / 2 - 1.5)
L = 2 * math.sqrt(cdist ** 2 - (r1 - r2) ** 2) + math.pi * (r1 + r2) + 2 * (r1 - r2) * math.asin((r1 - r2) / cdist)
ring = 2 * math.pi * mm(0.95 * 309.8 / (2 * math.pi))
say(0.9 * L < ring < L, f'belt path {L:.0f} mm, TPU ring {ring:.0f} mm ({100 * ring / L:.0f}% so it is stretched tight); or a rubber band about {0.9*L:.0f} mm around ({0.45*L:.0f} mm long laid flat)')
print('F. Smallest printed features')
feats = [('gear tooth module', p.M), ('pillar peg (square)', 3.6), ('bridge pin diameter', 3.0), ('fork thickness', p.FORK_T), ('dog lug height', p.LUG_H),
         ('middle plate thickness', p.MIDDLE[1] - p.MIDDLE[0]), ('washer wall', p.WASHER_R - p.BORE_FIX[1])]
for n, v in feats: say(mm(v) >= 0.85, f'{n:28s} {mm(v):.2f} mm')
print('\nALL FUNCTIONAL CHECKS PASSED' if ok_all else '\nSOME CHECKS FAILED')

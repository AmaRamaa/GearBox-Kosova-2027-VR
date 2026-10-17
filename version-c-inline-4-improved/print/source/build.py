import math, os, sys, json, time, numpy as np
import geom as g, parts as p
from parts import X, IN

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(f'{OUT}/stl', exist_ok=True)

def mesh_angle(a1, n1, n2, x1, x2):
    th = 0.0 if x2 > x1 else math.pi
    k = n1 / n2
    return -k * a1 + th + math.pi + k * th - math.pi / n2

def at(m, x, z, ang=0.0, y=0.0):
    return m.transform(g.rot_z(ang)).translate((x, y, z))

# ------------------------------------------------------------------ print parts (name, mesh, qty)
P = {}
P['plate_front'] = (p.plate('front'), 1)
P['plate_middle'] = (p.plate('middle'), 1)
P['plate_back'] = (p.plate('back'), 1)
P['pillar_front'] = (p.front_pillar(), 8)
P['pillar_back'] = (p.back_pillar(), 8)
P['bridge'] = (p.bridge(), 2)
P['selector_bar'] = (p.selector_bar(), 1)
P['fork'] = (p.fork(), 3)
P['collar'] = (p.collar(), 3)
P['gear_42T'] = (p.gear42(), 3)
P['pinion_14T'] = (p.pinion(), 4)
P['gear_14T_shifted'] = (p.gear14_shift(), 3)
P['gear_40T'] = (p.gear40(), 1)
P['gear_40T_dog'] = (p.gear40_dog(), 2)
P['pulley_66T_dog'] = (p.pulley(66, p.ROUND, dog=True), 1)
P['pulley_22T'] = (p.pulley(22, p.FIX), 1)
SH = {'shaft_ABC': 108.64, 'shaft_F': 108.0, 'shaft_I': 81.2, 'shaft_O2_O3': 86.9}
P['shaft_ABC'] = (p.shaft(SH['shaft_ABC']), 3)
P['shaft_F'] = (p.shaft(SH['shaft_F']), 1)
P['shaft_I'] = (p.shaft(SH['shaft_I']), 1)
P['shaft_O2_O3'] = (p.shaft(SH['shaft_O2_O3']), 2)
AX = {'axle_M1_M3': 42.62, 'axle_M4': 33.63}
P['axle_M1_M3'] = (p.d_axle(AX['axle_M1_M3']), 3)
P['axle_M4'] = (p.d_axle(AX['axle_M4']), 1)
P['crank_disc_handle'] = (p.crank_disc(True), 1)
P['crank_disc'] = (p.crank_disc(False), 3)
P['end_cap'] = (p.end_cap(), 12)
P['spacer_A'] = (p.spacer(p.SPACER_A), 1)
P['spacer_O2_O3'] = (p.spacer(p.SPACER_O), 2)
P['flywheel'] = (p.flywheel(), 1)
P['spool'] = (p.spool(), 2)
P['belt_ring_TPU'] = (p.belt_ring(), 1)

report = {}
for name, (m, q) in P.items():
    lo, hi = m.bounds()
    report[name] = dict(qty=q, bad_edges=g.edge_check(m), volume_cm3=round(g.volume(m) / 1000, 2),
                        size_mm=[round(float(v), 1) for v in hi - lo], min_z=round(float(lo[2]), 3))
    g.write_stl(m, f'{OUT}/stl/{name}.stl', name)

# ------------------------------------------------------------------ assembly (for checks)
def assembly(pos):
    A = []
    zl = {k: p.LUG_Z[k][pos] for k in ('A', 'O2', 'O3')}; zg = {k: p.SLOT_Z[k][pos] for k in ('A', 'O2', 'O3')}
    A.append(('plate_front', P['plate_front'][0].translate((0, 0, p.FRONT[0]))))
    A.append(('plate_middle', P['plate_middle'][0].translate((0, 0, p.MIDDLE[0]))))
    A.append(('plate_back', P['plate_back'][0].translate((0, 0, p.BACK[0]))))
    for i, (x, y) in enumerate(p.FRONT_PILLARS): A.append((f'pillar_f{i}', p.front_pillar(False).translate((x, y, p.FRONT[1] - 4))))
    for i, (x, y) in enumerate(p.BACK_PILLARS): A.append((f'pillar_b{i}', p.back_pillar(False).translate((x, y, p.MIDDLE[1] - 2.8))))
    for o in ('O2', 'O3'):
        A.append((f'bridge_{o}', P['bridge'][0].transform(g.rot_x(math.pi), (X[o], 0, p.BRIDGE[1]))))
    # shafts (assembly orientation: axis along Z)
    def shaft_asm(x, z0, z1, ang=0.0):
        prof = p.ring_pts(lambda th: p.rhex_r(th, p.SHAFT_AF, p.SHAFT_RC), 240)
        return g.extrude_star(prof, None, z0, z1).transform(g.rot_z(ang), (x, 0, 0))
    A.append(('shaft_F', shaft_asm(X['F'], 15.0, 15.0 + SH['shaft_F'])))
    def daxle(x, z0, z1):
        prof = p.ring_pts(lambda th: p.d_r(th, p.D_R, p.D_FLAT), 240)
        return g.extrude_star(prof, None, z0, z1).translate((x, 0, 0))
    AXLE_Z = {k: (-15.85, -15.85 + AX['axle_M1_M3']) for k in ('M1', 'M2', 'M3')}; AXLE_Z['M4'] = (-15.85, -15.85 + AX['axle_M4'])
    # gears with meshing phases
    thA = 0.0
    A.append(('g42_A', at(P['gear_42T'][0], X['A'], p.L1[0], thA)))
    pin = {k: mesh_angle(thA, 42, 14, X['A'], X[k]) for k in ('M1', 'M2')}
    thB = mesh_angle(pin['M2'], 14, 42, X['M2'], X['B'])
    pin['M3'] = mesh_angle(thB, 42, 14, X['B'], X['M3'])
    thC = mesh_angle(pin['M3'], 14, 42, X['M3'], X['C'])
    pin['M4'] = mesh_angle(thC, 42, 14, X['C'], X['M4'])
    A.append(('g42_B', at(P['gear_42T'][0], X['B'], p.L1[0], thB)))
    A.append(('g42_C', at(P['gear_42T'][0], X['C'], p.L1[0], thC)))
    for k, a in pin.items():
        A.append((f'pinion_{k}', at(P['pinion_14T'][0], X[k], p.L1[0], a)))
        A.append((f'axle_{k}', daxle(0, *AXLE_Z[k]).transform(g.rot_z(a), (X[k], 0, 0))))
        A.append((f'disc_{k}', P['crank_disc_handle' if k == 'M1' else 'crank_disc'][0].transform(g.rot_z(math.pi) @ g.rot_x(math.pi), (0, 0, 0)).transform(g.rot_z(a), (X[k], 0, p.FRONT[0] - 0.5))))
    A.append(('pulley_A', at(P['pulley_66T_dog'][0], X['A'], p.L2[0])))
    A.append(('pulley_F', at(P['pulley_22T'][0], X['F'], p.L2[0])))
    thI = mesh_angle(thC, 14, 40, X['C'], X['I'])
    for k, a in (('A', thA), ('B', thB), ('C', thC)): A.append((f'shaft_{k}', shaft_asm(X[k], -5.85, -5.85 + SH['shaft_ABC'], a)))
    A.append(('shaft_I', shaft_asm(X['I'], p.MIDDLE[0], p.MIDDLE[0] + SH['shaft_I'], thI)))
    A.append(('g14_C', at(P['gear_14T_shifted'][0], X['C'], p.L2[0], thC)))
    A.append(('g40_I', at(P['gear_40T'][0], X['I'], p.L2[0], thI)))
    A.append(('g14_B', at(P['gear_14T_shifted'][0], X['B'], p.L3[0], thB)))
    dang = {'A': 0.0, 'O2': mesh_angle(thB, 14, 40, X['B'], X['O2'])}
    A.append(('dog40_O2', at(P['gear_40T_dog'][0], X['O2'], p.L3[0], dang['O2'])))
    A.append(('g14_I', at(P['gear_14T_shifted'][0], X['I'], p.L3[0], thI)))
    dang['O3'] = mesh_angle(thI, 14, 40, X['I'], X['O3'])
    A.append(('dog40_O3', at(P['gear_40T_dog'][0], X['O3'], p.L3[0], dang['O3'])))
    for o in ('O2', 'O3'): A.append((f'shaft_{o}', shaft_asm(X[o], 44.8, 44.8 + SH['shaft_O2_O3'], dang[o])))
    for k in ('A', 'O2', 'O3'):
        c = P['collar'][0].transform(g.rot_x(math.pi)).transform(g.rot_z(dang[k]), (X[k], 0, zl[k] + p.COLLAR_BODY))
        A.append((f'collar_{k}', c))
        A.append((f'fork_{k}', P['fork'][0].translate((X[k], 0, zg[k] - p.FORK_T / 2))))
    bar = P['selector_bar'][0].transform(np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]), (-pos * p.PITCH, p.PLATE_TOP + p.BAR_T, 0))
    A.append(('selector_bar', bar))
    A.append(('flywheel', P['flywheel'][0].translate((X['F'], 0, 102.0))))
    A.append(('spacer_A', P['spacer_A'][0].translate((X['A'], 0, p.MIDDLE[1] + 0.05))))
    for o in ('O2', 'O3'): A.append((f'spacer_{o}', P['spacer_O2_O3'][0].translate((X[o], 0, p.BRIDGE[1] + 0.05))))
    for o in ('O2', 'O3'):
        A.append((f'spool_{o}', P['spool'][0].transform(g.rot_z(dang[o]), (X[o], 0, 98.3))))
    ang = {'A': thA, 'B': thB, 'C': thC, 'F': 0.0, 'I': thI, 'O2': dang['O2'], 'O3': dang['O3']}
    caps = [(k, p.BACK[1] + 0.2) for k in 'ABC'] + [('F', p.MIDDLE[0] - 6.2), ('F', 117.2),
            ('I', p.BACK[1] + 0.2), ('O2', p.BRIDGE[0] - 6.2), ('O3', p.BRIDGE[0] - 6.2), ('O2', 125.5), ('O3', 125.5)]
    for i, (k, z) in enumerate(caps): A.append((f'cap{i}', P['end_cap'][0].transform(g.rot_z(ang[k]), (X[k], 0, z))))
    for nm in ('flywheel',): pass
    return A

ALLOWED = {('fork', 'collar'), ('collar', 'shaft'), ('fork', 'selector_bar')}
def kind(n): return n.split('_')[0].rstrip('0123456789')

def overlaps(A, tol_frac=0.5):
    hits = []
    boxes = [(n, m, *m.bounds()) for n, m in A]
    for i in range(len(boxes)):
        ni, mi, loi, hii = boxes[i]
        for j in range(i + 1, len(boxes)):
            nj, mj, loj, hij = boxes[j]
            if np.any(hii < loj + 0.05) or np.any(hij < loi + 0.05): continue
            for (na, ma), (nb, mb, lob, hib) in [((ni, mi), (nj, mj, loj, hij)), ((nj, mj), (ni, mi, loi, hii))]:
                tri = ma.v[ma.f]; cent = tri.mean(1)
                nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
                pts = cent - 0.05 * nrm / ln          # nudged 0.05 mm into its own part
                sel = np.all((pts > lob + 0.02) & (pts < hib - 0.02), axis=1)
                if not sel.any(): continue
                w = g.winding(pts[sel], mb)
                inside = int((w > tol_frac).sum())
                if inside:
                    hits.append((na, nb, inside)); break
    return hits

t = time.time()
results = {}
for pos, label in enumerate(['Output 1', 'Neutral', 'Output 2', 'Output 3']):
    hits = overlaps(assembly(pos), tol_frac=0.8)
    results[label] = hits
    print(label, 'overlaps:', hits if hits else 'none', flush=True)
print('check time', round(time.time() - t, 1), 's')
json.dump(dict(parts=report, overlaps={k: [list(map(str, h)) for h in v] for k, v in results.items()}), open(f'{OUT}/report.json', 'w'), indent=1)
for k, v in report.items():
    print(f"{k:22s} x{v['qty']:<2d} bad_edges={v['bad_edges']} vol={v['volume_cm3']:7.2f}cm3 size={v['size_mm']}")

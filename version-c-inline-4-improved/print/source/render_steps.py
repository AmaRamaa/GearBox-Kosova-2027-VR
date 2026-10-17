"""Render the assembly guide pictures from the real print geometry."""
import math, os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import geom as g, parts as p, build_asm as B
from parts import X

OUT = 'guide'; os.makedirs(OUT, exist_ok=True)
NEW = np.array(matplotlib.colors.to_rgb('#e8590c'))
OLD = np.array(matplotlib.colors.to_rgb('#8d99a6'))
LIGHT = np.array([0.35, -0.55, 0.75]); LIGHT /= np.linalg.norm(LIGHT)

def belt_mesh():
    c1, r1, c2, r2 = X['F'], 22 * 3 / math.pi / 2, X['A'], 66 * 3 / math.pi / 2
    d = c2 - c1; beta = math.acos((r1 - r2) / d)
    def loop(ra, rb):
        pts = [(c2 + rb * math.cos(a), rb * math.sin(a)) for a in np.linspace(beta, -beta, 60)]
        pts += [(c1 + ra * math.cos(a), ra * math.sin(a)) for a in np.linspace(-beta - 0.02, beta - 2 * math.pi + 0.02, 30)]
        return np.array(pts)
    return g.extrude(loop(r1 + 2.0, r2 + 2.0), [loop(r1 - 0.5, r2 - 0.5)], p.L2[0] + 5.0, p.L2[1] - 5.0)

ASM = dict(B.assembly(0)); ASM['belt'] = belt_mesh()

def pick(*prefixes):
    return [n for n in ASM if any(n == q or n.startswith(q) for q in prefixes)]

STEPS = [
    ('02', 'Front plate and short pillars', pick('plate_front', 'pillar_f'), dict(azim=62, elev=24)),
    ('03', 'Shafts A, B, C and the motor axles', pick('shaft_A', 'shaft_B', 'shaft_C', 'g42_', 'g14_B', 'g14_C', 'axle_M', 'pinion_'), dict(azim=62, elev=24)),
    ('04', 'Middle plate', pick('plate_middle'), dict(azim=62, elev=24)),
    ('05', 'Long pillars and bearing bridges', pick('pillar_b', 'bridge_'), dict(azim=62, elev=24)),
    ('06', 'Shaft A: spacer, dog pulley, collar', pick('spacer_A', 'pulley_A', 'collar_A'), dict(azim=62, elev=24, zoom=(-90, 130))),
    ('07', 'Shaft I, shaft F and the belt', pick('shaft_I', 'g40_I', 'g14_I', 'shaft_F', 'pulley_F', 'belt', 'cap3'), dict(azim=62, elev=24)),
    ('08', 'Output shafts: cap, spacer, dog gear, collar', pick('shaft_O2', 'shaft_O3', 'cap6', 'cap7', 'spacer_O', 'dog40_', 'collar_O'), dict(azim=62, elev=24)),
    ('09', 'Forks on the collars', pick('fork_'), dict(azim=62, elev=30)),
    ('10', 'Back plate', pick('plate_back'), dict(azim=62, elev=24)),
    ('11', 'Flywheel, spools and end caps', pick('flywheel', 'spool_', 'cap0', 'cap1', 'cap2', 'cap4', 'cap5', 'cap8', 'cap9'), dict(azim=62, elev=24)),
    ('12', 'Crank discs', pick('disc_'), dict(azim=-118, elev=20)),
    ('13', 'Selector bar', pick('selector_bar'), dict(azim=62, elev=38)),
]

def render(names_old, names_new, path, azim, elev, zoom=None, title=None, size=(12, 6.5)):
    tris, cols = [], []
    for nm, is_new in [(n, False) for n in names_old] + [(n, True) for n in names_new]:
        m = ASM[nm]
        t = m.v[m.f][:, :, [0, 2, 1]]                       # X, Z(depth), Y(up)
        nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); ln = np.linalg.norm(nrm, axis=1) + 1e-12
        shade = 0.5 + 0.5 * np.abs((nrm / ln[:, None]) @ LIGHT)
        base = NEW if is_new else OLD
        alpha = (0.55 if is_new else 0.16) if nm.startswith('plate') else 1.0
        if nm.startswith('plate') and not is_new: base = np.array([0.72, 0.76, 0.80])
        c = np.c_[np.clip(base[None] * shade[:, None], 0, 1), np.full(len(t), alpha)]
        tris.append(t); cols.append(c)
    T = np.vstack(tris); C = np.vstack(cols)
    fig = plt.figure(figsize=size, dpi=120); ax = fig.add_subplot(111, projection='3d')
    pc = Poly3DCollection(T, facecolors=C, edgecolors='none'); pc.set_sort_zpos(None)
    ax.add_collection3d(pc)
    V = T.reshape(-1, 3); lo, hi = V.min(0) - 6, V.max(0) + 6
    if zoom: lo[0], hi[0] = zoom
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(hi - lo), zoom=1.05); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=150, facecolor='white'); plt.close(fig)
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    im = Image.open(path).convert('RGB')
    bbox = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
    im = im.crop((max(0, bbox[0] - 20), max(0, bbox[1] - 20), min(im.width, bbox[2] + 20), min(im.height, bbox[3] + 20)))
    if title:
        try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
        except Exception: font = ImageFont.load_default()
        canvas = Image.new('RGB', (im.width, im.height + 44), 'white'); canvas.paste(im, (0, 44))
        ImageDraw.Draw(canvas).text((14, 10), title, fill=(21, 32, 42), font=font); im = canvas
    im.save(path)

done = []
for num, title, new, view in STEPS:
    render(done, new, f'{OUT}/step_{num}.png', title=f'Step {int(num)}: {title}', **view)
    done += new
    print('step', num, len(new), 'new parts', flush=True)
# finished model, front view
render(done, [], f'{OUT}/finished_front.png', azim=-118, elev=26, title='Finished model (crank side)')

"""Parts identification sheet + dimensioned gluing diagram for the assembly guide."""
import math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw, ImageFont, ImageChops
import parts as p, build_asm as B

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(sz, bold=False):
    try: return ImageFont.truetype(FONT_B if bold else FONT, sz)
    except Exception: return ImageFont.load_default()

# ---------------------------------------------------------------- parts sheet
LABEL = {
 'plate_front': 'Front plate', 'plate_middle': 'Middle plate', 'plate_back': 'Back plate', 'selector_bar': 'Selector bar',
 'pillar_front': 'Short pillar', 'pillar_back': 'Long pillar', 'bridge': 'Bearing bridge', 'fork': 'Fork', 'collar': 'Collar',
 'gear_42T': '42T gear', 'pinion_14T': '14T pinion (D hole)', 'gear_14T_shifted': '14T gear, shifted (hex)', 'gear_40T': '40T gear',
 'gear_40T_dog': '40T dog gear (round hole)', 'pulley_66T_dog': '66T dog pulley', 'pulley_22T': '22T pulley',
 'shaft_ABC': 'Shaft A / B / C  76.0 mm', 'shaft_F': 'Shaft F  75.6 mm', 'shaft_I': 'Shaft I  56.8 mm', 'shaft_O2_O3': 'Output shaft  60.8 mm',
 'axle_M1_M3': 'Motor axle  29.8 mm', 'axle_M4': 'Short motor axle  23.5 mm', 'crank_disc_handle': 'Crank disc + handle',
 'crank_disc': 'Motor disc', 'end_cap': 'End cap', 'spacer_A': 'Spacer 3.9 mm', 'spacer_O2_O3': 'Spacer 5.2 mm',
 'flywheel': 'Flywheel', 'spool': 'Spool', 'belt_ring_TPU': 'Belt ring (TPU, optional)'}
ORDER = ['gear_42T', 'pinion_14T', 'gear_14T_shifted', 'gear_40T', 'gear_40T_dog', 'pulley_66T_dog', 'pulley_22T', 'collar',
         'fork', 'spacer_A', 'spacer_O2_O3', 'end_cap', 'shaft_ABC', 'shaft_F', 'shaft_I', 'shaft_O2_O3', 'axle_M1_M3', 'axle_M4',
         'pillar_front', 'pillar_back', 'bridge', 'crank_disc_handle', 'crank_disc', 'flywheel', 'spool', 'belt_ring_TPU',
         'plate_front', 'plate_middle', 'plate_back', 'selector_bar']
COL = {'gear': '#e8590c', 'pinion': '#e8590c', 'pulley': '#c92a2a', 'collar': '#1971c2', 'fork': '#1971c2', 'selector': '#2f9e44'}

def thumb(m, color, path):
    t = m.v[m.f]; c = np.array(matplotlib.colors.to_rgb(color))
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); ln = np.linalg.norm(nrm, axis=1) + 1e-12
    L = np.array([0.4, -0.5, 0.77]); L /= np.linalg.norm(L)
    sh = 0.45 + 0.55 * np.abs((nrm / ln[:, None]) @ L)
    fig = plt.figure(figsize=(3, 3), dpi=110); ax = fig.add_subplot(111, projection='3d')
    ax.add_collection3d(Poly3DCollection(t, facecolors=np.clip(c[None] * sh[:, None], 0, 1), edgecolors='none'))
    lo, hi = m.bounds(); ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(np.maximum(hi - lo, 1e-3))); ax.view_init(elev=35, azim=-60); ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1); fig.savefig(path, facecolor='white'); plt.close(fig)
    im = Image.open(path).convert('RGB'); bb = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
    return im.crop(bb) if bb else im

cells = []
for n in ORDER:
    m, q = B.P[n]
    col = next((v for k, v in COL.items() if n.startswith(k)), '#8d99a6')
    im = thumb(m, col, '/tmp/_thumb.png'); im.thumbnail((210, 150))
    cells.append((im, LABEL[n], q))
cols, cw, ch = 5, 250, 215
rows = math.ceil(len(cells) / cols)
sheet = Image.new('RGB', (cols * cw + 20, rows * ch + 70), 'white'); d = ImageDraw.Draw(sheet)
d.text((16, 14), f'Parts list ({round(p.S*100)}% scale): 76 PLA parts + optional TPU belt', fill=(21, 32, 42), font=font(24, True))
for i, (im, lab, q) in enumerate(cells):
    x = 10 + (i % cols) * cw; y = 60 + (i // cols) * ch
    d.rounded_rectangle((x + 4, y + 4, x + cw - 4, y + ch - 4), 10, outline=(204, 212, 220), width=2)
    sheet.paste(im, (x + (cw - im.width) // 2, y + 12 + (150 - im.height) // 2))
    d.text((x + 14, y + 168), lab, fill=(21, 32, 42), font=font(14, True))
    d.text((x + cw - 16, y + 14), f'× {q}', fill=(217, 72, 15), font=font(17, True), anchor='rt')
sheet.save('guide/parts_sheet.png'); print('parts sheet', sheet.size)

# ---------------------------------------------------------------- gluing diagram
GLUE, FREE, CAP, SHAFT = '#e8590c', '#1971c2', '#adb5bd', '#ced4da'
FR, MI, BA = p.FRONT, p.MIDDLE, p.BACK
def seg(z0, z1, start): return (z0 - start, z1 - start)
SHAFTS = [
 ('Shaft A (×1)  76.0 mm', -5.85, 108.64, [
    ('42T', 5.08, 17.78, 55.9, GLUE), ('spacer', p.MIDDLE[1] + 0.05, p.MIDDLE[1] + 0.05 + p.SPACER_A, 20, FREE),
    ('66T dog pulley', 30.48, 45.18, 67, FREE), ('collar', 43.58, 54.18, 25.4, FREE), ('cap', 97.99, 102.79, 20, CAP)]),
 ('Shaft B (×1)  76.0 mm', -5.85, 108.64, [('42T', 5.08, 17.78, 55.9, GLUE), ('14T shifted', 63.5, 76.2, 22, GLUE), ('cap', 97.99, 102.79, 20, CAP)]),
 ('Shaft C (×1)  76.0 mm', -5.85, 108.64, [('42T', 5.08, 17.78, 55.9, GLUE), ('14T shifted', 30.48, 43.18, 22, GLUE), ('cap', 97.99, 102.79, 20, CAP)]),
 ('Shaft I (×1)  56.8 mm', 21.59, 81.2, [('40T', 30.48, 43.18, 53.3, GLUE), ('14T shifted', 63.5, 76.2, 22, GLUE), ('cap', 97.99, 102.79, 20, CAP)]),
 ('Shaft F (×1)  75.6 mm', 15.0, 108.0, [('cap', 15.39, 21.39, 20, CAP), ('22T pulley', 30.48, 43.18, 25, GLUE),
    ('flywheel', 102.0, 117.0, 101.6, GLUE), ('cap', 117.2, 123.0, 20, CAP)]),
 ('Output shaft (×2)  60.8 mm', 44.8, 86.9, [('cap', 44.8, 50.6, 20, CAP), ('spacer', 55.93, 63.4, 20, FREE), ('40T dog', 63.5, 78.2, 53.3, FREE),
    ('collar', 76.6, 87.2, 25.4, FREE), ('spool', 98.3, 125.3, 45.7, GLUE), ('cap', 125.5, 131.7, 20, CAP)]),
 ('Motor axle (×3 long, ×1 short)', -15.85, 42.62, [('disc', -15.85, -6.85, 60, CAP), ('14T pinion', 5.08, 17.78, 20.3, GLUE)]),
]
fig, axes = plt.subplots(len(SHAFTS), 1, figsize=(12, 2.35 * len(SHAFTS)), dpi=130)
for ax, (name, start, length, items) in zip(axes, SHAFTS):
    ax.add_patch(Rectangle((0, -6.25), length, 12.5, color=SHAFT, zorder=1))
    pl = [(n, a, b) for n, (a, b) in (('front plate', FR), ('middle plate', MI), ('back plate', BA)) if b - start > -2 and a - start < length + 2]
    for i, (plate, a, b) in enumerate(pl):
        s0, s1 = a - start, b - start
        ax.add_patch(Rectangle((s0, -48), s1 - s0, 96, color='#e3e7eb', zorder=0))
        ax.text(s1 + 1.5, -46 + 9 * (i % 2), plate, ha='left', va='bottom', fontsize=8, color='#868e96', style='italic')
    lvl = 0
    for i, (lab, z0, z1, dia, col) in enumerate(items):
        s0, s1 = z0 - start, z1 - start
        h = min(dia, 76)
        ax.add_patch(Rectangle((s0, -h / 2), s1 - s0, h, color=col, alpha=0.92, zorder=2))
        ax.text((s0 + s1) / 2, h / 2 + 2 + 11 * (i % 2) if col != GLUE else -h / 2 - 3, lab, ha='center',
                va='bottom' if col != GLUE else 'top', fontsize=8.5, color='#15202a', zorder=3,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))
        if col == GLUE:
            y = 52 + 13 * lvl
            ax.annotate('', xy=(s0, y), xytext=(0, y), arrowprops=dict(arrowstyle='->', color='#15202a', lw=1.0))
            ax.plot([s0, s0], [h / 2, y], color='#15202a', lw=0.6, ls=':')
            ax.text(s0 + 1.5, y, f'{s0 * p.S + 1e-6:.1f} mm  ({lab})', ha='left', va='center', fontsize=9, fontweight='bold', color='#d9480f')
            lvl += 1
    ax.plot([0, 0], [-10, 52 + 13 * max(lvl - 1, 0)], color='#15202a', lw=1.0)
    ax.text(0, -12, 'front end', ha='center', va='top', fontsize=7.5, color='#15202a')
    ax.set_title(name, loc='left', fontsize=11.5, fontweight='bold', color='#15202a')
    ax.set_xlim(-22, 150); ax.set_ylim(-52, 80); ax.axis('off')
fig.text(0.01, 0.997, f'{round(p.S*100)}% model: where each part goes, measured from the front end of each shaft', fontsize=14, fontweight='bold', va='top')
fig.text(0.01, 0.982, 'Orange = glue in place     Blue = slides or spins free     Grey = end cap or disc     Shaded bands = plates', fontsize=10, va='top', color='#495057')
fig.tight_layout(rect=(0, 0, 1, 0.972)); fig.savefig('guide/step_01_gluing.png', facecolor='white'); plt.close(fig)
print('gluing diagram done')

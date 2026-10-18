"""All 76 PLA parts of the scaled model on ONE 350 x 350 mm bed (Creality K2 Plus) + optional TPU belt ring."""
import os, json, math, numpy as np
import build_asm as B, layout_core as L, geom as g, parts as p
OUT = os.environ.get('GB_OUT', 'out')
items = L.expand([n for n in B.P if n != 'belt_ring_TPU'])
got, left = L.pack(items, [])
assert not left, [n for n, _ in left]
for n, m, _ in got:
    lo, hi = m.bounds(); assert lo[0] >= 0 and lo[1] >= 0 and hi[0] <= L.BED and hi[1] <= L.BED and abs(lo[2]) < 1e-6, (n, lo, hi)
pct = round(p.S * 100)
L.save(got, f'{OUT}/bed_one_plate_PLA_{pct}pct', f'One bed (PLA), {pct}% scale - {len(got)} parts')
tpu = [('belt_ring_TPU', L.placed(B.P['belt_ring_TPU'][0], L.BED / 2 - 40, L.BED / 2 - 40), None)]
L.save(tpu, f'{OUT}/bed_TPU_belt_{pct}pct', f'Optional: belt ring (TPU), {pct}% scale')
vol = sum(g.volume(B.P[n][0]) * B.P[n][1] for n in B.P if n != 'belt_ring_TPU') / 1000
used = max(m.bounds()[1][1] for _, m, _ in got)
print('parts', len(got), 'PLA volume cm3', round(vol, 1), 'approx grams at 30% fill', round(vol * 1.24 * 0.55), 'bed rows used to y=', round(used, 1))

import os, sys, json, numpy as np
src = open('v2.py').read(); src = src[:src.index('results = {}')]
sys.argv = ['x', 'out/stl']; exec(src)
asm = dict(assembly(0, 0.0)); top = p.PLATE_TOP * S
rows = [r for r in json.load(open('v1.json')) if r['pen'] > 0.02]
bad = 0
for r in rows:
    A, Bp = Part(r['a'], asm[r['a']]), Part(r['b'], asm[r['b']])
    pl = A if A.name.startswith('plate') else Bp
    n = 0
    for X, Y in ((A, Bp), (Bp, A)):
        lo = np.maximum(X.lo, Y.lo) - 0.5; hi = np.minimum(X.hi, Y.hi) + 0.5
        P = X.pts[np.all((X.pts > lo) & (X.pts < hi), axis=1)]
        ins = P[g.winding(P, Y.m) > 0.5]
        if 'selector' in r['a'] + r['b']: ins = ins[np.abs(ins[:, 1] - top) > 0.02]      # bar rests on the plate tops
        else: ins = ins[(ins[:, 2] > pl.lo[2] + 0.02) & (ins[:, 2] < pl.hi[2] - 0.02)]  # pillar/bridge shoulders rest on the plate faces
        n += len(ins)
    bad += n > 0
    if n: print('REAL OVERLAP', r['a'], r['b'], n)
print(f'{len(rows)} flagged contacts re-checked: {len(rows) - bad} are parts resting on a face, {bad} real overlaps')

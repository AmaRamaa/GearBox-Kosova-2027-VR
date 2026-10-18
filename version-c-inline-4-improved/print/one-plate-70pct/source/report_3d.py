import json, collections
rows = json.load(open('verify3d.json'))
pen = [r for r in rows if r['pen'] > 0.02]
print('Pairs that intersect by more than 0.02 mm:', len(pen))
for r in sorted(pen, key=lambda r: -r['pen']): print(f"   {r['a']:16s} {r['b']:16s} {r['what']:34s} {r['pen']:.3f} mm  ({r['where']})")
by = collections.defaultdict(list)
for r in rows:
    if r['gap'] is not None: by[r['what']].append(r)
print('\nSmallest gap per kind of contact (mm, 70% part sizes):')
for what, rs in sorted(by.items(), key=lambda kv: min(r['gap'] for r in kv[1])):
    m = min(rs, key=lambda r: r['gap'])
    print(f"   {what:42s} {m['gap']:.3f}   e.g. {m['a']} / {m['b']}")
close = [r for r in rows if r['what'] == 'separate parts' and r['gap'] is not None and r['gap'] < 0.25]
print('\nSeparate parts closer than 0.25 mm:', len(close))
for r in sorted(close, key=lambda r: r['gap']): print(f"   {r['a']:16s} {r['b']:16s} {r['gap']:.3f}")

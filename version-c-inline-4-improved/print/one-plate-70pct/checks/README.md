# How the 70% model was checked

Every check runs on the exact files in `../stl` (the first check confirms the meshes match byte for byte).

| Check | Result |
| --- | --- |
| Gear meshes (2D, real tooth outlines, 24 angles through a full tooth cycle) | No interference. Backlash 0.40 mm (pinion/42T) and 0.33 mm (shifted 14T/40T). Teeth reach 1.78 and 1.48 mm deep, 1–2 teeth always in contact. [gear_report.txt](gear_report.txt) |
| Every part against every other part (3D, bar at Output 1) | 158 touching or near pairs. Only contacts are parts resting on a face (pillar shoulders, bridge legs, selector bar on the plate tops); re-checked, none overlap. [v1.json](v1.json) |
| Shift parts (collars, forks, bar, washers) at Neutral, Output 2, Output 3 | No overlaps. Released dogs clear by 0.28 mm or more, collar vs back plate 0.71 mm or more. [v2_pos1.json](v2_pos1.json), [v2_pos2.json](v2_pos2.json), [v2_pos3.json](v2_pos3.json) |
| Shifting, fits, shafts, belt, smallest features | All pass. Worst-case dog overlap 0.65 mm engaged and 0.65 mm clearance released, including all selector and fork play. [functional_report.txt](functional_report.txt) |

Two design faults were found and fixed during this check (they affected the 1:1 model too):

1. The selector bar slots were 1.9 mm wider than the fork pegs, more than the 1.7 mm collar travel, so a shift could leave a dog half engaged. Pegs are now square, slots are sized to the peg plus 0.2 mm, and collar travel is longer.
2. The free-spinning dog gears and dog pulley could slide back into their collars. A glued washer behind each now traps them; the dog lugs moved outward so the collar passes around the washer.

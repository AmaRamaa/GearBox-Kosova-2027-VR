# Version C: printable hand-turned model (1:1)

A full-size, hand-cranked model of the inline-4 gearbox (version C). The gear teeth are real 20DP involutes at REV sizes. Turn the crank, slide the selector bar, and watch each output engage.

Every part was checked in a virtual assembly at all four selector positions (Output 1, Neutral, Output 2, Output 3). No parts collide, the gears mesh, and the dog lugs interleave when engaged.

**Want it on one plate?** [`one-plate-70pct/`](one-plate-70pct/) has the same model at 70% scale, with every part on a single 350 × 350 mm bed and the fits kept at full-size clearances.

## What to print

| File | Printer bed | Contents |
| --- | --- | --- |
| `bed_1_PLA.3mf` | 350 × 350 mm | Back plate (diagonal), gears, pulleys, flywheel, collars, forks, cranks |
| `bed_2_PLA.3mf` | 350 × 350 mm | Middle plate (diagonal), shafts, axles, pillars, spacers, end caps |
| `bed_3_PLA.3mf` | 350 × 350 mm | Front plate and selector bar |
| `bed_TPU_belt.3mf` | any | Optional belt ring in TPU (or use a 3 mm O-ring cord / rubber band) |

Individual STLs are in `stl/` if you want to reprint one part.
Total: 79 PLA parts, about 0.8 kg of PLA.

## Slicer settings (Creality Print, K2 Plus, PLA, 0.4 mm nozzle)

- Layer height: 0.16 mm for beds 1 and 2 (gear teeth), 0.2 mm for bed 3.
- Walls: 3. Top/bottom: 4 layers.
- Infill: 25 % (40 % if you want stiffer gears).
- Supports: off. Every part is designed to print without them.
- Brim: 3 mm on beds 1 and 2 helps the long diagonal plates stay flat.
- Everything is already oriented and placed. Open the 3MF, pick the K2 Plus profile, and slice.

## Other things you need

- Superglue (CA) for fixing gears to shafts.
- A 3 mm cord loop, rubber band or the TPU ring for the flywheel belt.
- String for the two climber spools.
- A pen to mark the four selector positions.

No screws are needed: square pillar pegs push into the round plate holes. Add a drop of glue if they are loose.

## Where each part goes on its shaft

Distances are measured from the **front end of each shaft**. "Glue" parts are fixed; "free" parts must spin or slide.

| Shaft | Parts, front to back |
| --- | --- |
| A (108.6 mm) | 42T gear at 10.9 mm (glue), spacer (free), 66T dog pulley (free, lugs toward the back), washer (glue, against the pulley with a paper shim), collar (slides, lugs toward the pulley), end cap at the back |
| B (108.6 mm) | 42T gear at 10.9 mm (glue), shifted 14T gear at 69.4 mm (glue), end cap at the back |
| C (108.6 mm) | 42T gear at 10.9 mm (glue), shifted 14T gear at 36.3 mm (glue), end cap at the back |
| I (81.2 mm) | 40T gear at 8.9 mm (glue), shifted 14T gear at 41.9 mm (glue), end cap at the back |
| F (108 mm) | End cap at the front, 22T pulley at 15.5 mm (glue), flywheel at 87.0 mm (glue, after the back plate is on) |
| Output 2 and 3 (86.9 mm each) | End cap in front of the bridge, spacer (free), 40T dog gear (free, lugs toward the back), washer (glue, against the gear with a paper shim), collar (lugs toward the gear), spool at 53.5 mm (glue, after the back plate), end cap |
| Motor axles (42.6 mm × 3, 33.6 mm × 1) | Pinion at 20.9 mm (glue). The short axle goes in the motor position furthest from the flywheel |

## Assembly

**Illustrated step-by-step guide with a picture for every step: [ASSEMBLY.md](ASSEMBLY.md).** Short version:

1. Glue the fixed gears onto shafts A, B, C, I and F, and the pinions onto the motor axles, using the table. Let them dry.
2. Push the 8 short pillars into the front plate.
3. From the inside, put shafts A, B and C (42T gears inside) and the 4 motor axles (pinions inside) through the front plate. Turn them so every pinion meshes with the 42T gears on both sides.
4. Lower the middle plate onto the pillars, threading shafts A, B, C and three of the axles through it.
5. Push the 8 long pillars and the 2 bearing bridges into the back of the middle plate.
6. On shaft A, slide on the spacer, then the dog pulley, then a collar.
7. Put shaft I through the middle plate so its 40T meshes with the 14T on shaft C. Put shaft F through the middle plate and loop the belt over both pulleys.
8. Push the Output 2 and Output 3 shafts back-to-front through their bridges. Add the front end cap, then the spacer, dog gear and collar.
9. Clip a fork onto each collar groove from above.
10. Lower the back plate onto the pillars, threading every shaft through it.
11. Glue on the flywheel and spools, then the back end caps.
12. Glue the crank discs onto the front of the motor axles. The disc with the handle goes on the motor next to the flywheel.
13. Set the selector bar on top. Its lips go in front of the middle plate and behind the back plate, and each fork peg drops into its slot.

## Using it

The selector bar has four positions, 11.4 mm apart. Mark them on the plate edge with a pen.

| Bar position | Output engaged |
| --- | --- |
| Pushed fully toward the Output 3 end | Output 1, flywheel (1:1) |
| One step toward the flywheel | Neutral |
| Two steps | Output 2, climber fast (8.57:1) |
| Pulled fully toward the flywheel | Output 3, climber strong (24.5:1) |

Turn the crank and watch which shaft moves. In a robot, the motors stop before every shift. Do the same here: stop cranking, slide the bar, then crank again. If the dogs land tooth-on-tooth, wiggle the crank a little and they drop in.

## Fit tips

- Shafts are printed at 12.5 mm across flats, slightly under 1/2 in, so the printed parts slide.
- If a collar is tight on its shaft, lightly sand the shaft. If a fixed gear is loose, glue it.
- If the bar slides too freely, add a small rubber band across it as a detent.

## Differences from the real gearbox

- Motors are replaced by crank discs the size of a NEO Vortex.
- The selector bar is pushed by hand, with no servo.
- The flywheel belt uses 66T and 22T pulleys. An 18T pulley is too small for a 1/2 in hex shaft, so the real design should use these sizes too. The ratio is still 1:1.
- Ratchets and encoders are left out.

## Regenerating the files

The `source/` folder has the Python scripts that make every part (numpy only):
`python3 build.py out` writes the STLs and runs the fit check, then `python3 layout.py` packs the beds.

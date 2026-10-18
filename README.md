# GearBox Kosova 2027 VR

Shifting gearbox concepts for FRC 2027, built from REV ION parts (20DP steel gears on 1/2in hex, NEO Vortex motors).
One motor pack drives a flywheel or a climber, picked by dog collars, with a neutral position.

Each folder has an interactive 3D model. Open its `index.html` in a browser (it needs internet to load three.js).

**Want to hold it?** [`version-c-inline-4-improved/print/`](version-c-inline-4-improved/print/) has a full-size, hand-cranked printable model of version C: STLs, ready-to-slice 3MF beds for a 350 mm printer (Creality K2 Plus), and an assembly guide. A [70% one-plate version](version-c-inline-4-improved/print/one-plate-70pct/) puts every part on a single bed.
Drag to rotate, scroll to zoom, and click the gear buttons to watch a shift: stop motors, move collar, spin up.

These are layout models for checking spacing, ratios and power flow. They are not CAD files.

## The versions

| Version | Layout | Motors | Outputs | Shifting |
| --- | --- | --- | --- | --- |
| [A](version-a-two-output/) | 4 shafts in a cluster | 2–4 NEO Vortex | Flywheel + one climber shaft with 2 speeds | 2 dog collars, pneumatic |
| [B](version-b-inline-4/) | 9 shafts in one line, flat | 4 NEO Vortex in a row | Flywheel, climber fast, climber strong | 3 dog collars, pneumatic |
| [C](version-c-inline-4-improved/) | Same as B, refined | 4 NEO Vortex in a row | Flywheel, climber fast, climber strong | 1 servo + selector bar |
| [D](version-d-hyperdrive/) | C plus a camshaft on top, planetary, cycloid, differential | 4 NEO Vortex in a row | Flywheel (2 speeds), 2 climb hooks, haul, boost, park | Servo camshaft, 7 positions, synchronizers |
| [E](version-e-fgc/) | **FGC kit only**: pillow blocks on 15 mm extrusion | 2 HD Hex + UltraPlanetary 4:1 | Flywheel, climb fast, climb strong | 1 Smart Robot Servo + sliding 72T gear |
| [F](version-f-dual-differential/) | **FGC kit only**: two spur differentials built from kit gears | 4 HD Hex + UltraPlanetary 5:1, in 2 groups | Flywheel and climber, separately or both at once | No shifter: the motor speeds pick the output. Servo is a hang lock |

## Ratios (NEO Vortex, 6,784 RPM free)

Torque assumes 4 motors at a 40 A current limit and 95% efficiency per stage. Pull assumes a 1.25in winch spool.

| Version | Output | Overall ratio | Free speed | Torque | Pull |
| --- | --- | --- | --- | --- | --- |
| A | Flywheel (Gear 1) | 1:1 | 6,784 RPM | 2.3 Nm | – |
| A | Climber fast (Gear 2) | 12:1 | 565 RPM | 26 Nm | 167 kgf |
| A | Climber strong (Gear 3) | 24.8:1 | 274 RPM | 54 Nm | 345 kgf |
| B | Flywheel (Output 1) | 1.125:1 | 6,030 RPM | 2.6 Nm | – |
| B / C | Climber fast (Output 2) | 8.57:1 | 791 RPM | 19.6 Nm | 126 kgf |
| B / C | Climber strong (Output 3) | 24.5:1 | 277 RPM | 53 Nm | 341 kgf |
| C | Flywheel (Output 1, belt) | 1:1 | 6,784 RPM | 2.3 Nm | – |
| D | 1 Flywheel spin-up (planetary low) | 2.67:1 | 2,544 RPM | 6.0 Nm | – |
| D | 2 Flywheel cruise (planetary direct) | 1:1 | 6,784 RPM | 2.3 Nm | – |
| D | 3 Climb (differential, 2 hooks) | 8.57:1 | 791 RPM | 9.6 Nm per hook | 2 × 62 kgf |
| D | 4 Haul (cycloidal 8:1) | 24:1 | 283 RPM | 52 Nm | 333 kgf |

## Version A: two outputs

- Shaft A (input) carries a 42T gear for each motor pair, plus 60T and 30T dog gears.
- Collar A picks flywheel, neutral or climber. Collar D picks the climber speed.

| Mesh | Gears | Center distance |
| --- | --- | --- |
| Motors → A | 14T pinion → 42T | 1.400 in |
| A → F (flywheel) | 60T dog → 20T | 2.000 in |
| A → C | 30T dog → 72T | 2.550 in |
| C → D fast | 30T → 50T dog | 2.000 in |
| C → D strong | 18T → 62T dog | 2.000 in |

## Version B: inline-4

- All shafts are on one line, so the gearbox is only as tall as a motor: about 12.6 × 2.9 in.
- The 4 motors share one gear row. Each 14T pinion meshes the 42T gears on both sides of it, so all motors are locked together.
- A middle plate splits the box. Output shafts sit directly behind motors.
- Every mesh is 1.400 in: 14T pinion + 42T, or 14T/15T rounded-hex gears (profile-shifted to 16T) + 40T.

| Path | Gears |
| --- | --- |
| Gear row | 4 × 14T pinions, 3 × 42T (shafts A, B, C) |
| Flywheel | A 40T dog → F 15T |
| Climber fast | B 14T → O2 40T dog |
| Climber strong | C 14T → I 40T, I 14T → O3 40T dog |

## Version C: inline-4, improved

Changes from B:

1. **Selector bar.** A flat bar along the top edge has an angled slot for each fork. One servo slides it through 4 positions: Output 1, Neutral, Output 2, Output 3. Only one output can ever be engaged, and no pneumatics are needed.
2. **Belt-driven flywheel.** A GT2 3mm belt, 66T pulley on A to 22T on the flywheel shaft, gives a true 1:1. (An 18T pulley is too small to fit a 1/2in hex shaft, so 66T/22T is the smallest pair that works.) Center distance is about 3.4 in, so roughly a 103-tooth (310 mm) belt; set the final distance from the belt you buy.
3. **Bearing bridges.** Output 2 and Output 3 shafts start behind row 2, which removes the 1.5 mm rubs in version B.
4. 3-tooth chamfered dogs, pocketed plates and a 1/8in middle plate.
5. Encoders on both climber outputs and a position sensor on the selector bar.

Plate size: about 13.8 × 2.9 in.

## Version D: Hyperdrive (the over-engineered one)

Everything from C, plus every mechanism we could justify, and some we couldn't.

- **Camshaft shifter.** An engine-style camshaft runs along the top, turned by a servo with an absolute encoder. Six cams push the three forks, the planetary brake, the direct clutch and the park pawl through 7 positions: P, N, 1, 2, 3, 4, B. Positions sit 51.4° apart, so shifting rolls through the gears in order like a motorcycle.
- **Synchronizer cones** on all three dog clutches match speeds before the dogs lock, so the motors keep running during shifts.
- **2-speed planetary on the flywheel** (sun 36T, planets 12T, ring 60T). A band brake on the ring gives 2.67:1 for fast spin-up; a direct clutch locks it at 1:1 to shoot.
- **Boost (B).** Keeps the spun-up flywheel connected while the climber hauls. A 1 kg, 4 in flywheel at 6,784 RPM stores about 326 J, enough on its own to lift a 70 kg robot about 0.47 m. A slip clutch on the 66T pulley protects the belt.
- **Cycloidal 8:1 final drive** (8 lobes, 9 pins) on the haul output, coaxial with shaft C. It replaces version C's shaft I and two gear stages.
- **Open differential** on the climb output drives two spools, so both hooks pull with the same force even when one side touches first.
- **Park pawl** on shaft B locks the whole gear row (P).
- The camshaft sits above the plates, so D is about 0.7 in taller than C.

Honest note: this is a showcase of mechanisms, not a recommendation. Each feature adds weight, parts and failure points; version C is the one to build for a season.

## Version E: FIRST Global (FGC) kit build

Version E is the one to build for FGC. It uses only parts from the FIRST Global REV DUO kit, plus parts you cut from kit stock. No custom dog gears, no pneumatics, no belts, no machined plates.

- **Motors:** 2 HD Hex motors, each with an UltraPlanetary 4:1 cartridge, meshing one input shaft through 45T gears.
- **Shifter:** a single 72T plastic gear slides along the 5 mm hex input shaft between four lanes: Flywheel, Neutral, Climb fast, Climb strong. It is carried by two 15mm Plastic Motion Brackets with through-bore bearings and pushed by one Smart Robot Servo through a short polycarbonate link. One gear can only mesh one partner, so two outputs can never engage together.
- **Frame:** two walls of 15 mm extrusion. Bearing pillow blocks slide along the row bars, so every shaft sits at the exact gear centre distance (REV plastic gears are module 0.75: centre distance = 0.375 mm × total teeth).
- **Shifting:** stop the motors, slide the gear, spin up. File a small chamfer on the slider's teeth and on the entry face of the gears it slides into.

| Output | Gears | Ratio | Free speed | Stall torque (2 motors) |
| --- | --- | --- | --- | --- |
| Flywheel | 72T → 30T, 2 × 90 mm grip wheels | 1.51:1 | 3,979 RPM (18.8 m/s) | 0.27 Nm |
| Climb fast | 72T → 125T, chain 15T → 54T | 22.6:1 | 265 RPM | 3.9 Nm (≈16 kgf at half stall, 25 mm spool) |
| Climb strong | 72T → 125T, 45T → 125T, chain 15T → 54T | 62.8:1 | 96 RPM | 10.2 Nm (≈41 kgf at half stall) |

Shaft positions (mm, input shaft at 0,0): F (−38.25, 0), CF (73.88, 0), CS (43.10, −60), CS2 (106.85, −60), motors (0, ±33.75). Lanes along the shafts (mm from the front wall): motor gears 10, Flywheel 37, Neutral 54, Climb fast 71, Climb strong 88. The parts list and cut list are in the 3D page's panel.

Based on the 2024 FIRST Global kit list ([REV BOM](https://revrobotics.com/content/docs/REV-45-1188_FIRST_Global_Kit_2024-Visual_BOM.pdf)); check your 2027 kit and the game manual's motor and modification rules before building.

## Version F: FGC dual-differential (the "diffy" one)

Version F uses 4 of the kit's HD Hex motors and **never shifts**. It works like a differential swerve module: two motor groups feed two differentials, and the speeds you give the groups decide which output turns.

- **Group A** (2 HD Hex, 5:1 cartridges) drives shaft A. **Group B** (2 HD Hex) drives shaft B.
- **Differential 1** gets A and B by gear, so its carrier turns at **(A + B) ÷ 2**. It drives the flywheel.
- **Differential 2** gets A by gear but B by chain. A chain keeps the direction where a gear reverses it, so its carrier turns at **(B − A) ÷ 2**. It drives the climber.
- Run A and B the same way: all 4 motors drive the flywheel, and differential 2's planets spin in place, so the climber stays still. Run them opposite ways: all 4 motors climb, and the flywheel stays still. Any mix runs both at once. Both outputs share one speed budget: |fly| + |climb| ≤ 100%.
- **Spur-gear differentials from kit parts.** Each one has two 45T suns on separate half-shafts. Two 125T gears, drilled, act as the carrier plates. Three pairs of 30T planets sit between them: planet 1 meshes sun 1, planet 2 meshes sun 2, and the two planets mesh each other.
- **Hang lock.** A Smart Robot Servo holds a polycarbonate pawl away from C2's 125T, and a rubber band pulls it in. When the robot is disabled at the end of the match the servo goes limp, the pawl drops in and the robot stays up.

| Output | Gears | Ratio | Free speed | Stall torque (4 motors) |
| --- | --- | --- | --- | --- |
| Flywheel | diff 1 carrier 125T → 30T, 2 × 90 mm grip wheels | 1.26:1 | 4,779 RPM (22.5 m/s) | 0.39 Nm |
| Climber | diff 2 carrier 125T → 125T, 2 × 30T → 2 × 125T, chain 15T → 26T, 25 mm spool | 37.8:1 | 159 RPM (0.21 m/s rope) | 10.5 Nm (≈43 kgf at half stall) |

Shaft positions (mm, between the motor shafts A and B): A (−20.40, 0), B (20.40, 0), diff 1 (0, 50), diff 2 (0, −50), F (0, 108.13), C (93.75, −50), C2 (123.39, 0), spool S (123.39, 108.13). Lanes along the shafts (mm from the front wall): motor gears 10, A's 72T 30, front carrier 48, sun 1 66, middle 84, sun 2 102, rear carrier 120, B's 72T 138, chains 175 (behind the back wall). Every clearance was checked; the tightest is 3.5 mm, between the carriers and shafts A and B.

Building it:

1. Clamp two 125T gears together and drill them as a pair. Open the centre to the Through Bore Bearing's outside diameter and press a bearing in. Then drill 6 bearing holes on a 56.25 mm circle: 3 pairs 120° apart, with the 2 holes of a pair 22.5 mm apart.
2. All 3 planet pairs mesh, because 120° steps land on whole sun teeth (checked in the model).
3. Keep shafts A and B bare between the carriers, with no collars there.
4. The climb stage uses two 30T and two 125T side by side, for 30 mm of tooth face.
5. Run both groups with encoder velocity control, so the output that should be still doesn't creep:

```java
// fly, climb in -1..1 (|fly| + |climb| <= 1)
double a = fly - climb, b = fly + climb;
double s = Math.max(1, Math.max(Math.abs(a), Math.abs(b)));
groupA1.setVelocity(a / s * 2800); groupA2.setVelocity(a / s * 2800);   // HD Hex: 28 counts per motor turn
groupB1.setVelocity(b / s * 2800); groupB2.setVelocity(b / s * 2800);
```

It uses 49 gears (version E uses 9): 27 of the kit's 32 30T and 7 of its 8 125T. The full parts and cut lists are in the 3D page. If your kit has no 26T sprocket, chain 15T → 54T gives 78.5:1 instead (76 RPM, more pull).

## Parts

REV ION parts used across the versions:

| Part | REV part no. |
| --- | --- |
| NEO Vortex | REV-21-1652 |
| SPARK Flex | REV-11-2159 |
| Vortex Shaft – 15T Spline | REV-21-2849 |
| 20DP pinion, 15T spline, 14T | REV-21-4010 |
| 20DP gear, 1/2in rounded hex, 14T / 15T | REV-21-3361 / REV-21-3362 |
| 20DP gears, 1/2in hex, 18T–28T | REV-21-1920 to REV-21-1925 |
| 20DP gears, 1/2in hex, 30T–58T | REV-21-1926 to REV-21-1940 |
| 20DP gears, 1/2in hex, 60T–80T | REV-21-1941 to REV-21-1951 |

Not in REV ION: dog gears, dog collars, shift forks, the selector bar (version C) and the dog pulley on shaft A. These are machined or bought from another vendor.

## Build notes

- Always set current limits. Without them, 4 motors at stall can put about 300 Nm on the strong climber shaft.
- Use steel shafts wherever climber torque passes through.
- Each climber output needs a ratchet so the robot keeps hanging after the match.
- Check the 2027 game manual for motor and pneumatics rules before freezing a design.

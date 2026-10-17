# GearBox Kosova 2027 VR

Shifting gearbox concepts for FRC 2027, built from REV ION parts (20DP steel gears on 1/2in hex, NEO Vortex motors).
One motor pack drives a flywheel or a climber, picked by dog collars, with a neutral position.

Each folder has an interactive 3D model. Open its `index.html` in a browser (it needs internet to load three.js).
Drag to rotate, scroll to zoom, and click the gear buttons to watch a shift: stop motors, move collar, spin up.

These are layout models for checking spacing, ratios and power flow. They are not CAD files.

## The three versions

| Version | Layout | Motors | Outputs | Shifting |
| --- | --- | --- | --- | --- |
| [A](version-a-two-output/) | 4 shafts in a cluster | 2–4 NEO Vortex | Flywheel + one climber shaft with 2 speeds | 2 dog collars, pneumatic |
| [B](version-b-inline-4/) | 9 shafts in one line, flat | 4 NEO Vortex in a row | Flywheel, climber fast, climber strong | 3 dog collars, pneumatic |
| [C](version-c-inline-4-improved/) | Same as B, refined | 4 NEO Vortex in a row | Flywheel, climber fast, climber strong | 1 servo + selector bar |

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
2. **Belt-driven flywheel.** A GT2 3mm belt, 54T pulley on A to 18T on the flywheel shaft, gives a true 1:1. Center distance is about 3.4 in, so roughly a 95-tooth (285 mm) belt; set the final distance from the belt you buy.
3. **Bearing bridges.** Output 2 and Output 3 shafts start behind row 2, which removes the 1.5 mm rubs in version B.
4. 3-tooth chamfered dogs, pocketed plates and a 1/8in middle plate.
5. Encoders on both climber outputs and a position sensor on the selector bar.

Plate size: about 13.8 × 2.9 in.

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

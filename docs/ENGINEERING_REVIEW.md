# Cruiser III friction-drive retrofit — V0.4 engineering feasibility review

**Date:** 20 November 2026  
**Status:** Unoccupied research concept. **NOT safe or cleared for a person to ride.**  
**Reference chair:** Drive Medical Cruiser III, nominal 18-inch seat version with 24-inch rear wheels.  
**Architecture:** Two independent 50-mm friction rollers against original solid rear tires, gearmotors inboard, two manual release mechanisms, spring-preloaded sliding carriages, user joystick and under-seat power electronics.

## Executive conclusion

**Conditionally plausible on clean, dry ground in a narrow nominal operating envelope. Not viable as a safe occupied device in its present configuration.** Two motor friction rollers theoretically generate enough force to move a 120 kg loaded wheelchair at about 3 km/h and to climb a 5% grade with moderate acceleration *if* roller-tire friction remains around the illustrative 0.6 coefficient and normal preload remains near 140 N per roller. With a lower illustrative coefficient of 0.15, a 5% downhill controlled stop fails. On a 5% downgrade, complete loss of electrical braking causes the unbraked system to accelerate. The existing manual wheel locks are parking locks, not emergency running brakes.

The high-detail CAD is a real STEP B-rep assembly, rebuilt from the base Cruiser III reference and geometric primitives matching some published industrial part dimensions. It has **456 valid solids** (145 base + 311 retrofit/details). **It is not an exact as-built CAD model**: the wheelchair frame has not been physically measured, the complete NFP motor mounting drawing is missing, and enclosure and clamp geometry remain approximations.

## Source-traceable dimensions

| Item | Current CAD dimension | Evidence / confidence |
|---|---:|---|
| Cruiser III rear wheel | 24 in / 609.6 mm | Manufacturer product listing (wheel size; assumed configuration) |
| Cruiser III seat | 18 in nominal | Manufacturer listing K318DDA-SF |
| Front caster | 8 in | Manufacturer listing |
| Frame tubular material and exact wall | **Unknown** | Base 22-mm nominal OD is a visual estimate, not a physical measurement |
| NFP-42GP-775-EN motor diameter | 42 mm | Published motor family specification |
| NFP 13:1 gearbox length | 43.5 mm | Published motor family specification |
| Motor output shaft | 8 mm D-cut x 22 mm | Published motor family specification |
| RS775 can length | 66.7 mm | Typical RS775 size reference; not confirmed specific assembly drawing |
| Encoder outer length and flange PCD | **Assumed** | Diagrammatic CAD only, not known product fit |
| Two 6000-2RS radial bearings per module | 10 x 26 x 8 mm each | Standard bearing boundary dimensions |
| Intermediate roller axle | 10 mm nominal steel shaft | Proposed custom, not sourced |
| Friction roller | 50 mm OD x 34 mm width | Proposed; tire material, tolerances and tread untested |
| Primary brace | 20 x 25 x 2 mm aluminum rectangular tube | Proposed stock-section geometry; actual 6061-T6 grade not confirmed |
| Battery shell | 174 x 96 x 76 mm | Placeholder envelope; no selected battery part has been verified |

## Mechanical arrangement

Two modules are positioned near the upper rear quadrant of the large tires, with geared motors inside the tire planes. Each tire-facing roller is carried on a separate 10-mm axle and two 6000-2RS bearings. This separates much of the tire contact bending load from the 8-mm motor output shaft, which couples to the drive axle. Two split, bolt-on clamps anchor each module to the chair's nominal rear back-post tube. Four hollow braces per side connect the stationary clamp mounts to an engagement carrier. Two radial guide rods per side locate the sliding drive carriage; the spring and quick-release cam in the CAD are *non-functional concepts* until their kinematics, manufacturing tolerances and forces are engineered and tested.

A 15-mm released position is represented by a separate STEP assembly. The rollers move radially outward, while stationary frame clamps remain fixed. This proves geometric displacement but **not** a working or reliable quick-release mechanism.

The metal shaft, mounts, fasteners and braces are intended to be manufactured from conventional metal stock. Printing is reserved for non-loadbearing cases, adapters, shields, joystick shell and cover parts until tested. The STL exports are appearance/fit-test candidates and must **not** be treated as installation-ready components.

## Propulsion calculation

Assume loaded system mass m=120 kg, gravitational acceleration g=9.81 m/s², a 5% grade, rolling resistance coefficient Crr=0.020 (not measured) and acceleration a=0.30 m/s².

- Steady uphill force: F = mg(0.05+0.020) = **82.40 N**.
- Acceleration uphill: F = m[g(0.05+0.020)+0.30] = **118.40 N**.
- At 50-mm roller diameter (radius 0.025 m), output torque per motor during the acceleration case: (118.40/2)*0.025 = **1.48 N·m**.
- For 3 km/h (0.8333 m/s), each roller must spin at **318.31 RPM** and each 24-inch rear wheel at **26.11 RPM**.
- Mechanical power delivered to the wheels at steady 5% climb is 82.40*0.8333=**68.67 W** total (excluding gearbox, motor and electronic losses).

The NFP candidate is advertised at **2.94 N·m rated output torque at 300 RPM**, with **630 RPM no-load speed**. A simple linear interpolation (not a measured torque-speed curve) yields ~**2.78 N·m** available at 318 RPM, giving ~**1.88× nominal torque margin** against the acceleration case. The motor's thermal duty cycle, actual torque curve and enclosure temperature are unknown. Its listing also pairs `Max 150W` with rated-current upper-bound values as high as `≤13A at 24V`, which should not be used as a precise verified continuous electrical-power specification.

## Roller traction: governing condition

For two friction rollers, the maximum ideal tangential force is F_roller,max=2*mu*N, capped by the available motor torque. With nominal preload N=140 N per roller:

| Roller-tire friction coefficient (hypothetical) | Total contact force | 5% grade acceleration (needs 118 N) | 5% slope downhill 0.5 m/s² stop (needs 95 N) |
|---:|---:|---|---|
| mu=0.60 (illustrative dry) | 168 N | Pass | Pass |
| mu=0.30 | 84 N | Fail | Fail |
| mu=0.15 (illustrative wet) | 42 N | Fail | Fail |
| mu=0.10 | 28 N | Fail | Fail |

The minimum coefficient required for the acceleration case at this preload is mu ≥ 118.40/(2*140) = **0.423**. The corresponding dry minimum preload at mu=0.6 is **98.7 N per side**; at mu=0.15 it is **394.7 N** per side, which may be unacceptably high and would require validating tire deformation, shaft bearings, bracing and frame clamps. These are not measured friction values for the Cruiser III. The source research on pneumatic wheelchair anti-rollback rollers does not establish what an untested rubber-coated motor roller will achieve on the Cruiser III's *solid tire*.

**Spring sensitivity:** If we provisionally choose a 15 N/mm spring, 140 N preload implies ~9.3 mm compression. ±2 mm radial runout changes contact force by ±30 N, from 110 to 170 N; this remains purely a design hypothesis without measured wheel runout or spring testing.

## Dynamic stop and failure scenarios

A simple 1D time-step dynamic simulation (5 ms step, requested acceleration clamped at +0.30/-0.50 m/s², finite motor torque and friction saturation, no yaw or bumps) gives:

| 7-second scenario | Last speed | Travel distance | Observation |
|---|---:|---:|---|
| Start uphill, dry assumed friction | 3.00 km/h | 4.62 m | Reaches commanded speed |
| Start uphill, wet assumed friction | approximately 0 km/h | approximately 0 m | Cannot produce required drive force |
| Descend 5% at 3 km/h, command stop, dry | 0 km/h | 0.79 m | Stops in idealized model |
| Descend 5% at 3 km/h, command stop, wet | 1.60 km/h | 4.47 m | Still moving after seven seconds |
| Descend 5% at 3 km/h, controller/battery power lost | 10.42 km/h | 13.06 m | Accelerates uncontrollably in idealized model |

For power-off slope driving, available active brake torque = 0 and the net downhill acceleration in the model is g(0.05-0.02) = **0.2943 m/s²**. The chair's wheel locks are not automatically applied and must not be used as running brakes.

**Safety determination:** Motor reversal is viable for normal controlled deceleration if the roller retains traction, but neither it nor manual wheel locks provide reliable automatic power-off stopping. With the user-selected no-independent-brake architecture, **FAIL: not suitable for occupied slope use**. A person who needs electric assistance may not have the strength or dexterity to stop using the handrims. The safety case must be redesigned, not papered over with a nominal dry test.

## Shaft and bearing forces

Nominal roller normal force N=140 N. Tangential thrust on 5% grade while accelerating is F_t=59.2 N per side. Resultant R=sqrt(140²+59.2²)=**152 N** per side. Taking a 2× simplified dynamic multiplier gives **304 N** design reaction per side.

For a 10-mm shaft with bearing centers at y=253 and 273 mm and roller contact at y=297.5 mm:

- Bearing span = 20 mm; load overhang beyond outer bearing = 24.5 mm.
- Outer bearing reaction: **338 N** at nominal resultant; inner bearing reaction: **186 N opposite direction** (reverses reaction sign for overhung load).
- Shaft bending moment at outer bearing: 152*24.5 = **3724 N·mm**.
- Elastic nominal bending stress in an unkeyed solid Ø10-mm shaft: sigma=32*M/(pi*d³) = **37.9 MPa**, or **75.9 MPa** at 2×.
- Taking 250 MPa as an illustrative steel yield strength gives ~**3.3×** nominal yield ratio at 2× load, but does NOT cover keyways, torsion, radial fatigue, bearing L10 life, output coupling quality, shaft retention or misalignment.

## 3D solid finite-element support-member check

A **480-element, 1,000-node 3D linear elastic hexahedral mesh** was solved for a single 20 x 25 x 2 mm rectangular hollow tube with 205-mm free span, representative isotropic 6061-T6 aluminum material parameters E=69 GPa and nu=0.33. Fully fixed x=0 end, with **152 N transverse end load** distributed over the other end. The 152 N is already the 2× side reaction split over two effective members per side. This is a conservative allocation but does not model actual load sharing.

- Calculated 3D-FEA free-end deflection: **0.646 mm**.
- Maximum sampled element-center von Mises stress: **27.1 MPa** (mesh and element-center sampling underestimate local extremes).
- Euler-Bernoulli closed-form comparison: **0.666 mm deflection**, **32.8 MPa nominal root bending stress**.
- With representative 240 MPa yield, simplistic yield ratio is 240/27.1=**8.84**, but **NOT** an assembly safety factor.

**Major missing checks:** frame-tube crushing, clamp friction and slip, bored cross-section weakness at bolt holes, fatigue, joint eccentricity, torsion, roller pinch risk, anti-tip stability, curb contact, bridge collapse during folding and physical 3D load distribution. Passing the isolated tube model does not prove the assembled bracket is safe.

## Battery, controller and electrical system

At constant 3 km/h and 5% grade, wheel output requirement is 68.7 W. If the *total* battery-to-wheel efficiency ranges 35% to 70% and fixed electronics draw 8 W, predicted battery draw is roughly **106–204 W**. Using a hypothetical protected 25.6V/6Ah pack at 70% usable capacity (107.5 Wh), ideal constant-grade travel is **1.6–3.0 km**. This is an optimistic textbook energy model that excludes repeated starts, thermal derating, aging, variation in loaded terrain and high-power transient efficiency.

The motor listing contains a **24.5 A stall-current figure per motor**, making a combined fault demand potentially >40 A. The exact motor controllers, BMS, wiring, current limiting, fuses, charger and power-failure behavior are NOT selected or validated. A nominal 6Ah pack advertised with 15A discharge would not automatically be suitable for two unrestricted motors.

## CAD and software verification

- CAD source: `cad/build_high_fidelity.py`; parametric geometry based on `../cruiser_iii_base_cad_v02/cruiser_iii_parametric.py`.
- Full STEP `cad/CruiserIII_Retrofit_Detailed_V04.step` reimports as **456 B-rep solids**, all geometrically valid.
- Retrofit-only STEP (engaged) and released STEP exported separately.
- Both 50mm roller surfaces mathematically tangent to their associated 24in tire surfaces: computed zero radial gap (exact analytic idealization).
- Retrofit stays inside the modeled reference chair's lateral width: max half width base ~328.5 mm; retrofit ~325 mm.
- Selected component/base intersection screen: only expected joystick-on-armrest overlap remains after moving battery envelope away from base crossbraces.
- **17/17** unit tests passed for drive/braking equations, motor linear-envelope checks, CAD contact, fixed frame clamps, released-carriage travel and solid validity.
- No physical fit checks, environmental tests, full-carriage kinematic proof, full-chair nonlinear stress simulation or human trials performed.

## Next gates (do not skip)

1. **Measure actual chair**: several tube diameters/wall thicknesses, centerline frame coordinates, adjustable axle positions, folded envelope, wheel profile/runout and tire compound; replace guessed base geometry.
2. **Confirm motor drawings**: exact NFP 42GP motor/encoder length, PCD, mounting thread depth, shaft tolerance, torque-speed/current curves, thermal duty and rated speed under load. Also price equivalent parts from commodity suppliers.
3. **Bench traction rig, no occupant**: measure torque vs preload vs dry/wet/dust/worn solid tire under controlled speed and temperatures. Verify that 50mm tread does not wear tire or damage wheelchair components.
4. **Mechanical detailing**: design actual lever-cam latching, sliders, tolerance stack, spring preload adjuster, limit stops, couplings and bearing retention. Verify no hardware touches folding linkages.
5. **Frame/roller strength**: coupon tests; real bolt clamp strength and fatigue on real thin-walled wheelchair tubing; shaft flexure and bearing life.
6. **Electrical design**: real motor driver, current limiting, joystick plausibility, watchdog, BMS-thermal/fuse compatibility, safe power-loss response.
7. **Unoccupied ballast and brake testing**: straight, uneven ground, turn, slope, wet, electrical disconnect, slip, wheel locks parking, anti-tip and emergency stop. Benchmark relevant ISO 7176-1, -3, -14 methods.
8. **Occupant use remains prohibited** until independently resolved fail-safe stopping, measured frame geometry, qualified review and test evidence.

## Sources

- Drive Medical Canada, Cruiser III 18in K318DDA-SF official specifications: https://shop.drivemedical.com/ca/en/products/mobility/wheelchairs/standard-wheelchairs/cruiser-iii-wheelchair/p/K318DDA-SF
- Drive Cruiser III product/manual warning about wheel locks: https://easymedicalstore.com/content/manuals/Cruiser_III_hangtag.pdf
- NFP Motor, NFP-42GP-775-EN 24V model and 13:1 gearbox torque-speed table: https://nfpmotor.com/products/42mm-planetary-gear-motor/42mm-dc-planetary-geared-motor-with-encoder-model-nfp-42gp-775-en.html
- Xem Studio, 775 motor generic geometry: https://www.xemstudio.com/objects/775-dc-motor/
- Bearing 6000-2RS (10x26x8mm) reference: https://www.upgradebikes.co.uk/AdditionalDepartments/Footer-Content/Technical/SKF-Bearings
- Open-access roller-pressure and downhill anti-rollback experiment with *different pneumatic tires*: https://www.mdpi.com/2076-3417/15/23/12768
- ISO 7176-1 static stability: https://www.iso.org/standard/56817.html
- ISO 7176-3 brake effectiveness: https://www.iso.org/standard/53816.html
- ISO 7176-14 powered wheelchair control systems: https://committee.iso.org/standard/72408.html

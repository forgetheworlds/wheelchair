# PROJECT SPECIFICATION — Open-Source DIY Wheelchair Motorization Kit

**Project:** Compact dual-friction-drive retrofit for existing manual wheelchairs  
**Reference platform:** Drive Medical Cruiser III, 18-inch-seat / 24-inch-rear-wheel configuration  
**Version:** 0.4.1 | **Date:** 2026-11-20  
**Stage:** Engineering feasibility research; unoccupied prototype only  
**Authority:** This document states the intended product goal and its acceptance criteria. It does **not** certify the current CAD or hardware for human use.

## 1. Goal and motivation

Design and publicly document an **inexpensive, compact, easily installed, user-controlled electric conversion kit** for ordinary manual wheelchairs. The goal is to help wheelchair users or their caregivers convert an existing, properly fitted chair to joystick-controlled propulsion **without buying a costly new powered wheelchair**. This is primarily an **open-source, do-it-yourself accessibility effort**, not a retail product or profit-maximizing business. Potential commercialization is a separate future decision, not a current requirement.

The motivating hypothesis is that commodity motors/electronics, inexpensive mechanical stock, and 3D-printed noncritical parts can reduce cost and complexity versus existing commercial add-ons. The hypothesis must be established by an actual reproducible bill of materials and tested hardware—not by assumed supplier prices.

**North-star outcome:** An independent builder can obtain verified off-the-shelf parts, print the printable components, mount a compact reversible attachment to a supported wheelchair, and obtain controllable forward/reverse travel and turning, while retaining manual-push and parking functions **after an independently reviewed safety case has been demonstrated**.

## 2. Target users and boundaries

- Intended eventual users: owners of existing manual wheelchairs who benefit from powered propulsion, potentially including people with limited upper-body strength. The design must not assume the occupant can always stop by hand.
- Initial test platform: one specified Cruiser III configuration only; no claim of universal fit.
- Keep existing seat, frame, wheels, handrims, footrests and factory parking wheel locks intact.
- No drilling, welding, or permanent modification to the reference wheelchair in the intended design.
- No passenger testing until all mandatory safety gates below have been satisfied and appropriate clinical/engineering review is completed.
- This project is not autonomous navigation, robotics perception, or an AI wheelchair. It is basic direct user propulsion control.

## 3. Design priorities, in order

1. **Safety and control:** Prevent runaway, unintended acceleration, loss of control, or uncontrolled rolling. Provide safe stopping and parking despite credible electrical/mechanical faults. If this is not possible within cost, the budget target yields.
2. **Cost accessibility:** Aspirational **CAD $200 total DIY materials cost** for a reproducible build, excluding the base wheelchair, pre-existing tools, and the builder's labor. Show separately the actual landed cost including shipping, applicable taxes, 3D-printing material and waste. This target has **not** been demonstrated and must not be represented as the present cost of a safe kit.
3. **Compact appearance and packaging:** Slim inboard motor modules, no bulky protrusions beyond the rear-wheel envelope where practical, battery/electronics fitted without interfering with folding or transfers.
4. **Installation and reversibility:** Simple clamp-based attachment, quick engagement/disengagement, minimum adjustment and minimal specialist tools. Preserve normal attendant pushing and manual handrim use.
5. **Reproducibility and serviceability:** Open parametric CAD, editable source, clear documentation, replaceable commodity components, measurable tolerances, and straightforward maintenance.
6. **Comfort and user autonomy:** Low vibration/noise, intuitive joystick, predictable low-speed maneuvers and access to wheel locks.

## 4. Baseline performance requirements (provisional design targets)

| Requirement | Initial target | Status / evidence needed |
|---|---|---|
| Maximum commanded speed | ~3 km/h | Target only; closed-loop loaded tests required |
| Example range goal | ~3 km per charge | Target only; actual battery not selected |
| Initial mass for sizing | 120 kg chair + occupant + kit | Assumption; load envelope needs definition |
| Example grade analyzed | 5% incline | A calculation case, **not** an approved operating grade |
| Drive architecture | Two independently controlled powered friction rollers | Selected concept, not certified |
| Interface | Thumb/finger joystick on accessible armrest mount | Ergonomic/user testing needed |
| Release | Hand-operated retractable roller mechanism | CAD displacement exists; mechanics not proven |
| Installation | Bolt-on, reversible, no permanent alteration | Needs physical fit and clamp validation |
| Manual operation | Rollers disengaged; original handrims usable | Needs physical tests |
| Width | Avoid increasing overall chair width if feasible | CAD envelope screening only |
| DIY cost | Aspirational CAD $200 | Unproven; supplier-verified BOM required |
| Braking | Controlled motor deceleration **plus independently safe fault response** | **FAIL / unresolved**, see §8 |

Other performance targets—height/width tolerance, incline limit, turning radius, battery life, rated occupant mass, environmental conditions and installation time—must be established by testing and user feedback. Do not infer a permissible operating envelope from preliminary calculations.

## 5. Selected mechanical concept

- **Two friction-drive modules**, left and right, engage the existing large rear tire treads; differential speed allows steering. No replacement wheelchair wheels or third drive wheel.
- Nominal **50-mm-diameter** rollers; spring-preloaded sliding carriages and quick-release cam concept; motor modules tucked inside the rear-wheel profile.
- **24 V 42-mm-class planetary gearmotors** considered as candidates, not purchased/fully verified selections; separate roller axle with bearings to avoid loading the gearbox output bearing with tire preload.
- Custom metal force-bearing rails/shafts/clamps where necessary. 3D printing preferred for cases, spacers, fit adapters, ergonomic parts and noncritical guards; no assumption that printed polymer is suitable for fatigue-critical clamps or shafts.
- Battery/controller space planned under the seat, subject to folding linkage, ground clearance, axle adjustment, seat upholstery, and transfer access.
- Existing wheel locks are retained for **parking only** after stopping. They are not designed for moving downhill deceleration.

This architecture is a working design hypothesis. A 3D-looking part is not inherently dimensionally accurate: actual purchased motor drawings, wheels and wheelchair tubes must drive the final part geometry.

## 6. Electrical and control subsystem requirements

- Spring-return joystick with centered-input check, startup interlock and clearly identifiable power state.
- Independent left/right bidirectional motor control, compatible with verified motor stall currents, battery chemistry and fully charged voltage.
- Closed-loop speed measurement and current/temperature limits; controlled acceleration, deceleration and turning.
- Wiring protection including correctly rated fuses, BMS, connectors, charger and mechanical strain relief.
- Fault diagnostics for stuck joystick, controller reset, motor-driver short, broken encoder, brownout, undervoltage, disconnected power and dropped communication.
- Normal braking with opposing motor torque is permissible only while power, driver, contact force and roller traction are present.
- Emergency stopping and static holding performance must remain safe for credible failures. **The current motor-only/parking-lock design does not meet this requirement.** The exact fail-safe mechanism is deliberately unselected; its feasibility, architecture and cost must be researched and reviewed.

## 7. CAD quality and deliverable expectations

- Start from the standalone **Cruiser III base-wheelchair** model; retain separate frame, wheel, caster, seat, brake, armrest and footrest components.
- Real CAD solids with correct dimensions and mating relationships, not image-only visualizations or monolithic meshes.
- Parametric, editable source model with meaningful component names and adjustable constraints, plus STEP assembly, STL for appropriate printable components, and view-only renders/GLB.
- Subassemblies: left drive, right drive, carriage/engagement mechanism, mechanical mounts, joystick, battery/controller packaging and original wheelchair reference.
- Model each purchased part from its supplier drawing when available; mark guessed dimensions and indicate approximate envelopes otherwise.
- Verify clearances, bolt access, seat movement, handrim access, footrests, wheel locks, folding geometry, tire runout, shaft and bearing fit, and a serviceable wiring path.
- Organize files so another builder can regenerate CAD and calculations with dependency instructions and tests.

## 8. Engineering validation and mandatory safety gates

**Current results are computational screening, not occupant safety evidence.** Relevant findings in `docs/ENGINEERING_REVIEW.md`:

- Theory predicts 1.48 N·m per motor for 5% uphill acceleration at 120 kg using stated assumptions.
- The illustrated 42-mm motor may meet nominal torque demand; real sustained curves and thermal behavior are not yet verified.
- Under an illustrative dry roller friction coefficient of 0.6 and 140 N per roller, traction can satisfy the assumed scenarios. At coefficient 0.15, modeled traction drops to 42 N total and the downhill controlled-stop requirement is not met.
- Unpowered chair on a 5% downward grade can accelerate in the model. Handrim braking is not an acceptable presumed fallback for the eventual target population.
- Isolated hollow-brace 3D FEA predicts ~27.1 MPa sampled stress and 0.646 mm deflection for its specified boundary conditions; it does **not** cover frame clamps, fasteners, fatigue, rider loading, or chair frame integrity.
- 456 CAD solids and 17 software checks reportedly passed in V0.4. These checks validate geometry/algorithms, **not** assembly strength or real-world operation.

**Physical validation sequence (must be documented):**

1. Measure a real wheelchair; create a dimensional inspection sheet and identify load-carrying frame members and actual tire compound.
2. Obtain exact datasheets/engineering drawings and samples of motor, gearbox, bearings, couplings, battery and controller.
3. Bench-test the friction roller against the actual chair tire for traction, wear, heat, noise, wet/dust contamination, preloads and roller deformation—without a person.
4. Test mounts/bolts/tubes under static, repeated and shock loads, including proof-load tests of clamp slip, frame deformation and full carriage kinematics.
5. Validate electronics with hardware-in-the-loop and fault injection: stall, loss of power, frozen or disconnected joystick, failed MCU, failed brake command, BMS trip and controller faults.
6. Test the unoccupied wheelchair with instrumented ballast for drive, turning, slope, stopping distance, curb/obstacle interference, anti-tip stability, environmental variation and manual release.
7. Compare test methods with applicable wheelchair stability, brake and power/control standards (e.g. appropriate ISO 7176 parts), document gaps and obtain qualified independent safety and clinical assessment before any occupied trials.

**No-go conditions for occupied operation:** inability to stop/hold safely during credible faults; slipping rollers; unverified or damaged load-bearing tubes; loss of access to handrims/parking locks; wheel-interfering hardware; battery/drive thermal hazards; or missing appropriate supervised validation.

## 9. Project milestones and evidence of completion

- **M0 — Baseline reference:** base-chair CAD, dimension sources, uncertainty log and workshop measurement plan. **Partially done:** photo/spec-based model, not physically measured.
- **M1 — Architecture feasibility:** calculations, candidate parts, mock geometry and identified failure modes. **Partially done:** V0.4 math/FEA/CAD; stop and power-loss hazard open.
- **M2 — Manufacturer-specific CAD:** verified purchased-part and physical-chair measurements; integrated mechanical joint design; no collisions and documented tolerances.
- **M3 — Unoccupied bench prototype:** custom printed and metal components, instrumentation, reproducible assembly and traction/drive tests.
- **M4 — Unoccupied wheelchair verification:** instrumented loaded driving, stopping, faults, slopes, wet surface and frame/mount endurance tests.
- **M5 — Safety review:** independent mechanical, electrical and applicable wheelchair performance review; documented remediation, not just a positive demo.
- **M6 — Open-source release:** reproducible CAD, firmware, supplier-neutral BOM with actual 1-unit landed prices, build/fit/inspection procedures, test reports, limitations and safety warnings. Any instructions intended for occupant use follow validated review.

At every milestone, record **what was assumed, calculated, simulated, independently measured and verified**. Do not substitute a realistic render or a passing code test for the needed physical evidence.

## 10. Cost and sourcing approach

Search ordinary commodity motors, controllers, battery packs, bearings, aluminum stock, shafts, fasteners and switches, including Alibaba or comparable industrial vendors; avoid wheelchair-brand price premiums where generic parts are genuinely equivalent. Favor one-unit accessible ordering, clear dimensional drawings, available replacements and documented safety/quality data. For each quote record supplier, link, date, minimum quantity, currency, shipping, tax, warranty, and what is actually included. Supplier headline prices or MOQ bulk prices are **not** the one-off DIY builder's final cost.

Do not select a battery/driver solely to meet $200 if capacity, voltage, BMS discharge or motor-stall behavior are incompatible. Current 42-mm motor and 24V battery are **candidate families**, not a finalized procurement BOM.

## 11. Out of scope for the first prototype

- Autonomous driving, object detection, AI or robotics perception.
- Custom wheelchairs, custom seating or medical fitting.
- Universal compatibility across every chair brand and wheel diameter.
- Commercial sale, insurance reimbursement, regulatory market authorization or production tooling.
- Occupied demonstrations prior to verified safety gates.
- Claims of proven 3 km range, 5% grade performance, $200 all-in purchase price, full-chair stress safety or successful human operation.

## 12. Files and traceability

- `README.md`: package entry point.
- `docs/ENGINEERING_REVIEW.md`, `Cruiser_III_Engineering_Review_V04.pdf`: current analyses and limitations.
- `cad/build_high_fidelity.py`, `cad/cruiser_iii_base_parametric.py`: editable parametric source of the V0.4 assembly.
- `cad/CruiserIII_Retrofit_Detailed_V04.step`: B-rep full concept assembly.
- `cad/Friction_Drive_Modules_Detailed_V04.step`, `cad/Friction_Drive_Modules_Released_V04.step`: nominal engaged and disengaged concepts.
- `analysis/`: propulsion, traction, battery, shaft and isolated support-member simulation source/results.
- `tests/`: current software/geometry assertions; not a substitute for physical tests.
- `reference/base_wheelchair_v02/`: standalone original-chair geometry and workshop source/uncertainty notes.
- `reference/early_sourcing/`: archival sourcing notes (unverified and potentially stale; do not treat as a current BOM).

**Status statement:** The present design is a computational feasibility package. Its structural validation is incomplete and its credible fault stopping behavior is unresolved. It is **not** ready to carry a person.

# Design decisions and project intent

This summarizes decisions made during the initial discussion. It is a record of the intended project, not evidence that the engineering is solved.

## Why build it?

Powered wheelchairs and commercial power-assist systems can cost thousands of dollars. The project asks whether widely available motors, battery packs, small controllers and 3D-printed fittings can enable a far less expensive DIY conversion. The goal is to publish a reproducible design for people to build and improve, **not to sell kits as a business**. A CAD $200 total parts target is an engineering challenge, not a promise.

## Decisions in sequence

1. **Retrofit, don't redesign the wheelchair.** Start with an ordinary existing manual chair that is already fitted to its user.
2. **No powered replacement wheels.** Choose the friction-drive option: a roller presses against each existing large rear tire.
3. **Keep the chair compact.** Put motors near the inner rear-wheel area and electronics under the seat, with as little added width and bulk as possible.
4. **Avoid permanent modifications.** Adjustable clamps and a retractable roller contact mechanism should allow easy installation/removal and manual pushing.
5. **Print where sensible.** Joystick housings, alignment guides, shrouds and noncritical adapters are suitable candidates; load-bearing joints, motor shafts, fasteners and the most stressed brackets require proper engineered materials.
6. **Direct joystick control.** Two motors for independent left/right torque and steering. No sensors for autonomy, navigation or AI.
7. **Use generic components.** Source motors, rollers, battery, electronic controllers and fasteners from generic industrial, bike/scooter or robotics suppliers, including Alibaba, not wheelchair-marketed parts.
8. **Keep the wheel locks.** Existing locks can be used for parking after the chair stops. Motor braking handles normal deceleration while energized and traction is available. A separate bicycle braking system was considered but not selected for the baseline design.
9. **Do not assume hands are a safe fallback.** An eventual user might need powered assistance precisely because hand strength or dexterity is limited. The current concept does not automatically stop safely on power failure or loss of friction; this is a design blocker, not an optional enhancement.
10. **Build real CAD.** A dimensioned, editable base Cruiser III model first; then component-level friction-drive modules, with source scripts, separate solids, STEP assemblies and stress calculations. Visual realism alone is insufficient.

## Provisional geometry/performance assumptions

- One reference chair: Drive Medical Cruiser III, approximately 18-inch seat / 24-inch rear wheels.
- Two friction rollers, preliminary diameter 50 mm.
- Approximately 3 km/h target speed and 3 km tentative range.
- Combined wheelchair + person + kit sizing mass approximately 120 kg.
- 5% grades used for *engineering scenarios only*, not as a rated slope.
- 24 V, ~42 mm geared motor family studied, but no specific motor and battery/controller combination fully validated.

## Open engineering questions

- Roller preload, slip and tire wear (dry, wet, dusty, worn solid rubber tires)
- Failsafe stopping and holding on grades without relying on user strength
- Real wheel/frame clamp dimensions, folding and wheel-lock clearance
- Motor duty cycle and thermal margin, motor controller faults, safe lithium battery selection
- Fatigue, fastener security, corrosion and release mechanism durability
- User accessibility, joystick reliability, manual release usability, and ergonomic fit
- Whether the C$200 goal can be met without compromising safety

See [`../PROJECT_SPEC.md`](../PROJECT_SPEC.md) for requirements and safety gates.

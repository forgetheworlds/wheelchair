# DIY wheelchair friction-drive retrofit

**Goal:** Explore whether a compact, inexpensive and open-source motorization attachment could give people joystick control over an ordinary manual wheelchair, without purchasing a complete powered wheelchair. This is an accessibility project, not primarily a retail product.

**Cost ambition:** About **CAD $200** in DIY components, excluding the chair and tools. This has **not** been achieved or confirmed with landed supplier pricing.

## The concept

Two small geared motors drive rubber friction rollers against the existing large rear wheelchair tires. A user-operated joystick controls the motors independently for forward/reverse movement and turning. The modules should be removable or disengageable so the wheelchair remains manually usable. Motors should be tucked close to the wheels, with a small battery and electronics package under the seat.

## Decisions already made

- **Retrofit** an existing manual chair, rather than building a complete chair or replacing its wheels.
- Use **two friction-drive rollers**, not a separate drive wheel or expensive powered replacement wheels.
- **Compact, minimally clunky, removable**, with no permanent alteration to the wheelchair as a design target.
- **3D-print** covers, alignment jigs, and suitable adapters; retain engineered metal members in structural load paths.
- Use **generic, affordable components** from industrial/robotics/scooter suppliers and Alibaba rather than wheelchair-branded assemblies.
- Use a **basic joystick** and conventional embedded motor control, with no autonomous driving or AI.
- Retain existing wheel locks for **parking only**. Motor-controlled braking is the requested baseline. No independent wheel-mounted bike brake is included in the current prototype architecture.
- The reference chair is the **Drive Medical Cruiser III**, initially the 18-inch-seat variant with 24-inch rear wheels.

## CAD and research in this repository

- [Project specification](PROJECT_SPEC.md) explains goals, assumptions and unresolved safety gates.
- [Design decisions](docs/DESIGN_DECISIONS.md) records the reasoning.
- [CAD assembly generator](cad/build_high_fidelity.py) generates parametric B-rep parts and STEP exports with CadQuery.
- [Reference-chair CAD generator](cad/cruiser_iii_base_parametric.py) builds the base wheelchair from published dimensions and photo-estimated geometry.
- [Workshop measurements](reference/base_wheelchair_v02/SOURCES_AND_WORKSHOP.md) identifies measurements still needed from a real chair.
- [Preliminary Alibaba research](reference/early_sourcing/ALIBABA_SOURCING_V01_ARCHIVAL.md) records exploratory suppliers and assumptions.
- [Engineering assessment](docs/ENGINEERING_REVIEW.md) summarizes calculations and limitations.

Generated binary STEP, STL, GLB, PDF and rendering artifacts are available in the separately prepared project archive; this first GitHub commit contains the *editable generator source* and the engineering documentation. Generate solids locally using the CAD scripts after installing a compatible CadQuery environment.

## Important safety status

**Experimental design only. Not an approved wheelchair modification. Do not use to transport a person.** No hardware or human testing has taken place. Frame-clamp dimensions, tire friction, motor continuous ratings, battery performance, fatigue and real wheelchair clearances are not verified. Poor traction and power failure create unresolved stopping hazards; wheel locks are not dynamic brakes.

Numerical stress calculations and CAD validation are screening tools, **not physical stress tests or certification**.

The public repository's existing MIT license is retained. A software license does not demonstrate fitness for medical use.

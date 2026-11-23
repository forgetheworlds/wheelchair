# Engineering review (preliminary)

## Assumptions

Reference: 18-inch-seat Cruiser III with roughly 24-inch rear wheels. Combined mass approximately 120 kg. Two 50 mm rollers, 3 km/h target, 5% hypothetical grade. Assumed rolling resistance coefficient 0.02.

## Calculated performance

- Roller angular speed at 3 km/h: about **318 RPM**.
- 5% uphill force at constant speed: about **82.4 N total**.
- Nominal steady climb roller torque: about **1.03 N·m per motor**.
- Uphill acceleration case at 0.30 m/s²: approximately **1.48 N·m per motor**, including modeled losses.
- Downhill deceleration case (0.5 m/s² at 5% grade): approximately **95.3 N** total opposing force required.
- An example 42 mm planetary gearmotor has been evaluated based on published envelope and torque-speed data; supplier-specific data, mounting holes and continuous thermal rating remain unverified.

## Traction and safety findings

The friction interface can limit braking regardless of available motor torque. Under a hypothetical poor-contact coefficient of 0.15, the modeled rollers produce about 42 N total versus roughly 95 N demanded by the downhill stopping scenario. **That scenario fails.** Motor braking does not guarantee safe stopping during power loss or loss of roller traction. Existing wheel locks are for parking, not dynamic stops.

## Structural-screening results

The preliminary 3D finite-element model of a *single* hollow support member produced approximately **0.65 mm** displacement and **27 MPa** peak sampled von Mises stress under an assumed 152 N end load. This does **not** include actual frame clamps, bolt-hole stress concentrations, wheelchair tube loading, fatigue or complete chair stability.

## CAD validation boundaries

The previously generated concept STEP assembly reimported with 456 geometrically valid solids; selected idealized interference and geometry screens passed. That does not validate physical fit, real dimensions, stress, braking or ability to safely transport anyone.

## Next steps

Measure physical chair, get confirmed motor drawings, characterize tire friction (dry/wet), verify release/clamps and folding clearance, perform power-loss hazard engineering, then do **unoccupied instrumented tests**. No occupant tests without professional review and resolved safety case.

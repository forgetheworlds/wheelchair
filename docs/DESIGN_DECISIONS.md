# Design decisions

This is a record of choices made during the initial design discussion, not a validated product specification.

1. **Accessibility first.** The objective is an open-source DIY design that makes power assistance more affordable. Selling kits is not the primary goal.
2. **CAD $200 target.** Target generic components and 3D printing, but price is aspirational, not an established build cost.
3. **Use an existing manual wheelchair.** Keep the original seating, wheels, handrims, frame and parking locks. Start with the Cruiser III as the CAD reference, then consider compatibility.
4. **Friction drive selected.** Two independently controlled motor-driven rubber rollers press against the existing rear tires. No powered replacement wheels or standalone drive trolley.
5. **Keep it compact.** Tuck gearmotors near the inner rear wheels and electronics under the seat. Minimize added width and interference with folding, transfers and push handles.
6. **Tool-light reversible attachment.** Adjustable frame clamps, rapid installation/removal and disengagement for ordinary manual pushing are goals. The clamp/engagement hardware is not yet validated.
7. **Use 3D printing selectively.** Print covers, alignment fixtures and adapters, but use appropriate metals for stressed load paths and validate hardware.
8. **Joystick control.** Simple differential-drive motor commands, no AI.
9. **Brake decision.** User preferred motor deceleration plus existing parking locks instead of separate bicycle brakes. **This does not resolve power-loss stopping, roller slip or hill holding.** The user may not be able to brake by hand; no human testing is acceptable until the problem is engineered and assessed.
10. **Model and verify.** Parametric CAD, a photo-reconstructed base wheelchair, generic component research and numerical load tests are a starting point. Verify actual chair geometry and mechanical fit before fabrication.

Provisional targets: roughly 3 km/h, 3 km range, 50 mm diameter friction roller, 120 kg total design mass, and a 5% grade as an analysis scenario, **not a rated operating limit**.

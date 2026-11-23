# Research and references

These are working references used during exploratory design, not a validated parts list or independently verified manufacturer drawings. Prices and product variants may have changed.

## Wheelchair and dimensional references

- [Drive Medical Cruiser III — original product discussed](https://canadianmedicalstore.ca/products/cruiser-iii-wheelchair)
- [Cruiser III owners' manual — wheel locks, use, operation](https://4mdmedical.com/wp-content/uploads/2024/pdf/cruiser_iii_wheelchair_manual.pdf)
- Base-chair reconstruction provenance and the workshop measurements needed: [`../reference/base_wheelchair_v02/SOURCES_AND_WORKSHOP.md`](../reference/base_wheelchair_v02/SOURCES_AND_WORKSHOP.md)

## Image / drawing to editable CAD references

- [img2cad](https://github.com/YUI-TIEN/img2cad) — image-to-parametric-CAD loop and visual comparison
- [CAD Drawing to Model skill](https://github.com/Anson2251/cad-drawing-to-model-skill) — reconstruct from multiple measured views
- [Engineering Agent Skills](https://github.com/lukeoishi/engineering-agent-skills) — CAD and engineering verification workflows

The provided CAD was generated using **CadQuery and OpenCascade**, not directly by those repositories. External packages were not assumed to be available. The original wheelchair was reconstructed from published dimensions, photos and parts illustrations, **not** scanned or physically measured.

## Generic components and sourcing

- Preliminary Alibaba listings, costs, MOQ, compatibility concerns and supplier questions: [`../reference/early_sourcing/ALIBABA_SOURCING_V01_ARCHIVAL.md`](../reference/early_sourcing/ALIBABA_SOURCING_V01_ARCHIVAL.md)
- D60 24V motor family listing: https://www.alibaba.com/product-introduction/Manufacturer-D60mm-24-Volt-100w-150_1600637473223.html
- Cheap BTS7960 controller **rejected** for 8S LiFePO4 full-charge voltage incompatibility, see sourcing notes.
- Nominal 42 mm planetary gearmotor and encoder class explored for compact packaging, **not an approved part**; verified dimensional drawing, torque curve and physical part comparison still required.

## Simulations and limitations

- [`ENGINEERING_REVIEW.md`](ENGINEERING_REVIEW.md): propulsion, traction, braking and structural studies.
- [`../analysis/`](../analysis/): source of calculations, scenario assumptions, JSON results and isolated part finite element simulations.
- No full-chair finite element model, physical crash tests, occupied testing, endurance tests or medical-device conformity assessment.
- Proprietary reference imagery is not bundled; included renderings were generated from the project CAD.

## Next research tasks

Acquire measured wheelchair dimensions and approved part drawings. Compare low-cost generic motors at *continuous* output torque and speed, calculate battery discharge and thermal requirements, and devise/test a safe mechanical/electrical stopping strategy under power loss and wet-tire slip. Only then refine costs and mounting brackets.

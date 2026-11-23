# Cruiser III 18-inch — base wheelchair CAD reference v0.2

**Scope:** Only the base manual wheelchair. No motor, roller, battery, joystick, or retrofit geometry.

**Status:** A fully editable **parametric Python/CadQuery source assembly** with a STEP export of 145 named B-rep solids. This is a **visual and dimensional reference reconstruction**, **not** a manufacturer-authored CAD file, a measured installation drawing, or a certified structural assembly. The STEP geometry can be edited using standard CAD tools; it does *not* carry a native sketch/feature history into FreeCAD, Fusion 360 or Onshape. For fully parametric changes, edit the `Spec` dataclass and feature-building functions in `cruiser_iii_parametric.py`, then regenerate the STEP.

## Files

| File | Description |
|---|---|
| `cruiser_iii_parametric.py` | **Editable source of truth**: parameters and named CAD components |
| `Cruiser_III_base_reference.step` | CAD assembly: 145 separate named B-rep solids |
| `isometric.png`, `front.png`, `left_side.png`, `rear.png`, `top.png` | Rendered from the real CAD solids, not generative concept art |
| `four_views.png` | Combined review sheet |
| `render_views.py` | Render pipeline using CAD-generated meshes and VTK |
| `verify_cad.py` | Checks component names, bounding boxes, B-rep validity, and STEP round-trip |
| `verification.json` | Results of the last validation run |
| `components_and_parameters.json` | Readable manifest of each CAD component and primary dimensions |
| `SOURCES_AND_WORKSHOP.md` | Photo-to-CAD research, dimension provenance, and manual measurement plan |

## How to rebuild

From a Python environment with CadQuery 2.8, OCP and (for rendering only) VTK:

```bash
python cruiser_iii_parametric.py
python verify_cad.py
python render_views.py
```

Equivalent environment setup (requires access to PyPI):

```bash
python -m pip install 'cadquery==2.8.0' vtk
```

The sandbox already had CadQuery/OCP/VTK, so no additional packages were needed to generate this model. The external `img2cad` package was researched and its staged modeling/review principles were used, but the package could **not** be installed in this execution environment because access to external package hosts/DNS was unavailable. The project does **not** depend on it.

## Primary dimensions

**Manufacturer specifications** for a Cruiser III 18-inch-seat configuration (millimetres):

| Property | Value | Source confidence |
|---|---:|---|
| Seat width | 457.2 (18 in) | Published |
| Seat depth | adjustable 406.4–457.2 (16–18 in) | Published; model uses midpoint 419.1 |
| Seat height | adjustable 444.5–495.3 (17.5–19.5 in) | Published; model uses 482.6 |
| Backrest height above seat | 406.4 (16 in) | Published; actual post geometry estimated |
| Overall width | 660.4 (26 in) | Published |
| Overall height | 889.0 (35 in) | Published |
| Overall length with leg rests | 1066.8 (42 in) | Published |
| Rear-wheel diameter | 609.6 (24 in) | Retail specification |
| Front-caster diameter | 203.2 (8 in) | Manufacturer |

**Model measured envelope (from CAD, excluding precision tolerances):** 1052.3 mm length × 657.0 mm width × 892.0 mm height. Difference from published external envelope: −14.5 mm length, −3.4 mm width, +3.0 mm height. These matches **do not** establish internal geometric accuracy.

## What is estimated

Frame tube diameters; all exact tube centerline locations; wheel-hub/spoke shape; tire width; seat tubing/crossbrace positions; caster offset and swivel; axle mount and exact wheel lock mechanism; armrest release hardware; front footrest hinge, support tube and footplate geometry. All require physical measurement before planning motor mounting or producing load-bearing parts.

### Safety / usage

Do not manufacture frame components or mount a powered retrofit using these approximate dimensions. Verify every load path, rear-wheel clearance, folding path, support-tube geometry and parking-brake movement on an actual chair. This is for spatial planning only.

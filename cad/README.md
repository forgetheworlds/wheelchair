# Editable CAD sources

The design is **programmatic parametric CAD**, not a neural image mesh. Run the Python CadQuery generators to rebuild the model:

```sh
python -m pip install -r requirements.txt
python cad/build_high_fidelity.py
```

This source uses `cad/cruiser_iii_base_parametric.py` for the reconstructed reference chair. Generated STEP, GLB and STL exports can be opened in FreeCAD or other suitable CAD programs.

Important: source solids are individually named, but the geometry does **not** have a native sketch-feature history in Fusion 360 / FreeCAD. Frame geometry and some hardware are unmeasured estimates. The detailed motor casing is based partly on advertised dimensions; shaft/mounting details are not fully confirmed. Exported parts are **not print-ready or occupant-safe**.

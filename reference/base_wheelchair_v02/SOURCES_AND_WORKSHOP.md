# Sources, agent skills and measurement procedure

## 1. Image-to-editable-CAD skills researched

1. **img2cad** — https://github.com/YUI-TIEN/img2cad and https://yui-tien.github.io/img2cad/ — workflow: observe source photos; separate known/observed/estimated dimensions; plan parts; author parameterized OpenCascade solids; STEP export; compare rendered views and refine. Its photo-to-geometry examples are useful as workflow precedent, but do not demonstrate accurate reconstruction of this model from one image.
2. **CAD Drawing to Model Skill** — https://github.com/Anson2251/cad-drawing-to-model-skill — uses dimensioned multiple views to build source-based parametric solids and verify orthographic views.
3. **Engineering Agent Skills** — https://github.com/lukeoishi/engineering-agent-skills — emphasizes dimension authority and verified exported artifacts; noncommercial license is different from img2cad's MIT license.
4. **FreeCAD photo calibration tutorial** — https://blog.freecad.org/2026/04/12/tutorial-importing-and-using-scaled-reference-images/ — practical method: place orthogonal images on reference planes, calibrate from known distance, sketch over source images.
5. **Trace to Scale** — https://github.com/kcow3/trace-to-scale — measured photograph to scale DXF sketches; useful for flat brackets, but not sufficient for reconstructing curved multi-part wheelchair frame from a single perspective photo.

## 2. Wheelchair source evidence

* Drive Medical official specifications, 18-inch model: https://shop.drivemedical.com/ca/en/products/mobility/wheelchairs/standard-wheelchairs/cruiser-iii-wheelchair/p/K318ADDA-SF
* Drive official catalog PDF: https://shop.drivemedical.com/ca/en/products/mobility/wheelchairs/standard-wheelchairs/cruiser-iii-wheelchair/p/K318ADDA-SF/downloadPdf
* Manufacturer exploded parts diagram (illustration, not dimensioned shop drawing): https://www.grovemedical.com/Customer/grmein/Customerpages/specpages/K320ADDA-SF_Parts%20Diagram.pdf
* Reference product image: https://cdn.spinlife.com/images/product/52893.113614240119.png
* Retailer wheel diameters: https://mobility1st.ca/product/drive-cruiser-iii-wheelchair/

Variant caution: 16-, 18-, and 20-inch Cruiser III seat configurations exist, as do armrest and leg-rest variants. The retail page link supplied earlier does not establish which specific seat/arm/leg variant the CAD should match; this model deliberately assumes **18-inch seat with swing-away footrests**.

## 3. What was done in this iteration

**Observe:** inspected product photos, manufacturer catalog specifications, and the manufacturer exploded drawing; recorded major components and assembly arrangement.

**Model:** generated 145 separate named analytic CAD solids using CadQuery. Manufacturer exterior dimensions calibrate the model; occluded/internal geometry is expressly estimated.

**Review:** rendered actual solids from isometric/front/side/rear/top views. Verified STEP import round trip, all 145 solids, validity, and exterior dimension bounds.

**Not performed:** a pixel-perfect camera registration or quantitative image overlap check; the retail photos used were not accessible as downloadable binary files in the sandbox. No physical inspection was performed.

## 4. Workshop measurements needed before a useful retrofit mounting reference

Acquire a wheelchair identical to the intended test configuration. Photograph on a flat floor with a metric ruler or checkered calibration marker, from front/side/rear/top at roughly level camera angle and longer focal length to reduce perspective distortion. Measure with tape measure, calipers and a digital angle gauge:

1. Frame **tube outside diameter** at rear axle region, under-seat region and forward frame. Photograph/caliper each clampable straight length.
2. Actual **rear axle center** (X, Y and Z) relative to seat rear rail corner; measure axle diameter and fastener/bearing location.
3. Rear tire total diameter, **tire width**, material, tread profile and handrim spacing. Measure both sides.
4. **Available clearance inboard of each rear wheel** with chair loaded: between tire, cross-brace, side frame, spokes, hands and brake lever travel. Measure along the intended motor position.
5. **Cross-brace folding motion** and envelope throughout the complete folded-to-open path, not just when parked open.
6. Front caster swivel envelope and position in the adjustable-height settings.
7. Seat rail center-to-center spacing, front/back tube length, cushion and fabric clearance, brake lever sweep.
8. Check 16/18/20-inch chassis differences instead of assuming seat-width scaling applies to every part.

Record photos and measurements in a versioned table with uncertainty and measurement tool. Only then replace the estimated CAD parameters and position any retrofit clamps.

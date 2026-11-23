# Setup, Build & Simulator Guide — Cruiser III V1.0

---

## 1. Run the Interactive Browser Simulator

Works out of the box on macOS, Linux, and Windows directly in your web browser—no desktop OpenGL hacks required.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python sim/app.py
```

Open **http://localhost:8085/** in your browser:
- **Drive:** Click-drag the **2D Spring-Return Thumb Joystick** in the HUD **or** hold **`W`/`A`/`S`/`D`** (or **Arrow Keys**).
- **Speed Modes:** Click **`3 km/h`** / **`6 km/h`** / **`9 km/h`** (or press **`M`**).
- **Safety & Manual Mode:** Press **`E`** for E-Stop / FOC Electronic Hill-Hold; press **`R`** to retract rollers for 0-drag manual coasting.
- **Cameras:** Press **`V`** (or click **`Cam [V]`**) to cycle `Chase` → `Driver POV` → `Hero 3/4` → `Drive Detail` → `Explode View` → `Free Orbit`.
- **Interactive 3D CAD Exploded View:** Drag the **`Explode (0%–100%)`** slider (or click **`Explode (100%)`**) to expand all 10 CAD sub-assemblies live in 3D space.
- **Switch Worlds Live:** Click any world in the HUD (`Proving Ground`, `8.3% Max ADA Ramp`, `10% Steep Driveway`, `Wet Tile 5% Ramp`, `Downhill -8% Regen`, `Grass/Gravel + 4% Camber`).

---

## 2. Inspect or Edit the Finished CAD

- **Complete Assembly:** Decompress [`cad/CruiserIII_V10_Full.step.gz`](cad/CruiserIII_V10_Full.step.gz) (`gunzip -k cad/CruiserIII_V10_Full.step.gz`) to open the full B-rep STEP assembly in FreeCAD, Fusion 360, SolidWorks, or Onshape.
- **3D Printing:** Slice all 6 watertight STLs in [`cad/stl/`](cad/stl/) using the quantities, mirroring, and wall/infill settings listed in [`BOM.md`](BOM.md#2-3d-printed-parts-schedule-cadstl).

---

## 3. Mechanical Assembly (Zero Drilling or Welding)

1. **Press Bronze Bushings:** Press two `8 × 12 × 15 mm` sintered bronze sleeve bushings into each PA-CF `bldc_hub_slider_v10`.
2. **Mount 70 mm BLDC Hub Motors:** Slide each motor's stationary M8 flat-keyed axle into the slider's double-D anti-rotation slot and tighten the pinch bolt securely. *(Tip: score shallow diagonal chevron water-shedding sipes into smooth 78A PU sleeves if your vendor supplies un-grooved sleeves for wet traction.)*
3. **Assemble Linear Guide Rails:** Slide two `Ø8 × 160 mm` stainless rods and preload compression springs (`~15 N/mm`) through the slider and seat the rod ends into the upper/lower PA-CF `frame_clamp_v10` sockets. Attach the PETG `release_lever_v10` cam at the top pivot lug.
4. **Clamp to Wheelchair Rear Posts:** Wrap rubber grip tape around the Ø22 mm rear upright tubes, bolt the split PA-CF frame clamps with M5 stainless SHCS + nyloc nuts so the 70 mm hub motor meets the 24" rear tire cleanly at the **130° upper-rear quadrant** with ~10 mm spring compression (~145 N preload), and verify the quick-release lever retracts the motor **15 mm** clear of the tire.
5. **Install Anti-Tippers & Caster Dampers:** Bolt the rear anti-tippers onto the lower frame tubes set to **44 mm ground clearance** (clears 15–35 mm thresholds while preventing backward wheelies on 8–10% ramps). Add a thin rubber O-ring under each 8" front caster stem nut to eliminate high-speed flutter above 6 km/h.
6. **Mount Under-Seat Bay & Armrest Joystick:** Hang `underseat_bay_v10` beneath the seat rails using the 4 split steel straps (clearing the dual X-brace), seat the `36 V 10 Ah` battery and `STM32 Dual-FOC` mainboard inside, bolt on `underseat_lid_v10`, and clamp `joystick_pod_v10` onto the right armrest rail.

---

## 4. Wiring & Flashing the 36 V STM32 Dual-FOC Controller

1. **Follow the Verified Schematic:** Open [`electronics/wheelchair_v10_bldc_foc.kicad_sch`](electronics/wheelchair_v10_bldc_foc.kicad_sch) (or view [`media/schematic.png`](media/schematic.png)):
   - **Main Power (12 AWG):** `BT1 (36V 10Ah)` → `F1 (30A inline blade fuse)` → `SW1 (16mm NC E-Stop)` → `U1 (STM32 Dual-FOC VBAT/GND)`.
   - **Wall Charging (14 AWG):** Rear panel `J1 (XT60)` → `F2 (10A fuse)` → `BT1 Charge Input` (connects to the compact **42 V 4 A portable wall charger**).
   - **Motors:** Connect Left/Right 3-phase bullet leads + 5-pin Hall plugs directly from `U1` to `M1`/`M2`.
   - **Joystick (22 AWG shielded):** Wire the 2-axis analog thumb joystick to the **Left Sideboard 4-pin port (USART2)** using **3.3 V ONLY** (*never apply 5 V to STM32 USART2 ADC pins!*).
2. **Flash Open-Source FOC Firmware:**
   - Clone [`EFeru/hoverboard-firmware-hack-FOC`](https://github.com/EFeru/hoverboard-firmware-hack-FOC).
   - Include [`firmware/eferu_foc_wheelchair_config.h`](firmware/eferu_foc_wheelchair_config.h) in `Inc/config.h` (pre-tuned for 10S 36 V, 70 mm 60 KV hub motors, natural progressive joystick feel, 6% deadband, wire-break protection, active electric brake, and downhill regen).
   - Flash via an **ST-Link V2** programmer to the mainboard SWD header.

---

## 5. Pre-Ride Bench & Unoccupied Verification Checklist

- [ ] Lift both rear wheels off the ground (`quick-release` disengaged, then engaged) and verify joystick **Forward**, **Reverse**, **Left**, **Right**, and **E-Stop** direction and instant cutoff.
- [ ] Verify joystick wire-unplug protection triggers an immediate zero-torque stop.
- [ ] Run unoccupied weighted tests (100 kg sandbags/weights) on flat ground, beveled thresholds, and a 5%–8% slope before any human test.

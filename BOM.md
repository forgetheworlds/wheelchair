# Bill of Materials (BOM) — Cruiser III V1.0 Direct-Drive BLDC FOC

**Target Chair:** Drive Medical Cruiser III (18" seat / 24" rear wheels, Ø22 mm tubular steel frame)  
**Estimated Core Kit Cost:** **~$185.00 USD (~$255.30 CAD)** excluding consolidated shipping, taxes, tools, and base wheelchair (`1 USD ≈ 1.38 CAD`).

---

## 1. Purchased Parts (Alibaba / Commodity Direct)

| # | Subsystem | Component & Exact Spec | Key Dimensions | Qty | Unit (USD) | Subtotal (USD) | Subtotal (CAD) | Sourcing Links |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | **Direct-Drive Hub Motors** | **70 mm × 50 mm 60 KV Sensored BLDC Hub Motor** (`MTO7052HBM` / 7052 class, 12–42 V, 450 W max, **built-in replaceable 78A–82A PU sleeve**, internal radial bearings, **M8 flat-keyed stationary axle**, 5-pin Hall + NTC) | Ø70 × 50 mm, M8 flat axle, ~615 g | 2 | $27.50 | $55.00 | $75.90 | [Alibaba 70mm BLDC Hub Motors](https://www.alibaba.com/trade/search?SearchText=70mm+brushless+sensored+hub+motor+electric+skateboard+PU) · [Maytech MTO7052HBM Spec](https://maytech.cn/products/brushless-hub-motor-hall-sensor-motor-mto7052-hbm-60-ha) |
| 2 | **Dual BLDC FOC Controller** | **36 V STM32F103RCT6 / GD32F103 Hoverboard Dual-FOC Mainboard** (flashed with `EFeru/hoverboard-firmware-hack-FOC` — takes 2-axis analog joystick directly on 3.3 V Left USART2 port; no separate ESP32 or 5 V buck needed!) | 168 × 94 × 24 mm | 1 | $18.00 | $18.00 | $24.84 | [Alibaba 36V Hoverboard Mainboard](https://www.alibaba.com/trade/search?SearchText=36V+hoverboard+motherboard+controller+STM32+dual+brushless) · [EFeru FOC Firmware](https://github.com/EFeru/hoverboard-firmware-hack-FOC) *(Plug-and-play alt: Dual Mini VESC ~$42)* |
| 3 | **36 V Battery Pack** | **36 V (10S4P) 10 Ah Lithium-Ion Pack (360 Wh)** with **30 A continuous BMS**, XT60 discharge + XT60/DC5521 charge (Grade-A 18650 cells, UN38.3) | 195 × 95 × 72 mm, ~2.0 kg | 1 | $58.00 | $58.00 | $80.04 | [Alibaba 36V 10Ah 10S4P XT60 Battery](https://www.alibaba.com/trade/search?SearchText=36V+10Ah+10S4P+lithium+battery+pack+30A+BMS+XT60) |
| 4 | **Portable Fast Wall Charger** | **42 V 4 A Compact Switching Wall Charger (168 W, XT60 plug)** — plugs into **any standard AC wall outlet** (home, café, library, office); adds **+10–12 km/hr** (~1.8 h to 80%, ~2.3 h full), ~350 g | 140 × 62 × 38 mm | 1 | $10.50 | $10.50 | $14.49 | [Alibaba 42V 4A Lithium Charger XT60](https://www.alibaba.com/trade/search?SearchText=42V+4A+lithium+battery+charger+XT60) |
| 5 | **Armrest Joystick & Safety UI** | **2-Axis Analog Thumb Joystick (10 kΩ spring-return)** + **16 mm NC Red Mushroom E-Stop** + **3-Position Speed-Mode Rocker** + **30 A Inline Blade Fuse** + **10 A Charge Fuse** + **Rear Panel-Mount XT60** | Joystick 34×26×32 mm; E-Stop Ø16 mm | 1 set | $11.00 | $11.00 | $15.18 | [2-Axis Joystick](https://www.alibaba.com/trade/search?SearchText=2+axis+analog+joystick+module) · [16mm NC E-Stop](https://www.alibaba.com/trade/search?SearchText=16mm+emergency+stop+switch+NC) · [XT60 Panel Mount](https://www.alibaba.com/trade/search?SearchText=XT60+panel+mount+connector) |
| 6 | **Linear Rails, Bushings & Springs** | **Ø8 × 160 mm Stainless Linear Guide Rods (×4)**, **8 × 12 × 15 mm Sintered Bronze Sleeve Bushings (×4)** *(exact fit for Ø12.1 mm slider bores — do NOT order Ø15 mm OD LM8UU!)*, **Compression Springs (Ø14 OD, 2 mm wire, 35 mm L, ~15 N/mm, ×4)** | Ø8×160 rods; 8×12×15 bushings | 1 set | $10.50 | $10.50 | $14.49 | [8mm Linear Rod 160mm](https://www.alibaba.com/trade/search?SearchText=8mm+linear+rod+160mm) · [8x12x15 Bronze Bushings](https://www.alibaba.com/trade/search?SearchText=8x12x15mm+sintered+bronze+sleeve+bushing) · [Compression Springs](https://www.alibaba.com/trade/search?SearchText=compression+spring+2x14x35mm) |
| 7 | **Stability & Fastener Hardware** | **Rear Anti-Tipper Wheel Pair** (set to **44 mm ground clearance**), **Caster-Stem Friction O-Rings**, **M4/M5/M8 Stainless SHCS & Nylocs**, **12 AWG Silicone Power Wire**, **22 AWG 5-Core Shielded Joystick Cable**, **ST-Link V2 Flasher ($2)**, **4× 16×3 mm Flat Steel Rail Straps** | Standard metric | 1 set | $10.50 | $10.50 | $14.49 | [Wheelchair Anti-Tippers 22mm](https://www.alibaba.com/trade/search?SearchText=wheelchair+anti+tipper+wheels+22mm) · [ST-Link V2](https://www.alibaba.com/trade/search?SearchText=ST-Link+V2+programmer) |
| 8 | **3D Printing Filament** | **PA-CF (~0.35 kg)** for structural clamps & hub sliders + **PETG (~0.30 kg)** for enclosures, levers & joystick pod (~0.65 kg total) | 6 unique STL files | 1 set | $11.50 | $11.50 | $15.87 | Standard 1.75 mm PA-CF & PETG spools |
| | | **CORE KIT TOTAL (Excl. Shipping/Tax)** | | | | **$185.00 USD** | **$255.30 CAD** | |

---

## 2. 3D-Printed Parts Schedule (`cad/stl/`)

All six STL files are **single-solid, watertight, FDM DFM-verified** (0 errors at 0.4 mm nozzle / 0.2 mm layer height).

| STL File | Material | Print Qty | Mirroring / Orientation | Recommended Print Settings |
|---|---|---:|---|---|
| [`frame_clamp_v10.stl`](cad/stl/frame_clamp_v10.stl) | **PA-CF** *(or PETG-CF)* | **4** | 2 normal + 2 mirrored in Y | 5 walls, 50% gyroid infill, 0.2 mm layers |
| [`bldc_hub_slider_v10.stl`](cad/stl/bldc_hub_slider_v10.stl) | **PA-CF** *(or PETG-CF)* | **2** | 1 normal + 1 mirrored in Y | 6 walls, 60% gyroid infill (FEA: 46.5× SF) |
| [`release_lever_v10.stl`](cad/stl/release_lever_v10.stl) | **PETG** | **2** | 1 normal + 1 mirrored in Y | 4 walls, 40% gyroid infill |
| [`underseat_bay_v10.stl`](cad/stl/underseat_bay_v10.stl) | **PETG** | **1** | Flat on base (requires ≥270×255 mm bed) | 4 walls, 25% gyroid infill |
| [`underseat_lid_v10.stl`](cad/stl/underseat_lid_v10.stl) | **PETG** | **1** | Flat on top face | 3 walls, 25% gyroid infill |
| [`joystick_pod_v10.stl`](cad/stl/joystick_pod_v10.stl) | **PETG** | **1** | Flat on top face | 3 walls, 25% gyroid infill |

> **Pre-Order Checklist:** Before ordering final hardware or printing, measure your wheelchair's rear upright tube OD (nominal Ø22 mm) with calipers and request the exact shaft-flat drawing from your Alibaba 70 mm hub motor vendor.

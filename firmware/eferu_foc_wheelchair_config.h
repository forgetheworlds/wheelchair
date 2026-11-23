/*
 * Cruiser III V1.0 FINAL — Natural Mobility Joystick Config for EFeru/hoverboard-firmware-hack-FOC
 * Drop these defines into Inc/config.h of https://github.com/EFeru/hoverboard-firmware-hack-FOC
 *
 * Wiring (matches electronics/wheelchair_v10_bldc_foc.kicad_sch):
 *   Left Sideboard 4-pin Port (USART2 -> Dual 12-bit 3.3V ADC):
 *     Pin 1 (3.3V reg) -> Joystick VCC (NEVER exceed 3.3V on STM32 USART2!)
 *     Pin 2 (PA2/ADC)  -> Joystick Y (Throttle: Forward / Reverse)
 *     Pin 3 (PA3/ADC)  -> Joystick X (Steer: Left / Right)
 *     Pin 4 (GND)      -> Joystick GND
 *
 * Tuning Goal — Identical to our validated MuJoCo V1.0 controller:
 *   - Crisp, immediate response (<100 ms torque onset, zero sluggish lag)
 *   - Natural progressive curve near center (fine control through doorways)
 *   - Effortless zero-radius spin-in-place (180° in ~1.5 s)
 *   - Smooth active FOC deceleration & hill-hold when stick returns to center
 *   - Downhill FOC regenerative braking back into the 36V 10Ah battery
 */

#ifndef CRUISER_III_V10_FOC_CONFIG_H
#define CRUISER_III_V10_FOC_CONFIG_H

// --- 1. FOC Sinewave Control & Speed Mode ---
#define CTRL_TYP_SEL        FOC_CTRL     // Silent Field-Oriented Control + Regen
#define CTRL_MOD_REQ        SPD_MODE     // Closed-loop velocity control (consistent speed up/down hills!)
#define ELECTRIC_BRAKE_ENABLE            // Active FOC braking & gentle electronic hill-hold at center
#define ELECTRIC_BRAKE_MAX  120          // Strong confident stopping without pitching forward
#define ELECTRIC_BRAKE_THRES 120

// --- 2. Natural 2-Axis Analog Joystick Input (Left Port / USART2 ADC) ---
#define VARIANT_ADC
#define PRI_INPUT1          3, 200, 2048, 3900, 120   // Steer (X): center 2048, ±120 (~6%) deadband
#define PRI_INPUT2          3, 200, 2048, 3900, 120   // Throttle (Y): center 2048, ±120 (~6%) deadband
#define ADC_PROTECT_ENA     1                         // Instant safe-stop if joystick wire breaks (<150 or >3950)
#define ADC_PROTECT_THRESH  150

// --- 3. Responsiveness & Turning Feel (No Sluggishness!) ---
// Higher FILTER = snappier stick response (6553 = 10% -> crisp ~80 ms lag-free feel)
#define FILTER              6553
// High-authority turning coefficient so hallway 180° turns & sweeping arcs feel effortless
#define SPEED_COEFFICIENT   16384        // 100% forward speed authority
#define STEER_COEFFICIENT   13926        // 85% steering authority (zero-radius spin in place!)
#define INVERT_R_DIRECTION               // Mirror right 70mm hub motor rotation

// --- 4. 36V (10S) Battery & 70mm 60KV Hub Motor Limits ---
// At 70mm OD (0.220m circ): 250 RPM = 3.3 km/h (Indoor), 455 RPM = 6.0 km/h (Walk), 680 RPM = 9.0 km/h (Cruise)
#define I_MOT_MAX           15           // 15 A continuous phase limit per 70mm hub motor
#define I_DC_MAX            24           // 24 A total battery draw (< 30A BMS limit)
#define N_MOT_MAX           460          // Default Mode 2 Walking Pace (~6.0 km/h); raise to 680 for 9.0 km/h Cruise
#define BAT_CELLS           10           // 10S Lithium-Ion (36V nom, 42V full, 31V safe cutoff)
#define BAT_LVL1_ENABLE     1            // Low-battery beep warning @ 34.0V

#endif // CRUISER_III_V10_FOC_CONFIG_H

# Interfaces and Protocols

This note reflects the normalized implementation view. The source sketch behind it is preserved in [`top-level-reference.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/top-level-reference.md).

## Peripheral-Level Interfaces

| Link | Protocol | Why It Fits |
|---|---|---|
| STM32 to OLED | I2C | Standard, low pin count, low bandwidth |
| STM32 to INA219 sensors | I2C | Native sensor interface, shared bus supported |
| STM32 to `BH1750 + mux` light ring | I2C | Multiplexed digital lux sensing matches the 16-sensor ring plan |
| STM32 to `A4988` drivers | STEP/DIR GPIO | Matches `NEMA17` stepper control cleanly |
| Raspberry Pi to STM32 | UART | Carries RL state upload and target-angle return |

## Board-Level Pin Assignment

| Signal | STM32 Pin |
|---|---|
| `I2C_SCL` | `PB6` |
| `I2C_SDA` | `PB7` |
| `YAW_STEP` | `PA8` |
| `YAW_DIR_EN` | `PB0/PB1` |
| `PITCH_STEP` | `PA9` |
| `PITCH_DIR_EN` | `PB10/PB11` |

## I2C Bus Details

- Both `INA219` devices, the OLED, and the mux controller share the same logic-side I2C bus.
- Suggested addresses from the current design:
  - `INA219_1`: `0x40`
  - `INA219_2`: `0x41`
- `BH1750` sensors sit behind the mux rather than directly on the shared bus.
- This is the implementation-ready interpretation of the `TopLevel.txt` "I2C splitter/module" block.
- STM32 master pins:
  - `PB6`: `SCL`
  - `PB7`: `SDA`

## Light-Ring Interface

- The final light ring uses `16` `BH1750` sensors through an I2C mux.
- The mux isolates repeated sensor addresses while keeping the STM32-side protocol simple.
- The STM32 polls each mux channel and packs the resulting lux readings into the light-ring representation used by the Raspberry Pi model.

## Stepper-Driver Interface

- Each `NEMA17` axis is driven through an `A4988` stepper driver.
- The STM32 exports:
  - `STEP` for pulse generation
  - `DIR` and optional `EN` style control lines
- The protocol assumption is `STEP/DIR`, not PWM plus H-bridge direction.

## Raspberry Pi Communication Link

- A simple `4-pin` header carrying `5V`, `GND`, `TX`, and `RX` is enough for Raspberry Pi supervision and inference traffic.
- In the current RL pipeline, the UART link is used for:
  - `STM32 -> Pi` online state upload
  - `Pi -> STM32` next target-angle command return
  - optional status and fault reporting

## RL Data Boundary

- Online inference input is intentionally narrow:
  - current light-ring readings
  - current two-axis angle, defined as the previous target angle accepted by the `STM32`
- Training and evaluation logs may additionally contain:
  - voltage and current measurements
  - power estimates
  - safety flags or error codes

## PCB Interface Notes

- The `BH1750 + mux` bus should stay physically separate from noisy motor-driver routing.
- The solar measurement path and motor measurement path should be physically legible in the schematic and layout.
- Motor power must come from the external `12 V` supply branch, not from the STM32 rail.
- The `12 V` and `5 V` branches must share a common ground reference for control signaling.
- Keep the schematic visually close to the top-level source split:
  - panel-under-test -> `INA219_1` -> dummy load
  - external `12V` adapter -> motor branch -> `INA219_2` -> `A4988` drivers
  - external `5V` supply -> Raspberry Pi and STM32 logic

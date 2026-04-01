# Interfaces and Protocols

## Peripheral-Level Interfaces

| Link | Protocol | Why It Fits |
|---|---|---|
| STM32 to OLED | I2C | Standard, low pin count, low bandwidth |
| STM32 to INA219 sensors | I2C | Native sensor interface, shared bus supported |
| STM32 to LDR quadrant sensors | ADC | Analog voltage dividers are simplest and cheapest |
| STM32 to motor driver | PWM + GPIO | Standard speed, direction, and standby control for a dual H-bridge |
| Raspberry Pi to STM32 | UART | Carries RL state upload and target-angle return |

## Board-Level Pin Assignment

| Signal | STM32 Pin |
|---|---|
| `LDR1` | `PA0` |
| `LDR2` | `PA1` |
| `LDR3` | `PA2` |
| `LDR4` | `PA3` |
| `I2C_SCL` | `PB6` |
| `I2C_SDA` | `PB7` |
| `PWMA` | `PA8` |
| `AIN1` | `PB0` |
| `AIN2` | `PB1` |
| `PWMB` | `PA9` |
| `BIN1` | `PB10` |
| `BIN2` | `PB11` |

## I2C Bus Details

- Both `INA219` devices and the OLED share the same `3.3 V` I2C bus.
- Suggested addresses from the source-of-truth design:
  - `INA219_1`: `0x40`
  - `INA219_2`: `0x41`
- STM32 master pins:
  - `PB6`: `SCL`
  - `PB7`: `SDA`

## ADC Front End

- Each LDR forms a `3.3 V` divider with a `10 kOhm` resistor.
- Each ADC node may include a `0.01 uF` capacitor to ground for noise filtering.
- These local sensor values are sampled by the STM32 and can be further transformed into the online light-state representation used by the Raspberry Pi model.

## Motor-Driver Interface

- `TB6612FNG` receives:
  - `PWMA` and `PWMB` for speed
  - `AIN1/AIN2` and `BIN1/BIN2` for direction
- Direction logic:
  - `1/0`: forward
  - `0/1`: reverse
  - `0/0`: stop
  - `1/1`: brake

## Raspberry Pi Communication Link

- A simple `4-pin` header carrying `5V`, `GND`, `TX`, and `RX` is enough for Raspberry Pi supervision and inference traffic.
- In the current RL pipeline, the UART link is used for:
  - `STM32 -> Pi` online state upload
  - `Pi -> STM32` next target-angle command return
  - optional status and fault reporting

## RL Data Boundary

- Online inference input is intentionally narrow:
  - current light-ring readings
  - current two-axis angle
- Training and evaluation logs may additionally contain:
  - voltage and current measurements
  - power estimates
  - remaining-energy estimate
  - safety flags or error codes

## PCB Interface Notes

- The OLED and both INA219 devices should share one `3.3 V` I2C bus with configurable pull-ups.
- The LDR network should include RC filtering at the ADC nodes and stay far from buck and motor switching regions.
- The solar measurement path and load measurement path should be physically legible in the schematic and layout.
- Motor power must come from the regulated system supply, not from the STM32 rail.

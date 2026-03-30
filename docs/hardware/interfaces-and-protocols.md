# Interfaces and Protocols

## Peripheral-Level Interfaces

| Link | Protocol | Why It Fits |
|---|---|---|
| STM32 to OLED | I2C | Standard, low pin count, low bandwidth |
| STM32 to INA219 sensors | I2C | Native sensor interface, shared bus supported |
| STM32 to LDR quadrant sensors | ADC | Analog voltage dividers are simplest and cheapest |
| STM32 to limit switches | GPIO | Direct digital reads with interrupts or polling |
| STM32 to motor driver | PWM + GPIO | Standard speed, direction, and standby control for a dual H-bridge |
| STM32 to motor encoders | Timer encoder mode / GPIO interrupt | Accurate local closed-loop angle estimation |
| Raspberry Pi to STM32 | UART | Simple, robust, easy to debug, standard on both boards |

## Why UART Between Raspberry Pi and STM32

- The data volume is small.
- UART is easy to inspect with a serial terminal during bring-up.
- It avoids Linux SPI driver complexity on the Raspberry Pi.
- It is sufficient for command/telemetry exchange at `115200 bps` or higher.
- It matches the `.docx` recommendation to keep the Raspberry Pi electrically simple and detachable.

## Proposed UART Framing

Use a fixed binary frame with checksum for reliability.

### Frame Layout

| Byte(s) | Meaning |
|---|---|
| `0xAA 0x55` | Start bytes |
| `type` | Message type |
| `len` | Payload length |
| `payload[len]` | Data |
| `crc8` | Check byte |

### Pi to STM32 Message Types

- `0x10 SET_MODE`
- `0x11 MOVE_TARGET`
- `0x12 HOLD_POSITION`
- `0x13 START_HOME`
- `0x14 OLED_PAGE`
- `0x15 HEARTBEAT`

### STM32 to Pi Message Types

- `0x20 TELEMETRY`
- `0x21 HOME_DONE`
- `0x22 FAULT_REPORT`
- `0x23 ACK`
- `0x24 DEBUG_SNAPSHOT`

## Example Payloads

### `MOVE_TARGET`

- `int16 yaw_target_deg_x10`
- `int16 pitch_target_deg_x10`
- `uint8 speed_limit_pct`

### `TELEMETRY`

- `int16 yaw_deg_x10`
- `int16 pitch_deg_x10`
- `uint16 panel_mv`
- `int16 panel_ma`
- `uint16 battery_mv`
- `int16 battery_ma`
- `uint16 light_nw`
- `uint16 light_ne`
- `uint16 light_sw`
- `uint16 light_se`
- `uint8 mode`
- `uint8 fault_flags`

## Command Strategy

- The Raspberry Pi sends low-rate supervisory commands, for example `2 Hz` to `10 Hz`.
- The STM32 runs local motor and sensor loops much faster, for example `100 Hz` to `1000 Hz` depending on the function.
- If the Pi heartbeat is lost, the STM32 enters `ECO_HOLD` or `FAULT` rather than continuing motion blindly.

## PCB Interface Notes

- The OLED and both INA219 devices should share one `3.3 V` I2C bus with configurable pull-ups.
- The LDR network should include RC filtering at the ADC nodes and stay far from buck and motor switching regions.
- The motor-driver header should expose `PWMA`, `AIN1`, `AIN2`, `PWMB`, `BIN1`, `BIN2`, and `STBY` if `TB6612FNG` is used.
- A `4-pin` Raspberry Pi header carrying `5V`, `GND`, `TX`, and `RX` is sufficient for the current architecture.

## One-Button Operation Logic

1. Button press wakes or starts the system.
2. STM32 performs self-test and homes both axes.
3. STM32 reports `HOME_DONE`.
4. Raspberry Pi transitions into optimization mode and begins sending supervisory commands.
5. OLED shows mode, power, battery, and current command state.

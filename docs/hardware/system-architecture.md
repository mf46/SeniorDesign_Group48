# System Architecture

## Proposed Hardware Stack

The custom PCB should be treated as the project's lower-level control and power board. It should host the sensor front end, motor drivers, power-tree circuitry, OLED and Raspberry Pi headers, and the interfaces around an `STM32F407ZGT6` development board or equivalent STM32 core implementation.

### High-Level Compute

- `Raspberry Pi Zero 2 W`
- Role: calculate net-energy benefit, supervise operating modes, log data, and send motion targets to the STM32

### Real-Time Controller

- `STM32F407ZGT6`
- Role: sample sensors, run motor control loops, execute calibration, refresh OLED, and enforce safety limits

### Sensing

- Four LDRs arranged in a quadrant light-sensor head with divider resistors
- `INA219` for solar-panel bus current/voltage measurement
- `INA219` for battery or main bus measurement so net-gain logic can compare harvested power against movement overhead
- Two limit switches per axis for homing and over-travel protection
- Incremental encoder feedback from geared DC motors

### Actuation

- Two low-current geared DC motors with encoders, one for yaw and one for pitch
- `TB6612FNG` dual H-bridge as the preferred default motor driver
- `BTS7960` kept only as a fallback if measured stall current is too high for the compact on-board driver

### Local User Interface

- `0.96"` I2C OLED
- One push button for start/calibration
- Optional buzzer or status LED for fault indication

### Power Path

- Small solar panel feeds the measured generation path
- Battery pack or stable input bus powers the tracker
- `5 V / 3 A` buck converter powers Raspberry Pi and any 5 V peripherals
- `3.3 V` logic regulator powers STM32-side sensors and digital logic
- Motor supply remains a separately routed noisy power branch rather than being mixed with the weak-signal logic area

## Why This Architecture Fits the Project

- It preserves the RFA master-slave split between Raspberry Pi and STM32.
- It stays within a student-feasible budget by avoiding industrial servos and oversized compute hardware.
- It directly supports Minghao's responsibility area: STM32 communication with motors, light sensors, and current/voltage sensors.
- A lighter Raspberry Pi and lighter H-bridge reduce board cost, complexity, and idle power draw.
- The PCB role is clearer: power distribution, measurement, motor driving, and communication hub.

## Recommended Signal Flow

1. LDRs, INA219 sensors, limit switches, and encoder signals are read by the STM32.
2. The STM32 computes filtered local telemetry and sends state packets to the Raspberry Pi over UART.
3. The Raspberry Pi decides whether motion is worth the energy cost and sends movement or hold commands.
4. The STM32 closes the low-level motor loop using PWM and direction outputs through the motor drivers.
5. The OLED displays operating mode, panel power, battery state, and current axis angles.

## PCB-Level Design Rules

- Use a two-layer board only if the strong-current and weak-signal regions are physically separated.
- Keep the buck converter, motor driver, and motor connector return loops compact and away from the ADC/I2C region.
- Provide dedicated test points for `VIN`, `5V`, `3V3`, `GND`, `SCL`, `SDA`, `UART_TX`, `UART_RX`, and the motor rail.
- Put the Raspberry Pi on a simple UART plus power header rather than deeply coupling it into the low-level board.

## Suggested Operating Modes

- `BOOT`: power-up self-check
- `HOME`: limit-switch based calibration
- `TRACK`: normal light-seeking and angle correction
- `ECO_HOLD`: pause movement because expected gain is too small
- `FAULT`: stop movement because of over-current, bad sensor data, or travel fault

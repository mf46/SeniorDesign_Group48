# System Architecture

## Proposed Hardware Stack

The custom PCB should be treated as the project's lower-level control and power board. Following `dual_axis_solar_tracker.md`, it hosts the LDR front end, dual INA219 measurement path, motor-driver stage, OLED header, charging and regulation stages, and the interfaces around an `STM32F407ZGT6`.

### Real-Time Controller

- `STM32F407ZGT6`
- Role: sample sensors, run motor control loops, execute calibration, refresh OLED, and enforce safety limits

### Sensing

- Four LDRs arranged in a quadrant light-sensor head with divider resistors
- `INA219_1` for solar-panel-side current/voltage measurement
- `INA219_2` for battery-side or load-side current/voltage measurement
- `0.01 uF` optional capacitor on each ADC node for simple RC filtering

### STM32 Pin Map

- `PA0` to `PA3`: four LDR ADC channels
- `PB6`: I2C `SCL`
- `PB7`: I2C `SDA`
- `PA8`: `PWMA` for yaw motor
- `PA9`: `PWMB` for pitch motor
- `PB0` and `PB1`: yaw direction control
- `PB10` and `PB11`: pitch direction control

### Actuation

- Two geared DC motors, one for yaw and one for pitch
- `TB6612FNG` dual H-bridge as the baseline motor driver
- PWM sets speed and digital lines set direction through `IN1/IN2`

### Local User Interface

- `0.96"` I2C OLED
- One push button for start/calibration
- Optional buzzer or status LED for fault indication

### Power Path

- Small `5 V` to `6 V` solar panel feeds the generation path
- `INA219_1` measures the solar path before regulation
- `LM2596` or `TPS5430` buck stage creates a regulated `5 V` rail
- `TP4056` manages `18650` cell charging from the regulated `5 V` input
- `INA219_2` measures the battery-side or load-side path
- `MT3608` boosts the battery voltage back to `5 V` for the system rail when needed
- `3.3 V` logic regulation powers STM32-side sensors and digital logic
- Motor supply remains separate from the weak-signal logic region even when sharing a common ground reference

## Why This Architecture Fits the Project

- It matches the newly added authoritative hardware summary.
- It stays within a student-feasible budget and uses commonly available modules.
- It directly supports Minghao's responsibility area: STM32 communication with motors, light sensors, and current/voltage sensors.
- The PCB role is explicit: sensing, power regulation, battery charging, power measurement, and motor driving.
- The design exposes measurable net-energy data instead of relying only on geometric tracking logic.

## Recommended Signal Flow

1. The solar panel output is measured by `INA219_1`.
2. The regulated charging path feeds the `18650` battery through `TP4056`.
3. The battery-side system load is measured by `INA219_2`.
4. The STM32 reads four LDR channels through the ADC and both INA219 devices through I2C.
5. The STM32 drives yaw and pitch through `TB6612FNG` using PWM plus direction signals.
6. The OLED displays operating mode and electrical telemetry over the same I2C bus.
7. A UART header can still expose telemetry to a Raspberry Pi or external host if the team keeps the higher-level optimization split.

## PCB-Level Design Rules

- Use a two-layer board only if the strong-current and weak-signal regions are physically separated.
- Keep the buck converter, motor driver, and motor connector return loops compact and away from the ADC/I2C region.
- Provide dedicated test points for `VIN`, `5V`, `3V3`, `GND`, `SCL`, `SDA`, and the motor rail, with UART pads if external supervision is retained.
- Keep the Raspberry Pi or PC connection optional through a simple UART header rather than making it a hard dependency of the board.

## Suggested Operating Modes

- `BOOT`: power-up self-check
- `HOME`: limit-switch based calibration
- `TRACK`: normal light-seeking and angle correction
- `ECO_HOLD`: pause movement because expected gain is too small
- `FAULT`: stop movement because of over-current, bad sensor data, or travel fault

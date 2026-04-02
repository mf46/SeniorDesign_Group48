# System Architecture

This page is the normalized hardware architecture. For the original top-level sketch and preserved source details, see [`top-level-reference.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/top-level-reference.md).

## Proposed Hardware Stack

The custom PCB should be treated as the project's lower-level control and interface board. It hosts the `BH1750 + mux + 16-sensor ring`, dual INA219 measurement path, the `A4988` stepper-driver stage, the OLED header, and the interfaces around an `STM32F407ZGT6`.

### Real-Time Controller

- `STM32F407ZGT6`
- Role: poll sensors, run motor control logic, execute calibration, refresh OLED, enforce safety limits, and exchange state and command data with the Raspberry Pi

### Sensing

- A `BH1750 + mux + 16-sensor ring` arranged around the panel for directional light sampling
- `INA219_1` for solar-panel test-path current and voltage measurement
- `INA219_2` for motor-branch current and voltage measurement
- The top-level hardware sketch still records the panel placeholder as a `6V 100mA 80x55 mm` polycrystalline panel

### STM32 Pin Map

- `PB6`: I2C `SCL`
- `PB7`: I2C `SDA`
- `PA8`: yaw `STEP`
- `PA9`: pitch `STEP`
- `PB0` and `PB1`: yaw `DIR/EN`
- `PB10` and `PB11`: pitch `DIR/EN`

### Actuation

- Two `NEMA17` stepper motors, one for yaw and one for pitch
- `A4988` stepper drivers as the baseline driver stage
- `STEP/DIR` style signals are used for motion control
- The current angle used by the RL pipeline is defined as the last target angle accepted by the `STM32`, not a separately measured encoder angle

### Local User Interface

- `0.96"` I2C OLED
- One push button for start and calibration
- Optional buzzer or status LED for fault indication

### Power Path

- An external `12 V` adapter feeds the motor branch and both `A4988` drivers
- An external `5 V` supply feeds the Raspberry Pi and `STM32` logic branch
- The original top-level source describes the motor adapter as a `60W 12V 5A` supply fed from `220V AC` mains
- `INA219_1` measures the solar-panel test path, where the panel drives a dummy load and does not power the controller
- `INA219_2` measures the motor branch supplied by the external `12 V` adapter
- The logic branch and motor branch remain separate but must share a common ground reference for control signaling

## Why This Architecture Fits the Project

- It stays within a student-feasible budget and uses commonly available modules.
- It directly supports Minghao's responsibility area: STM32 communication with sensors, motor execution, and the Raspberry Pi inference path.
- The PCB role is explicit: sensing, interface control, power measurement, and motor driving.
- The design exposes measurable panel-output and motor-consumption data instead of relying only on geometric tracking logic.

## RL-Related Control Split

In the current pipeline, the control split above the hardware board is:

- `STM32`: poll sensors, execute commands, report status, and enforce safety
- Raspberry Pi: receive online state, run inference, return the next target angles, and store logs
- `PC/云端`: use logs for offline training, export `ONNX`, and redeploy the model to the Raspberry Pi

At the RL interface level, the Raspberry Pi consumes online state derived from current light information and current axis angle, then returns the next target angles for the two axes. The electrical telemetry measured on the board remains available for logging, reward design, and evaluation.

In the current implementation assumption, `current_angle` is defined as the previous target angle output that the `STM32` accepted after homing. The system does not currently assume a separate online angle sensor in the RL state.

## Recommended Signal Flow

1. The solar panel output is sent through `INA219_1` into a dummy load so panel output power can be measured independently of the control system power rails.
2. The external `12 V` adapter feeds the two `A4988` motor drivers through the motor branch measured by `INA219_2`.
3. The external `5 V` supply feeds the Raspberry Pi and the `STM32` logic branch.
4. The `STM32` polls the `BH1750 + mux + 16-sensor ring` and the two INA219 devices, reflecting the top-level sketch's original "I2C splitter/module" concept in a more implementation-ready form.
5. The `STM32` uploads the online state needed for RL inference to the Raspberry Pi.
6. The Raspberry Pi predicts the next target angles and returns them to the `STM32`.
7. The `STM32` drives yaw and pitch through `A4988` using `STEP/DIR` style signals.
8. The OLED displays operating mode and electrical telemetry over the same I2C bus.

## PCB-Level Design Rules

- Use a two-layer board only if the strong-current and weak-signal regions are physically separated.
- Keep the stepper-driver stage and motor connector return loops compact and away from the I2C sensor region.
- Provide dedicated test points for `12V`, `5V`, `3V3`, `GND`, `SCL`, `SDA`, and the motor rail, with UART pads for the Raspberry Pi communication link.
- Keep the `12 V` motor branch and `5 V` logic branch physically legible and tied only through a controlled common-ground strategy.
- Keep the board-level design centered on the STM32 even though the full RL pipeline includes Raspberry Pi inference above it.

## Suggested Operating Modes

- `BOOT`: power-up self-check
- `HOME`: limit-switch based calibration
- `TRACK`: normal light-seeking and angle correction
- `ECO_HOLD`: pause movement because expected gain is too small
- `FAULT`: stop movement because of over-current, bad sensor data, or travel fault

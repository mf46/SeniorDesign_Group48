# Figure Plan

## Required Figures

1. `System visual aid`
Description: context image showing the solar tracker, panel under test, external 12 V motor supply, external 5 V logic supply, Raspberry Pi, STM32, and dual-axis mount in use. Use [`docs/hardware/top-level-reference.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/top-level-reference.md) as the source for the panel-path, motor-path, and training-deployment split.
Section: `1.2 Solution Overview & Visual Aid`

2. `Whole-system block diagram`
Description: Raspberry Pi inference node, STM32 lower-level control PCB, state-upload path, target-angle return path, `BH1750 + mux` light ring, two INA219 measurement paths, A4988 motor-drive stage, motors, OLED, and split 12 V / 5 V power rails with signal arrows. Preserve the top-level source relationships: panel -> `INA219_1` -> dummy load, and external `12V` adapter -> motor branch -> `INA219_2`.
Section: `2.1 Block Diagram`

3. `Mechanical dual-axis tracker sketch`
Description: yaw axis base, pitch axis bracket, panel mounting, and limit-switch locations.
Section: `2.2 Mechanical and Actuation Subsystem`

4. `Sensor subsystem diagram`
Description: `BH1750 + mux` light ring, angle-state source, INA219 for motor branch, INA219 for solar-panel test branch, and sampled signals into STM32.
Section: `2.3 Sensing Subsystem`

5. `Control and communication flow`
Description: state upload from STM32 to Raspberry Pi, target-angle command return from Raspberry Pi to STM32, local PWM and I2C interfaces, heartbeat, logging path, and fail-safe behavior.
Section: `2.4 Control and Communication Subsystem`

6. `Power architecture`
Description: external 12 V motor branch, external 5 V logic branch, A4988 supply path, Raspberry Pi/STM32 logic path, current-sense points, and strong-current versus weak-current partitioning.
Section: `2.5 Power Subsystem`

7. `OLED example screen`
Description: mock screen showing mode, panel power, motor power, and yaw/pitch angles.
Section: `2.6 User Interface and One-Button Operation`

8. `Tolerance analysis figure`
Description: plot or geometry diagram showing how angular misalignment affects captured solar power or net gain.
Section: `2.7 Tolerance Analysis`

## Nice-to-Have Figures

1. `UART packet format`
Description: frame layout table or bit or byte diagram showing `light_ring + current_angle` upload and `target_angle` return.
Section: `2.4 Control and Communication Subsystem`

2. `Training and deployment loop`
Description: tree showing Raspberry Pi logging, offline `PyTorch` training, `ONNX` export, and redeployment to Raspberry Pi.
Section: `2.4 Control and Communication Subsystem`

3. `Verification setup photo`
Description: benchtop measurement arrangement showing staged bring-up at test points, rail validation, and tracking or motor-energy tests.
Section: `2.x verification discussion`

# Figure Plan

## Required Figures

1. `System visual aid`
Description: context image showing the solar tracker, panel, battery, Raspberry Pi, STM32, and dual-axis mount in use.
Section: `1.2 Solution Overview & Visual Aid`

2. `Whole-system block diagram`
Description: Raspberry Pi, STM32 lower-level control PCB, UART header, shared I2C bus, ADC-based LDR inputs, motor-drive stage, motors, OLED, and split power rails with signal arrows.
Section: `2.1 Block Diagram`

3. `Mechanical dual-axis tracker sketch`
Description: yaw axis base, pitch axis bracket, panel mounting, and limit-switch locations.
Section: `2.2 Mechanical and Actuation Subsystem`

4. `Sensor subsystem diagram`
Description: LDR quadrant head, INA219 current/voltage sensors, battery telemetry path, and sampled signals into STM32.
Section: `2.3 Sensing Subsystem`

5. `Control and communication flow`
Description: UART command/telemetry loop between Raspberry Pi and STM32 plus local PWM, ADC, and shared I2C interfaces, including heartbeat and fail-safe behavior.
Section: `2.4 Control and Communication Subsystem`

6. `Power architecture`
Description: input bus, 5 V buck, 3.3 V regulation, Raspberry Pi branch, motor branch, current-sense points, and strong-current versus weak-current partitioning.
Section: `2.5 Power Subsystem`

7. `OLED example screen`
Description: mock screen showing mode, panel power, battery voltage, and yaw/pitch angles.
Section: `2.6 User Interface and One-Button Operation`

8. `Tolerance analysis figure`
Description: plot or geometry diagram showing how angular misalignment affects captured solar power or net gain.
Section: `2.7 Tolerance Analysis`

## Nice-to-Have Figures

1. `UART packet format`
Description: frame layout table or bit/byte diagram.
Section: `2.4 Control and Communication Subsystem`

2. `Verification setup photo`
Description: benchtop measurement arrangement showing staged bring-up at test points, rail validation, and tracking or motor-energy tests.
Section: `2.x verification discussion`

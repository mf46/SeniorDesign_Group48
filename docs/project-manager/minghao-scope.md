# Minghao Fang Scope and Interfaces

## Owned Work

Minghao Fang is responsible for the control and software path that links sensing, optimization, and feedback:

- STM32 communication with motors, light sensors, and current/voltage sensors
- Raspberry Pi edge-computing optimization algorithms
- Serial communication protocol between Raspberry Pi and STM32
- OLED data visualization

## Interface Boundaries

### Raspberry Pi

The Pi should make higher-level decisions:

- Estimate whether motion will improve net energy
- Decide if tracking should be paused or resumed
- Send commands to the STM32 in a compact protocol

### STM32F407ZGT6

The STM32 should handle:

- Sensor sampling
- Real-time actuator control
- PWM or motor-control outputs
- Command execution and status reporting

### Sensors

Likely sensing inputs include:

- Light sensors for irradiance or relative brightness
- Current and voltage sensing for energy accounting

### OLED

The OLED should provide a compact live status display such as battery/power state, operating mode, and whether tracking is active.

## PM Takeaway

Minghao's work sits at the system integration layer. Most design risk will come from the protocol, timing, and how accurately the controller can estimate net energy from sensor data.

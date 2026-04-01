# Minghao Fang Scope and Interfaces

## Owned Work

Minghao Fang is responsible for the control and software path that links sensing, inference, training, and feedback:

- `STM32` communication with light sensors, motor execution, and status return
- Raspberry Pi online inference, logging, and model loading
- Serial communication protocol between Raspberry Pi and `STM32`
- Offline training data preparation and model deployment flow
- OLED data visualization

## Interface Boundaries

### Raspberry Pi

The Raspberry Pi is responsible for the online RL path:

- Receive current light-ring readings and current two-axis angles from `STM32`
- Here the current-angle fields are the last target angles accepted by `STM32`
- Run online inference with the deployed model
- Output the next target angles for the two axes
- Store training logs for later offline training
- Load the exported `ONNX` model for deployment

### STM32F407ZGT6

The `STM32` should handle:

- Sensor sampling
- Real-time actuator control
- Command execution and status reporting
- Safety checks such as timeout stop, travel limits, and fault handling

### Training Side

`PC/云端` should handle:

- Offline model training
- Reward calculation based on logged energy and safety information
- Model export and version update

### Sensors

The current RL pipeline uses:

- A `BH1750 + mux + 16-sensor ring` as the online light input
- The previous accepted target angle as the online current-angle input
- `INA219` measurements for motor-power and panel-output evaluation support data

### OLED

The OLED should provide a compact live status display such as panel power, motor power, operating mode, and current yaw or pitch state.

## PM Takeaway

Minghao's work sits at the system integration layer. Most design risk will come from the protocol, timing, logging quality, and whether the online model interface stays simple enough for stable deployment while still supporting useful reward design.

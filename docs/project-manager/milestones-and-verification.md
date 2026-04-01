# Milestones and Verification Focus

## Build Milestones

1. Confirm the RL pipeline and role split between `STM32`, Raspberry Pi, and `PC/云端`.
2. Select sensing and actuation components that fit the budget.
3. Define the serial protocol for state upload and target-angle command return.
4. Implement basic sensor reading and motor control on `STM32`.
5. Bring up the Raspberry Pi inference path using light-ring input and current-angle input.
6. Add logging for offline training samples and reward-related measurements.
7. Export the trained model to `ONNX` and deploy it to the Raspberry Pi.
8. Integrate OLED status display.
9. Verify end-to-end behavior under changing light conditions.

## Verification Themes

- The system should only move when the expected energy gain is worth the motion cost.
- The online model interface should remain stable: light-ring plus current angle in, next target angles out.
- The `STM32` should respond to target-angle commands deterministically and report status reliably.
- Sensor readings should support repeatable decisions, not just raw telemetry.
- The OLED should reflect current system state without blocking control loops.

## Design-Document Angle

For the design document, the most important evidence is not just that the tracker moves. It is that the system can explain why it moved, why it did not move, and how the control architecture separates online inference from offline training while keeping the energy balance positive.

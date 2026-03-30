# Milestones and Verification Focus

## Build Milestones

1. Confirm architecture and role split between Pi and STM32.
2. Select sensing and actuation components that fit the budget.
3. Define the serial protocol and command/status schema.
4. Implement basic sensor reading and motor control on STM32.
5. Add Pi-side decision logic for net-energy-aware tracking.
6. Integrate OLED status display.
7. Verify end-to-end behavior under changing light conditions.

## Verification Themes

- The system should only move when the expected energy gain is worth the motion cost.
- The STM32 should respond to commands deterministically and report status reliably.
- Sensor readings should support repeatable decisions, not just raw telemetry.
- The OLED should reflect current system state without blocking control loops.

## Design-Document Angle

For the design document, the most important evidence is not just that the tracker moves. It is that the system can explain why it moved, why it did not move, and how the control architecture keeps the energy balance positive.

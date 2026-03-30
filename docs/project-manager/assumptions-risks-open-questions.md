# Assumptions, Risks, and Open Questions

## Assumptions

- The STM32F407ZGT6 is the real-time control hub and remains fixed.
- The Raspberry Pi is available for optimization and higher-level logic.
- The tracker uses a dual-axis mechanical structure.
- The project must fit within the stated 1500 RMB budget.
- The system is judged primarily on feasibility, reliability, and energy-aware behavior.

## Risks

- Motor actuation may consume too much energy in weak light, reducing or eliminating net gain.
- Sensor noise may cause unstable motion decisions or false tracking triggers.
- Serial protocol timing may become a bottleneck if the Pi and STM32 exchange too much data.
- OLED/status logic may distract from core control work if not kept minimal.
- Budget pressure may force component substitutions later in the semester.

## Open Questions

- What exact motor or actuator family will be used for the two axes?
- Which light sensor and current/voltage sensor parts best fit the budget and accuracy target?
- How often should the Pi update tracking decisions?
- What command set should the serial protocol support for normal operation, calibration, and fault handling?
- What minimum OLED fields are required for the design document and demo?

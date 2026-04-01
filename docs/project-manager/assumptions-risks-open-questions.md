# Assumptions, Risks, and Open Questions

## Assumptions

- The `STM32F407ZGT6` is the real-time control hub and remains fixed.
- The Raspberry Pi is part of the formal online RL pipeline rather than an optional afterthought.
- The tracker uses a dual-axis mechanical structure.
- Online inference only uses current light-ring intensity and current two-axis angle.
- Reward and evaluation can still use logged electrical measurements and safety states.
- The project must fit within the stated `1500 RMB` budget.
- The system is judged primarily on feasibility, reliability, and energy-aware behavior.

## Risks

- Motor actuation may consume too much energy in weak light, reducing or eliminating net gain.
- Sensor noise may cause unstable target-angle predictions.
- Serial protocol timing may become a bottleneck if state upload and logging fields are not separated cleanly.
- Logged reward-related data may be noisy enough to slow down model improvement.
- OLED/status logic may distract from core control work if not kept minimal.
- Budget pressure may force component substitutions later in the semester.

## Open Questions

- What exact motor or actuator family will be used for the two axes?
- How many light sensors will the final light ring use in the deployed RL pipeline?
- How often should the Raspberry Pi update target-angle predictions?
- What command set should the serial protocol support for normal operation, calibration, and fault handling?
- What minimum OLED fields are required for the design document and demo?

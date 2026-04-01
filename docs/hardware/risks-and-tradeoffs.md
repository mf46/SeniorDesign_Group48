# Risks and Tradeoffs

## Main Tradeoffs

### NEMA17 Steppers vs. Smaller Actuators

- `NEMA17` stepper motors match the current target-angle control abstraction and simplify the meaning of "current angle" after homing.
- They may draw more holding current and add mechanical weight compared with smaller geared solutions.

### Fixed Four-Quadrant Head vs. Light Ring

- A light ring matches the RL input definition directly and gives the model richer directional information.
- It adds more channels, routing complexity, and interface-definition work than a simple four-quadrant head.

### Analog Light Ring vs. BH1750 + Mux

- `BH1750 + mux` gives a cleaner digital interface and avoids calibrating many analog ADC channels.
- It increases shared-bus complexity and may limit polling rate if the full `16`-sensor ring is sampled too aggressively.

### STM32 Execution vs. Raspberry Pi Inference

- The board-level hardware remains fundamentally STM32-centered.
- The current RL pipeline still depends on the Raspberry Pi for online inference, logging, and model loading.
- This split keeps real-time execution and safety on the STM32 while leaving model iteration and deployment on the Pi and offline training side.

## Technical Risks

- Motor current spikes may brown out the Raspberry Pi if power rails are not isolated well.
- The `A4988` current limit may be misconfigured if the `NEMA17` requirement is not screened early.
- The muxed `BH1750` ring may become a timing bottleneck if the sampling schedule is not designed carefully.
- Mechanical backlash may reduce pointing repeatability.
- INA219 accuracy may be enough for relative optimization but not for precision energy auditing.
- The external-supply test setup means the report must distinguish measured panel output from total system input power.
- If the UART protocol mixes online control data and training logs poorly, latency or debugging cost may rise.
- If the panel is too heavy, the chosen stepper may still lose steps or overheat.

## Mitigations

- Use a separated motor branch plus distinct 12 V and 5 V rails with controlled grounding discipline.
- Screen the required motor current before locking the stepper-driver footprint.
- Add current limits, travel limits, and software deadbands to avoid hunting.
- Keep the online inference interface narrow: current light state plus current angle in, next target angles out.
- Log electrical telemetry and safety states separately for reward design and offline analysis.
- Set a fixed polling schedule for the `BH1750 + mux` ring and verify that it stays within the control-loop budget.
- Use homing switches so the internal angle estimate can be reset each startup.
- Place test points on the power rails and communication buses so bring-up can proceed in stages.
- Keep the final report honest that the platform is externally powered and uses the solar panel as a measured test source.

## Assumptions

- The mechanical team can provide a low-friction dual-axis mount compatible with modest torque motors.
- The team accepts demonstration-oriented energy measurement accuracy rather than laboratory-grade metrology.
- The full RL pipeline includes Raspberry Pi inference and offline retraining even though the board-level hardware summary remains STM32-centered.

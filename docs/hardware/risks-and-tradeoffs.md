# Risks and Tradeoffs

## Main Tradeoffs

### Geared DC Motors vs. Servos

- Geared DC motors plus encoder feedback are cheaper per torque and scale well for panel loads.
- Servos simplify control but may have limited range, weaker holding behavior, or worse long-term durability.

### TB6612FNG vs. Higher-Current Drivers

- `TB6612FNG` is much more PCB-friendly for a compact student design and is a better fit for low-current tracker motors.
- A higher-current driver provides more current margin but is physically bulkier and less aligned with an integrated custom PCB unless the motor choice truly demands it.

### LDR Array vs. Dedicated Sun Sensor

- LDRs are cheap and easy to explain in a senior design setting.
- They are less accurate and more temperature-sensitive, so the control algorithm should combine online light input with measured energy results rather than trusting light sensing alone.

### STM32 Execution vs. Raspberry Pi Inference

- The board-level hardware remains fundamentally STM32-centered.
- The current RL pipeline still depends on the Raspberry Pi for online inference, logging, and model loading.
- This split keeps real-time execution and safety on the STM32 while leaving model iteration and deployment on the Pi and offline training side.

## Technical Risks

- Motor current spikes may brown out the Raspberry Pi if power rails are not isolated well.
- The chosen compact H-bridge may be under-sized if the motor stall current is not screened early.
- Mechanical backlash may reduce pointing repeatability.
- INA219 accuracy may be enough for relative optimization but not for precision energy auditing.
- `TP4056` and `MT3608` add practical inefficiency, so measured net-gain results may be worse than idealized calculations.
- If the UART protocol mixes online control data and training logs poorly, latency or debugging cost may rise.
- If the panel is too heavy, low-cost motors may stall or overheat.

## Mitigations

- Use a separated motor branch plus distinct 5 V and 3.3 V logic rails with controlled grounding discipline.
- Measure or estimate stall current before locking the motor-driver footprint.
- Add current limits, travel limits, and software deadbands to avoid hunting.
- Keep the online inference interface narrow: current light state plus current angle in, next target angles out.
- Log electrical telemetry and safety states separately for reward design and offline analysis.
- Use homing switches so angle estimates can be reset each startup.
- Place test points on the power rails and communication buses so bring-up can proceed in stages.
- Keep the final report honest that the charging and boost stages are low-cost pragmatic choices, not high-efficiency energy-harvesting ICs.

## Assumptions

- The mechanical team can provide a low-friction dual-axis mount compatible with modest torque motors.
- The team accepts demonstration-oriented energy measurement accuracy rather than laboratory-grade metrology.
- The full RL pipeline includes Raspberry Pi inference and offline retraining even though the board-level hardware summary remains STM32-centered.

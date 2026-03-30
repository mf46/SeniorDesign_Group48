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
- They are less accurate and more temperature-sensitive, so the control algorithm should combine light imbalance with measured power gain instead of trusting LDRs alone.

### Direct STM32 Control vs. Optional Pi-Assisted Supervision

- The new hardware summary is fundamentally an STM32-centered board design.
- A Raspberry Pi can still be added through UART for higher-level logic, but the board should not depend on it for basic operation.

## Technical Risks

- Motor current spikes may brown out the Raspberry Pi if power rails are not isolated well.
- The chosen compact H-bridge may be under-sized if the motor stall current is not screened early.
- Mechanical backlash may reduce pointing repeatability.
- INA219 accuracy may be enough for relative optimization but not for precision energy auditing.
- `TP4056` and `MT3608` add practical inefficiency, so measured net-gain results may be worse than idealized calculations.
- If the panel is too heavy, low-cost motors may stall or overheat.

## Mitigations

- Use a separated motor branch plus distinct 5 V and 3.3 V logic rails with controlled grounding discipline.
- Measure or estimate stall current before locking the motor-driver footprint.
- Add current limits, travel limits, and software deadbands to avoid hunting.
- Verify motor energy per movement experimentally, then feed that value into the Pi optimization algorithm.
- Use homing switches so angle estimates can be reset each startup.
- Place test points on the power rails and communication buses so bring-up can proceed in stages.
- Keep the final report honest that the charging and boost stages are low-cost pragmatic choices, not high-efficiency energy-harvesting ICs.

## Assumptions

- The mechanical team can provide a low-friction dual-axis mount compatible with modest torque motors.
- The team accepts demonstration-oriented energy measurement accuracy rather than laboratory-grade metrology.
- Any optional Raspberry Pi algorithm layer is an extension above the core STM32 hardware, not a prerequisite for board bring-up.

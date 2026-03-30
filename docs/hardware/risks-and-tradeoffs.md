# Risks and Tradeoffs

## Main Tradeoffs

### Geared DC Motors vs. Servos

- Geared DC motors plus encoder feedback are cheaper per torque and scale well for panel loads.
- Servos simplify control but may have limited range, weaker holding behavior, or worse long-term durability.

### TB6612FNG vs. BTS7960

- `TB6612FNG` is much more PCB-friendly for a compact student design and is a better fit for low-current tracker motors.
- `BTS7960` provides more current margin but is physically bulkier and less aligned with an integrated custom PCB unless the motor choice truly demands it.

### LDR Array vs. Dedicated Sun Sensor

- LDRs are cheap and easy to explain in a senior design setting.
- They are less accurate and more temperature-sensitive, so the control algorithm should combine light imbalance with measured power gain instead of trusting LDRs alone.

### UART vs. CAN

- UART is sufficient and easier for this project.
- CAN would be more robust electrically but adds complexity without clear benefit at this scale.

## Technical Risks

- Motor current spikes may brown out the Raspberry Pi if power rails are not isolated well.
- The chosen compact H-bridge may be under-sized if the motor stall current is not screened early.
- Mechanical backlash may reduce pointing repeatability.
- INA219 accuracy may be enough for relative optimization but not for precision energy auditing.
- If the panel is too heavy, low-cost motors may stall or overheat.

## Mitigations

- Use a separated motor branch plus distinct 5 V and 3.3 V logic rails with controlled grounding discipline.
- Measure or estimate stall current before locking the motor-driver footprint.
- Add current limits, travel limits, and software deadbands to avoid hunting.
- Verify motor energy per movement experimentally, then feed that value into the Pi optimization algorithm.
- Use homing switches so angle estimates can be reset each startup.
- Place test points on the power rails and communication buses so bring-up can proceed in stages.

## Assumptions

- The mechanical team can provide a low-friction dual-axis mount compatible with modest torque motors.
- The team accepts demonstration-oriented energy measurement accuracy rather than laboratory-grade metrology.
- The Raspberry Pi compute load is light enough that a `Pi Zero 2 W` is sufficient.

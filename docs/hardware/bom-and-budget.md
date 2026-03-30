# BOM and Budget

All prices are rough 2026 student-market estimates in RMB. The goal is to stay below the 1500 RMB cap with some reserve.

| Item | Qty | Est. Unit Cost (RMB) | Subtotal (RMB) | Notes |
|---|---:|---:|---:|---|
| STM32F407ZGT6 development board | 1 | 80 | 80 | Required controller |
| DC geared motor | 2 | 70 | 140 | Yaw and pitch axes |
| TB6612FNG dual H-bridge | 1 | 20 | 20 | Default on-board motor driver |
| INA219 current/voltage sensor | 2 | 18 | 36 | Panel rail and battery rail |
| LDR plus 10 kOhm resistor set | 1 set | 15 | 15 | Four-quadrant light sensing |
| 0.96 in I2C OLED | 1 | 20 | 20 | Local display |
| LM2596 or TPS5430 buck stage | 1 | 25 | 25 | Solar-side or bus-side 5 V regulation |
| TP4056 charging module | 1 | 8 | 8 | Safe single-cell charging |
| 18650 Li-ion cell | 1 | 20 | 20 | Battery storage |
| MT3608 boost converter | 1 | 8 | 8 | Battery to 5 V system rail |
| 3.3 V logic regulator stage | 1 | 8 | 8 | Logic and sensor rail |
| Push button, connectors, and test points | 1 set | 35 | 35 | UI, debug, and assembly |
| Small 5 V to 6 V solar panel | 1 | 80 | 80 | Demonstration source |
| PCB fabrication and misc. passive parts | 1 lot | 180 | 180 | Includes headers and wiring |
| Mechanical coupling/brackets reserve | 1 lot | 150 | 150 | Shared with ME subsystem |

Estimated total: `817 RMB`

Budget reserve: about `683 RMB`

## Cost Rationale

- The motors are deliberately modest in power because the project goal is net gain, not fast industrial tracking.
- `INA219` is good enough for demonstration-grade energy accounting and communicates cleanly over I2C.
- `TB6612FNG`, `TP4056`, `LM2596/TPS5430`, and `MT3608` match the new authoritative board-level design.
- Using LDRs for directional sensing is much cheaper than precision irradiance instruments and matches the course scope.

## Fallback Options

- If the full master-slave architecture is kept, a Raspberry Pi can still be added through a UART header without changing the core PCB design.
- If measured motor stall current is too high for `TB6612FNG`, switch only the driver stage to a higher-current alternative.
- If worm-geared motors are unavailable, use compact metal-geared DC motors only if travel, backlash, and holding torque still meet the mechanical requirement.
- If two INA219 boards are unnecessary, measure only the panel rail directly and infer battery usage from motor and system states.

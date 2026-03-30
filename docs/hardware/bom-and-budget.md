# BOM and Budget

All prices are rough 2026 student-market estimates in RMB. The goal is to stay below the 1500 RMB cap with some reserve.

| Item | Qty | Est. Unit Cost (RMB) | Subtotal (RMB) | Notes |
|---|---:|---:|---:|---|
| STM32F407ZGT6 development board | 1 | 80 | 80 | Required controller |
| Raspberry Pi Zero 2 W | 1 | 120 | 120 | Enough for optimization and UART supervision |
| Low-current geared DC motor with encoder | 2 | 75 | 150 | Yaw and pitch axes |
| TB6612FNG dual H-bridge | 1 | 20 | 20 | Default on-board motor driver |
| INA219 current/voltage sensor | 2 | 18 | 36 | Panel rail and battery rail |
| LDR plus resistor set | 1 set | 15 | 15 | Four-quadrant light sensing |
| 0.96 in I2C OLED | 1 | 20 | 20 | Local display |
| Limit switches | 4 | 5 | 20 | Two per axis |
| 5 V buck converter stage | 1 | 25 | 25 | Pi rail, target 3 A class |
| 3.3 V logic regulator stage | 1 | 8 | 8 | Logic and sensor rail |
| Push button, LED, buzzer, connectors, test points | 1 set | 40 | 40 | UI, debug, and assembly |
| Small solar panel for demo | 1 | 120 | 120 | Demonstration source |
| 3S battery pack / sealed battery | 1 | 180 | 180 | Energy storage |
| PCB fabrication and misc. passive parts | 1 lot | 180 | 180 | Includes headers and wiring |
| Mechanical coupling/brackets reserve | 1 lot | 150 | 150 | Shared with ME subsystem |

Estimated total: `1144 RMB`

Budget reserve: about `356 RMB`

## Cost Rationale

- The motors are deliberately modest in power because the project goal is net gain, not fast industrial tracking.
- `Pi Zero 2 W` keeps the RFA's Raspberry Pi requirement while reducing cost and standby power draw.
- `INA219` is good enough for demonstration-grade energy accounting and communicates cleanly over I2C.
- `TB6612FNG` makes more sense than `BTS7960` for a custom student PCB if the motor current is truly low enough.
- Using LDRs for directional sensing is much cheaper than precision irradiance instruments and matches the course scope.

## Fallback Options

- If a Pi Zero 2 W is unavailable, reuse any team-owned Raspberry Pi and keep the UART/software interface unchanged.
- If measured motor stall current is too high for `TB6612FNG`, switch only the driver stage to `BTS7960` or another higher-current driver rather than redesigning the rest of the board.
- If worm-geared motors are unavailable, use compact metal-geared DC motors only if travel, backlash, and holding torque still meet the mechanical requirement.
- If two INA219 boards are unnecessary, measure only the panel rail directly and infer battery usage from motor and system states.

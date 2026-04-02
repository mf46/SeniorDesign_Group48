# BOM and Budget

All prices are rough 2026 student-market estimates in RMB. The goal is to stay below the 1500 RMB cap with some reserve.

| Item | Qty | Est. Unit Cost (RMB) | Subtotal (RMB) | Notes |
|---|---:|---:|---:|---|
| STM32F407ZGT6 development board | 1 | 80 | 80 | Required controller |
| NEMA17 stepper motor | 2 | 80 | 160 | Yaw and pitch axes |
| A4988 stepper driver | 2 | 20 | 40 | One driver per axis |
| INA219 current/voltage sensor | 2 | 18 | 36 | Panel test path and motor branch |
| BH1750 lux sensor | 16 | 8 | 128 | `16`-sensor light ring |
| I2C mux module or IC | 1 | 20 | 20 | For repeated BH1750 addressing |
| 0.96 in I2C OLED | 1 | 20 | 20 | Local display |
| 12 V 5 A power adapter | 1 | 45 | 45 | Motor branch supply |
| 5 V logic supply | 1 | 20 | 20 | Raspberry Pi and STM32 supply |
| Push button, connectors, and test points | 1 set | 35 | 35 | UI, debug, and assembly |
| Small solar panel | 1 | 80 | 80 | Panel-under-test source |
| Dummy load parts | 1 lot | 25 | 25 | Resistor or MOS test load for panel measurement |
| PCB fabrication and misc. passive parts | 1 lot | 180 | 180 | Includes headers and wiring |
| Mechanical coupling/brackets reserve | 1 lot | 150 | 150 | Shared with ME subsystem |

Estimated total: `1019 RMB`

Budget reserve: about `481 RMB`

## Cost Rationale

- The current top-level source sketch describes the panel placeholder as `6V 100mA 80x55 mm`, which is adequate as a documentation assumption until the exact purchased panel is frozen.
- `NEMA17` keeps the actuation model compatible with target-angle control and open-loop step counting after homing.
- `INA219` is good enough for demonstration-grade energy accounting and communicates cleanly over I2C.
- `A4988` matches the final stepper control path.
- `BH1750 + mux` matches the final light-ring interface more directly than an analog ring prototype.
- Separate external `12V` and `5V` supplies simplify bring-up compared with a self-powered architecture. The top-level sketch currently calls the motor adapter out as `60W 12V 5A`.
- The Raspberry Pi remains a system-level RL node for inference and logging, but the PCB BOM stays centered on the STM32-side hardware actually mounted on the board.

## Fallback Options

- If Raspberry Pi deployment is delayed, the board can still be brought up and validated at the STM32 hardware level first.
- If the final `NEMA17` holding torque is larger than needed, a smaller stepper can still be substituted without changing the control abstraction.
- If the first chosen `A4988` module is hard to source, switch to another `STEP/DIR` compatible driver without changing the high-level protocol.
- If the first mux part is hard to source, switch to another I2C mux without changing the software-level light-ring abstraction.

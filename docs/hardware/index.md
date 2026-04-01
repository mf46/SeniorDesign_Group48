# Hardware Knowledge Base

This folder captures the proposed electrical and embedded architecture for the energy-aware solar tracker.

## Start Here

- [Authoritative hardware summary](./dual_axis_solar_tracker.md)
- [Proposal review](./proposal-review.md)
- [System architecture](./system-architecture.md)
- [BOM and budget](./bom-and-budget.md)
- [Interfaces and protocols](./interfaces-and-protocols.md)
- [Risks and tradeoffs](./risks-and-tradeoffs.md)

## Design Summary

- `STM32F407ZGT6` is the mandatory real-time controller.
- `dual_axis_solar_tracker.md` is the board-level source of truth.
- The custom PCB acts as the low-level control, sensing, power-conditioning, charging, and motor-drive board.
- Four-quadrant LDR sensing, dual `INA219` measurement, `TB6612FNG`, `LM2596/TPS5430`, `TP4056`, and `MT3608` form the baseline electrical stack.
- In the current RL pipeline, the Raspberry Pi is the online inference and logging node connected above the STM32 control board.
- The hardware notes should treat Pi connectivity as part of the RL control path, while still keeping the board-level hardware description focused on the STM32-centered PCB.

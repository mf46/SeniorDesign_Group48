# Hardware Knowledge Base

This folder captures the proposed electrical and embedded architecture for the energy-aware solar tracker.

## Start Here

- [System architecture](./system-architecture.md)
- [Proposal review](./proposal-review.md)
- [BOM and budget](./bom-and-budget.md)
- [Interfaces and protocols](./interfaces-and-protocols.md)
- [Risks and tradeoffs](./risks-and-tradeoffs.md)

## Design Summary

- `STM32F407ZGT6` is the mandatory real-time controller.
- `system-architecture.md` is the current hardware source of truth.
- The custom PCB acts as the low-level control, sensing, logic-interface, and motor-drive board.
- A `BH1750 + mux + 16-sensor ring`, dual `INA219` measurement, `NEMA17` stepper motors, `A4988` stepper drivers, and separate external `12V` and `5V` supplies form the current electrical stack.
- In the current RL pipeline, the Raspberry Pi is the online inference and logging node connected above the STM32 control board.
- The hardware notes should treat Pi connectivity as part of the RL control path, while still keeping the board-level hardware description focused on the STM32-centered PCB.

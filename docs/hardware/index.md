# Hardware Knowledge Base

This folder captures the proposed electrical and embedded architecture for the energy-aware solar tracker.

## Start Here

- [Proposal review](./proposal-review.md)
- [System architecture](./system-architecture.md)
- [BOM and budget](./bom-and-budget.md)
- [Interfaces and protocols](./interfaces-and-protocols.md)
- [Risks and tradeoffs](./risks-and-tradeoffs.md)

## Design Summary

- `STM32F407ZGT6` is the mandatory real-time controller.
- The custom PCB should act as the low-level control, power distribution, and measurement board.
- `Raspberry Pi Zero 2 W` is the preferred high-level optimizer because it is cheaper and lower-power than a Pi 4 while still satisfying the RFA architecture.
- Two low-current geared DC motors with encoders drive yaw and pitch through a compact dual H-bridge, with a heavier driver kept as fallback only if stall current testing demands it.
- Four-quadrant LDR sensing, INA219-based power measurement, and battery telemetry inform motion decisions.
- The STM32 exposes a compact UART packet protocol to the Raspberry Pi, shares I2C with INA219 plus OLED, and benefits from dedicated test points and strong/weak current partitioning on the PCB.

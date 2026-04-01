# Proposal Review

## Short Evaluation

The earlier `.docx` proposal was directionally strong, but the newer `dual_axis_solar_tracker.md` is now the authoritative hardware summary because it is more concrete about the actual board-level implementation. Its strongest contributions are:

- defining the board as a `low-level control + power distribution + measurement` board,
- using a concrete solar to buck to charger to battery to boost system power chain,
- keeping `STM32F407ZGT6` as the deterministic real-time controller,
- using `INA219` so the reward and evaluation path can be based on measured electrical data rather than guesswork,
- reusing `I2C` for OLED and power monitors,
- specifying an actual STM32 pin map for sensing and motor control.

## What Makes Sense

- `LDR quadrant + ADC` is a good low-cost way to get directional light information.
- `INA219` is a realistic choice for panel and battery/power-rail measurement in a senior design project.
- `I2C` shared across OLED and INA219 is standard and easy to debug.
- PCB partitioning between strong-current and weak-signal zones is exactly the right mindset.
- `TB6612FNG` is a clean fit for a low-power dual-axis tracker board.
- The current RL split keeps online inference on the Raspberry Pi while preserving deterministic execution on the `STM32`.

## What Is Risky or Needs Adjustment

- `TP4056` is simple and cheap, but it is a single-cell charger and not a true solar MPPT solution.
- `MT3608` is convenient for prototyping, but its conversion loss must be reflected honestly in any net-energy claim.
- `TB6612FNG` is only safe if the selected motor current stays within its comfort range.
- The hardware summary should explain clearly that the board itself is STM32-centered while the full RL pipeline still uses Raspberry Pi inference and offline training.

## Replacements to Current Assumptions

- Treat `dual_axis_solar_tracker.md` as the board-level source of truth.
- Replace the broad power-tree description with the specific chain: solar panel -> INA219 -> buck -> TP4056 -> 18650 -> INA219 -> MT3608 -> system rail.
- Replace generic motor-control language with the explicit `TB6612FNG + PWM + IN1/IN2` scheme and the stated STM32 pins.
- Replace any remaining "Pi is only optional optimization" phrasing with the current pipeline wording: Raspberry Pi performs online inference, logging, and model loading above the STM32 control layer.

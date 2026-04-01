# Proposal Review

## Short Evaluation

The earlier `.docx` proposal was directionally strong, but the current hardware definition has moved beyond that first-pass summary. Its strongest contributions are:

- defining the board as a `low-level control + power distribution + measurement` board,
- keeping the measurement path explicit even when the solar panel is only used as a test source,
- keeping `STM32F407ZGT6` as the deterministic real-time controller,
- using `INA219` so the reward and evaluation path can be based on measured electrical data rather than guesswork,
- reusing `I2C` for OLED and power monitors,
- keeping the Raspberry Pi inference path above the STM32 control layer.

## What Makes Sense

- A multi-channel light ring is a better match to the current RL input than a four-quadrant head.
- `INA219` is a realistic choice for panel-output and motor-branch measurement in a senior design project.
- `I2C` shared across OLED and INA219 is standard and easy to debug.
- `BH1750 + mux` is coherent with the final 16-sensor light-ring plan.
- PCB partitioning between strong-current and weak-signal zones is exactly the right mindset.
- The current RL split keeps online inference on the Raspberry Pi while preserving deterministic execution on the `STM32`.
- `NEMA17` plus `A4988` is coherent with a target-angle control pipeline.

## What Is Risky or Needs Adjustment

- `A4988` current limiting has to be tuned correctly for the chosen `NEMA17` setup.
- The `BH1750 + mux` polling strategy has to be defined so the control loop remains stable.
- The hardware summary should explain clearly that the board itself is STM32-centered while the full RL pipeline still uses Raspberry Pi inference and offline training.
- The final report must clearly state that the solar panel is measured as a test source and does not power the controller.

## Replacements to Current Assumptions

- Replace the old self-powered energy tree with the externally powered test architecture: solar panel -> INA219 -> dummy load, plus external 12 V motor branch and external 5 V logic branch.
- Replace generic motor-control language with the explicit `NEMA17 + A4988 + STEP/DIR` scheme and the stated STM32 pins.
- Replace analog light-ring assumptions with the `BH1750 + mux + 16-sensor ring` plan.
- Replace any remaining "Pi is only optional optimization" phrasing with the current pipeline wording: Raspberry Pi performs online inference, logging, and model loading above the STM32 control layer.

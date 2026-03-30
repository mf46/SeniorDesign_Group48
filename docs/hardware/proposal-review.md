# Proposal Review

## Short Evaluation

The `.docx` proposal is directionally strong and better aligned with a student-built PCB than our earlier hardware notes. Its best ideas are:

- defining the board as a `low-level control + power distribution + measurement` board,
- using a clear split between motor power, 5 V logic/compute power, and 3.3 V sensor logic,
- keeping `STM32F407ZGT6` as the deterministic real-time controller,
- using `INA219` so the reward path is based on measured electrical data rather than guesswork,
- reusing `I2C` for OLED and power monitors,
- emphasizing layout discipline, test points, and a Raspberry Pi UART header.

## What Makes Sense

- `STM32 + Raspberry Pi` matches the RFA master-slave split.
- `LDR quadrant + ADC` is a good low-cost way to get directional light information.
- `INA219` is a realistic choice for panel and battery/power-rail measurement in a senior design project.
- `I2C` shared across OLED and INA219 is standard and easy to debug.
- PCB partitioning between strong-current and weak-signal zones is exactly the right mindset.

## What Is Risky or Needs Adjustment

- A `Pi 4B/3B+` is overpowered for this job and costs more energy budget than needed. A `Pi Zero 2 W` is a better fit unless a heavier compute workload is proven necessary.
- `AMS1117-3.3` is acceptable only for small logic loads; it is not a good general answer for anything that may dissipate significant heat.
- `TB6612FNG` or `DRV8833` is only the right replacement for `BTS7960` if the selected motor stall current stays within the driver margin. The project should not lock in a light motor driver before measuring or screening motor current.
- The motor rail should not be described as just another 5 V logic branch. It must be treated as a noisy power domain with separate return-current management.

## Replacements to Current Assumptions

- Replace `Raspberry Pi 4B/3B+` with `Raspberry Pi Zero 2 W`.
- Replace `BTS7960` as the default driver with `TB6612FNG` as the baseline dual-H-bridge for low-current motors.
- Keep `BTS7960` or a similar higher-current fallback only if measured stall current exceeds the TB6612FNG comfort range.
- Make PCB test points, UART header, and strong/weak current partitioning first-class design requirements.

# Writing Notes

## Drafting Strategy

The LaTeX draft is intentionally written as a strong first-pass submission document rather than a minimal outline. It includes:

- a title page and table of contents
- a rubric-aligned introduction
- subsystem-level design sections with requirements and verification procedures
- a mathematical tolerance analysis tied to the net-energy decision logic
- draft cost and schedule sections
- ethics, safety, and references
- a more explicit lower-level PCB narrative covering power distribution, measurement, and testability

## Assumptions Used

- Team member list was inferred from the RFA text.
- Team number and advisor are still marked as TODO items in the LaTeX file.
- The hardware narrative now follows `docs/hardware/dual_axis_solar_tracker.md` as the board-level source of truth.
- Hardware part costs are provisional and should be reconciled with vendor quotes before submission.
- The tolerance analysis uses representative values to justify the decision threshold; replace them with measured prototype data when available.
- The LaTeX draft assumes `TB6612FNG`, `INA219`, `LM2596/TPS5430`, `TP4056`, and `MT3608` remain the baseline hardware choices.

## Recommended Next Updates

1. Replace the placeholder figures listed in `figure-plan.md`, especially the power-tree and control-PCB diagrams.
2. Replace any remaining placeholder figure text with diagrams that match the STM32 pin map and the solar -> buck -> charger -> battery -> boost power chain.
3. Update the schedule to match the official course week numbering.
4. Add finalized communication-protocol byte fields once the hardware/control interface is frozen.
5. Verify all external references are in the team’s required IEEE citation style at submission time.

# Writing Notes

## Drafting Strategy

The LaTeX draft is intentionally written as a strong first-pass submission document rather than a minimal outline. It includes:

- a title page and table of contents
- a rubric-aligned introduction
- subsystem-level design sections with requirements and verification procedures
- a mathematical tolerance analysis tied to the net-energy decision logic
- draft cost and schedule sections
- ethics, safety, and references
- a more explicit lower-level PCB narrative covering power distribution, measurement, control interfaces, and testability

## Assumptions Used

- Team member list was inferred from the RFA text.
- Team number and advisor are still marked as TODO items in the LaTeX file.
- The hardware narrative now follows `docs/hardware/system-architecture.md` as the board-level source of truth.
- The RL narrative is now fixed to the current pipeline: online inference uses only light-ring intensity plus current two-axis angle, while training and evaluation may additionally use logged electrical and safety data.
- The current angle in the RL state is defined as the previous target angle accepted by the `STM32` after homing, not a separately measured encoder angle.
- The final light sensing plan is `BH1750 + mux + 16-sensor ring`.
- The final power narrative is an external-power test platform; the solar panel is measured as a test source and does not power the controller.
- Hardware part costs are provisional and should be reconciled with vendor quotes before submission.
- The tolerance analysis uses representative values to justify the decision threshold; replace them with measured prototype data when available.
- The LaTeX draft assumes `NEMA17` stepper actuation, `A4988`, `INA219`, `BH1750 + mux`, and separate external `12V` and `5V` supplies remain the baseline hardware choices.

## Recommended Next Updates

1. Replace the placeholder figures listed in `figure-plan.md`, especially the control-flow, training-loop, and power-tree diagrams.
2. Replace any remaining placeholder figure text with diagrams that match the current RL pipeline and the external 12 V / 5 V split power architecture.
3. Update the schedule to match the official course week numbering.
4. Add finalized communication-protocol byte fields once the hardware/control interface is frozen.
5. Verify all external references are in the team’s required IEEE citation style at submission time.

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
- Hardware part costs are provisional and should be reconciled with the finalized BOM once the motor-driver family is frozen.
- The tolerance analysis uses representative values to justify the decision threshold; replace them with measured prototype data when available.
- The LaTeX draft intentionally uses generic wording such as ``two-channel motor-drive stage'' in places where the exact driver IC still depends on motor current validation.

## Recommended Next Updates

1. Replace the placeholder figures listed in `figure-plan.md`, especially the power-tree and control-PCB diagrams.
2. Replace generic motor-driver wording with the final chosen part after stall-current testing.
3. Update the schedule to match the official course week numbering.
4. Add finalized communication-protocol byte fields once the hardware/control interface is frozen.
5. Verify all external references are in the team’s required IEEE citation style at submission time.

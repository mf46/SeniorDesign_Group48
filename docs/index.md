# Docs Index

This `docs/` directory is the shared knowledge base for the senior design project.

## Main Areas

- [Project manager notes](./project-manager/index.md)
- [Hardware architecture](./hardware/index.md)
- [Design document notes](./design-doc/index.md)
- [RL document notes](./RL/index.md)

## Shared Context

- Project theme: dual-axis solar tracker optimized for net energy gain, not simple always-on tracking
- The original top-level hardware sketch from `TopLevel.txt` is now captured under `docs/hardware/top-level-reference.md`
- Control split: STM32F407ZGT6 handles real-time sensing, execution, status return, and safety; Raspberry Pi handles online inference, logging, and model loading
- RL pipeline: inference uses only the current light-ring readings and current two-axis angles, then predicts the next target angles for the two axes
- Training split: PC or cloud handles offline training, exports `ONNX`, and redeploys the model back to the Raspberry Pi
- Key constraints: one-semester scope, 1500 RMB hardware budget, one-button operation, measurable verification

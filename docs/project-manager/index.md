# Project Manager Knowledge Base

This folder is the project-management system of record for the senior design team. It is intentionally split into small notes so future agents can find the right context quickly.

## Start Here

- [Project overview](./project-overview.md)
- [Minghao Fang scope and interfaces](./minghao-scope.md)
- [Assumptions, risks, and open questions](./assumptions-risks-open-questions.md)
- [Milestones and verification focus](./milestones-and-verification.md)

## Working Notes

- The project is a net-energy-optimized solar tracking system, not a conventional "always track the sun" project.
- The current RL pipeline is formalized: `STM32` handles sensing and execution, Raspberry Pi handles inference and logging, and `PC/云端` handles offline training and model updates.
- The online model input is limited to light-ring intensity plus current two-axis angle, and the model output is the next target angles.
- Keep hardware, communication protocol, and verification criteria aligned with the one-semester, 1500 RMB budget.
- Prefer concise, durable notes over long narrative documents.

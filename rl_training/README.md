# RL Training Skeleton

This directory contains a simulator-first TD3 training skeleton for the dual-axis solar tracker.

## What It Covers

- `16`-sensor light ring + `2`-axis current-angle observation
- continuous `[-1, 1]^2` action that maps to absolute yaw/pitch target angles
- simplified simulator with panel-gain proxy, motor-cost proxy, hold behavior, and travel limits
- `PyTorch` TD3 training
- actor-only `ONNX` export for Raspberry Pi deployment

## Suggested Commands

Run a smoke training pass:

```bash
python -m rl_training.scripts.train_td3 --smoke
```

Evaluate a saved actor:

```bash
python -m rl_training.scripts.evaluate_policy --checkpoint rl_training/runs/default/best_actor.pt
```

Export the actor to ONNX:

```bash
python -m rl_training.scripts.export_onnx --checkpoint rl_training/runs/default/best_actor.pt
```

Run one ONNX inference demo:

```bash
python -m rl_training.scripts.run_onnx_demo --model rl_training/exports/policy_actor.onnx
```


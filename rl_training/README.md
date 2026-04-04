# RL Training Skeleton

This directory contains a simulator-first TD3 training skeleton for the dual-axis solar tracker.

## What It Covers

- `16`-sensor light ring + `2`-axis current-angle + `1` energy reserve observation
- continuous `[-1, 1]^2` action that maps to absolute yaw/pitch target angles
- simplified simulator with panel-gain proxy, motor-cost proxy, idle-power model, hold behavior, and travel limits
- two-stage training:
  - `stage1`: pure panel-power chasing
  - `stage2`: fine-tune from stage1 checkpoint with survival-oriented reward
- actor-only `ONNX` export for Raspberry Pi deployment

## Model Input

The final online input is `19`-dimensional:

- `light_ring[16]`
- `current_angle[2]`
- `energy_reserve[1]`

The model does not read raw `INA219` values directly.
Reward and RL logs also assume `STM32` has already converted low-level telemetry into derived quantities such as `panel_power`, `motor_power`, and `energy_reserve`.

## Feature Encoder

The current encoder uses a strict `24`-dimensional feature vector:

- `16` ring `log1p` features
- `2` normalized angles
- `1` energy reserve
- `4` angle trig features
- `1` ring mean

## Suggested Commands

Run a stage1 smoke pass:

```bash
python -m rl_training.scripts.train_td3 --stage stage1 --smoke
```

Evaluate the saved stage1 actor:

```bash
python -m rl_training.scripts.evaluate_policy --checkpoint rl_training/runs/default/stage1_best_actor.pt
```

Run stage2 fine-tuning from the stage1 checkpoint:

```bash
python -m rl_training.scripts.train_td3 --stage stage2 --resume rl_training/runs/default/stage1_best_actor.pt
```

Export the actor to ONNX:

```bash
python -m rl_training.scripts.export_onnx --checkpoint rl_training/runs/default/stage2_best_actor.pt
```

Run one ONNX inference demo:

```bash
python -m rl_training.scripts.run_onnx_demo --model rl_training/exports/policy_actor.onnx
```

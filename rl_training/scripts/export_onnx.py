"""Export a trained actor to ONNX."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from rl_training.models.actor import Actor
from rl_training.utils.checkpoint import load_torch_checkpoint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default="rl_training/exports/policy_actor.onnx")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    payload = load_torch_checkpoint(args.checkpoint, map_location=args.device)
    config = payload["config"]
    if config["model"]["feature_dim"] != 24:
        raise ValueError(f"Expected feature_dim=24, got {config['model']['feature_dim']}")

    actor = Actor(
        model_config=config["model"],
        angle_limits=[config["env"]["yaw_limits_deg"], config["env"]["pitch_limits_deg"]],
        num_sensors=config["env"]["num_sensors"],
    ).to(args.device)
    if actor.encoder.feature_dim != 24:
        raise ValueError(f"Actor encoder feature_dim must be 24, got {actor.encoder.feature_dim}")
    actor.load_state_dict(payload["actor"])
    actor.eval()

    dummy_state = torch.zeros(1, config["env"]["num_sensors"] + 3, dtype=torch.float32, device=args.device)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        actor,
        dummy_state,
        output_path.as_posix(),
        input_names=[config["export"]["onnx_input_name"]],
        output_names=[config["export"]["onnx_output_name"]],
        dynamic_axes={config["export"]["onnx_input_name"]: {0: "batch"}, config["export"]["onnx_output_name"]: {0: "batch"}},
        opset_version=config["export"]["opset_version"],
    )
    print(f"Exported ONNX model to {output_path}")


if __name__ == "__main__":
    main()

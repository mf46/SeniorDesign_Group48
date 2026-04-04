"""Run an exported ONNX actor on one simulated observation."""

from __future__ import annotations

import argparse

import numpy as np
import onnxruntime as ort

from rl_training.configs.default import get_default_config, get_reward_config
from rl_training.env.solar_tracker_env import SolarTrackerEnv
from rl_training.utils.angles import denormalize_action


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="rl_training/exports/policy_actor.onnx")
    args = parser.parse_args()

    config = get_default_config()
    reward_cfg = get_reward_config(config, "stage1")
    env = SolarTrackerEnv(config["env"], reward_cfg, "stage1")
    obs, _ = env.reset(seed=config["train"]["seed"])

    session = ort.InferenceSession(args.model, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    action_norm = session.run([output_name], {input_name: obs[None, :].astype(np.float32)})[0][0]
    target_angle = denormalize_action(action_norm, [config["env"]["yaw_limits_deg"], config["env"]["pitch_limits_deg"]])

    print("state_raw:", obs.tolist())
    print("action_norm:", action_norm.tolist())
    print("target_angle_deg:", target_angle.tolist())


if __name__ == "__main__":
    main()

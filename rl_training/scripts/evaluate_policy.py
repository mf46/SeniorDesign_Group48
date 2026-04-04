"""Evaluate a saved actor checkpoint in the simulator."""

from __future__ import annotations

import argparse

from rl_training.configs.default import get_default_config
from rl_training.env.solar_tracker_env import SolarTrackerEnv
from rl_training.models.actor import Actor
from rl_training.utils.checkpoint import load_torch_checkpoint
from rl_training.utils.logging import format_metrics
from rl_training.utils.seed import set_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    payload = load_torch_checkpoint(args.checkpoint, map_location=args.device)
    config = payload.get("config", get_default_config())
    set_seed(config["train"]["seed"])
    env = SolarTrackerEnv(config["env"], config["reward"])
    actor = Actor(
        model_config=config["model"],
        angle_limits=[config["env"]["yaw_limits_deg"], config["env"]["pitch_limits_deg"]],
        num_sensors=config["env"]["num_sensors"],
    ).to(args.device)
    actor.load_state_dict(payload["actor"])
    actor.eval()

    totals = {
        "episode_return": 0.0,
        "average_panel_gain_proxy": 0.0,
        "average_motor_cost_proxy": 0.0,
        "average_action_magnitude": 0.0,
        "hold_ratio": 0.0,
        "limit_hit_count": 0.0,
    }
    for episode_idx in range(args.episodes):
        obs, _ = env.reset(seed=episode_idx)
        done = False
        local = {"ret": 0.0, "panel": [], "motor": [], "action": 0.0, "hold": 0, "limit": 0, "steps": 0}
        while not done:
            action = actor.predict_normalized_action(obs, device=args.device)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            local["ret"] += reward
            local["panel"].append(info["panel_gain_proxy"])
            local["motor"].append(info["motor_cost_proxy"])
            local["action"] += float(abs(action).mean())
            local["hold"] += int(info["hold"])
            local["limit"] += int(info["limit_hit"])
            local["steps"] += 1
        totals["episode_return"] += local["ret"]
        totals["average_panel_gain_proxy"] += sum(local["panel"]) / max(len(local["panel"]), 1)
        totals["average_motor_cost_proxy"] += sum(local["motor"]) / max(len(local["motor"]), 1)
        totals["average_action_magnitude"] += local["action"] / max(local["steps"], 1)
        totals["hold_ratio"] += local["hold"] / max(local["steps"], 1)
        totals["limit_hit_count"] += local["limit"]
    for key in totals:
        totals[key] /= args.episodes
    print(format_metrics(totals))


if __name__ == "__main__":
    main()


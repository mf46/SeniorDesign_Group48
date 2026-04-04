"""Train the simulator-first TD3 policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rl_training.algorithms.replay_buffer import ReplayBuffer
from rl_training.algorithms.td3 import TD3Agent
from rl_training.configs.default import get_default_config
from rl_training.env.solar_tracker_env import SolarTrackerEnv
from rl_training.utils.checkpoint import load_torch_checkpoint, save_torch_checkpoint
from rl_training.utils.logging import append_jsonl, format_metrics
from rl_training.utils.seed import set_seed


def evaluate_agent(agent, env, episodes):
    totals = {
        "episode_return": 0.0,
        "average_panel_gain_proxy": 0.0,
        "average_motor_cost_proxy": 0.0,
        "average_action_magnitude": 0.0,
        "hold_ratio": 0.0,
        "limit_hit_count": 0.0,
    }
    for episode_idx in range(episodes):
        obs, _ = env.reset(seed=1000 + episode_idx)
        done = False
        episode_return = 0.0
        action_sum = 0.0
        hold_steps = 0
        panel_values = []
        motor_values = []
        limit_hits = 0
        step_count = 0
        while not done:
            action = agent.select_action(obs, noise_std=0.0)
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            obs = next_obs
            episode_return += reward
            action_sum += float(abs(action).mean())
            hold_steps += int(info["hold"])
            panel_values.append(float(info["panel_gain_proxy"]))
            motor_values.append(float(info["motor_cost_proxy"]))
            limit_hits += int(info["limit_hit"])
            step_count += 1
        totals["episode_return"] += episode_return
        totals["average_panel_gain_proxy"] += sum(panel_values) / max(len(panel_values), 1)
        totals["average_motor_cost_proxy"] += sum(motor_values) / max(len(motor_values), 1)
        totals["average_action_magnitude"] += action_sum / max(step_count, 1)
        totals["hold_ratio"] += hold_steps / max(step_count, 1)
        totals["limit_hit_count"] += limit_hits
    for key in totals:
        totals[key] /= episodes
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="rl_training/runs/default")
    parser.add_argument("--resume", default="")
    parser.add_argument("--device", default="")
    parser.add_argument("--total-steps", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    config = get_default_config()
    if args.device:
        config["train"]["device"] = args.device
    if args.total_steps > 0:
        config["train"]["total_steps"] = args.total_steps
    if args.smoke:
        config["train"]["total_steps"] = 600
        config["train"]["random_steps"] = 100
        config["train"]["update_after"] = 100
        config["train"]["update_every"] = 20
        config["train"]["eval_interval"] = 200
        config["train"]["checkpoint_interval"] = 200
        config["train"]["eval_episodes"] = 2
        config["train"]["batch_size"] = 64

    train_cfg = config["train"]
    set_seed(train_cfg["seed"])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    save_torch_checkpoint(output_dir / "config.pt", {"config": config})
    with (output_dir / "config.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)

    env = SolarTrackerEnv(config["env"], config["reward"])
    eval_env = SolarTrackerEnv(config["env"], config["reward"])
    agent = TD3Agent(
        model_config=config["model"],
        train_config=train_cfg,
        angle_limits=[config["env"]["yaw_limits_deg"], config["env"]["pitch_limits_deg"]],
        num_sensors=config["env"]["num_sensors"],
        device=train_cfg["device"],
    )
    buffer = ReplayBuffer(
        obs_dim=env.obs_dim,
        action_dim=env.action_dim,
        capacity=train_cfg["replay_capacity"],
        device=train_cfg["device"],
    )

    global_step = 0
    best_return = float("-inf")
    if args.resume:
        checkpoint = load_torch_checkpoint(args.resume, map_location=train_cfg["device"])
        agent.load_state_dict(checkpoint["agent"])
        global_step = checkpoint.get("global_step", 0)
        best_return = checkpoint.get("best_return", best_return)

    obs, _ = env.reset(seed=train_cfg["seed"])
    episode_return = 0.0
    episode_index = 0

    while global_step < train_cfg["total_steps"]:
        global_step += 1
        if global_step <= train_cfg["random_steps"]:
            action = env.sample_random_action()
        else:
            action = agent.select_action(obs, noise_std=train_cfg["exploration_noise"])

        next_obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        buffer.add(obs, action, reward, next_obs, done)
        obs = next_obs
        episode_return += reward

        if global_step >= train_cfg["update_after"] and len(buffer) >= train_cfg["batch_size"]:
            if global_step % train_cfg["update_every"] == 0:
                latest_train_metrics = {}
                for _ in range(train_cfg["update_every"]):
                    latest_train_metrics = agent.train_step(buffer, train_cfg["batch_size"])
                append_jsonl(
                    output_dir / "train_metrics.jsonl",
                    {"step": global_step, **latest_train_metrics},
                )

        if done:
            append_jsonl(
                output_dir / "episodes.jsonl",
                {
                    "episode": episode_index,
                    "step": global_step,
                    "episode_return": float(episode_return),
                    "limit_hit_count": int(info["limit_hit_count"]),
                },
            )
            episode_index += 1
            episode_return = 0.0
            obs, _ = env.reset()

        if global_step % train_cfg["eval_interval"] == 0:
            metrics = evaluate_agent(agent, eval_env, train_cfg["eval_episodes"])
            metrics["step"] = global_step
            append_jsonl(output_dir / "eval_metrics.jsonl", metrics)
            print(f"[eval] {format_metrics(metrics)}")
            if metrics["episode_return"] > best_return:
                best_return = metrics["episode_return"]
                save_torch_checkpoint(
                    output_dir / "best_actor.pt",
                    {
                        "actor": agent.actor.state_dict(),
                        "config": config,
                        "step": global_step,
                        "best_return": best_return,
                    },
                )

        if global_step % train_cfg["checkpoint_interval"] == 0:
            save_torch_checkpoint(
                output_dir / "latest.pt",
                {
                    "agent": agent.state_dict(),
                    "config": config,
                    "global_step": global_step,
                    "best_return": best_return,
                },
            )

    save_torch_checkpoint(
        output_dir / "latest.pt",
        {
            "agent": agent.state_dict(),
            "config": config,
            "global_step": global_step,
            "best_return": best_return,
        },
    )


if __name__ == "__main__":
    main()


"""Reward computation for the simplified simulator.

This module mirrors the project contract that RL-side reward uses only
STM32-derived quantities such as panel gain, motor cost proxies, and
energy reserve state. Raw INA219 voltage/current readings are out of scope.
"""

from __future__ import annotations


def compute_reward(
    stage_name,
    panel_gain,
    panel_delta,
    motor_cost,
    limit_hit,
    hold,
    reward_config,
    delta_net_gain=0.0,
    death=False,
):
    if stage_name == "stage1":
        reward = (
            reward_config["panel_weight"] * panel_gain
            + reward_config["panel_delta_weight"] * panel_delta
        )
        if limit_hit:
            reward -= reward_config["fault_penalty"]
    elif stage_name == "stage2":
        reward = (
            reward_config["delta_weight"] * delta_net_gain
            + reward_config["panel_weight"] * panel_gain
        )
        if limit_hit:
            reward -= reward_config["fault_penalty"]
        if hold and delta_net_gain >= reward_config["hold_delta_threshold"]:
            reward += reward_config["hold_bonus"]
        if death:
            reward -= reward_config["death_penalty"]
    else:
        raise ValueError(f"Unsupported stage_name: {stage_name}")

    components = {
        "panel_gain_proxy": float(panel_gain),
        "panel_delta_proxy": float(panel_delta),
        "motor_cost_proxy": float(motor_cost),
        "limit_hit": int(limit_hit),
        "hold": int(hold),
        "delta_net_gain_proxy": float(delta_net_gain),
        "death": int(death),
    }
    return float(reward), components

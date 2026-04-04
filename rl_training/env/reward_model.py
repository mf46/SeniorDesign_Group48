"""Reward computation for the simplified simulator."""

from __future__ import annotations


def compute_reward(
    panel_gain,
    panel_delta,
    motor_cost,
    move_magnitude,
    limit_hit,
    hold,
    reward_config,
):
    reward = (
        reward_config["panel_weight"] * panel_gain
        + reward_config["panel_delta_weight"] * panel_delta
        - reward_config["motor_weight"] * motor_cost
        - reward_config["move_weight"] * move_magnitude
    )
    if limit_hit:
        reward -= reward_config["limit_penalty"]
    if hold and panel_delta >= reward_config["hold_delta_threshold"]:
        reward += reward_config["hold_bonus"]
    components = {
        "panel_gain_proxy": float(panel_gain),
        "panel_delta_proxy": float(panel_delta),
        "motor_cost_proxy": float(motor_cost),
        "move_magnitude": float(move_magnitude),
        "limit_hit": int(limit_hit),
        "hold": int(hold),
    }
    return float(reward), components


"""Default configuration for simulator-first TD3 training."""

from copy import deepcopy


DEFAULT_CONFIG = {
    "env": {
        "num_sensors": 16,
        "episode_length": 240,
        "control_hz": 10.0,
        "yaw_limits_deg": (-60.0, 60.0),
        "pitch_limits_deg": (-30.0, 30.0),
        "max_delta_per_step_deg": (6.0, 4.0),
        "ambient_light": 0.08,
        "diffuse_gain": 0.35,
        "directional_gain": 0.95,
        "sensor_noise_std": 0.01,
        "sun_yaw_span_deg": 110.0,
        "sun_pitch_center_deg": 24.0,
        "sun_pitch_span_deg": 18.0,
        "hold_tolerance_deg": 0.75,
        "motor_cost_bias": 0.01,
        "motor_cost_scale": 0.14,
        "idle_power": 0.03,
        "initial_energy_reserve": 0.75,
        "reserve_min": 0.05,
        "reserve_max": 1.0,
        "stage2_window_steps": 5,
        "death_penalty": 4.0,
    },
    "model": {
        "ring_hidden_dim": 32,
        "aux_hidden_dim": 16,
        "fusion_hidden_dims": (64, 32),
        "critic_hidden_dims": (96, 96, 48),
        "feature_dim": 24,
    },
    "train": {
        "seed": 7,
        "device": "cpu",
        "stage_name": "stage1",
        "resume_from_stage1": "",
        "total_steps": 20000,
        "random_steps": 1000,
        "batch_size": 256,
        "replay_capacity": 200000,
        "gamma": 0.99,
        "tau": 0.005,
        "actor_lr": 1e-4,
        "critic_lr": 3e-4,
        "policy_noise": 0.1,
        "noise_clip": 0.2,
        "policy_delay": 2,
        "exploration_noise": 0.15,
        "update_after": 1000,
        "update_every": 50,
        "eval_interval": 2000,
        "eval_episodes": 5,
        "checkpoint_interval": 2000,
    },
    "stage1_reward": {
        "panel_weight": 1.0,
        "panel_delta_weight": 0.30,
        "fault_penalty": 1.5,
    },
    "stage2_reward": {
        "delta_weight": 1.0,
        "panel_weight": 0.20,
        "fault_penalty": 1.5,
        "hold_bonus": 0.05,
        "hold_delta_threshold": -0.02,
        "death_penalty": 4.0,
    },
    "export": {
        "opset_version": 17,
        "onnx_input_name": "state_raw",
        "onnx_output_name": "action_norm",
    },
}


def get_default_config():
    return deepcopy(DEFAULT_CONFIG)


def get_reward_config(config, stage_name):
    if stage_name == "stage1":
        return deepcopy(config["stage1_reward"])
    if stage_name == "stage2":
        return deepcopy(config["stage2_reward"])
    raise ValueError(f"Unsupported stage_name: {stage_name}")

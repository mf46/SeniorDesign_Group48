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
    },
    "model": {
        "ring_hidden_dim": 32,
        "aux_hidden_dim": 16,
        "fusion_hidden_dims": (64, 32),
        "critic_hidden_dims": (96, 96, 48),
    },
    "train": {
        "seed": 7,
        "device": "cpu",
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
    "reward": {
        "panel_weight": 1.0,
        "panel_delta_weight": 0.35,
        "motor_weight": 0.30,
        "move_weight": 0.08,
        "limit_penalty": 1.25,
        "hold_bonus": 0.04,
        "hold_delta_threshold": -0.02,
    },
    "export": {
        "opset_version": 17,
        "onnx_input_name": "state_raw",
        "onnx_output_name": "action_norm",
    },
}


def get_default_config():
    return deepcopy(DEFAULT_CONFIG)


"""A small simulator aligned with the project's online RL interface."""

from __future__ import annotations

import math

import numpy as np

from rl_training.env.reward_model import compute_reward
from rl_training.env.sensor_model import compute_light_ring, compute_panel_gain, spherical_to_vector, sun_angles_from_progress
from rl_training.utils.angles import build_angle_arrays, clip_delta, denormalize_action


class SolarTrackerEnv:
    """Simplified continuous-control environment for dual-axis solar tracking."""

    def __init__(self, env_config, reward_config):
        self.cfg = env_config
        self.reward_cfg = reward_config
        self.num_sensors = int(env_config["num_sensors"])
        self.angle_limits = np.asarray(
            [env_config["yaw_limits_deg"], env_config["pitch_limits_deg"]],
            dtype=np.float32,
        )
        self.max_delta_per_step = np.asarray(env_config["max_delta_per_step_deg"], dtype=np.float32)
        _, _, self.angle_mid, self.angle_half = build_angle_arrays(self.angle_limits)
        self.sensor_angles_rad = np.linspace(0.0, 2.0 * math.pi, self.num_sensors, endpoint=False, dtype=np.float32)
        self.obs_dim = self.num_sensors + 2
        self.action_dim = 2
        self.rng = np.random.default_rng()
        self.current_angle = self.angle_mid.copy()
        self.step_count = 0
        self.sun_bias = np.zeros(2, dtype=np.float32)
        self.limit_hit_count = 0

    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.step_count = 0
        self.limit_hit_count = 0
        self.sun_bias = np.asarray(
            [
                self.rng.uniform(-10.0, 10.0),
                self.rng.uniform(-4.0, 4.0),
            ],
            dtype=np.float32,
        )
        low = self.angle_limits[:, 0]
        high = self.angle_limits[:, 1]
        self.current_angle = self.rng.uniform(low, high).astype(np.float32)
        obs = self._build_observation()
        info = self._build_info(panel_gain=self._panel_gain(), motor_cost=0.0, move_magnitude=0.0, hold=True, limit_hit=False)
        return obs, info

    def _sun_angles(self):
        progress = self.step_count / max(self.cfg["episode_length"] - 1, 1)
        yaw, pitch = sun_angles_from_progress(
            progress,
            self.cfg["sun_yaw_span_deg"],
            self.cfg["sun_pitch_center_deg"],
            self.cfg["sun_pitch_span_deg"],
        )
        yaw += float(self.sun_bias[0])
        pitch += float(self.sun_bias[1])
        return yaw, pitch

    def _sun_vector(self):
        yaw, pitch = self._sun_angles()
        return spherical_to_vector(yaw, pitch)

    def _panel_normal(self):
        return spherical_to_vector(float(self.current_angle[0]), float(self.current_angle[1]))

    def _panel_gain(self):
        return compute_panel_gain(self._sun_vector(), self._panel_normal())

    def _light_ring(self):
        return compute_light_ring(
            sun_vector=self._sun_vector(),
            panel_normal=self._panel_normal(),
            sensor_angles_rad=self.sensor_angles_rad,
            ambient_light=self.cfg["ambient_light"],
            diffuse_gain=self.cfg["diffuse_gain"],
            directional_gain=self.cfg["directional_gain"],
            noise_std=self.cfg["sensor_noise_std"],
            rng=self.rng,
        )

    def _build_observation(self):
        light_ring = self._light_ring()
        return np.concatenate([light_ring, self.current_angle.astype(np.float32)], axis=0).astype(np.float32)

    def _build_info(self, panel_gain, motor_cost, move_magnitude, hold, limit_hit):
        return {
            "panel_gain_proxy": float(panel_gain),
            "motor_cost_proxy": float(motor_cost),
            "move_magnitude": float(move_magnitude),
            "hold": bool(hold),
            "limit_hit": bool(limit_hit),
            "limit_hit_count": int(self.limit_hit_count),
            "current_angle": self.current_angle.astype(np.float32).copy(),
            "sun_angles_deg": np.asarray(self._sun_angles(), dtype=np.float32),
        }

    def sample_random_action(self):
        return self.rng.uniform(-1.0, 1.0, size=(self.action_dim,)).astype(np.float32)

    def step(self, action_norm):
        action_norm = np.asarray(action_norm, dtype=np.float32).reshape(self.action_dim)
        panel_before = self._panel_gain()
        previous_angle = self.current_angle.copy()

        raw_target = denormalize_action(action_norm, self.angle_limits)
        applied_target = clip_delta(previous_angle, raw_target, self.max_delta_per_step, self.angle_limits)

        limit_hit = bool(np.any(np.abs(raw_target - applied_target) > 1e-4))
        if limit_hit:
            self.limit_hit_count += 1

        delta = applied_target - previous_angle
        hold = bool(np.all(np.abs(delta) <= self.cfg["hold_tolerance_deg"]))
        move_norm = np.abs(delta) / np.maximum(self.max_delta_per_step, 1e-6)
        move_magnitude = float(move_norm.mean())
        motor_cost = float(
            self.cfg["motor_cost_bias"]
            + self.cfg["motor_cost_scale"] * float(np.square(move_norm).mean())
        )

        self.current_angle = applied_target.astype(np.float32)
        self.step_count += 1

        panel_after = self._panel_gain()
        reward, components = compute_reward(
            panel_gain=panel_after,
            panel_delta=panel_after - panel_before,
            motor_cost=motor_cost,
            move_magnitude=move_magnitude,
            limit_hit=limit_hit,
            hold=hold,
            reward_config=self.reward_cfg,
        )

        terminated = self.step_count >= int(self.cfg["episode_length"])
        truncated = False
        observation = self._build_observation()
        info = self._build_info(panel_gain=panel_after, motor_cost=motor_cost, move_magnitude=move_magnitude, hold=hold, limit_hit=limit_hit)
        info.update(
            {
                "raw_target_angle": raw_target.astype(np.float32),
                "applied_target_angle": applied_target.astype(np.float32),
            }
        )
        info.update(components)
        return observation, reward, terminated, truncated, info


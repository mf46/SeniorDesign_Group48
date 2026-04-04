"""A small simulator aligned with the project's online RL interface."""

from __future__ import annotations

import math

import numpy as np

from rl_training.env.reward_model import compute_reward
from rl_training.env.sensor_model import compute_light_ring, compute_panel_gain, spherical_to_vector, sun_angles_from_progress
from rl_training.utils.angles import apply_step_delta_limit, build_angle_arrays, denormalize_action


class SolarTrackerEnv:
    """Simplified continuous-control environment for dual-axis solar tracking."""

    def __init__(self, env_config, reward_config, stage_name):
        self.cfg = env_config
        self.reward_cfg = reward_config
        self.stage_name = stage_name
        self.num_sensors = int(env_config["num_sensors"])
        if self.num_sensors != 16:
            raise ValueError(f"Current environment expects 16 sensors, got {self.num_sensors}")
        if int(env_config["episode_length"]) <= 1:
            raise ValueError(f"episode_length must be > 1, got {env_config['episode_length']}")
        self.angle_limits = np.asarray(
            [env_config["yaw_limits_deg"], env_config["pitch_limits_deg"]],
            dtype=np.float32,
        )
        self.max_delta_per_step = np.asarray(env_config["max_delta_per_step_deg"], dtype=np.float32)
        if np.any(self.max_delta_per_step <= 0.0):
            raise ValueError(f"max_delta_per_step_deg must be strictly positive, got {self.max_delta_per_step}")
        self.idle_power = float(env_config["idle_power"])
        self.reserve_min = float(env_config["reserve_min"])
        self.reserve_max = float(env_config["reserve_max"])
        self.initial_energy_reserve = float(env_config["initial_energy_reserve"])
        self.stage2_window_steps = int(env_config["stage2_window_steps"])
        self.death_penalty = float(env_config["death_penalty"])
        if not (0.0 < self.reserve_min < self.reserve_max <= 1.0):
            raise ValueError("reserve bounds must satisfy 0 < reserve_min < reserve_max <= 1")
        if not (self.reserve_min < self.initial_energy_reserve <= self.reserve_max):
            raise ValueError("initial_energy_reserve must be within (reserve_min, reserve_max]")
        if self.stage2_window_steps <= 0:
            raise ValueError("stage2_window_steps must be positive")

        _, _, self.angle_mid, _ = build_angle_arrays(self.angle_limits)
        self.sensor_angles_rad = np.linspace(0.0, 2.0 * math.pi, self.num_sensors, endpoint=False, dtype=np.float32)
        self.obs_dim = self.num_sensors + 3
        self.action_dim = 2
        self.rng = np.random.default_rng()
        self.current_angle = self.angle_mid.copy()
        self.energy_reserve = np.float32(self.initial_energy_reserve)
        self.step_count = 0
        self.sun_bias = np.zeros(2, dtype=np.float32)
        self.limit_hit_count = 0
        self.episode_length = int(env_config["episode_length"])
        self.dt = 1.0 / float(env_config["control_hz"])

    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.step_count = 0
        self.limit_hit_count = 0
        self.energy_reserve = np.float32(self.initial_energy_reserve)
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
        info = self._build_info(panel_gain=self._panel_gain(), motor_cost=0.0, hold=True, limit_hit=False, delta_net_gain=0.0, death=False)
        return obs, info

    def _sun_angles(self, step_offset=0, angle_override=None):
        progress = (self.step_count + step_offset) / (self.episode_length - 1)
        yaw, pitch = sun_angles_from_progress(
            progress,
            self.cfg["sun_yaw_span_deg"],
            self.cfg["sun_pitch_center_deg"],
            self.cfg["sun_pitch_span_deg"],
        )
        yaw += float(self.sun_bias[0])
        pitch += float(self.sun_bias[1])
        return yaw, pitch

    def _sun_vector(self, step_offset=0):
        yaw, pitch = self._sun_angles(step_offset=step_offset)
        return spherical_to_vector(yaw, pitch)

    def _panel_normal(self, angle=None):
        target_angle = self.current_angle if angle is None else np.asarray(angle, dtype=np.float32)
        return spherical_to_vector(float(target_angle[0]), float(target_angle[1]))

    def _panel_gain(self, step_offset=0, angle=None):
        return compute_panel_gain(self._sun_vector(step_offset=step_offset), self._panel_normal(angle=angle))

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

    def _estimate_motor_cost(self, previous_angle, applied_target):
        delta = applied_target - previous_angle
        move_norm = np.abs(delta) / self.max_delta_per_step
        move_magnitude = float(move_norm.mean())
        motor_cost = float(
            self.cfg["motor_cost_bias"]
            + self.cfg["motor_cost_scale"] * float(np.square(move_norm).mean())
        )
        return move_magnitude, motor_cost

    def _estimate_window_net_gain(self, candidate_angle, motor_cost_now):
        net_gain = 0.0
        for step_offset in range(self.stage2_window_steps):
            panel_gain = self._panel_gain(step_offset=step_offset, angle=candidate_angle)
            motor_cost = motor_cost_now if step_offset == 0 else 0.0
            net_gain += (panel_gain - motor_cost - self.idle_power) * self.dt
        return float(net_gain)

    def _build_observation(self):
        light_ring = self._light_ring()
        reserve = np.asarray([self.energy_reserve], dtype=np.float32)
        return np.concatenate([light_ring, self.current_angle.astype(np.float32), reserve], axis=0).astype(np.float32)

    def _build_info(self, panel_gain, motor_cost, hold, limit_hit, delta_net_gain, death):
        return {
            "panel_gain_proxy": float(panel_gain),
            "motor_cost_proxy": float(motor_cost),
            "hold": bool(hold),
            "limit_hit": bool(limit_hit),
            "limit_hit_count": int(self.limit_hit_count),
            "current_angle": self.current_angle.astype(np.float32).copy(),
            "energy_reserve": float(self.energy_reserve),
            "sun_angles_deg": np.asarray(self._sun_angles(), dtype=np.float32),
            "delta_net_gain_proxy": float(delta_net_gain),
            "death": bool(death),
        }

    def sample_random_action(self):
        return self.rng.uniform(-1.0, 1.0, size=(self.action_dim,)).astype(np.float32)

    def step(self, action_norm):
        action_norm = np.asarray(action_norm, dtype=np.float32).reshape(self.action_dim)
        if np.any(action_norm < -1.0) or np.any(action_norm > 1.0):
            raise ValueError(f"action_norm must stay within [-1, 1], got {action_norm}")

        panel_before = self._panel_gain()
        previous_angle = self.current_angle.copy()
        raw_target = denormalize_action(action_norm, self.angle_limits)

        # This limit is the actuator model used by the environment, not an error-recovery path.
        applied_target = apply_step_delta_limit(previous_angle, raw_target, self.max_delta_per_step, self.angle_limits)
        limit_hit = bool(np.any(np.abs(raw_target - applied_target) > 1e-4))
        if limit_hit:
            self.limit_hit_count += 1

        hold = bool(np.all(np.abs(applied_target - previous_angle) <= self.cfg["hold_tolerance_deg"]))
        _, motor_cost = self._estimate_motor_cost(previous_angle, applied_target)
        move_window_gain = self._estimate_window_net_gain(applied_target, motor_cost)
        hold_window_gain = self._estimate_window_net_gain(previous_angle, 0.0)
        delta_net_gain = move_window_gain - hold_window_gain

        self.current_angle = applied_target.astype(np.float32)
        self.step_count += 1

        panel_after = self._panel_gain()
        delta_energy = (panel_after - motor_cost - self.idle_power) * self.dt
        self.energy_reserve = np.float32(self.energy_reserve + delta_energy)
        death = bool(self.energy_reserve <= self.reserve_min)

        reward, components = compute_reward(
            stage_name=self.stage_name,
            panel_gain=panel_after,
            panel_delta=panel_after - panel_before,
            motor_cost=motor_cost,
            limit_hit=limit_hit,
            hold=hold,
            reward_config=self.reward_cfg,
            delta_net_gain=delta_net_gain,
            death=death,
        )

        terminated = death or self.step_count >= self.episode_length
        truncated = False
        observation = self._build_observation()
        info = self._build_info(
            panel_gain=panel_after,
            motor_cost=motor_cost,
            hold=hold,
            limit_hit=limit_hit,
            delta_net_gain=delta_net_gain,
            death=death,
        )
        info.update(
            {
                "raw_target_angle": raw_target.astype(np.float32),
                "applied_target_angle": applied_target.astype(np.float32),
            }
        )
        info.update(components)
        return observation, reward, terminated, truncated, info

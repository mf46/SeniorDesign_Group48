"""Angle conversion helpers shared by training and deployment code."""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def build_angle_arrays(angle_limits: Iterable[Tuple[float, float]]):
    limits = np.asarray(angle_limits, dtype=np.float32)
    low = limits[:, 0]
    high = limits[:, 1]
    mid = 0.5 * (low + high)
    half = 0.5 * (high - low)
    return low, high, mid, half


def normalize_angles(angles_deg, angle_limits):
    angles = np.asarray(angles_deg, dtype=np.float32)
    _, _, mid, half = build_angle_arrays(angle_limits)
    safe_half = np.where(half == 0.0, 1.0, half)
    return np.clip((angles - mid) / safe_half, -1.0, 1.0)


def denormalize_action(action_norm, angle_limits):
    action = np.asarray(action_norm, dtype=np.float32)
    low, high, mid, half = build_angle_arrays(angle_limits)
    target = mid + np.clip(action, -1.0, 1.0) * half
    return np.clip(target, low, high)


def clip_delta(current_angle, target_angle, max_delta_deg, angle_limits):
    current = np.asarray(current_angle, dtype=np.float32)
    target = np.asarray(target_angle, dtype=np.float32)
    max_delta = np.asarray(max_delta_deg, dtype=np.float32)
    limited = current + np.clip(target - current, -max_delta, max_delta)
    low, high, _, _ = build_angle_arrays(angle_limits)
    return np.clip(limited, low, high)


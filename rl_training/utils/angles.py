"""Angle conversion helpers shared by training and deployment code."""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def build_angle_arrays(angle_limits: Iterable[Tuple[float, float]]):
    limits = np.asarray(angle_limits, dtype=np.float32)
    if limits.shape != (2, 2):
        raise ValueError(f"angle_limits must have shape (2, 2), got {limits.shape}")
    low = limits[:, 0]
    high = limits[:, 1]
    half = 0.5 * (high - low)
    if np.any(high <= low):
        raise ValueError(f"angle_limits must satisfy high > low, got {limits}")
    if np.any(half <= 0.0):
        raise ValueError(f"angle_limits must have positive span, got {limits}")
    mid = 0.5 * (low + high)
    return low, high, mid, half


def normalize_angles(angles_deg, angle_limits):
    angles = np.asarray(angles_deg, dtype=np.float32)
    _, _, mid, half = build_angle_arrays(angle_limits)
    normalized = (angles - mid) / half
    if np.any(normalized < -1.0) or np.any(normalized > 1.0):
        raise ValueError(f"angles_deg out of range for angle_limits: {angles}")
    return normalized.astype(np.float32)


def denormalize_action(action_norm, angle_limits):
    action = np.asarray(action_norm, dtype=np.float32)
    if np.any(action < -1.0) or np.any(action > 1.0):
        raise ValueError(f"action_norm must stay within [-1, 1], got {action}")
    low, high, mid, half = build_angle_arrays(angle_limits)
    target = mid + action * half
    if np.any(target < low) or np.any(target > high):
        raise RuntimeError(f"denormalize_action produced out-of-range target: {target}")
    return target.astype(np.float32)


def apply_step_delta_limit(current_angle, target_angle, max_delta_deg, angle_limits):
    current = np.asarray(current_angle, dtype=np.float32)
    target = np.asarray(target_angle, dtype=np.float32)
    max_delta = np.asarray(max_delta_deg, dtype=np.float32)
    if current.shape != (2,) or target.shape != (2,) or max_delta.shape != (2,):
        raise ValueError("current_angle, target_angle, and max_delta_deg must all have shape (2,)")
    if np.any(max_delta <= 0.0):
        raise ValueError(f"max_delta_deg must be strictly positive, got {max_delta}")

    low, high, _, _ = build_angle_arrays(angle_limits)
    delta = target - current
    limited = current + np.sign(delta) * np.minimum(np.abs(delta), max_delta)
    if np.any(limited < low) or np.any(limited > high):
        raise RuntimeError(f"Actuator-constrained target violates angle_limits: {limited}")
    return limited.astype(np.float32)

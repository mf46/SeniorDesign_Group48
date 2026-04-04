"""Simplified solar-geometry and light-ring sensor model."""

from __future__ import annotations

import math

import numpy as np


def spherical_to_vector(yaw_deg: float, pitch_deg: float) -> np.ndarray:
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    return np.asarray(
        [
            math.cos(pitch) * math.cos(yaw),
            math.cos(pitch) * math.sin(yaw),
            math.sin(pitch),
        ],
        dtype=np.float32,
    )


def sun_angles_from_progress(progress: float, yaw_span_deg: float, pitch_center_deg: float, pitch_span_deg: float):
    centered = 2.0 * progress - 1.0
    yaw = centered * 0.5 * yaw_span_deg
    pitch = pitch_center_deg + pitch_span_deg * math.sin(math.pi * progress)
    return yaw, pitch


def build_tangent_basis(normal: np.ndarray):
    world_up = np.asarray([0.0, 0.0, 1.0], dtype=np.float32)
    tangent_x = np.cross(world_up, normal)
    if np.linalg.norm(tangent_x) < 1e-5:
        tangent_x = np.asarray([0.0, 1.0, 0.0], dtype=np.float32)
    tangent_x = tangent_x / np.linalg.norm(tangent_x)
    tangent_y = np.cross(normal, tangent_x)
    tangent_y = tangent_y / np.linalg.norm(tangent_y)
    return tangent_x, tangent_y


def compute_panel_gain(sun_vector: np.ndarray, panel_normal: np.ndarray) -> float:
    return float(max(np.dot(sun_vector, panel_normal), 0.0))


def compute_light_ring(
    sun_vector: np.ndarray,
    panel_normal: np.ndarray,
    sensor_angles_rad: np.ndarray,
    ambient_light: float,
    diffuse_gain: float,
    directional_gain: float,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    tangent_x, tangent_y = build_tangent_basis(panel_normal)
    incidence = max(np.dot(sun_vector, panel_normal), 0.0)
    projected = sun_vector - np.dot(sun_vector, panel_normal) * panel_normal
    projected_norm = float(np.linalg.norm(projected))
    if projected_norm > 1e-6:
        projected_unit = projected / projected_norm
    else:
        projected_unit = tangent_x

    sensor_dirs = (
        np.cos(sensor_angles_rad)[:, None] * tangent_x[None, :]
        + np.sin(sensor_angles_rad)[:, None] * tangent_y[None, :]
    )
    directional_alignment = np.clip(sensor_dirs @ projected_unit, 0.0, 1.0)

    base = ambient_light + diffuse_gain * incidence
    directional = directional_gain * projected_norm * directional_alignment
    readings = base + directional
    if noise_std > 0.0:
        readings = readings + rng.normal(0.0, noise_std, size=readings.shape)
    return np.clip(readings.astype(np.float32), 0.0, None)


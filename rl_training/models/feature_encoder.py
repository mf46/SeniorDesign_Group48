"""Fixed feature encoder from raw observation to model features."""

from __future__ import annotations

import math

import torch
from torch import nn


class StateFeatureEncoder(nn.Module):
    """Encode raw state into a compact, deployment-aligned feature vector."""

    def __init__(self, num_sensors=16, angle_limits=((-60.0, 60.0), (-30.0, 30.0))):
        super().__init__()
        self.num_sensors = num_sensors
        sensor_angles = torch.linspace(0.0, 2.0 * math.pi, steps=num_sensors + 1, dtype=torch.float32)[:-1]
        angle_limits_tensor = torch.tensor(angle_limits, dtype=torch.float32)
        angle_mid = 0.5 * (angle_limits_tensor[:, 0] + angle_limits_tensor[:, 1])
        angle_half = 0.5 * (angle_limits_tensor[:, 1] - angle_limits_tensor[:, 0])
        self.register_buffer("sensor_angles", sensor_angles)
        self.register_buffer("ring_log_mean", torch.zeros(num_sensors, dtype=torch.float32))
        self.register_buffer("ring_log_std", torch.ones(num_sensors, dtype=torch.float32))
        self.register_buffer("angle_mid", angle_mid)
        self.register_buffer("angle_half", angle_half)
        self.feature_dim = num_sensors + 2 + 4 + 1 + 2

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        squeeze = False
        if obs.dim() == 1:
            obs = obs.unsqueeze(0)
            squeeze = True

        light_ring = torch.clamp(obs[:, : self.num_sensors], min=0.0)
        angles_deg = obs[:, self.num_sensors : self.num_sensors + 2]

        log_ring = torch.log1p(light_ring)
        norm_ring = (log_ring - self.ring_log_mean) / torch.clamp(self.ring_log_std, min=1e-6)

        angle_norm = (angles_deg - self.angle_mid) / torch.clamp(self.angle_half, min=1e-6)
        angle_rad = torch.deg2rad(angles_deg)
        angle_trig = torch.cat([torch.sin(angle_rad), torch.cos(angle_rad)], dim=-1)

        ring_mean = log_ring.mean(dim=-1, keepdim=True)
        weights = log_ring / torch.clamp(log_ring.sum(dim=-1, keepdim=True), min=1e-6)
        ring_cos = torch.sum(weights * torch.cos(self.sensor_angles), dim=-1, keepdim=True)
        ring_sin = torch.sum(weights * torch.sin(self.sensor_angles), dim=-1, keepdim=True)

        features = torch.cat([norm_ring, angle_norm, angle_trig, ring_mean, ring_cos, ring_sin], dim=-1)
        return features.squeeze(0) if squeeze else features


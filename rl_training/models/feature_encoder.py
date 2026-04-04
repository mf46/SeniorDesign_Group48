"""Fixed feature encoder from raw observation to model features."""

from __future__ import annotations

import torch
from torch import nn


class StateFeatureEncoder(nn.Module):
    """Encode raw state into a compact, deployment-aligned feature vector."""

    def __init__(self, num_sensors=16, angle_limits=((-60.0, 60.0), (-30.0, 30.0))):
        super().__init__()
        if num_sensors != 16:
            raise ValueError(f"Current encoder expects 16 sensors, got {num_sensors}")
        angle_limits_tensor = torch.tensor(angle_limits, dtype=torch.float32)
        if angle_limits_tensor.shape != (2, 2):
            raise ValueError(f"angle_limits must have shape (2, 2), got {tuple(angle_limits_tensor.shape)}")
        angle_span = angle_limits_tensor[:, 1] - angle_limits_tensor[:, 0]
        if torch.any(angle_span <= 0.0):
            raise ValueError(f"angle_limits must satisfy high > low, got {angle_limits}")
        angle_mid = 0.5 * (angle_limits_tensor[:, 0] + angle_limits_tensor[:, 1])
        angle_half = 0.5 * angle_span
        self.num_sensors = num_sensors
        self.register_buffer("ring_log_mean", torch.zeros(num_sensors, dtype=torch.float32))
        self.register_buffer("ring_log_std", torch.ones(num_sensors, dtype=torch.float32))
        self.register_buffer("angle_mid", angle_mid)
        self.register_buffer("angle_half", angle_half)
        self.feature_dim = num_sensors + 2 + 1 + 4 + 1

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        squeeze = False
        if obs.dim() == 1:
            obs = obs.unsqueeze(0)
            squeeze = True
        if obs.dim() != 2:
            raise ValueError(f"obs must be 1D or 2D tensor, got dim={obs.dim()}")
        if obs.shape[-1] != self.num_sensors + 3:
            raise ValueError(f"obs last dimension must be {self.num_sensors + 3}, got {obs.shape[-1]}")

        light_ring = obs[:, : self.num_sensors]
        angles_deg = obs[:, self.num_sensors : self.num_sensors + 2]
        energy_reserve = obs[:, self.num_sensors + 2 : self.num_sensors + 3]

        if torch.any(light_ring < 0.0):
            raise ValueError("light_ring must be non-negative")
        if torch.any(energy_reserve < 0.0) or torch.any(energy_reserve > 1.0):
            raise ValueError("energy_reserve must be within [0, 1]")

        angle_norm = (angles_deg - self.angle_mid) / self.angle_half
        if torch.any(angle_norm < -1.0) or torch.any(angle_norm > 1.0):
            raise ValueError("angles_deg out of configured limits")

        log_ring = torch.log1p(light_ring)
        norm_ring = (log_ring - self.ring_log_mean) / self.ring_log_std
        angle_rad = torch.deg2rad(angles_deg)
        angle_trig = torch.cat([torch.sin(angle_rad), torch.cos(angle_rad)], dim=-1)
        ring_mean = log_ring.mean(dim=-1, keepdim=True)

        features = torch.cat([norm_ring, angle_norm, energy_reserve, angle_trig, ring_mean], dim=-1)
        return features.squeeze(0) if squeeze else features

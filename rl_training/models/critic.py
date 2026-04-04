"""Twin-critic implementation for TD3."""

from __future__ import annotations

import torch

from rl_training.models.actor import mlp
from rl_training.models.feature_encoder import StateFeatureEncoder

from torch import nn


class TwinCritic(nn.Module):
    def __init__(self, model_config, angle_limits, num_sensors=16):
        super().__init__()
        self.encoder = StateFeatureEncoder(num_sensors=num_sensors, angle_limits=angle_limits)
        hidden_dims = model_config["critic_hidden_dims"]
        self.q1 = mlp(self.encoder.feature_dim + 2, hidden_dims, 1)
        self.q2 = mlp(self.encoder.feature_dim + 2, hidden_dims, 1)

    def forward(self, obs, action):
        features = self.encoder(obs)
        if features.dim() == 1:
            features = features.unsqueeze(0)
        if action.dim() == 1:
            action = action.unsqueeze(0)
        critic_input = torch.cat([features, action], dim=-1)
        return self.q1(critic_input), self.q2(critic_input)

    def q1_forward(self, obs, action):
        features = self.encoder(obs)
        if features.dim() == 1:
            features = features.unsqueeze(0)
        if action.dim() == 1:
            action = action.unsqueeze(0)
        critic_input = torch.cat([features, action], dim=-1)
        return self.q1(critic_input)

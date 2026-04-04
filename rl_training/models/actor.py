"""Policy network for online inference and ONNX export."""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

from rl_training.models.feature_encoder import StateFeatureEncoder
from rl_training.utils.angles import denormalize_action


def mlp(in_dim, hidden_dims, out_dim):
    layers = []
    last_dim = in_dim
    for hidden_dim in hidden_dims:
        layers.append(nn.Linear(last_dim, hidden_dim))
        layers.append(nn.ReLU())
        last_dim = hidden_dim
    layers.append(nn.Linear(last_dim, out_dim))
    return nn.Sequential(*layers)


class Actor(nn.Module):
    def __init__(self, model_config, angle_limits, num_sensors=16):
        super().__init__()
        self.encoder = StateFeatureEncoder(num_sensors=num_sensors, angle_limits=angle_limits)
        if model_config["feature_dim"] != self.encoder.feature_dim:
            raise ValueError(
                f"Configured feature_dim {model_config['feature_dim']} does not match encoder feature_dim {self.encoder.feature_dim}"
            )
        self.ring_branch = mlp(
            num_sensors,
            (model_config["ring_hidden_dim"], model_config["ring_hidden_dim"]),
            model_config["ring_hidden_dim"],
        )
        self.aux_branch = mlp(
            7,
            (model_config["aux_hidden_dim"], model_config["aux_hidden_dim"]),
            model_config["aux_hidden_dim"],
        )
        fusion_dims = model_config["fusion_hidden_dims"]
        self.fusion = mlp(
            model_config["ring_hidden_dim"] + model_config["aux_hidden_dim"],
            fusion_dims,
            2,
        )

    def forward(self, obs):
        features = self.encoder(obs)
        if features.dim() == 1:
            features = features.unsqueeze(0)
        ring_feat = self.ring_branch(features[:, :16])
        aux_feat = self.aux_branch(features[:, 16:])
        action = torch.tanh(self.fusion(torch.cat([ring_feat, aux_feat], dim=-1)))
        return action

    @torch.no_grad()
    def predict_normalized_action(self, state_raw, device="cpu"):
        state_tensor = torch.as_tensor(state_raw, dtype=torch.float32, device=device)
        action = self.forward(state_tensor).squeeze(0)
        return action.cpu().numpy().astype(np.float32)

    @torch.no_grad()
    def predict_target_angle(self, state_raw, angle_limits, device="cpu"):
        action_norm = self.predict_normalized_action(state_raw, device=device)
        return denormalize_action(action_norm, angle_limits)

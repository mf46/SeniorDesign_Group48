"""TD3 training implementation."""

from __future__ import annotations

import copy

import numpy as np
import torch
import torch.nn.functional as F

from rl_training.models.actor import Actor
from rl_training.models.critic import TwinCritic


class TD3Agent:
    def __init__(self, model_config, train_config, angle_limits, num_sensors=16, device="cpu"):
        self.device = torch.device(device)
        self.train_config = train_config
        self.actor = Actor(model_config, angle_limits=angle_limits, num_sensors=num_sensors).to(self.device)
        self.actor_target = copy.deepcopy(self.actor).to(self.device)
        self.critic = TwinCritic(model_config, angle_limits=angle_limits, num_sensors=num_sensors).to(self.device)
        self.critic_target = copy.deepcopy(self.critic).to(self.device)

        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=train_config["actor_lr"])
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=train_config["critic_lr"])

        self.gamma = train_config["gamma"]
        self.tau = train_config["tau"]
        self.policy_noise = train_config["policy_noise"]
        self.noise_clip = train_config["noise_clip"]
        self.policy_delay = train_config["policy_delay"]
        self.total_updates = 0

    @torch.no_grad()
    def select_action(self, obs, noise_std=0.0):
        action = self.actor.predict_normalized_action(obs, device=self.device)
        if noise_std > 0.0:
            action = action + np.random.normal(0.0, noise_std, size=action.shape).astype(np.float32)
        return np.clip(action, -1.0, 1.0).astype(np.float32)

    def train_step(self, replay_buffer, batch_size):
        batch = replay_buffer.sample(batch_size)
        obs = batch["obs"]
        actions = batch["actions"]
        rewards = batch["rewards"]
        next_obs = batch["next_obs"]
        not_dones = batch["not_dones"]

        with torch.no_grad():
            noise = torch.randn_like(actions) * self.policy_noise
            noise = noise.clamp(-self.noise_clip, self.noise_clip)
            next_actions = (self.actor_target(next_obs) + noise).clamp(-1.0, 1.0)
            target_q1, target_q2 = self.critic_target(next_obs, next_actions)
            target_q = torch.min(target_q1, target_q2)
            target_q = rewards + not_dones * self.gamma * target_q

        current_q1, current_q2 = self.critic(obs, actions)
        critic_loss = F.mse_loss(current_q1, target_q) + F.mse_loss(current_q2, target_q)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        metrics = {
            "critic_loss": float(critic_loss.item()),
        }

        if self.total_updates % self.policy_delay == 0:
            actor_actions = self.actor(obs)
            actor_loss = -self.critic.q1_forward(obs, actor_actions).mean()
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()
            self._soft_update(self.actor, self.actor_target)
            self._soft_update(self.critic, self.critic_target)
            metrics["actor_loss"] = float(actor_loss.item())

        self.total_updates += 1
        return metrics

    def _soft_update(self, source, target):
        for source_param, target_param in zip(source.parameters(), target.parameters()):
            target_param.data.mul_(1.0 - self.tau)
            target_param.data.add_(self.tau * source_param.data)

    def state_dict(self):
        return {
            "actor": self.actor.state_dict(),
            "actor_target": self.actor_target.state_dict(),
            "critic": self.critic.state_dict(),
            "critic_target": self.critic_target.state_dict(),
            "actor_optimizer": self.actor_optimizer.state_dict(),
            "critic_optimizer": self.critic_optimizer.state_dict(),
            "total_updates": self.total_updates,
        }

    def load_state_dict(self, payload):
        self.actor.load_state_dict(payload["actor"])
        self.actor_target.load_state_dict(payload["actor_target"])
        self.critic.load_state_dict(payload["critic"])
        self.critic_target.load_state_dict(payload["critic_target"])
        self.actor_optimizer.load_state_dict(payload["actor_optimizer"])
        self.critic_optimizer.load_state_dict(payload["critic_optimizer"])
        self.total_updates = payload.get("total_updates", 0)


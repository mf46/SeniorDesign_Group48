"""Replay buffer for continuous-control training."""

from __future__ import annotations

import numpy as np
import torch


class ReplayBuffer:
    def __init__(self, obs_dim, action_dim, capacity, device="cpu"):
        self.capacity = int(capacity)
        self.device = device
        self.obs = np.zeros((self.capacity, obs_dim), dtype=np.float32)
        self.next_obs = np.zeros((self.capacity, obs_dim), dtype=np.float32)
        self.actions = np.zeros((self.capacity, action_dim), dtype=np.float32)
        self.rewards = np.zeros((self.capacity, 1), dtype=np.float32)
        self.not_dones = np.zeros((self.capacity, 1), dtype=np.float32)
        self.ptr = 0
        self.size = 0

    def __len__(self):
        return self.size

    def add(self, obs, action, reward, next_obs, done):
        self.obs[self.ptr] = obs
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.next_obs[self.ptr] = next_obs
        self.not_dones[self.ptr] = 1.0 - float(done)
        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        indices = np.random.randint(0, self.size, size=batch_size)
        return {
            "obs": torch.as_tensor(self.obs[indices], device=self.device),
            "actions": torch.as_tensor(self.actions[indices], device=self.device),
            "rewards": torch.as_tensor(self.rewards[indices], device=self.device),
            "next_obs": torch.as_tensor(self.next_obs[indices], device=self.device),
            "not_dones": torch.as_tensor(self.not_dones[indices], device=self.device),
        }


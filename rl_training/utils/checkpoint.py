"""Checkpoint helpers for TD3 training."""

from __future__ import annotations

from pathlib import Path

import torch


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def save_torch_checkpoint(path, payload):
    ensure_parent(path)
    torch.save(payload, path)


def load_torch_checkpoint(path, map_location="cpu"):
    return torch.load(path, map_location=map_location)


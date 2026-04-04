"""Normalization helpers for raw observations."""

from __future__ import annotations

import numpy as np


class RunningMeanStd:
    """Simple running statistics for optional future log-based calibration."""

    def __init__(self, epsilon=1e-4):
        self.count = epsilon
        self.mean = 0.0
        self.var = 1.0

    def update(self, values):
        values = np.asarray(values, dtype=np.float32)
        batch_mean = float(values.mean())
        batch_var = float(values.var())
        batch_count = values.size
        delta = batch_mean - self.mean
        total = self.count + batch_count
        new_mean = self.mean + delta * batch_count / total
        m_a = self.var * self.count
        m_b = batch_var * batch_count
        m_2 = m_a + m_b + delta * delta * self.count * batch_count / total
        self.mean = new_mean
        self.var = m_2 / total
        self.count = total

    @property
    def std(self):
        return float(np.sqrt(self.var + 1e-8))


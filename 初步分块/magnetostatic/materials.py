"""Constitutive data for scalar-potential magnetostatics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class Air:
    relative_permeability: float = 1.0

    def __post_init__(self) -> None:
        if self.relative_permeability <= 0.0:
            raise ValueError("relative permeability must be positive")

    @property
    def magnetization(self) -> tuple[float, float, float]:
        """Return the zero magnetization ``(0, 0, 0)`` in A/m."""
        return (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class PermanentMagnet:
    """Linear permanent magnet in ``B = mu0 * (mu_r H + M)`` form.

    ``magnetization`` is stored as an immutable tuple so the frozen
    dataclass cannot be mutated in place through a numpy array.
    """

    magnetization: tuple[float, float, float]
    relative_permeability: float = 1.0

    def __init__(
        self,
        magnetization: Iterable[float],
        relative_permeability: float = 1.0,
    ) -> None:
        vector = np.asarray(magnetization, dtype=float)
        if vector.shape != (3,):
            raise ValueError("magnetization must contain exactly three values")
        if relative_permeability <= 0.0:
            raise ValueError("relative permeability must be positive")
        object.__setattr__(
            self, "magnetization", tuple(float(item) for item in vector.tolist())
        )
        object.__setattr__(self, "relative_permeability", relative_permeability)

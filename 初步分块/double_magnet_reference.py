"""Reference solutions used only by the cuboidal double-magnet benchmark."""

from __future__ import annotations

from itertools import product
import math

import numpy as np


MU0 = 4.0 * math.pi * 1.0e-7
BR_Z = 0.38


ANSYS_REFERENCE_FORCE = {
    0.0: (0.59446, 0.62914),
    2.0: (0.22622, 0.64344),
    4.0: (-0.004062, 0.64730),
    6.0: (-0.22972, 0.64007),
    8.0: (-0.60745, 0.60659),
    10.0: (-0.93074, 0.52447),
    12.0: (-1.09950, 0.43539),
    14.0: (-1.13700, 0.35075),
    16.0: (-1.08570, 0.23258),
    18.0: (-0.91710, 0.12708),
    20.0: (-0.58312, 0.041178),
    22.0: (-0.24666, 0.0034075),
    24.0: (-0.079544, 0.0021191),
    26.0: (0.010552, 0.0039768),
    28.0: (0.036675, -0.0022967),
    30.0: (0.052253, 0.011228),
}


def akoun_yonnet_force(displacement_mm: float) -> np.ndarray:
    """Return the analytical force on the upper magnet as ``(Fx, Fy)``."""
    d = float(displacement_mm)
    a, b, c = np.array([10.0, 6.0, 3.0]) * 1.0e-3
    A, B, C = np.array([6.0, 10.0, 3.0]) * 1.0e-3
    alpha, beta, gamma = np.array([-4.0 + d, -4.0, 8.0]) * 1.0e-3
    force = np.zeros(2)

    for m, n, p, q, r, s in product((0, 1), repeat=6):
        U = alpha + A * (-1) ** m - a * (-1) ** n
        V = beta + B * (-1) ** q - b * (-1) ** p
        W = gamma + C * (-1) ** s - c * (-1) ** r
        R = np.sqrt(U**2 + V**2 + W**2)
        angle = np.arctan2(U * V, W * R)
        sign = (-1) ** (m + n + p + q + r + s)
        force[0] += sign * (
            (V**2 - W**2) * np.log(R - U) / 2
            + U * V * np.log(R - V)
            + V * W * angle
            + U * R / 2
        )
        force[1] += sign * (
            (U**2 - W**2) * np.log(R - V) / 2
            + U * V * np.log(R - U)
            + U * W * angle
            + V * R / 2
        )
    return BR_Z**2 * force / (4 * np.pi * MU0)


def ansys_reference_force(displacement_mm: float) -> np.ndarray:
    """Return ANSYS ``(Fx, Fy)`` or NaNs when the displacement is unavailable."""
    value = ANSYS_REFERENCE_FORCE.get(float(displacement_mm))
    if value is None:
        return np.full(2, np.nan)
    return np.asarray(value, dtype=float)


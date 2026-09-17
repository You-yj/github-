"""Geometry and mesh-size descriptions independent of Gmsh state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np


def _vector3(value: Iterable[float], name: str) -> tuple[float, float, float]:
    """Convert ``value`` into a validated length-3 tuple of floats."""
    result = np.asarray(value, dtype=float)
    if result.shape != (3,):
        raise ValueError(f"{name} must contain exactly three values")
    return tuple(float(item) for item in result.tolist())


@dataclass(frozen=True)
class BoxRegion:
    """An axis-aligned named volume, expressed in SI units (metres).

    ``center`` and ``size`` are stored as immutable tuples so that the
    frozen dataclass cannot be mutated in place through numpy arrays.
    """

    name: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    priority: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "center", _vector3(self.center, "center"))
        object.__setattr__(self, "size", _vector3(self.size, "size"))
        if not self.name:
            raise ValueError("region name must not be empty")
        if np.any(np.asarray(self.size) <= 0.0):
            raise ValueError("all box dimensions must be positive")

    @classmethod
    def from_corners(
        cls,
        name: str,
        lower: Iterable[float],
        upper: Iterable[float],
        priority: int = 0,
    ) -> "BoxRegion":
        """Construct from exact corner coordinates.

        Deriving the lower corner as ``center - size / 2`` can differ from
        the caller's corner by one ulp; this constructor stores the corners
        verbatim so that mesh generation reproduces reference geometries
        bit for bit.
        """
        lower = _vector3(lower, "lower")
        upper = _vector3(upper, "upper")
        if np.any(np.asarray(upper) <= np.asarray(lower)):
            raise ValueError("upper corners must exceed lower corners")
        center = tuple(0.5 * (lower[i] + upper[i]) for i in range(3))
        size = tuple(upper[i] - lower[i] for i in range(3))
        region = cls(name, center, size, priority)
        object.__setattr__(region, "_lower", lower)
        object.__setattr__(region, "_upper", upper)
        return region

    @property
    def lower(self) -> np.ndarray:
        """Lower corner as a fresh numpy array.

        Exact when the region was built with :meth:`from_corners`; otherwise
        computed as ``center - size / 2``.
        """
        stored = getattr(self, "_lower", None)
        if stored is not None:
            return np.asarray(stored)
        return np.asarray(self.center) - 0.5 * np.asarray(self.size)

    @property
    def upper(self) -> np.ndarray:
        """Upper corner as a fresh numpy array.

        Exact when the region was built with :meth:`from_corners`; otherwise
        computed as ``center + size / 2``.
        """
        stored = getattr(self, "_upper", None)
        if stored is not None:
            return np.asarray(stored)
        return np.asarray(self.center) + 0.5 * np.asarray(self.size)


@dataclass(frozen=True)
class BoxSizeField:
    """Gmsh Box background field, expressed in SI units.

    ``lower`` and ``upper`` are stored as immutable tuples.
    """

    lower: tuple[float, float, float]
    upper: tuple[float, float, float]
    h_inside: float
    h_outside: float
    thickness: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "lower", _vector3(self.lower, "lower"))
        object.__setattr__(self, "upper", _vector3(self.upper, "upper"))
        if np.any(np.asarray(self.upper) <= np.asarray(self.lower)):
            raise ValueError("field upper bounds must exceed lower bounds")
        if self.h_inside <= 0.0 or self.h_outside <= 0.0:
            raise ValueError("mesh sizes must be positive")
        if self.thickness < 0.0:
            raise ValueError("field thickness must be non-negative")


@dataclass(frozen=True)
class MeshOptions:
    """Options controlling the linear tetrahedral geometry mesh."""

    size_fields: tuple[BoxSizeField, ...] = ()
    algorithm_3d: int = 10
    show: bool = False


@dataclass(frozen=True)
class GeometryModel:
    """Outer domain and named embedded volumes.

    Embedded regions may overlap. Higher-priority regions own cells in an
    overlap; this lets a magnet override an auxiliary Maxwell-air volume.
    """

    outer: BoxRegion
    regions: tuple[BoxRegion, ...] = field(default_factory=tuple)
    interface_names: dict[str, tuple[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        names = [self.outer.name, *(region.name for region in self.regions)]
        if len(names) != len(set(names)):
            raise ValueError("all geometry region names must be unique")
        known = set(names)
        for surface_name, pair in self.interface_names.items():
            if not surface_name or len(pair) != 2 or not set(pair) <= known:
                raise ValueError(f"invalid named interface {surface_name!r}: {pair!r}")

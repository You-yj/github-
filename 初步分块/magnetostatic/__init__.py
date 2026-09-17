"""Reusable scalar-potential magnetostatic finite-element components."""

from .geometry import BoxRegion, BoxSizeField, GeometryModel, MeshOptions
from .materials import Air, PermanentMagnet
from .mesh import GmshTetraMesher, MeshData
from .pde import ScalarPotentialPDE
from .postprocess import MaxwellStressPostprocessor, SurfaceData
from .solver import FEMSolution, ScalarPotentialSolver, SolverOptions

__all__ = [
    "Air",
    "BoxRegion",
    "BoxSizeField",
    "FEMSolution",
    "GeometryModel",
    "GmshTetraMesher",
    "MaxwellStressPostprocessor",
    "MeshData",
    "MeshOptions",
    "PermanentMagnet",
    "ScalarPotentialPDE",
    "ScalarPotentialSolver",
    "SolverOptions",
    "SurfaceData",
]

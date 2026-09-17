"""Finite-element assembly and solution for magnetic scalar potential."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

from scipy.sparse.linalg import cg

try:
    import pyamg
except ImportError:
    pyamg = None

from fealpy.backend import backend_manager as bm
from fealpy.fem import BilinearForm, GradSourceIntegrator, LinearForm
from fealpy.fem import ScalarDiffusionIntegrator
from fealpy.functionspace import LagrangeFESpace
from fealpy.typing import TensorLike

from .mesh import MeshData
from .pde import ScalarPotentialPDE


@dataclass(frozen=True)
class SolverOptions:
    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    maxiter: int = 5000


@dataclass
class FEMSolution:
    mesh_data: MeshData
    pde: ScalarPotentialPDE
    space: LagrangeFESpace
    degree: int
    potential: TensorLike
    solver_info: dict = field(default_factory=dict)


class ScalarPotentialSolver:
    def __init__(self, p: int = 1, options: SolverOptions = SolverOptions()):
        if p < 1:
            raise ValueError("the Lagrange degree p must be at least one")
        self.p = int(p)
        self.options = options

    def assemble(self, mesh_data: MeshData, pde: ScalarPotentialPDE):
        space = LagrangeFESpace(mesh_data.mesh, p=self.p)
        mu_r = pde.relative_permeability_by_cell(mesh_data)
        bilinear = BilinearForm(space)
        if bm.allclose(mu_r, 1.0):
            integrator = ScalarDiffusionIntegrator(q=self.p + 1)
        else:
            integrator = ScalarDiffusionIntegrator(coef=mu_r[:, None], q=self.p + 1)
        bilinear.add_integrator(integrator)
        stiffness = bilinear.assembly()

        linear = LinearForm(space)
        linear.add_integrator(
            GradSourceIntegrator(pde.magnetization_by_cell(mesh_data), q=self.p)
        )
        rhs = linear.assembly()
        return space, stiffness, rhs

    def solve(self, mesh_data: MeshData, pde: ScalarPotentialPDE) -> FEMSolution:
        space, stiffness, rhs = self.assemble(mesh_data, pde)
        matrix = stiffness.to_scipy().tocsr()
        vector = bm.to_numpy(rhs)
        if pyamg is not None:
            multigrid = pyamg.smoothed_aggregation_solver(
                matrix, symmetry="symmetric"
            )
            preconditioner = multigrid.aspreconditioner(cycle="V")
        else:
            warnings.warn(
                "pyamg is not installed; falling back to unpreconditioned CG",
                RuntimeWarning,
                stacklevel=2,
            )
            preconditioner = None
        potential, info = cg(
            matrix,
            vector,
            M=preconditioner,
            rtol=self.options.rtol,
            atol=self.options.atol,
            maxiter=self.options.maxiter,
        )
        if info < 0:
            raise RuntimeError(f"CG failed with status {info}")
        if info > 0:
            warnings.warn(
                f"CG reached the iteration limit ({info}) without meeting "
                "the requested tolerance; the returned solution may be "
                "inaccurate",
                RuntimeWarning,
                stacklevel=2,
            )
        return FEMSolution(
            mesh_data=mesh_data,
            pde=pde,
            space=space,
            degree=self.p,
            potential=bm.from_numpy(potential),
            solver_info={"cg_info": int(info)},
        )

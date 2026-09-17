"""PDE data for the magnetic scalar-potential equation."""

from __future__ import annotations

import numpy as np

from fealpy.backend import backend_manager as bm

from .materials import Air, PermanentMagnet
from .mesh import MeshData

Material = Air | PermanentMagnet


class ScalarPotentialPDE:
    """Region-wise material model for ``B = mu0 * (mu_r H + M)``."""

    def __init__(self, materials: dict[str, Material], mu0=4.0e-7 * np.pi):
        self.materials = dict(materials)
        self.mu0 = float(mu0)

    def validate(self, mesh_data: MeshData) -> None:
        missing = set(mesh_data.region_tags) - set(self.materials)
        if missing:
            raise ValueError(f"materials missing for regions: {sorted(missing)}")

    def relative_permeability_by_cell(self, mesh_data: MeshData):
        self.validate(mesh_data)
        values = bm.ones(
            mesh_data.mesh.number_of_cells(), dtype=mesh_data.mesh.ftype
        )
        for name, tag in mesh_data.region_tags.items():
            values = bm.set_at(
                values,
                mesh_data.cell_tags == tag,
                self.materials[name].relative_permeability,
            )
        return values

    def magnetization_by_cell(self, mesh_data: MeshData):
        self.validate(mesh_data)
        values = bm.zeros(
            (mesh_data.mesh.number_of_cells(), 1, 3),
            dtype=mesh_data.mesh.ftype,
        )
        for name, tag in mesh_data.region_tags.items():
            vector = bm.asarray(
                self.materials[name].magnetization, dtype=mesh_data.mesh.ftype
            )
            values = bm.set_at(values, (mesh_data.cell_tags == tag, 0, slice(None)), vector)
        return values

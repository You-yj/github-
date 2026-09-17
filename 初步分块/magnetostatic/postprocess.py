"""Magnetic-field recovery and Maxwell stress integration."""

from __future__ import annotations

from dataclasses import dataclass

from fealpy.backend import backend_manager as bm
from fealpy.typing import TensorLike

from .solver import FEMSolution


@dataclass
class SurfaceData:
    face_indices: TensorLike
    outward_normals: TensorLike
    inside_region: str
    outside_region: str


class MaxwellStressPostprocessor:
    def select_interface(self, solution: FEMSolution, name: str) -> SurfaceData:
        mesh_data = solution.mesh_data
        try:
            inside_name, outside_name = mesh_data.interface_names[name]
        except KeyError as exc:
            raise KeyError(f"unknown named interface {name!r}") from exc

        inside_tag = mesh_data.tag(inside_name)
        outside_tag = mesh_data.tag(outside_name)
        face_to_cell = mesh_data.mesh.face_to_cell()[:, :2]
        adjacent_tags = mesh_data.cell_tags[face_to_cell]
        selected = (
            ((adjacent_tags[:, 0] == inside_tag) & (adjacent_tags[:, 1] == outside_tag))
            | ((adjacent_tags[:, 1] == inside_tag) & (adjacent_tags[:, 0] == outside_tag))
        )
        indices = bm.nonzero(selected)[0]
        if len(indices) == 0:
            raise ValueError(f"interface {name!r} contains no mesh faces")

        adjacency = face_to_cell[indices]
        tags = mesh_data.cell_tags[adjacency]
        inside_on_first = tags[:, 0] == inside_tag
        inside_cells = bm.where(inside_on_first, adjacency[:, 0], adjacency[:, 1])
        outside_cells = bm.where(inside_on_first, adjacency[:, 1], adjacency[:, 0])
        centers = mesh_data.mesh.entity_barycenter("cell")
        direction = centers[outside_cells] - centers[inside_cells]
        normals = bm.copy(mesh_data.mesh.face_unit_normal(index=indices))
        points_outward = bm.einsum("fi,fi->f", normals, direction) > 0.0
        normals = bm.set_at(normals, ~points_outward, -normals[~points_outward])
        return SurfaceData(indices, normals, inside_name, outside_name)

    @staticmethod
    def _cell_grad_basis_on_faces(solution, face_indices, face_bc, side):
        mesh = solution.mesh_data.mesh
        face = mesh.entity("face")[face_indices]
        cells = mesh.entity("cell")
        adjacency = mesh.face_to_cell()[face_indices]
        adjacent_cells = adjacency[:, side]
        local_cells = cells[adjacent_cells]
        result = bm.empty(
            (
                len(face_indices),
                len(face_bc),
                solution.space.number_of_local_dofs("cell"),
                3,
            ),
            dtype=face_bc.dtype,
        )
        positions = bm.argmax(face[:, :, None] == local_cells[:, None, :], axis=2)
        patterns, pattern_index = bm.unique(positions, axis=0, return_inverse=True)
        for index in range(len(patterns)):
            group = bm.nonzero(pattern_index == index)[0]
            cell_bc = bm.zeros((len(face_bc), 4), dtype=face_bc.dtype)
            cell_bc = bm.set_at(cell_bc, (slice(None), patterns[index]), face_bc)
            basis = solution.space.grad_basis(cell_bc, index=adjacent_cells[group])
            result = bm.set_at(result, group, basis)
        return result

    def compute_force(self, solution: FEMSolution, surface_name: str):
        surface = self.select_interface(solution, surface_name)
        mesh = solution.mesh_data.mesh
        degree = solution.degree
        quadrature = mesh.quadrature_formula(2 * degree - 1, "face")
        face_bc, weights = quadrature.get_quadrature_points_and_weights()
        adjacency = mesh.face_to_cell()[surface.face_indices]
        cell_to_dof = solution.space.cell_to_dof()
        mu_r = solution.pde.relative_permeability_by_cell(solution.mesh_data)
        magnetization = solution.pde.magnetization_by_cell(solution.mesh_data)[:, 0, :]

        magnetic_flux = []
        for side in (0, 1):
            basis = self._cell_grad_basis_on_faces(
                solution, surface.face_indices, face_bc, side
            )
            cell_index = adjacency[:, side]
            local_phi = solution.potential[cell_to_dof[cell_index]]
            grad_phi = bm.einsum("fi,fqid->fqd", local_phi, basis)
            b_side = solution.pde.mu0 * (
                magnetization[cell_index, None, :]
                - mu_r[cell_index, None, None] * grad_phi
            )
            magnetic_flux.append(b_side)
        face_b = 0.5 * (magnetic_flux[0] + magnetic_flux[1])

        normals = surface.outward_normals[:, None, :]
        b_dot_n = bm.sum(face_b * normals, axis=-1)
        b_squared = bm.sum(face_b * face_b, axis=-1)
        traction = (
            b_dot_n[:, :, None] * face_b
            - 0.5 * b_squared[:, :, None] * normals
        ) / solution.pde.mu0
        areas = mesh.entity_measure("face")[surface.face_indices]
        return bm.einsum("f,q,fqi->i", areas, weights, traction)

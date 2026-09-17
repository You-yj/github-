"""Gmsh-to-FEALPy conforming tetrahedral mesh generation."""

from __future__ import annotations

from dataclasses import dataclass, field

import gmsh
import numpy as np

from fealpy.backend import backend_manager as bm
from fealpy.mesh import TetrahedronMesh
from fealpy.typing import TensorLike

from .geometry import GeometryModel, MeshOptions


@dataclass
class MeshData:
    mesh: TetrahedronMesh
    cell_tags: TensorLike
    region_tags: dict[str, int]
    interface_names: dict[str, tuple[str, str]] = field(default_factory=dict)

    def tag(self, region_name: str) -> int:
        try:
            return self.region_tags[region_name]
        except KeyError as exc:
            raise KeyError(f"unknown mesh region {region_name!r}") from exc


def _extract_tetra_mesh(volume_to_cell_tag: dict[int, int]):
    node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
    node_tags = np.asarray(node_tags, dtype=np.int64)
    nodes = np.asarray(coordinates, dtype=float).reshape(-1, 3)
    element_tags, connectivity = gmsh.model.mesh.getElementsByType(4)
    element_tags = np.asarray(element_tags, dtype=np.int64)
    connectivity = np.asarray(connectivity, dtype=np.int64).reshape(-1, 4)

    node_tag_to_index = np.empty(node_tags.max() + 1, dtype=np.int64)
    node_tag_to_index[node_tags] = np.arange(len(node_tags))
    cells = node_tag_to_index[connectivity]

    element_tag_to_cell = np.full(element_tags.max() + 1, -1, dtype=np.int64)
    element_tag_to_cell[element_tags] = np.arange(len(element_tags))
    cell_tags = np.zeros(len(cells), dtype=np.int32)
    for volume_tag, cell_tag in volume_to_cell_tag.items():
        tags, _ = gmsh.model.mesh.getElementsByType(4, volume_tag)
        tags = np.asarray(tags, dtype=np.int64)
        if len(tags):
            cell_tags[element_tag_to_cell[tags]] = cell_tag

    mesh = TetrahedronMesh(bm.from_numpy(nodes), bm.from_numpy(cells))
    return mesh, bm.from_numpy(cell_tags)


class GmshTetraMesher:
    """Generate a conforming linear tetrahedral mesh for box regions."""

    def generate(
        self,
        geometry: GeometryModel,
        options: MeshOptions = MeshOptions(),
        model_name: str = "magnetostatic",
    ) -> MeshData:
        region_tags = {geometry.outer.name: 0}
        ordered_regions = sorted(geometry.regions, key=lambda item: item.priority)
        region_tags.update(
            (region.name, index + 1) for index, region in enumerate(ordered_regions)
        )

        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.model.add(model_name)
            outer = gmsh.model.occ.addBox(
                *geometry.outer.lower, *geometry.outer.size
            )
            embedded = [
                gmsh.model.occ.addBox(*region.lower, *region.size)
                for region in ordered_regions
            ]
            if embedded:
                _, fragment_map = gmsh.model.occ.fragment(
                    [(3, outer)], [(3, tag) for tag in embedded]
                )
            else:
                # Gmsh skips the boolean fragment when a single volume is
                # given; the outer box then maps directly to itself.
                fragment_map = [[(3, outer)]]
            gmsh.model.occ.synchronize()

            self._configure_size_fields(options)
            gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
            gmsh.option.setNumber("Mesh.Algorithm3D", options.algorithm_3d)
            gmsh.option.setNumber("Mesh.ElementOrder", 1)
            gmsh.model.mesh.generate(3)

            volume_to_cell_tag: dict[int, int] = {}
            # The outer domain owns every cell initially. Embedded regions are
            # applied in priority order so later (higher-priority) regions win.
            for _, volume_tag in fragment_map[0]:
                volume_to_cell_tag[volume_tag] = region_tags[geometry.outer.name]
            for region, mapped_volumes in zip(ordered_regions, fragment_map[1:]):
                for _, volume_tag in mapped_volumes:
                    volume_to_cell_tag[volume_tag] = region_tags[region.name]

            mesh, cell_tags = _extract_tetra_mesh(volume_to_cell_tag)
            if options.show:
                gmsh.fltk.run()
        finally:
            gmsh.finalize()

        return MeshData(
            mesh=mesh,
            cell_tags=cell_tags,
            region_tags=region_tags,
            interface_names=dict(geometry.interface_names),
        )

    @staticmethod
    def _configure_size_fields(options: MeshOptions) -> None:
        fields = []
        for config in options.size_fields:
            field = gmsh.model.mesh.field.add("Box")
            fields.append(field)
            gmsh.model.mesh.field.setNumber(field, "VIn", config.h_inside)
            gmsh.model.mesh.field.setNumber(field, "VOut", config.h_outside)
            gmsh.model.mesh.field.setNumber(field, "Thickness", config.thickness)
            for axis, lower, upper in zip("XYZ", config.lower, config.upper):
                gmsh.model.mesh.field.setNumber(field, f"{axis}Min", lower)
                gmsh.model.mesh.field.setNumber(field, f"{axis}Max", upper)
        if len(fields) == 1:
            gmsh.model.mesh.field.setAsBackgroundMesh(fields[0])
        elif fields:
            combined = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(combined, "FieldsList", fields)
            gmsh.model.mesh.field.setAsBackgroundMesh(combined)

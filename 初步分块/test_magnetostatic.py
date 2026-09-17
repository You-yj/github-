"""Unit tests for the reusable magnetostatic package (no Gmsh required)."""

import numpy as np
import pytest
from dataclasses import FrozenInstanceError

from fealpy.backend import backend_manager as bm
from fealpy.mesh import TetrahedronMesh

from magnetostatic import (
    Air,
    BoxRegion,
    BoxSizeField,
    GeometryModel,
    MeshData,
    PermanentMagnet,
    ScalarPotentialPDE,
)


def _unit_cube_mesh():
    """Return a six-tetrahedron mesh of the unit cube."""
    nodes = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
        ]
    )
    cells = np.array(
        [
            [0, 3, 1, 7],
            [0, 5, 1, 7],
            [0, 3, 2, 7],
            [0, 6, 2, 7],
            [0, 5, 4, 7],
            [0, 6, 4, 7],
        ]
    )
    return TetrahedronMesh(bm.from_numpy(nodes), bm.from_numpy(cells))


def _mesh_data(cell_tags, region_tags):
    mesh = _unit_cube_mesh()
    return MeshData(
        mesh=mesh,
        cell_tags=bm.from_numpy(np.asarray(cell_tags)),
        region_tags=region_tags,
    )


# ---------- materials ----------


def test_air_defaults():
    air = Air()
    assert air.relative_permeability == 1.0
    assert air.magnetization == (0.0, 0.0, 0.0)


def test_air_rejects_non_positive_permeability():
    with pytest.raises(ValueError):
        Air(relative_permeability=0.0)
    with pytest.raises(ValueError):
        Air(relative_permeability=-5.0)


def test_permanent_magnet_validates():
    with pytest.raises(ValueError):
        PermanentMagnet([0.0, 0.0])  # 非三维向量
    with pytest.raises(ValueError):
        PermanentMagnet([0.0, 0.0, 1.0], relative_permeability=0.0)


def test_permanent_magnet_immutable_fields():
    magnet = PermanentMagnet([0.0, 0.0, 3.0e5])
    assert magnet.magnetization == (0.0, 0.0, 3.0e5)
    assert isinstance(magnet.magnetization, tuple)


# ---------- geometry ----------


def test_box_region_stores_immutable_tuples():
    region = BoxRegion("magnet", [0.0, 0.0, 0.0], [0.02, 0.012, 0.006], 10)
    assert isinstance(region.center, tuple)
    assert isinstance(region.size, tuple)
    np.testing.assert_allclose(region.lower, [-0.01, -0.006, -0.003])
    np.testing.assert_allclose(region.upper, [0.01, 0.006, 0.003])
    with pytest.raises(FrozenInstanceError):
        region.priority = 5  # frozen


def test_box_region_validates():
    with pytest.raises(ValueError):
        BoxRegion("", [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
    with pytest.raises(ValueError):
        BoxRegion("bad", [0.0, 0.0], [1.0, 1.0, 1.0])
    with pytest.raises(ValueError):
        BoxRegion("bad", [0.0, 0.0, 0.0], [1.0, 0.0, 1.0])


def test_box_size_field_validates():
    with pytest.raises(ValueError):
        BoxSizeField([1.0, 0.0, 0.0], [1.0, 1.0, 1.0], 0.1, 0.2)
    with pytest.raises(ValueError):
        BoxSizeField([0.0, 0.0, 0.0], [1.0, 1.0, 1.0], -0.1, 0.2)
    with pytest.raises(ValueError):
        BoxSizeField([0.0, 0.0, 0.0], [1.0, 1.0, 1.0], 0.1, 0.2, thickness=-1.0)


def test_geometry_model_validates_names_and_interfaces():
    outer = BoxRegion("air", [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
    with pytest.raises(ValueError):
        GeometryModel(
            outer=outer,
            regions=(BoxRegion("air", [0.1, 0.1, 0.1], [0.2, 0.2, 0.2]),),
        )
    with pytest.raises(ValueError):
        GeometryModel(outer=outer, interface_names={"s": ("air", "ghost")})
    with pytest.raises(ValueError):
        GeometryModel(outer=outer, interface_names={"s": ("air",)})


# ---------- pde ----------


def test_pde_missing_material_raises():
    pde = ScalarPotentialPDE({"air": Air()})
    mesh_data = _mesh_data([0, 0, 0, 1, 1, 1], {"air": 0, "magnet": 1})
    with pytest.raises(ValueError):
        pde.validate(mesh_data)


def test_pde_cell_fields_shapes():
    pde = ScalarPotentialPDE(
        {"air": Air(), "magnet": PermanentMagnet([0.0, 0.0, 3.0e5])}
    )
    mesh_data = _mesh_data([0, 0, 0, 1, 1, 1], {"air": 0, "magnet": 1})
    mu_r = pde.relative_permeability_by_cell(mesh_data)
    assert mu_r.shape == (6,)
    assert bm.allclose(mu_r, 1.0)
    magnetization = pde.magnetization_by_cell(mesh_data)
    assert magnetization.shape == (6, 1, 3)
    assert bm.allclose(magnetization[:, 0, 2], 3.0e5 * (bm.arange(6) >= 3))


# ---------- solver (variable-permeability branch) ----------


def test_variable_permeability_assembly():
    pytest.importorskip("pyamg")
    from magnetostatic import ScalarPotentialSolver

    mesh_data = _mesh_data([0, 0, 0, 1, 1, 1], {"air": 0, "magnet": 1})
    unit_pde = ScalarPotentialPDE(
        {
            "air": Air(),
            "magnet": PermanentMagnet([0.0, 0.0, 0.0], relative_permeability=1.0),
        }
    )
    variable_pde = ScalarPotentialPDE(
        {
            "air": Air(),
            "magnet": PermanentMagnet([0.0, 0.0, 0.0], relative_permeability=5.0),
        }
    )
    solver = ScalarPotentialSolver(p=1)

    space_unit, stiffness_unit, _ = solver.assemble(mesh_data, unit_pde)
    space_var, stiffness_var, _ = solver.assemble(mesh_data, variable_pde)

    assert stiffness_var.shape == stiffness_unit.shape
    dense_unit = stiffness_unit.to_scipy().tocsr().toarray()
    dense_var = stiffness_var.to_scipy().tocsr().toarray()
    assert not np.allclose(dense_unit, dense_var)
    # 变系数矩阵仍应对称
    assert np.allclose(dense_var, dense_var.T)

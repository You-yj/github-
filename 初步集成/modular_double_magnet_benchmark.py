#!/usr/bin/env python3
"""Double-magnet benchmark assembled from FEALPy magnetostatic components.

The reusable magnetostatic components (materials, box-region Gmsh meshing,
the magnetic scalar-potential FEM model and Maxwell-stress postprocessing)
are imported from the ``fealpy`` checkout inside this project. The bootstrap
block below puts that checkout first on ``sys.path`` so the benchmark always
imports this vendored FEALPy instead of any other installed copy.
"""

from __future__ import annotations

# Make the vendored FEALPy checkout in this project take precedence over any
# other installed copy (for example an editable install elsewhere).
import sys
from pathlib import Path

_FEALPY_REPO = Path(__file__).resolve().parent / "fealpy"
if str(_FEALPY_REPO) not in sys.path:
    sys.path.insert(0, str(_FEALPY_REPO))

import numpy as np

from fealpy.backend import backend_manager as bm
from fealpy.cem.fem import MU0, MagnetostaticLFEMModel
from fealpy.material import Air, PermanentMagnet
from fealpy.mesher import BoxRegionMesher


BR_Z = 0.38
MZ = BR_Z / MU0


def make_mesher(
    displacement_mm: float,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
) -> BoxRegionMesher:
    """Build the benchmark geometry and mesh options using SI units.

    Command-line sizes stay in mm and are converted to m inside the options.

    ``d >= 0`` and ``h_near <= h_far`` are benchmark semantics: the generic
    ``BoxRegionMesher`` accepts any valid geometry and any size-field pair,
    so these two constraints deliberately live here rather than in fealpy.
    """
    d = float(displacement_mm)
    h_near = float(h_near_mm)
    h_far = float(h_far_mm)
    # 带参数名的快速失败；BoxRegionMesher 会在网格生成前二次校验尺寸场数值。
    if not np.isfinite(d) or d < 0.0:
        raise ValueError("displacement_mm must be finite and non-negative")
    if not np.isfinite(h_near) or h_near <= 0.0:
        raise ValueError("h_near_mm must be finite and positive")
    if not np.isfinite(h_far) or h_far <= 0.0:
        raise ValueError("h_far_mm must be finite and positive")
    if h_near > h_far:
        raise ValueError("h_near_mm must not exceed h_far_mm")
    x_max_mm = 30.0 + max(d - 8.0, 0.0)
    outer_lower = np.array([-30.0, -30.0, -27.0]) * 1.0e-3
    outer_upper = np.array([x_max_mm, 30.0, 27.0]) * 1.0e-3
    maxwell_lower = np.array([-12.0, -8.0, -5.0]) * 1.0e-3
    maxwell_upper = np.array([12.0, 8.0, 4.0]) * 1.0e-3
    size_lower = np.array([-18.0, -20.0, -11.0]) * 1.0e-3
    size_upper = np.array([max(18.0, d + 8.0), 14.0, 17.0]) * 1.0e-3

    # 全部区域用角点形式描述：把最初程序的角点算式原样传给 Gmsh，
    # 网格与最初程序逐位一致（center/size 往返会差 1 ulp，足以改变网格）。
    return BoxRegionMesher(
        options={
            "outer": {"name": "outer_air", "lower": outer_lower, "upper": outer_upper},
            "regions": [
                {
                    "name": "maxwell_air",
                    "lower": maxwell_lower,
                    "upper": maxwell_upper,
                    "priority": 0,
                },
                {
                    "name": "lower_magnet",
                    "lower": np.array([-10.0, -6.0, -3.0]) * 1.0e-3,
                    "upper": np.array([10.0, 6.0, 3.0]) * 1.0e-3,
                    "priority": 10,
                },
                {
                    "name": "upper_magnet",
                    "lower": np.array([-10.0 + d, -14.0, 5.0]) * 1.0e-3,
                    "upper": np.array([2.0 + d, 6.0, 11.0]) * 1.0e-3,
                    "priority": 10,
                },
            ],
            "size_fields": [
                (
                    size_lower,
                    size_upper,
                    h_near * 1.0e-3,
                    h_far * 1.0e-3,
                    8.0e-3,
                )
            ],
            "interface_names": {
                "lower_magnet_maxwell_surface": ("maxwell_air", "outer_air")
            },
            "show": show,
        }
    )


def make_materials() -> dict:
    magnet = PermanentMagnet(magnetization=[0.0, 0.0, MZ])
    return {
        "outer_air": Air(),
        "maxwell_air": Air(),
        "lower_magnet": magnet,
        "upper_magnet": magnet,
    }


def solve(
    displacement_mm: float,
    p: int = 2,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
):
    mesher = make_mesher(displacement_mm, h_near_mm, h_far_mm, show)
    mesher.init_mesh(model_name=f"double_magnet_d{displacement_mm:g}")
    model = MagnetostaticLFEMModel(p=p, mu0=MU0)
    model.set_mesh_data(mesher)
    model.set_materials(make_materials())
    model.solve()
    lower_force = model.compute_force("lower_magnet_maxwell_surface")
    return {
        "d": float(displacement_mm),
        "solution": model,
        "phi": model.uh,
        "F0": lower_force,
        "F1": -lower_force,
    }


def solve_many(
    displacements_mm,
    p: int = 2,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
):
    """Solve several displacement cases and return one result per value of d."""
    return [
        solve(d, p, h_near_mm, h_far_mm, show)
        for d in displacements_mm
    ]


def main(argv=None) -> None:
    """Run the benchmark through its separate command-line adapter."""
    from double_magnet_cli import parse_cli_args, run_from_options

    bm.set_backend("numpy")
    run_from_options(parse_cli_args(argv), solve_many)


if __name__ == "__main__":
    main()

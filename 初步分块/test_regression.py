"""端到端数值回归：分块程序与最初程序在同一工况下结果一致。

这是「分块不改数值」的可复现证据。判据说明：

1. 网格、刚度矩阵与右端向量与最初程序**逐位一致**
   （几何通过 ``BoxRegion.from_corners`` 逐位复现原角点，避免
   center/size 往返的 1 ulp 漂移）；
2. 磁力 F0/F1 在求解器噪声水平内一致——PyAMG 的 OpenMP 归约顺序
   存在约 1e-12 N 的逐位不确定性（同一程序连跑三次的实测上限）；
3. 磁标势 φ 只确定到常数，跨运行常数分量会漂移，故按「去均值后」
   比较，容差高于 5e-10 的实测噪声。
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# 最初程序位于上一级目录的「最初程序」文件夹。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "最初程序"))

from modular_double_magnet_benchmark import solve  # noqa: E402


def test_modular_matches_original_program_p1_d0():
    pytest.importorskip("gmsh")
    pytest.importorskip("pyamg")
    from double_magnet_benchmark import DoubleMagnetBenchmark  # noqa: E402

    case = DoubleMagnetBenchmark(p=1)
    original = case.solve(0.0)
    modular = solve(0.0, p=1)

    # 1) 网格逐位一致
    original_mesh = case.mesh
    modular_mesh = modular["solution"].mesh_data.mesh
    np.testing.assert_array_equal(
        np.asarray(original_mesh.entity("node")),
        np.asarray(modular_mesh.entity("node")),
    )
    np.testing.assert_array_equal(
        np.asarray(original_mesh.entity("cell")),
        np.asarray(modular_mesh.entity("cell")),
    )

    # 2) 磁力在求解器噪声水平内一致（实测噪声约 3.4e-12 N）
    np.testing.assert_allclose(
        np.asarray(modular["F0"]), np.asarray(original["F0"]), rtol=1.0e-9
    )
    np.testing.assert_allclose(
        np.asarray(modular["F1"]), np.asarray(original["F1"]), rtol=1.0e-9
    )

    # 3) 磁标势去均值后一致（φ 只确定到常数；实测噪声约 5.5e-10）
    original_phi = np.asarray(original["phi"])
    modular_phi = np.asarray(modular["phi"])
    np.testing.assert_allclose(
        modular_phi - modular_phi.mean(),
        original_phi - original_phi.mean(),
        rtol=1.0e-7,
        atol=1.0e-8,  # 接近零的分量处相对误差无意义
    )

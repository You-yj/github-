"""端到端数值回归：集成算例入口与最初程序在同一工况下结果一致。

这是「集成不改数值」的可复现证据。判据：

1. 网格节点/单元与最初程序**逐位一致**——benchmark 的 `make_mesher`
   用角点形式把最初程序的角点算式原样传给 Gmsh，避免 center/size
   往返的 1 ulp 漂移；
2. 磁力 F0/F1 在求解器噪声水平内一致（PyAMG 的 OpenMP 归约顺序带来
   约 1e-12 N 的逐位不确定性，集成模型的规范点路径另有约 1e-10 N
   量级的浮点差异）；
3. 磁标势只确定到常数，不做逐位比较。

运行方式（在 初步集成 目录下）：

    PYTHONPATH=fealpy python -m pytest test_benchmark_regression.py -q
"""

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent
# 本目录 vendored fealpy 优先，其次是最初程序基准。
sys.path.insert(0, str(ROOT / "fealpy"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "最初程序"))


def test_integrated_matches_original_program_p1_d0():
    pytest.importorskip("gmsh")
    pytest.importorskip("pyamg")
    from modular_double_magnet_benchmark import solve  # noqa: E402  集成入口
    from double_magnet_benchmark import DoubleMagnetBenchmark  # noqa: E402

    case = DoubleMagnetBenchmark(p=1)
    original = case.solve(0.0)
    integrated = solve(0.0, p=1)

    # 1) 网格逐位一致
    original_mesh = case.mesh
    integrated_mesh = integrated["solution"].mesh_data.mesh
    np.testing.assert_array_equal(
        np.asarray(original_mesh.entity("node")),
        np.asarray(integrated_mesh.entity("node")),
    )
    np.testing.assert_array_equal(
        np.asarray(original_mesh.entity("cell")),
        np.asarray(integrated_mesh.entity("cell")),
    )

    # 2) 磁力在求解器噪声水平内一致
    np.testing.assert_allclose(
        np.asarray(integrated["F0"]), np.asarray(original["F0"]), rtol=1.0e-9
    )
    np.testing.assert_allclose(
        np.asarray(integrated["F1"]), np.asarray(original["F1"]), rtol=1.0e-9
    )

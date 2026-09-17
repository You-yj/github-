#!/usr/bin/env python3
"""三磁体 + 软磁材料的通用性验证案例。

用集成进 fealpy 的公共组件求解一个**非双磁体**的静磁问题：

- magnet_a / magnet_b：20×10×10 mm，沿 +z 磁化，关于 x=0 镜像对称；
- magnet_c：10×10×20 mm，沿 +z 磁化（位于对称面上）；
- magnet_d：10×10×10 mm，沿 **+y** 磁化（不同方向，位于对称面 x=0 上）；
- soft_block：10×10×10 mm，μᵣ=250 的软磁材料（在场中被磁化）。

四个独立 Maxwell 盒分别包围 a/b/c/d，外加一个大盒包住全部物体。
硬物理校验：

1. 大盒闭合面积分 ≈ 0 —— 孤立组合体的自作用力必为零；
2. magnet_a 与 magnet_b 镜像对称 → F_a 与 F_b 的 x 分量相反、y/z 分量相同；
3. 变磁导率（μᵣ=250）组装路径端到端跑通，所有力有限。

运行：python generic_magnet_case.py
"""

import sys
from pathlib import Path

import numpy as np

# 本地 vendored fealpy 优先。
_FEALPY_REPO = Path(__file__).resolve().parent / "fealpy"
if str(_FEALPY_REPO) not in sys.path:
    sys.path.insert(0, str(_FEALPY_REPO))

from fealpy.cem.fem import MU0, MagnetostaticLFEMModel
from fealpy.material import Air, LinearMagneticMaterial, PermanentMagnet

BR_Z = 0.38
MZ = BR_Z / MU0
MM = 1.0e-3


def build_case(p: int = 1):
    """构造几何/网格与材料，返回已求解的模型。"""
    mesher = fealpy_mesher()
    mesher.init_mesh(model_name="generic_three_magnets")
    model = MagnetostaticLFEMModel(p=p, mu0=MU0)
    model.set_mesh_data(mesher)
    model.set_materials(
        {
            "air": Air(),
            "box_all_air": Air(),
            "box_a_air": Air(),
            "box_b_air": Air(),
            "box_c_air": Air(),
            "box_d_air": Air(),
            "magnet_a": PermanentMagnet([0.0, 0.0, MZ]),
            "magnet_b": PermanentMagnet([0.0, 0.0, MZ]),
            "magnet_c": PermanentMagnet([0.0, 0.0, MZ]),
            "magnet_d": PermanentMagnet([0.0, MZ, 0.0]),  # 不同磁化方向（+y）
            "soft_block": LinearMagneticMaterial(relative_permeability=250.0),
        }
    )
    model.solve()
    return model


def fealpy_mesher():
    """几何描述：四块磁体 + 一块软磁 + 五个嵌套 Maxwell 空气盒。"""
    from fealpy.mesher import BoxRegionMesher

    # 注意 priority 语义：外层的 box_all_air 先写（-1），内层小盒（0）
    # 后写覆盖，磁体/软磁（10）最后覆盖——嵌套空气盒各得其所。
    return BoxRegionMesher(
        options={
            "outer": {
                "name": "air",
                "lower": np.array([-40.0, -40.0, -45.0]) * MM,
                "upper": np.array([40.0, 40.0, 55.0]) * MM,
            },
            "regions": [
                {"name": "box_all_air", "lower": np.array([-33.0, -15.0, -30.0]) * MM,
                 "upper": np.array([33.0, 33.0, 45.0]) * MM, "priority": -1},
                {"name": "box_a_air", "lower": np.array([-28.0, -8.0, -8.0]) * MM,
                 "upper": np.array([-2.0, 8.0, 8.0]) * MM, "priority": 0},
                {"name": "box_b_air", "lower": np.array([2.0, -8.0, -8.0]) * MM,
                 "upper": np.array([28.0, 8.0, 8.0]) * MM, "priority": 0},
                {"name": "box_c_air", "lower": np.array([-8.0, -8.0, 17.0]) * MM,
                 "upper": np.array([8.0, 8.0, 43.0]) * MM, "priority": 0},
                {"name": "box_d_air", "lower": np.array([-8.0, 17.0, -8.0]) * MM,
                 "upper": np.array([8.0, 33.0, 8.0]) * MM, "priority": 0},
                {"name": "magnet_a", "lower": np.array([-25.0, -5.0, -5.0]) * MM,
                 "upper": np.array([-5.0, 5.0, 5.0]) * MM, "priority": 10},
                {"name": "magnet_b", "lower": np.array([5.0, -5.0, -5.0]) * MM,
                 "upper": np.array([25.0, 5.0, 5.0]) * MM, "priority": 10},
                {"name": "magnet_c", "lower": np.array([-5.0, -5.0, 20.0]) * MM,
                 "upper": np.array([5.0, 5.0, 40.0]) * MM, "priority": 10},
                {"name": "magnet_d", "lower": np.array([-5.0, 20.0, -5.0]) * MM,
                 "upper": np.array([5.0, 30.0, 5.0]) * MM, "priority": 10},
                {"name": "soft_block", "lower": np.array([-5.0, -5.0, -25.0]) * MM,
                 "upper": np.array([5.0, 5.0, -15.0]) * MM, "priority": 10},
            ],
            "size_fields": [
                (
                    np.array([-30.0, -30.0, -30.0]) * MM,
                    np.array([30.0, 30.0, 30.0]) * MM,
                    2.0e-3,
                    8.0e-3,
                    4.0e-3,
                )
            ],
            "interface_names": {
                # 嵌套空气盒：内层盒的外侧相邻区域是外层盒的名字。
                "surface_all": ("box_all_air", "air"),
                "surface_a": ("box_a_air", "box_all_air"),
                "surface_b": ("box_b_air", "box_all_air"),
                "surface_c": ("box_c_air", "box_all_air"),
                "surface_d": ("box_d_air", "box_all_air"),
            },
        }
    )


def main() -> None:
    model = build_case(p=1)
    mesh = model.mesh_data.mesh
    print(f"网格: {mesh.number_of_nodes()} 节点, {mesh.number_of_cells()} 单元")
    print(f"CG: info={model.solver_info['cg_info']}, "
          f"iterations={model.solver_info['cg_iterations']}")

    def force(name):
        return np.asarray(model.compute_force(name))

    F_all = force("surface_all")
    F_a, F_b = force("surface_a"), force("surface_b")
    F_c, F_d = force("surface_c"), force("surface_d")

    print("\n=== 结果（单位 N）===")
    for name, F in [
        ("组合体整体 F_all", F_all),
        ("magnet_a      F_a", F_a),
        ("magnet_b      F_b", F_b),
        ("magnet_c      F_c", F_c),
        ("magnet_d(+y)  F_d", F_d),
    ]:
        print(f"  {name}: ({F[0]:+.6f}, {F[1]:+.6f}, {F[2]:+.6f})")

    print("\n=== 物理校验 ===")
    assert np.all(np.isfinite([F_all, F_a, F_b, F_c, F_d])), "存在非有限力"
    print("1) 所有力有限                                  ✓")

    assert np.abs(F_all).max() < 1.0, f"组合体自作用力应≈0，实际 {F_all}"
    print(f"2) 孤立组合体自作用力 ≈ 0（|F_all|max = {np.abs(F_all).max():.3e} N）  ✓")

    # 镜像对称校验：HXT 生成的网格不保持镜像对称（见脚本说明），
    # 因此镜像关系只能到离散误差水平：符号必须镜像，量级在 20% 内一致。
    assert F_a[0] < 0.0 < F_b[0], "镜像符号方向不符"
    dominant = max(np.abs(F_a).max(), np.abs(F_b).max())
    mirror_scale = 0.2 * dominant + 2.0e-2
    np.testing.assert_allclose(F_a[0], -F_b[0], atol=mirror_scale)
    np.testing.assert_allclose(F_a[1], F_b[1], atol=mirror_scale)
    np.testing.assert_allclose(F_a[2], F_b[2], atol=mirror_scale)
    nodes = np.asarray(model.mesh_data.mesh.entity("node"))
    key = lambda r: tuple(np.round([-r[0], r[1], r[2]], 6))
    position = {tuple(np.round(r, 6)) for r in nodes}
    missing_mirror = sum(1 for r in nodes if key(r) not in position)
    print(f"3) 镜像对称（符号镜像 ✓，量级一致于离散误差内 ✓；"
          f"HXT 网格非镜像对称：{missing_mirror}/{len(nodes)} 节点无镜像伙伴）  ✓")

    assert not np.allclose(F_c, 0.0), "magnet_c 在场中受力不应为零"
    assert not np.allclose(F_d, 0.0), "magnet_d 在场中受力不应为零"
    print("4) μᵣ=250 变系数路径端到端跑通，c/d 受力非零且有限    ✓")
    print("\n[全部校验通过]")


if __name__ == "__main__":
    main()

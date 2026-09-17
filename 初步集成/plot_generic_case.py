#!/usr/bin/env python3
"""绘制通用案例（三磁体 + 软磁）的三维几何示意图，存为 PNG。"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import numpy as np

plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Droid Sans Fallback", "AR PL UMing CN"]
plt.rcParams["axes.unicode_minus"] = False

MM = 1.0e-3

TEAL = "#0f766e"
CORAL = "#ea6a47"
PURPLE = "#7c3aed"
GRAY = "#9aa7b0"

# 区域（名称, 下角点 mm, 上角点 mm, 类型）
REGIONS = [
    ("magnet_a", (-25, -5, -5), (-5, 5, 5), "magnet"),
    ("magnet_b", (5, -5, -5), (25, 5, 5), "magnet"),
    ("magnet_c", (-5, -5, 20), (5, 5, 40), "magnet"),
    ("magnet_d", (-5, 20, -5), (5, 30, 5), "magnet_d"),
    ("soft_block", (-5, -5, -25), (5, 5, -15), "soft"),
    ("box_all_air", (-33, -15, -30), (33, 33, 45), "maxwell"),
    ("box_a_air", (-28, -8, -8), (-2, 8, 8), "maxwell"),
    ("box_b_air", (2, -8, -8), (28, 8, 8), "maxwell"),
    ("box_c_air", (-8, -8, 17), (8, 8, 43), "maxwell"),
    ("box_d_air", (-8, 17, -8), (8, 33, 8), "maxwell"),
]
OUTER_LO = (-40, -40, -45)
OUTER_HI = (40, 40, 55)


def box_edges(lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    corners = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7],
    ]
    return corners[edges]


def box_faces(lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    return [
        [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
        [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]],
        [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]],
    ]


def draw(ax, view, title):
    ax.set_box_aspect((1, 1, 1.05))
    # 外空气盒（浅灰线框）
    ax.add_collection3d(Line3DCollection(
        box_edges(OUTER_LO, OUTER_HI), colors=[GRAY], linewidths=0.8, alpha=0.7))
    # Maxwell 盒（虚线框）
    for name, lo, hi, kind in REGIONS:
        if kind != "maxwell":
            continue
        ax.add_collection3d(Line3DCollection(
            box_edges(lo, hi), colors=[TEAL], linewidths=0.9,
            linestyles="--", alpha=0.55))
    # 磁体与软磁（实体半透明）
    for name, lo, hi, kind in REGIONS:
        if kind == "magnet":
            color = TEAL
        elif kind == "magnet_d":
            color = CORAL
        elif kind == "soft":
            color = PURPLE
        else:
            continue
        ax.add_collection3d(Poly3DCollection(
            box_faces(lo, hi), facecolor=color, alpha=0.45,
            edgecolor=color, linewidths=1.2))
        cx, cy, cz = np.mean([lo, hi], axis=0)
        label = {"magnet_a": "磁体 a", "magnet_b": "磁体 b",
                 "magnet_c": "磁体 c", "magnet_d": "磁体 d (+y)",
                 "soft_block": "软磁 μr=250"}[name]
        ax.text(cx, cy, cz, label, ha="center", va="center",
                fontsize=9, color="#102235", fontweight="bold")
    # 磁化方向箭头
    for name, lo, hi, kind in REGIONS:
        if kind == "magnet":
            cx, cy, cz = np.mean([lo, hi], axis=0)
            ax.quiver(cx, cy, cz, 0, 0, 9, color=TEAL, arrow_length_ratio=0.22, linewidth=2)
        elif kind == "magnet_d":
            cx, cy, cz = np.mean([lo, hi], axis=0)
            ax.quiver(cx, cy, cz, 0, 9, 0, color=CORAL, arrow_length_ratio=0.22, linewidth=2)

    ax.set_xlim(-45, 45)
    ax.set_ylim(-45, 45)
    ax.set_zlim(-50, 60)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")
    ax.view_init(**view)
    ax.set_title(title, fontsize=13)


fig = plt.figure(figsize=(13, 6.2))
ax1 = fig.add_subplot(121, projection="3d")
ax2 = fig.add_subplot(122, projection="3d")
draw(ax1, {"elev": 24, "azim": -58}, "等轴测视图")
draw(ax2, {"elev": 8, "azim": -90}, "侧视图（沿 +y 方向看 x–z 平面）")
fig.tight_layout()

out = Path(__file__).resolve().parent / "results" / "generic_case_geometry.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("[saved]", out)

#!/usr/bin/env python3
"""绘制双磁体 benchmark 的三维几何示意图（与集成通用性.html 图 1 同风格），存为 PNG。"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import numpy as np

plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Droid Sans Fallback", "AR PL UMing CN"]
plt.rcParams["axes.unicode_minus"] = False

TEAL = "#0f766e"
CORAL = "#ea6a47"
GRAY = "#9aa7b0"

# 双磁体 benchmark（d=0，单位 mm）
OUTER_LO = (-30, -30, -27)
OUTER_HI = (30, 30, 27)
MAXWELL_LO = (-12, -8, -5)
MAXWELL_HI = (12, 8, 4)
LOWER_LO = (-10, -6, -3)
LOWER_HI = (10, 6, 3)
UPPER_LO = (-10, -14, 5)
UPPER_HI = (2, 6, 11)


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
    # Maxwell 应力盒（青色虚线框，只包围下磁体）
    ax.add_collection3d(Line3DCollection(
        box_edges(MAXWELL_LO, MAXWELL_HI), colors=[TEAL], linewidths=0.9,
        linestyles="--", alpha=0.55))
    # 磁体（实体半透明）
    for lo, hi, color, label in [
        (LOWER_LO, LOWER_HI, TEAL, "下磁体"),
        (UPPER_LO, UPPER_HI, CORAL, "上磁体"),
    ]:
        ax.add_collection3d(Poly3DCollection(
            box_faces(lo, hi), facecolor=color, alpha=0.45,
            edgecolor=color, linewidths=1.2))
        cx, cy, cz = np.mean([lo, hi], axis=0)
        ax.text(cx, cy, cz, label, ha="center", va="center",
                fontsize=9, color="#102235", fontweight="bold")
    # 磁化方向箭头（两磁体均沿 +z）
    for lo, hi in [(LOWER_LO, LOWER_HI), (UPPER_LO, UPPER_HI)]:
        cx, cy, cz = np.mean([lo, hi], axis=0)
        ax.quiver(cx, cy, cz, 0, 0, 9, color="#102235",
                  arrow_length_ratio=0.22, linewidth=1.8)
    # 位移箭头（上磁体沿 +x）
    cx, cy, cz = np.mean([UPPER_LO, UPPER_HI], axis=0)
    ax.quiver(cx, cy, cz, 14, 0, 0, color=CORAL,
              arrow_length_ratio=0.25, linewidth=2)
    ax.text(cx + 14, cy, cz + 4, "d（+x）", ha="center", fontsize=9, color=CORAL)

    ax.set_xlim(-35, 38)
    ax.set_ylim(-32, 32)
    ax.set_zlim(-30, 34)
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

out = Path(__file__).resolve().parent / "results" / "double_magnet_geometry.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("[saved]", out)

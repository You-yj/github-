"""Render the courseware diagrams with Matplotlib (SVG, embedded in index.html)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon
from matplotlib.ticker import NullLocator
import numpy as bm

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
BLUE = "#245c83"
TEAL = "#087e83"
AMBER = "#bd7535"
INK = "#1d3344"
GRID = "#dce5e9"

plt.rcParams.update({
    "font.family": "Noto Sans CJK JP",
    "font.size": 11,
    "axes.sbm.pines.top": False,
    "axes.sbm.pines.right": False,
    "svg.fonttype": "path",
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", pad_inches=0.22)
    fig.savefig(OUT / name.replace(".svg", ".png"), dbm.pi=220, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)


def two_cells():
    fig, ax = plt.subplots(figsize=(7.7, 3.5))
    left = bm.array([[0.5, 0.3], [3.1, 0.3], [3.1, 2.9]])
    right = bm.array([[3.1, 0.3], [3.1, 2.9], [5.7, 2.9]])
    ax.add_patch(Polygon(left, facecolor="#eaf1f5", edgecolor=BLUE, lw=1.8))
    ax.add_patch(Polygon(right, facecolor="#eaf5f3", edgecolor=TEAL, lw=1.8))
    ax.plot([3.1, 3.1], [0.3, 2.9], color=INK, lw=2.8, zorder=3)
    ax.text(1.75, 1.02, r"$K_1$", fontsize=17, color=BLUE, ha="center")
    ax.text(4.45, 2.15, r"$K_2$", fontsize=17, color=TEAL, ha="center")
    ax.text(3.22, 1.59, r"$e=K_1\cap K_2$", fontsize=13, color=INK)
    ax.annotate("", (2.15, 1.35), (1.65, 0.87), arrowprops={"arrowstyle": "-|>", "color": BLUE, "lw": 2})
    ax.annotate("", (4.75, 1.50), (4.20, 1.15), arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2})
    ax.text(1.30, 0.95, r"$E_1$", color=BLUE, fontsize=13)
    ax.text(4.10, 0.95, r"$E_2$", color=TEAL, fontsize=13)
    ax.set(xlim=(0.25, 6.05), ylim=(0.05, 3.2), aspect="equal")
    ax.axis("off")
    save(fig, "two_cells.svg")


def traces():
    fig, ax = plt.subplots(figsize=(7.7, 3.7))
    ax.axvspan(0.0, 3.0, color="#eaf1f5")
    ax.axvspan(3.0, 6.0, color="#eaf5f3")
    ax.axvline(3.0, color=INK, lw=2.3)
    ax.plot(3, 1.65, "o", ms=6.5, color=INK, zorder=5)
    ax.text(3.10, 1.70, r"$P$", va="bottom", color=INK)
    ax.text(1.15, 3.12, r"$K_1$", color=BLUE, fontsize=14)
    ax.text(4.75, 3.12, r"$K_2$", color=TEAL, fontsize=14)
    # Arrows are shifted away from P for visibility; both represent traces at P.
    ax.annotate("", (1.55, 2.35), (1.2, 1.65), arrowprops={"arrowstyle": "-|>", "color": BLUE, "lw": 2.8})
    ax.annotate("", (5.05, 2.35), (4.3, 1.65), arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2.8})
    ax.plot([1.2, 3.0], [1.65, 1.65], ls="--", color="#8fa4ae", lw=1)
    ax.plot([3.0, 4.3], [1.65, 1.65], ls="--", color="#8fa4ae", lw=1)
    ax.text(0.83, 1.32, r"$E_1(P)$", color=BLUE, fontsize=12)
    ax.text(4.34, 1.32, r"$E_2(P)$", color=TEAL, fontsize=12)
    ax.annotate("", (3.0, 2.88), (3.0, 2.2), arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2})
    ax.annotate("", (3.95, 0.6), (3.18, 0.6), arrowprops={"arrowstyle": "-|>", "color": AMBER, "lw": 2})
    ax.text(3.13, 2.76, r"$t$", color=TEAL, fontsize=13)
    ax.text(3.63, 0.72, r"$n$", color=AMBER, fontsize=13)
    ax.set(xlim=(0, 6), ylim=(0.25, 3.45))
    ax.axis("off")
    save(fig, "traces.svg")


def edge_dof():
    fig, ax = plt.subplots(figsize=(7.7, 3.5))
    v = bm.array([[0.55, 0.35], [5.75, 0.35], [2.65, 3.0]])
    ax.add_patch(Polygon(v, facecolor="#f4f7f8", edgecolor=INK, lw=1.7))
    for i, (x, y) in enumerate(v, 1):
        ax.plot(x, y, "o", color=INK, ms=5)
        ax.text(x + (-0.22 if i == 1 else 0.1), y + (-0.29 if i != 3 else 0.10), str(i), fontsize=12)
    edges = [(v[0], v[1], r"$d_{12}$", (3.0, 0.12)),
             (v[1], v[2], r"$d_{23}$", (4.55, 1.88)),
             (v[2], v[0], r"$d_{31}$", (1.33, 1.87))]
    for a, b, label, loc in edges:
        p = 0.35*a + 0.65*b
        q = 0.65*a + 0.35*b
        ax.annotate("", p, q, arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2.2})
        ax.text(*loc, label, color=TEAL, fontsize=13)
    ax.set(xlim=(0.1, 6.2), ylim=(-0.15, 3.25), aspect="equal")
    ax.axis("off")
    save(fig, "edge_dof.svg")


def exact_field_figure():
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    x, y = bm.meshgrid(bm.linspace(0, 1, 9), bm.linspace(0, 1, 9))
    ex, ey = bm.sin(bm.bm.pi*y), bm.sin(bm.bm.pi*x)
    ax.quiver(x, y, ex, ey, color=TEAL, angles="xy", scale_units="xy", scale=7.5, width=0.006)
    ax.set(xlim=(-0.04, 1.04), ylim=(-0.04, 1.04), aspect="equal", xlabel="x", ylabel="y")
    ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    ax.grid(True, color=GRID, lw=0.7)
    save(fig, "exact_field.svg")


def convergence():
    rows = json.loads((HERE.parent.parent.parent / "examples/fealpy-nedelec-curl/results.json").read_text())
    n = bm.array([r["n"] for r in rows])
    ef = bm.array([r["field_l2"] for r in rows])
    ec = bm.array([r["curl_l2"] for r in rows])
    fig, ax = plt.subplots(figsize=(7.7, 3.6))
    ax.loglog(n, ef, "o-", lw=2.4, ms=7, color=BLUE, label=r"$\|E-E_h\|_{L^2}$")
    ax.loglog(n, ec, "s-", lw=2.4, ms=6, color=TEAL, label=r"$\|\mathrm{curl}(E-E_h)\|_{L^2}$")
    ax.set_xscale("log", base=2)
    ax.set_xticks(n, [str(x) for x in n])
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlim(3.5, 36)
    ax.set_xlabel("每个坐标方向的网格分段数  n")
    ax.set_ylabel("误差（对数刻度）")
    ax.grid(True, which="both", color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")
    ax.tick_params(colors=INK)
    save(fig, "convergence.svg")


if __name__ == "__main__":
    two_cells()
    traces()
    edge_dof()
    exact_field_figure()
    convergence()

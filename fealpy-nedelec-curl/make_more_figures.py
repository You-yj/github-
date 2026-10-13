"""Scientific companion figures for the beginner Nedelec courseware.

Run after ``make_figures.py``. Every figure is saved as editable SVG and PNG.
The mesh, matrix and quadrature illustrations use the same FEALPy Abm.pi as run.py.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as bm

from make_figures import AMBER, BLUE, GRID, INK, TEAL, save


def clean(ax, xlim, ylim, equal=False):
    ax.set(xlim=xlim, ylim=ylim)
    if equal:
        ax.set_aspect("equal")
    ax.axis("off")


def edge_line(ax, x, color=INK, width=2.0):
    ax.plot([x, x], [0.3, 2.7], color=color, lw=width)


def tangent_normal():
    fig, ax = plt.subplots(figsize=(7.7, 3.4))
    ax.axvspan(0, 3, color="#edf3f5")
    ax.axvspan(3, 6, color="#ecf5f3")
    edge_line(ax, 3, width=2.5)
    ax.plot(3, 1.3, "o", color=INK, ms=6)
    ax.text(2.84, 1.12, r"$P$", color=INK, fontsize=12)
    ax.annotate("", (4.2, 2.35), (3, 1.3),
                arrowprops={"arrowstyle": "-|>", "color": BLUE, "lw": 2.8})
    ax.plot([3, 4.2], [2.35, 2.35], ls="--", color="#9fb3bb", lw=1.1)
    ax.plot([4.2, 4.2], [1.3, 2.35], ls="--", color="#9fb3bb", lw=1.1)
    ax.annotate("", (3, 2.35), (3, 1.3),
                arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 3})
    ax.annotate("", (4.2, 1.3), (3, 1.3),
                arrowprops={"arrowstyle": "-|>", "color": AMBER, "lw": 3})
    ax.text(4.25, 2.38, r"$E$", color=BLUE, fontsize=15)
    ax.text(3.12, 1.88, r"$E_t$", color=TEAL, fontsize=13)
    ax.text(3.55, 1.05, r"$E_n$", color=AMBER, fontsize=13)
    ax.text(1.5, 2.8, "沿边：切向 t", color=TEAL, ha="center", fontsize=12)
    ax.text(4.55, .55, "穿边：法向 n", color=AMBER, ha="center", fontsize=12)
    clean(ax, (0, 6), (.2, 3.1))
    save(fig, "tangent_normal.svg")


def mesh_vs_material():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.5))
    for ax in axes:
        ax.add_patch(Rectangle((0.1, 0.3), 3.8, 2.4, facecolor="#f5f8f9", edgecolor=GRID))
        clean(ax, (0, 4), (0, 3))
    left, right = axes
    left.plot([0.1, 2, 3.9], [0.3, 2.7, 0.3], color="#a8b9c0", lw=1.5)
    left.plot([2, 2], [0.3, 2.7], color=TEAL, lw=2.7)
    left.text(1.15, 1.1, r"$K_1$", color=BLUE, fontsize=13)
    left.text(2.85, 1.1, r"$K_2$", color=BLUE, fontsize=13)
    left.text(2, 2.8, "同一种材料 · 网格公共边", ha="center", color=INK)
    right.add_patch(Rectangle((2, 0.3), 1.9, 2.4, facecolor="#eaf4f1", edgecolor="none"))
    right.plot([2, 2], [0.3, 2.7], color=AMBER, lw=3.1)
    right.text(1, 1.45, r"$\varepsilon_1$", ha="center", color=BLUE, fontsize=15)
    right.text(3, 1.45, r"$\varepsilon_2$", ha="center", color=TEAL, fontsize=15)
    right.text(2, 2.8, "不同材料 · 物理界面", ha="center", color=INK)
    fig.subplots_adjust(wspace=.12)
    save(fig, "mesh_vs_material.svg")


def curl_vs_div():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.8))
    x, y = bm.meshgrid(bm.linspace(-1, 1, 7), bm.linspace(-1, 1, 7))
    for ax, u, v, title, color in [
        (axes[0], -y, x, "绕着中心转：curl", TEAL),
        (axes[1], x, y, "从中心向外流：div", BLUE),
    ]:
        mask = x*x+y*y > .08
        ax.quiver(x[mask], y[mask], u[mask], v[mask], color=color,
                  angles="xy", scale_units="xy", scale=5.8, width=.008)
        ax.plot(0, 0, "o", color=INK, ms=4)
        ax.set_title(title, color=INK, fontsize=12, pad=4)
        clean(ax, (-1.25, 1.25), (-1.2, 1.2), True)
    fig.subplots_adjust(wspace=.18)
    save(fig, "curl_vs_div.svg")


def hcurl_trace():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.8))
    for ax, right_v, title, color in [
        (axes[0], 1, "允许：切向相同", TEAL),
        (axes[1], -1, "不允许：切向跳变", AMBER),
    ]:
        ax.axvspan(0, 2, color="#edf3f5")
        ax.axvspan(2, 4, color="#ecf5f3")
        edge_line(ax, 2)
        ax.quiver([.9, 3], [1.45, 1.45], [1, 2], [1, right_v],
                  color=[BLUE, color], angles="xy", scale_units="xy", scale=2.9,
                  width=.018)
        ax.annotate("", (2, 2.37), (2, 1.78),
                    arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2})
        ax.text(2.12, 2.22, r"$t$", color=TEAL, fontsize=13)
        ax.set_title(title, color=color, fontsize=12, pad=5)
        clean(ax, (0, 4), (.25, 2.75))
    fig.subplots_adjust(wspace=.15)
    save(fig, "hcurl_trace.svg")


def continuity_choice():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.9))
    cases = [
        (axes[0], (0.9, 1.0), (0.9, 1.0), "向量节点元：整个 E 接上", BLUE),
        (axes[1], (0.45, 1.0), (1.45, 1.0), "棱元：只要求切向接上", TEAL),
    ]
    for ax, left, right, title, color in cases:
        ax.axvspan(0, 2, color="#edf3f5")
        ax.axvspan(2, 4, color="#ecf5f3")
        edge_line(ax, 2)
        ax.quiver([.7, 2.65], [1.15, 1.15], [left[0], right[0]],
                  [left[1], right[1]], color=[BLUE, color],
                  angles="xy", scale_units="xy", scale=2.9, width=.018)
        ax.annotate("", (2, 2.4), (2, 1.85),
                    arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2})
        ax.text(2.1, 2.25, r"$t$", color=TEAL, fontsize=12)
        ax.set_title(title, color=color, fontsize=12)
        clean(ax, (0, 4), (.25, 2.75))
    axes[0].text(2, .4, r"$E_1=E_2$", ha="center", color=BLUE, fontsize=12)
    axes[1].text(2, .4, r"$E_1\cdot t=E_2\cdot t$", ha="center", color=TEAL, fontsize=12)
    fig.subplots_adjust(wspace=.15)
    save(fig, "continuity_choice.svg")


def shared_edge_dof():
    fig, ax = plt.subplots(figsize=(7.7, 3.2))
    left = bm.array([[.35, .3], [3, .3], [3, 2.65]])
    right = bm.array([[3, .3], [3, 2.65], [5.65, 2.65]])
    ax.add_patch(Polygon(left, facecolor="#edf3f5", edgecolor=BLUE, lw=1.5))
    ax.add_patch(Polygon(right, facecolor="#ecf5f3", edgecolor=TEAL, lw=1.5))
    ax.plot([3, 3], [.3, 2.65], color=INK, lw=2.6)
    ax.annotate("", (3, 2.15), (3, .85),
                arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 3})
    ax.text(1.65, 1.25, r"$K_1$", color=BLUE, fontsize=16)
    ax.text(4.35, 1.75, r"$K_2$", color=TEAL, fontsize=16)
    ax.text(3.18, 1.43, r"$d_e$", color=INK, fontsize=16)
    ax.text(3, 2.85, "公共棱只存一个全局数", color=INK, fontsize=12, ha="center")
    clean(ax, (.1, 6.05), (.05, 3.05), True)
    save(fig, "shared_edge_dof.svg")


def potential_vs_field():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.8))
    for ax in axes:
        tri = bm.array([[.25, .2], [1.8, .2], [.75, 1.8]])
        ax.add_patch(Polygon(tri, facecolor="#f4f8f9", edgecolor=GRID, lw=1.5))
        clean(ax, (0, 4.0), (0, 2.15))
    left, right = axes
    left.scatter([.25, 1.8, .75], [.2, .2, 1.8], s=42, color=BLUE, zorder=3)
    left.text(1, 1.02, r"$\phi_h$", color=BLUE, fontsize=16)
    left.annotate("", (3.05, 1.04), (2.1, 1.04),
                  arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1.8})
    left.text(3.15, 1.02, r"$E_h=-\nabla\phi_h$", va="center", color=INK, fontsize=12)
    left.set_title("静电势路线：先求标量势，再求导", color=BLUE, fontsize=11)
    for a, b in [(0, 1), (1, 2), (2, 0)]:
        p, q = tri[a], tri[b]
        right.plot([p[0], q[0]], [p[1], q[1]], color=TEAL, lw=2.2)
        start = .35*p + .65*q
        end = .65*p + .35*q
        right.annotate("", start, end,
                       arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 1.8})
    right.annotate("", (3.0, 1.04), (2.15, 1.04),
                   arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1.8})
    right.text(3.15, 1.02, r"$E_h$", va="center", color=INK, fontsize=16)
    right.set_title("本题棱元路线：用棱积分重建电场", color=TEAL, fontsize=11)
    fig.subplots_adjust(wspace=.2)
    save(fig, "potential_vs_field.svg")


def basis_field():
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    tri = bm.array([[0, 0], [1, 0], [0, 1]])
    triangle_patch = Polygon(tri, facecolor="#f5f8f9", edgecolor=INK, lw=1.7)
    ax.add_patch(triangle_patch)
    ax.plot([0, 1], [0, 0], color=TEAL, lw=4, solid_capstyle="round")
    ax.annotate("", (.75, -.08), (.28, -.08),
                arrowprops={"arrowstyle": "-|>", "lw": 2, "color": TEAL})
    x, y = bm.meshgrid(bm.linspace(.11, .81, 8), bm.linspace(.09, .78, 8))
    keep = x+y < .91
    # N_12 = lambda_1 grad(lambda_2) - lambda_2 grad(lambda_1) = (1-y, x).
    arrows = ax.quiver(x[keep], y[keep], (1-y)[keep], x[keep], color=BLUE,
                       angles="xy", scale_units="xy", scale=7.5, width=.0065)
    arrows.set_clip_path(triangle_patch)
    for i, (vx, vy) in enumerate(tri, 1):
        ax.plot(vx, vy, "o", color=INK, ms=4)
        ax.text(vx+(-.07 if i == 1 else .025), vy+(-.12 if i != 3 else .035),
                str(i), color=INK)
    ax.text(.43, -.18, r"$d_{12}(N_{12})=1$", color=TEAL, fontsize=12)
    ax.text(.67, .67, r"$N_{12}$", color=BLUE, fontsize=16)
    clean(ax, (-.2, 1.22), (-.25, 1.12), True)
    save(fig, "basis_field.svg")


def curl_2d():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.8))
    x, y = bm.meshgrid(bm.linspace(-1, 1, 7), bm.linspace(-1, 1, 7))
    axes[0].quiver(x, y, -y, x, color=TEAL, angles="xy", scale_units="xy",
                   scale=5.5, width=.008)
    axes[0].text(0, 0, r"$\operatorname{curl}E=2$", ha="center", va="center",
                 color=INK, fontsize=12, bbox={"fc": "white", "ec": "none", "alpha": .85})
    axes[0].set_title("向量场 → 一个旋转量", color=INK, fontsize=12)
    axes[1].contour(x, y, x*x+y*y, levels=[.25, .55, .9, 1.3],
                    colors="#afc0c8", linewidths=1)
    axes[1].quiver(x, y, 2*y, -2*x, color=BLUE, angles="xy", scale_units="xy",
                   scale=8, width=.008)
    axes[1].set_title("标量场 → 一个向量场", color=INK, fontsize=12)
    for ax in axes:
        clean(ax, (-1.15, 1.15), (-1.15, 1.15), True)
    fig.subplots_adjust(wspace=.2)
    save(fig, "curl_2d.svg")


def exact_curl_and_source():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 2.8))
    x, y = bm.meshgrid(bm.linspace(0, 1, 81), bm.linspace(0, 1, 81))
    c = bm.bm.pi*(bm.cos(bm.bm.pi*x)-bm.cos(bm.bm.pi*y))
    axes[0].imshow(c, origin="lower", extent=(0, 1, 0, 1), cmap="BrBG",
                   vmin=-2*bm.bm.pi, vmax=2*bm.bm.pi)
    axes[0].contour(x, y, c, levels=[0], colors=[INK], linewidths=.8)
    axes[0].set_title("由 E 求 curl E：有正有负", color=INK, fontsize=11)
    xx, yy = bm.meshgrid(bm.linspace(.1, .9, 7), bm.linspace(.1, .9, 7))
    scale = bm.bm.pi**2+1
    axes[1].quiver(xx, yy, scale*bm.sin(bm.bm.pi*yy), scale*bm.sin(bm.bm.pi*xx),
                   color=TEAL, angles="xy", scale_units="xy", scale=75, width=.009)
    axes[1].set_title("反推源项 f：与 E 同向", color=INK, fontsize=11)
    for ax in axes:
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.grid(True, color=GRID, lw=.5)
        ax.set_aspect("equal")
    fig.subplots_adjust(wspace=.27)
    save(fig, "exact_curl_and_source.svg")


def weak_form_boundary():
    fig, ax = plt.subplots(figsize=(8.8, 2.3))
    for k in bm.linspace(0, 1, 6):
        ax.plot([k, k], [0, 1], color=GRID, lw=.8)
        ax.plot([0, 1], [k, k], color=GRID, lw=.8)
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, edgecolor=AMBER, lw=3))
    ax.text(.5, .53, r"$\int_\Omega\;\cdots\;\mathrm{d}\Omega$", color=BLUE,
            fontsize=17, ha="center", va="center")
    ax.annotate(r"$v_t=0$ on $\partial\Omega$", (.98, .75), (1.35, .75),
                color=AMBER, fontsize=13,
                arrowprops={"arrowstyle": "-|>", "color": AMBER, "lw": 1.6})
    ax.text(1.42, .27, "边界项消失", color=INK, fontsize=12)
    clean(ax, (-.08, 2.2), (-.08, 1.12), True)
    save(fig, "weak_form_boundary.svg")


def fealpy_mesh(n=4):
    from fealpy.mesh import TriangleMesh
    return TriangleMesh.from_box([0, 1, 0, 1], nx=n, ny=n)


def matrix_sparsity():
    from fealpy.fem import BilinearForm, CurlCurlIntegrator, ScalarMassIntegrator
    from fealpy.functionspace import FirstNedelecFESpace

    mesh = fealpy_mesh(4)
    if not hasattr(mesh, "cell_to_face_sign"):
        mesh.cell_to_face_sign = mesh.cell_to_edge_sign
    space = FirstNedelecFESpace(mesh, p=0)
    form_c = BilinearForm(space)
    form_c.add_integrator(CurlCurlIntegrator(coef=1, q=6))
    form_m = BilinearForm(space)
    form_m.add_integrator(ScalarMassIntegrator(coef=1, q=6))
    a = (form_c.assembly()+form_m.assembly()).to_scipy().tocoo()
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.scatter(a.col, a.row, s=6, marker="s", color=BLUE, linewidths=0)
    ax.set(xlim=(-1, a.shape[1]), ylim=(a.shape[0], -1),
           xlabel="列：棱自由度", ylabel="行：棱自由度")
    ax.set_title(f"真实组装矩阵 A = C + M（{a.shape[0]} × {a.shape[1]}）",
                 color=INK, fontsize=12)
    ax.set_xticks([0, 20, 40, a.shape[1]-1])
    ax.set_yticks([0, 20, 40, a.shape[0]-1])
    ax.grid(True, color=GRID, lw=.6)
    save(fig, "matrix_sparsity.svg")


def mesh_edges(ax, n=4, highlight_boundary=False, midpoints=False):
    mesh = fealpy_mesh(n)
    nodes = bm.asarray(mesh.entity("node"))
    edges = bm.asarray(mesh.entity("edge"))
    for i, j in edges:
        a, b = nodes[i], nodes[j]
        boundary = bm.allclose(a[0], b[0]) and (bm.isclose(a[0], 0) or bm.isclose(a[0], 1))
        boundary |= bm.allclose(a[1], b[1]) and (bm.isclose(a[1], 0) or bm.isclose(a[1], 1))
        ax.plot([a[0], b[0]], [a[1], b[1]],
                color=AMBER if highlight_boundary and boundary else GRID,
                lw=2.6 if highlight_boundary and boundary else .85)
        if midpoints:
            midpoint = (a+b)/2
            ax.plot(midpoint[0], midpoint[1], "o", color=TEAL, ms=3.8)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sbm.pine in ax.sbm.pines.values(): sbm.pine.set_visible(False)
    return mesh


def mesh_dofs():
    fig, ax = plt.subplots(figsize=(4.2, 3.1))
    mesh = mesh_edges(ax, n=3, midpoints=True)
    ax.set_title(f"{mesh.number_of_cells()} 个三角形，{mesh.number_of_edges()} 个棱自由度",
                 color=INK, fontsize=11)
    ax.scatter([], [], color=TEAL, label="每条棱对应一个数")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(.5, -.18), fontsize=10)
    save(fig, "mesh_dofs.svg")


def boundary_dofs():
    fig, ax = plt.subplots(figsize=(4.2, 3.1))
    mesh_edges(ax, n=4, highlight_boundary=True)
    ax.set_title("橙色：外边界棱；灰色：内部棱", color=INK, fontsize=11)
    ax.annotate("", (.71, 1.035), (.32, 1.035),
                arrowprops={"arrowstyle": "-|>", "color": AMBER, "lw": 2})
    ax.text(.51, 1.07, r"$t$", color=AMBER, ha="center", fontsize=11)
    ax.set(xlim=(-.06, 1.06), ylim=(-.08, 1.16))
    save(fig, "boundary_dofs.svg")


def quadrature_triangle():
    mesh = fealpy_mesh(1)
    bcs, weights = mesh.quadrature_formula(8, "cell").get_quadrature_points_and_weights()
    bcs, weights = bm.asarray(bcs), bm.asarray(weights)
    # Reference vertices: (0,0), (1,0), (0,1), matching barycentric order.
    points = bcs @ bm.array([[0, 0], [1, 0], [0, 1]])
    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    ax.add_patch(Polygon([[0, 0], [1, 0], [0, 1]], facecolor="#f5f8f9",
                         edgecolor=INK, lw=1.8))
    ax.scatter(points[:, 0], points[:, 1], s=25+650*weights,
               color=TEAL, alpha=.75, edgecolor="white", linewidth=.5)
    ax.set_title(f"q = 8：{len(weights)} 个实际积分点", color=INK, fontsize=11)
    ax.text(.57, .75, "点越大，权重越高", color=TEAL, fontsize=10)
    clean(ax, (-.05, 1.12), (-.08, 1.10), True)
    save(fig, "quadrature_triangle.svg")


def boundary_cases():
    fig, axes = plt.subplots(1, 3, figsize=(8.8, 2.1))
    for ax, title, color in zip(axes,
        ["内部公共边", "外边界", "材料界面"], [TEAL, BLUE, AMBER]):
        ax.add_patch(Rectangle((0, 0), 2, 1.25, facecolor="#f4f8f9", edgecolor=GRID))
        ax.plot([1, 1], [0, 1.25], color=color, lw=3)
        ax.set_title(title, color=color, fontsize=11)
        clean(ax, (-.05, 2.05), (-.28, 1.45))
    axes[0].plot([0, 1, 2], [0, 1.25, 0], color=GRID, lw=1)
    axes[1].patches[0].set_width(1)
    axes[1].lines[0].set_xdata([1, 1])
    axes[2].add_patch(Rectangle((1, 0), 1, 1.25, facecolor="#eaf4f1", edgecolor="none"))
    axes[0].text(1, -.1, "共享切向迹", ha="center", color=INK, fontsize=10)
    axes[1].text(1, -.1, "施加切向边界值", ha="center", color=INK, fontsize=10)
    axes[2].text(1, -.1, r"$D_n$ 的物理条件", ha="center", color=INK, fontsize=10)
    fig.subplots_adjust(wspace=.12)
    save(fig, "boundary_cases.svg")


if __name__ == "__main__":
    tangent_normal()
    mesh_vs_material()
    curl_vs_div()
    hcurl_trace()
    continuity_choice()
    shared_edge_dof()
    potential_vs_field()
    basis_field()
    curl_2d()
    exact_curl_and_source()
    weak_form_boundary()
    matrix_sparsity()
    mesh_dofs()
    boundary_dofs()
    quadrature_triangle()
    boundary_cases()

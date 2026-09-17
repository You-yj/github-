#!/usr/bin/env python3
"""
Gmsh 共形网格上的三维双永磁体磁标势有限元算例。

Gmsh 只生成线性四面体几何网格；有限元次数由
``LagrangeFESpace(mesh, p=p)`` 控制。近磁体和 Maxwell 盒区域较细，
远场较粗。默认使用 p=2 计算 d=0 mm，``--scan`` 扫描全部 16 个位置。
"""


from __future__ import annotations

import argparse
import math
from itertools import product

import gmsh
import matplotlib.pyplot as plt
import numpy as np
import pyamg
from scipy.sparse.linalg import cg

from fealpy.backend import backend_manager as bm

from fealpy.mesh import TetrahedronMesh
from fealpy.functionspace import LagrangeFESpace
from fealpy.fem import BilinearForm, LinearForm
from fealpy.fem import GradSourceIntegrator, ScalarDiffusionIntegrator


MU0 = 4.0 * math.pi * 1.0e-7  # 真空磁导率，单位 H/m。
BR_Z = 0.38                   # 两个永磁体沿 +z 方向的剩磁通密度，单位 T。
MZ = BR_Z / MU0               # 磁化强度幅值，A/m

# 包围下磁体的 Maxwell 应力积分盒的两个对角点，单位 m。
MAXWELL_LO = np.array([-12.0, -8.0, -5.0]) * 1.0e-3
MAXWELL_HI = np.array([12.0, 8.0, 4.0]) * 1.0e-3

# ANSYS Mechanical APDL 指南第 6.7.2 节 EMFT 宏的参考磁力（作用在上磁体上），
# 仅用于结果对比与绘图，不参与求解。
ANSYS_REFERENCE_FORCE = {
    0.0: (0.59446, 0.62914), 2.0: (0.22622, 0.64344), 4.0: (-0.004062, 0.64730),
    6.0: (-0.22972, 0.64007), 8.0: (-0.60745, 0.60659), 10.0: (-0.93074, 0.52447),
    12.0: (-1.09950, 0.43539), 14.0: (-1.13700, 0.35075), 16.0: (-1.08570, 0.23258),
    18.0: (-0.91710, 0.12708), 20.0: (-0.58312, 0.041178), 22.0: (-0.24666, 0.0034075),
    24.0: (-0.079544, 0.0021191), 26.0: (0.010552, 0.0039768), 28.0: (0.036675, -0.0022967),
    30.0: (0.052253, 0.011228),
}


def akoun_yonnet_force(d):
    """计算位移 d 下上磁体（磁体 2）受到的解析力 (Fx, Fy)，d 的单位为 mm。"""
    a, b, c = np.array([10.0, 6.0, 3.0])*1.0e-3
    A, B, C = np.array([6.0, 10.0, 3.0])*1.0e-3
    alpha, beta, gamma = np.array([-4.0+d, -4.0, 8.0])*1.0e-3
    force = np.zeros(2)

    for m, n, p, q, r, s in product((0, 1), repeat=6):
        U = alpha + A*(-1)**m - a*(-1)**n
        V = beta + B*(-1)**q - b*(-1)**p
        W = gamma + C*(-1)**s - c*(-1)**r
        R = np.sqrt(U**2 + V**2 + W**2)
        angle = np.arctan2(U*V, W*R)
        sign = (-1)**(m+n+p+q+r+s)

        force[0] += sign*(
            (V**2-W**2)*np.log(R-U)/2
            + U*V*np.log(R-V)
            + V*W*angle
            + U*R/2
        )
        force[1] += sign*(
            (U**2-W**2)*np.log(R-V)/2
            + U*V*np.log(R-U)
            + U*W*angle
            + V*R/2
        )
    return BR_Z**2*force/(4*np.pi*MU0)


def gmsh_to_fealpy_tetra_mesh(volume_to_cell_tag):
    """
    提取 Gmsh 四节点四面体网格，并按体区域写入单元标签。

    Parameters
    ----------
    volume_to_cell_tag : dict[int, int]
        Gmsh 三维体编号到单元区域编号的映射。

    Returns
    -------
    mesh : TetrahedronMesh
        转换后的 FEALPy 四面体网格。
    cell_tag : TensorLike, shape (NC,)
        每个四面体的区域编号。
    """
    node_tags, node_coordinates, _ = gmsh.model.mesh.getNodes()
    node_tags = np.asarray(node_tags, dtype=np.int64)
    node = np.asarray(node_coordinates).reshape(-1, 3)
    element_tags, connectivity = gmsh.model.mesh.getElementsByType(4)
    element_tags = np.asarray(element_tags, dtype=np.int64)
    connectivity = np.asarray(connectivity, dtype=np.int64).reshape(-1, 4)

    node_tag_to_index = np.empty(node_tags.max() + 1, dtype=np.int64)
    node_tag_to_index[node_tags] = np.arange(len(node_tags))
    cell = node_tag_to_index[connectivity]

    element_tag_to_cell = np.full(element_tags.max() + 1, -1, dtype=np.int64)
    element_tag_to_cell[element_tags] = np.arange(len(element_tags))
    cell_tag = np.zeros(len(cell), dtype=np.int32)
    for volume_tag, tag in volume_to_cell_tag.items():
        volume_element_tags, _ = gmsh.model.mesh.getElementsByType(4, volume_tag)
        cell_tag[element_tag_to_cell[volume_element_tags]] = tag

    mesh = TetrahedronMesh(bm.from_numpy(node), bm.from_numpy(cell))
    return mesh, bm.from_numpy(cell_tag)


class DoubleMagnetBenchmark:
    """
    Gmsh 共形网格上的双永磁体磁标势有限元算例。
    """

    def __init__(self, p=2, h_near=1.5, h_far=6.0, show=False):
        """
        保存离散参数；具体位移对应的网格和空间由 ``solve(d)`` 创建。

        Parameters
        ----------
        p : int
            连续 Lagrange 有限元的次数，当前使用 1 或 2。
        h_near : float
            磁体及 Maxwell 盒附近的目标网格尺寸，单位 mm。
        h_far : float
            远场空气区域的目标网格尺寸，单位 mm。
        show : bool
                    是否弹出 Gmsh FLTK 图形窗口（无显示环境请保持 False）。
        """
        self.p = p
        self.h_near = h_near
        self.h_far = h_far
        self.show = show
        self.d = None
        self.mesh = None
        self.space = None
        self.cell_tag = None
        self.air_box = None
        self.face_indices = None
        self.face_normals = None

    def build_gmsh_mesh(self):
        """
        Boolean fragment 后生成材料面和 Maxwell 面都共形的四面体网格。

        使用 ``solve(d)`` 设置的 ``self.d`` 以及网格尺寸参数，
        结果保存在 ``self.mesh``、``self.cell_tag`` 和 ``self.space`` 中，
        同时构造 Maxwell 面编号和外法向。
        """
        x_max = 30.0 + max(self.d - 8.0, 0.0)
        self.air_box = np.array(
            [-30.0, -30.0, -27.0, x_max, 30.0, 27.0]
        ) * 1.0e-3
        magnet1_lo = np.array([-10.0, -6.0, -3.0]) * 1.0e-3
        magnet1_hi = np.array([10.0, 6.0, 3.0]) * 1.0e-3
        magnet2_lo = np.array([-10.0 + self.d, -14.0, 5.0]) * 1.0e-3
        magnet2_hi = np.array([2.0 + self.d, 6.0, 11.0]) * 1.0e-3

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(f"double_magnet_d{self.d:g}")

        # 构建几何
        air = gmsh.model.occ.addBox(
            self.air_box[0], 
            self.air_box[1], self.air_box[2],
            self.air_box[3] - self.air_box[0],
            self.air_box[4] - self.air_box[1],
            self.air_box[5] - self.air_box[2],
        )
        magnet1 = gmsh.model.occ.addBox(*magnet1_lo, *(magnet1_hi - magnet1_lo))
        magnet2 = gmsh.model.occ.addBox(*magnet2_lo, *(magnet2_hi - magnet2_lo))
        maxwell_box = gmsh.model.occ.addBox(*MAXWELL_LO, *(MAXWELL_HI - MAXWELL_LO))

        ## 几何合并
        _, fragment_map = gmsh.model.occ.fragment(
            [(3, air)], [(3, magnet1), (3, magnet2), (3, maxwell_box)]
        )
        magnet1_volumes = fragment_map[1]
        magnet2_volumes = fragment_map[2]
        maxwell_volumes = fragment_map[3]
        gmsh.model.occ.synchronize()

        # 构造尺寸场：近场细、远场粗
        field = gmsh.model.mesh.field.add("Box")
        near_bounds = {
            "XMin": -18.0,
            "XMax": max(18.0, self.d + 8.0),
            "YMin": -20.0,
            "YMax": 14.0,
            "ZMin": -11.0,
            "ZMax": 17.0,
        }
        gmsh.model.mesh.field.setNumber(field, "VIn", self.h_near * 1.0e-3)
        gmsh.model.mesh.field.setNumber(field, "VOut", self.h_far * 1.0e-3)
        for name, value in near_bounds.items():
            gmsh.model.mesh.field.setNumber(field, name, value * 1.0e-3)

        gmsh.model.mesh.field.setNumber(field, "Thickness", 8.0e-3)
        gmsh.model.mesh.field.setAsBackgroundMesh(field)

        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)  # HXT
        gmsh.option.setNumber("Mesh.ElementOrder", 1)

        gmsh.model.mesh.generate(3)

        # 单元区域编号：0=盒外空气，1=盒内空气，2=下磁体，3=上磁体。
        volume_to_cell_tag = {tag: 1 for _, tag in maxwell_volumes}
        volume_to_cell_tag.update({tag: 2 for _, tag in magnet1_volumes})
        volume_to_cell_tag.update({tag: 3 for _, tag in magnet2_volumes})
        self.mesh, self.cell_tag = gmsh_to_fealpy_tetra_mesh(volume_to_cell_tag)

        if self.show:
            gmsh.fltk.run()
        gmsh.finalize()

        self.space = LagrangeFESpace(self.mesh, p=self.p)
        self.face_indices, self.face_normals = self.find_maxwell_faces()

    def assemble(self):
        """
        组装刚度和右端 (M, grad v)。

        Returns
        -------
        stiffness : fealpy.sparse.CSRTensor
            FEALPy 后端的全局刚度矩阵，对应积分 ``(grad(phi), grad(v))``。
        rhs : TensorLike, shape (gdof,)
            全局右端向量，对应永磁体区域上的 ``(M, grad(v))``。
        """
        form = BilinearForm(self.space)
        form.add_integrator(ScalarDiffusionIntegrator(q=self.p + 1))
        stiffness = form.assembly()

        NC = self.mesh.number_of_cells()
        magnetization = bm.zeros((NC, 1, 3), dtype=self.mesh.ftype)
        magnetization = bm.set_at(magnetization, (self.cell_tag >= 2, 0, 2),MZ)
        form = LinearForm(self.space)
        form.add_integrator(GradSourceIntegrator(magnetization, q=self.p))
        rhs = form.assembly()
        return stiffness, rhs

    def find_maxwell_faces(self):
        """
        由盒内外空气区域的跳变找 Maxwell 面，并给出指向盒外的法向。

        Returns
        -------
        face_indices : TensorLike, shape (NF,)
            Maxwell 闭合面上的全局三角面编号。
        face_normals : TensorLike, shape (NF, 3)
            各三角面的单位法向，方向由盒内指向盒外。
        """
        face_to_cell = self.mesh.face_to_cell()[:, :2]
        adjacent_tags = self.cell_tag[face_to_cell]
        is_maxwell_face = (
            ((adjacent_tags[:, 0] == 1) & (adjacent_tags[:, 1] == 0))
            | ((adjacent_tags[:, 0] == 0) & (adjacent_tags[:, 1] == 1))
        )
        fidx = bm.nonzero(is_maxwell_face)[0]

        face_center = self.mesh.entity_barycenter("face")[fidx]
        fn = bm.copy(self.mesh.face_unit_normal(index=fidx))
        box_center = bm.asarray(0.5*(MAXWELL_LO + MAXWELL_HI), dtype=bm.float64)

        points_outward = bm.einsum("fi,fi->f", fn, face_center-box_center)>0.0
        fn = bm.set_at(fn, ~points_outward, -fn[~points_outward])
        return fidx, fn

    def _solve_linear_system(self, stiffness, rhs):
        """
        用 PyAMG 预条件的 CG 求解相容的半正定 Neumann 系统。

        Parameters
        ----------
        stiffness : fealpy.sparse.CSRTensor
            FEALPy 全局刚度矩阵。
        rhs : TensorLike, shape (gdof,)
            FEALPy 后端的全局右端向量。

        Returns
        -------
        phi : TensorLike, shape (gdof,)
            转回 FEALPy 后端的磁标势自由度值。
        """
        matrix = stiffness.to_scipy().tocsr()
        vector = bm.to_numpy(rhs)

        multigrid = pyamg.smoothed_aggregation_solver(matrix, symmetry="symmetric")
        preconditioner = multigrid.aspreconditioner(cycle="V")
        phi, info = cg(matrix, vector, M=preconditioner, rtol=1.0e-10,
                       atol=1.0e-12, maxiter=5000,)
        return bm.from_numpy(phi)

    def _cell_grad_basis_on_faces(self, face_indices, face_bc, side):
        """
        在相同物理面高斯点求指定一侧四面体的基函数梯度。

        Parameters
        ----------
        face_indices : TensorLike, shape (NF,)
            待计算的全局三角面编号。
        face_bc : TensorLike, shape (NQ, 3)
            三角面高斯点的重心坐标。
        side : int
            取 ``face_to_cell`` 中的第 0 或第 1 个相邻四面体。

        Returns
        -------
        grad_basis : TensorLike, shape (NF, NQ, ldof, 3)
            指定侧四面体基函数在面高斯点处的物理梯度。
        """
        face = self.mesh.entity("face")[face_indices]
        cell = self.mesh.entity("cell")
        face_to_cell = self.mesh.face_to_cell()[face_indices]
        adjacent_cell = face_to_cell[:, side]
        cell = cell[adjacent_cell]

        NF = len(face_indices)
        NQ = len(face_bc)
        ldofs = self.space.number_of_local_dofs("cell")
        result = bm.empty((NF, NQ, ldofs, 3), dtype=face_bc.dtype)

        # 计算面顶点在相邻四面体局部顶点中的位置，形状为 (NF, 3)。
        positions = bm.argmax(face[:, :, None] == cell[:, None, :], axis=2)
        # grad_basis 要求一组单元共享相同的重心坐标，因此按最多 24 种排列分组。
        patterns, pattern_index = bm.unique( positions, axis=0, return_inverse=True)

        for i in range(len(patterns)):
            group = bm.nonzero(pattern_index == i)[0]
            cell_bc = bm.zeros((NQ, 4), dtype=face_bc.dtype)
            cell_bc = bm.set_at(cell_bc, (slice(None), patterns[i]), face_bc)

            gbasis = self.space.grad_basis(cell_bc, index=adjacent_cell[group])
            result = bm.set_at(result, group, gbasis)
        return result

    def compute_maxwell_force(self, phi):
        """
        在面高斯点平均相邻 0/1 单元的磁场，再积分 Maxwell 应力。

        Parameters
        ----------
        phi : TensorLike, shape (gdof,)
            磁标势的有限元自由度值。
        Returns
        -------
        force : TensorLike, shape (3,)
            Maxwell 闭合面包围的下磁体所受力，单位 N。
        """
        mface = self.face_indices

        quadrature = self.mesh.quadrature_formula(2 * self.p - 1, "face")
        face_bc, weights = quadrature.get_quadrature_points_and_weights()

        gbasis0 = self._cell_grad_basis_on_faces(mface, face_bc, side=0)
        gbasis1 = self._cell_grad_basis_on_faces(mface, face_bc, side=1)

        face2cell = self.mesh.face_to_cell()[mface]
        cell2dof = self.space.cell_to_dof()

        phi0 = phi[cell2dof[face2cell[:, 0]]]
        phi1 = phi[cell2dof[face2cell[:, 1]]]

        grad0 = bm.einsum("fi,fqid->fqd", phi0, gbasis0)
        grad1 = bm.einsum("fi,fqid->fqd", phi1, gbasis1)
        face_b = -0.5*MU0*(grad0 + grad1)

        normals = self.face_normals[:, None, :]
        b_dot_n = bm.sum(face_b * normals, axis=-1)
        b_squared = bm.sum(face_b * face_b, axis=-1)
        traction = (b_dot_n[:, :, None]*face_b - b_squared[:, :, None]*normals/2)/MU0
        face_area = self.mesh.entity_measure("face")[mface]
        return bm.einsum("f,q,fqi->i", face_area, weights, traction)

    def solve(self, d):
        """
        为给定位移生成网格和空间，然后完成场求解与磁力计算。

        Parameters
        ----------
        d : float
            上磁体沿 x 方向的位移，单位 mm。

        Returns
        -------
        result : dict
            包含位移、磁标势以及上下磁体受力。
        """
        self.d = float(d)
        self.build_gmsh_mesh()

        stiffness, rhs = self.assemble()
        phi = self._solve_linear_system(stiffness, rhs)
        F0 = self.compute_maxwell_force(phi)
        return {"d": self.d, "phi": phi, "F0": F0, "F1": -F0}

    @classmethod
    def run_scan(cls, p= None):
        """
        扫描 d=0,2,...,30 mm，支持一个或多个有限元阶次 p。
        打印磁力并显示力—位移曲线。
        打印 FEALPy 与解析解、ANSYS 的误差对比图。
        
        Parameters
        ----------
        p : int or list[int], optional
            连续 Lagrange 有限元的次数，若为整数则仅计算该阶次。
            若为 None 或列表，则分别计算列表中的每个阶次。
            默认 None 等价于 [1, 2]。
        """
        if p is None:
            p_values = [1, 2]
        elif isinstance(p, int):
            p_values = [p]
        else:
            p_values = list(p)

        # 存储每个 p 的结果    
        results = {}    
        displacement = bm.arange(0.0, 31.0, 2.0)

        for p_val in p_values:
            print(f"\n===== 正在计算 p={p_val} =====")
            case = cls(p=p_val)
            forces = []
            for d in displacement:
                full_force = case.solve(float(d))["F1"]  # 三维向量
                force_xy = full_force[:2]                # 只取 x 和 y 分量 , 为后面绘图、误差计算方便
                print(f"d={d:4.0f} mm  F={full_force} N")# 输出结果仍然是包括 x、y、z 三个分量的力
                forces.append(force_xy)
            
            forces = bm.stack(forces)  # shape (N, 2
            plot_d = bm.to_numpy(displacement)
            plot_force = bm.to_numpy(forces)# 转 numpy 便于绘图

            # 解析解 (Akoun-Yonnet)
            analytic = np.array([akoun_yonnet_force(d) for d in plot_d])
            # ANSYS 参考
            ansys = np.array([ANSYS_REFERENCE_FORCE.get(float(d), (np.nan, np.nan))
                                      for d in plot_d])

            results[p_val] = {
                "d": plot_d,
                "force": plot_force,
                "analytic": analytic,
                "ansys": ansys,
            }

        # ---------- 力-位移曲线 ----------
        plt.figure()
        # 颜色循环
        colors = ['b', 'r']
        markers = ['o', 's']
        for idx, p_val in enumerate(p_values):
            data = results[p_val]
            plot_d = data["d"]
            plot_force = data["force"]
            ana = data["analytic"]
            ans = data["ansys"]
            c = colors[idx % len(colors)]
            m = markers[idx % len(markers)]

            plt.plot(plot_d, plot_force[:, 0], f"{m}-", color=c,
                     label=f"FEALPy_FEM p={p_val} $F_x$")
            plt.plot(plot_d, plot_force[:, 1], f"{m}--", color=c,
                     label=f"FEALPy_FEM p={p_val} $F_y$")

        # 解析解和 ANSYS 只画一次（相同）
        data0 = results[p_values[0]]
        d_np = data0["d"]
        ana = data0["analytic"]
        ans = data0["ansys"]
        plt.plot(d_np, ana[:, 0], "k--", label="analytic $F_x$")
        plt.plot(d_np, ana[:, 1], "k:", label="analytic $F_y$")
        plt.plot(d_np, ans[:, 0], "s:", label="ANSYS $F_x$")
        plt.plot(d_np, ans[:, 1], "s--", label="ANSYS $F_y$")

        plt.xlabel(r"Displacement $d$ (mm)")
        plt.ylabel("Force (N)")
        plt.grid(True)
        plt.legend()
        plt.show()


        # ---------- 误差对比图 ----------
        ##注意，用FEALPy求解得到的 force 是三维的， 但我们只关心 x 和 y 分量，因此在绘制误差时，只取前两列。
        plt.figure()
        for idx, p_val in enumerate(p_values):
            data = results[p_val]
            d_np = data["d"]
            f_np = data["force"]
            ana = data["analytic"]
            ans = data["ansys"]
            c = colors[idx % len(colors)]
            m = markers[idx % len(markers)]

            # 与解析解的误差
            err_ana = f_np - ana
            plt.plot(d_np, err_ana[:, 0], f"{m}-", color=c,
                     label=f"p={p_val} vs analytic $F_x$")
            plt.plot(d_np, err_ana[:, 1], f"{m}--", color=c,
                     label=f"p={p_val} vs analytic $F_y$")

            # 与 ANSYS 的误差（仅有效点）
            mask = np.isfinite(ans[:, 0]) & np.isfinite(ans[:, 1])
            if np.any(mask):
                d_ans = d_np[mask]
                err_ans_x = f_np[mask, 0] - ans[mask, 0]
                err_ans_y = f_np[mask, 1] - ans[mask, 1]
                plt.plot(d_ans, err_ans_x, f"{m}-", color=c, alpha=0.5,
                         label=f"p={p_val} vs ANSYS $F_x$")
                plt.plot(d_ans, err_ans_y, f"{m}--", color=c, alpha=0.5,
                         label=f"p={p_val} vs ANSYS $F_y$")


        plt.xlabel(r"Displacement $d$ (mm)")
        plt.ylabel("Force Error (N)")
        plt.grid(True)
        plt.legend()
        plt.show()


    @classmethod
    def main(cls):
        """
        解析命令行参数并运行单点计算或完整位移扫描。
        """
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--d", type=float, default=0.0)
        parser.add_argument("--p", type=int, choices=(1, 2), default=2)
        parser.add_argument("--scan", action="store_true")
        args = parser.parse_args()
        bm.set_backend("numpy")
        if args.scan:
            # 扫描模式：同时计算 p=1 和 p=2
            cls.run_scan(None)
        else:
            case = cls(p=args.p)
            result = case.solve(args.d)
            print("F0 (lower magnet):", result["F0"], "N")
            print("F1 (upper magnet):", result["F1"], "N")


if __name__ == "__main__":
    DoubleMagnetBenchmark.main()

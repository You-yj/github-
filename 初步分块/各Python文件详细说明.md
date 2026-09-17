# 永磁静磁标势程序——各 Python 文件详细说明

## 1. 项目结构

当前程序分为三层：

```text
双磁体具体算例层
    modular_double_magnet_benchmark.py
                │
                ▼
通用静磁有限元模块
    magnetostatic/
        geometry.py
        materials.py
        mesh.py
        pde.py
        solver.py
        postprocess.py
        __init__.py
                │
                ▼
原始数值回归基准
    double_magnet_benchmark.py
```

> 注：`double_magnet_benchmark.py` 的物理文件位于上一级「最初程序」目录；
> 本目录通过 `test_regression.py` 引用它作为数值回归基准。

模块化程序的数据流为：

```text
GeometryModel + MeshOptions
              │
              ▼
     GmshTetraMesher
              │
              ▼
          MeshData
              │
              ├────────────── ScalarPotentialPDE
              │                         │
              └──────────┬──────────────┘
                         ▼
              ScalarPotentialSolver
                         │
                         ▼
                    FEMSolution
                         │
                         ▼
            MaxwellStressPostprocessor
                         │
                         ▼
                    Force (3,)
```

总体设计原则是：

1. 几何模块只描述区域和网格参数；
2. 网格模块只负责 Gmsh 建模、共形分割及 FEALPy 网格转换；
3. 材料和 PDE 模块负责向每个区域提供物理系数；
4. 求解模块只负责有限元空间、组装和线性方程求解；
5. 后处理模块只读取有限元解并计算 Maxwell 应力；
6. 具体 benchmark 只保存本算例的尺寸、位置、材料和运行参数。

程序内部统一采用 SI 单位：长度为 m，磁化强度为 A/m，磁感应强度为 T，磁力为 N。命令行中的位移和网格尺寸保留使用 mm，进入模块后转换成 m。

---

## 2. `magnetostatic/geometry.py`

### 2.1 文件职责

该文件定义与具体网格生成器无关的几何数据。它回答的是：

> 用户希望建立哪些区域，这些区域的位置和尺寸是多少，需要怎样的网格尺寸场？

该文件不调用 Gmsh，不创建 FEALPy 网格，也不包含磁性材料参数。

### 2.2 `_vector3`

```python
def _vector3(value, name) -> np.ndarray
```

内部辅助函数，用于把输入转换为长度为 3 的 NumPy 浮点向量。

有效输入：

```python
[0.0, 1.0, 2.0]
np.array([0.0, 1.0, 2.0])
```

如果输入不是三维向量，会立即抛出 `ValueError`，从而提前发现中心、尺寸或上下界输入错误。

### 2.3 `BoxRegion`

```python
@dataclass(frozen=True)
class BoxRegion:
    name: str
    center: tuple
    size: tuple
    priority: int = 0
```

表示一个轴对齐长方体区域。`center` 与 `size` 内部以**不可变 tuple** 存储，`frozen` 数据类不会被 numpy 数组原地修改。

参数含义：

| 参数 | 含义 | 单位 |
|---|---|---|
| `name` | 区域唯一名称 | — |
| `center` | 长方体中心坐标 | m |
| `size` | $x,y,z$ 三个方向的完整长度 | m |
| `priority` | 重叠区域的标签优先级 | — |

例如，一个中心位于原点、尺寸为 $20\times12\times6\ \mathrm{mm}$ 的磁体写成：

```python
BoxRegion(
    name="lower_magnet",
    center=[0.0, 0.0, 0.0],
    size=np.array([20.0, 12.0, 6.0]) * 1.0e-3,
    priority=10,
)
```

类中提供两个计算属性：

```python
region.lower
region.upper
```

计算公式为：

$$
\boldsymbol{x}_{\mathrm{lo}}
=\boldsymbol{x}_c-\frac12\boldsymbol{s},
\qquad
\boldsymbol{x}_{\mathrm{hi}}
=\boldsymbol{x}_c+\frac12\boldsymbol{s}.
$$

`size` 表示完整尺寸，而不是半尺寸。

#### 用角点构造（逐位复现）

当几何来自已知角点（例如需要与既有基准逐位对齐）时，使用：

```python
BoxRegion.from_corners(
    name="upper_magnet",
    lower=np.array([-10.0 + d, -14.0, 5.0]) * 1.0e-3,
    upper=np.array([2.0 + d, 6.0, 11.0]) * 1.0e-3,
    priority=10,
)
```

`from_corners` 原样保存角点，`lower` / `upper` 返回这些精确值。若用`BoxRegion(center, size)` 构造，角点按 `center ± size/2` 反推，可能与原始
角点相差 1 ulp——这种微小差异足以让 Gmsh 产生拓扑略不同的网格。`make_geometry` 中全部区域都使用 `from_corners`，因此分块版与最初程序的
几何输入**逐位一致**。

#### 区域优先级

本算例的 Maxwell 空气盒包围下磁体，因此两个区域在几何上重叠。为了保证重叠部分最终属于磁体，使用：

```python
maxwell_air.priority = 0
lower_magnet.priority = 10
```

网格标签按优先级从低到高写入，高优先级磁体会覆盖低优先级 Maxwell 空气区域。

### 2.4 `BoxSizeField`

```python
@dataclass(frozen=True)
class BoxSizeField:
    lower: tuple
    upper: tuple
    h_inside: float
    h_outside: float
    thickness: float = 0.0
```

描述一个 Gmsh `Box` 背景尺寸场。

| 参数 | 含义 | 单位 |
|---|---|---|
| `lower` | 加密盒下角点 | m |
| `upper` | 加密盒上角点 | m |
| `h_inside` | 盒内目标网格尺寸 | m |
| `h_outside` | 盒外目标网格尺寸 | m |
| `thickness` | 内外尺寸的过渡厚度 | m |

该对象只描述尺寸场，真正的 Gmsh field 在 `mesh.py` 中创建。

### 2.5 `MeshOptions`

```python
@dataclass(frozen=True)
class MeshOptions:
    size_fields: tuple[BoxSizeField, ...] = ()
    algorithm_3d: int = 10
    show: bool = False
```

保存网格生成选项：

- `size_fields`：一个或多个局部尺寸场；
- `algorithm_3d=10`：Gmsh HXT 三维四面体算法；
- `show`：是否打开 Gmsh FLTK 窗口。

有限元次数 $p$ 不属于网格选项，因为 Gmsh 只生成线性几何网格，有限元次数由 FEALPy `LagrangeFESpace` 控制。

### 2.6 `GeometryModel`

```python
@dataclass(frozen=True)
class GeometryModel:
    outer: BoxRegion
    regions: tuple[BoxRegion, ...]
    interface_names: dict[str, tuple[str, str]]
```

完整几何模型由以下内容组成：

- `outer`：最外层计算域，通常为空气盒；
- `regions`：磁体、Maxwell 空气区等嵌入区域；
- `interface_names`：需要在后处理中使用的命名区域界面。

例如：

```python
interface_names={
    "lower_magnet_maxwell_surface": (
        "maxwell_air",
        "outer_air",
    )
}
```

元组第一个区域是积分面的内部区域，第二个区域是外部区域。这个顺序决定后处理中的外法向方向。

该类会检查所有区域名称是否唯一，以及命名界面引用的区域是否存在。

当前几何生成器只支持轴对齐长方体，但可以在以后增加圆柱、旋转体或 STEP 模型，同时保持 PDE、求解器和后处理模块不变。

---

## 3. `magnetostatic/materials.py`

### 3.1 文件职责

该文件描述材料的相对磁导率和磁化强度。

采用材料关系：

$$
\boldsymbol B
=\mu_0\left(\mu_r\boldsymbol H+\boldsymbol M\right),
\qquad
\boldsymbol H=-\nabla\phi.
$$

因此：

$$
\boldsymbol B
=\mu_0\left(-\mu_r\nabla\phi+\boldsymbol M\right).
$$

### 3.2 `Air`

```python
@dataclass(frozen=True)
class Air:
    relative_permeability: float = 1.0
```

空气默认满足：

$$
\mu_r=1,
\qquad
\boldsymbol M=\boldsymbol 0.
$$

`magnetization` 属性返回三维零向量。这样 PDE 模块可以统一访问空气和磁体的：

```python
material.relative_permeability
material.magnetization
```

### 3.3 `PermanentMagnet`

```python
class PermanentMagnet:
    magnetization: tuple
    relative_permeability: float = 1.0
```

表示一个线性永磁材料。

沿 $+z$ 方向磁化：

```python
PermanentMagnet(
    magnetization=[0.0, 0.0, MZ],
    relative_permeability=1.0,
)
```

任意方向磁化：

```python
PermanentMagnet(
    magnetization=[1.0e5, 2.0e5, 3.0e5],
    relative_permeability=1.05,
)
```

磁化强度单位为 A/m。构造函数会检查磁化强度是否为三维向量，并检查相对磁导率是否为正数。

---

## 4. `magnetostatic/mesh.py`

### 4.1 文件职责

该文件负责：

1. 根据 `GeometryModel` 建立 Gmsh OCC 几何；
2. 对空气、磁体和 Maxwell 区域进行共形布尔分割；
3. 配置背景网格尺寸场；
4. 生成线性四面体网格；
5. 把 Gmsh 网格转换为 FEALPy `TetrahedronMesh`；
6. 建立单元标签和区域名称映射。

### 4.2 `MeshData`

```python
@dataclass
class MeshData:
    mesh: TetrahedronMesh
    cell_tags: TensorLike
    region_tags: dict[str, int]
    interface_names: dict[str, tuple[str, str]]
```

#### `mesh`

FEALPy 四面体网格，保存节点、单元、三角面、拓扑邻接和几何量。

#### `cell_tags`

形状为 `(NC,)`，其中 `NC` 为四面体单元数。每个整数表示一个四面体所属的区域。

#### `region_tags`

保存区域名称到整数标签的映射，例如：

```python
{
    "outer_air": 0,
    "maxwell_air": 1,
    "lower_magnet": 2,
    "upper_magnet": 3,
}
```

其他模块应使用：

```python
mesh_data.tag("lower_magnet")
```

查询标签，而不应该假定磁体标签一定大于等于 2。

#### `interface_names`

保存命名区域界面，供 Maxwell 后处理使用。

### 4.3 `_extract_tetra_mesh`

```python
def _extract_tetra_mesh(volume_to_cell_tag)
```

该函数完成 Gmsh 到 FEALPy 的转换。

#### 提取节点

```python
node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
```

Gmsh 节点编号不保证从 0 开始，也不保证连续。

#### 提取四面体

```python
element_tags, connectivity = gmsh.model.mesh.getElementsByType(4)
```

Gmsh 元素类型 4 表示线性四节点四面体。

#### 压缩节点编号

程序建立 `node_tag_to_index`，把 Gmsh 的任意节点编号映射成 FEALPy 需要的连续下标：

```text
Gmsh:  1, 2, 5, 8, ...
FEALPy: 0, 1, 2, 3, ...
```

#### 建立单元标签

`volume_to_cell_tag` 描述：

```text
Gmsh 三维体编号 → 用户区域标签
```

程序查询各 Gmsh 三维体包含的四面体编号，并给 `cell_tags` 赋值。

#### 构造 FEALPy 网格

```python
mesh = TetrahedronMesh(
    bm.from_numpy(nodes),
    bm.from_numpy(cells),
)
```

### 4.4 `GmshTetraMesher.generate`

主要调用方式：

```python
mesh_data = GmshTetraMesher().generate(
    geometry,
    mesh_options,
    model_name="double_magnet_d0",
)
```

执行步骤如下。

1. 外空气默认分配标签 0；
2. 嵌入区域按 `priority` 从低到高排序并分配标签；
3. 调用 `gmsh.initialize()`；
4. 通过 `gmsh.model.occ.addBox()` 创建各区域；
5. 通过 `gmsh.model.occ.fragment()` 做共形布尔分割；
6. 创建一个或多个 Gmsh `Box` 尺寸场；
7. 设置 HXT 算法并生成三维线性四面体；
8. 按区域优先级写入单元标签；
9. 转换成 FEALPy 网格；
10. 返回 `MeshData`；
11. 在 `finally` 中调用 `gmsh.finalize()`。

使用 `try/finally` 可以保证即使网格生成失败，Gmsh 状态也会被正确释放。

### 4.5 多个尺寸场

如果只有一个尺寸场，直接设为背景场。如果有多个尺寸场，使用 Gmsh `Min` 场组合，取各尺寸场给出的最小网格尺寸。

### 4.6 共形网格的重要性

空气、磁体和 Maxwell 盒必须一起执行 `fragment`。这样：

- 磁体表面是四面体真实公共面；
- Maxwell 盒表面是四面体真实公共面；
- 后处理可以通过 `face_to_cell` 精确找到积分面；
- 不需要依靠坐标容差搜索近似表面。

---

## 5. `magnetostatic/pde.py`

### 5.1 文件职责

该文件把命名区域映射为逐单元物理系数。它不生成网格，也不直接组装矩阵。

由：

$$
\nabla\cdot\boldsymbol B=0,
\qquad
\boldsymbol H=-\nabla\phi,
$$

得到磁标势弱形式：

$$
\int_\Omega
\mu_r\nabla\phi\cdot\nabla v\,\mathrm dx
=
\int_\Omega
\boldsymbol M\cdot\nabla v\,\mathrm dx.
$$

### 5.2 `ScalarPotentialPDE`

```python
pde = ScalarPotentialPDE(
    materials={
        "outer_air": Air(),
        "magnet_0": PermanentMagnet(...),
    },
    mu0=MU0,
)
```

材料字典的键必须与 `GeometryModel` 的区域名称相同。

### 5.3 `validate`

检查网格中的每个命名区域是否都有对应材料。如果缺少材料，立即抛出异常，避免把未知区域错误地当作空气。

### 5.4 `relative_permeability_by_cell`

生成形状为 `(NC,)` 的逐单元相对磁导率：

$$
(\mu_r)_K,
\qquad K=1,\ldots,N_C.
$$

程序通过 `cell_tags == region_tag` 找到属于某个材料区域的全部单元，然后写入对应的 $\mu_r$。

### 5.5 `magnetization_by_cell`

生成形状为 `(NC, 1, 3)` 的逐单元磁化强度。

最后一个维度是三维向量，中间的长度 1 用于兼容 FEALPy `GradSourceIntegrator` 的求积点维度。

该方法不再使用原程序中的：

```python
cell_tag >= 2
```

也不再把磁化方向固定为 z 方向。每个命名区域都可以有独立的磁化强度和磁化方向。

---

## 6. `magnetostatic/solver.py`

### 6.1 文件职责

该文件负责：

1. 创建连续 Lagrange 有限元空间；
2. 组装磁标势方程的刚度矩阵和右端；
3. 建立 PyAMG 预条件器；
4. 使用共轭梯度法求解；
5. 输出包含完整上下文的 `FEMSolution`。

### 6.2 `SolverOptions`

```python
@dataclass(frozen=True)
class SolverOptions:
    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    maxiter: int = 5000
```

用于控制 SciPy 共轭梯度法的相对容差、绝对容差和最大迭代次数。

### 6.3 `FEMSolution`

```python
@dataclass
class FEMSolution:
    mesh_data: MeshData
    pde: ScalarPotentialPDE
    space: LagrangeFESpace
    degree: int
    potential: TensorLike
    solver_info: dict
```

相比只返回 `phi` 数组，该对象还保存：

- 网格和区域标签；
- 材料/PDE；
- 有限元空间；
- 有限元次数；
- 求解器状态。

后处理模块因此不需要用户再次传入网格、空间和材料参数。

### 6.4 `ScalarPotentialSolver.__init__`

```python
solver = ScalarPotentialSolver(p=2)
```

这里的 `p` 是连续 Lagrange 有限元次数，要求 $p\ge1$。它和 Gmsh 的几何网格阶次相互独立。

### 6.5 `assemble`

输入：

```python
mesh_data, pde
```

输出：

```python
space, stiffness, rhs
```

首先创建：

```python
space = LagrangeFESpace(mesh, p=p)
```

当全部区域满足 $\mu_r=1$ 时，左端使用：

```python
ScalarDiffusionIntegrator(q=p + 1)
```

对应：

$$
K_{ij}
=\int_\Omega\nabla N_j\cdot\nabla N_i\,\mathrm dx.
$$

当不同材料具有不同相对磁导率时，加入逐单元系数：

$$
K_{ij}
=\int_\Omega\mu_r\nabla N_j\cdot\nabla N_i\,\mathrm dx.
$$

右端使用：

```python
GradSourceIntegrator(magnetization, q=p)
```

对应：

$$
f_i
=\int_\Omega\boldsymbol M\cdot\nabla N_i\,\mathrm dx.
$$

### 6.6 `solve`

FEALPy 稀疏矩阵先转换为 SciPy CSR：

```python
matrix = stiffness.to_scipy().tocsr()
```

然后建立 PyAMG 平滑聚合多重网格预条件器，最后使用预条件共轭梯度法：

```python
potential, info = cg(...)
```

本算例外边界为自然齐次 Neumann 边界，刚度矩阵具有常数核。相容右端与常数核正交，从零初值开始的 CG 可以在去掉常数方向的子空间中求解。磁场和磁力只依赖 $\nabla\phi$，所以磁标势相差一个常数不会影响结果。

求解器的两个实现细节：

- **pyamg 为可选依赖**：模块顶部 `try/except` 导入；未安装时回退无预条件 CG，并发出 `RuntimeWarning`。
- **CG 未收敛的处理**：`info < 0` 抛 `RuntimeError`；`info > 0`（达到最大迭代次数但未达到容限）发出 `RuntimeWarning`，提示解可能不准确。

需要注意：PyAMG 的 OpenMP 归约顺序存在约 $10^{-12}\ \mathrm{N}$ 量级的逐位不确定性（同一程序连跑三次的实测上限），且奇异系统的常数分量会随之漂移——因此数值回归以「磁力 F0/F1」和「去均值后的 $\phi$」为判据，而不是逐位比较 $\phi$。

当前求解器尚未实现：

- 显式 Dirichlet 边界条件；
- 零均值约束；
- 固定单个自由度的规范条件。

---

## 7. `magnetostatic/postprocess.py`

### 7.1 文件职责

该文件负责：

1. 根据命名区域界面寻找 Maxwell 闭合面；
2. 根据相邻单元拓扑确定积分面外法向；
3. 在相同面求积点计算两侧单元的磁标势梯度；
4. 恢复磁感应强度；
5. 积分 Maxwell 应力得到磁力。

### 7.2 `SurfaceData`

```python
@dataclass
class SurfaceData:
    face_indices: TensorLike
    outward_normals: TensorLike
    inside_region: str
    outside_region: str
```

保存离散积分面的三角面编号、外法向以及内外区域名称。

### 7.3 `select_interface`

调用方式：

```python
surface = postprocessor.select_interface(
    solution,
    "lower_magnet_maxwell_surface",
)
```

程序首先读取命名界面：

```python
("maxwell_air", "outer_air")
```

然后从 `mesh.face_to_cell()` 获得每个三角面两侧的四面体。只有两侧标签恰好分别是 `maxwell_air` 和 `outer_air` 的面才会被选中。

不能简单选择 `maxwell_air` 的全部边界，因为 Maxwell 空气区域还与下磁体接触，那样会错误地把磁体表面加入积分面。

### 7.4 外法向

对于每个选中的面，程序找到内部单元和外部单元的重心，并构造：

$$
\boldsymbol d
=\boldsymbol x_{\mathrm{outside}}
-\boldsymbol x_{\mathrm{inside}}.
$$

如果 FEALPy 返回的面法向与 $\boldsymbol d$ 方向相反，就将法向翻转。

因此法向始终从命名界面的第一个区域指向第二个区域。该方法由拓扑确定方向，不依赖固定 Maxwell 盒中心，也可以扩展到非凸积分面。

### 7.5 `_cell_grad_basis_on_faces`

为了计算面上的磁场，需要在同一个物理三角面求积点分别计算两侧四面体中的基函数梯度。

三角面三个顶点在相邻四面体中的局部编号可能不同，因此程序：

1. 找到面顶点在相邻四面体中的局部位置；
2. 按相同局部顶点排列进行分组；
3. 把三角形重心坐标嵌入四面体重心坐标；
4. 调用 `space.grad_basis()`；
5. 得到形状 `(NF, NQ, ldof, 3)` 的物理梯度。

其中：

- `NF`：Maxwell 三角面数量；
- `NQ`：每个面的求积点数量；
- `ldof`：每个四面体的局部自由度数。

### 7.6 `compute_force`

首先采用面求积阶数：

```python
2*p - 1
```

两侧磁标势梯度为：

$$
\nabla\phi_h^\pm
=\sum_i\Phi_i\nabla N_i^\pm.
$$

两侧磁感应强度为：

$$
\boldsymbol B^\pm
=\mu_0\left(
\boldsymbol M^\pm
-\mu_r^\pm\nabla\phi_h^\pm
\right).
$$

面磁场采用两侧平均：

$$
\boldsymbol B_F
=\frac12\left(\boldsymbol B^-+\boldsymbol B^+\right).
$$

本算例的 Maxwell 面两侧均为空气，因此：

$$
\boldsymbol B_F
=-\frac{\mu_0}{2}
\left(\nabla\phi_h^-+\nabla\phi_h^+\right),
$$

与原 benchmark 完全一致。

真空 Maxwell 应力牵引为：

$$
\boldsymbol t
=\frac1{\mu_0}
\left[
(\boldsymbol B\cdot\boldsymbol n)\boldsymbol B
-\frac12|\boldsymbol B|^2\boldsymbol n
\right].
$$

离散磁力为：

$$
\boldsymbol F
\approx
\sum_{F\in\mathcal S_h}|F|
\sum_qw_q\boldsymbol t(\boldsymbol x_q).
$$

返回形状为 `(3,)` 的磁力向量，单位为 N。

使用该后处理时，Maxwell 面应当：

- 位于空气中；
- 是闭合面；
- 不穿过磁体或其他非空气材料；
- 与网格保持共形。

---

## 8. `magnetostatic/__init__.py`

### 8.1 文件职责

该文件统一导出包的公开接口，本身不进行数值计算。

有了它，可以直接写：

```python
from magnetostatic import (
    Air,
    BoxRegion,
    GeometryModel,
    GmshTetraMesher,
    PermanentMagnet,
    ScalarPotentialPDE,
    ScalarPotentialSolver,
)
```

而不需要分别从每个子模块导入。

`__all__` 明确哪些类属于包的稳定公开接口，以下划线开头的内部辅助函数不会被导出。

---

## 9. `modular_double_magnet_benchmark.py`

### 9.1 文件职责

该文件是具体双永磁体算例的配置和运行入口。它不再实现通用网格转换、有限元组装或 Maxwell 应力算法。

### 9.2 物理常量

```python
MU0 = 4.0 * math.pi * 1.0e-7
BR_Z = 0.38
MZ = BR_Z / MU0
```

- `MU0`：真空磁导率，H/m；
- `BR_Z`：沿 z 方向的剩磁通密度，T；
- `MZ`：等效磁化强度，A/m。

### 9.3 `make_geometry`

```python
geometry = make_geometry(displacement_mm)
```

根据上磁体的 x 方向位移建立本算例几何。全部区域用
`BoxRegion.from_corners` 以最初程序的原始角点算式构造，保证传入 Gmsh 的
几何参数与最初程序**逐位一致**（见 §2.3）。

下磁体：

$$
\boldsymbol x_0=(0,0,0)\ \mathrm{mm},
\qquad
\boldsymbol s_0=(20,12,6)\ \mathrm{mm}.
$$

上磁体：

$$
\boldsymbol x_1=(-4+d,-4,8)\ \mathrm{mm},
\qquad
\boldsymbol s_1=(12,20,6)\ \mathrm{mm}.
$$

当 $d>8\ \mathrm{mm}$ 时，外空气盒的 $+x$ 边界随位移增大，保持与原程序相同的远场截断策略。

该函数还创建：

- `outer_air`；
- `maxwell_air`；
- `lower_magnet`；
- `upper_magnet`；
- `lower_magnet_maxwell_surface` 命名界面。

### 9.4 `make_mesh_options`

```python
make_mesh_options(
    displacement_mm,
    h_near_mm=1.5,
    h_far_mm=6.0,
    show=False,
)
```

把原程序的近场和远场网格参数转换成 `BoxSizeField`。函数参数使用 mm，内部转换成 m。

### 9.5 `make_pde`

建立区域到材料的映射：

```python
{
    "outer_air": Air(),
    "maxwell_air": Air(),
    "lower_magnet": magnet,
    "upper_magnet": magnet,
}
```

两个磁体当前都沿 $+z$ 方向磁化。若要让磁体方向不同，只需要为两个区域绑定不同的 `PermanentMagnet`，不需要修改求解器。

### 9.6 `solve`

```python
result = solve(
    displacement_mm=0.0,
    p=2,
    h_near_mm=1.5,
    h_far_mm=6.0,
)
```

内部执行：

```text
make_geometry
    → GmshTetraMesher.generate
    → make_pde
    → ScalarPotentialSolver.solve
    → MaxwellStressPostprocessor.compute_force
```

返回：

```python
{
    "d": displacement,
    "solution": solution,
    "phi": solution.potential,
    "F0": lower_force,
    "F1": -lower_force,
}
```

- `F0`：Maxwell 盒包围的下磁体所受力；
- `F1`：按照封闭系统力平衡取 `-F0`；
- `solution`：完整 `FEMSolution`；
- `phi`：为了兼容原程序提供的磁标势快捷字段。

### 9.7 `main`

命令行入口。运行示例：

```bash
python modular_double_magnet_benchmark.py \
    --d 0 --p 2 --h-near 1.5 --h-far 6.0
```

参数含义：

| 参数 | 含义 | 默认值 |
|---|---|---:|
| `--d` | 一个或多个上磁体 x 方向位移，mm | 0 |
| `--p` | 连续 Lagrange 有限元次数 | 2 |
| `--h-near` | 近场网格尺寸，mm | 1.5 |
| `--h-far` | 远场网格尺寸，mm | 6.0 |
| `--show` | 打开 Gmsh 图形窗口 | False |

当前模块化入口支持一个或多个离散工况，并可通过 `--compare`、`--csv` 和
`--plot` 调用独立对比模块。原程序将解析公式、参考数据、误差计算和绘图混在
benchmark 类中；模块化版本已将这些职责拆开。

### 9.8 `solve_many`

`solve_many` 用于一次提交多个离散的位移：

```python
results = solve_many([0.0, 2.0, 4.0, 10.0], p=2)
```

命令行等价写法为：

```powershell
python modular_double_magnet_benchmark.py --d 0 2 4 10 --p 2
```

每个返回元素都与 `solve(d)` 的返回字典相同。由于位移会改变上磁体和空气盒
的几何，每个 `d` 都必须重新执行几何分割和网格生成，不能直接共用同一张网格。
该接口只负责批量求解；其结果可以继续交给独立的 `comparison.py` 完成解析解
对比、统计和曲线绘制。

### 9.9 对比相关命令行参数

| 参数 | 作用 |
|---|---|
| `--compare` | 在终端打印逐点对比表和误差统计 |
| `--csv PATH` | 将逐点结果写入 CSV，同时打印误差统计 |
| `--plot PATH` | 保存 FEALPy、解析解和 ANSYS 的对比曲线 |
| `--error-plot PATH` | 保存 `FEALPy - reference` 的带符号误差曲线 |
| `--show-comparison` | 交互显示对比曲线 |

对比明确使用上磁体的 `F1`，从而与解析公式和 ANSYS 表采用相同的受力对象与
符号约定。

---

## 10. `double_magnet_reference.py`

### 10.1 文件职责

该文件只保存双长方体永磁体 benchmark 特有的参考数据，不依赖 FEALPy：

- `akoun_yonnet_force(d)`：Akoun–Yonnet 解析磁力；
- `ANSYS_REFERENCE_FORCE`：ANSYS 的离散参考表；
- `ansys_reference_force(d)`：统一的 ANSYS 查询接口。

解析函数返回作用在上磁体上的 `(Fx, Fy)`。ANSYS 表仅在
$d=0,2,\ldots,30\ \mathrm{mm}$ 上有值；查询其他位移会返回两个 `NaN`，后续
统计会自动忽略这些缺失项。

将参考解放在独立文件后，通用有限元模块不再知道 Akoun–Yonnet 公式或 ANSYS
数据，新算例也可以换用自己的参考函数。

---

## 11. `comparison.py`

### 11.1 文件职责

该文件是与 FEALPy 无关的通用比较模块，负责：

1. 从一组求解结果中提取指定磁力；
2. 在相同位移上计算一个或多个参考解；
3. 计算逐点误差；
4. 统计 MAE、RMSE 和最大绝对误差；
5. 输出终端表格、CSV 和对比曲线。

### 11.2 `compare_force_results`

典型调用为：

```python
comparison = compare_force_results(
    results,
    references={
        "analytic": akoun_yonnet_force,
        "ANSYS": ansys_reference_force,
    },
    force_key="F1",
)
```

参考源既可以是 `reference(d)` 形式的函数，也可以是 `{d: force}` 字典。默认
比较 x、y 两个分量。

### 11.3 `ForceComparison`

保存位移、有限元磁力、各参考磁力及分量名称，并提供：

- `errors`：逐点 `FEM - reference`；
- `metrics()`：统计指标；
- `format_cases()`：格式化逐点表；
- `format_metrics()`：格式化统计表；
- `write_csv(path)`：写出 UTF-8 CSV；
- `plot(path, show)`：保存或显示曲线。
- `plot_errors(path, show)`：保存或显示逐分量带符号误差曲线。

每个分量的误差定义为：

$$e_i=F_i^{\mathrm{FEM}}-F_i^{\mathrm{ref}}.$$

统计量包括：

$$
\mathrm{MAE}=\frac1N\sum_i|e_i|,
\qquad
\mathrm{RMSE}=\sqrt{\frac1N\sum_i e_i^2},
\qquad
e_{\max}=\max_i|e_i|.
$$

归一化 RMSE 使用该参考分量在全部有效位移上的峰值作为尺度。没有采用逐点
相对误差，因为本算例的 $F_x$ 在部分位移附近过零，逐点相对误差会发散并失去
物理意义。

---

## 12. `double_magnet_benchmark.py`

---

### 12.1 文件职责

这是重构前已经实现和验证的单文件 benchmark。当前保留该文件不变，作为模块化版本的数值回归基准。

### 12.2 `akoun_yonnet_force`

计算两个长方体永磁体之间的 Akoun–Yonnet 解析力，返回作用在**上磁体**上的 `(Fx, Fy)`（与 §10.1 的符号口径一致），用于和 FEALPy 有限元结果比较，不参与有限元求解。

### 12.3 `gmsh_to_fealpy_tetra_mesh`

提取 Gmsh 节点、线性四面体和区域标签，然后构造 FEALPy `TetrahedronMesh`。对应模块化版本中的 `_extract_tetra_mesh`。

### 12.4 `DoubleMagnetBenchmark.__init__`

保存：

- 有限元次数 `p`；
- 近场网格尺寸 `h_near`；
- 远场网格尺寸 `h_far`；
- 是否显示 Gmsh 窗口；
- 当前位移、网格、空间、标签和 Maxwell 面等运行状态。

### 12.5 `build_gmsh_mesh`

该方法同时负责具体几何、尺寸场、布尔分割、网格生成、FEALPy 转换、有限元空间和 Maxwell 面构造。

模块化版本把这些职责拆分到：

```text
geometry.py
mesh.py
postprocess.py
```

### 12.6 `assemble`

组装刚度矩阵和磁化右端。原程序通过：

```python
self.cell_tag >= 2
```

判断磁体，并通过：

```python
magnetization[..., 2] = MZ
```

把所有磁化方向固定为 $+z$。模块化版本已经用命名区域和材料映射消除了这些限制。

### 12.7 `find_maxwell_faces`

通过标签 1 和标签 0 的跳变寻找 Maxwell 面，再根据固定盒心判断面法向。模块化版本改为通过命名界面选面，并根据内外相邻单元重心确定法向。

### 12.8 `_solve_linear_system`

将 FEALPy 矩阵转换为 SciPy CSR，使用 PyAMG 预条件的 CG 求解纯 Neumann 半正定系统。对应模块化版本的 `ScalarPotentialSolver.solve()`。

### 12.9 `_cell_grad_basis_on_faces`

在 Maxwell 面求积点上计算两侧相邻四面体的基函数梯度。该算法在模块化版本中移动到了后处理模块。

### 12.10 `compute_maxwell_force`

计算两侧磁标势梯度、恢复平均磁场、构造 Maxwell 应力牵引并完成闭合面积分。对应模块化版本的 `MaxwellStressPostprocessor.compute_force()`。

### 12.11 `solve`

单个位移工况的总流程：

```text
build_gmsh_mesh
    → assemble
    → _solve_linear_system
    → compute_maxwell_force
```

返回位移、磁标势以及上下两个磁体的力。

### 12.12 `run_scan`

扫描：

$$
d=0,2,\ldots,30\ \mathrm{mm},
$$

支持 $P_1/P_2$ 有限元，并绘制：

- FEALPy 力—位移曲线；
- Akoun–Yonnet 解析曲线；
- ANSYS 参考曲线；
- FEALPy 相对解析解和 ANSYS 的误差曲线。

该部分属于具体 benchmark 的验证逻辑，后续适合迁移成独立的扫描和验证文件，而不应放入通用求解器。

### 12.13 `main`

原程序命令行入口，支持单工况和完整位移扫描：

```bash
python double_magnet_benchmark.py --d 0 --p 2
python double_magnet_benchmark.py --scan
```

---

## 13. 原程序与模块化程序的对应关系

| 原程序内容 | 模块化位置 |
|---|---|
| 双磁体尺寸和位置 | `modular_double_magnet_benchmark.py` |
| Gmsh 几何描述 | `geometry.py` |
| 网格尺寸场 | `geometry.py`、`mesh.py` |
| Gmsh 到 FEALPy 转换 | `mesh.py` |
| 区域材料参数 | `materials.py`、`pde.py` |
| 刚度矩阵和右端组装 | `solver.py` |
| PyAMG-CG 求解 | `solver.py` |
| Maxwell 面选择 | `postprocess.py` |
| 面两侧梯度计算 | `postprocess.py` |
| Maxwell 应力积分 | `postprocess.py` |
| 解析公式和 ANSYS 数据 | `double_magnet_reference.py` |
| 通用误差统计、CSV 和对比图 | `comparison.py` |
| 多位移批量求解 | `modular_double_magnet_benchmark.py` 的 `solve_many` |

---

## 14. 如何定义一个新的永磁体问题

### 第一步：定义几何

```python
geometry = GeometryModel(
    outer=BoxRegion("outer_air", outer_center, outer_size),
    regions=(
        BoxRegion("magnet_a", center_a, size_a, priority=10),
        BoxRegion("magnet_b", center_b, size_b, priority=10),
    ),
)
```

### 第二步：生成网格

```python
mesh_data = GmshTetraMesher().generate(
    geometry,
    MeshOptions(size_fields=(size_field,)),
)
```

### 第三步：绑定材料

```python
pde = ScalarPotentialPDE({
    "outer_air": Air(),
    "magnet_a": PermanentMagnet([0.0, 0.0, 3.0e5]),
    "magnet_b": PermanentMagnet([1.0e5, 0.0, 2.8e5]),
})
```

### 第四步：求解

```python
solution = ScalarPotentialSolver(p=2).solve(mesh_data, pde)
phi = solution.potential
```

### 第五步：计算磁力

若几何中定义了 Maxwell 空气区和命名界面：

```python
force = MaxwellStressPostprocessor().compute_force(
    solution,
    "maxwell_surface",
)
```

---

## 15. 当前版本的适用范围和后续工作

当前版本已经完成的功能：

- 任意数量的轴对齐长方体磁体；
- 任意磁体中心和尺寸；
- 任意三维均匀磁化方向；
- 命名区域到材料的映射；
- 不同区域相对磁导率的数据接口；
- Gmsh 共形四面体网格；
- FEALPy 连续 Lagrange 磁标势求解；
- 命名 Maxwell 界面；
- 基于拓扑的积分面外法向；
- Maxwell 应力磁力计算。
- Akoun–Yonnet 和 ANSYS 参考数据对比；
- MAE、RMSE、最大绝对误差和归一化 RMSE；
- 对比 CSV 与曲线输出。

建议后续依次完成：

1. ~~在正确安装 FEALPy 的环境中运行新旧程序单工况数值回归~~ 已由
   `test_regression.py` 完成 p=1、d=0 的端到端回归（网格逐位一致、磁力在
   求解器噪声水平内一致）；可扩展到 p=2 与更多位移；
2. ~~对 CG 的 `info > 0` 未收敛状态增加严格处理~~ 已改为 `RuntimeWarning`，
   可进一步改为抛异常或自动重试；
3. 增加显式 Dirichlet、零均值或固定自由度规范条件；
4. ~~增加对比模块和原 benchmark 的端到端数值回归测试~~ 已由
   `test_regression.py` 覆盖；
5. ~~增加更多求解器和后处理单元测试~~ 已新增 15 项包内单元测试
   （`test_magnetostatic.py`）；后处理路径仍可继续补充测试；
6. 扩展圆柱、旋转体和 STEP 几何；
7. 增加 VTK/VTU 场结果输出；
8. 验证不同相对磁导率条件下 FEALPy 系数积分器的数据形状和数值结果。

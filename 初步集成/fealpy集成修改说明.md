# 双永磁体算例 → FEALPy 集成：修改说明

本文档说明将「双永磁体算例 + 命令行参数」项目中的可复用静磁组件集成进`fealpy/` 仓库的全部修改内容、规范依据、设计决策与验证结果。

## 1. 目标与范围

- **目标**：把算例 `magnetostatic/` 包中的通用组件（材料、几何描述、Gmsh网格生成、磁标势 FEM 求解、Maxwell 应力后处理）集成进本目录的 `fealpy/`仓库，并把算例入口切换到集成后的 FEALPy 接口；算例实际运行时导入的是本目录替换后的 `fealpy`，而不是环境中其他目录下的 fealpy。
- **不集成**：双磁体 benchmark 专属内容（具体几何尺寸、Akoun–Yonnet 解析公式、ANSYS 参考表、CLI、对比/绘图）仍留在算例目录，作为 FEALPy 公共能力的下游用户。
- **原 `magnetostatic/` 本地包**：保留但不再被算例导入（可逆），其通用逻辑已并入 `fealpy`。原 `double_magnet_benchmark.py` 数值回归基准保持
  数值逻辑不变，仅增加本地 fealpy 优先引导。

## 2. 规范依据与两份规范文档的差异核查

本工作以 `fealpy/` 仓库内的规范为**主**：

- `fealpy/AGENTS.md`（仓库级 AI 协作入口）
- `fealpy/standards/fealpy_python_coding_standard.md`（v0.2）
- `fealpy/standards/fealpy_python_docstring_standard.md`（v0.2）
- `fealpy/standards/fealpy_examples_standard.md`（v0.4）
- `fealpy/standards/fealpy_logging_standard.md`（v0.1）

项目根目录的《FEALPy 开发规范.md》为较旧文档，与仓库内现行规范存在以下差异，本次一律以 **fealpy 目录内规范为准**：

| 事项 | 旧《FEALPy 开发规范.md》 | fealpy 目录内现行规范（本次采用） |
|---|---|---|
| 测试目录 | 测试放 `fealpy/test` | 新测试写 `tests/`；`test/` 为遗留目录，CI 不运行 |
| 算例目录 | 算例放 `fealpy/example` | 新增示例进 `examples/`；`example/` 为历史迁移来源 |
| `__str__` | 所有主要类都应实现 | 已废除机械要求（coding standard 10.5），按对象需要实现 |
| 类型别名 | 别名默认加下划线 | 公共/内部边界决定是否加 `_`（如 `TensorLike`、`Index`） |
| 后端约束 | 一律用 bm，不能出现 np/torch | 算法代码用 bm；Backend adapter、数据转换边界等允许具体后端 |
| 导入顺序 | 先绝对后相对、按 FEM 流程分组 | 标准库 / 第三方 / FEALPy 三组，组间空行 |
| PDE 算例命名 | `exp0001.py` + DATA_TABLE | 仍适用于 `fealpy/model/<type>/` 的算例注册体系；本集成不属该体系，不适用 |

本次集成不涉及 `mesh_old/`、`old/` 等遗留代码，不新增第三方依赖（`pyamg` 按 fealpy 既有 optional 依赖处理，见 §5.3），不修改`fealpy.egg-info/`、构建产物与版本号。

## 3. 修改文件清单

### 3.1 fealpy 仓库内（本次替换的目标）

| 文件 | 类型 | 内容 |
|---|---|---|
| `fealpy/fealpy/material/magnetic_material.py` | 新增 | `Air`、`LinearMagneticMaterial`、`PermanentMagnet` 与可扩展的 `MagneticMaterialProtocol` |
| `fealpy/fealpy/material/__init__.py` | 修改 | 导出上述四个符号 |
| `fealpy/fealpy/mesher/box_region_mesher.py` | 新增 | 单类 `BoxRegionMesher`：几何描述（options 字典，支持角点形式的区域描述以逐位复现参考几何）+ Gmsh 建模/提取/尺寸场；逐单元标签存为 mesh cell sector 的 `"region"` attribute（新网格机制正统），`cell_tags` 属性读透该 attribute |
| `fealpy/fealpy/mesher/__init__.py` | 修改 | 在既有 try/except 块内追加导出 `BoxRegionMesher` |
| `fealpy/fealpy/cem/fem/magnetostatic_lfem_model.py` | 新增 | `MagnetostaticLFEMModel`、`SolverOptions`、`SurfaceData`、`RegionTaggedMeshDataProtocol`、`MU0`；支持函数型磁化源、显式规范点与 Maxwell 应力后处理 |
| `fealpy/fealpy/cem/fem/__init__.py` | 修改 | 导出静磁标势 FEM 模型、显式解 Maxwell 力函数及公共辅助类型 |
| `fealpy/tests/material/test_magnetic_material.py` | 新增 | 材料构造、有限值和三分量向量校验测试（10 项） |
| `fealpy/tests/mesher/test_box_region_mesher.py` | 新增 | options 严格解析/校验（含角点形式）+ Gmsh 网格冒烟测试（29 项） |
| `fealpy/tests/cem/fem/test_magnetostatic_lfem_model.py` | 新增 | 模型组装/求解/后处理 + 制造解收敛性 + 网格标签、材料协议和状态守卫测试（29 项） |

### 3.2 算例目录（项目根目录，配合集成切换接口）

| 文件 | 类型 | 内容 |
|---|---|---|
| `modular_double_magnet_benchmark.py` | 修改 | 导入源由本地 `magnetostatic` 包切换为 `fealpy.material` / `fealpy.mesher` / `fealpy.cem.fem`；`make_pde()` 改为 `make_materials()`；`solve()` 改用 `MagnetostaticLFEMModel`；入口增加本地 fealpy 优先引导；`make_mesher` 全部区域改用**角点形式**，与最初程序的几何输入逐位一致 |
| `double_magnet_benchmark.py` | 修改 | 仅增加相同的本地 fealpy 优先引导块，数值逻辑不变 |
| `double_magnet_cli.py` | 修改 | 补充位移、近场和远场网格尺寸的有限值、非负/正值及大小关系校验 |
| `comparison.py` | 修改 | 补充结果、参考源、分量索引/名称、向量维数和有限值校验，拒绝歧义输入 |
| `test_double_magnet_cli.py`、`test_comparison.py` | 修改 | 覆盖新增的非法参数与比较数据边界条件 |
| `test_benchmark_regression.py` | 新增 | 端到端回归：集成入口与最初程序在 p=1、d=0 工况下网格逐位一致、磁力在求解器噪声水平内一致 |
| `fealpy集成修改说明.md` | 新增 | 本文档 |
| 其余文件 | 不变 | `double_magnet_reference.py`、`magnetostatic/`（保留未用） |

### 3.3 CGraph 节点库（`node-library/`）

新增 11 个可发现节点，覆盖材料构造、双永磁体工况、盒区域网格、静磁求解、
Maxwell 力、位移扫描、参考数据、误差比较、CSV 导出和曲线绘制；同时提供两条
可执行 CGraph 工作流、三份节点规范文档及节点契约/工作流测试。节点适配层仅负责
校验、序列化材料转换和端口拼接，有限元计算继续由 FEALPy 内核完成。

### 3.4 组件映射（算例 `magnetostatic` 包 → fealpy）

| 原算例组件 | 集成位置 | 说明 |
|---|---|---|
| `materials.Air` | `fealpy.material.Air` | 磁化强度由 np.ndarray 改为不可变 tuple |
| `materials.PermanentMagnet` | `fealpy.material.PermanentMagnet` | 同上 |
| 用户自定义线性材料 | `fealpy.material.LinearMagneticMaterial` / `MagneticMaterialProtocol` | 支持非单位 μᵣ，并允许结构化扩展 |
| `geometry.BoxRegion` | `BoxRegionMesher` options 的 `outer`/`regions` 条目 `(name, center, size, priority)`，或角点形式 `{"name", "lower", "upper", "priority"}` | 折叠进单类，构造时校验；角点形式原样保存坐标，避免 center/size 往返的 1 ulp 漂移 |
| `geometry.BoxSizeField` | options 的 `size_fields` 条目 `(lower, upper, h_inside, h_outside, thickness)` | 同上 |
| `geometry.MeshOptions` | options 的 `algorithm_3d`/`show` 键 | 折叠进单类 |
| `geometry.GeometryModel` | `BoxRegionMesher.__init__(options)` 整体描述 | 折叠进单类，构造时校验名称/界面 |
| `mesh.MeshData` | `BoxRegionMesher` 实例属性 `mesh`/`region_tags`/`interface_names` + mesh cell sector 的 `"region"` attribute | `init_mesh()` 后可用，`tag()` 方法保留；`cell_tags` 属性读透网格 attribute（VTK 写出时自动成为 cell data） |
| `mesh.GmshTetraMesher` | `fealpy.mesher.BoxRegionMesher` | 按 fealpy mesher 命名习惯更名 |
| `pde.ScalarPotentialPDE` | 并入 `fealpy.cem.fem.MagnetostaticLFEMModel` | 逐单元系数方法成为模型方法 |
| `solver.ScalarPotentialSolver` | `fealpy.cem.fem.MagnetostaticLFEMModel` | 改为继承 `ComputationalModel` 的有状态模型 |
| `solver.SolverOptions` | `fealpy.cem.fem.magnetostatic_lfem_model.SolverOptions` | 增加参数合法性校验 |
| `solver.FEMSolution` | 模型自身状态（`space`/`uh`/`stiffness`/`rhs`/`solver_info`） | 与 fealpy 现有 `*LFEMModel` 惯例一致 |
| `postprocess.MaxwellStressPostprocessor` | `MagnetostaticLFEMModel.compute_force()` | 方法与 `select_interface()` |
| `postprocess.SurfaceData` | `fealpy.cem.fem.magnetostatic_lfem_model.SurfaceData` | 不变 |
| `modular_double_magnet_benchmark.make_pde` | 该文件 `make_materials()` | 返回区域名→材料字典 |

## 4. 落点依据（AGENTS.md 路由）

- **材料本构** → `fealpy/material/`（AGENTS.md 3.3：材料模型与参数）。
- **网格生成器** → `fealpy/mesher/`（AGENTS.md 3.1）。按仓库既有
  mesher 形态组织为**单个类**（同 `HollowBlockMesher`）：几何描述、尺寸场、
  界面名称全部作为 `__init__(options)` 的参数，`init_mesh()` 生成网格并把
  `mesh`/`cell_tags`/`region_tags` 存到实例上；`gmsh` 导入方式沿用
  `stp_mesher.py` 的 `try/except ImportError` 守卫。
  嵌入盒必须完全位于外盒内，尺寸场厚度必须非负；错误在 Gmsh 调用前报告。
  网格器本身不绑定电磁语义或 SI 单位，调用者只需保持坐标单位一致。
  **导出约定**：`fealpy/mesher/__init__.py` 顶层与其他条目一致，只导出
  `XxxMesher` 网格器类（`BoxRegionMesher`）。
- **磁标势 FEM 模型与 Maxwell 应力** → `fealpy/cem/fem/`。它虽然复用
  `fealpy.fem` 的通用形式、积分器和空间，但公共接口包含 μ₀、μᵣ、M/H/B、
  永磁体及 Maxwell 应力，属于计算电磁学领域模型。此布局与
  `fealpy/csm/fem/` 的领域包组织一致，也利用了仓库已经预留的
  `fealpy/cem/fem/` 子包。依赖方向保持为 `fealpy.cem.fem -> fealpy.fem`，
  通用 FEM 层不反向导入 CEM，避免循环依赖。

### 4.1 测试内制造解与函数型磁化源

制造解不再注册为 `fealpy.model.poisson.Exp0014`。原因是它的主输入是向量
磁化场 M、边界条件是 B·n=0，不能由通用 `PoissonLFEMModel` 的标量 source
与 Dirichlet 接口直接消费；放入 Poisson DATA_TABLE 会形成名义可发现、实际
不可互换的公共算例。FEALPy 中也并非每个领域模型都必须配一个 `Exp`。

解析函数保留在 `tests/cem/fem/test_magnetostatic_lfem_model.py`，继续验证：

- 区域 Ω=(0,1)³，真解 φ = sin(πx)sin(πy)sin(πz)；
- 磁化场 M = ∇φ + ∇×ψ，ψ = q(x,y,z)(1,1,1)，q=[x(1−x)y(1−y)z(1−z)]²
  紧支撑 → 边界上 (∇×ψ)·n = 0，自然条件 B·n=0 **精确成立**；
- 纯 Neumann 下解差常数，收敛性按 **H¹ 半范**（∇φ 误差）衡量；
- 网格直接使用确定性的 `TetrahedronMesh.from_box()`，不依赖 Gmsh。

配套地，`MagnetostaticLFEMModel` 新增 `set_magnetization_source(source)`：
`source` 可为 callable `M(p)->(...,3)`（`GradSourceIntegrator` 在单元积分
点求值，`@cartesian` 装饰后传入笛卡尔坐标）或 `(NC,1,3)` 张量；传 `None`
恢复分区域常数材料路径。双磁体 benchmark 的默认路径（材料字典）数值逻辑
完全不变。回归测试验证 H¹ 误差随网格加密单调下降。

## 5. 关键设计决策

### 5.1 模型形态：有状态 `ComputationalModel`

`MagnetostaticLFEMModel(p, mu0, options)` 的使用方式：

```python
mesher = BoxRegionMesher(options={
    "outer": ("air", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    "regions": [("magnet", (0.2, 0.2, 0.2), (0.4, 0.4, 0.4), 10)],
})
mesher.init_mesh()

model = MagnetostaticLFEMModel(p=2, mu0=MU0)  # from fealpy.cem.fem import ...
model.set_mesh_data(mesher)   # 使用 mesher.mesh/cell_tags/region_tags/interface_names
model.set_materials({"air": Air(), "magnet": PermanentMagnet([0, 0, MZ])})
uh = model.solve()                  # 返回磁标势，并保存 space/stiffness/rhs/uh
force = model.compute_force("maxwell_surface")   # (3,) N
```

- 前置条件未满足时抛 `RuntimeError`（`set_mesh_data`/`set_materials`必须先于 `assemble`/`solve`/`compute_force`）；
- 材料字典缺区域名时抛 `ValueError`（不静默当作空气）。
- `mesh_data` 只需满足 `RegionTaggedMeshDataProtocol`，不再绑定具体的
  `BoxRegionMesher`，因此后续可接入圆柱、STEP 或外部导入网格。
- 纯 Neumann 线性系统在 SciPy 求解副本上固定第 0 个自由度作为规范点，
  消除常数核；该操作只改变磁标势的任意常数，不改变 H、B 与力。

### 5.2 后端规范

- 组装与应力积分经 `fealpy.backend`（`bm`）；求解边界显式转换为 SciPy CSR，
  完成后再转回当前 FEALPy 后端。当前求解器因此是 CPU/SciPy 路径，而不是
  GPU 原生求解路径；
- `box_region_mesher._extract_tetra_mesh()` 属 Gmsh↔FEALPy 数据转换边界，按 standards 7.2 允许直接使用 numpy（docstring 中已注明职责）；
- 材料/几何参数对象只存纯 Python 标量与 tuple，不依赖任何后端。

### 5.3 可选依赖 pyamg

`pyamg` 在 fealpy 的 `setup.py` 中属 `extras_require["optional"]`，因此：

- 模块顶部 `try: import pyamg / except ImportError: pyamg = None`；
- 有 pyamg：沿用算例原逻辑（smoothed_aggregation + V-cycle 预条件 CG）；
- 无 pyamg：回退无预条件 CG，并按 logging standard 记录 `WARNING`（「使用明显低性能实现」类告警）；
- 未修改 `requirements.txt` / `setup.py`，不引入新依赖。

### 5.4 日志

- 模型继承 `ComputationalModel` 的 `self.logger`（模块路径为 `fealpy.cem.fem.magnetostatic_lfem_model`）；
- 库代码不调用 `basicConfig()`、不装 Handler、默认安静（loggingstandard 3.1/3.2）；
- 组装规模、CG 收敛用 `INFO` 参数化消息，并通过 callback 记录真实迭代数；CG 达到 `maxiter` 未收敛用`WARNING`（logging standard 4.3 的典型场景）；CG `info < 0` 抛
  `RuntimeError`（异常承担失败语义）。

### 5.5 命名、类型标注与 Docstring

- 类 `PascalCase`、函数/变量 `snake_case`、计数缩写 `NC/GDOF` 等按FEALPy 约定；
- 公共接口均有类型标注（`TensorLike`、`RegionTaggedMeshDataProtocol`、`Mapping[str, MagneticMaterialProtocol]` 等），复用 FEALPy 类型约定；
- Docstring 默认英文，说明对象职责、参数语义、shape 约定、前置条件与数学公式（`B = μ₀(μ_r H + M)` 等），与实现保持一致。

### 5.6 数值逻辑保持

弱式、积分器配置（`q=p+1` 扩散、`q=p` 梯度源）、Maxwell 面选择与法向
定向、应力积分公式保持不变。新增规范点、输入状态校验、求解迭代计数，以及
Maxwell 面两侧必须满足 μᵣ=1、M=0 的物理条件检查（见 §7）。

数值对齐策略：`make_mesher` 全部区域使用 `BoxRegionMesher` 的**角点形式**，
把最初程序的角点算式原样传给 Gmsh。center/size 往返会让个别角点漂移 1 ulp，
足以使 Gmsh 产生拓扑略不同的网格（实测磁力差约 2e-6 N）；角点形式下集成
入口与最初程序生成的网格**逐位一致**（`test_benchmark_regression.py` 断言）。

### 5.7 逐单元标签的存放位置（与网格侧机制对齐）

逐单元区域标签存入 **mesh cell sector 的 `"region"` attribute**
（`mesh.cell_view.set_attribute("region", tags)`），而不是游离在 mesher
实例上：

- 这是新网格系统逐单元元数据的**正统存放处**（`vtk_reader`/`vtk_writter`、
  nastran/abaqus adapter 均走同一通道），写 VTU 时 `"region"` 自动成为
  cell data，ParaView 直接可见；
- `BoxRegionMesher.cell_tags` 属性读透该 attribute，模型侧
  `RegionTaggedMeshDataProtocol` 的消费方式不变；
- `region_tags`（name→int）与 `interface_names` 属几何/语义元数据，
  保留在 mesher 实例上；
- 已知限制：网格加密/重编号后 attributes **不自动 remap**，需要调用方
  显式迁移（本算例每工况重建网格，不受影响）。

## 6. 导入优先级问题与解决方案

**问题**：环境中存在一个 editable 安装的 fealpy 3.4.0，指向`/home/you-yingjun/FealPy/fealpy`。若从算例目录直接 `import fealpy`，Python 会把本项目 `./fealpy`（仓库根，无 `__init__.py`）识别为命名空间包的一部分，与 editable finder 混叠，导致 `fealpy.logger` 缺失而`ImportError: cannot import name 'logger' from 'fealpy'`。

**解决**：两个算例入口脚本顶部加入引导块，在任何 fealpy 导入之前把本项目的 `fealpy/` 仓库根插到 `sys.path[0]`：

```python
import sys
from pathlib import Path

_FEALPY_REPO = Path(__file__).resolve().parent / "fealpy"
if str(_FEALPY_REPO) not in sys.path:
    sys.path.insert(0, str(_FEALPY_REPO))
```

之后 `import fealpy` 解析到 `./fealpy/fealpy/__init__.py`（已验证`fealpy.__file__` 指向本项目）。**注意**：引导块必须在本进程首次`import fealpy` 之前执行；直接以脚本方式运行入口文件即可满足（等价做法是运行前设置 `PYTHONPATH=./fealpy`）。不建议在已导入其他 fealpy 的进程中再导入本算例模块。

## 7. 测试与数值回归

### 7.1 新增 FEALPy 测试（68 项全部通过）

```bash
cd 双永磁体算例+命令行参数
PYTHONPATH=fealpy python -m pytest \
    fealpy/tests/material/test_magnetic_material.py \
    fealpy/tests/mesher/test_box_region_mesher.py \
    fealpy/tests/cem/fem/test_magnetostatic_lfem_model.py -q
# 68 passed
```

覆盖：材料默认值、有限值和三分量向量校验，几何名称、优先级、尺寸场、界面
映射与角点形式严格校验，Gmsh 共形网格区域标签，单位及非单位相对磁导率组装，
网格标签完整性、材料协议和值域守卫，CG 规范点与迭代信息，测试内制造解 H¹
收敛，Maxwell 应力端到端（孤立磁体闭合力≈0，按 `B²/(2μ₀)·S` 尺度取容差）。

### 7.2 算例端回归

- 根目录算例测试（`test_comparison.py`、`test_double_magnet_cli.py`、
  `test_benchmark_regression.py`）：19 项通过，含「集成入口与最初程序
  网格逐位一致、磁力在求解器噪声水平内一致」的端到端回归。
- 节点库测试：17 项通过，覆盖 11 个节点的发现/元数据/文档契约、材料与工况校验、工作流连线、参考数据、误差比较及导出。
- CGraph 回归测试：18 项通过。上述相关测试合计 122 项通过。
- 两条节点工作流均实际执行成功；单工况工作流的默认 `p=2, d=0` 结果与下表一致，CG `info=0`、迭代 37 次。
- 数值回归（引导块 + 集成后 fealpy 接口，本机环境实测）：

| 工况 | F0 / N（下磁体受力） | 说明 |
|---|---|---|
| p=1, d=0 | (-0.56731597, -0.57342061, 1.66752555) | 与阶段①②基线一致（网格与最初程序逐位一致） |
| p=2, d=0 | (-0.58042072, -0.57281791, 1.73712687) | 与阶段①②基线逐位一致 |

在同一张 p=1 网格上，显式固定规范点与原奇异 Neumann CG 路径得到的力在
求解器噪声水平内一致（实测最大差异 1.3e-10 N）；规范点只改变磁标势常数。
本表此前的数值来自另一台机器（不同 Gmsh 版本）；在本机重新生成网格后，
p=1 与 p=2 结果与阶段①②基线一致（p=2 逐位复现），不是方程或力公式改变。

### 7.3 变更范围检查（AGENTS.md 6.2）

本次修改只涉及 §3.1 所列静磁文件、§3.2 所列算例/说明文件和新增的
`node-library/`；工作区原有的其他未提交修改保持不动。未触碰 `mesh_old/`、
`old/`、`fealpy.egg-info/` 和构建产物；未新增依赖；未执行安装或发布操作。

## 8. 已知限制与后续建议

- CG `info > 0`（达最大迭代数未收敛）目前仅记录 WARNING，仍返回结果；如需严格处理可改为异常（算例文档原有 TODO 项）。
- 模型暂不支持用户指定的 Dirichlet 边界或零均值约束；当前固定第 0 个自由度
  作为纯 Neumann 问题的内部规范点。
- `compute_force()` 目前只支持分区域常数或张量磁化；设置函数型磁化源（callable）后调用会抛 `NotImplementedError`，避免静默使用错误的磁化数据。
- 磁标势公式要求无自由电流，并要求区域拓扑允许单值标势（多连通区域需要预先
  引入适当的 cut）；材料模型当前为线性、各向同性、标量 μᵣ。
- 线性系统当前通过 SciPy/PyAMG 在 CPU 上求解，其他 FEALPy 后端会经过
  NumPy 往返转换。
- `BoxRegionMesher` 目前只支持轴对齐长方体区域；扩展圆柱/旋转体/STEP 几何时无需改动模型与后处理接口。
- `fealpy/physics/constant.py` 尚未加入 `mu0` 常量（本次为最小变更，仅在模型模块定义 `MU0`）；如后续多模块需要，可再统一迁移。
- 如需在 `examples/fem/` 放置独立可运行示例（按 examples standard 命名 `*_example.py`、headless 可运行），可在本集成基础上另行添加。

## 9. 运行方式

```bash
cd 双永磁体算例+命令行参数

# 单工况（自动使用本目录替换后的 fealpy）
python modular_double_magnet_benchmark.py --d 0 --p 2

# 多位移 + 对比/CSV/图
python modular_double_magnet_benchmark.py \
    --d 0 2 4 6 8 --p 2 --compare \
    --csv results/force_comparison.csv \
    --plot results/force_comparison.png \
    --error-plot results/force_error.png

# 原数值回归基准（仅加引导块，数值逻辑不变）
python double_magnet_benchmark.py --d 0 --p 2
```

Python API：

```python
from modular_double_magnet_benchmark import solve_many

results = solve_many([0.0, 2.0, 4.0, 10.0], p=2)
```

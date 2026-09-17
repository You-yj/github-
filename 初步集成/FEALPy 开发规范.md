# FEALPy 开发规范

# **一、代码风格**

## （1）对象命名

|**对象类型**|**解释**|**命名方式**|**示例**|
|---|---|---|---|
|类\(class\)||所有**首**字母大写<br>|```Python<br>class ScalarDiffusionIntegrator():<br>    ...<br>```|
|函数/方法\(function/method\)||小写\+下划线|```Python<br>def multi_index_matrix():<br>    ...<br>```|
|变量\(variable\)||小写\+下划线<br>***或者***<br>FEALPy 中约定好的缩写|```Python<br>face_to_cell = ...<br>cell2edge = ... # 同 cell_to_edge<br>gdof = 37680 # 指全局自由度个数<br>```|
|常量变量\(constant\)|指自创建就不再修改的变量；也可以按普通变量进行命名。|大写\+下划线<br>***或者***<br>FEALPy 中约定好的缩写|```Python<br>GDOF = space.number_of_global_dofs()<br>LDOF = space.number_of_local_dofs()<br>NN = mesh.number_of_nodes()<br>TD = 2 # 指拓扑维数<br>```|
|不需要用户直接操作的方法和属性||在原有命名前面加上一个下划线|```Python<br>def _simplex_measure(self, index): # 方法<br>    self._value = ... # 属性<br>```|
|不需要用户直接操作的全局对象||***可选****  *在原有命名前面加上一个下划线|```Python<br># 全部索引，常用于默认值<br># 类似于 np.s_[:]<br>_S = slice(None)<br>```|
|类型变量|用于 typehint 的类型对象。|\(1\)自定义类型<br>与“类”做法相同<br>\(2\)别名<br>在原名或其缩写前加下划线（别名通常用于简化代码，而非用户使用，故本质上是上一条“不需要用户直接操作的全局对象”）|```Python<br># 自定义“索引”类型，<br># 可以是张量、整数或切片<br>Index = Union[Tensor, int, slice]<br># 定义了 dtype 类型的别名<br>_dtype = torch.dtype<br># 临时把函数空间称为 _FS<br>_FS = FunctionSpace<br>```|

注意：

- 采用 “face” 作为接口和变量名，可以保证代码在 2D/3D 甚至更高维统一扩展，具有更好的通用性和可维护性。

- 只有在实现极其依赖 2D 几何结构时，才会用 edge，否则推荐一律使用 face。



## （2）源码文件内布局

单个文件应当按如下框架组织其内容：\(1\)导入、\(2\)全局变量、\(3\)类和函数。由于需求的多样化，布局不可能做精细的规范，大致按这种方式形成代码块集群即可，允许零散的特例存在。这三类代码之间都需要至少一个空行将它们分割开来。

*注意：此处仅规范源代码，脚本可能类似。*

例如：

```Python
from abc import ABCMeta
from typing import(
    Union, Optional, Dict, Tuple, Any, Type, Generic, TypeVar, overload
)

from .. import logger

_Self = TypeVar("_Self")
_DT = TypeVar("_DT")
Number = Union[int, float, complex]
Size = Tuple[int, ...]

class TensorLike(metaclass=ABCMeta):
```

### 2\.1 导入

导入的对象按其来源一般分为三类：\(1\)Python 内置库、\(2\)第三方库、\(3\)其它导入。导入时应按此顺序导入，**并在类别之间有一个空行**，先导入Python内置库和第三方库，再导入FEALPy的相关库，例如：

1. 导入 Python 内置库

2. 导入 Python 第三方库

3. 导入 FEALPy 相关模块，导入的顺序参考有限元求解的算法流程导入，先进行网格空间材料等定义，再进行有限元矩阵的组装等

    1. **第一类**：`FEALPy`内的工具库，比如backend，typing，decorator，model等

    2. **第二类**：网格，空间和材料等

    3. **第三类**：fem内关于有限元的部分

    4. **第四类**：求解器的导入

注意：先进行绝对导入，再进行相对导入！

```Python
from typing import Any, Optional, Union

from ..backend import bm
from ..typing import TensorLike
from ..decorator import variantmethod
from ..model import ComputationalModel
from ..model.linear_elasticity import LinearElasticityPDEDataT

from ..mesh import Mesh
from ..functionspace import functionspace 
from ..material import LinearElasticMaterial
from ..fem import BilinearForm
from ..fem import LinearElasticityIntegrator
from ..fem import ScalarMassIntegrator as MassIntegrator
from ..fem import DirichletBC
```

**领域****模块****与具体计算模型****开发注意**：在各领域模块（如 cem，csm，cfd 等）进行开发的时候，如果用到 FEALPy 的基础功能的时候，需要采用绝对导入；进行**具体计算模型（本质上量个小型的APP应用，保证用户单独拿出来也可以使用）**开发时，用到的 FEALPy 基础功能，也需要采用绝对导入，如：

```Python
from fealpy.backend import bm
from fealpy.typing import TensorLike
from fealpy.decorator import variantmethod
from fealpy.model import ComputationalModel
```

如果采用本模块内的功能的时候，采用相对导入，如：

```Python
from ..model import CSMModelManager
```

**示例如下**

```Python
from typing import Any, Optional, Union
from scipy.sparse.linalg import eigsh

from fealpy.backend import bm
from fealpy.typing import TensorLike
from fealpy.decorator import variantmethod
from fealpy.model import ComputationalModel

from fealpy.mesh import Mesh
from fealpy.functionspace import functionspace 

from fealpy.fem import (
    BilinearForm,
    LinearElasticityIntegrator, 
    DirichletBC
)
from fealpy.fem import ScalarMassIntegrator as MassIntegrator

from ..model import CSMModelManager
```

**导入代码长度控制**

单个 import 语句不要太长。如果导入的代码明显超过 80 个字符，应考虑换行：

```Python
from fealpy.fem import (
    BilinearForm,
    LinearElasticityIntegrator, 
    DirichletBC
)
```

### 2\.2 函数和类

1. 函数和类之间需要有 2 个空行将它们相互分离；

2. 单个类的方法之间、方法和类属性之间，需要有 1 个空行将它们相互分离；

3. 如果利用注释进行区域分割，则空行数量可以适当增加。

例如：

```Python
class TriangleMeshDataStructure(HomoMeshDataStructure):
    def __init__(*self*, *NN*: int, *cell*: Tensor):
        # 相关代码
        pass
    # 空行
    def construct(self):
        # 相关代码
        pass
# 空两行
# 空两行
class TriangleMesh(HomoMesh):
    local_edge = ...
    # 空行
    def __init__(self, *node*, *cell*):
        *self*.node = *node*
        *self*.ds = TriangleMeshDataStructure(*node*.shape[0], *cell*)
    # 空行
    def integrator(*self*, *q*: int, *etype*: Union[int, str]='cell',
                   *qtype*: str='legendre') -> Quadrature:
        # 相关代码
# 也是空两行
# 也是空两行
def some_function_here():
    pass
```

### 2\.3 单行长度

单行长度不要明显超过 80 个字符。

## （3）代码细节

1. 非行末的逗号后要有空格

```Python
mesh = QuadrangleMesh.from_box(**[-1, 1, -1, 1],nx=5,ny=5**) # 错误
space = LagrangeFESpace(**mesh, p=3**) # 正确
```

2. 赋值语句中的等号的两侧要有空格

```Python
A = D0@A@D0 + D1 # 正确
uh**=**spsolve(A, F) # 错误
```

3. 关键字参数相关的等号是否需要空格？

    1. 一般情况下，赋值、定义默认值都无需空格

    ```Python
    parser.add_argument("-n", ***type *****= int**) # 错误，有空格就太宽了
    grad_basis = space.grad_basis(bcs, **index=flag**) # 正确
    
    def basis(self, bcs, **index=_S**): ... # 正确
    def entity_barycenter(self, **index = _S**): ... # 错误
    ```

    2. 存在 typehint 的时候，默认值的等号两侧需要空格

    ```Python
    def index_add(a: Tensor, index, src, /, *, axis: **int = 0**, alpha=1): ... # 正确
    ```

4. 最外层的操作符两侧要有空格

```Python
x = x+pe[:x.size(0), None, :] # 错误，+ 号两侧要有空格
num = length // batch_size # 正确
```

5. 换行要缩进

```Python
a = bm.concat([
    cell1,
    cell2
], axis=0) # 对输入的列表换行

b = bm.stack(
    [x_data, y_data, z_data],
    axis=-1
) # 对stack函数的参数换行
```

6. 其它情形：以美观为目标自己调整即可。

## （4）关于 Type Hint

Typehint 即类型提示，可方便用户的编辑器提示函数、类等的参数类型、返回值类型。例如：

```Python
def boundary_interpolate(
    self,
    gd: Callable | int | float | TensorLike,
    uh: TensorLike | None = None,
    *,
    threshold: Callable | TensorLike | None = None,
    method=None
) -> TensorLike: ...
```

在这个函数声明中，参数名后跟一个冒号\+空格，再之后就是 type hint 的内容：它们分别表示

- gd 可以是函数、整型、浮点数或张量

- uh 可以是张量或 None

- threshold 可以是函数、张量或者 None

**要求：所有面向用户的接口，都需要 TypeHint。**

注：用于 FEALPy 内多后端张量的提示类型 TensorLike，可以通过 from fealpy\.backend import TensorLike 取得。

# **二、文件结构**

## （1）文件位置

- 源代码放入 fealpy/fealpy

- 测试放入 fealpy/test

- 算例放入 fealpy/example

这些文件夹下都有各种分类的子文件夹，根据所属研究领域放入即可。

## （2）文件命名

- 如果是用类，如几何代数多重网格解法器，文件命名格式为 gamg\_solver\.py ，类名为 GAMGSolver

- 如果是用函数，方法名字可以用缩写（如 cg， minres, gmres, lgmres 等）；可以用全称，如 jacobi, gauss\_seidel 等，相应文件名与方法名一致。

# 三、代码文档

## （1）注释示例（函数/方法）

```Python
def entity(self, etype: Union[int, str], index: Optional[Index] = None, *, default=_default) -> Tensor:
    """
    Retrieves entities within the mesh based on the specified type (`etype`) and index location (`index`), 
    returning a default value if the entity is not present.

    Parameters:
        etype(int | str): Defines the entity by its topology dimension (as an integer) or by name.
            Accepted names include 'cell', 'face', or 'edge'.
            Note that 'node' is unsupported in the current data structure.
            For polygonal meshes, 'cell_location' and 'face_location' can also be used, 
            in which scenario `index` operates on the flattened entity tensor.

        index(Index | None, optional): The index specifying the location of the entity.
            Specifies the entity's position using an integer, slice, or tensor.
            Defaults to `None` if not explicitly provided.

        default(Any): The value returned when the entity is not located within the mesh.
            Defaults to the module-level variable `_default`.

    Returns:
        Tensor: The entity located at the specified `index`, or the `default` value if the entity is absent.
    """
    if isinstance(etype, str):
        etype = entity_str2dim(self, etype)
    return entity_dim2tensor(self, etype, index=index, default=default)
```

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NmI3ZmRmYzRmZTBiMDA3MmMzN2ZmYjk5YjBkYjQwYWZfNTc4MzkyZmUzMjg0MTUzYmU0YzZkZjAzNmIwMjM2NTRfSUQ6NzUzMDkxMjQwNDkxODc0NzEzOV8xNzg5MTI3MzQ5OjE3ODkyMTM3NDlfVjM)

## （2）注释示例（类）

```Python
class QuadrangleMeshDataStructure(HomogeneousMesh):
    """
    A data structure class representing a quadrangle mesh, inheriting from the HomoMeshDataStructure.

    This class specifically handles quadrangle elements in a mesh, initializing with a given number of nodes (NN) and a 
    tensor defining cells. It sets up constant tensors for local edges, faces, a counter-clockwise order, and cell definitions,
    tailored for quadrilateral geometries. Upon instantiation, it calls the `construct` method to further initialize or 
    update any additional data structures necessary for the quadrangle mesh.

    Parameters:
        NN(int): The total number of nodes in the mesh.
    
        cell(Tensor): A tensor that defines the connectivity of cells within the mesh, specific to quadrangles.

    Attributes:
        localEdge(Tensor): A tensor defining the local edge connections within each quadrangle cell.
    
        localFace(Tensor): A tensor defining the local face connections within each quadrangle cell (though typically same as `localEdge` for quads).
    
        ccw(Tensor): A tensor providing a counter-clockwise ordering of indices for a standard quadrangle.
    
        localCell(Tensor): Defines how each local cell (quadrangle) is connected to the global node indexing.
    
    Methods:
        construct():Internal method to construct additional data or perform post-initialization steps for the quadrangle mesh.
    """
    def __init__(self, NN: int, cell: Tensor):
        ...
    def construct(self) -> None:
        ...
```

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZjIyMGI5MDdkM2QxOWI4ZWRmN2JlYWQzMDZmY2I1ZTNfZjk5OGZlZGM1OWRlYzM3OTI4NGJlZDg0NzFlM2I2NWRfSUQ6NzUzMDkxMjQwMTMwODc0NTc1Nl8xNzg5MTI3MzQ5OjE3ODkyMTM3NDlfVjM)

## （3）类的字符串表示规范

为了提高代码的可读性和调试效率，所有主要类都应实现 `__str__` 方法，提供清晰、格式化的对象信息输出。

以材料类 `fealpy/fealpy/material/elastic_material.py` 为例：

```Python
class LinearElasticMaterial(ElasticMaterial):
    ......
    def __str__(self) -> str:
        """Return a nicely formatted, multi-line summary of the material."""
        return (
            f"Material '{self.name}':\n"
            f"  E (Young's modulus):      {self.E:.3g}\n"
            f"  ν (Poisson's ratio):      {self.nu:.3g}\n"
            f"  λ (Lame's first param):   {self.lam:.3g}\n"
            f"  μ (Shear modulus):        {self.mu:.3g}\n"
            f"  ρ (Density):              {self.rho:.3g}\n"
            f"  Hypothesis:               {self.hypo}\n"
            f"  Device:                   {self.device}"
        )
    ......
```

使用方式如下：

```Python
marterial = LinearElasticMaterial()
self.logger.info(material)
```

# 四、协作规范

## （1）draft/xx 分支中的 Commit 要求

### Commit 内容

- 若功能尚未完成，但需要提交中间进展，可以使用 `WIP`（Work In Progress）标记。

- 在 draft/xx 分支中，每个 commit 应表示一个功能的进展。

- **`WIP`**** 提交仅在 draft/xx 分支中有效，且只用于中间开发阶段，****最终功能完成时**

### WIP Commit 的具体要求

所有的 WIP Commit 信息都要遵守以下格式：

```Plain Text
WIP(模块名): 描述
// 空行
更详细的描述，可选
```

例如：

```Python
WIP(fem): 在 scalar_source_integrator 添加等参有限元积分子组装功能
```

### 功能完成后 commit 的具体要求

完成这个功能的开发后，所有的 commit 信息都要遵守以下格式：

```Plain Text
类型(模块名): 描述
// 空行
更详细的描述，可选
```

例如

```Plain Text
feat(backend): add the `vmap` function for NumPy backend.
```

**类型**：

- `feat`: 新功能（对应minor版本升级）

- `fix`: bug修复（对应patch版本升级）

- `refactor`: 重构代码（不改变外部行为）

- `perf`: 性能优化

- `test`: 测试相关

- `docs`: 文档变更

- `chore`: 构建/配置变更

## （2）开发中的注意事项

1. 大家在各自项目分支下开发新功能时，可能会需要 develop 中的新功能，大家只需要把上游的 develop 分支拉取到本地 develop 分支，然后把  draft/xx 分支 rebase 到 develop 分支。

# 五、审查规则

维护者审查 Checklist

1. 完整性验证：

    - PR描述是否包含影响范围评估

    - 是否附带必要的测试报告

    - 文档更新是否同步完成

2. 代码健康度：

    - SonarQube扫描结果（0新增异味）

    - 测试覆盖率变动趋势

    - Linter规则通过情况

3. 提交记录质量：

    - Commit是否遵循原子性原则

    - Rebase操作是否合理（禁止无意义的merge commit）

    - 敏感信息过滤检查

# 六、model 模块算例数据开发规范

## （1）PDE 模型编写完整性要求

1. 在对应的PDE模块中添加算例时需要编写类注释，包括此PDE的真解、源项、求解区域、参考文献（如果有），下为某个2维Helmholtz方程的算例注释示例：

    ```Python
    """
        2D Helmholtz problem with complex Robin (impedance-type) boundary condition:
    
            -Δu(x, y) - k^2·u(x, y) = 0,       (x, y) ∈ (0, 1) x (0, 1)
               ∂u/∂n + i·k·u = g(x, y),        on ∂Ω
    
        Exact solution:
    
            u(x, y) = exp(i·β·k·y) * exp(-k·sqrt(β² - 1)·(x + 1))
    
        This represents an evanescent wave propagating in the y-direction,
        and exponentially decaying in the x-direction.
    
        Parameters:
            k : wave number (float)
            beta : dimensionless propagation parameter (β > 1)
    
        Source: 
            https://www.sciencedirect.com/science/article/pii/S0045794917302602#e0010
        """
    ```

2. 在编写PDE类的过程中要尽量根据协议中的接口实现完整功能，包括真解、源项、求解区域、边界条件等。

3. 在编写PDE类的过程中，要根据求解区域，继承model\.mesher模块下的网格生成基类。



## （2）PDE 模型编写规范性要求

1. 命名格式要求：PDE程序文件的命名为exp\+4位数字\.py，按照从旧到新的顺序排列，比如，某一类 PDE 中已经有了两个 PDE，则各自的程序文件名为 exp0001\.py、exp0002\.py，后续新开发的 PDE 文件命名为 exp0003\.py ；相应地， PDE 类名为Exp\+4位数字，这三个PDE的类名分别为 Exp0001、Exp0002、Exp0003。

2. 添加新的 PDE 模型后，同时要在对应 PDE 类型模块中的 \_\_init\_\_\.py 文件中的 DATA\_TABLE 增加相应的键值对。

3. 要增加新的方程类型，在 model\_manager\.py 文件的类属性` _registry`  中新增键值对，将方程类型名称映射到模块导入路径，这样才能通过 `PDE``Model``Manager` 管理与调用。

4. 在model中增加新的PDE类型模块时，\_\_init\_\_\.py 文件中的 DATA\_TABLE 的命名不能修改。

5. PDE 模型文件用相对导入进行开发。

6. PDE的注释与代码实现要一致，不能出现注释中求解区域为$[0,1]\times[0,1] $，代码中编写的求解区域为$[-1,1]\times[-1,1] $的错误。

7. 在注释中描述 PDE 的数学形式时，不能直接拷贝 latex 公式，比如$\mu$不要写成\\mu，而是写成μ，尽量用 AI 修正自己的注释，让数学式子简单明了。

8. PDE 模型的 \_\_init\_\_  函数中只包含与 PDE 本身相关的内容，至于网格剖分规模等参数不要写在其中。

9. 如果 PDE 模型可以在外部传入参数，则在  \_\_init\_\_  函数增加类型为字典的参数 options，并赋空值，用字典的 get 函数给参数赋默认值，不需要用户传参时，参数 options 不要写；

    1. 示例，如果 PDE 中有一个用户可以自由调控的参数k，且默认为 1\.0，则 PDE 的 \_\_init\_\_\(\) 函数编写格式如下：

    ```Python
    def __init__(self, options: dict = {}):
            self.box = [-0.5, 0.5, -0.5, 0.5]
            super().__init__(box=self.box)
            self.k = options.get('k', 1.0)
    ```

    2. 如果需要修改 k 为 10，则对应的调用方式为：

    `pde = PDEDataManager('helmholtz').get_example(1 , k=10)`

10. 开发后端用一律使用 bm，不能出现 np 或者 torch。

11. 在所有需要用到坐标运算的函数前都加上 @cartesian 装饰子，示例：

    ```Python
    def domain(self) -> Sequence[float]:
        
        @cartesian
        def solution(self, p: TensorLike) -> TensorLike:
        
        @cartesian
        def gradient(self, p: TensorLike) -> TensorLike:
        
    ```

12. 如果源项、梯度计算式较为复杂，要调用 ~~scipy~~ sympy进行计算，尽量不要写太长的计算式子。

## （3）PDE 模型编写需求性要求

1. 如果有新的新的方程类型需要增加，并且接口协议不明确时，要及时、主动找老师讨论，确定后续的开发规范。

2. 在某一类型的 PDE 中，可能会有特殊的、接口与协议中不一致的 PDE ，也需要及时、主动找老师讨论，确定编写规范。

3. 当目前的网格生成基类不能满足新开发的pde的需求时，要及时、主动与网格组进行讨论，对 mesher 模块进行后续完善。

## （4）PDE 模型接口统一参数管理规范

所有计算模型所需的参数（材料参数、几何参数、优化参数等）应通过统一的 PDE 接口获取，确保参数管理的一致性和可维护性。

以线弹性模型基类为例（`fealpy/fealpy/model/linear_elasticity/__init__.py/`），需要包含材料参数：

```Python
class LinearElasticityPDEDataProtocol(Protocol):
    ......
    
    def geo_dimension(self) -> int: ...
    def domain(self) -> Sequence[float]: ...

    # --- Material properties ---
    material: LinearElasticMaterial 
    
    ......
```

以线弹性特征值问题有限元方法计算模型为例（`fealpy/fealpy/fem/linear_elasticity_eigen_lfem_model.py`），先设置 PDE，然后根据需要设置各类参数：

```Python
class LinearElasticityEigenLFEMModel(ComputationalModel):
    ......
    
    def set_pde(self, pde: Union[LinearElasticityPDEDataT, int] = 1) -> None:
        if isinstance(pde, int):
            self.pde = PDEModelManager("linear_elasticity").get_example(1)
        else:
            self.pde = pde
        
        self.logger.info(self.pde)
        self.logger.info(self.pde.material)

        
    ......
```

几何参数和优化参数采取类似的方法定义和调用。




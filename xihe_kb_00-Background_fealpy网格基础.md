# xihe\_kb\_00\-Background\_fealpy网格基础

# 一、网格简介

## （1）**网格(mesh)的概念**

- **网格**一般由很多 **节点(node)** 以一定方式连接成的 **边(edge)、面(face)、单元(cell)** 形成。

- **网格**是一种特殊的数据结构，它常用于空间的表示、可视化或物理建模。

网格是一种用于描述空间的离散表达形式，同时也是一类特殊的数据结构，广泛应用于空间表征、几何可视化与数值建模。连续的空间区域本身无法直接开展数值运算，网格的核心思想就是离散化：把完整、连续的区域切分成大量形状简单、互不重叠的小单元。通过这些单元、单元顶点（节点）以及相互之间的连接关系，近似描述原本连续的空间。

- 在偏微分方程数值计算程序设计中，**网格是最核心的数据结构**，是实现所有数值离散方法的基础。

网格的质量直接决定了数值模拟的准确性、稳定性和计算效率。

## **（2）网格的分类**

网格最基本的分类方式是将其分**结构网格**和**非结构网格**，这两种类型的根本区别在于其拓扑结构，即节点和单元之间的连接关系。同时，我们还可以发挥不同网格类型的优点，构造混合网格。

根据网格形状的不同，可以分为三角形网格、多边形网格，四面体网格、多面体网格等。

按离散几何的拓扑维度，可以分为平面网格、曲面网格、实体网格。

| <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%209.png?raw=true" width="200"/><br><small style="color:#faf8f8">结构三角形网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%205.png?raw=true" width="200"/><br><small style="color:#faf8f8">结构多边形网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/%E7%BD%91%E6%A0%BC%E7%9A%84%E5%88%86%E7%B1%BB.png?raw=true" width="200"/><br><small style="color:#faf8f8">结构六面体网格</small> |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%204.png?raw=true" width="200"/><br><small style="color:#faf8f8">非结构三角形网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%202.png?raw=true" width="200"/><br><small style="color:#faf8f8">非结构多边形网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image.png?raw=true" width="200"/><br><small style="color:#faf8f8">混合网格</small> |
| <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%207.png?raw=true" width="200"/><br><small style="color:#faf8f8">平面网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/%E5%9B%BE%E7%89%872.png?raw=true" width="185"/><br><small style="color:#faf8f8">曲面网格</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/%E5%9B%BE%E7%89%873.png?raw=true" width="185"/><br><small style="color:#faf8f8">实体网格</small> |

# 二、FEALPy 中的网格数据结构

## （1）FEALPy 网格模块设计目标

## （2）网格相关术语约定

<div>
    <table>
  <thead>
    <tr>
      <th>分类</th>
      <th>符号 / 术语</th>
      <th>名称</th>
      <th>维数 / 释义</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="4">拓扑实体(entity)</td>
      <td>node</td>
      <td>节点</td>
      <td>拓扑维数 0</td>
    </tr>
    <tr>
      <td>edge</td>
      <td>边</td>
      <td>拓扑维数 1</td>
    </tr>
    <tr>
      <td>face</td>
      <td>面</td>
      <td>次高维拓扑实体</td>
    </tr>
    <tr>
      <td>cell</td>
      <td>单元</td>
      <td>最高维拓扑实体</td>
    </tr>
    <tr>
      <td rowspan="5">统计变量</td>
      <td>NN</td>
      <td>节点数量</td>
      <td>Number of Nodes</td>
    </tr>
    <tr>
      <td>NE</td>
      <td>边数量</td>
      <td>Number of Edges</td>
    </tr>
    <tr>
      <td>NF</td>
      <td>面数量</td>
      <td>Number of Faces</td>
    </tr>
    <tr>
      <td>NC</td>
      <td>单元数量</td>
      <td>Number of Cells</td>
    </tr>
    <tr>
      <td>NVC</td>
      <td>单元顶点数</td>
      <td>Vertices per Cell</td>
    </tr>
    <tr>
      <td rowspan="2">维度参数</td>
      <td>GD</td>
      <td>几何维数</td>
      <td>Geometric Dimension</td>
    </tr>
    <tr>
      <td>TD</td>
      <td>拓扑维数</td>
      <td>Topological Dimension</td>
    </tr>
  </tbody>
</table>



> 最高拓扑维数为 2 时，`edge` 和 `face` 指代同一类实体。

| <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/%E5%9B%BE%E7%89%875.png?raw=true" width="200"/><br><small style="font-size:12px;color:#faf8f8">最高拓扑维数为2</small> | <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/%E5%9B%BE%E7%89%876.png?raw=true" width="200"/><br><small style="font-size:12px;color:#faf8f8">最高拓扑维数为3</small> |
| :----------------------------------------------------------: | :----------------------------------------------------------: |

## （3）基于数组表示的网格数据结构

FEALPy 中核心网格数据结构是用**数组**表示的：**`node`**为**节点坐标数组**，**`cell`**为**单元顶点数组**，**`edge`**为**边数组**，**`face`**为**面数组**。

### `node`、`cell`、`edge`、`face`

```python
node = bm.array([
    [0.0, 0.0],  #0
    [0.0, 0.5],  #1
    [0.0, 1.0],  #2
    [0.5, 0.0],  #3
    [0.5, 0.5],  #4
    [0.5, 1.0],  #5
    [1.0, 0.0],  #6
    [1.0, 0.5],  #7
    [1.0, 1.0],  #8
], dtype=bm.float64)
```

```python
cell = bm.array([
    [3, 4, 0],  #0
    [6, 7, 3],  #1
    [4, 5, 1],  #2
    [7, 8, 4],  #3
    [1, 0, 4],  #4
    [4, 3, 7],  #5
    [2, 1, 5],  #6
    [5, 4, 8],  #7
],
dtype=bm.int32)
```

```python
edge = bm.array([
    [1, 0],  #0
    [0, 3],  #1
    [4, 0],  #2
    [2, 1],  #3
    [1, 4],  #4
    [5, 1],  #5
    [5, 2],  #6
    [3, 4],  #7
    [3, 6],  #8
    [7, 3],  #9
    [4, 5],  #10
    [4, 7],  #11
    [8, 4],  #12
    [8, 5],  #13
    [6, 7],  #14
    [7, 8],  #15
], dtype=bm.int32)
```

<div align="center">
    <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/e3298410cb3871265910dd65b34d2993.png?raw=true" width="350" />
</div>

1. `node[i]`中的 i 对应于红色点的序号 i，例如红色序号0对应于`node[0]=[0.0, 0.0]`，红色序号3对应于`node[3]=[0.5, 0.0]` ；

2. `cell[i]`中的 i 对应于蓝色点的序号 i，例如蓝色序号0对应于`cell[0]=[3, 4, 0]`\(即由节点序号分别为3，4，0的节点构成的cell\)，蓝色序号3对应于`cell[0]=[7, 8, 4]`\(即由节点序号分别为7，8，4的节点构成的cell\)；

3. `edge[i]`中的 i 对应于绿色点的序号 i，例如绿色序号0对应于`edge[0]=[1, 0]`\(即由节点序号分别为1，0的节点构成的edge\)，绿色序号3对应于`edge[3]=[2, 1]`\(即由节点序号分别为2，1的节点构成的edge\)；

4. 由于最高拓扑维数为 2 ，故`edge` 和 `face` 指代同一类实体。

不难发现，除了`node`节点坐标数组中的元素的顺序，其节点坐标会随之改变。但`cell`、`edge`、`face`中数组的元素的顺序即使改变，它仍然是由这几个节点构成的，不会改变其形状，也不会改变每个cell的序号。例如：`cell[0]=[3, 4, 0]`，将其改成`cell[0]=[3, 0, 4]`，**这有什么区别？**

### 网格实体的全局和局部编号

先统一基础前提，网格实体：`node`、`cell`、`edge`、`face`所有实体都存在两套编号体系：

1. 全局编号（Global Index）

2. 局部编号（Local Index）

> 之前说的序号均为全局编号
> 

#### 全局编号

- 在整个计算域、整张网格范围内，给每一个实体分配唯一 ID

- 作用是跨单元寻址、全局拓扑关联

- 作用范围：整张网格，唯一、固定

- 存储位置：`node`/ `cell`/ `edge`/ `face` 数组的行下标

#### 局部编号

- 只在某一个单元内部生效的临时编号，脱离当前单元就失去意义。 每个单元内部，独立对自己拥有的顶点、边、面重新从 0 开始编号。

- 作用范围：仅限单个单元内部，不跨单元；不同单元局部编号相互独立，局部编号是单元内部的顺序规则。

- 举例：以 [二、（3）](https://wnesm678i4.feishu.cn/wiki/IZJFwou0JiYf1gkUXnecj4ZOnYe#share-JnkPd3OiWoWM2LxzfVbc6jlcnoh)为例，设单元全局编号 i：cell[i]=\[ $v_{i0}$，  $v_{i1}$， $v_{i2}$]，该单元由全局编号为 $v_{i0}$、 $v_{i1}$、 $v_{i2}$ 的三个节点构成。

    - **规定：（仅限于本文档）**
    - 全局编号为 $v_{ij}$ 的 **node** 在全局编号为 i 的 cell 内的**局部编号**为 j ;
      
    - 全局编号为 i 的 cell 内的 **edge 的局部编号**：该cell内
      
        - 【局部编号为 1 的node→局部编号为 2 的node】表示 局部编号为 0 的edge；
        
        - 【局部编号为 2 的node→局部编号为 0 的node】表示 局部编号为 1 的edge；
        
        - 【局部编号为 0 的node→局部编号为 1 的node】表示 局部编号为 2 的edge。
    
- 举例：`cell[0]=[3, 4, 0]`，该单元内
  
    - 全局编号为3的node的局部编号为 0 ；全局编号为4的node的局部编号为 1 ；全局编号为0的node的局部编号为 2 。
    
    - 局部编号为 1 的 edge 为 【全局编号为 4 的 node →全局编号为 0 的 node】以此类推

> 这里就可以片面的回答一下上面问的一个问题，若将`cell[0]=[3, 4, 0]`改成`cell[0]=[3, 0, 4]`，noda以及edge的局部编号会发生改变。
> 

### 网格实体之间的关系

#### face2cell

同样是拿上面的例子。

```python
face2cell = bm.array([
    [4, 4, 2, 2], #0
    [0, 0, 1, 1], #1
    [0, 4, 0, 0], #2
    [6, 6, 2, 2], #3
    [2, 4, 1, 1], #4
    [2, 6, 0, 0], #5
    [6, 6, 1, 1], #6
    [0, 5, 2, 2], #7
    [1, 1, 1, 1], #8
    [1, 5, 0, 0], #9
    [2, 7, 2, 2], #10
    [3, 5, 1, 1], #11
    [3, 7, 0, 0], #12
    [7, 7, 1, 1], #13
    [1, 1, 2, 2], #14
    [3, 3, 2, 2], #15
], dtype=bm.int32)
```

`face2cell`面和单元的邻接关系，`face2cell[i]=[cell1, cell2, local_face1, local_face2]`表示的是全局编号为 i 的 face 与相邻 cell 的关系。

这行数据的具体含义是：

- `cell1`：与该面相邻的第一个单元的全局编号。

- `cell2`：与该面相邻的第二个单元的全局编号。

> 1. 如果该 face 位于计算域的边界，没有第二个相邻单元，则`cell2`=`cell1`；
> 
> 2. 若不是，则会出现两个不同全局编号的 cell ，这时就需要用到** face 的朝向** 
> 
>     1. 以`face[9]`为例
> 
>     - 在本文情况下，`face`=`edge`，`face[9]=[7 , 3]`正向朝向为 7 到 3，负向朝向为 3 到 7
> 
>     - 该 face 在哪个 cell 里面是正向朝向的，那么哪个就是 `cell1`（右边）
> 
>     - 该 face 在哪个 cell 里面是负向朝向的，那么哪个就是 `cell2`（左边）
> 

- `local_face1`：在 `cell1` 这个单元中，该面的局部编号。

- `local_face2`：在 `cell2` 这个单元中，该面的局部编号。如果该面位于计算域的边界，没有第二个相邻单元，则数值等于`local_face1`。

举例：

- `face2cell[0]=[4, 4, 2, 2]`
由于全局编号为 0 的 face(`face[0]=[1, 0]`) 位于网格边界，故`cell1`=`cell2`且`local_face1`=`local_face2`。
该 face 相邻的是的全局编号为 4 的 cell(`cell[4]=[1, 0, 4]`) ，从而`cell1`=`cell2`=4；
根据本文局部编号的规定，该 face 在该 cell 的局部编号为 2 ，从而`local_face1`=`local_face2`=2。

- `face2cell[9]=[1, 5, 0, 0]`
与全局编号为 9 的 face(`face[9]=[7, 3]`) 相邻的两个 cell(`cell[1]=[6, 7, 3]`、`cell[5]=[4, 3, 7]`\)，故 `cell1`=1，`cell2`=5；
该 face 在该 cell 的局部编号均为 0 ，故`local_face1`=`local_face2`=0

#### cell2cell

`cell2cell`单元和单元的邻接关系，存储了每个单元的邻接单元编号，若单元存在边界边，则该边对应的邻接单元编号就存储该单元本身的编号。

- 举例：`cell2cell[0]`
全局编号为 0 的cell(`cell[0]=[3, 4, 0]`)相邻的两个 cell(`cell[4]=[1, 0, 4]`、`cell[5]=[4, 3, 7]`);

- `cell[0]`与`cell[4]`的共 edge 为`edge[2]=[4, 0]`，该 edge 在 `cell[0]` 的局部编号为 0；

- `cell[0]`与`cell[5]`的共 edge 为`edge[7]=[4, 3]`，该 edge 在 `cell[0]` 的局部编号为 1；

- 故`cell2cell[0]=[4, 5, 0]`

> 1. 为什么是三个元素？
>
>   因为该网格单元均为三角形，最多只有三个相邻单元。
>
> 2. 元素顺序怎么放？
>
>   三个位置依次对应：局部边 0、局部边 1、局部边 2；局部边顺序由单元顶点排列**规定**预先定义。
>

#### cell2edge

`cell2edge[i]`存储单元`cell[i]`的边的全局编号，元素顺序为按照边在该单元的局部编号排。

# 三、FEALPy 网格模块的使用方法

## （1）生成网格

举例，我们想要用三角形网格。 在网格模块中，可以直接导入所需网格类型。

```Python
from fealpy.mesh import TriangleMesh
```

使用 FEALPy 初始化网格对象有两种方式：

1. `mesh = TriangleMesh(node, cell) # 通过已有的 node 和 cell 初始化` 

2. `boxmesh = TriangleMesh.from_box([-1, 1, -1, 1], nx=5, ny=5) # 通过类方法构造特殊区域的网格` 

## （2）可视化网格

基于 **matplotlib** 的可视化分为可选的两个方面：

1. 绘制整个网格的背景图（`add_plot`）

2. 在图中画出网格实体的重心所在

```Python
from fealpy.mesh import TriangleMesh
from matplotlib import pyplot as plt
boxmesh = TriangleMesh.from_box([-1, 1, -1, 1], nx=5, ny=5) # 通过类方法构造特殊区域的网格
fig = plt.figure()
axes = fig.add_subplot(111)
boxmesh.add_plot(axes) # 画出网格背景
boxmesh.find_cell(axes, showindex=True) # 找到单元重心
plt.show()
```

<div align="center">
    <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%203.png?raw=true" width="350" />
</div>

## （3）基本信息获取

### 获取网格实体数组与计数

```Python
import matplotlib.pyplot as plt
from fealpy.mesh import TriangleMesh
mesh = TriangleMesh.from_box([0, 1, 0, 1], nx=1, ny=1)

node = mesh.entity('node') # (NN, GD)
edge = mesh.entity('edge') # (NE, 2)
face = mesh.entity('face') # (NF, 2)
cell = mesh.entity('cell') # (NC, 3)

NN = mesh.number_of_nodes()
NE = mesh.number_of_edges()
NF = mesh.number_of_faces()
NC = mesh.number_of_cells()

print("NN:", NN, "NE:", NE, "NF:", NF, "NC:", NC, sep=' ')
```

本例网格为：

<div align="center">
    <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%201.png?raw=true" width="350" />
</div>

```Python
node = [[0. 0.]
        [0. 1.]
        [1. 0.]
        [1. 1.]]

edge = [[1 0]
        [0 2]
        [3 0]
        [3 1]
        [2 3]]

face = [[1 0]
        [0 2]
        [3 0]
        [3 1]
        [2 3]]
 
cell = [[2 3 0]
        [1 0 3]]

NN: 4 NE: 5 NF: 5 NC: 2
```

### 获取网格实体重心 

对于三角形网格

- 单元的重心计算公式：假设一个三角形单元的三个顶点坐标分别为 $(x_1, y_1), (x_2, y_2), (x_3, y_3)$，则其重心坐标 $(G_x, G_y)$ 的计算公式为： $G_x = (x_1 + x_2 + x_3) / 3$, $\ G_y = (y_1 + y_2 + y_3) / 3$

- 边的重心计算公式：假设一条边的两个端点坐标为 $(x_1, y_1)$, $(x_2, y_2)$，则其重心坐标 $(G_x, G_y)$ 的计算公式为： $G_x = (x_1 + x_2) / 2,\ G_y = (y_1 + y_2) / 2$ 

```Python
bc = mesh.entity_barycenter('cell') # 单元的重心 (NC, GD)
be = mesh.entity_barycenter('edge') # 边的重心 (NE, GD)
print("bc:", bc, "be:", be)
```

本例网格的结果为：

```Python
bc: [[0.66666667 0.33333333]
     [0.33333333 0.66666667]] 
be: [[0.  0.5]
     [0.5 0. ]
     [0.5 0.5]
     [0.5 1. ]
     [1.  0.5]]
```

### 获取网格实体切向与法向

- **切向**（`mesh.edge_tangent()`）：切向是指沿着网格边本身的方向向量。对于条连接顶点 $v_i$ 和 $v_j$ 的边，其切向量通常计算为终点减去起点，即 $\vec t = v_j - v_i$

    - 输出的切向量通常是未归一化的（保留了边的实际长度信息）

- **法向**（`mesh.edge_normal()`）：法向是指垂直于边的方向向量。在二维平面中，通常通过将切向量顺时针旋转 90 度来得到法向量。如果切向量是 $(a,b)$，那么法向量通常是 $(b, -a)$

    - 输出的切向量通常是未归一化的（长度等于对应边的长度）

- **单位切向与单位法向**（`mesh.edge_unit_tangent()` / `mesh.edge_unit_normal()`）：这是将上述的切向量和法向量进行归一化处理后的结果，即除以自身的模长，使其长度变为 1。

```Python
t = mesh.edge_tangent() # 实体切向 (NE, 2)
n = mesh.edge_normal() # 实体法向 (NE, 2)

ut = mesh.edge_unit_tangent()
un = mesh.edge_unit_normal()
```

本例网格的结果为：

```Python
t = [[ 0. -1.]
     [ 1.  0.]
     [-1. -1.]
     [-1.  0.]
     [ 0.  1.]]
n = [[-1. -0.]
     [ 0. -1.]
     [-1.  1.]
     [ 0.  1.]
     [ 1. -0.]]
ut = [[ 0.         -1.        ]
      [ 1.          0.        ]
      [-0.70710678 -0.70710678]
      [-1.          0.        ]
      [ 0.          1.        ]]
un = [[-1.         -0.        ]
      [ 0.         -1.        ]
      [-0.70710678  0.70710678]
      [ 0.          1.        ]
      [ 1.         -0.        ]]
```

### 获取网格实体测度

- 边的测度：`mesh.entity_measure('edge')`

    - **含义**：指网格中每条边的**长度（Length）**

- 单元的测度：`mesh.entity_measure('cell')`

    - **含义**：指网格中每个单元（在二维中通常是三角形或四边形）的**面积（Area）**。

```Python
h = mesh.entity_measure('edge')
area = mesh.entity_measure('cell')
```

本例网格的结果为：

```Python
h = [1.         1.         1.41421356 1.         1.        ]
area = [0.5 0.5]
```

### 获取网格实体上的积分公式

在有限元分析（FEA）和计算几何中，网格实体上的积分公式通常指：构造用于数值积分的积分点和权重。下面的 `integrator` 就是用来生成这些积分公式的工具。

```Python
cqf = mesh.integrator(3, 'cell') # 单元上的 3 次积分公式
fqf = mesh.integrator(3, 'face') # 面（在 2D 中通常等价于 edge）上的 3 次积分公式
eqf = mesh.integrator(3, 'edge') # 边上的 3 次积分公式
```

### 获取网格实体的邻接关系

在网格处理（特别是有限元分析或计算几何库，如 PyMesh、MFEM、FEniCS 等）中，“邻接关系” 描述的是网格中不同几何实体（节点、边、面/单元）之间的连接或归属关系。简单来说，就是“谁和谁挨着”、“谁属于谁”。

- `mesh.edge_to_cell()` 

    - 返回的矩阵形状为 `(NE, 4)`

    - 每一行分别表示某一条边

    - 在某一行中，每一列分别为：朝向 1 的单元的全局编号、朝向 2 的单元的全局编号、该边在朝向 1 的单元中的局部编号、该边在朝向 2 的单元中的局部编号

- `mesh.cell_to_edge()` 

    - 返回的矩阵形状为 `(NC, 3)` 

    - 每一行表示某一个单元

    - 在某一行中，每一列分别为：该单元的第 0 条边的全局编号、第 1 条边的全局编号、第 2 条边的全局编号

- `mesh.node_to_node()` 

    - 返回的稀疏矩阵（通常为 CSR 格式）形状为 `(NN, NN)` 

    - 第 `i` 行表示节点 `i` 的邻接节点信息，第 `i` 行中非零元素的位置 `j` 表示节点 `i` 与节点 `j` 之间存在边相连

    - 通常是对称矩阵（无向图）

- `mesh.node_to_cell()` 

    - 返回的稀疏矩阵（通常为 CSR 格式）形状为 `(NN, NC)` 

    - 第 `i` 行表示节点 `i` 所属的单元信息，第 `i` 行中非零元素的位置 `j` 表示节点 `i` 属于第 `j` 个单元

- `mesh.cell_to_cell()` 

    - 返回的矩阵形状为 `(NC, K)` （其中 K 是每个单元的最大邻居数）

    - 每一行代表一个单元。

    - 每一列代表该单元的一个“邻居槽位”。

    - 值代表该槽位上邻居的全局单元编号。值为 0 在对应位置表示“该槽位为空，没有邻居”。

```Python
edge2cell = mesh.edge_to_cell() # 每条边属于哪些单元（cell），每一行为一条边，
cell2edge = mesh.cell_to_edge() # 每个单元包含哪些边
node2node = mesh.node_to_node() # 每个节点相邻（相连）的节点
node2cell = mesh.node_to_cell() # 每个节点属于哪些单元
cell2cell = mesh.cell_to_cell() # 每个单元相邻（共享边）的单元
```

这些方法返回的不是普通列表，而是**稀疏矩阵或张量结构**（如 CSR Tensor），用于表示“存在性”或“索引映射”。

本例网格的结果为：

```Python
edge2cell = [[1 1 2 2]
             [0 0 1 1]
             [0 1 0 0]
             [1 1 1 1]
             [0 0 2 2]]
cell2edge = [[2 1 4]
             [2 3 0]]
node2node = CSRTensor(crow=[ 0  3  5  7 10], col=[1 2 3 0 3 0 3 0 1 2], values=[ True  True  True  True  True  True  True  True  True  True], shape=(4, 4))
node2cell = CSRTensor(crow=[0 2 3 4 6], col=[0 1 1 0 0 1], values=[ True  True  True  True  True  True], shape=(4, 2))
cell2cell = [[1 0 0]
             [0 1 1]]
```

### 获取网格实体的边界标记

```Python
isBdNode = mesh.boundary_node_flag()
isBdEdge = mesh.boundary_edge_flag()
isBdFace = mesh.boundary_face_flag()
isBdCell = mesh.boundary_cell_flag()
nidx = mesh.boundary_node_index()
eidx = mesh.boundary_edge_index()
fidx = mesh.boundary_face_index()
cidx = mesh.boundary_cell_index()
```

- `isBdNode`：节点边界标记。`True` 表示该节点位于网格的边界上。

- `isBdEdge`：边边界标记。`True` 表示该边位于网格的边界上。

- `isBdFace`：面边界标记（在2D网格中，“面”就是三角形单元本身，但此处通常指单元的“边界面”；在3D中才是真正的面）。

- `isBdCell`：单元边界标记。True 表示该单元（三角形）至少有一个边位于整个区域的边界上。

- `nidx`：所有边界节点的索引列表。

- `eidx`：所有边界边的索引列表。

- `fidx`：所有边界面（或边界边）的索引列表。

- `cidx`：所有边界单元的索引列表。

本例网格的结果为：

```Python
isBdNode = [ True  True  True  True]
isBdEdge = [ True  True False  True  True]
isBdFace = [ True  True False  True  True]
isBdCell = [ True  True]
nidx = [0 1 2 3]
eidx = [0 1 3 4]
fidx = [0 1 3 4]
cidx = [0 1]
```

### 获取网格实体上的插值点

- 插值点的**全局编号**和**局部编号**

```Python
import matplotlib.pyplot as plt
from fealpy.mesh import TriangleMesh
mesh = TriangleMesh.from_box([0, 1, 0, 1], nx=1, ny=1)
p = 3
ipoint = mesh.interpolation_points(p) # p 次插值点的坐标
cell2ipoint = mesh.cell_to_ipoint(p)  # 建立“单元到插值点”的映射。它是一个二维数组，行对应单元，列对应该单元上的局部插值点，值是这些插值点在全局中的编号。
edge2ipoint = mesh.edge_to_ipoint(p) # 建立“边到插值点”的映射

print(ipoint)
print(cell2ipoint)
print(edge2ipoint)

np = mesh.number_of_local_ipoints(p)  # 计算单个单元上 p 次插值点的个数
NP = mesh.number_of_global_ipoints(p) # 计算整个网格上全局唯一的插值点总数
fig, axes= plt.subplots()
mesh.add_plot(axes)
mesh.find_node(axes, node=ipoint, showindex=True)
print('局部插值点个数：', np)
print('全局插值点个数：', NP)
plt.show()
```

本例网格的输出为：

```Python
[[1.         1.        ]
 [0.         0.66666667]
 [0.         0.33333333]
 [0.33333333 0.        ]
 [0.66666667 0.        ]
 [0.66666667 0.66666667]
 [0.33333333 0.33333333]
 [0.66666667 1.        ]
 [0.33333333 1.        ]
 [1.         0.33333333]
 [1.         0.66666667]
 [0.66666667 0.33333333]
 [0.33333333 0.66666667]]
[[ 2 12  7 13 14  6  3  8  9  0]
 [ 1  4 11  5 15 10  0  9  8  3]]
[[ 1  4  5  0]
 [ 0  6  7  2]
 [ 3  8  9  0]
 [ 3 10 11  1]
 [ 2 12 13  3]]
局部插值点个数： 10
全局插值点个数： 16
```

<div align="center">
    <img src="https://github.com/You-yj/markdown_photo/blob/main/fealpy%E7%BD%91%E6%A0%BC%E5%9F%BA%E7%A1%80_photo/image%208.png?raw=true" width="350" />
</div>



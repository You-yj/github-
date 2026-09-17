# 双永磁体三维静磁算例 · 三站讲解

两块沿 +z 平行充磁的长方体永磁体，上磁体沿 x 平移 d = 0..30 mm，
用**磁标势有限元**求磁力，对标 **Akoun–Yonnet 解析解**与 **ANSYS EMFT 参考**。

三步走，三站数值**逐位一致**：

| 阶段 | 目录 | 内容 |
|---|---|---|
| ① 独立算例基线 | `最初程序/` | 558 行单文件算例（Gmsh 共形网格 + 磁标势 FEM + Maxwell 应力），对标解析解与 ANSYS |
| ② 算例工程化分块 | `初步分块/` | `magnetostatic/` 包：geometry / materials / mesh / pde / solver / postprocess，16 项测试 + 端到端回归 |
| ③ FEALPy 通用化集成 | `初步集成/` | 材料进 `fealpy.material`、网格进 `fealpy.mesher`、模型归口 `fealpy.cem.fem`（fealpy 源码见《fealpy集成修改说明.md》的修改清单） |

## 查看入口

- **入口页**：`index.html`（三站导航）
- 每个阶段都有两个版本：
  - **演示版**（`*_简洁版.html`）：点击翻页的幻灯片，适合汇报；
  - **详细版**（`*_详细版.html`）：左文右码的滚动文档，代码带真实行号，可折叠/复制/深色模式。
- 另有专题页 `初步集成/集成通用性.html`：三磁体 + 软磁通用性实测与边界表。

所有页面**离线可用**：公式渲染（MathJax）与图片均本地化，无需联网。

## 在线查看（GitHub Pages）

1. 把本目录内容上传到 GitHub 仓库（根目录保持 `index.html`）；
2. 仓库 **Settings → Pages** → Source 选 **Deploy from a branch**，分支选 `main`，目录选 `/ (root)`，保存；
3. 稍等片刻，访问 `https://<用户名>.github.io/<仓库名>/` 即可；
4. 老师点开入口页后，各页面间的跳转链接均为相对路径，可直接点入。

> 说明：目录与文件名含中文，GitHub Pages 会自动做 URL 编码，在线浏览不受影响；
> Windows 本地 `git clone` 若出现中文乱码，属系统编码问题，不影响网页浏览。

## 本地查看

直接双击任意 `.html` 文件用浏览器打开即可（推荐 Chrome / Edge / Firefox）。
无需安装任何依赖；各页面的结果图与公式都随文件打包。

## 复现数值与测试

```bash
# 阶段②：分块程序测试（16 项，含与最初程序的网格逐位一致回归）
cd 初步分块
python -m pytest test_magnetostatic.py test_comparison.py test_regression.py -q

# 阶段③：算例端测试（19 项）
cd ../初步集成
python -m pytest test_comparison.py test_double_magnet_cli.py test_benchmark_regression.py -q

# 阶段③：fealpy 静磁测试（68 项）——需先按《fealpy集成修改说明.md》把修改应用到 fealpy 检出
PYTHONPATH=fealpy python -m pytest \
    fealpy/tests/material fealpy/tests/mesher/test_box_region_mesher.py \
    fealpy/tests/cem/fem -q
```

环境依赖：Python 3.11+、fealpy（develop）、gmsh、numpy、scipy、pyamg（可选，缺失时回退无预条件 CG）、matplotlib。

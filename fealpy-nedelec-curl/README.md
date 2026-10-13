# 第一类 Nédélec 棱元课件

三页全屏交互版见 [`index-three-act.html`](index-three-act.html)，配套样式和动画逻辑分别在 `three-act.css`、`three-act.js`。它按照 [`三页交互课件设计方案.md`](三页交互课件设计方案.md) 展示封面、知识主线与 FEALPy 实现；底部时间线可播放、暂停、拖动并跳到每段起点或终点。原有 `index.html` 与 `index-draft.html` 保留供对照。

打开 `index.html` 即可离线浏览.公式使用内嵌字体的 LaTeX 排版；点击公式旁的“ LaTeX ”可查看源码.另有可独立编译的 `formulas.tex`.

图例由 Matplotlib 绘制，源代码在 `make_figures.py` 与 `make_more_figures.py`；`figures/` 同时保留可编辑 SVG 与 PNG.网格、数值积分点和稀疏矩阵图调用与算例相同的 FEALPy 接口.

重新生成图例并写入单文件课件：

```bash
python3 make_figures.py
python3 make_more_figures.py
python3 embed_figures.py
python3 embed_figures.py --check
```

课程数值算例与逐步编程教程位于 `../../../examples/fealpy-nedelec-curl/`：

- `run.py`：可直接执行的 FEALPy 实现；
- `README.md`：按方程、网格、空间、组装、边界、求解和误差验证讲解程序；
- `results.json`：已有网格加密运行记录。

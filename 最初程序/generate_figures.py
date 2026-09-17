#!/usr/bin/env python3
"""运行最初程序的完整扫描（p=1 与 p=2，d=0..30 mm），并把结果图存盘。

等价于 `python double_magnet_benchmark.py --scan`，只是把
`plt.show()` 替换为 savefig，便于无显示环境下保存图片。
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from double_magnet_benchmark import DoubleMagnetBenchmark  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "images"
OUT_DIR.mkdir(exist_ok=True)

_state = {"fig_no": 0}


def _save_show():
    _state["fig_no"] += 1
    if _state["fig_no"] == 1:
        path = OUT_DIR / "force_displacement.png"
    elif _state["fig_no"] == 2:
        path = OUT_DIR / "force_error.png"
    else:
        path = OUT_DIR / f"figure_{_state['fig_no']}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[saved] {path}", flush=True)


plt.show = _save_show

if __name__ == "__main__":
    DoubleMagnetBenchmark.run_scan(None)
    print("[done]", flush=True)

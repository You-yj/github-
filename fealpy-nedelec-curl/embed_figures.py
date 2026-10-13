"""Refresh or check the self-contained PNG images embedded in index.html.

Run ``python3 embed_figures.py --check`` after generating figures. Without
``--check``, this script updates the embedded images from figures/*.png.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
HTML = HERE / "index.html"
FIGURES = HERE / "figures"
PATTERN = re.combm.pile(
    r'(<img\s+alt="[^"]*"\s+data-figure="([^"]+)"\s+'
    r'src="data:image/png;base64,)([^"]+)(">)'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    args = parser.parse_args()

    html = HTML.read_text(encoding="utf-8")
    changed = []
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        prefix, name, embedded, suffix = match.groups()
        if Path(name).name != name:
            raise ValueError(f"Unsafe figure name: {name}")
        image = FIGURES / name
        fresh = base64.b64encode(image.read_bytes()).decode("ascii")
        count += 1
        if embedded != fresh:
            changed.append(name)
        return prefix + fresh + suffix

    updated = PATTERN.sub(replace, html)
    if count == 0:
        raise RuntimeError("No embedded figures with data-figure attributes")
    if args.check:
        if changed:
            raise SystemExit("Outdated embedded figures: " + ", ".join(changed))
        print(f"All {count} embedded figures match their PNG sources")
    else:
        HTML.write_text(updated, encoding="utf-8")
        print(f"Refreshed {count} embedded figures ({len(changed)} changed)")


if __name__ == "__main__":
    main()

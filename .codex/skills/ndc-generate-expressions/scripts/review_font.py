"""Portable font discovery for diagnostic review labels; no bundled system paths."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import ImageFont


def load_review_font(size: int) -> ImageFont.ImageFont:
    candidates: list[str | Path] = []
    if os.environ.get("NDC_REVIEW_FONT"):
        candidates.append(Path(os.environ["NDC_REVIEW_FONT"]))
    system_root = os.environ.get("WINDIR") or os.environ.get("SystemRoot")
    if system_root:
        candidates.extend(Path(system_root) / "Fonts" / name for name in ("msyh.ttc", "arial.ttf"))
    candidates.extend(("NotoSansCJK-Regular.ttc", "DejaVuSans.ttf"))
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), size=size)
        except OSError:
            continue
    return ImageFont.load_default()

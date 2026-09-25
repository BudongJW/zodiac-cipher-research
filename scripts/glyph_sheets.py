"""方向 A：由公有领域扫描件生成字形对比图（data/glyphs/）。

扫描件（Wikimedia Commons，公有领域），需先下载到 external/scans/：
    https://upload.wikimedia.org/wikipedia/commons/3/3b/Zodiac-name.gif            （1970-04-20 信，Z13）
    https://upload.wikimedia.org/wikipedia/commons/3/33/June_26_1970_Zodiac_letter.jpg  （1970-06-26 信与地图，Z32）

用法：python scripts/glyph_sheets.py（需要 Pillow）
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from zkc.console import utf8_stdio  # noqa: E402

SCANS = ROOT / "external" / "scans"
OUT = ROOT / "data" / "glyphs"

# Z32：各位置字形中心的横坐标（原图像素），第 1 行 y = 925–962，第 2 行 y = 960–998
Z32_X = {1: 125, 2: 161, 3: 194, 4: 227, 5: 262, 6: 297, 7: 330, 8: 361, 9: 396, 10: 432, 11: 466,
         12: 502, 13: 535, 14: 569, 15: 605, 16: 636, 17: 674, 18: 124, 19: 160, 20: 197, 21: 231,
         22: 262, 23: 297, 24: 330, 25: 364, 26: 395, 27: 434, 28: 466, 29: 501, 30: 536, 31: 570,
         32: 604}
Z13_LINE = (5, 160, 480, 205)  # Z13 密文行在 Zodiac-name.gif 中的范围


def sheet(tiles: list[tuple[int, Image.Image]], path: Path) -> None:
    w = sum(t.width + 20 for _, t in tiles)
    h = max(t.height for _, t in tiles) + 30
    out = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(out)
    x = 0
    for pos, tile in tiles:
        out.paste(tile.convert("RGB"), (x, 25))
        draw.text((x + 4, 4), f"pos {pos}", fill="red")
        x += tile.width + 20
    out.save(path)


def z32_glyph(im: Image.Image, pos: int, scale: int = 6) -> Image.Image:
    y0, y1 = (925, 962) if pos <= 17 else (960, 998)
    g = im.crop((Z32_X[pos] - 19, y0, Z32_X[pos] + 19, y1))
    return g.resize((g.width * scale, g.height * scale), Image.LANCZOS)


def z13_glyphs(im: Image.Image, scale: int = 8) -> list[Image.Image]:
    """按列投影自动切分 Z13 的 13 个字形。"""
    x0, y0, x1, y1 = Z13_LINE
    dark = (np.array(im.crop(Z13_LINE)) < 128).any(axis=0)
    segs, start = [], None
    for x, v in enumerate(dark):
        if v and start is None:
            start = x
        if not v and start is not None:
            segs.append([start, x])
            start = None
    if start is not None:
        segs.append([start, len(dark)])
    merged: list[list[int]] = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 3:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    if len(merged) != 13:
        raise RuntimeError(f"切分出 {len(merged)} 个字形，预期 13 个")
    tiles = []
    for a, b in merged:
        g = im.crop((x0 + a - 3, y0, x0 + b + 3, y1))
        tiles.append(g.resize((g.width * scale, g.height * scale), Image.NEAREST))
    return tiles


def main() -> None:
    utf8_stdio()
    OUT.mkdir(parents=True, exist_ok=True)
    z32 = Image.open(SCANS / "June_26_1970_Zodiac_letter.jpg").convert("RGB")
    sheet([(p, z32_glyph(z32, p)) for p in range(1, 18)], OUT / "z32_row1_tiles.png")
    sheet([(p, z32_glyph(z32, p)) for p in range(18, 33)], OUT / "z32_row2_tiles.png")
    groups = [[1, 26, 17], [6, 14, 19], [2, 32, 12], [5, 24]]
    rows = [[(p, z32_glyph(z32, p)) for p in g] for g in groups]
    w = max(sum(t.width + 20 for _, t in r) for r in rows)
    h = sum(r[0][1].height + 40 for r in rows)
    out = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(out)
    y = 0
    for r in rows:
        x = 0
        for pos, tile in r:
            out.paste(tile, (x, y + 30))
            draw.text((x + 5, y + 5), f"pos {pos}", fill="red")
            x += tile.width + 20
        y += r[0][1].height + 40
    out.save(OUT / "z32_compare.png")

    z13 = Image.open(SCANS / "Zodiac-name.gif").convert("L")
    line = z13.crop(Z13_LINE)
    line.resize((line.width * 3, line.height * 3), Image.NEAREST).save(OUT / "z13_line_x3.png")
    tiles = z13_glyphs(z13)
    sheet([(p, tiles[p - 1]) for p in (5, 7, 9, 4)], OUT / "z13_circles.png")
    sheet([(p, tiles[p - 1]) for p in (3, 11, 10, 1, 12)], OUT / "z13_misc.png")
    print(f"已生成 {OUT.relative_to(ROOT)}/ 下的对比图")


if __name__ == "__main__":
    sys.exit(main())

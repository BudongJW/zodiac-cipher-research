"""外部线索（crib）的约束力：可能出现在 Z32 / Z13 明文中的词，能在多大程度上缩小可能性？

对每个 crib 统计：
    可放置位置数 / 全部位置数（同音替换条件）；
    放置后连带确定的“窗口外”符号数（= crib 对其余位置提供的信息）；
以及多个 crib 同时出现时，互不重叠且映射一致的放置组合数。

用法：python scripts/crib_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.cribs import constrained_symbols, joint_placements, placements  # noqa: E402

# 依据 1970-06-26 信（地图、炸弹、“明年秋天”）与 1970-07-26 信附言（弧度、英寸）
Z32_CRIBS = ["RADIANS", "RADIAN", "INCHES", "INCH", "ALONG", "BOMB", "MAG", "NORTH", "MAGNORTH",
             "MOUNT", "DIABLO", "FALL", "DIG", "BUTTON", "ZERO", "SET"]
Z32_COMBOS = [("RADIANS", "INCHES"), ("RADIANS", "INCH"), ("RADIAN", "INCHES"),
              ("RADIANS", "INCHES", "ALONG"), ("RADIANS", "INCHES", "BOMB")]
# 1970-04-20 信：“My name is —”
Z13_CRIBS = ["ZODIAC", "NAME", "THE", "KILLER", "MR", "JR"]


def analyse(cipher: str, cribs: list[str], combos: list[tuple[str, ...]]) -> dict:
    out = {"single": {}, "joint": {}}
    for crib in cribs:
        pos = placements(cipher, crib)
        total = len(cipher) - len(crib) + 1
        info = [constrained_symbols(cipher, crib, p) for p in pos]
        out["single"][crib] = {"placements": len(pos), "positions": total,
                               "max_outside_symbols": max(info) if info else 0,
                               "mean_outside_symbols": round(sum(info) / len(info), 2) if info else 0}
    for combo in combos:
        out["joint"]["+".join(combo)] = len(joint_placements(cipher, combo))
    return out


def main() -> None:
    utf8_stdio()
    z32 = load("z32").text
    z32_alt = z32[:25] + "④" + z32[26:]
    z13 = load("z13").text
    results = {
        "z32": analyse(z32, Z32_CRIBS, Z32_COMBOS),
        "z32_pos26_distinct": analyse(z32_alt, Z32_CRIBS, Z32_COMBOS),
        "z13": analyse(z13, Z13_CRIBS, []),
    }
    for name, res in results.items():
        print(f"\n=== {name}")
        for crib, r in res["single"].items():
            print(f"  {crib:<9} 可放置 {r['placements']:>2}/{r['positions']:<2}  "
                  f"连带确定窗口外符号：最多 {r['max_outside_symbols']}，平均 {r['mean_outside_symbols']}")
        for combo, n in res["joint"].items():
            print(f"  组合 {combo}：{n} 种放置")
    out = ROOT / "results" / "cribs.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

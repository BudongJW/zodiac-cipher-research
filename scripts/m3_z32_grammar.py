"""M3 补充：Z32 “弧度 + 英寸”类声明的基准——一个小文法里有多少条指令同样符合 Z32？

历来 Z32 声明（Grinell、Cragle、Stampher、Foxon……）几乎都是“X 弧度 … Y 英寸”型指令，
这是由 1970-07-26 信的附言（Radians & # inches along the radians）决定的。
本脚本用一个很小的文法枚举此类指令，统计字母数恰为 32 且符合 Z32 重复模式
（同音替换条件：C(1,26)、△(2,32)、O(6,14) 三组位置字母相同）的短语数量，
以及它们对应的不同 (弧度, 英寸) 组合数。符合者越多，单个“符合”的声明越没有证据价值。

用法：python scripts/m3_z32_grammar.py
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.names import fits  # noqa: E402

NUMBERS = {
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8,
    "NINE": 9, "TEN": 10, "ELEVEN": 11, "TWELVE": 12, "THIRTEEN": 13, "FOURTEEN": 14,
    "FIFTEEN": 15, "SIXTEEN": 16, "SEVENTEEN": 17, "EIGHTEEN": 18, "NINETEEN": 19, "TWENTY": 20,
}
FRACTIONS = {"": 0.0, "ANDAHALF": 0.5, "ANDAQUARTER": 0.25, "POINTFIVE": 0.5}
VERBS = ["", "ESTIMATE", "MEASURE", "GO", "SET", "TAKE", "USE", "TURN", "FIND", "DIG", "COUNT", "PACE", "IN", "AT"]
CONJ = ["", "AND", "THEN", "PLUS", "ANDTHEN"]
RAD = ["RADIANS", "RADIAN"]
INCH = ["INCHES", "INCH"]
TAILS = ["", "ALONG", "ALONGIT", "ALONGTHERADIANS", "ALONGTHERADIAN", "FROMMOUNTDIABLO", "FROMDIABLO",
         "FROMTHEMOUNT", "FROMMTDIABLO", "NORTH", "EAST", "WEST", "SOUTH", "OUT", "AWAY", "FROMZERO",
         "FROMMAGNORTH", "ONTHEMAP"]


def numbers():
    for word, value in NUMBERS.items():
        for frac, fv in FRACTIONS.items():
            yield word + frac, value + fv


MIDS = ["ALONG", "ALONGTHE", "ON", "ONTHE", "AT"]


def phrases(length: int):
    """两种语序：… R 弧度 … I 英寸 …；… I 英寸 ALONG (THE) R 弧度 …

    只生成字母数恰为 length 的短语（按长度索引结尾词，避免枚举全部组合）。
    返回 (短语, 弧度, 英寸) 的生成器，以及文法可生成的短语总数。
    """
    nums = list(numbers())
    tails_by_len: dict[int, list[str]] = {}
    for t in TAILS:
        tails_by_len.setdefault(len(t), []).append(t)
    total = 2 * len(VERBS) * len(nums) ** 2 * len(TAILS) * len(RAD) * len(INCH) * len(CONJ)

    def gen():
        for verb, (r_word, r), conj, rad, (i_word, i), inch in itertools.product(
                VERBS, nums, CONJ, RAD, nums, INCH):
            head = verb + r_word + rad + conj + i_word + inch
            for tail in tails_by_len.get(length - len(head), ()):
                yield head + tail, r, i
        for verb, (i_word, i), inch, mid, (r_word, r), rad in itertools.product(
                VERBS, nums, INCH, MIDS, nums, RAD):
            head = verb + i_word + inch + mid + r_word + rad
            for tail in tails_by_len.get(length - len(head), ()):
                yield head + tail, r, i

    return gen(), total


def main() -> None:
    utf8_stdio()
    z32 = load("z32").text
    gen, total = phrases(len(z32))
    length_ok = 0
    hits: list[tuple[str, float, float]] = []
    for text, r, i in gen:
        length_ok += 1
        if fits(text, z32):
            hits.append((text, r, i))
    pairs = Counter((r, i) for _, r, i in hits)
    print(f"文法共生成 {total:,} 条指令；字母数恰为 32 的 {length_ok:,} 条；符合 Z32 重复模式的 {len(hits):,} 条"
          f"（占长度相符者 {len(hits) / length_ok:.2%}）")
    print(f"符合者对应的不同 (弧度, 英寸) 组合：{len(pairs)} 种")
    print("示例：", ", ".join(t for t, _, _ in hits[:12]))
    for claim in ("ESTIMATEFOURRADIANSANDFIVEINCHES",):
        print(f"Grinell 2020 声明是否在文法内且符合：{claim in {t for t, _, _ in hits}}")

    out = ROOT / "results" / "m3_z32_grammar.json"
    out.write_text(json.dumps({
        "generated": total, "length_32": length_ok, "fits": len(hits),
        "distinct_radian_inch_pairs": len(pairs),
        "pairs": sorted([[r, i, n] for (r, i), n in pairs.items()]),
        "examples": [t for t, _, _ in hits[:200]],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

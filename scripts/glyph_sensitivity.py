"""方向 A：字形核对后的敏感性分析——Z32 第 26 位若与第 1 位不是同一符号，结论会怎样变化？

对照高清扫描（docs/glyph-report.md）发现：Z32 第 26 位的 “C” 下端向内回钩、比第 1 位小，
可能是另一个符号；第 6、14 位的 “O” 仅倾斜不同。本脚本对以下读法重算 M2 / M3 的关键统计：
    原转录 / 第 26 位为独立符号 / 第 14 位为独立符号 / 两者皆为独立符号
统计：不同符号数与重复结构、Zodiac 式密钥下出现该程度重复的概率（M2 / B1b）、
普通英文片段符合率（M3）、“弧度 + 英寸”小文法中的符合数（M3）、各 Z32 声明是否仍符合。

用法：python scripts/glyph_sensitivity.py [--trials 20000]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from m3_z32_grammar import phrases  # noqa: E402

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import stdlib_english  # noqa: E402
from zkc.evaluate import pattern_base_rate  # noqa: E402
from zkc.names import fits  # noqa: E402
from zkc.stats import count_profile  # noqa: E402
from zkc.synth import encrypt, homophone_counts, random_key, sample_window, zodiac_plaintexts  # noqa: E402

CLAIMS = {
    "Grinell 2020": "ESTIMATEFOURRADIANSANDFIVEINCHES",
    "Cragle": "THREERADIANSFROMMOUNTAREATWOINCH",
    "Stampher": "INTHREEANDTHREEEIGHTHSRADIANSTEN",
}


def replace_at(text: str, pos: int, symbol: str) -> str:
    """把第 pos 位（1 起）替换为新符号。"""
    return text[:pos - 1] + symbol + text[pos:]


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=20000)
    args = p.parse_args()

    z32 = load("z32").text
    variants = {
        "原转录": z32,
        "第26位为独立符号": replace_at(z32, 26, "④"),
        "第14位为独立符号": replace_at(z32, 14, "⑤"),
        "第14、26位皆为独立符号": replace_at(replace_at(z32, 26, "④"), 14, "⑤"),
    }
    english = zodiac_plaintexts() + [stdlib_english()]
    grammar = list(phrases(32)[0])
    counts = homophone_counts("z340")

    results = {}
    for name, cipher in variants.items():
        distinct = len(set(cipher))
        profile = count_profile(cipher)
        rng = random.Random(f"glyph-{name}")
        ge = same = 0
        for _ in range(args.trials):
            c = encrypt(sample_window(zodiac_plaintexts(), 32, rng), random_key(counts, rng), "cycle", rng)
            ge += len(set(c)) >= distinct
            same += count_profile(c) == profile
        base = pattern_base_rate(cipher, english)
        hits = [(t, r, i) for t, r, i in grammar if fits(t, cipher)]
        results[name] = {
            "cipher": cipher, "distinct": distinct, "repeats": sum(1 for k in profile if k > 1),
            "p_ge_distinct_z340_cycle": ge / args.trials, "p_same_profile_z340_cycle": same / args.trials,
            "english_fit": base, "grammar_fits": len(hits),
            "grammar_pairs": len({(r, i) for _, r, i in hits}),
            "claims_fit": {k: fits(v, cipher) for k, v in CLAIMS.items()},
        }
        r = results[name]
        print(f"{name}：不同符号 {distinct}，重复组 {r['repeats']}；Z340 式密钥下 P(≥{distinct}) = "
              f"{r['p_ge_distinct_z340_cycle']:.3f}，P(结构相同) = {r['p_same_profile_z340_cycle']:.3f}；"
              f"英文片段符合 {base['fits']:,}/{base['windows']:,}（{base['rate']:.1e}）；"
              f"文法符合 {len(hits)} 条 / {r['grammar_pairs']} 种组合；声明仍符合：{r['claims_fit']}", flush=True)

    out = ROOT / "results" / "glyph_sensitivity.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

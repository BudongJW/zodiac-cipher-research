"""M2 / B1b：重复结构检验——Z13、Z32 的符号重复程度是否与“Zodiac 式”密钥相符？

用 Z408 / Z340 的同音数分布生成随机密钥，加密 Zodiac 自己的英文片段（长度 13 与 32），
统计不同符号数的分布，并与 Z13（13 个符号中 8 个不同）、Z32（32 个中 29 个不同）比较。
另以“简单替换”（每个字母只有 1 个符号）作为对照。

用法：python scripts/m2_repetition.py [--trials 20000]
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.ngram import ALPHABET  # noqa: E402
from zkc.synth import encrypt, homophone_counts, random_key, sample_window, zodiac_plaintexts  # noqa: E402


def count_profile(text: str) -> tuple[int, ...]:
    """各符号出现次数，降序——与具体符号无关的“重复结构”。"""
    return tuple(sorted(Counter(text).values(), reverse=True))


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=20000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/m2_repetition.csv")
    args = p.parse_args()

    texts = zodiac_plaintexts()
    targets = {"z13": load("z13").text, "z32": load("z32").text}
    systems = {
        "simple": (dict.fromkeys(ALPHABET, 1), "cycle"),
        "z408-cycle": (homophone_counts("z408"), "cycle"),
        "z408-random": (homophone_counts("z408"), "random"),
        "z340-cycle": (homophone_counts("z340"), "cycle"),
        "z340-random": (homophone_counts("z340"), "random"),
    }

    rows = []
    for target, observed in targets.items():
        length, obs_distinct, obs_profile = len(observed), len(set(observed)), count_profile(observed)
        print(f"\n{target}：长度 {length}，观测不同符号 {obs_distinct}，重复结构 {obs_profile[:5]}…")
        print(f"{'体制':<13}{'不同符号 均值±sd':>18}{'P(≤观测)':>12}{'P(≥观测)':>12}{'P(结构相同)':>14}")
        for name, (counts, policy) in systems.items():
            rng = random.Random(f"{args.seed}-{target}-{name}")
            distinct, same = [], 0
            for _ in range(args.trials):
                plain = sample_window(texts, length, rng)
                c = encrypt(plain, random_key(counts, rng), policy, rng)
                distinct.append(len(set(c)))
                same += count_profile(c) == obs_profile
            n = len(distinct)
            mean = sum(distinct) / n
            sd = (sum((d - mean) ** 2 for d in distinct) / (n - 1)) ** 0.5
            le = sum(d <= obs_distinct for d in distinct) / n
            ge = sum(d >= obs_distinct for d in distinct) / n
            rows.append({"target": target, "system": name, "trials": n, "mean_distinct": round(mean, 3),
                         "sd_distinct": round(sd, 3), "p_le_observed": le, "p_ge_observed": ge,
                         "p_same_profile": same / n})
            print(f"{name:<13}{mean:>11.2f} ± {sd:<5.2f}{le:>12.4f}{ge:>12.4f}{same / n:>14.4f}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n已写入 {out}")


if __name__ == "__main__":
    main()

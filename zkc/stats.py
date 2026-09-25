"""密文统计量。"""

from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence


def multiplicity(text: Sequence) -> float:
    """King & Bahler (1993) 的 multiplicity：不同符号数 ÷ 长度。"""
    return len(set(text)) / len(text)


def isomorph_pattern(text: Sequence) -> list[int]:
    """同构模式：按首次出现顺序给符号编号（从 1 开始）。"""
    ids: dict = {}
    return [ids.setdefault(ch, len(ids) + 1) for ch in text]


def repeated_positions(text: Sequence) -> dict:
    """出现次数 ≥ 2 的符号及其位置（1 起）。"""
    pos: dict = {}
    for i, ch in enumerate(text, 1):
        pos.setdefault(ch, []).append(i)
    return {ch: p for ch, p in pos.items() if len(p) > 1}


def bigram_repeats(text: Sequence, period: int = 1) -> int:
    """周期 p 的双字母重复数：Σ(count − 1)，统计 (text[i], text[i+p]) 对。

    Z340 的著名统计（周期 1 为 25、周期 19 为 37）即采用此定义。
    """
    pairs = Counter((text[i], text[i + period]) for i in range(len(text) - period))
    return sum(c - 1 for c in pairs.values() if c > 1)


def period_profile(text: Sequence, periods: Iterable[int]) -> dict[int, int]:
    return {p: bigram_repeats(text, p) for p in periods}


def index_of_coincidence(text: Sequence) -> float:
    n = len(text)
    counts = Counter(text)
    return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))


def entropy_bits(text: Sequence) -> float:
    n = len(text)
    return -sum(c / n * math.log2(c / n) for c in Counter(text).values())


def shuffle_test(
    text: Sequence,
    statistic: Callable[[Sequence], float],
    trials: int = 10_000,
    seed: int | None = 0,
) -> dict[str, float]:
    """置换检验：随机打乱符号顺序，计算统计量 ≥ 观测值的比例（单侧 p 值）。

    打乱保留符号频率、破坏顺序结构，是检验“顺序结构是否显著”的零假设。
    """
    rng = random.Random(seed)
    observed = statistic(text)
    seq = list(text)
    values = []
    for _ in range(trials):
        rng.shuffle(seq)
        values.append(statistic(seq))
    mean = sum(values) / trials
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (trials - 1))
    ge = sum(v >= observed for v in values)
    return {
        "observed": observed,
        "mean": mean,
        "sd": sd,
        "z": (observed - mean) / sd if sd else float("inf"),
        "p": (ge + 1) / (trials + 1),
    }


def overlap_table(ciphers: Mapping[str, Sequence]) -> dict[tuple[str, str], int]:
    """两两符号重合数：|symbols(a) ∩ symbols(b)|。"""
    sets = {k: set(v) for k, v in ciphers.items()}
    return {(a, b): len(sets[a] & sets[b]) for a in sets for b in sets}


def summary(text: str) -> dict:
    counts = Counter(text)
    return {
        "length": len(text),
        "distinct": len(counts),
        "multiplicity": multiplicity(text),
        "ioc": index_of_coincidence(text) if len(text) > 1 else float("nan"),
        "entropy_bits": entropy_bits(text),
        "singletons": sum(1 for c in counts.values() if c == 1),
        "repeated": repeated_positions(text),
        "isomorph": isomorph_pattern(text),
    }

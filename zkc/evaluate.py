"""破译声明的统一评估（路线图 M3）。"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping

from .names import fits

# 英文字母频率（常用参考值，%）
ENGLISH_FREQ = {
    "E": 12.70, "T": 9.06, "A": 8.17, "O": 7.51, "I": 6.97, "N": 6.75, "S": 6.33, "H": 6.09,
    "R": 5.99, "D": 4.25, "L": 4.03, "C": 2.78, "U": 2.76, "M": 2.41, "W": 2.36, "F": 2.23,
    "G": 2.02, "Y": 1.97, "P": 1.93, "B": 1.29, "V": 0.98, "K": 0.77, "J": 0.15, "X": 0.15,
    "Q": 0.10, "Z": 0.07,
}
_TOTAL = sum(ENGLISH_FREQ.values())
ENGLISH_P = {k: v / _TOTAL for k, v in ENGLISH_FREQ.items()}


def consistency(cipher: str, plain: str) -> dict:
    """声明明文与密文的一致性。

    min_errors：为使“同一符号 = 同一字母”成立，至少要假设多少处加密错误
    （每个符号保留其最常见的字母，其余位置记为错误）。
    """
    if len(cipher) != len(plain):
        raise ValueError(f"长度不一致：{len(cipher)} vs {len(plain)}")
    letters: dict[str, Counter] = defaultdict(Counter)
    for sym, ch in zip(cipher, plain):
        letters[sym][ch] += 1
    conflicts = {s: dict(c) for s, c in letters.items() if len(c) > 1}
    min_errors = sum(sum(c.values()) - max(c.values()) for c in letters.values())
    return {
        "fits_homophonic": not conflicts,
        "fits_simple": fits(plain, cipher, simple=True),
        "conflicts": conflicts,
        "min_errors": min_errors,
    }


def _poisson_binomial_tail(ps: list[float], k: int) -> float:
    """P(X ≥ k)，X 为独立伯努利变量之和。"""
    dist = [1.0]
    for p in ps:
        new = [0.0] * (len(dist) + 1)
        for i, q in enumerate(dist):
            new[i] += q * (1 - p)
            new[i + 1] += q * p
        dist = new
    return sum(dist[k:])


def key_agreement(cipher: str, plain: str, reference: Mapping[str, str]) -> dict:
    """在与参考密钥共有的符号上，声明明文与参考密钥一致的位置数，及其偶然一致的概率。

    零假设：声明字母按英文频率独立出现，与某位置的密钥字母 k 一致的概率为 f(k)。
    """
    positions = [(s, ch) for s, ch in zip(cipher, plain) if s in reference]
    matches = sum(reference[s] == ch for s, ch in positions)
    ps = [ENGLISH_P[reference[s]] for s, _ in positions]
    return {
        "shared_positions": len(positions),
        "matches": matches,
        "expected": sum(ps),
        "p_value": _poisson_binomial_tail(ps, matches) if positions else float("nan"),
    }


def pattern_base_rate(cipher: str, texts: Iterable[str], min_distinct: int = 6) -> dict:
    """英文中所有长度为 len(cipher) 的连续片段里，符合 cipher 重复模式（同音替换条件）的比例。"""
    n = len(cipher)
    total = hits = 0
    for t in texts:
        for s in range(len(t) - n + 1):
            w = t[s:s + n]
            if len(set(w)) < min_distinct:
                continue
            total += 1
            hits += fits(w, cipher)
    return {"windows": total, "fits": hits, "rate": hits / total if total else float("nan")}


def grade(fits_homophonic: bool | None, extra_assumptions: bool, independent_key_p: float | None) -> str:
    """M3 分级：A 符合且有独立证据；B 符合但证据价值低；C 需额外假设；D 无法逐位验证。

    independent_key_p：与某个已知密钥的一致性 p 值（仅当该密钥并非声明者据以构造读法时才算独立证据）。
    """
    if fits_homophonic is None:
        return "D"
    if not fits_homophonic or extra_assumptions:
        return "C"
    return "A" if independent_key_p is not None and independent_key_p < 1e-3 else "B"


def score_claim(cipher: str, plaintext: str, *, reading: str | None = None,
                references: Mapping[str, Mapping[str, str]] | None = None,
                key_source: str | None = None, extra_assumptions: bool = False,
                english: Iterable[str] | None = None, model=None, free_scores: list[float] | None = None,
                entropy_weight: float | None = None) -> dict:
    """对单条逐位明文声明做 M3 式评估（供命令行 `python -m zkc score` 使用）。

    reading：若声明含换位，给出阅读顺序的明文（用于语言得分）；plaintext 须为密文顺序。
    references：{名称: 已知密钥}；key_source：声明据以构造读法的密钥名（其一致性不计为独立证据）。
    english：用于计算模式基准率的英文语料；model / free_scores：用于语言得分比较（可省略）。
    """
    from .solver import DEFAULT_ENTROPY_WEIGHT, objective
    from .stats import entropy_bits

    cons = consistency(cipher, plaintext)
    out: dict = {"length": len(cipher), **cons}
    independent_p = None
    for name, key in (references or {}).items():
        ka = key_agreement(cipher, plaintext, key)
        out[f"key_{name}"] = ka
        if name != key_source and ka["shared_positions"]:
            independent_p = ka["p_value"] if independent_p is None else min(independent_p, ka["p_value"])
    if english is not None:
        out["pattern_base_rate"] = pattern_base_rate(cipher, english)
    if model is not None:
        text = reading or plaintext
        w = DEFAULT_ENTROPY_WEIGHT if entropy_weight is None else entropy_weight
        out["language_score"] = objective(model.score(text), entropy_bits(text), w)
        if free_scores:
            out["free_best"] = max(free_scores)
            out["beaten_by_free"] = sum(s > out["language_score"] for s in free_scores) / len(free_scores)
    out["grade"] = grade(cons["fits_homophonic"], extra_assumptions, independent_p)
    return out

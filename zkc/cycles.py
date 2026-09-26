"""同音符号轮换（homophone cycling）模型——Zodiac 的加密习惯。

在 Z408 中，同一明文字母的几个同音符号大体按固定顺序轮流使用；在 Z340 中，这种轮换出现在
**密文的书写顺序**（逐行）而非明文阅读顺序中。本模块：
    1. 度量轮换强度（“后继一致率”：某符号之后最常见的同字母后继所占比例），并与随机打乱比较；
    2. 用“带错误的轮换”生成模型拟合错误率 ε；
    3. 计算候选明文在该模型下的对数似然：只看每个字母各次出现所用符号的“相等 / 不等”结构。

生成模型（每个明文字母独立）：该字母有 k 个同音符号，排成一个循环；起点随机；
每次出现时指针前进一步，以概率 1 − ε 使用指针所指的符号，以概率 ε 从 k 个符号中随机选一个。
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from functools import lru_cache

from .reproduce import reference_key


def letter_sequences(cipher: Sequence[str], plain: str) -> dict[str, list[str]]:
    """每个明文字母按出现顺序所用的密文符号。"""
    seq: dict[str, list[str]] = defaultdict(list)
    for c, p in zip(cipher, plain):
        seq[p].append(c)
    return dict(seq)


def successor_consistency(seqs: Mapping[str, Sequence[str]]) -> tuple[float, int]:
    """多同音字母的“后继一致率”及转移总数。"""
    hit = tot = 0
    for syms in seqs.values():
        if len(set(syms)) < 2:
            continue
        nxt: dict[str, Counter] = defaultdict(Counter)
        for a, b in zip(syms, syms[1:]):
            nxt[a][b] += 1
        for c in nxt.values():
            hit += max(c.values())
            tot += sum(c.values())
    return (hit / tot if tot else float("nan")), tot


def shuffle_test(seqs: Mapping[str, Sequence[str]], trials: int = 2000, seed: int = 0) -> dict:
    """与“每个字母内部随机打乱符号顺序”的零假设比较后继一致率。"""
    rng = random.Random(seed)
    obs, n = successor_consistency(seqs)
    null = [successor_consistency({k: rng.sample(list(v), len(v)) for k, v in seqs.items()})[0]
            for _ in range(trials)]
    mean = sum(null) / trials
    sd = (sum((x - mean) ** 2 for x in null) / (trials - 1)) ** 0.5
    return {"observed": obs, "transitions": n, "null_mean": mean, "null_sd": sd,
            "z": (obs - mean) / sd if sd else float("inf"),
            "p": (sum(x >= obs for x in null) + 1) / (trials + 1)}


def simulate(n: int, k: int, eps: float, rng: random.Random) -> list[int]:
    start = rng.randrange(k)
    return [(start + t) % k if rng.random() >= eps else rng.randrange(k) for t in range(n)]


def canonical(syms: Sequence) -> tuple[int, ...]:
    """相等结构：按首次出现编号，如 [x, y, x] → (0, 1, 0)。"""
    ids: dict = {}
    return tuple(ids.setdefault(s, len(ids)) for s in syms)


def fit_epsilon(seqs: Mapping[str, Sequence[str]], grid: Sequence[float] | None = None,
                reps: int = 200, seed: int = 0) -> float:
    """选取使模拟的后继一致率最接近观测值的 ε（各字母使用观测到的 k 与出现次数）。"""
    grid = grid or [i / 20 for i in range(21)]
    obs, _ = successor_consistency(seqs)
    rng = random.Random(seed)
    best, best_gap = 0.0, float("inf")
    for eps in grid:
        vals = []
        for _ in range(reps):
            sim = {L: simulate(len(v), len(set(v)), eps, rng) for L, v in seqs.items()}
            vals.append(successor_consistency(sim)[0])
        gap = abs(sum(vals) / reps - obs)
        if gap < best_gap:
            best, best_gap = eps, gap
    return best


@lru_cache(maxsize=None)
def pattern_distribution(n: int, k: int, eps: float, sims: int = 20000, seed: int = 0) -> dict:
    """n 次出现、k 个同音符号、错误率 ε 下，各相等结构的概率（蒙特卡罗，加 0.5 平滑）。"""
    rng = random.Random(f"{seed}-{n}-{k}-{eps}")
    counts = Counter(canonical(simulate(n, k, eps, rng)) for _ in range(sims))
    total = sims + 0.5 * (len(counts) + 1)
    return {"probs": {p: (c + 0.5) / total for p, c in counts.items()}, "floor": 0.5 / total}


def homophone_prior(sources: Sequence[str] = ("z408", "z340")) -> dict[str, list[int]]:
    """每个字母同音符号数 k 的先验：取已知密钥（默认 Z408 与 Z340）中该字母的同音数，上下各放宽 1。

    验证时可只用另一份密钥（留一法），避免用被检验的密文自身构造先验。
    """
    counts: dict[str, list[int]] = defaultdict(list)
    for name in sources:
        per: Counter = Counter(reference_key(name).values())
        for letter, k in per.items():
            counts[letter].append(k)
    prior = {}
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        ks = counts.get(letter)
        if ks:
            lo, hi = max(1, min(ks) - 1), max(ks) + 1
            prior[letter] = list(range(lo, hi + 1))
        else:
            prior[letter] = [1, 2]
    return prior


def cycle_loglik(cipher: Sequence[str], plain: str, eps: float,
                 prior: Mapping[str, Sequence[int]] | None = None) -> float:
    """候选明文（与密文逐位对齐，书写顺序）在轮换模型下的对数似然（只计各字母的相等结构）。

    若同一符号对应了不同字母（不符合同音替换），返回 −inf。
    """
    prior = prior or homophone_prior()
    sym_letter: dict = {}
    for c, p in zip(cipher, plain):
        if sym_letter.setdefault(c, p) != p:
            return float("-inf")
    total = 0.0
    for letter, syms in letter_sequences(cipher, plain).items():
        pat = canonical(syms)
        ks = [k for k in prior.get(letter, [1, 2]) if k >= max(pat) + 1] or [max(pat) + 1]
        like = 0.0
        for k in ks:
            dist = pattern_distribution(len(syms), k, eps)
            like += dist["probs"].get(pat, dist["floor"]) / len(ks)
        total += math.log(like)
    return total


def encrypt_with_cycles(plain: str, counts: Mapping[str, int], eps: float, rng: random.Random) -> list[str]:
    """按轮换模型加密（合成数据用）：每个字母有 counts[字母] 个同音符号，记作 “字母 + 序号”。"""
    pointer = {L: rng.randrange(max(1, counts[L])) for L in counts}
    out = []
    for ch in plain:
        k = max(1, counts[ch])
        idx = pointer[ch] % k if rng.random() >= eps else rng.randrange(k)
        pointer[ch] += 1
        out.append(f"{ch}{idx}")
    return out


class CycleTerm:
    """求解器中的轮换似然项。

    维护“每个字母当前分到哪些符号”，按书写顺序（密文位置顺序）得到该字母各次出现的符号序列，
    计算其在轮换模型下的对数似然；过长的序列按每 chunk 次出现分块，块间视为独立（近似）。
    """

    def __init__(self, sid, n_symbols: int, eps: float,
                 prior: Mapping[str, Sequence[int]] | None = None, chunk: int = 10):
        self.eps, self.chunk = eps, chunk
        self.prior = prior or homophone_prior()
        self.positions = [[i for i, s in enumerate(sid) if s == sym] for sym in range(n_symbols)]
        self.cache: dict = {}
        self.members: list[set] = []
        self.ll: list[float] = []

    def _letter_ll(self, letter: int, members) -> float:
        if not members:
            return 0.0
        seq = [s for _, s in sorted((p, s) for s in members for p in self.positions[s])]
        pat = canonical(seq)
        key = (letter, pat)
        if key in self.cache:
            return self.cache[key]
        name = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[letter]
        need = max(pat) + 1
        ks = [k for k in self.prior.get(name, [1, 2]) if k >= need] or [need]
        like = 0.0
        for k in ks:
            p = 1.0
            for i in range(0, len(pat), self.chunk):
                sub = canonical(pat[i:i + self.chunk])
                dist = pattern_distribution(len(sub), k, self.eps)
                p *= dist["probs"].get(sub, dist["floor"])
            like += p / len(ks)
        self.cache[key] = math.log(like)
        return self.cache[key]

    def init(self, key: Sequence[int]) -> None:
        self.members = [set() for _ in range(26)]
        for sym, letter in enumerate(key):
            self.members[int(letter)].add(sym)
        self.ll = [self._letter_ll(l, self.members[l]) for l in range(26)]

    def delta(self, sym: int, old: int) -> list[float]:
        """把符号 sym 从字母 old 改为各字母时，总对数似然的变化（长度 26）。"""
        old_without = self._letter_ll(old, self.members[old] - {sym}) - self.ll[old]
        return [0.0 if l == old else
                old_without + self._letter_ll(l, self.members[l] | {sym}) - self.ll[l]
                for l in range(26)]

    def commit(self, sym: int, old: int, new: int) -> None:
        self.members[old].discard(sym)
        self.members[new].add(sym)
        self.ll[old] = self._letter_ll(old, self.members[old])
        self.ll[new] = self._letter_ll(new, self.members[new])

    def total(self) -> float:
        return float(sum(self.ll))

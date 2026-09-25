"""同音替换求解器：模拟退火 + 热浴（Gibbs）更新。

打分函数（与 AZdecrypt 同类）：

    score = mean_ngram × (H / H_REF) ** w

mean_ngram 为明文平均 n-gram 分数，H 为明文字母熵（bits），w 为熵权重，
H_REF = 4.1 为英文字母熵的典型值（归一化后得分与温度都以“n-gram 分”为单位，不随 w 变化）。
熵项用于抑制同音替换中常见的“退化解”（大量符号挤向少数高频字母）。

每一步选取一个符号，向量化地一次算出它改为 26 个字母中任一字母后的得分，
再按 exp(score / T) 的概率采样新字母；T 按几何级数从 t_start 降到 t_end，
最后以贪心扫描收尾。多次随机重启，取得分最高者。
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import numpy as np

from .ngram import ALPHABET, NgramModel, ngram_indices

_LETTERS = np.arange(26, dtype=np.int64)
H_REF = 4.1
DEFAULT_ENTROPY_WEIGHT = 2.0


@dataclass
class SolveResult:
    score: float
    plaintext: str
    key: dict[str, str]
    ngram_mean: float
    entropy: float
    seed: int

    def __str__(self) -> str:
        return (f"score={self.score:.2f} ngram={self.ngram_mean:.2f} "
                f"H={self.entropy:.3f} seed={self.seed}\n{self.plaintext}")


def _plogp(counts, total: int) -> np.ndarray:
    """逐项计算 −(x/N)·log2(x/N)，x = 0 时为 0。"""
    p = np.asarray(counts, dtype=np.float64) / total
    out = np.zeros_like(p)
    nz = p > 0
    out[nz] = -p[nz] * np.log2(p[nz])
    return out


class Problem:
    """预计算：每个符号影响到的 n-gram 起点，以及该符号在这些 n-gram 中的位权之和。"""

    def __init__(self, text: str, n: int):
        self.text = text
        self.symbols = list(dict.fromkeys(text))
        index = {s: i for i, s in enumerate(self.symbols)}
        self.sid = np.array([index[c] for c in text], dtype=np.int64)
        self.n = n
        self.length = len(text)
        self.n_grams = self.length - n + 1
        if self.n_grams <= 0:
            raise ValueError(f"密文长度 {self.length} 小于 n-gram 长度 {n}")
        self.counts = np.bincount(self.sid, minlength=len(self.symbols))
        pos_weight = 26 ** np.arange(n - 1, -1, -1, dtype=np.int64)
        self.affected: list[np.ndarray] = []
        self.weight: list[np.ndarray] = []
        for s in range(len(self.symbols)):
            m = np.zeros(self.n_grams, dtype=np.int64)
            for j in range(n):
                m[self.sid[j:j + self.n_grams] == s] += pos_weight[j]
            starts = np.flatnonzero(m)
            self.affected.append(starts)
            self.weight.append(m[starts])


def anneal(problem: Problem, table: np.ndarray, rng: np.random.Generator, *,
           sweeps: int, t_start: float, t_end: float, entropy_weight: float,
           fixed: dict[int, int] | None = None, polish_sweeps: int = 50):
    """单次退火。返回 (score, key 数组, mean_ngram, H)。"""
    n_sym, length, n_grams = len(problem.symbols), problem.length, problem.n_grams
    fixed = fixed or {}
    key = rng.integers(0, 26, size=n_sym)
    for s, letter in fixed.items():
        key[s] = letter
    free = np.array([s for s in range(n_sym) if s not in fixed], dtype=np.int64)

    plain = key[problem.sid]
    idx = ngram_indices(plain, problem.n)
    total = int(table[idx].sum(dtype=np.int64))
    cnt = np.bincount(plain, minlength=26).astype(np.float64)
    plogp = _plogp(cnt, length)
    h = float(plogp.sum())
    w = entropy_weight

    temps = list(t_start * (t_end / t_start) ** np.linspace(0.0, 1.0, sweeps))
    temps += [0.0] * polish_sweeps  # 贪心收尾

    for sweep_t in temps:
        changed = False
        for s in rng.permutation(free):
            starts, weight = problem.affected[s], problem.weight[s]
            old, c = int(key[s]), int(problem.counts[s])
            cur = idx[starts]
            cand = cur[:, None] + weight[:, None] * (_LETTERS - old)[None, :]
            tot = (total - int(table[cur].sum(dtype=np.int64))) + table[cand].sum(axis=0, dtype=np.int64)
            h_new = h + (_plogp(cnt + c, length) - plogp) \
                + (_plogp(cnt[old] - c, length) - plogp[old])
            h_new[old] = h
            sc = tot / n_grams * np.power(np.maximum(h_new, 1e-12) / H_REF, w)
            if sweep_t > 0:
                z = np.exp((sc - sc.max()) / sweep_t)
                cdf = np.cumsum(z)
                new = min(int(np.searchsorted(cdf, rng.random() * cdf[-1], side="right")), 25)
            else:
                new = int(np.argmax(sc))
            if new != old:
                changed = True
                key[s] = new
                idx[starts] = cand[:, new]
                total = int(tot[new])
                cnt[old] -= c
                cnt[new] += c
                plogp[[old, new]] = _plogp(cnt[[old, new]], length)
                h = float(plogp.sum())
        if sweep_t == 0 and not changed:
            break

    mean = total / n_grams
    return objective(mean, h, w), key.copy(), mean, h


def objective(mean_ngram: float, entropy: float, entropy_weight: float) -> float:
    """求解器的目标函数（也用于给已知明文打分以作对照）。"""
    return mean_ngram * (entropy / H_REF) ** entropy_weight


# -- 多次重启（可多进程） -------------------------------------------------------

_WORKER: dict = {}


def _init_worker(table: np.ndarray) -> None:
    _WORKER["table"] = table


def _run_one(args):
    text, n, seed, opts, fixed = args
    problem = Problem(text, n)
    rng = np.random.default_rng(seed)
    score, key, mean, h = anneal(problem, _WORKER["table"], rng, fixed=fixed, **opts)
    return score, key, mean, h, seed


def solve(text: str, model: NgramModel, *, restarts: int = 8, sweeps: int = 1000,
          t_start: float = 2.0, t_end: float = 0.02,
          entropy_weight: float = DEFAULT_ENTROPY_WEIGHT,
          seed: int = 0, jobs: int = 1, fixed: dict[str, str] | None = None) -> list[SolveResult]:
    """求解同音替换密文 text（应已按明文顺序排列，即已去除换位）。

    fixed：预先固定的 {符号: 字母}（例如密钥复用假设）。
    返回按得分降序排列的各次重启结果。
    """
    problem = Problem(text, model.n)
    fixed_ids = {problem.symbols.index(s): ALPHABET.index(l.upper())
                 for s, l in (fixed or {}).items() if s in problem.symbols}
    opts = dict(sweeps=sweeps, t_start=t_start, t_end=t_end, entropy_weight=entropy_weight)
    tasks = [(text, model.n, seed * 100_003 + r, opts, fixed_ids) for r in range(restarts)]

    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_worker,
                                 initargs=(model.table,)) as pool:
            raw = list(pool.map(_run_one, tasks))
    else:
        _init_worker(model.table)
        raw = [_run_one(t) for t in tasks]

    results = []
    for score, key, mean, h, sd in raw:
        key_map = {sym: ALPHABET[key[i]] for i, sym in enumerate(problem.symbols)}
        plaintext = "".join(key_map[c] for c in text)
        results.append(SolveResult(score, plaintext, key_map, mean, h, sd))
    return sorted(results, key=lambda r: r.score, reverse=True)

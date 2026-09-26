"""H004：把轮换似然加入目标函数，能否降低可解长度门槛？（预注册见 hypotheses/H004-cycle-aware-solver.md）

合成数据：Zodiac 自己的英文，同音数在先验范围内随机，按带错误的轮换模型（ε_gen = 0.4）加密。
对同一份密文比较：仅语言目标（λ = 0）与语言 + λ × 轮换对数似然（λ ∈ {1, 3, 10}）。

用法：python scripts/h004_cycle_solver.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import get_model  # noqa: E402
from zkc.cycles import CycleTerm, encrypt_with_cycles, homophone_prior  # noqa: E402
from zkc.ngram import ALPHABET  # noqa: E402
from zkc.solver import DEFAULT_ENTROPY_WEIGHT, Problem, objective, solve  # noqa: E402
from zkc.stats import entropy_bits  # noqa: E402
from zkc.synth import sample_window, zodiac_plaintexts  # noqa: E402

LAMBDAS = (0.0, 1.0, 3.0, 10.0)
EPS = 0.4
_MODEL = None


def _init(spec: str) -> None:
    global _MODEL
    _MODEL = get_model(spec)


def run_trial(task: dict) -> list[dict]:
    L, t = task["length"], task["trial"]
    rng = random.Random(f"h004-{L}-{t}")
    prior = homophone_prior()
    plain = sample_window(zodiac_plaintexts(), L, rng)
    counts = {k: rng.choice(v) for k, v in prior.items()}
    cipher = encrypt_with_cycles(plain, counts, EPS, rng)
    sweeps = 400 if L <= 50 else 800

    # 真实明文在各目标下的得分
    problem = Problem(cipher, _MODEL.n)
    true_key = [ALPHABET.index(sym[0]) for sym in problem.symbols]
    ct = CycleTerm(problem.sid.tolist(), len(problem.symbols), EPS, prior)
    ct.init(true_key)
    lang_truth = objective(_MODEL.score(plain), entropy_bits(plain), DEFAULT_ENTROPY_WEIGHT)
    cycle_truth = ct.total()

    rows = []
    for lam in LAMBDAS:
        t0 = time.time()
        best = solve(cipher, _MODEL, restarts=task["restarts"], sweeps=sweeps, seed=t, jobs=1,
                     cycle_weight=lam, cycle_eps=EPS)[0]
        acc = sum(a == b for a, b in zip(best.plaintext, plain)) / L
        truth_score = lang_truth + lam * cycle_truth
        rows.append({"length": L, "trial": t, "lambda": lam, "acc": round(acc, 4),
                     "best_score": round(best.score, 3), "truth_score": round(truth_score, 3),
                     "spurious": int(best.score > truth_score + 1e-9), "seconds": round(time.time() - t0, 1),
                     "plain": plain, "best": best.plaintext})
    return rows


def sign_test(diffs: list[float]) -> float:
    """配对符号检验（单侧：正差多于负差），忽略零差。"""
    pos = sum(d > 0 for d in diffs)
    n = sum(d != 0 for d in diffs)
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(pos, n + 1)) / 2 ** n


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--lengths", default="32,50,75,100")
    p.add_argument("--trials", type=int, default=12)
    p.add_argument("--restarts", type=int, default=8)
    p.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    p.add_argument("--out", default="results/h004_cycle_solver.csv")
    args = p.parse_args()

    lengths = [int(x) for x in args.lengths.split(",")]
    tasks = [{"length": L, "trial": t, "restarts": args.restarts} for L in lengths for t in range(args.trials)]
    print(f"{len(tasks)} 个试验 × λ ∈ {LAMBDAS}", flush=True)
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=args.jobs, initializer=_init, initargs=(args.model,)) as pool:
        for i, res in enumerate(pool.map(run_trial, tasks), 1):
            rows += res
            print(f"  {i}/{len(tasks)} 完成（L={res[0]['length']}）[{time.time() - t0:.0f}s]", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"\n{'L':>4}{'λ':>6}{'平均准确率':>10}{'P(acc≥0.5)':>12}{'错误解胜出':>10}{'较基线提高':>10}{'符号检验 p':>12}")
    for L in lengths:
        base = {r["trial"]: r["acc"] for r in rows if r["length"] == L and r["lambda"] == 0.0}
        for lam in LAMBDAS:
            sub = [r for r in rows if r["length"] == L and r["lambda"] == lam]
            accs = [r["acc"] for r in sub]
            diffs = [r["acc"] - base[r["trial"]] for r in sub]
            p_sign = sign_test(diffs) if lam > 0 else float("nan")
            print(f"{L:>4}{lam:>6.0f}{statistics.mean(accs):>10.3f}{sum(a >= 0.5 for a in accs) / len(accs):>12.2f}"
                  f"{sum(r['spurious'] for r in sub) / len(sub):>10.2f}{statistics.mean(diffs):>+10.3f}"
                  f"{p_sign:>12.4f}")
    print(f"\n已写入 {args.out}（用时 {time.time() - t0:.0f}s）")


if __name__ == "__main__":
    main()

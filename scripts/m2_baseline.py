"""M2 / B1：短密文可解性基线。

对不同长度 L，从 Zodiac 自己的英文中截取片段，用“Zodiac 式”同音替换密钥（默认按 Z340 密钥的
同音数分布、同音符号轮换使用）加密，再用求解器盲解，统计：

    acc        最佳解的逐位准确率
    spurious   求解器找到的最佳解得分是否高于真实明文（= 目标函数已无法认出真实明文）

用法：
    python scripts/m2_baseline.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
"""

from __future__ import annotations

import argparse
import csv
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
from zkc.solver import objective, solve  # noqa: E402
from zkc.stats import entropy_bits  # noqa: E402
from zkc.synth import encrypt, homophone_counts, random_key, sample_window, zodiac_plaintexts  # noqa: E402

_MODEL = None


def _init(spec: str) -> None:
    global _MODEL
    _MODEL = get_model(spec)


def sweeps_for(length: int) -> int:
    return 400 if length <= 50 else 800 if length <= 150 else 1500


def run_trial(task: dict) -> dict:
    rng = random.Random(f"{task['seed']}-{task['length']}-{task['trial']}")
    plain = sample_window(zodiac_plaintexts(), task["length"], rng)
    key = random_key(homophone_counts(task["reference"]), rng)
    cipher = encrypt(plain, key, task["policy"], rng)
    results = solve(cipher, _MODEL, restarts=task["restarts"], sweeps=sweeps_for(task["length"]),
                    seed=task["trial"], jobs=1)
    best = results[0]
    true_obj = objective(_MODEL.score(plain), entropy_bits(plain), task["weight"])
    acc = sum(a == b for a, b in zip(best.plaintext, plain)) / len(plain)
    return {"length": task["length"], "trial": task["trial"], "distinct": len(set(cipher)),
            "acc": round(acc, 4), "best_score": round(best.score, 3), "true_score": round(true_obj, 3),
            "spurious": int(best.score > true_obj + 1e-9), "plain": plain, "best": best.plaintext}


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--lengths", default="13,20,32,50,75,100,150,200,340")
    p.add_argument("--trials", type=int, default=24)
    p.add_argument("--restarts", type=int, default=8)
    p.add_argument("--reference", default="z340", choices=["z340", "z408"])
    p.add_argument("--policy", default="cycle", choices=["cycle", "random"])
    p.add_argument("--weight", type=float, default=2.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    p.add_argument("--out", default="results/m2_baseline.csv")
    args = p.parse_args()

    lengths = [int(x) for x in args.lengths.split(",")]
    tasks = [dict(length=L, trial=t, seed=args.seed, reference=args.reference, policy=args.policy,
                  restarts=args.restarts, weight=args.weight)
             for L in lengths for t in range(args.trials)]
    print(f"{len(tasks)} 个试验：长度 {lengths}，每个长度 {args.trials} 次，密钥 {args.reference}-{args.policy}，"
          f"每次 {args.restarts} 次重启", flush=True)

    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=args.jobs, initializer=_init, initargs=(args.model,)) as pool:
        for row in pool.map(run_trial, tasks):
            rows.append(row)
            if row["trial"] == args.trials - 1:
                print(f"  L={row['length']} 完成 [{time.time() - t0:.0f}s]", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'L':>5}{'多重度':>8}{'准确率 均值':>11}{'中位数':>8}{'P(acc≥0.9)':>12}{'P(错误解得分>真实)':>20}")
    for L in lengths:
        sub = [r for r in rows if r["length"] == L]
        accs = [r["acc"] for r in sub]
        mult = statistics.mean(r["distinct"] for r in sub) / L
        print(f"{L:>5}{mult:>8.2f}{statistics.mean(accs):>11.3f}{statistics.median(accs):>8.3f}"
              f"{sum(a >= 0.9 for a in accs) / len(accs):>12.2f}"
              f"{sum(r['spurious'] for r in sub) / len(sub):>20.2f}")
    print(f"\n已写入 {out}（用时 {time.time() - t0:.0f}s）")


if __name__ == "__main__":
    main()

"""Z340 换位扫描：对第 1、2 段施加全部可遍历的 (dr, dc) 抽取，以求解器得分评估。

小规模复现 2020 年破解的核心思路——“候选换位 × 同音替换求解器”：
正确的换位应得到显著高于其他候选的得分。第 2 段的 LIFEIS / H 移位异常
与末两行的倒写在此不做处理（破解者当时也是先在无异常假设下找到 (1,2) 的）。

两阶段：粗扫（全部候选，低预算）→ 精扫（粗扫前 K 名，高预算）。

用法（在仓库根目录）：
    python scripts/z340_transposition_scan.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
    python scripts/z340_transposition_scan.py --model ... --refine-only   # 只基于已有粗扫结果做精扫
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import get_model  # noqa: E402
from zkc.solver import solve  # noqa: E402
from zkc.transpose import Z340_SECTIONS, section_decimation_order, untranspose  # noqa: E402


def candidate_order(dr: int, dc: int) -> list[int]:
    """第 1、2 段各自做 (dr, dc) 抽取，第 3 段按行读取。"""
    order: list[int] = []
    for first, last in Z340_SECTIONS[:2]:
        order += section_decimation_order(first, last, dr, dc)
    first, last = Z340_SECTIONS[2]
    return order + list(range(first * 17, last * 17))


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--restarts", type=int, default=8)
    p.add_argument("--sweeps", type=int, default=600)
    p.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="results/z340_transposition_scan.csv")
    p.add_argument("--refine-top", type=int, default=5)
    p.add_argument("--refine-restarts", type=int, default=16)
    p.add_argument("--refine-sweeps", type=int, default=2000)
    p.add_argument("--refine-out", default="results/z340_transposition_refine.csv")
    p.add_argument("--refine-only", action="store_true", help="跳过粗扫，读取 --out 中已有结果")
    args = p.parse_args()

    model = get_model(args.model)
    cipher = load("z340").text
    orders = {"none": list(range(340))}
    for dr in range(1, 9):
        for dc in range(17):
            try:
                orders[f"({dr},{dc})"] = candidate_order(dr, dc)
            except ValueError:
                pass

    def run(label: str, restarts: int, sweeps: int) -> dict:
        best = solve(untranspose(cipher, orders[label]), model, restarts=restarts,
                     sweeps=sweeps, seed=args.seed, jobs=args.jobs)[0]
        return {"scheme": label, "score": round(best.score, 3), "ngram_mean": round(best.ngram_mean, 2),
                "entropy": round(best.entropy, 3), "plaintext_head": best.plaintext[:34]}

    out = Path(args.out)
    if args.refine_only:
        with out.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            r["score"] = float(r["score"])
    else:
        print(f"粗扫：{len(orders)} 个候选（含原顺序），每个 {args.restarts} 次重启 × {args.sweeps} 次扫描", flush=True)
        rows, t0 = [], time.time()
        for label in orders:
            rows.append(run(label, args.restarts, args.sweeps))
            print(f"{label:>7} score={rows[-1]['score']:7.2f}  {rows[-1]['plaintext_head']}  "
                  f"[{time.time() - t0:.0f}s]", flush=True)
        rows.sort(key=lambda r: r["score"], reverse=True)
        write_csv(out, rows)

    report("粗扫", rows)

    print(f"\n精扫：粗扫前 {args.refine_top} 名，每个 {args.refine_restarts} 次重启 × {args.refine_sweeps} 次扫描",
          flush=True)
    refined = [run(r["scheme"], args.refine_restarts, args.refine_sweeps) for r in rows[:args.refine_top]]
    refined.sort(key=lambda r: r["score"], reverse=True)
    write_csv(Path(args.refine_out), refined)
    for rank, r in enumerate(refined, 1):
        print(f"  {rank}. {r['scheme']:>7} {r['score']:.2f}  {r['plaintext_head']}")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"已写入 {path}")


def report(title: str, rows: list[dict]) -> None:
    scores = [r["score"] for r in rows]
    mean = sum(scores) / len(scores)
    sd = (sum((s - mean) ** 2 for s in scores) / (len(scores) - 1)) ** 0.5
    print(f"\n{title}：{len(rows)} 个候选，得分均值 {mean:.2f} ± {sd:.2f}；前 5 名：")
    for rank, r in enumerate(rows[:5], 1):
        print(f"  {rank}. {r['scheme']:>7} {r['score']:.2f}（z = {(r['score'] - mean) / sd:.1f}）{r['plaintext_head']}")


if __name__ == "__main__":
    main()

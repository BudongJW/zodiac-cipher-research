"""M3：用统一标准为历次 Z13 / Z32 破译声明打分。

对 data/claims.json 中每条声明计算：
    1. 与密文的一致性（同音替换 / 简单替换条件；至少需假设的加密错误数）
    2. 在与 Z408 / Z340 共有的符号上，与已知密钥的一致程度（及偶然一致的概率）
    3. 语言得分：声明明文在强语言模型下的目标函数值，与“无约束求解”能达到的得分比较
    4. 重复模式的基准符合率：普通英文片段有多大比例同样符合（=“符合”本身的证据上限）
    5. 额外自由度（变位、多步变换、通配符等）
并给出分级：
    A  符合密文且有独立证据（例如与已知密钥的一致远超偶然，且密钥并非由声明者据此构造）
    B  符合密文，但证据价值低（模式约束弱 / 语言得分不高于无约束求解 / 事后构造）
    C  需额外假设（加密错误、通配符、空符等）才能与密文一致
    D  无法逐位验证（变位、多步变换、含数字、长度不符）——不可证伪

用法：
    python scripts/m3_evaluate_claims.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import get_model, stdlib_english  # noqa: E402
from zkc.evaluate import consistency, key_agreement, pattern_base_rate  # noqa: E402
from zkc.reproduce import reference_key  # noqa: E402
from zkc.solver import DEFAULT_ENTROPY_WEIGHT, objective, solve  # noqa: E402
from zkc.stats import entropy_bits  # noqa: E402
from zkc.synth import zodiac_plaintexts  # noqa: E402


def baseline_spurious(length: int) -> float | None:
    """M2 基线中该长度的“错误解胜出率”。"""
    path = ROOT / "results" / "m2_baseline.csv"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if int(r["length"]) == length]
    return sum(int(r["spurious"]) for r in rows) / len(rows) if rows else None


def grade(c: dict) -> str:
    if c["plaintext"] is None:
        return "D"
    if not c["fits_homophonic"] or c["wildcards"]:
        return "C"
    independent_key = c.get("key_source") is None and (
        c["z340_p"] < 1e-3 or c["z408_p"] < 1e-3)
    return "A" if independent_key else "B"


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--restarts", type=int, default=32)
    p.add_argument("--sweeps", type=int, default=1000)
    p.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    p.add_argument("--out", default="results/m3_claims.csv")
    args = p.parse_args()

    model = get_model(args.model)
    w = DEFAULT_ENTROPY_WEIGHT
    claims = json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))["claims"]
    keys = {"z340": reference_key("z340"), "z408": reference_key("z408")}
    english = zodiac_plaintexts() + [stdlib_english()]

    context = {}
    for name in ("z13", "z32"):
        cipher = load(name).text
        free = solve(cipher, model, restarts=args.restarts, sweeps=args.sweeps, seed=1, jobs=args.jobs)
        base = pattern_base_rate(cipher, english)
        context[name] = {"cipher": cipher, "free_best": free[0].score, "free_best_text": free[0].plaintext,
                         "free_scores": [r.score for r in free], "base_rate": base,
                         "spurious": baseline_spurious(len(cipher))}
        print(f"{name}：无约束求解最佳得分 {free[0].score:.1f}（{free[0].plaintext}）；"
              f"英文片段模式符合率 {base['fits']}/{base['windows']:,}；"
              f"M2 基线错误解胜出率 {context[name]['spurious']}", flush=True)

    rows = []
    for claim in claims:
        ctx = context[claim["cipher"]]
        row = {"id": claim["id"], "cipher": claim["cipher"], "claimant": claim["claimant"],
               "year": claim["year"], "claimed": claim["claimed"], "plaintext": claim["plaintext"],
               "key_source": claim.get("key_source"),
               "wildcards": any("通配" in f or "空符" in f for f in claim["freedoms"]),
               "freedoms": "；".join(claim["freedoms"])}
        plain = claim["plaintext"]
        if plain is not None:
            cons = consistency(ctx["cipher"], plain)
            score = objective(model.score(plain), entropy_bits(plain), w)
            row.update(fits_homophonic=cons["fits_homophonic"], fits_simple=cons["fits_simple"],
                       min_errors=cons["min_errors"],
                       conflicts=json.dumps(cons["conflicts"], ensure_ascii=False) if cons["conflicts"] else "",
                       score=round(score, 2), free_best=round(ctx["free_best"], 2),
                       beaten_by_free=sum(s > score for s in ctx["free_scores"]) / len(ctx["free_scores"]))
            for kname, key in keys.items():
                ka = key_agreement(ctx["cipher"], plain, key)
                row[f"{kname}_agree"] = f"{ka['matches']}/{ka['shared_positions']}"
                row[f"{kname}_expected"] = round(ka["expected"], 2)
                row[f"{kname}_p"] = ka["p_value"]
        else:
            row.update(fits_homophonic=None, fits_simple=None, min_errors=None, conflicts="", score=None,
                       free_best=round(ctx["free_best"], 2), beaten_by_free=None,
                       z340_agree=None, z340_expected=None, z340_p=None,
                       z408_agree=None, z408_expected=None, z408_p=None)
        row["grade"] = grade(row)
        rows.append(row)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "results" / "m3_context.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "free_scores"} for k, v in context.items()},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'声明':<20}{'分级':>4}{'同音':>6}{'错误':>6}{'得分':>8}{'被无约束解超过':>14}{'Z340一致':>10}{'Z408一致':>10}")
    for r in rows:
        fmt = lambda v, f="": "—" if v is None else format(v, f)  # noqa: E731
        print(f"{r['id']:<20}{r['grade']:>4}{fmt(r['fits_homophonic']):>6}{fmt(r['min_errors']):>6}"
              f"{fmt(r['score'], '.1f'):>8}{fmt(r['beaten_by_free'], '.0%'):>14}"
              f"{fmt(r['z340_agree']):>10}{fmt(r['z408_agree']):>10}")
    print(f"\n已写入 {args.out}、results/m3_context.json")


if __name__ == "__main__":
    main()

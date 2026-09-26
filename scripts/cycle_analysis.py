"""方向 F：同音符号轮换——Zodiac 自己的加密习惯能否为 Z32 提供新的约束？（探索性分析）

步骤：
    1. 度量 Z408、Z340 的轮换强度（明文阅读顺序 vs 密文书写顺序）；
    2. 拟合“带错误的轮换”模型的错误率 ε；
    3. 功效检验：用该模型加密 32 字母的 Zodiac 明文，看真实明文在“同样符合重复模式的
       普通英文片段”中按轮换似然排第几——即这一约束在 32 字符下有没有区分力；
    4. 对 Z32 的 B 级声明与“弧度 + 英寸”文法候选计算轮换似然，并给出其在基准分布中的百分位。

用法：python scripts/cycle_analysis.py [--trials 60]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from m3_z32_grammar import phrases  # noqa: E402

from zkc.cipher import ROOT, load, load_solution  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import stdlib_english  # noqa: E402
from zkc.cycles import (cycle_loglik, fit_epsilon, homophone_prior, letter_sequences,  # noqa: E402
                        shuffle_test)
from zkc.names import fits  # noqa: E402
from zkc.ngram import ALPHABET, encode  # noqa: E402
from zkc.synth import homophone_counts, sample_window, zodiac_plaintexts  # noqa: E402
from zkc.transpose import untranspose, z340_order  # noqa: E402

Z32_CLAIMS = {
    "Grinell 2020": "ESTIMATEFOURRADIANSANDFIVEINCHES",
    "Cragle": "THREERADIANSFROMMOUNTAREATWOINCH",
    "DMW 2019 / Stampher": "INTHREEANDTHREEEIGHTHSRADIANSTEN",
    "Reese（密文顺序）": "AERIEHDETARNRHISTXHDITNSHASGENIE",
    "Burke 2018": "COUPLEDWITHTHEMAPINWDVCINCHESTWO",
    "Burke 2019": "OKAYISEVENINSSOUTHOFDIABLOMTPEAK",
}


def fitting_windows(codes: np.ndarray, cipher: str, min_distinct: int = 6) -> list[int]:
    """语料中所有符合 cipher 重复模式（同音替换条件）的片段起点（向量化）。"""
    n = len(cipher)
    m = len(codes) - n + 1
    ok = np.ones(m, dtype=bool)
    groups: dict = {}
    for i, s in enumerate(cipher):
        groups.setdefault(s, []).append(i)
    for pos in groups.values():
        for j in pos[1:]:
            ok &= codes[pos[0]:pos[0] + m] == codes[j:j + m]
    starts = np.flatnonzero(ok)
    return [int(s) for s in starts if len(set(codes[s:s + n].tolist())) >= min_distinct]


def encrypt_cycle(plain: str, counts: dict, eps: float, rng: random.Random) -> list[str]:
    """按轮换模型加密：每个字母有 counts[字母] 个同音符号（记作 “字母+序号”）。"""
    pointer = {L: rng.randrange(counts[L]) for L in counts}
    out = []
    for ch in plain:
        k = counts[ch]
        idx = pointer[ch] % k if rng.random() >= eps else rng.randrange(k)
        pointer[ch] += 1
        out.append(f"{ch}{idx}")
    return out


def decode(codes) -> str:
    return "".join(ALPHABET[int(c)] for c in codes)


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=60)
    p.add_argument("--alternatives", type=int, default=300)
    args = p.parse_args()
    rng = random.Random(0)
    results: dict = {}

    # 1. 轮换强度
    z408c, z408p = load("z408").text, load_solution("z408_plaintext.txt")
    z340c = load("z340").text
    z340_written_p = load_solution("z340_plaintext_cipher_order.txt")
    z340_read_c = untranspose(z340c, z340_order())
    z340_read_p = load_solution("z340_plaintext.txt")
    views = {
        "Z408（书写 = 阅读顺序）": letter_sequences(z408c, z408p),
        "Z340 阅读顺序": letter_sequences(z340_read_c, z340_read_p),
        "Z340 书写顺序（逐行）": letter_sequences(z340c, z340_written_p),
    }
    results["cycling"] = {}
    for name, seqs in views.items():
        t = shuffle_test(seqs)
        results["cycling"][name] = t
        print(f"{name}：后继一致率 {t['observed']:.3f}（随机 {t['null_mean']:.3f} ± {t['null_sd']:.3f}，"
              f"z = {t['z']:.1f}）", flush=True)

    # 2. 拟合 ε
    eps = {"Z408": fit_epsilon(views["Z408（书写 = 阅读顺序）"]),
           "Z340": fit_epsilon(views["Z340 书写顺序（逐行）"])}
    results["epsilon"] = eps
    print(f"拟合的错误率 ε：Z408 {eps['Z408']:.2f}，Z340（书写顺序）{eps['Z340']:.2f}", flush=True)

    # 语料
    corpus = encode(" ".join(zodiac_plaintexts()) + stdlib_english())
    prior = homophone_prior()
    counts = homophone_counts("z340")

    # 3. 功效检验
    results["power"] = {}
    for label, e in eps.items():
        ranks = []
        for t in range(args.trials):
            trng = random.Random(f"power-{label}-{t}")
            plain = sample_window(zodiac_plaintexts(), 32, trng)
            cipher = encrypt_cycle(plain, counts, e, trng)
            starts = fitting_windows(corpus, cipher)
            alts = [decode(corpus[s:s + 32]) for s in starts]
            alts = [a for a in alts if a != plain]
            if len(alts) > args.alternatives:
                alts = trng.sample(alts, args.alternatives)
            if len(alts) < 20:
                continue
            truth = cycle_loglik(cipher, plain, e, prior)
            scores = [cycle_loglik(cipher, a, e, prior) for a in alts]
            ranks.append(sum(s >= truth for s in scores) / len(scores))
        ranks.sort()
        res = {"trials": len(ranks), "median_percentile": ranks[len(ranks) // 2] if ranks else None,
               "p_top10": sum(r <= 0.10 for r in ranks) / len(ranks) if ranks else None,
               "p_top1": sum(r <= 0.01 for r in ranks) / len(ranks) if ranks else None}
        results["power"][label] = res
        print(f"功效（ε = {e:.2f}，{label} 式）：{res['trials']} 次试验，真实明文轮换似然的中位百分位 "
              f"{res['median_percentile']:.2f}；进入前 10% 的比例 {res['p_top10']:.2f}，前 1% {res['p_top1']:.2f}",
              flush=True)

    # 3b. 真实数据验证（无循环论证）：Z408 / Z340 书写顺序中的 32 字符窗口，真实明文 vs 同样符合模式的英文片段
    results["real_windows"] = {}
    # 留一法：验证 Z408 时只用 Z340 密钥构造先验，反之亦然；另以 ε = 1（完全不轮换）作消融对照
    real = {"Z408": (z408c, z408p, homophone_prior(("z340",))),
            "Z340（书写顺序）": (z340c, z340_written_p, homophone_prior(("z408",)))}
    for label, e in list(eps.items()) + [("无轮换消融", 1.0)]:
        for rname, (c, pl, prior_loo) in real.items():
            ranks = []
            for s0 in range(0, len(c) - 32 + 1, 4):
                cw, pw = c[s0:s0 + 32], pl[s0:s0 + 32]
                alts = [decode(corpus[s:s + 32]) for s in fitting_windows(corpus, cw)]
                alts = [a for a in alts if a != pw]
                if len(alts) > args.alternatives:
                    alts = rng.sample(alts, args.alternatives)
                if len(alts) < 20:
                    continue
                truth = cycle_loglik(cw, pw, e, prior_loo)
                scores = [cycle_loglik(cw, a, e, prior_loo) for a in alts]
                ranks.append(sum(s >= truth for s in scores) / len(scores))
            ranks.sort()
            res = {"windows": len(ranks),
                   "median_percentile": ranks[len(ranks) // 2] if ranks else None,
                   "p_top10": sum(r <= 0.10 for r in ranks) / len(ranks) if ranks else None}
            results["real_windows"][f"{rname}/ε={e:.2f}"] = res
            if ranks:
                print(f"真实数据验证 {rname}（ε = {e:.2f}）：{len(ranks)} 个窗口，真实明文的中位百分位 "
                      f"{res['median_percentile']:.2f}，进入前 10% 的比例 {res['p_top10']:.2f}", flush=True)
            else:
                print(f"真实数据验证 {rname}（ε = {e:.2f}）：没有备选足够多的窗口", flush=True)

    # 3c. 更严格的合成检验：各字母同音数在先验范围内随机取值（不再与打分所用的 Z340 同音数一致）
    results["power_random_k"] = {}
    for label, e in eps.items():
        ranks = []
        for t in range(args.trials * 3):
            trng = random.Random(f"power-rk-{label}-{t}")
            rk = {L: trng.choice(prior[L]) for L in prior}
            plain = sample_window(zodiac_plaintexts(), 32, trng)
            cipher = encrypt_cycle(plain, rk, e, trng)
            alts = [decode(corpus[s:s + 32]) for s in fitting_windows(corpus, cipher)]
            alts = [a for a in alts if a != plain]
            if len(alts) > args.alternatives:
                alts = trng.sample(alts, args.alternatives)
            if len(alts) < 20:
                continue
            truth = cycle_loglik(cipher, plain, e, prior)
            scores = [cycle_loglik(cipher, a, e, prior) for a in alts]
            ranks.append(sum(s >= truth for s in scores) / len(scores))
        ranks.sort()
        res = {"trials": len(ranks), "median_percentile": ranks[len(ranks) // 2] if ranks else None,
               "p_top10": sum(r <= 0.10 for r in ranks) / len(ranks) if ranks else None}
        results["power_random_k"][label] = res
        if ranks:
            print(f"严格合成检验（ε = {e:.2f}，同音数随机）：{len(ranks)} 次，中位百分位 {res['median_percentile']:.2f}，"
                  f"前 10% 比例 {res['p_top10']:.2f}", flush=True)

    # 4. Z32：基准分布、声明与文法候选
    z32 = load("z32").text
    starts = fitting_windows(corpus, z32)
    base_texts = [decode(corpus[s:s + 32]) for s in starts]
    grammar = sorted({t for t, _, _ in phrases(32)[0] if fits(t, z32)})
    results["z32"] = {"baseline_windows": len(base_texts), "grammar_candidates": len(grammar)}
    for label, e in eps.items():
        base = np.array([cycle_loglik(z32, t, e, prior) for t in base_texts])
        pct = lambda x: float((base >= x).mean())  # noqa: E731
        claims = {k: cycle_loglik(z32, v, e, prior) for k, v in Z32_CLAIMS.items()}
        gram = sorted(((cycle_loglik(z32, t, e, prior), t) for t in grammar), reverse=True)
        results["z32"][label] = {
            "baseline_mean": float(base.mean()), "baseline_sd": float(base.std()),
            "claims": {k: {"loglik": v, "percentile": pct(v)} for k, v in claims.items()},
            "grammar_top": [{"text": t, "loglik": s, "percentile": pct(s)} for s, t in gram[:10]],
            "grammar_percentiles": [pct(s) for s, _ in gram],
        }
        print(f"\nZ32（ε = {e:.2f}，{label} 式）：基准 {len(base_texts)} 个符合模式的英文片段，"
              f"轮换对数似然 {base.mean():.2f} ± {base.std():.2f}", flush=True)
        for k, v in claims.items():
            print(f"  {k:<22} {v:7.2f}  百分位 {pct(v):.2f}（越小越好）", flush=True)
        print(f"  文法候选 {len(grammar)} 条中最佳：" + "；".join(f"{t}（{s:.2f}，{pct(s):.2f}）" for s, t in gram[:3]),
              flush=True)

    out = ROOT / "results" / "cycle_analysis.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

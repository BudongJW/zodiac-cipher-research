"""命令行入口：python -m zkc <命令> ...

    stats NAME        统计量（长度、符号数、多重度、同构模式、周期双字母重复、置换检验）
    overlap           四份密文的符号重合表
    verify            确定性复现 Z408 / Z340 的已知解
    solve NAME        同音替换盲解（Z340 默认先按已发表方案去除换位）
    score NAME TEXT   按 M3 标准为一条新的破译声明打分
    build-model       由语料构建 n-gram 模型
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from . import stats
from .cipher import KNOWN, load
from .console import utf8_stdio
from .corpus import get_model
from .keys import format_key


def _cmd_stats(args) -> None:
    c = load(args.name)
    s = stats.summary(c.text)
    print(f"{c.name}: 长度 {s['length']}，{c.height} 行，不同符号 {s['distinct']}，"
          f"多重度 {s['multiplicity']:.3f}，单次出现符号 {s['singletons']}，"
          f"IoC {s['ioc']:.4f}，熵 {s['entropy_bits']:.3f} bits")
    if s["length"] <= 64:
        print("同构模式：", " ".join(map(str, s["isomorph"])))
        print("重复符号：", ", ".join(f"{k}{v}" for k, v in s["repeated"].items()) or "无")
    if s["length"] > args.periods:
        profile = stats.period_profile(c.text, range(1, args.periods + 1))
        top = sorted(profile.items(), key=lambda kv: -kv[1])[:5]
        print("周期双字母重复（前 5）：", ", ".join(f"p{p}={v}" for p, v in top))
        if args.shuffle:
            best_p = top[0][0]
            t = stats.shuffle_test(c.text, lambda seq: stats.bigram_repeats(seq, best_p),
                                   trials=args.shuffle, seed=0)
            print(f"置换检验 p{best_p}：观测 {t['observed']}，打乱均值 {t['mean']:.2f} ± {t['sd']:.2f}，"
                  f"z = {t['z']:.2f}，p ≈ {t['p']:.2g}（{args.shuffle} 次）")


def _cmd_overlap(args) -> None:
    texts = {n: load(n).text for n in KNOWN}
    table = stats.overlap_table(texts)
    print("      " + "".join(f"{n:>6}" for n in KNOWN))
    for a in KNOWN:
        print(f"{a:>6}" + "".join(f"{table[(a, b)]:>6}" for b in KNOWN))
    solved = set(texts["z408"]) | set(texts["z340"])
    for n in ("z13", "z32"):
        print(f"{n} 中未见于 Z408/Z340 的符号：{''.join(sorted(set(texts[n]) - solved))}")


def _cmd_verify(args) -> None:
    from .reproduce import verify_z340, verify_z408
    ok = True
    for v in (verify_z408(), verify_z340()):
        ok &= v.plaintext_matches
        print(f"{v.name}: 长度 {v.length}，符号 {v.symbols}，密钥自洽 {v.key_consistent}，"
              f"与已知明文逐字一致 {v.plaintext_matches}" + (f"（{v.note}）" if v.note else ""))
    sys.exit(0 if ok else 1)


def _cmd_solve(args) -> None:
    from .keys import plaintext_accuracy
    from .reproduce import reference_key, solver_input
    from .solver import solve

    model = get_model(args.model)
    text = solver_input(args.name, args.transposition)
    print(f"模型 {model.name}（n={model.n}），密文 {args.name}，长度 {len(text)}，"
          f"换位 {args.transposition}，重启 {args.restarts}，扫描 {args.sweeps}")
    t0 = time.time()
    results = solve(text, model, restarts=args.restarts, sweeps=args.sweeps,
                    t_start=args.t_start, t_end=args.t_end, entropy_weight=args.weight,
                    seed=args.seed, jobs=args.jobs)
    print(f"用时 {time.time() - t0:.1f}s")
    ref = reference_key(args.name) if args.name in ("z408", "z340") else None
    cipher = load(args.name).text
    for rank, r in enumerate(results[:args.top], 1):
        acc = f"，准确率 {plaintext_accuracy(cipher, r.key, ref):.1%}" if ref else ""
        print(f"\n#{rank} 得分 {r.score:.2f}（n-gram {r.ngram_mean:.1f}，熵 {r.entropy:.3f}）{acc}")
        for i in range(0, len(r.plaintext), 17):
            print("   ", r.plaintext[i:i + 17])
    if args.show_key and results:
        print("\n密钥（明文字母: 符号）：\n" + format_key(results[0].key))


def _cmd_score(args) -> None:
    from .corpus import stdlib_english
    from .evaluate import score_claim
    from .names import letters_only
    from .reproduce import reference_key
    from .solver import solve
    from .synth import zodiac_plaintexts

    cipher = load(args.name).text
    for sym in args.drop:
        cipher = cipher.replace(sym, "")
    plain = letters_only(args.plaintext)
    reading = letters_only(args.reading) if args.reading else None
    if len(plain) != len(cipher):
        sys.exit(f"明文 {len(plain)} 个字母，密文 {len(cipher)} 个符号，长度不一致——无法逐位评估（D 级）")
    model = get_model(args.model)
    free = None
    if not args.no_free:
        free = [r.score for r in solve(cipher, model, restarts=args.free_restarts, sweeps=1000,
                                       seed=1, jobs=args.jobs)]
    english = None if args.no_base_rate else zodiac_plaintexts() + [stdlib_english()]
    r = score_claim(cipher, plain, reading=reading,
                    references={"z340": reference_key("z340"), "z408": reference_key("z408")},
                    key_source=args.key_source, extra_assumptions=args.extra or bool(args.drop),
                    english=english, model=model, free_scores=free)

    print(f"密文 {args.name}（{len(cipher)} 符号{'，删去 ' + args.drop if args.drop else ''}）｜声明 {plain}")
    print(f"同音替换条件：{'符合' if r['fits_homophonic'] else '不符合'}；简单替换条件："
          f"{'符合' if r['fits_simple'] else '不符合'}；至少需假设的加密错误：{r['min_errors']}")
    if r["conflicts"]:
        print("  冲突：" + "；".join(f"{s}→{'/'.join(v)}" for s, v in r["conflicts"].items()))
    for k in ("z340", "z408"):
        ka = r[f"key_{k}"]
        tag = "（读法据此构造，不计为独立证据）" if k == args.key_source else ""
        print(f"与 {k.upper()} 密钥一致：{ka['matches']}/{ka['shared_positions']}（偶然期望 {ka['expected']:.2f}，"
              f"p = {ka['p_value']:.3g}）{tag}")
    if "pattern_base_rate" in r:
        b = r["pattern_base_rate"]
        print(f"模式基准率：普通英文片段 {b['fits']:,} / {b['windows']:,} 同样符合（{b['rate']:.2e}）")
    print(f"语言得分（模型 {model.name}）：{r['language_score']:.1f}"
          + (f"；无约束求解最佳 {r['free_best']:.1f}，{r['beaten_by_free']:.0%} 的无约束解得分更高"
             if free else ""))
    print(f"分级：{r['grade']}（A 符合且有独立证据 / B 符合但证据价值低 / C 需额外假设 / D 无法逐位验证）")


def _cmd_build_model(args) -> None:
    from pathlib import Path

    from .corpus import builtin_model
    from .ngram import NgramModel
    if args.corpus:
        text = Path(args.corpus).read_text(encoding="utf-8", errors="replace")
        model = NgramModel.from_corpus(text, args.n, name=Path(args.corpus).stem)
        out = Path(args.out or f"models/{Path(args.corpus).stem}-{args.n}gram.bin")
        model.save(out)
    else:
        model = builtin_model(args.n)
        out = f"models/{model.name}.bin"
    print(f"已生成 {out}：n={model.n}，非零项 {(model.table > 0).mean():.2%}")


def main(argv=None) -> None:
    utf8_stdio()
    p = argparse.ArgumentParser(prog="python -m zkc", description="Zodiac 密文分析工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stats", help="统计量")
    s.add_argument("name", help="z408 / z340 / z13 / z32 或文件路径")
    s.add_argument("--periods", type=int, default=40)
    s.add_argument("--shuffle", type=int, default=0, help="置换检验次数（0 = 不做）")
    s.set_defaults(func=_cmd_stats)

    s = sub.add_parser("overlap", help="符号重合表")
    s.set_defaults(func=_cmd_overlap)

    s = sub.add_parser("verify", help="确定性复现 Z408 / Z340")
    s.set_defaults(func=_cmd_verify)

    s = sub.add_parser("solve", help="同音替换盲解")
    s.add_argument("name")
    s.add_argument("--model", default="builtin:4", help="builtin:4 或 AZdecrypt n-gram 文件路径")
    s.add_argument("--transposition", default="auto", choices=["auto", "none", "z340"])
    s.add_argument("--restarts", type=int, default=8)
    s.add_argument("--sweeps", type=int, default=2000)
    s.add_argument("--t-start", type=float, default=2.0)
    s.add_argument("--t-end", type=float, default=0.02)
    s.add_argument("--weight", type=float, default=2.0, help="熵权重 w")
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    s.add_argument("--top", type=int, default=3)
    s.add_argument("--show-key", action="store_true")
    s.set_defaults(func=_cmd_solve)

    s = sub.add_parser("score", help="按 M3 标准为一条新的破译声明打分")
    s.add_argument("name", help="z13 / z32 或文件路径")
    s.add_argument("plaintext", help="与密文逐位对应的明文（密文顺序，空格与标点会被忽略）")
    s.add_argument("--reading", help="声明含换位时，阅读顺序的明文（用于语言得分）")
    s.add_argument("--drop", default="", help="声明视为空符而删去的符号，如 0（圈 8）")
    s.add_argument("--key-source", choices=["z340", "z408"], help="读法据以构造的已知密钥")
    s.add_argument("--extra", action="store_true", help="声明需要额外假设（错误、通配符等）")
    s.add_argument("--model", default="auto", help="auto / builtin:4 / n-gram 文件路径")
    s.add_argument("--free-restarts", type=int, default=16)
    s.add_argument("--no-free", action="store_true", help="跳过无约束求解对照")
    s.add_argument("--no-base-rate", action="store_true", help="跳过模式基准率（较慢）")
    s.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    s.set_defaults(func=_cmd_score)

    s = sub.add_parser("build-model", help="构建 n-gram 模型")
    s.add_argument("--n", type=int, default=4)
    s.add_argument("--corpus", help="语料文本文件（省略则使用内置标准库语料）")
    s.add_argument("--out")
    s.set_defaults(func=_cmd_build_model)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

"""命令行入口：python -m zkc <命令> ...

    stats NAME        统计量（长度、符号数、多重度、同构模式、周期双字母重复、置换检验）
    overlap           四份密文的符号重合表
    verify            确定性复现 Z408 / Z340 的已知解
    solve NAME        同音替换盲解（Z340 默认先按已发表方案去除换位）
    build-model       由语料构建 n-gram 模型
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from . import stats
from .cipher import KNOWN, load
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
    for stream in (sys.stdout, sys.stderr):  # Windows 管道默认编码可能不支持中文
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
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

    s = sub.add_parser("build-model", help="构建 n-gram 模型")
    s.add_argument("--n", type=int, default=4)
    s.add_argument("--corpus", help="语料文本文件（省略则使用内置标准库语料）")
    s.add_argument("--out")
    s.set_defaults(func=_cmd_build_model)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

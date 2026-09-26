"""H005：Z32 是否使用了 Z340 / Z408 密钥的简单变换（字母移位或 Atbash）？预注册见 hypotheses/H005-z32-key-transforms.md。

用法：python scripts/h005_key_transforms.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
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

from m4_key_reuse import best_fill, permuted_key  # noqa: E402

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import get_model  # noqa: E402
from zkc.ngram import ALPHABET  # noqa: E402
from zkc.reproduce import reference_key  # noqa: E402
from zkc.transpose import ragged_grid_orders, untranspose  # noqa: E402

TRANSFORMS = {f"shift+{k}": (lambda c, k=k: ALPHABET[(ALPHABET.index(c) + k) % 26]) for k in range(1, 26)}
TRANSFORMS["atbash"] = lambda c: ALPHABET[25 - ALPHABET.index(c)]


def best_over(key: dict[str, str], texts: dict[str, str], model, rng, starts: int) -> tuple[float, str, str, str]:
    best = (-1.0, "", "", "")
    for tname, f in TRANSFORMS.items():
        tkey = {s: f(l) for s, l in key.items()}
        for oname, text in texts.items():
            r = best_fill(text, tkey, model, rng, starts=starts)
            if r["score"] > best[0]:
                best = (r["score"], tname, oname, r["text"])
    return best


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--null", type=int, default=100)
    p.add_argument("--null-z408", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    model = get_model(args.model)
    rng = random.Random(args.seed)
    z32 = load("z32")
    orders = ragged_grid_orders([len(r) for r in z32.rows])
    texts = {name: untranspose(z32.text, o) for name, o in orders.items()}
    results = {}
    for kname in ("z340", "z408"):
        key = reference_key(kname)
        score, tname, oname, text = best_over(key, texts, model, rng, starts=8)
        n_null = args.null if kname == "z340" else args.null_z408
        null = [best_over(permuted_key(key, rng), texts, model, rng, starts=3)[0] for _ in range(n_null)]
        pval = (sum(s >= score for s in null) + 1) / (n_null + 1)
        results[kname] = {"best_score": score, "transform": tname, "order": oname, "text": text,
                          "null_mean": float(np.mean(null)), "null_sd": float(np.std(null)),
                          "null_n": n_null, "p_value": pval}
        print(f"{kname}：最佳 {tname} / {oname} → {text}（{score:.1f}）；零假设 {np.mean(null):.1f} ± {np.std(null):.1f}；"
              f"p = {pval:.3f}", flush=True)
    out = ROOT / "results" / "h005_key_transforms.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

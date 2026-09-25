"""M4 / H001 与 H002：密钥复用假设（路线图方向 C）。

H001  Z32 是否用 Z340（或 Z408）的密钥加密，可能叠加简单换位？
H002  Z13 在 Z340（或 Z408）密钥下得到的框架（如 DREA_A_O__EDO，Garlick 读法的基础）
      是否比随机密钥下的框架更“像英文”？

方法：共有符号按已知密钥固定，其余符号（自由符号）穷举（≤ 2 个）或坐标上升搜索（> 2 个）；
以目标函数（5-gram × 熵项）的最高分为统计量。零假设：把已知密钥的字母在其符号间随机打乱
（保持字母分布不变）后重复同一流程，p 值 = 零假设最高分 ≥ 观测最高分的比例。
预注册见 hypotheses/H001-*.md、hypotheses/H002-*.md。

用法：
    python scripts/m4_key_reuse.py --model models/5-grams_english_beijinghouse_10TB_v7.gz
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import get_model  # noqa: E402
from zkc.ngram import ALPHABET, NgramModel  # noqa: E402
from zkc.reproduce import reference_key  # noqa: E402
from zkc.solver import batch_objective  # noqa: E402
from zkc.synth import sample_window, zodiac_plaintexts  # noqa: E402
from zkc.transpose import ragged_grid_orders, transpose, untranspose  # noqa: E402

CODE = {ch: i for i, ch in enumerate(ALPHABET)}


def best_fill(text: str, key: dict[str, str], model: NgramModel, rng: random.Random,
              starts: int = 12, keep: int = 0) -> dict:
    """固定 key 中已有的符号，为其余符号选字母使目标函数最大。

    自由符号 ≤ 2 个时穷举（keep > 0 时返回前 keep 名），否则多起点坐标上升。
    """
    free = [s for s in dict.fromkeys(text) if s not in key]
    base = np.array([CODE[key[s]] if s in key else 0 for s in text], dtype=np.int64)
    slots = [np.array([i for i, s in enumerate(text) if s == f]) for f in free]

    def render(assign) -> np.ndarray:
        row = base.copy()
        for pos, letter in zip(slots, assign):
            row[pos] = letter
        return row

    if len(free) <= 2:
        assigns = list(itertools.product(range(26), repeat=len(free)))
        scores = batch_objective(np.stack([render(a) for a in assigns]), model)
        order = np.argsort(-scores)
        top = [("".join(ALPHABET[c] for c in render(assigns[i])), float(scores[i])) for i in order[:max(keep, 1)]]
        return {"score": top[0][1], "text": top[0][0], "free": free, "top": top if keep else None}

    best_score, best_assign = -1.0, None
    letters = np.arange(26)
    for _ in range(starts):
        assign = [rng.randrange(26) for _ in free]
        current = -1.0
        improved = True
        while improved:
            improved = False
            for k in range(len(free)):
                rows = []
                for letter in letters:
                    a = assign.copy()
                    a[k] = int(letter)
                    rows.append(render(a))
                scores = batch_objective(np.stack(rows), model)
                j = int(np.argmax(scores))
                if scores[j] > current + 1e-12:
                    improved = improved or assign[k] != j
                    assign[k], current = j, float(scores[j])
        if current > best_score:
            best_score, best_assign = current, assign
    return {"score": best_score, "text": "".join(ALPHABET[c] for c in render(best_assign)),
            "free": free, "top": None}


def permuted_key(key: dict[str, str], rng: random.Random) -> dict[str, str]:
    symbols, letters = list(key), list(key.values())
    rng.shuffle(letters)
    return dict(zip(symbols, letters))


def run_h002(model, keys, n_null, rng) -> dict:
    z13 = load("z13").text
    variants = {"原顺序": z13, "逆序": z13[::-1], "删去圈8": z13.replace("0", "")}
    out = {}
    for kname, key in keys.items():
        for vname, text in variants.items():
            obs = best_fill(text, key, model, rng, keep=26 ** 2)
            null = [best_fill(text, permuted_key(key, rng), model, rng)["score"] for _ in range(n_null)]
            p = (sum(s >= obs["score"] for s in null) + 1) / (n_null + 1)
            ranking = [t for t, _ in obs["top"]]
            out[f"{kname}/{vname}"] = {
                "frame": "".join(key.get(s, "_") for s in text), "best": obs["text"], "score": obs["score"],
                "top10": obs["top"][:10], "fills": len(ranking), "null_mean": float(np.mean(null)),
                "null_sd": float(np.std(null)), "null_n": n_null, "p_value": p}
            if kname == "z340" and vname == "原顺序":
                rank = ranking.index("DREATATOTPEDO") + 1
                out[f"{kname}/{vname}"]["garlick_rank"] = rank
                print(f"H002 Garlick 读法 DREATATOTPEDO 在 {len(ranking)} 种补全中排第 {rank}", flush=True)
            obs["top"] = obs["top"][:10]
            print(f"H002 {kname}/{vname}: 框架 {out[f'{kname}/{vname}']['frame']} 最佳 {obs['text']} "
                  f"{obs['score']:.1f}；零假设 {np.mean(null):.1f} ± {np.std(null):.1f}；p = {p:.3f}", flush=True)
            if obs["top"]:
                print("   前 10：", ", ".join(f"{t}({s:.1f})" for t, s in obs["top"]), flush=True)
    return out


def run_h001(model, keys, n_null, rng) -> dict:
    z32 = load("z32")
    orders = ragged_grid_orders([len(r) for r in z32.rows])
    texts = {name: untranspose(z32.text, order) for name, order in orders.items()}
    print(f"H001：{len(orders)} 种读取顺序", flush=True)
    out = {}
    for kname, key in keys.items():
        per_order = {name: best_fill(t, key, model, rng) for name, t in texts.items()}
        best_name = max(per_order, key=lambda k: per_order[k]["score"])
        obs = per_order[best_name]
        null = []
        for _ in range(n_null):
            pk = permuted_key(key, rng)
            null.append(max(best_fill(t, pk, model, rng, starts=4)["score"] for t in texts.values()))
        p = (sum(s >= obs["score"] for s in null) + 1) / (n_null + 1)
        out[kname] = {
            "free_symbols": per_order[best_name]["free"], "best_order": best_name, "best": obs["text"],
            "score": obs["score"], "null_mean": float(np.mean(null)), "null_sd": float(np.std(null)),
            "null_n": n_null, "p_value": p,
            "per_order": {k: {"score": round(v["score"], 2), "text": v["text"]} for k, v in per_order.items()}}
        print(f"H001 {kname}: 最佳顺序 {best_name} → {obs['text']} {obs['score']:.1f}；"
              f"零假设（各顺序取最大）{np.mean(null):.1f} ± {np.std(null):.1f}；p = {p:.3f}", flush=True)
    return out


def run_power(model, key, trials, threshold, rng) -> dict:
    """H001 的检验功效：若 32 字母的 Zodiac 明文确实用该密钥（同音轮换）加密，并经过候选族中
    随机一种换位，本检验的统计量能否超过零假设的 1% 阈值？密钥中没有的字母用新符号代替。"""
    homophones: dict[str, list[str]] = {}
    for sym, letter in key.items():
        homophones.setdefault(letter, []).append(sym)
    orders = ragged_grid_orders([17, 15])
    names = list(orders)
    scores = []
    for t in range(trials):
        plain = sample_window(zodiac_plaintexts(), 32, rng)
        turn = {ch: rng.randrange(len(s)) for ch, s in homophones.items()}
        cipher = []
        for i, ch in enumerate(plain):
            if ch in homophones:
                syms = homophones[ch]
                cipher.append(syms[turn[ch] % len(syms)])
                turn[ch] += 1
            else:
                cipher.append(chr(0x4E00 + i))  # 密钥中没有的字母 → 新符号
        cipher_t = transpose(cipher, orders[rng.choice(names)])
        scores.append(max(best_fill(untranspose(cipher_t, o), key, model, rng, starts=4)["score"]
                          for o in orders.values()))
    power = sum(s > threshold for s in scores) / trials
    print(f"功效检验：{trials} 次，统计量均值 {np.mean(scores):.1f}，超过阈值 {threshold:.1f} 的比例 {power:.2f}",
          flush=True)
    return {"trials": trials, "threshold": threshold, "mean": float(np.mean(scores)),
            "min": float(np.min(scores)), "power": power}


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--null-z13", type=int, default=2000)
    p.add_argument("--null-z32", type=int, default=200)
    p.add_argument("--power", type=int, default=0, help="只做 H001 功效检验（次数），读取已有结果中的零假设阈值")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    model = get_model(args.model)
    keys = {"z340": reference_key("z340"), "z408": reference_key("z408")}
    rng = random.Random(args.seed)
    out = ROOT / "results" / "m4_key_reuse.json"
    if args.power:
        results = json.loads(out.read_text(encoding="utf-8"))
        h001 = results["H001"]["z340"]
        threshold = h001["null_mean"] + 2.326 * h001["null_sd"]  # 正态近似的 1% 单侧阈值
        results["H001_power_z340"] = run_power(model, keys["z340"], args.power, threshold, rng)
        out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"已更新 {out.relative_to(ROOT)}")
        return
    results = {"H002": run_h002(model, keys, args.null_z13, rng),
               "H001": run_h001(model, keys, args.null_z32, rng)}
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

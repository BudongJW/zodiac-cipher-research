"""M2 / B2：Z13 姓名空间实验——“某个名字符合 Z13 的重复模式”本身值多少证据？

数据：1990 年美国人口普查姓名频率表（公有领域），需先下载到 external/names/：
    https://www2.census.gov/topics/genealogy/1990surnames/dist.male.first
    https://www2.census.gov/topics/genealogy/1990surnames/dist.female.first
    https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last

统计三种形式（字母总数须与密文长度相同）：名+姓、男性名+姓、名+中间名首字母+姓；
分别在同音替换条件与更严格的简单替换条件下计数，并按人口频率加权。
另以普通英文作对照：所有连续片段中有多大比例符合 Z13 的模式。
对四种读法做敏感性分析：原转录、圈8视为三个不同符号、删去圈8、第 11 位视为反写 N。

用法：python scripts/m2_z13_names.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.corpus import stdlib_english  # noqa: E402
from zkc.names import count_two_part_fits, fits  # noqa: E402
from zkc.ngram import ALPHABET  # noqa: E402
from zkc.synth import zodiac_plaintexts  # noqa: E402

NAMES_DIR = ROOT / "external" / "names"


def read_census(filename: str) -> dict[str, float]:
    """人口普查格式：名字 频率% 累计% 排名。"""
    out: dict[str, float] = {}
    for line in (NAMES_DIR / filename).read_text(encoding="ascii").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = out.get(parts[0], 0.0) + float(parts[1])
    return out


def window_fits(texts: list[str], cipher: str, min_distinct: int = 6) -> dict:
    """穷举语料中所有长度为 len(cipher) 的连续片段，统计符合者。

    不同字母少于 min_distinct 个的片段（如文档中的 “FFFFFFFFFFFFF”）视为退化片段，单独计数、不计入比率。
    """
    n = len(cipher)
    total, degenerate, hits = 0, 0, []
    for t in texts:
        for s in range(len(t) - n + 1):
            w = t[s:s + n]
            if len(set(w)) < min_distinct:
                degenerate += 1
                continue
            total += 1
            if fits(w, cipher):
                hits.append(w)
    return {"windows": total, "degenerate_skipped": degenerate, "fits": len(hits),
            "rate": len(hits) / total, "examples": sorted(set(hits))[:20]}


def variants(z13: str) -> dict[str, str]:
    """转录/解释的敏感性分析：不同读法下的“密文”。①②③④ 为互不相同的占位符号。"""
    return {
        "原转录": z13,
        "圈8视为三个不同符号": z13.replace("0", "①", 1).replace("0", "②", 1).replace("0", "③", 1),
        "删去圈8（视为空符）": z13.replace("0", ""),
        "第11位视为反写N（不同符号）": z13[:10] + "④" + z13[11:],
    }


def main() -> None:
    utf8_stdio()
    z13 = load("z13").text
    male, female = read_census("dist.male.first"), read_census("dist.female.first")
    first = dict(male)
    for k, v in female.items():
        first[k] = first.get(k, 0.0) + v
    last = read_census("dist.all.last")
    initials = {f + x: w / 26 for f, w in first.items() for x in ALPHABET}
    english = {"Zodiac 明文": zodiac_plaintexts(), "标准库英文": [stdlib_english()]}
    print(f"名 {len(first)}（男 {len(male)}、女 {len(female)}），姓 {len(last)}", flush=True)

    forms = {
        "名+姓": (first, last),
        "男性名+姓": (male, last),
        "名+中间名首字母+姓": (initials, last),
    }
    results = {}
    for vname, cipher in variants(z13).items():
        print(f"\n=== {vname}：{cipher}（长度 {len(cipher)}）", flush=True)
        res = results[vname] = {"cipher": cipher}
        for label, (f, l) in forms.items():
            for cond, simple in (("同音替换", False), ("简单替换", True)):
                r = count_two_part_fits(cipher, f, l, examples=15, simple=simple)
                res[f"{label}/{cond}"] = r
                print(f"{label}（{cond}）：组合 {r['pairs']:,}，符合 {r['fits']:,}"
                      f"（{r['fit_rate']:.2e}；加权 {r['weighted_fit_rate']:.2e}）"
                      f"  例：{', '.join(r['examples'][:6])}", flush=True)
        for k, texts in english.items():
            v = res[f"英文片段/{k}"] = window_fits(texts, cipher)
            print(f"英文片段对照（{k}）：{v['fits']:,} / {v['windows']:,} = {v['rate']:.2e}"
                  f"  例：{', '.join(v['examples'][:6])}", flush=True)

    out = ROOT / "results" / "m2_z13_names.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

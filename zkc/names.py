"""候选明文与密文重复模式的匹配（路线图方向 B2：Z13 姓名空间实验）。

同音替换下，“符合”密文的必要条件是：同一符号的所有位置必须是同一字母
（不同符号可以对应同一字母）。简单替换还要求不同符号对应不同字母。
"""

from __future__ import annotations

import heapq
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping


def letters_only(s: str) -> str:
    return re.sub(r"[^A-Z]", "", s.upper())


def fits(candidate: str, cipher: str, simple: bool = False) -> bool:
    """candidate（仅字母）能否作为 cipher 的明文。"""
    candidate = letters_only(candidate)
    if len(candidate) != len(cipher):
        return False
    sym_to_letter: dict[str, str] = {}
    for sym, ch in zip(cipher, candidate):
        if sym_to_letter.setdefault(sym, ch) != ch:
            return False
    return not simple or len(set(sym_to_letter.values())) == len(sym_to_letter)


def _groups(cipher: str) -> list[list[int]]:
    pos: dict[str, list[int]] = defaultdict(list)
    for i, sym in enumerate(cipher):
        pos[sym].append(i)
    return [p for p in pos.values() if len(p) > 1]


def count_two_part_fits(cipher: str, first: Mapping[str, float], last: Mapping[str, float],
                        examples: int = 20, simple: bool = False) -> dict:
    """统计“名 + 姓”（无空格拼接）符合 cipher 重复模式的组合（simple=True 时用简单替换条件）。

    first / last：{名字: 权重}（权重可为出现频数；只计数时全部为 1）。
    返回组合数、加权占比（相对全部“总长度相符”的组合）与权重最高的示例。
    按姓的长度分组，并以“跨越名/姓边界的约束位置上的字母”为键建立索引，避免 O(|名|×|姓|) 枚举。
    """
    n = len(cipher)
    groups = _groups(cipher)
    first = {letters_only(k): v for k, v in first.items() if letters_only(k)}
    last = {letters_only(k): v for k, v in last.items() if letters_only(k)}
    by_len_first: dict[int, dict[str, float]] = defaultdict(dict)
    for name, w in first.items():
        by_len_first[len(name)][name] = w
    by_len_last: dict[int, dict[str, float]] = defaultdict(dict)
    for name, w in last.items():
        by_len_last[len(name)][name] = w

    total_pairs = total_weight = fit_pairs = fit_weight = 0.0
    top: list[tuple[float, str]] = []  # 最小堆，保留权重最高的 examples 个
    for k, firsts in by_len_first.items():
        m = n - k
        lasts = by_len_last.get(m)
        if not lasts:
            continue
        total_pairs += len(firsts) * len(lasts)
        total_weight += sum(firsts.values()) * sum(lasts.values())
        # 每个重复组：在名内的位置、在姓内的位置
        split = [([i for i in g if i < k], [i - k for i in g if i >= k]) for g in groups]
        cross = [(fp[0], lp) for fp, lp in split if fp and lp]  # 跨界组：名中一个代表位置 → 姓中位置
        index: dict[tuple, list[tuple[str, float]]] = defaultdict(list)
        for name, w in lasts.items():
            if all(len({name[i] for i in lp}) == 1 for fp, lp in split if lp):
                index[tuple(name[lp[0]] for _, lp in cross)].append((name, w))
        for name, w in firsts.items():
            if not all(len({name[i] for i in fp}) == 1 for fp, lp in split if fp):
                continue
            for lname, lw in index.get(tuple(name[i] for i, _ in cross), ()):
                if simple and not fits(name + lname, cipher, simple=True):
                    continue
                fit_pairs += 1
                fit_weight += w * lw
                item = (w * lw, f"{name} {lname}")
                if len(top) < examples:
                    heapq.heappush(top, item)
                elif item > top[0]:
                    heapq.heapreplace(top, item)
    return {
        "pairs": int(total_pairs), "fits": int(fit_pairs),
        "fit_rate": fit_pairs / total_pairs if total_pairs else 0.0,
        "weighted_fit_rate": fit_weight / total_weight if total_weight else 0.0,
        "examples": [name for _, name in sorted(top, reverse=True)],
    }


def filter_fits(candidates: Iterable[str], cipher: str, simple: bool = False) -> list[str]:
    return [c for c in candidates if fits(c, cipher, simple)]

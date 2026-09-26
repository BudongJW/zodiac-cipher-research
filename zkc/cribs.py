"""已知 / 可能明文（crib）的放置分析。

同音替换下，把 crib 放在位置 i 的必要条件：窗口内同一符号对应同一字母，
且与已固定的符号 → 字母对应不冲突。不同符号可以对应同一字母，因此在重复很少的
短密文（如 Z32）中，几乎任何位置都能放下任何 crib——这正是 crib 在 Z32 上约束力很弱的原因。
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import product

from .names import letters_only


def _consistent(cipher: str, crib: str, pos: int, fixed: dict[str, str]) -> dict[str, str] | None:
    """在 pos 放置 crib；若与 fixed 及自身一致，返回扩展后的符号 → 字母映射，否则 None。"""
    mapping = dict(fixed)
    for sym, ch in zip(cipher[pos:pos + len(crib)], crib):
        if mapping.setdefault(sym, ch) != ch:
            return None
    return mapping


def placements(cipher: str, crib: str) -> list[int]:
    """crib 可以放置的全部位置（0 起）。"""
    crib = letters_only(crib)
    return [i for i in range(len(cipher) - len(crib) + 1) if _consistent(cipher, crib, i, {}) is not None]


def joint_placements(cipher: str, cribs: Sequence[str]) -> list[tuple[int, ...]]:
    """多个 crib 互不重叠、且符号 → 字母映射相互一致的全部放置组合。"""
    cribs = [letters_only(c) for c in cribs]
    single = [placements(cipher, c) for c in cribs]
    out = []
    for combo in product(*single):
        spans = sorted((p, p + len(c)) for p, c in zip(combo, cribs))
        if any(a[1] > b[0] for a, b in zip(spans, spans[1:])):
            continue
        mapping: dict[str, str] | None = {}
        for p, c in zip(combo, cribs):
            mapping = _consistent(cipher, c, p, mapping)
            if mapping is None:
                break
        if mapping is not None:
            out.append(combo)
    return out


def constrained_symbols(cipher: str, crib: str, pos: int) -> int:
    """在 pos 放置 crib 后，有多少个“窗口外也出现”的符号被连带确定（即 crib 对其余位置的信息量）。"""
    window = set(cipher[pos:pos + len(letters_only(crib))])
    outside = set(cipher[:pos]) | set(cipher[pos + len(letters_only(crib)):])
    return len(window & outside)

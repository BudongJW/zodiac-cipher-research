"""替换密钥：推导、应用与评估。"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping


class KeyConflict(ValueError):
    """同一符号对应了多个明文字母。"""

    def __init__(self, conflicts: dict[str, set[str]]):
        self.conflicts = conflicts
        detail = ", ".join(f"{s}→{sorted(v)}" for s, v in conflicts.items())
        super().__init__(f"密钥不一致：{detail}")


def derive_key(cipher_text: str, plain_text: str) -> dict[str, str]:
    """由逐位对齐的密文/明文推导替换密钥；若不一致则抛出 KeyConflict。"""
    if len(cipher_text) != len(plain_text):
        raise ValueError(f"长度不一致：{len(cipher_text)} vs {len(plain_text)}")
    seen: dict[str, set[str]] = defaultdict(set)
    for c, p in zip(cipher_text, plain_text):
        seen[c].add(p)
    conflicts = {c: v for c, v in seen.items() if len(v) > 1}
    if conflicts:
        raise KeyConflict(conflicts)
    return {c: next(iter(v)) for c, v in seen.items()}


def apply_key(cipher_text: str, key: Mapping[str, str], missing: str = "?") -> str:
    return "".join(key.get(c, missing) for c in cipher_text)


def plaintext_accuracy(cipher_text: str, key: Mapping[str, str],
                       reference: Mapping[str, str]) -> float:
    """按出现次数加权的准确率：解出的明文与参考明文逐位相同的比例。"""
    hits = sum(key.get(c) == reference.get(c) for c in cipher_text)
    return hits / len(cipher_text)


def symbol_accuracy(key: Mapping[str, str], reference: Mapping[str, str]) -> float:
    """按符号计的准确率：与参考密钥一致的符号比例。"""
    return sum(key.get(s) == v for s, v in reference.items()) / len(reference)


def format_key(key: Mapping[str, str]) -> str:
    """按明文字母分组显示密钥：A: 符号…"""
    groups: dict[str, list[str]] = defaultdict(list)
    for sym, letter in key.items():
        groups[letter].append(sym)
    return "\n".join(f"{letter}: {''.join(sorted(groups[letter]))}" for letter in sorted(groups))

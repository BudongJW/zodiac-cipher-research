"""合成密文：用“Zodiac 式”同音替换密钥加密英文，供可解性基线实验使用（路线图方向 B）。"""

from __future__ import annotations

import random
from collections import defaultdict

from .cipher import load_solution
from .ngram import ALPHABET
from .reproduce import reference_key

# 生成合成密钥时使用的符号池（与字母表分开，避免与明文混淆）
SYMBOL_POOL = [chr(0x3400 + i) for i in range(400)]


def zodiac_plaintexts() -> list[str]:
    """Zodiac 自己的英文：Z408 明文（去掉末尾 18 个填充字符）与 Z340 阅读顺序明文。"""
    return [load_solution("z408_plaintext.txt")[:-18], load_solution("z340_plaintext.txt")]


def homophone_counts(reference: str = "z340") -> dict[str, int]:
    """已知密钥中每个明文字母对应的同音符号数；密钥中没有的字母记为 1。"""
    counts: dict[str, int] = defaultdict(int)
    for letter in reference_key(reference).values():
        counts[letter] += 1
    return {ch: counts.get(ch, 0) or 1 for ch in ALPHABET}


def random_key(counts: dict[str, int], rng: random.Random) -> dict[str, list[str]]:
    """按给定的同音数为每个字母随机分配符号。"""
    pool = SYMBOL_POOL[:]
    rng.shuffle(pool)
    return {ch: [pool.pop() for _ in range(n)] for ch, n in counts.items()}


def encrypt(plain: str, key: dict[str, list[str]], policy: str, rng: random.Random) -> str:
    """policy = 'cycle'：同一字母的同音符号按顺序轮换（Z408 中观察到的习惯），起点随机；
    policy = 'random'：每次随机选一个同音符号。"""
    turn = {ch: rng.randrange(len(syms)) for ch, syms in key.items()}
    out = []
    for ch in plain:
        syms = key[ch]
        if policy == "cycle":
            out.append(syms[turn[ch] % len(syms)])
            turn[ch] += 1
        elif policy == "random":
            out.append(rng.choice(syms))
        else:
            raise ValueError(f"未知策略：{policy}")
    return "".join(out)


def sample_window(texts: list[str], length: int, rng: random.Random) -> str:
    """从语料中随机截取长度为 length 的连续片段。"""
    candidates = [t for t in texts if len(t) >= length]
    if not candidates:
        raise ValueError(f"语料中没有长度 ≥ {length} 的文本")
    text = rng.choice(candidates)
    start = rng.randrange(len(text) - length + 1)
    return text[start:start + length]

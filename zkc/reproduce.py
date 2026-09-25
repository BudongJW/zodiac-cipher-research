"""复现 Z408 / Z340 的已知解。

两个层次：
1. 确定性复现（verify_*）：由已知明文推导密钥，检查密钥自洽、与已发表的换位方案一致；
2. 盲解复现（blind_solve）：不使用任何明文信息，仅凭求解器 + 语言模型解出密文，
   再与已知密钥比较准确率。
"""

from __future__ import annotations

from dataclasses import dataclass

from .cipher import load, load_solution
from .keys import apply_key, derive_key, plaintext_accuracy
from .ngram import NgramModel
from .solver import SolveResult, solve
from .transpose import untranspose, z340_order


@dataclass
class Verification:
    name: str
    length: int
    symbols: int
    key_consistent: bool
    plaintext_matches: bool
    note: str = ""


def reference_key(name: str) -> dict[str, str]:
    """已知解的密钥（Z408：Harden 密钥；Z340：Oranchak/Blake/Van Eycke 密钥）。"""
    cipher = load(name).text
    if name == "z408":
        return derive_key(cipher, load_solution("z408_plaintext.txt"))
    if name == "z340":
        return derive_key(cipher, load_solution("z340_plaintext_cipher_order.txt"))
    raise ValueError(f"没有 {name} 的已知解")


def verify_z408() -> Verification:
    cipher = load("z408").text
    plain = load_solution("z408_plaintext.txt")
    key = reference_key("z408")
    return Verification("z408", len(cipher), len(key), True, apply_key(cipher, key) == plain)


def verify_z340() -> Verification:
    """密钥应用于密文后，再按已发表的换位方案读取，应逐字等于已知明文。"""
    cipher = load("z340").text
    key = reference_key("z340")
    reading = untranspose(apply_key(cipher, key), z340_order())
    return Verification("z340", len(cipher), len(key), True,
                        reading == load_solution("z340_plaintext.txt"),
                        note="换位：两段 (1,2) 抽取 + LIFEIS 跳读 + H 移位 + 末两行倒写片段")


def solver_input(name: str, transposition: str = "auto") -> str:
    """求解器的输入：Z340 默认先按已发表方案去除换位。"""
    if transposition not in ("auto", "none", "z340"):
        raise ValueError(f"未知换位方案：{transposition}")
    cipher = load(name).text
    if transposition == "none" or (transposition == "auto" and name != "z340"):
        return cipher
    if name != "z340":
        raise ValueError("z340 换位方案只适用于 Z340")
    return untranspose(cipher, z340_order())


def blind_solve(name: str, model: NgramModel, transposition: str = "auto",
                **solve_kwargs) -> tuple[list[SolveResult], list[float]]:
    """盲解并返回 (各次重启结果, 各结果相对已知密钥的逐位准确率)。"""
    text = solver_input(name, transposition)
    results = solve(text, model, **solve_kwargs)
    ref = reference_key(name)
    cipher = load(name).text
    return results, [plaintext_accuracy(cipher, r.key, ref) for r in results]

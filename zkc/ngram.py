"""字母 n-gram 语言模型。

表格为长度 26**n 的 uint8 数组，值为对数尺度分数（0 = 未见过），与 AZdecrypt 的
n-gram 格式一致，因此可以直接加载 AZdecrypt 附带的 n-gram 文件（二进制 / 文本 / .gz），
也可以从任意英文语料自建。
"""

from __future__ import annotations

import gzip
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_CODE = {ch: i for i, ch in enumerate(ALPHABET)}


def encode(text: str) -> np.ndarray:
    """字母串 → 0..25 编码（忽略非 A–Z 字符）。"""
    return np.fromiter((_CODE[ch] for ch in text.upper() if ch in _CODE), dtype=np.int64)


def decode(codes) -> str:
    return "".join(ALPHABET[int(c)] for c in codes)


def ngram_indices(codes: np.ndarray, n: int) -> np.ndarray:
    """编码序列 → 各起点的 n-gram 表索引（基数 26）。"""
    length = len(codes) - n + 1
    if length <= 0:
        return np.zeros(0, dtype=np.int64)
    idx = np.zeros(length, dtype=np.int64)
    for j in range(n):
        idx = idx * 26 + codes[j:j + length]
    return idx


def _ini_path(path: Path) -> Path:
    base = path.with_suffix("") if path.suffix == ".gz" else path
    return base.with_suffix(".ini")


def _read_ini(path: Path) -> dict[str, str]:
    ini = _ini_path(path)
    if not ini.exists():
        return {}
    params = {}
    for line in ini.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            params[k.strip()] = v.strip()
    return params


@dataclass
class NgramModel:
    n: int
    table: np.ndarray  # uint8, shape (26**n,)
    name: str = ""
    params: dict = field(default_factory=dict)

    # -- 构建 / 加载 ---------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path) -> "NgramModel":
        """加载 AZdecrypt 格式的 n-gram 文件（同名 .ini 可选）。"""
        path = Path(path)
        params = _read_ini(path)
        spec = params.get("N-gram size", "")
        m = re.fullmatch(r"([bt]?)(\d+)", spec) if spec else None
        fmt, n = (m.group(1), int(m.group(2))) if m else ("", None)

        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rb") as fh:
            raw = fh.read()

        if n is None:  # 根据长度推断二进制格式
            n = next((k for k in range(2, 11) if len(raw) == 26 ** k), None)
            fmt = "b" if n else "t"
        if fmt == "b" or (fmt == "" and len(raw) == 26 ** n):
            if len(raw) != 26 ** n:
                raise ValueError(f"{path}: 二进制长度 {len(raw)} ≠ 26**{n}")
            table = np.frombuffer(raw, dtype=np.uint8).copy()
        else:
            if n is None:
                raise ValueError(f"{path}: 无法确定 n-gram 大小，请提供 .ini")
            table = np.zeros(26 ** n, dtype=np.uint8)
            for gram, val in re.findall(rb"([A-Z]{%d})\s*(\d+)" % n, raw):
                idx = 0
                for ch in gram:
                    idx = idx * 26 + (ch - 65)
                table[idx] = min(int(val), 255)
        return cls(n=n, table=table, name=path.name, params=params)

    @classmethod
    def from_corpus(cls, text: str, n: int, name: str = "corpus") -> "NgramModel":
        """从语料自建：值 = 1 + log(count) 线性缩放到 1..255，未见过为 0。"""
        idx = ngram_indices(encode(text), n)
        counts = np.bincount(idx, minlength=26 ** n).astype(np.float64)
        seen = counts > 0
        logs = np.zeros_like(counts)
        logs[seen] = np.log(counts[seen])
        top = logs.max() or 1.0
        table = np.zeros(26 ** n, dtype=np.uint8)
        table[seen] = np.clip(np.rint(1 + 254 * logs[seen] / top), 1, 255).astype(np.uint8)
        return cls(n=n, table=table, name=name,
                   params={"corpus_letters": str(len(idx) + n - 1)})

    def save(self, path: str | Path) -> None:
        """保存为 AZdecrypt 兼容的二进制格式（附 .ini）。"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.table.tobytes())
        _ini_path(path).write_text(
            f"N-gram size=b{self.n}\nAlphabet={ALPHABET}\n", encoding="utf-8")

    # -- 打分 ---------------------------------------------------------------

    def score(self, text: str) -> float:
        """平均 n-gram 分数（越高越像英文）。"""
        idx = ngram_indices(encode(text), self.n)
        return float(self.table[idx].mean()) if len(idx) else 0.0

"""内置英文语料：当前 Python 安装的标准库文档字符串 + pydoc 主题文档。

目的：不下载任何外部数据，也能得到一个与 Zodiac 明文完全无关的英文语言模型，
用于复现 Z408 / Z340 的破解。语料为技术英语，与 1960 年代口语化英语有差距，
因此它是一个“偏弱”的模型——能用它复现已知解，说明求解流程本身是可靠的。
更强的模型可使用 AZdecrypt 附带的 n-gram 文件（见 docs/m0-report.md）。
"""

from __future__ import annotations

import ast
import os
import re
import sys
import sysconfig
from pathlib import Path

from .cipher import ROOT
from .ngram import NgramModel

MODELS_DIR = ROOT / "models"
_SKIP_DIRS = {"test", "tests", "idle_test", "site-packages", "__pycache__", "lib2to3"}


def stdlib_english() -> str:
    """收集标准库英文文本，返回仅含 A–Z 的大写字符串。"""
    parts: list[str] = []
    try:
        from pydoc_data.topics import topics
        parts += [topics[k] for k in sorted(topics)]
    except ImportError:
        pass
    lib = sysconfig.get_paths()["stdlib"]
    for root, dirs, files in os.walk(lib):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            try:
                tree = ast.parse(Path(root, name).read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, ValueError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node, clean=True)
                    if doc:
                        parts.append(doc)
    return re.sub(r"[^A-Z]", "", " ".join(parts).upper())


def builtin_model(n: int = 4, cache: bool = True) -> NgramModel:
    """由内置语料构建 n-gram 模型；结果缓存在 models/（已被 .gitignore 忽略）。"""
    tag = f"builtin-{n}gram-py{sys.version_info.major}{sys.version_info.minor}"
    path = MODELS_DIR / f"{tag}.bin"
    if cache and path.exists():
        model = NgramModel.load(path)
        model.name = tag
        return model
    model = NgramModel.from_corpus(stdlib_english(), n, name=tag)
    if cache:
        model.save(path)
    return model


AZ_5GRAM = MODELS_DIR / "5-grams_english_beijinghouse_10TB_v7.gz"


def get_model(spec: str) -> NgramModel:
    """模型规格：'auto'（有 AZdecrypt 5-gram 则用之，否则内置 4-gram）/ 'builtin:4' / 'builtin:5' /
    AZdecrypt n-gram 文件路径。"""
    if spec == "auto":
        spec = str(AZ_5GRAM) if AZ_5GRAM.exists() else "builtin:4"
    if spec.startswith("builtin"):
        _, _, n = spec.partition(":")
        return builtin_model(int(n) if n else 4)
    return NgramModel.load(spec)

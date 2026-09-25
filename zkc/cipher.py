"""密文加载与网格表示。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SOLUTIONS_DIR = DATA_DIR / "solutions"

KNOWN = ("z408", "z340", "z13", "z32")


def _read_rows(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    return tuple(line.rstrip("\r") for line in text.splitlines() if line.strip())


@dataclass(frozen=True)
class Cipher:
    """按原件行结构保存的密文（行可以不等长，如 Z32）。"""

    name: str
    rows: tuple[str, ...]

    @classmethod
    def from_file(cls, path: str | Path, name: str | None = None) -> "Cipher":
        path = Path(path)
        return cls(name or path.stem, _read_rows(path))

    @property
    def text(self) -> str:
        return "".join(self.rows)

    @property
    def width(self) -> int:
        return max(len(r) for r in self.rows)

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def is_grid(self) -> bool:
        return len({len(r) for r in self.rows}) == 1

    @property
    def symbols(self) -> list[str]:
        """不同符号，按首次出现顺序。"""
        return list(dict.fromkeys(self.text))

    def __len__(self) -> int:
        return len(self.text)

    def index(self, row: int, col: int) -> int:
        """网格坐标（0 起）→ 线性位置。仅适用于等宽网格。"""
        if not self.is_grid:
            raise ValueError(f"{self.name} 不是等宽网格")
        return row * self.width + col


def load(name: str) -> Cipher:
    """加载 data/ 下的密文：z408、z340、z13、z32，或任意文件路径。"""
    path = DATA_DIR / f"{name}.txt"
    if not path.exists():
        path = Path(name)
    return Cipher.from_file(path, name if name in KNOWN else None)


def load_solution(filename: str) -> str:
    """加载 data/solutions/ 下的已知明文（去掉换行后的连续字符串）。"""
    return "".join(_read_rows(SOLUTIONS_DIR / filename))

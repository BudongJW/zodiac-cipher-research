"""换位（transposition）。

约定：换位方案用“读取顺序” order 表示——明文第 k 个字符位于密文线性位置 order[k]。
untranspose(密文, order) 得到按明文顺序排列的密文符号，可直接交给替换求解器。
"""

from __future__ import annotations

from collections.abc import Sequence


def decimation(n_rows: int, n_cols: int, dr: int = 1, dc: int = 2,
               start: tuple[int, int] = (0, 0)) -> list[tuple[int, int]]:
    """(dr, dc) 抽取读取：从 start 出发，每步下移 dr 行、右移 dc 列，越界回绕。

    返回遍历全部格子的坐标序列（0 起）。若该步长无法遍历全部格子则抛出 ValueError。
    Z340 前两段即为 9×17 网格上的 (1, 2) 抽取。
    """
    r0, c0 = start
    total = n_rows * n_cols
    cells = [((r0 + k * dr) % n_rows, (c0 + k * dc) % n_cols) for k in range(total)]
    if len(set(cells)) != total:
        raise ValueError(f"步长 ({dr},{dc}) 无法遍历 {n_rows}×{n_cols} 网格")
    return cells


def untranspose(seq: Sequence, order: Sequence[int]):
    """按读取顺序重排：返回明文顺序的符号序列（str 输入则返回 str）。"""
    out = [seq[i] for i in order]
    return "".join(out) if isinstance(seq, str) else out


def transpose(seq: Sequence, order: Sequence[int]):
    """untranspose 的逆操作：把明文顺序的序列放回密文位置。"""
    out = [None] * len(order)
    for k, i in enumerate(order):
        out[i] = seq[k]
    return "".join(out) if isinstance(seq, str) else out


def is_permutation(order: Sequence[int], n: int) -> bool:
    return sorted(order) == list(range(n))


# ---------------------------------------------------------------------------
# Z340：Oranchak, Blake, Van Eycke (2020 破解；arXiv:2403.17350) 发表的换位方案
# ---------------------------------------------------------------------------

Z340_ROWS, Z340_COLS = 20, 17

# 第 1 段：第 1–9 行；第 2 段：第 10–18 行；第 3 段：第 19–20 行（0 起行号见下）
Z340_SECTIONS = ((0, 9), (9, 18), (18, 20))

# 第 2 段异常 1：段内第 1 行右端 6 格（明文 “LIFEIS”）按普通顺序书写，
# 抽取时跳过，并置于该段明文末尾。
Z340_SECTION2_SKIP = tuple((0, c) for c in range(11, 17))

# 第 2 段异常 2：段内第 6 行（全局第 15 行）第 17 列的符号，应视为位于第 4 列
# （即 “H 移至第 4 列”，可修复多处拼写）。格式：(段内行, 原列, 目标列)，均 0 起。
Z340_SECTION2_SHIFT = (5, 16, 3)

# 第 3 段不换位，但部分单词倒写。以下为依据已知明文划分的 (长度, 是否倒写) 片段：
# EFIL|WILL|EB|NA|EASY|ENO|NI|ECIDARAP|DEATH
# → LIFE WILL BE AN EASY ONE IN PARADICE DEATH
Z340_TAIL_SEGMENTS = ((4, True), (4, False), (2, True), (2, True), (4, False),
                      (3, True), (2, True), (8, True), (5, False))


def _section_rows(first: int, last: int, n_cols: int = Z340_COLS) -> list[list[int]]:
    return [[r * n_cols + c for c in range(n_cols)] for r in range(first, last)]


def section_decimation_order(first_row: int, last_row: int, dr: int = 1, dc: int = 2,
                             n_cols: int = Z340_COLS) -> list[int]:
    """对密文的某个行区段做 (dr, dc) 抽取，返回线性位置序列（用于换位扫描）。"""
    rows = _section_rows(first_row, last_row, n_cols)
    return [rows[r][c] for r, c in decimation(len(rows), n_cols, dr, dc)]


def z340_order(include_tail_reversals: bool = True) -> list[int]:
    """Z340 的完整读取顺序（长度 340 的排列）。"""
    order: list[int] = []

    # 第 1 段：9×17 上的 (1, 2) 抽取
    order += section_decimation_order(*Z340_SECTIONS[0])

    # 第 2 段：先修正 “H” 的位置，再做 (1, 2) 抽取并跳过 LIFEIS 六格
    rows = _section_rows(*Z340_SECTIONS[1])
    sr, src, dst = Z340_SECTION2_SHIFT
    rows[sr].insert(dst, rows[sr].pop(src))
    skip = set(Z340_SECTION2_SKIP)
    order += [rows[r][c] for r, c in decimation(len(rows), Z340_COLS) if (r, c) not in skip]
    order += [rows[r][c] for r, c in Z340_SECTION2_SKIP]

    # 第 3 段：按行读取，部分片段倒写
    tail = [i for row in _section_rows(*Z340_SECTIONS[2]) for i in row]
    if include_tail_reversals:
        pos = 0
        for length, rev in Z340_TAIL_SEGMENTS:
            seg = tail[pos:pos + length]
            order += seg[::-1] if rev else seg
            pos += length
    else:
        order += tail

    assert is_permutation(order, Z340_ROWS * Z340_COLS)
    return order

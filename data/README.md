# 数据：密文转录与已知解

| 文件 | 内容 |
|---|---|
| [z13.txt](z13.txt) | Z13（“My name is”密文）ASCII 转录，1 行 13 符号 |
| [z32.txt](z32.txt) | Z32（Mt. Diablo 地图密文）ASCII 转录，按原件分 2 行（17 + 15） |
| [z408.txt](z408.txt) | Z408 转录，24 行 × 17 列 |
| [z340.txt](z340.txt) | Z340 转录，20 行 × 17 列 |
| [solutions/z408_plaintext.txt](solutions/z408_plaintext.txt) | Z408 已知明文（Harden 密钥），与密文逐位对齐，保留 Zodiac 原有的拼写与加密错误 |
| [solutions/z340_plaintext_cipher_order.txt](solutions/z340_plaintext_cipher_order.txt) | Z340 已知密钥作用于密文后的字母，仍处于**密文位置**（未去除换位） |
| [solutions/z340_plaintext.txt](solutions/z340_plaintext.txt) | Z340 已知明文，**阅读顺序**（已去除换位；保留原有错误，如 SOOHER、PARADLCE） |

**来源**：Z408 / Z340 的转录与已知解取自 AZdecrypt 1.25 附带的数据（https://github.com/doranchak/azdecrypt ，`AZdecrypt/Ciphers/Zodiac ciphers/`，GPL-3.0），同样采用 webtoy 转录方案。该处的 Z13 / Z32 转录与本目录独立核对的版本逐字相同。

**一致性检查**（`python -m zkc verify`，亦见 `tests/`）：两份已知明文推导出的密钥均自洽（Z408 54 个符号、Z340 63 个符号，每个符号只对应一个字母）；Z340 的密钥作用于密文后，按已发表的换位方案读取，与阅读顺序明文逐字一致。

## 转录约定

- 采用 David Oranchak 的 **webtoy 转录方案**（社区事实标准，AZdecrypt 等工具通用）：
  https://www.zodiackillerciphers.com/wiki/index.php?title=Webtoy%27s_transcription_scheme
- **ASCII 字符只是符号的 ID，并不代表明文字母。** 例如 `z` 表示 Zodiac 十字圈符号 ⊕，`0` 表示“圈 8”，`9` 表示空心三角形。
- 本目录的两份转录已于 2026-09-25 与 Oranchak Wiki 原始 wikitext 逐字符核对一致：
  - Z13：https://zodiackillerciphers.com/wiki/index.php?title=Unsolved_13-character_%22My_name_is%22_cipher
  - Z32：https://zodiackillerciphers.com/wiki/index.php?title=Unsolved_32-character_%22map_code%22_cipher

---

## Z13

```
AENz0K0M0[NAM
```

| 位置 | ASCII | 字形描述 | 备注 |
|---|---|---|---|
| 1 | `A` | 字母 A | 与 12 同 |
| 2 | `E` | 字母 E | |
| 3 | `N` | 字母 N | 与 11 同 |
| 4 | `z` | 圆圈内加十字（类 Zodiac 标志 ⊕） | 有人指出十字明显偏离圆心 |
| 5 | `0` | 圈 8（圆圈内写 8，“eight-ball”） | 与 7、9 同 |
| 6 | `K` | 字母 K | |
| 7 | `0` | 圈 8 | |
| 8 | `M` | 字母 M | 与 13 同 |
| 9 | `0` | 圈 8 | |
| 10 | `[` | 类锚形：竖笔立于底座之上 | **有争议**：Pelling 记作 “ω”，Garlick 称“倒 T”，Culver-Young 称“不对称锚”，Praetorian 称“下箭头” |
| 11 | `N` | 字母 N | **小争议**：有评论者认为是反写 N；主流转录视为与 3 相同 |
| 12 | `A` | 字母 A | |
| 13 | `M` | 字母 M | |

**统计**

- 长度 13，不同符号 8 个（A, E, N, ⊕, 圈8, K, M, `[`）。
- 同构模式（isomorph）：`1 2 3 4 5 6 5 7 5 8 3 1 7`，即 A(1,12)、N(3,11)、圈8(5,7,9)、M(8,13)。
- 字母形 / 非字母形符号分布呈镜像：`aen??k?m??nam`。
- multiplicity = 8 / 13 ≈ 0.62。
- 与其他密文的符号重合（`python -m zkc overlap` 计算）：A、E、N、⊕、K、M 同时见于 Z408 与 Z340；**圈 8 与 `[` 在 Z408、Z340 中均未出现**。

**其他转录写法（对照）**：Pelling `AEN+8K8M8ωNAM`。
来源：https://ciphermysteries.com/2017/12/16/zodiac-killers-z13-cipher-meets-z340-cipher · https://forum.zodiackillerciphers.com/community/zodiac-cipher-mailings-discussion/all-features-present-in-the-z13-cipher/

---

## Z32

```
C9J|#Ok[AMf8?ORTG
X6FDVj%HCELzPW9
```

| 位置 | ASCII | 字形描述 | 备注 |
|---|---|---|---|
| 1 | `C` | C 形 | 与 26 同；不在 Z408 密钥中 |
| 2 | `9` | 空心三角形 △ | 与 32 同 |
| 3 | `J` | 字母 J | |
| 4 | `\|` | 竖线 / “I” | **有争议**：Pelling 视为 Z408 符号（→E） |
| 5 | `#` | 方框 | |
| 6 | `O` | O 形 | 与 14 同 |
| 7 | `k` | 疑为反写 K | 【待核实】 |
| 8 | `[` | 类锚形 / 下箭头（同 Z13 第 10 位） | **有争议**：Pelling 视为 Z408 符号（→O） |
| 9 | `A` | 字母 A | |
| 10 | `M` | 字母 M | |
| 11 | `f` | 非标准 F 形 | 具体字形【待核实】 |
| 12 | `8` | 疑为实心三角形 ▲ | 【推断】Pelling 称 Z32 同时含实心与空心三角形 |
| 13 | `?` | Ω 形 | 不在 Z408 中 |
| 14 | `O` | O 形 | |
| 15 | `R` | 字母 R | |
| 16 | `T` | 字母 T | |
| 17 | `G` | 字母 G | 第 1 行结束 |
| 18 | `X` | 字母 X | 第 2 行开始 |
| 19 | `6` | 圆圈内加 X | |
| 20 | `F` | 字母 F | |
| 21 | `D` | 字母 D | |
| 22 | `V` | 字母 V | |
| 23 | `j` | 折线形（zigzag） | |
| 24 | `%` | 实心方框 / 实心圆 | **有争议**：Pelling 称“涂黑方框”且不在 Z408 中；Oranchak 转录为 Z408 的 `%` 符号 |
| 25 | `H` | 字母 H | |
| 26 | `C` | C 形 | |
| 27 | `E` | 字母 E | |
| 28 | `L` | 字母 L | |
| 29 | `z` | Zodiac 十字圈 ⊕ | |
| 30 | `P` | 字母 P | |
| 31 | `W` | 字母 W | |
| 32 | `9` | 空心三角形 △ | |

**统计**

- 长度 32（两行 17 + 15），不同符号 29 个。
- 仅 3 个符号重复：C(1,26)、△(2,32)、O(6,14)；其余 26 个符号各出现一次。
- multiplicity = 29 / 32 ≈ 0.91。
- 与其他密文的符号重合（`python -m zkc overlap` 计算）：29 个符号中 25 个见于 Z408（缺 C、`|`、`[`、`?`），27 个见于 Z340（缺 `[`、`?`）。**`[` 只出现在 Z13 与 Z32 中**——两份未解密文共享一个其他密文中没有的符号。

**其他转录写法（对照）**：Foxon（IACR ePrint 2023/982, Fig. 1A）以数字标记非字母符号：
```
C 1 J I 2 O 3 4 A M 5 6 7 O R T G
X 8 F D V 9 ! H C E L ? P W 1
```
来源：https://eprint.iacr.org/2023/982 · https://ciphermysteries.com/other-ciphers/zodiac-killer-ciphers/zodiac-killer-z32 · https://www.praetorian.com/blog/a-possible-solution-to-the-zodiac-killer-z32-cipher/

---

## 待办

- [ ] 对照高清扫描件，逐一确认所有标注“有争议 / 待核实”的字形，并记录备选读法。
- [x] 取得 Z408 / Z340 的 webtoy 转录，用脚本精确计算四份密文之间的符号重合表。
- [ ] 为每个符号建立统一 ID 与字形图片索引（便于跨密文比对）。

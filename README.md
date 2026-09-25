# 黄道十二宫杀手密码研究（Zodiac Cipher Research）

本项目旨在系统整理并研究**黄道十二宫杀手**（Zodiac Killer）留下的、至今**尚未破译**的密文，主要是 **Z13**（“My name is”密文）与 **Z32**（Mt. Diablo 地图密文）。

1969 年至 1970 年间，该凶手向旧金山湾区多家报社寄出四份密文：**Z408** 于 1969 年被一对夫妇在一周内破解；**Z340** 历经 51 年，于 2020 年 12 月由三位民间研究者破解并获 FBI 确认。剩下的两份短密文由于长度远低于“唯一解距离”，50 多年来出现过数百个互相矛盾的“解”，却没有一个能被证明正确。

我们的目标不是再提出一个新“解”，而是：

1. **建立最完整的中文资料库**：一手资料、学术文献、工具，以及 1969 年以来所有重要的破译尝试；
2. **建立可量化、可复现的评估框架**：用统一标准衡量任何“破译声明”到底有多可信；
3. **系统引入外部约束**（地图几何、密钥关联、换位结构、作者习惯），在严格的统计对照下检验新假设。

---

## 密文现状

| 代号 | 日期 | 长度 / 不同符号 | 状态 |
|---|---|---|---|
| Z408 | 1969-07-31 | 408 / 54 | ✅ 已解（1969，Donald & Bettye Harden）；末尾 18 字符无公认解释 |
| Z340 | 1969-11-08 | 340 / 63 | ✅ 已解（2020，Oranchak / Blake / Van Eycke；同音替换 + 换位） |
| **Z13** | 1970-04-20 | 13 / 8 | ❌ **未解** |
| **Z32** | 1970-06-26 | 32 / 29 | ❌ **未解**（附 Phillips 66 地图，声称指向埋藏的炸弹） |

```
Z13:  AENz0K0M0[NAM

Z32:  C9J|#Ok[AMf8?ORTG
      X6FDVj%HCELzPW9
```

> 转录采用 David Oranchak 的 webtoy 方案，ASCII 字符只是符号 ID，不代表明文字母。逐符号说明与争议字形见 [data/README.md](data/README.md)。

---

## 仓库结构

```
.
├── README.md                 本文件
├── docs/
│   ├── ciphers.md            案件背景、四份密文概览、信件年表、作者书写习惯
│   ├── roadmap.md            破译方向、方法论、验收标准与阶段计划
│   ├── m0-report.md          M0/M1 报告：工具链与 Z408 / Z340 复现结果
│   ├── m2-report.md          M2 报告：短密文可解性基线、重复结构检验、Z13 姓名空间
│   ├── m3-report.md          M3 报告：历次 Z13 / Z32 破译声明的统一评估
│   ├── m4-report.md          M4 报告：密钥复用假设检验与后续方向
│   └── glyph-report.md       方向 A 报告：对照扫描件核对争议字形
├── references/
│   ├── README.md             参考文献总表（一手资料、论文、书籍、工具、视频）
│   └── attempts.md           历次破译尝试汇总（Z408 / Z340 / Z13 / Z32 / 其他信件）
├── data/
│   ├── README.md             转录约定、来源与逐符号说明
│   ├── z408.txt z340.txt     已解密文转录
│   ├── z13.txt  z32.txt      未解密文转录
│   ├── claims.json           历次 Z13 / Z32 破译声明的结构化记录（M3 评估用）
│   ├── glyphs/               由公有领域扫描件生成的字形对比图
│   └── solutions/            Z408 / Z340 已知解（用于回归测试）
├── zkc/                      Python 分析工具包（统计、换位、密钥、n-gram、求解器、合成密文、姓名匹配）
├── scripts/                  实验脚本（Z340 换位扫描、M2 基线实验）
├── results/                  实验结果（CSV / JSON）
├── tests/                    单元测试
└── hypotheses/               预注册假设（README 为规则、模板与索引；H001、H002 已完成）
```

## 快速开始

需要 Python ≥ 3.10 与 numpy。

```bash
python -m zkc verify                      # 确定性复现 Z408 / Z340 已知解
python -m zkc overlap                     # 四份密文的符号重合表
python -m zkc stats z32                   # 统计量（长度、多重度、同构模式、重复符号……）
python -m zkc stats z340 --shuffle 20000  # 周期双字母重复 + 置换检验
python -m zkc solve z408                  # 同音替换盲解（内置语言模型，无需下载数据）
python -m unittest discover -s tests      # 运行测试
```

### 当前进度

| 阶段 | 状态 | 主要结果 |
|---|---|---|
| M0 / M1 | ✅ | Z408、Z340 已知解逐字复现；盲解（不使用任何明文信息）在 AZdecrypt 5-gram 模型下 **Z408 准确率 100%、Z340 95%**（[m0-report](docs/m0-report.md)） |
| M2 | ✅ | **Z32 的重复结构与 Zodiac 的 Z340 式同音替换一致，Z13 则不一致**；按原转录，Z13 的重复模式极严（7,800 万个“名+姓”中仅 21 个符合），决定性约束是三个“圈 8”（[m2-report](docs/m2-report.md)） |
| M3 | ✅ | 为 16 条历次 Z13 / Z32 声明统一打分：**无一达到 A 级**（B 6、C 3、D 7）；Z32 各声明与 Z340 / Z408 密钥的一致均在偶然水平（[m3-report](docs/m3-report.md)） |
| M4 | ✅ | 预注册假设检验：**H001 不支持**（Z32 未沿用 Z340 / Z408 密钥，p = 0.51 / 0.18，功效 92%）；**H002 不支持**（Z13 的 Z340 密钥框架仅有弱信号 p = 0.014，Garlick 读法排第 58 / 676）（[m4-report](docs/m4-report.md)） |
| 方向 A | ✅ | 对照公有领域扫描件核对争议字形：Z13 转录成立（圈 8 未见差异，第 11 位为正写 N）；**Z32 第 26 位发现新的读法争议**（下端回钩的 C），更正 3 处字形描述；敏感性分析显示结论不变、对 Z32 声明的否定更强（[glyph-report](docs/glyph-report.md)） |
| 下一步 | 进行中 | 方向 E：Z32 地图几何——1970-06-26 扫描件中已含 Zodiac 实际寄出的地图（含比例尺），可直接作为底图 |

**截至 M4 的核心结论**：Z32 很可能与 Z408 / Z340 属同一类同音替换体制，但换了一张新密钥；在 32 字符下，任何“读得通”的解都无法与大量同样读得通的错误解区分——**现有 Z13 / Z32 声明没有一条具备证据价值**，突破只能来自密文以外的独立约束。

### 外部数据（可选，均不纳入本仓库）

```bash
# 语言模型：AZdecrypt 附带的 beijinghouse n-gram（许可 CC BY-NC 4.0）
mkdir -p models
curl -L -o models/5-grams_english_beijinghouse_10TB_v7.gz https://raw.githubusercontent.com/doranchak/azdecrypt/main/AZdecrypt/N-grams/5-grams_english_beijinghouse_10TB_v7.gz
curl -L -o models/5-grams_english_beijinghouse_10TB_v7.ini https://raw.githubusercontent.com/doranchak/azdecrypt/main/AZdecrypt/N-grams/5-grams_english_beijinghouse_10TB_v7.ini
python -m zkc solve z340 --model models/5-grams_english_beijinghouse_10TB_v7.gz --restarts 16

# 姓名数据：1990 年美国人口普查姓名频率表（公有领域），供 scripts/m2_z13_names.py 使用
mkdir -p external/names
for f in dist.male.first dist.female.first dist.all.last; do
  curl -L -o external/names/$f https://www2.census.gov/topics/genealogy/1990surnames/$f
done

# 信件扫描件：Wikimedia Commons（公有领域），供 scripts/glyph_sheets.py 使用
mkdir -p external/scans
curl -L -o external/scans/Zodiac-name.gif https://upload.wikimedia.org/wikipedia/commons/3/3b/Zodiac-name.gif
curl -L -o external/scans/June_26_1970_Zodiac_letter.jpg https://upload.wikimedia.org/wikipedia/commons/3/33/June_26_1970_Zodiac_letter.jpg
```

---

## 破译方向摘要

完整内容见 [docs/roadmap.md](docs/roadmap.md)。

| 方向 | 内容 |
|---|---|
| **A. 数据与基础设施** | 对照高清扫描核对争议字形；四份密文符号重合表；Zodiac 信件语料与拼写错误表；求解器与统计检验工具链；先复现 Z408 / Z340 的已知解 |
| **B. 短密文可解性基线** | 合成实验：在 13 / 32 字符长度下，求解器能否恢复正确明文、会产生多少“错误但可读”的解；Z13 姓名空间实验：多少人名符合其重复模式 |
| **C. 密钥关联** | Z32 有 27/29 个符号也见于 Z340，时间上也最接近 Z340；检验沿用 Z340 / Z408 密钥，以及 Z13 与 Z32 共用一张新密钥（两者共享一个其他密文中没有的符号） |
| **D. 换位结构** | Z340 在替换之上叠加了换位。Z32 第 1 行恰为 17 个符号，与 Z408 / Z340 的 17 列网格相同，需系统检验各换位族 |
| **E. 地图几何（Z32）** | 地图配准到 GIS；按“0 对准磁北（1970 年 ≈ 16.88° E）、弧度、英寸、比例尺 1 英寸 ≈ 6.4 英里”的预注册规则解析；受限词表生成候选明文；与随机点基准比较 |
| **F. 作者习惯画像** | 从已解密文中归纳加密错误、同音字轮换、倒写、填充等习惯，作为错误模型的先验 |
| **G. AI / LLM 辅助** | 仅用于候选生成与辅助评审，必须与零假设对照一同使用 |

**阶段计划**：M0 数据与工具 → M1 复现已知解 → M2 可解性基线 → M3 为所有既有声明打分 → M4 新假设搜索 → M5 汇总报告

---

## 验收标准（摘要）

任何“解”须满足：

1. 同一符号对应同一字母，例外须事先声明并计入自由度；
2. 预注册：方法、参数空间、打分与阈值先于运行确定；
3. 与零假设对照（打乱密文 / 随机密钥合成密文），显著优于对照；
4. 代码、密钥与步骤完全公开、可复现；
5. 拼写与用词风格与 Zodiac 已知信件一致；
6. 不以任何嫌疑人为出发点。

历史上所有被否定的声明，几乎都违反了其中至少一条。详见 [references/attempts.md §6](references/attempts.md#6-经验教训失败声明的共同模式)。

---

## 参与方式

- 新假设请按 [docs/roadmap.md](docs/roadmap.md) 中的假设模板提交到 `hypotheses/` 目录（负面结果同样欢迎）。
- 补充或更正文献请修改 `references/`，每条事实须附来源链接；无法确认的内容请标注【待核实】。
- 字形核对请注明所依据的扫描件来源。

## 声明

- 本项目仅做密码学与历史研究，**不指认任何个人为凶手**。凡涉及具体人物的内容，都只是对已公开声明的记录与评估。
- 本案至今仍是未结刑事案件。若掌握与案件相关的实质性线索，请直接联系执法机构（FBI：https://tips.fbi.gov/ ）。
- 请尊重受害者及其家属。

## 主要参考

- David Oranchak 的 Zodiac Killer Ciphers 维基与博客：https://zodiackillerciphers.com/
- Oranchak, Blake, Van Eycke. *The Solution of the Zodiac Killer's 340-Character Cipher.* arXiv:2403.17350, 2024.
- Craig P. Bauer. *Unsolved!* Princeton University Press, 2017.
- 完整书目：[references/README.md](references/README.md)

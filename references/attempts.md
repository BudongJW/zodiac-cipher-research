# 历次破译尝试汇总

> 最后整理：2026-09-25
> 本文按密文分类整理 1969 年以来的主要破译尝试（成功、失败与已被否定的声明），每条均附来源。
> 标记：**【待核实】** = 仅见于二手转述/搜索摘要；**【有争议】** = 权威来源说法冲突。
> 完整书目见 [README.md](README.md)。

**目录**

- [1. Z408（已破解，1969）](#1-z408已破解1969)
- [2. Z340（已破解，2020）](#2-z340已破解2020)
- [3. Z13（未破解）](#3-z13未破解)
- [4. Z32（未破解）](#4-z32未破解)
- [5. 其他信件中的“暗码”声明](#5-其他信件中的暗码声明)
- [6. 经验教训：失败声明的共同模式](#6-经验教训失败声明的共同模式)

---

## 1. Z408（已破解，1969）

### 1.1 基本事实

- **寄出**：1969-07-31，旧金山邮戳，分三份寄给《Vallejo Times-Herald》《San Francisco Examiner》《San Francisco Chronicle》，每份含 408 字符密文的三分之一；信中要求 1969-08-01（周五）下午前刊登于头版，否则将“整个周末四处游荡杀人”。信中声称密文包含其身份（原文拼作 “idenity”）。
  来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_San_Francisco_Chronicle,_July_31st_1969 · https://en.wikipedia.org/wiki/Zodiac_Killer
- **三份分别寄往哪家报社【有争议】**：Oranchak Wiki 为 Part 1→Times-Herald、Part 2→Examiner、Part 3→Chronicle；Tom Voigt 网站则为 Times-Herald 1/3、Chronicle 2/3、Examiner 3/3。
  来源：https://zodiackillerciphers.com/wiki/index.php?title=Solved_408-character_cipher · https://www.zodiackiller.com/Letters.html
- **密码体制**：同音替换（homophonic substitution），24 行 × 17 列，54 个不同符号；J、Q、X、Z 无对应符号。
  来源：https://zodiackillerciphers.com/408/key.html · https://arxiv.org/html/2403.17350v1

### 1.2 Harden 夫妇的破译（成功）

- **破译者**：Donald Harden（North Salinas 高中历史/经济教师）与妻子 Bettye Harden，断断续续用了约 20 小时。
- **日期【有争议】**：Oranchak 等人的 arXiv 论文记为 **1969-08-08**；英文维基百科记为 08-05（引自 Bauer）。前者佐证更多。1969-08-09《SF Chronicle》刊出报道“A 'Murder Code' Broken”。
- **方法**：
  - Bettye 提出“心理学 crib”：凶手自我中心，密文应以 “I” 开头，且应包含 KILL / KILLING / I LIKE KILLING。
  - 寻找重复双符（LL），发现一组反复出现的 4 符号组合可能是 KILL；以出现 6 次的双符（→LL）为锚点，手工推进。
- **错误**：Zodiac 本人约 5 处加密错误（如 “DANGERTUE” 应为 DANGEROUS；三角形符号用法不一致），Harden 夫妇另有约 7 处误读（如 “MUDH”）。
- 来源：https://eng.vt.edu/magazine/stories/spring-2020/the-new-cryptographers.html · https://zodiackillerciphers.com/408/key.html · http://www.zodiackillerciphers.com/?p=233 · https://www.history.com/articles/the-zodiac-ciphers-what-we-know

> **启示**：Z408 能被业余者在一周内破解，关键在于（1）足够长（408 字符），（2）心理学 crib 命中，（3）同音字按顺序轮换使用，存在可利用的规律。Z13/Z32 缺乏（1），因此（2）（3）类外部约束的价值更大。

### 1.3 末尾 18 字符之谜

用 Harden 密钥解出末尾 18 字符为 `EBEORIETEMETHHPITI`，**至今无公认解释**。

| 声明 | 提出者 / 时间 | 评价 | 来源 |
|---|---|---|---|
| 填充字符（filler）| 论坛用户 “glurk” 观察，“DerekP” 分析 | **主流观点**：许多符号与正上方同列符号重复，像是为凑满网格而随手填写 | http://zodiackillerciphers.com/wiki/index.php?title=Encyclopedia_of_observations |
| “ROBERT EMMET THE HIPPIE” | 1969-08-12《SF Chronicle》报道多名读者提出【待核实】 | 并非真正的变位词：该短语 20 个字母，需额外的 R、M、P，且少一个 I | https://forum.zodiackillerciphers.com/community/zodiac-cipher-mailings-discussion/robert-emmet-the-hippie/ |
| “Robert Hemphill”、“Emmet O'Wright” | 同期读者【待核实】 | 同样的不完全变位问题 | https://www.tapatalk.com/groups/zodiackillerfr/408-final-18-as-filler-t10792-s90.html |
| “ROBERT E SMITH THE II” | 论坛管理员 “Horan”，2015 | 针对 Graysmith 的讽刺性变位 | https://zodiackillerhoax1986.freeforums.net/thread/84/solutions-408-anagram |
| 以 “PARADICE” 为密钥的列换位（意英混合读法），及更早的 “Giuseppe Bevilacqua” | Francesco Amicone，2022 | 自由度过高，无法证伪 | https://ostellovolante.com/2022/06/01/408-cipher-final-words-decryption-paradice-key/ |

> **通用批评**：18 个字母的变位组合数量极其庞大，几乎可以拼出任何想要的名字（Oranchak：http://www.zodiackillerciphers.com/?p=267）。

---

## 2. Z340（已破解，2020）

### 2.1 基本事实

- **寄出**：1969-11-08，旧金山邮戳，寄往《SF Chronicle》，附一张“滴墨笔”（Dripping Pen）贺卡，卡上手写 “This is the Zodiac speaking”、要求刊登于 “frunt page”、及 “Des July Aug Sept Oct = 7” 等字样。1969-11-13 前后刊出。
  来源：https://www.zodiackiller.com/340Cipher.html · https://en.wikisource.org/wiki/Zodiac_Killer_letter,_November_8th_1969
- **规格**：20 行 × 17 列 = 340 字符，63 个不同符号。

### 2.2 1969–2020 年间失败 / 被否定的声明

| 年份 | 声明者 | 声明内容 | 否定理由 | 来源 |
|---|---|---|---|---|
| 1979 / 1986 | Robert Graysmith | 著作中给出的“解” | FBI 1979-02-15 分析认为其解“has been forced”；Oranchak 批评为“选择性变位” | https://zodiackillerfacts.com/main/the-340-cipher-dead-ends/ |
| 1981 / 1987 | Gareth Penn | 《Times 17》：“弧度理论”+“17 倍”数字模式，指认 Michael O'Hare | 并非真正解密；刺伤数实为 16 而非 17、字符计数有误、弧度理论有挑选数据之嫌 | https://zodiackillerfacts.com/zodiac-theories/the-accused-the-accusers/gareth-penn-michael-ohare/ · http://www.zodiackillerciphers.com/?p=543 |
| 2008 | John Cecil | 放弃“一符号对应一字母”约束 | 自由度过高 | http://zodiackillersolved.blogspot.com/2008/12/340-cipher-solution.html |
| 2011 | Corey Starliper | “98% 可读”，结尾为 “My name is Leigh Allen” | 任意系统，可插入预设信息；Oranchak 称其为骗局，本人后承认“可能不对” | https://www.nbcnews.com/id/wbna43884248 · https://zodiackillerfacts.com/main/the-starliper-solution/ |
| 2012 | Daryll Lathers | 在《SF Chronicle》登广告公布“解” | Oranchak 证明其字母串可重排出约 920 亿种句子，且使用了多表替换 | http://www.zodiackillerciphers.com/?p=267 |
| 2014 | Gary L. Stewart / Susan Mustafa | 著作《The Most Dangerous Animal of All》称 Z340 中藏有 “EARL VAN BEST” | 字母分配为人为挑选；2020 年 FX 纪录片亦逐一驳斥其笔迹、指纹、DNA 证据 | https://zodiackillerfacts.com/zodiac-theories/the-accused-the-accusers/earl-van-best-jr-gary-stewart/ |
| 2017 | History Channel《The Hunt for the Zodiac Killer》（Craig Bauer 等） | 终集展示“部分解”，假设部分符号代表其自身 | Nick Pelling 统计约 23 个字母吻合、61 个不吻合；据 Bill Briere 称团队内部异议被剪掉，Ed Scheidt 后称该解“似乎不正确” | https://ciphermysteries.com/2017/12/14/hunt-zodiac-killer-season-finale-craig-bauers-z340-cipher-crack · https://www.linkedin.com/pulse/zodiac-speaking-bill-briere |
| 其他 | Özcan Türkmen、Thomas Dougherty、AK Wilks/Zander Kite、Hal Kravcik、Chris Farmer/OPORD 等 | 各类声明 | Oranchak Wiki 列为已否定 | https://www.zodiackillerciphers.com/wiki/index.php?title=Main_Page |

> 2020 年的正确解中**不含任何人名**，从根本上否定了上述所有“姓名藏于密文”的说法。

### 2.3 破解前的社区统计工作（通往成功的铺垫）

| 时间 | 贡献者 | 发现 | 意义 |
|---|---|---|---|
| 2008 | David Oranchak | 以约束满足 + 进化算法攻击同音替换（GECCO 2008） | 早期自动化尝试 |
| 2010 | 论坛用户 “bentley”、“Smithy” | **Pivots**：两个相交的重复三元组构成 L 形；随机打乱测试中约每 237,000 次才出现一次 | 暗示存在非平凡的结构 |
| 2010 | Raddum & Sýs | 证明 Z340 符号序列显著非随机 | 学术界首次给出严格结论 |
| 2015-01 | Jarl Van Eycke | 发布 **AZdecrypt** | 后来破解 Z340 的核心求解器 |
| 2015 夏 | Jarl Van Eycke（2015-07-28 帖）与 “daikon” 独立发现 | **周期-19 双字母统计**：以周期 19 读取时有 37 个重复双字母组，而按顺序读仅 25 个（约 1/216 的偶然概率） | 强烈提示存在换位层 |
| 2019 | Juzek（HistoCrypt 2019） | n-gram 熵表明 Z340“不是单纯替换” | 独立的学术佐证 |
| 2019-01 起 | Sam Blake | 枚举数十亿种候选换位，按重复双字母数筛选，最终批次 **655,088** 种（即常说的“约 65 万”） | 系统化搜索换位空间 |
| 2020 | Oranchak《Let's Crack Zodiac》系列 | 公开讲解统计线索与研究进展 | 社区协作 |

来源：http://zodiackillerciphers.com/wiki/index.php?title=Encyclopedia_of_observations · https://zodiackillerciphers.com/wiki/index.php?title=Solution_to_the_340 · https://blog.wolfram.com/2021/03/24/the-solution-of-the-zodiac-killers-340-character-cipher/

### 2.4 2020 年 12 月的破解（成功）

- **破解团队**：David Oranchak（美国，软件开发者）、Sam Blake（澳大利亚，应用数学家）、Jarl Van Eycke（比利时，AZdecrypt 作者）。
- **时间线**（据 Oranchak Wiki）：
  - 12-02 开始处理 655,088 种候选换位
  - 12-03 出现首个有希望的结果（可读片段 “HOPE YOU ARE”“TRYING TO CATCH ME”“THE GAS CHAMBER”）
  - 12-05 Jarl 发现跳过 “LIFEIS” 可修复剩余乱码；同日提交 FBI 密码实验室，数十分钟内获非正式确认
  - 12-11 公开讲解视频；FBI 旧金山分局发表声明
- **方法**：
  1. 20×17 网格按行分为三段：第 1–9 行、第 10–18 行、第 19–20 行。
  2. 前两段各自以 **(1,2)-抽取**（decimation）方式读取：从左上角出发，每步“下移 1 行、右移 2 列”，越界回绕（类似“马步”）。
  3. 63 个符号全部出现在第一段中，因此整份同音替换密钥可由第 1–9 行确定。
  4. 第 19–20 行不做换位，按正常顺序读取，但部分单词倒写（如 PARADICE 写作 ECIDARAP）。
  5. 异常：第二段右上角的 “LIFEIS” 以普通顺序书写，还原换位时需跳过；第二段第 6 行将一个 “H” 移至第 4 列可修复多处拼写。
- **推定的加密错误**：FAN→FUN、BRINGO→BRINGS、BECAASE→BECAUSE、PARADLCE→PARADICE、SOOHER→SOONER 等。
- **内容概要**：嘲讽警方追捕、否认曾在 1969-10 的电视节目中打电话、声称不惧毒气室因其会把他更快送往“天堂”（paradice），在那里奴隶们将为他服务。**明文中不含 “ZODIAC”，也不含任何人名。**
- **遗留歧义**：“LIFE IS” 与 “DEATH” 的位置与读法（“LIFE IS DEATH” 等多种提议）。
- **独立验证**：FBI CRRU 验证（仅微调 “sooner”）；Nils Kopal 以 CrypTool 2 独立复现（https://github.com/n1k0m0/Zodiac-340-Transposition-Reverser）；von zur Gathen（2023）计算唯一解距离在 80–152 之间，从理论上支持解的唯一性。
- **论文**：Oranchak, Blake, Van Eycke, arXiv:2403.17350（2024）。

来源：https://arxiv.org/abs/2403.17350 · https://zodiackillerciphers.com/wiki/index.php?title=Solution_to_the_340 · https://blog.wolfram.com/2021/03/24/the-solution-of-the-zodiac-killers-340-character-cipher/ · https://ciphermysteries.com/2020/12/11/zodiac-z340-is-cracked · https://www.theregister.com/2020/12/12/zodiac_killers_cipher_solved/

> **启示**：Z340 的突破来自（1）统计异常的长期积累（pivots、周期-19），（2）对换位空间的系统枚举，（3）高性能同音替换求解器，（4）对“作者本人加密错误”的容忍与建模。同时它提醒我们：**Zodiac 会在同音替换之上叠加换位，而且会犯错**——这两点必须纳入对 Z13/Z32 的建模。

---

## 3. Z13（未破解）

### 3.1 基本事实

- **出处**：1970-04-20 旧金山邮戳，寄往《SF Chronicle》。信中写道：“By the way have you cracked the last cipher I sent you? My name is —”，随后给出 13 个符号。同信附有光电开关控制的炸弹示意图，并记分“[Zodiac 符号] = 10, SFPD = 0”。
  来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_April_20th_1970 · https://www.zodiackiller.com/MyNameIsLetter.html
- **转录**（Oranchak webtoy 方案）：`AENz0K0M0[NAM`；13 个符号，8 个不同符号；重复位置：A(1,12)、N(3,11)、圈8(5,7,9)、M(8,13)。详见 [../data/README.md](../data/README.md)。

### 3.2 主要破译声明

| 声明明文 | 提出者 / 时间 | 方法 | 是否符合重复模式 | 评价 | 来源 |
|---|---|---|---|---|---|
| ALFRED E NEUMAN（《Mad》杂志吉祥物） | Craig Bauer，《Unsolved!》2017, p.182 | 前三符号 AEN 恰为其首字母 | **否**：两个 N 须分别解为 F 与 M，需假设一处加密错误 | 趣味性强，但违反纯替换约束 | https://www.history.com/articles/the-zodiac-ciphers-what-we-know · https://ciphermysteries.com/2017/12/16/zodiac-killers-z13-cipher-meets-z340-cipher |
| DR EAT A TOTPEDO（= torpedo） | Ryan Garlick（北德州大学），2020-12 论坛首发；2025-04-08《Let's Crack Zodiac》#23 | 沿用 Z340 密钥，圈8→T，倒 T 形符号→P；解读为嘲讽美国密码协会（ACA）会长 D.C.B. Marsh（曾公开挑战 Zodiac 在密文中写出姓名） | **是**（D/D、E/E、O/O、T/T/T） | 批评：混用 Z340 符号与新符号、需接受拼写错误 TOTPEDO | https://zodiackillerciphers.com/zodiac-killers-z13-cipher-solved/ · https://forum.zodiackillerciphers.com/community/zodiac-cipher-mailings-discussion/ryan-garlicks-z13-solution/ |
| KAYR → KAYE（指嫌疑人 Lawrence Kane，化名 Kaye） | Fayçal Ziraoui，2021-01-19 | Z340 密钥 → A1Z26 变体 → 表盘位置 → Trifid 多步变换 | — | 步骤过多，等于“强行”得到结果；Oranchak 对《纽约时报》表示“几乎不可能判断其中任何一个是否正确” | https://forum.zodiackillerciphers.com/community/zodiac-cipher-mailings-discussion/detailed-solution-to-z13-and-z32/ · https://www.oxygen.com/crime-news/faycal-ziraoui-says-he-cracked-remaining-zodiac-ciphers |
| Gary Francis Poste | Case Breakers，2021-10-06 | 从信件字母中剔除 Poste 全名后对余下字母做变位 | — | Sam Blake：Z13 信息量不足以确定任何解，软件可生成数百万候选；FBI 否认案件已破 | https://www.abc.net.au/news/2021-10-07/zodiac-killer-could-be-gary-poste/100520022 · https://www.nbcnews.com/news/us-news/case-remains-open-fbi-refutes-claim-zodiac-killer-case-solved-n1281002 |
| Earl Van Best Jr | Gary L. Stewart | “Earl Van Best Jr” 恰好 13 个字母 | **否**（第 1、12 位应同字母，却为 E 与 J） | 循环论证 | https://zodiackillerfacts.com/zodiac-theories/the-accused-the-accusers/earl-van-best-jr-gary-stewart/ |
| LEE ALLEN / ALLEN NAME（Arthur Leigh Allen） | Tim Clausen，2025–26（借助 AI 工具） | 以“校验和”将圈8设为 L | — | 自费发布，未经独立验证 | https://thezodiacsolved.com/debunked-theories.html |
| thebigsecrete | Michael Kelleher | 将圈8视为通配符 | — | 自由度过高 | https://zodiackillerciphers.com/wiki/index.php?title=Z13_Solutions |
| NAME (IS) GRANT | Lyndon Lafferty | — | — | — | 同上 |
| ED SHAW | “Rembrandt” | Z408 密钥 + 空符 | — | — | 同上 |
| FROM TED KACZYNS[K]I | Doug Oswell | — | — | 需补字母 | 同上 |
| “Eddie Penerden”、“Steve Pete West”、“Gary Lyle Large”、“Laura Catapult” 等 | Oranchak 等（**反例演示**） | 专门构造的“完全符合重复模式”的名字 | **是** | 用来说明：符合模式的名字多得是，符合本身不构成证据 | 同上 |

### 3.3 可解性评估

- Oranchak Wiki：允许变位时，在 69,607 个常见名/姓样本中有大量名字“可以符合”，连 “international” 这类 13 字母单词也符合；即便不允许变位，解也非常多，“可能根本无法选出正确的那一个”。
  来源：https://zodiackillerciphers.com/wiki/index.php?title=Z13_Solutions
- Oranchak、Blake、Van Eycke（arXiv:2403.17350）：Z13 的密码分析“基本不可能”，解不唯一，数千个已提出的解都无法证伪。
- Craig Bauer：Z13 短到足以容许多个解。
- **本项目推算**：Z13 的 multiplicity = 8/13 ≈ 0.62（参考：Z408 ≈ 0.13，Z340 ≈ 0.19）；而英文简单替换密码的唯一解距离约 28 字符，同音替换的唯一解距离更长（Z340 体制为 80–152）。13 个符号远低于任何合理的唯一解距离——**纯密文分析在理论上无法得到唯一解**，必须引入外部约束（见 [../docs/roadmap.md](../docs/roadmap.md)）。

---

## 4. Z32（未破解）

### 4.1 基本事实

- **出处**：1970-06-26 旧金山邮戳，寄往《SF Chronicle》（俗称“Button 信”）。信中抱怨没人佩戴他的徽章（button），称因学校放假未能炸校车，改为“用 .38 手枪射杀了一名坐在车里的男子”；并称“地图配合这段密码将告诉你们炸弹埋在哪里，你们有时间到明年秋天去挖出来”。附一张 Phillips 66 湾区公路地图，在 Mt. Diablo 上画有 Zodiac 十字圈符号，外圈顺时针标 0、3、6、9，旁注 “0 is to be set to Mag. N.”（0 应对准磁北）。
  来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_June_26th_1970 · https://www.zodiackiller.com/ZMap.html
- **后续线索**：1970-07-26 “Little List”（戏仿《日本天皇》）信的附言：“PS. The Mt. Diablo Code concerns Radians & # inches along the radians”（Mt. Diablo 密码与弧度及沿弧度方向的英寸数有关）。
  来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_July_26th_1970
- **地图比例**：约 1 英寸 ≈ 6.4 英里（Pelling）。**1970 年 Mt. Diablo 磁偏角**：约 16.88° E（NOAA DGRF70 模型计算）。
- **转录**（Oranchak webtoy 方案，两行，17 + 15）：
  ```
  C9J|#Ok[AMf8?ORTG
  X6FDVj%HCELzPW9
  ```
  32 个符号、29 个不同符号，仅 3 个符号重复：C(1,26)、△(2,32)、O(6,14)。详见 [../data/README.md](../data/README.md)。
- **用 Z408 密钥直接解 Z32**：得到乱码（Pelling 试验）。来源：https://ciphermysteries.com/other-ciphers/zodiac-killer-ciphers/zodiac-killer-z32

### 4.2 Gareth Penn 的“弧度理论”

- **出处**：“Portrait of the Artist as a Mass Murderer”，*California Magazine*，1981-11；著作《Times 17》（1987）、《The Second Power》（1999）。
- **内容**：以 Mt. Diablo 为顶点，几个作案地点之间构成约 1 弧度（57.3°）的夹角；据此指认伯克利教授 Michael O'Hare（O'Hare 曾就此向 FBI 投诉；1981 年 FBI 探员警告过 Penn）。
- **不同来源对其几何构造的描述并不一致**（维基百科引 Bauer p.190；Foxon；ZodiacKillerFacts）。
- **批评**（Michael Butterfield）：Penn 选用了高尔夫球场而非 Blue Rock Springs 公园真实案发点，校正后夹角约 60°；且 Zodiac 写的是复数 “radians”。
- 来源：https://en.wikipedia.org/wiki/Gareth_Penn · https://zodiackillerfacts.com/myths-legends/debunking-the-radian-theory/ · https://washingtonmonthly.com/2009/05/01/confessions-of-a-nonserial-killer/

### 4.3 其他破译声明（按时间）

| 提出者 | 时间 | 声明 | 评价 / 备注 | 来源 |
|---|---|---|---|---|
| Blaine Smith | 1986 手稿 | 密码指向 Richard Gaikowski、Darlene Ferrin、Webster 学区 | FBI（1991-12）核查结论为否定 | https://zodiackillerfacts.com/zodiac-theories/the-accused-the-accusers/richard-gaikowski-and-blaine-blaine-the-rest-of-the-story/ |
| Sundberg & Thelin（瑞典） | 2014-01 | 符号读作化学式（C3H3 + 辛烷、HClO3）；11 点钟方向径向、向西 1 英寸 | Pelling 否定其推理 | https://ciphermysteries.com/2014/01/30/swedish-zodiac-killer-z32-theory |
| David Cobb | 2018-01 | “CALI [纬度] NORTH / X [经度] WEST” 坐标方案 | — | https://www.zodiacz32.com/z32-exercise |
| Richard Grinell | 2018-09 | “RADIANS AND 5 INCHES ALONG THE RADIANS” | 三角形符号映射不一致（A/S） | Foxon 2023 |
| Richard Grinell（归功于 Druzer；Oranchak Wiki 归功于 InStepWithTheStars） | 2020-06 | “ESTIMATE FOUR RADIANS AND FIVE INCHES”；4 rad + 17° ≈ 246°，5 英寸 → SFPD Ingleside 警局 | 符合重复模式（C=E、△=S、O=A） | https://www.zodiacciphers.com/zodiac-news/the-answer-to-the-mount-diablo-code |
| Francesco Amicone | 2018/2019 | “FOOTHILL BLVD HILLCREST 14 MI FAR 570°” → San Leandro 的 Eden Township 警局 | — | https://ostellovolante.com/2020/08/05/zodiac-mount-diablo-cipher-decrypted-eden-township-san-leandro/ |
| Fayçal Ziraoui | 2021-01 | “LABOR DAY FIND 45.609 NORT 58.719 WEST”，指向南太浩湖中学附近 | 媒体数字转述不一（45.069）；Foxon 批评步骤任意、有两个符号被直接丢弃 | https://www.oxygen.com/crime-news/faycal-ziraoui-says-he-cracked-remaining-zodiac-ciphers |
| Case Breakers | 2021-10 | 变位法 | 同 Z13 | Foxon 2023 §2.5 |
| Cragle | 不详 | “THREE RADIANS FROM MOUNT AREA TWO INCH” | 符合重复模式 | https://zodiackillerciphers.com/wiki/index.php?title=Z32_Solutions |
| Floe Foxon | 2023-06 | 把表盘“指针”按磁偏角（16–18°）设定得到 (12, 3)；经 Z340 式换位后读出带拼写错误的 “TWELVE INCHES ALONG THE THREE RADIANS” | 作者自认“不具说服力、属初步结果” | https://eprint.iacr.org/2023/982 |
| R. Allen | 2024 | SSRN 预印本 | 未经同行评审 | https://doi.org/10.2139/ssrn.4715713 |
| David Stampher | 2026 | “IN THREE AND THREE EIGHTHS RADIANS TEN” → 38.10995 N, 122.18535 W（Blue Rock Springs 附近）；附地理约束求解代码 | 未经他人验证 | https://github.com/dstampher/zodiac-z32-cipher |
| Grant Dickinson | 2026-03 | Devils Elbow → Lake Spaulding（与失踪护士 Donna Lass 相关） | Pelling 评论 | https://ciphermysteries.com/other-ciphers/zodiac-killer-ciphers/zodiac-killer-z32 |
| Praetorian（N. Sportsman） | 2026-04-01 | 弧度/角度三元组几何 | 注意发布日期为愚人节；作者承认可能是事后推理 | https://www.praetorian.com/blog/a-possible-solution-to-the-zodiac-killer-z32-cipher/ |
| Tim Clausen | 2025–26 | “I AM THE ZODIAC KILLER” | 未经独立验证 | https://thezodiacsolved.com/debunked-theories.html |

### 4.4 可解性评估

- Oranchak Wiki：Z32 “可能是最难以有把握地破解的一份，因为重复符号极少”。
- Oranchak、Blake、Van Eycke（arXiv:2403.17350）：Z32 短且唯一符号过多，难以分析；引用 King & Bahler 的 multiplicity 概念。
- Craig Bauer：建议用 Kevin Knight 的 CARMEL 程序系统测试地图上的数值位置。
- **本项目推算**：Z32 的 multiplicity = 29/32 ≈ 0.91——几乎每个符号只出现一次，任何含 3 组重复字母、长度 32 的英文句子都可能“符合”。**唯一可行的路径是引入强外部约束**：地图几何（磁北、弧度、英寸、比例尺）、与 Z408/Z340 的密钥关联、以及可能的换位结构。

---

## 5. 其他信件中的“暗码”声明

以下信件并非正式密文，但常被认为藏有信息。所列均为个人主张，**无一被执法机构或主流研究者接受**。

| 信件 | 声明 / 解读 | 提出者 | 评价 | 来源 |
|---|---|---|---|---|
| 1969-11-08“滴墨笔”贺卡 | “Des July Aug Sept Oct = 7” 对应 11-09 炸弹信十字准星上的刻痕（钟点位置） | 博客评论者 “ggluckman”“Doc” | 无法证伪 | https://zodiackillerciphers.com/daryll-lathers-solution-makes-the-front-page/ |
| 同上 | 该串 17 字符、月份全称 34 字符，与 Z340 的 17 列相关 | Marcelo Leandro | 数字巧合 | https://www.zodiacciphers.com/zodiac-news/the-dripping-pen |
| 1970-04-20 炸弹图 | 炸弹图藏在 Z340 中 | 论坛用户【待核实】 | Z340 已解，明文中无此内容 | — |
| 1970-10-27 万圣节卡（寄 Paul Avery） | “VF” 状符号：仙后座、牛烙印、宽翼缘钢梁（Graysmith）、“4F”、卢恩字母、Hells Angels 等 | 多人 | 无共识 | https://zodiackillerciphers.com/wiki/index.php?title=Halloween_card |
| 同上 | “BY GUN” 做 +9 凯撒移位后经 Z408 密钥得到 “STINE” | Jade Goldstone | 多重自由度叠加 | 同上 |
| 同上 | “why spoil the game” 与当天《Examiner》对应，第 14 版刊有 Nancy Bennallack 案 | 论坛用户 “Shawn”，2020 | 无指向报纸的指令 | https://forum.zodiackillerciphers.com/community/10-27-70-halloween-card-sent-to-paul-avery/halloween-card-breakthrough/ |
| 同上 | 信封内 “Sorry no cipher” 暗示 Z13 | 论坛用户 “Urik”，2021 | 推测 | https://forum.zodiackillerciphers.com/community/zodiac-cipher-mailings-discussion/sorry-no-cipher/ |
| 同上 | 意大利语 “cucù” / “Q” 双关，指向 Bevilacqua | Francesco Amicone | 推测 | https://ostellovolante.com/2020/08/05/zodiac-halloween-riddle-and-italian-cuckoos-game/ |
| 1971-03-13《LA Times》信 | “Blue Meannies” 指阿拉米达县警、与电影《Vanishing Point》上映时间吻合等 | Richard Grinell | 观察性质 | https://www.zodiacciphers.com/los-angeles-times-letter.html |
| 1974-01-29 “Exorcist” 信末尾符号 | 读作 “To Kill”（Kevin Robert Brooks）、酱油桶（Kim Allen）、“HFC”（Harvey Francis Colliver）等 | 多人 | 仍无解释 | https://zodiackillerciphers.com/wiki/index.php?title=Exorcist_letter_markings · https://www.zodiacciphers.com/the-exorcist-letter.html |
| 十字准星符号本身 | 枪械瞄准镜、Zodiac 牌手表商标（嫌疑人 Arthur Leigh Allen 佩戴）、表盘/罗盘（地图上标有 0/3/6/9） | 多人 | 无定论 | https://en.wikipedia.org/wiki/Arthur_Leigh_Allen · https://forum.zodiackillerciphers.com/community/zodiac-case-general-discussion/the-zodiac-symbol-is-a-watch-face-rather-than-crosshairs/ |
| 2021 “Case Breakers” | 从多封信中变位出 Gary Francis Poste 的全名 | Case Breakers（Jen Bucholtz、Dale Julin 等） | FBI：“案件仍在侦办，无新信息”；Riverside 警方否认 Bates 案与 Zodiac 相关；Grinell：已有 100 多个名字被“硬塞进” Z13 | https://www.nbcnews.com/news/us-news/case-remains-open-fbi-refutes-claim-zodiac-killer-case-solved-n1281002 · https://forum.zodiackillerciphers.com/community/zodiac-suspects-pois-general-discussion/gary-f-poste/ |

---

## 6. 经验教训：失败声明的共同模式

综合上述案例，被否定的“破译”几乎都落入以下陷阱之一。本项目将以此作为自我审查清单（详见 [../docs/roadmap.md](../docs/roadmap.md) 的评估标准）：

1. **放宽“同一符号 = 同一字母”约束**（Cecil、Lathers、History Channel）——自由度一旦放开，任何明文都能“解”出来。
2. **变位（anagram）**（Graysmith、Robert Emmet、Case Breakers）——字母串越长，可拼出的名字越多，几乎无证据价值。
3. **先有嫌疑人，后找证据**（Stewart、Starliper、Penn）——目标明文预设导致确认偏误。
4. **挑选数据**（Penn 的弧度理论选用高尔夫球场而非 Blue Rock Springs 公园）——在众多候选点中总能找到“吻合”的几何关系。
5. **无统计显著性检验**——从不计算“随机密文/随机密钥下出现同等吻合的概率”。
6. **不可复现**——未公开完整密钥与步骤，他人无法独立验证。

相反，Z408 与 Z340 的真正解都满足：**密钥前后一致、明文连贯可读且风格与 Zodiac 其他信件一致、方法可被第三方独立复现、错误可被解释且数量有限**。

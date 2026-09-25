# 案件与密文概览

> 最后整理：2026-09-25。所有事实均附来源；【待核实】/【有争议】含义同 [../references/README.md](../references/README.md)。

---

## 1. 案件背景

“黄道十二宫杀手”（Zodiac Killer）是 1960 年代末至 1970 年代初活动于美国北加州旧金山湾区的连环杀手，身份至今未被确认。

**已确认的袭击（7 名受害者，5 人死亡）**

| 日期 | 地点 | 受害者 |
|---|---|---|
| 1968-12-20 | Lake Herman Road（Benicia/Vallejo 附近） | David Faraday（17，死亡）、Betty Lou Jensen（16，死亡） |
| 1969-07-04 午夜前后 | Blue Rock Springs 公园，Vallejo | Darlene Ferrin（22，死亡）、Michael Mageau（19，幸存） |
| 1969-09-27 | Lake Berryessa | Cecelia Shepard（22，两日后死亡）、Bryan Hartnell（20，幸存） |
| 1969-10-11 | Presidio Heights，旧金山（Washington 街与 Cherry 街口） | 出租车司机 Paul Stine（29，死亡） |

**案件状态**：未结。SFPD 曾于 2004 年将案件列为非活跃，2006 年重新开启；FBI、加州司法部、Vallejo 警局及 Napa、Solano 两县警长办公室仍将其列为未结案件。2021 年 “Case Breakers” 声称凶手为 Gary Francis Poste，FBI 回应“案件仍在侦办，无新信息”；2023 年再度重申案件未破。

来源：https://en.wikipedia.org/wiki/Zodiac_Killer · https://www.nbcnews.com/news/us-news/case-remains-open-fbi-refutes-claim-zodiac-killer-case-solved-n1281002 · https://www.newsweek.com/did-fbi-miss-chance-arrest-suspect-zodiac-killer-gary-francis-poste-1801101

---

## 2. 四份密文一览

| 代号 | 寄出日期 | 收件方 | 长度 / 不同符号 | 体制 | 状态 |
|---|---|---|---|---|---|
| **Z408** | 1969-07-31 | 《Vallejo Times-Herald》《SF Examiner》《SF Chronicle》各三分之一 | 408 / 54（24×17） | 同音替换 | **已解**：1969-08 由 Donald & Bettye Harden 破解；末尾 18 字符无公认解释 |
| **Z340** | 1969-11-08 | 《SF Chronicle》（附“滴墨笔”贺卡） | 340 / 63（20×17） | 同音替换 + 换位（(1,2)-抽取） | **已解**：2020-12 由 Oranchak、Blake、Van Eycke 破解，FBI 确认 |
| **Z13** | 1970-04-20 | 《SF Chronicle》 | 13 / 8 | 未知 | **未解**：信中写“My name is —”，其后为该密文 |
| **Z32** | 1970-06-26 | 《SF Chronicle》（附 Phillips 66 地图） | 32 / 29（两行 17+15） | 未知 | **未解**：声称配合地图可找到埋藏的炸弹 |

各密文的详细破译经过见 [../references/attempts.md](../references/attempts.md)；Z13 / Z32 的逐符号转录见 [../data/README.md](../data/README.md)。

### 2.1 Z408 要点

- 信中声称密文包含其身份，并以“整个周末四处杀人”威胁报社刊登。
- 明文大意：自称享受杀人、影射小说《The Most Dangerous Game》，声称受害者将在来世成为他的奴隶（“paradice”），拼写错误甚多。**不含姓名。**
- 已知 Zodiac 本人约 5 处加密错误；同音字存在按顺序轮换使用的规律。

### 2.2 Z340 要点

- 20×17 网格分三段：第 1–9 行、第 10–18 行各自按“下 1 右 2”的抽取路径读取，第 19–20 行正常读取（部分单词倒写）。
- 明文大意：嘲讽警方追捕、否认曾在电视节目中打电话、声称不惧毒气室。**不含 “ZODIAC”，也不含任何人名。**
- 对 Z13/Z32 的启示：**Zodiac 会叠加换位、会倒写、会犯加密错误。**

### 2.3 Z13 要点

- 同信内容：询问“你们破解了我上次寄的密码吗”、否认用炸弹杀死警局警察、附光电开关炸弹图、记分“[Zodiac 符号] = 10, SFPD = 0”。
- 转录：`AENz0K0M0[NAM`。其中“圈 8”（3 次）与 `[` 从未在 Z408/Z340 中出现。
- 来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_April_20th_1970 · https://zodiackillerciphers.com/wiki/index.php?title=Unsolved_13-character_%22My_name_is%22_cipher

### 2.4 Z32 要点

- 同信内容：抱怨没人佩戴他的徽章（button），称因学校放假未炸校车，改为射杀一名坐在车中的男子；“地图配合这段密码将告诉你们炸弹埋在哪里，你们有时间到明年秋天去挖出来。”
- 地图：Phillips 66 湾区公路地图，Mt. Diablo 上画十字圈，外圈顺时针标 0、3、6、9，注明 “0 is to be set to Mag. N.”；比例约 1 英寸 ≈ 6.4 英里；1970 年当地磁偏角 ≈ 16.88° E（NOAA）。
- 追加线索（1970-07-26 信附言）：“The Mt. Diablo Code concerns Radians & # inches along the radians”。
- 转录：`C9J|#Ok[AMf8?ORTG` / `X6FDVj%HCELzPW9`。
- 来源：https://en.wikisource.org/wiki/Zodiac_Killer_letter,_June_26th_1970 · https://en.wikisource.org/wiki/Zodiac_Killer_letter,_July_26th_1970 · https://zodiackillerciphers.com/wiki/index.php?title=Unsolved_32-character_%22map_code%22_cipher

---

## 3. 信件年表（含非密文通信）

> 真实性判断：网上没有官方的统一清单。下表“状态”综合英文维基百科与 Tom Voigt 清单（最常被引用的非官方清单）。

| 日期（邮戳） | 收件方 | 内容摘要 | 密码 / 符号内容 | 状态 |
|---|---|---|---|---|
| 1966-11-29 | Riverside 警局、《Riverside Press-Enterprise》 | “The Confession”，自称杀害 Cheri Jo Bates | 无 | 有争议 |
| 1966-12 | Riverside City College 图书馆课桌 | “Sick of living / unwilling to die”诗，署 “r h” | 无 | 有争议 |
| 1967-04-30 | Riverside 警局、报社、Bates 之父 | “Bates had to die” | 底部有类 Z 记号 | 有争议（Riverside 警局 2021 年称 Bates 案与 Zodiac 无关） |
| 1969-07-31 | 三家报社 | 各附 Z408 的三分之一 | **Z408** | 真实 |
| 1969-08-04 | 《SF Examiner》 | 首次使用 “This is the Zodiac speaking” | 无 | 真实 |
| 1969-09-27 | Lake Berryessa 受害者车门 | 十字圈符号 + 作案日期 | 十字圈 | 真实 |
| 1969-10-13 | 《SF Chronicle》 | 附 Paul Stine 衬衫碎片，威胁校车 | 无 | 真实 |
| 1969-11-08 | 《SF Chronicle》 | “滴墨笔”贺卡，“Des July Aug Sept Oct = 7” | **Z340** | 真实 |
| 1969-11-09 | 《SF Chronicle》 | 7 页“校车炸弹”信，附炸弹图 | 炸弹图 | 真实 |
| 1969-12-20 | 律师 Melvin Belli | 附 Stine 衬衫碎片，“Please help me I am drownding” | 无 | 真实 |
| 1970-04-20 | 《SF Chronicle》 | “My name is” 信，炸弹图，“SFPD = 0” | **Z13** | 真实 |
| 1970-04-28 | 《SF Chronicle》 | “Dragon”贺卡，要求人们佩戴 Zodiac 徽章 | 无 | 真实 |
| 1970-06-26 | 《SF Chronicle》 | “Button”信，附 Phillips 66 地图 | **Z32** + 地图 | 真实 |
| 1970-07-24 | 《SF Chronicle》 | 提及 1970-03-22 Kathleen Johns 被绑架事件 | 无 | 真实 |
| 1970-07-26 | 《SF Chronicle》 | “Little List”（戏仿《日本天皇》），记分 “= 13, SFPD = 0” | **弧度附言**（Z32 线索） | 真实 |
| 1970-10-05 | 《SF Chronicle》 | 用报纸剪字拼贴的 3×5 卡片，打有 13 个孔 | 13 孔、十字 | 有争议 |
| 1970-10-27 | 记者 Paul Avery | 万圣节卡：“Peek-a-boo you are doomed”、“4-TEEN”、“PARADICE SLAVES”十字排列 | 多种符号 | 真实 |
| 1971-03-13 | 《Los Angeles Times》 | 自称“17+”名受害者、“SFPD-0”、“Blue Meannies” | 无 | 真实 |
| 1971-03-22 | Paul Avery | Lake Tahoe 拼贴明信片，与失踪护士 Donna Lass 相关 | 拼贴 | Voigt 列入；维基未判定 |
| 1974-01-29 | 《SF Chronicle》 | “Exorcist”信，“Me = 37, SFPD = 0” | 末尾未解符号 | 一般认为真实 |
| 1974-02 | 《SF Chronicle》 | “SLA” 信，署 “a friend” | 无 | 有争议 |
| 1974-05-08 | 《SF Chronicle》 | “Citizen”/“Badlands” 卡片 | 无 | 有争议 |
| 1974-07-08 | 《SF Chronicle》 | “Red Phantom” 信 | 无 | 有争议 |
| 1978-04-24 | 《SF Chronicle》 | “I am back with you” | 十字圈 | 多数认为伪造 |

来源：https://en.wikisource.org/wiki/Zodiac_Killer_letters · https://www.zodiackiller.com/Letters.html · https://en.wikipedia.org/wiki/Zodiac_Killer

---

## 4. 已知的 Zodiac 书写 / 加密习惯（供建模参考）

| 习惯 | 证据 | 对 Z13/Z32 的意义 |
|---|---|---|
| 系统性拼写错误 | PARADICE、FRUNT、CRUSE、BUSS、UNTILL、IDENITY、DROWNDING 等 | 语言模型需容忍其个人拼写 |
| 加密错误 | Z408 约 5 处；Z340 多处（如 SOOHER→SOONER） | 错误模型需要先验，不能事后随意修正 |
| 同音字顺序轮换 | Z408（King & Bahler 1993） | 可能为短密文提供额外约束 |
| 叠加换位 | Z340 的 (1,2)-抽取 | 不能默认 Z13/Z32 为纯替换 |
| 倒写 | Z340 末两行（ECIDARAP） | 需纳入换位族 |
| 填充 | Z408 末尾 18 字符疑为填充 | 短密文中也可能有空符 |
| 17 列网格 | Z408、Z340 均为 17 列；Z32 第 1 行恰为 17 符号 | 值得检验的结构线索 |
| 地理 / 数学提示 | 地图、磁北、弧度、英寸 | Z32 明文很可能包含数值与方位信息 |

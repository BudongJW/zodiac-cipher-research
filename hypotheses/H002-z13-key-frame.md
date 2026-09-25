# H002：Z13 在 Z340 / Z408 密钥下的框架可读（检验 Garlick 读法的统计依据）

- 提出日期 / 提出人：2026-09-25 / 本项目
- 目标密文：Z13
- 动机：Z13 的 8 个符号中 6 个（A、E、N、⊕、K、M）见于 Z340 与 Z408。把 Z340 密钥代入得到框架 `DREA_A_O__EDO`，Garlick 的 “DR EAT A TOTPEDO” 即在此框架上为圈 8、`[` 两个符号选定 T、P。问题是：这个框架是否比随机密钥给出的框架更容易被补成英文？
- 密码体制假设：共有符号沿用 Z340（或 Z408）密钥，圈 8 与 `[` 字母未知。考察三种读法：原顺序、逆序、删去圈 8（视为空符）。
- 参数空间与自由度：2 个自由符号（穷举 676 种）；删去圈 8 时 1 个（26 种）。
- 打分函数与判定阈值（运行前写定）：统计量 = 穷举中目标函数的最高分。**p < 0.01 判为“支持”，否则“不支持”。** 另报告 Garlick 读法在 676 种补全中的排名。
- 零假设对照设计：把密钥字母在其全部符号间随机打乱 2000 次，取同样位置的 6 个符号构成随机框架，重复穷举取最高分。
- 运行记录：`python scripts/m4_key_reuse.py --model models/5-grams_english_beijinghouse_10TB_v7.gz`（种子 0）
- 结果：见下文“结果”一节（运行后补充，以上各项不作修改）
- 结论：**不支持**（6 个变体均未达到 p < 0.01；最小者 p = 0.014）

## 结果（2026-09-25 运行，零假设 2000 次）

| 密钥 / 读法 | 框架 | 最佳补全 | 得分 | 零假设 | p |
|---|---|---|---|---|---|
| **Z340 / 原顺序** | `DREA_A_O__EDO` | DREATATOTHEDO | 85.7 | 63.8 ± 10.2 | **0.014** |
| Z340 / 逆序 | `ODE__O_A_AERD` | ODESTOTATAERD | 71.0 | 64.1 ± 9.9 | 0.24 |
| Z340 / 删去圈 8 | `DREAAO_EDO` | DREAAONEDO | 50.4 | 47.1 ± 12.8 | 0.39 |
| Z408 / 原顺序 | `WEED_S_H__EWH` | WEEDASAHAVEWH | 74.4 | 62.9 ± 10.1 | 0.12 |
| Z408 / 逆序 | `HWE__H_S_DEEW` | HWERAHASADEEW | 65.2 | 63.3 ± 10.4 | 0.43 |
| Z408 / 删去圈 8 | `WEEDSH_EWH` | WEEDSHOEWH | 58.0 | 45.9 ± 13.4 | 0.18 |

**Z340 / 原顺序框架的前 10 种补全**：DREATATOTHEDO、DREANANONCEDO、DREASASOSTEDO、DREANANONTEDO、DREANANONSEDO、DREANANONWEDO、DREANANONGEDO、DREASASOSHEDO、DREANANONBEDO、DREANANONMEDO。
**Garlick 的读法 DREATATOTPEDO 在 676 种补全中排第 58。**

**解读**：
1. 按预注册标准，六个变体都不支持“Z13 沿用已知密钥”。
2. Z340 / 原顺序的 p = 0.014 是一个**弱信号**：该框架比约 98.6% 的随机框架更容易补成“像英文”的串。但它未达到预注册阈值，且共做了 6 次比较（Bonferroni 校正后阈值为 0.0017），不能据此认定。
3. 即使接受 Z340 框架，语言模型也并不偏好 Garlick 的补全（第 58 名）；圈 8 取 T 的补全 “DR EAT A TOT HE DO” 同样不成句。Garlick 读法的说服力来自对 “D.C.B. Marsh / torpedo” 的语境解读，而非统计证据。
4. 后续若要追踪这一弱信号，应**另行预注册**一个独立检验（例如：用 Z340 框架对照 Zodiac 其他信件中的用语），而不是在同一数据上继续调整。

结果文件：`results/m4_key_reuse.json`。

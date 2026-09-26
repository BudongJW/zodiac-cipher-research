# 其他被归于 Zodiac 的密文（对照数据）

这些密文都**不是**公认的 Zodiac 真迹。收录它们是为了：检验“是否有与 Z32 同一密钥的其他密文”，以及作为工具链的对照（阴性 / 阳性）样本。详见 [../../references/external-leads.md](../../references/external-leads.md)。

| 文件 | 名称 | 日期 / 来源 | 长度 / 不同符号 | 真实性 | 本项目结果 |
|---|---|---|---|---|---|
| [z148.txt](z148.txt) | “Z148”（Fairfield 148） | 约 1971-05，Fairfield 邮戳，寄《SF Chronicle》 | 148 / 24 | 有争议，多认为是模仿者 | 本项目求解器 16 秒解出（**简单替换**，非同音替换），开头为 “…THE ZODIAC SPEAKING…”，与 zodiologists.com 公布的解一致；体制与 Z32 不同 |
| [albany51.txt](albany51.txt) | Albany Medical Center 信 | 1973-08-01，寄 Albany *Times Union* | 51 / 24 | 有争议，多认为是模仿者 | 太短，每次重启得到不同的读法（与 M2 基线一致）；FBI 曾读出大部分内容 |
| [z263_94.txt](z263_94.txt)、[z263_169.txt](z263_169.txt) | “Z263”（1988 年 Stamford / New Canaan 信） | 1988-04，Stamford, CT | 94 / 51、169 / 54 | 恶作剧 / 模仿者 | 两段开头 6 个符号相同（FMGYOS），疑为同一密钥；详见 external-leads.md |

来源：转录取自 AZdecrypt 1.25 附带数据（https://github.com/doranchak/azdecrypt ，`AZdecrypt/Ciphers/Zodiac ciphers/`，GPL-3.0）。背景资料见 external-leads.md 所列来源。

**未收录**：1969-12-07 Fairfield 信中的 38 符号密文（“Z38”）是唯一一个可能与 Z340 / Z32 同一体制的候选，但目前没有公开的文本转录，只有质量很差的图像。

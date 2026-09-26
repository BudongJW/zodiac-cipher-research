# 原件图像请求草稿（Z13 / Z32）

> 目的：取得 1970-04-20 信（含 Z13）与 1970-06-26 信（含 Z32 与地图）的**高分辨率图像**，用于核对三个“圈 8”是否为同一符号等字形问题（见 [glyph-report.md](glyph-report.md)、[../references/external-leads.md §1](../references/external-leads.md#1-z13-原件与高清图像)）。
> **本文件只是草稿**：是否提出、以谁的名义提出，由项目负责人决定。请在发送前补全 `[方括号]` 中的信息，并核对各机构当前的提交渠道与所引法条编号（加州公共记录法已于 2023 年重新编号）。

## 策略要点

- **只请求已有的复制件**（照片、扫描件、2002 年为 ABC 制作的彩色复制件、实验室照片），不请求接触证物本身，以降低被“案件未结”理由拒绝的可能。
- 强调这些信件**早在 1970 年即已登报公开**，提供其图像不会损害调查。
- 说明用途为非商业的密码学研究，结果公开发表。
- 各机构分别提交；保留提交记录与回复。

---

## 1. 旧金山警察局（SFPD）——《加州公共记录法》请求

提交渠道：https://sanfrancisco.nextrequest.com/ 或 https://www.sanfranciscopolice.org/get-service/public-records-request/form

```text
Subject: California Public Records Act request – existing images of two 1970 "Zodiac" letters

To the San Francisco Police Department, Custodian of Records:

Under the California Public Records Act (Gov. Code § 7920.000 et seq.), I request copies of
EXISTING photographs, photocopies or digital scans (not access to physical evidence) of the
following two documents, both of which were published by the San Francisco Chronicle in 1970:

  1. The letter postmarked April 20, 1970, addressed to the San Francisco Chronicle
     (the "My name is" letter containing a 13-symbol cipher and a bomb diagram);
  2. The letter postmarked June 26, 1970, addressed to the San Francisco Chronicle,
     together with the enclosed Phillips 66 map (the "button" letter containing a
     32-symbol cipher).

This request includes, where they exist: crime-laboratory photographs; the color
reproductions made in 2002 (reported by ABC News "Primetime"); and any other image
records of these two documents. I request the images in electronic form at the highest
resolution in which they are held (ideally 600 dpi or higher, in color).

Because the full text and images of both letters were published in 1970 and remain widely
reproduced, releasing images of them would not disclose investigative information or
endanger any investigation. If any portion is withheld, please cite the specific exemption
and release all reasonably segregable portions (Gov. Code § 7922.525).

The purpose is non-commercial cryptographic research on the unsolved ciphers; results are
published openly. Please inform me in advance if fees will exceed [USD amount].

Thank you,
[Name]
[Email / postal address]
```

## 2. 《旧金山纪事报》（San Francisco Chronicle）——档案图片

联系方式：报社图片授权（据称为 licensing@sfchronicle.com，经由 Wright's Media 办理【待核实】）

```text
Subject: Archive image request – Zodiac letters of April 20 and June 26, 1970

Hello,

I am researching the unsolved Zodiac ciphers. I would like to license (or purchase
research-use copies of) the highest-resolution images held in the Chronicle archive of:

  - the letter to the Chronicle postmarked April 20, 1970 (13-symbol cipher and bomb diagram);
  - the letter to the Chronicle postmarked June 26, 1970, with its Phillips 66 map.

If the archive holds original photographs, photostats or negatives made in 1970, those
would be most valuable; newspaper page scans are also helpful. Please let me know the
available formats, resolutions and fees for non-commercial research use.

Best regards,
[Name, affiliation, contact]
```

## 3. ABC News——2002 年《Primetime》彩色复制件

联系方式：ABC News 资料 / 授权部门【待核实】

```text
Subject: Request regarding 2002 "Primetime" color reproductions of Zodiac letters

Hello,

In October 2002, ABC News "Primetime" reported having high-resolution color copies made of
the original Zodiac letters held by the San Francisco Police Department. For non-commercial
cryptographic research, I would like to ask whether the images of the letter postmarked
April 20, 1970 (13-symbol cipher) and the letter postmarked June 26, 1970 (32-symbol cipher
and map) could be licensed or shared at full resolution, with or without watermark.

Thank you for considering this request.
[Name, affiliation, contact]
```

## 4. FBI——《信息自由法》（FOIA）请求

提交渠道：FBI eFOIPA 门户 https://efoia.fbi.gov/ 。已知档案号 9-HQ-49911（2012 年曾有研究者取得约 800–1,000 页）。FBI 档案中多为影印件，预期分辨率有限。

```text
Request: All photographs, photocopies and laboratory images of letters and ciphers
attributed to the "Zodiac" (FBI file 9-HQ-49911), specifically including the letters
postmarked April 20, 1970 and June 26, 1970 (with map), and any FBI Laboratory or
Cryptanalysis Unit reports on the 13-character and 32-character ciphers, provided in
the highest available image resolution. Previously released pages may be provided in
their original scan resolution rather than re-processed copies.
```

---

## 收到图像之后

1. 按 `scripts/glyph_sheets.py` 的方式切分字形，逐一比对三个圈 8、第 10 / 11 位，以及 Z32 第 26 位；
2. 如发现新的读法，先按 `hypotheses/` 模板**预注册**，再重跑 M2（`scripts/m2_z13_names.py`、`scripts/glyph_sensitivity.py`）；
3. 注意图像的授权条件：非公有领域的图像只用于分析，不放入本仓库。

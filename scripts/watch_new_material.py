"""监测 Zodiac 密码相关的新材料与新声明（手动运行，不做任何定时或持久配置）。

检查以下公开来源在 --since 之后的新条目：
    GitHub 新仓库（REST 搜索 API；标出 references/ 中尚未收录的项目）
    David Oranchak 的博客（zodiackillerciphers.com）RSS
    Cipher Mysteries RSS（只保留与 Zodiac 相关的文章）
    Zenodo 新记录（关键词 zodiac cipher）
    arXiv 新论文（关键词 zodiac + cipher）
新的逐位读法可用 `python -m zkc score` 评分，并补入 data/claims.json。

用法：python scripts/watch_new_material.py [--since 2026-09-01] [--out report.md]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zkc.cipher import ROOT  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402

UA = "zodiac-cipher-research-watch/0.1 (+https://github.com/BudongJW/zodiac-cipher-research)"
GITHUB_QUERIES = ["zodiac cipher", "zodiac killer", "z340", "z13 zodiac", "z32 zodiac", "mount diablo cipher"]
TIMEOUT = 20


def _ssl_context() -> ssl.SSLContext:
    try:  # 某些环境的系统证书库不完整；若装有 certifi 则使用其证书
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def github_token() -> str | None:
    """GITHUB_TOKEN 环境变量，或本机已登录的 gh CLI 的令牌（仅用于提高搜索 API 的速率上限）。"""
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    if shutil.which("gh"):
        r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


def fetch(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=_ssl_context()) as resp:
        return resp.read()


def known_text() -> str:
    """references/ 与 docs/ 的全部文本（小写），用于判断仓库是否已收录（含只写了 owner/repo 的情形）。"""
    paths = list((ROOT / "references").glob("*.md")) + list((ROOT / "docs").glob("*.md"))
    return "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()


def github_new(since: dt.date) -> list[dict]:
    token = github_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    found: dict[str, dict] = {}
    for q in GITHUB_QUERIES:
        query = urllib.parse.quote(f"{q} created:>={since.isoformat()}")
        data = json.loads(fetch(f"https://api.github.com/search/repositories?q={query}&sort=updated&per_page=50",
                                headers))
        time.sleep(0 if token else 7)  # 未认证时搜索 API 每分钟限 10 次
        for item in data.get("items", []):
            found[item["full_name"].lower()] = {
                "name": item["full_name"], "url": item["html_url"], "created": item["created_at"][:10],
                "stars": item["stargazers_count"], "description": (item.get("description") or "")[:120]}
    return sorted(found.values(), key=lambda r: r["created"], reverse=True)


def rss_new(url: str, since: dt.date, keyword: str | None = None) -> list[dict]:
    root = ET.fromstring(fetch(url))
    out = []
    for item in root.iter("item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        date = parsedate_to_datetime(item.findtext("pubDate")).date()
        text = title + " " + (item.findtext("description") or "")
        if date >= since and (keyword is None or keyword.lower() in text.lower()):
            out.append({"title": title, "url": link, "date": date.isoformat()})
    return out


def zenodo_new(since: dt.date) -> list[dict]:
    q = urllib.parse.quote('zodiac AND (cipher OR z13 OR z32 OR z340)')
    data = json.loads(fetch(f"https://zenodo.org/api/records?q={q}&sort=mostrecent&size=25"))
    out = []
    for hit in data.get("hits", {}).get("hits", []):
        created = hit.get("created", "")[:10]
        title = hit["metadata"]["title"].lower()
        relevant = "killer" in title or re.search(r"\bz(13|32|340|408)\b", title) or "mount diablo" in title
        if created and dt.date.fromisoformat(created) >= since and relevant:
            out.append({"title": hit["metadata"]["title"], "date": created,
                        "url": hit.get("links", {}).get("self_html") or f"https://zenodo.org/records/{hit['id']}"})
    return out


def arxiv_new(since: dt.date) -> list[dict]:
    q = urllib.parse.quote("all:zodiac AND all:cipher")
    root = ET.fromstring(fetch(f"http://export.arxiv.org/api/query?search_query={q}"
                               f"&sortBy=submittedDate&sortOrder=descending&max_results=20"))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in root.findall("a:entry", ns):
        date = e.findtext("a:published", default="", namespaces=ns)[:10]
        if date and dt.date.fromisoformat(date) >= since:
            out.append({"title": " ".join(e.findtext("a:title", "", ns).split()),
                        "url": e.findtext("a:id", "", ns), "date": date})
    return out


def main() -> None:
    utf8_stdio()
    p = argparse.ArgumentParser()
    p.add_argument("--since", default=(dt.date.today() - dt.timedelta(days=30)).isoformat())
    p.add_argument("--out", help="把报告另存为 Markdown 文件")
    args = p.parse_args()
    since = dt.date.fromisoformat(args.since)

    known = known_text()
    sources = {
        "GitHub 新仓库": lambda: github_new(since),
        "Oranchak 博客": lambda: rss_new("https://zodiackillerciphers.com/feed/", since),
        "Cipher Mysteries（Zodiac 相关）": lambda: rss_new("https://ciphermysteries.com/feed", since, "zodiac"),
        "Zenodo": lambda: zenodo_new(since),
        "arXiv": lambda: arxiv_new(since),
    }
    lines = [f"# Zodiac 新材料监测报告（{since.isoformat()} 至 {dt.date.today().isoformat()}）", ""]
    for title, func in sources.items():
        lines.append(f"## {title}")
        try:
            items = func()
        except Exception as exc:  # 单个来源失败不影响其他来源
            lines += [f"- 获取失败：{type(exc).__name__}: {exc}", ""]
            continue
        if not items:
            lines += ["- （无新条目）", ""]
            continue
        for it in items:
            if title.startswith("GitHub"):
                own = it["name"].lower() == "budongjw/zodiac-cipher-research"
                flag = "（本仓库）" if own else "" if it["name"].lower() in known else " **【未收录】**"
                lines.append(f"- {it['created']} [{it['name']}]({it['url']})（★{it['stars']}）{flag} {it['description']}")
            else:
                lines.append(f"- {it['date']} [{it['title']}]({it['url']})")
        lines.append("")
    lines.append("新的逐位读法可用 `python -m zkc score z13|z32 \"明文\"` 评分，并补入 data/claims.json。")
    report = "\n".join(lines)
    print(report)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

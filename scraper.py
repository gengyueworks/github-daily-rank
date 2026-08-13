#!/usr/bin/env python3
"""GitHub 趋势抓取器（日榜 / 周榜）。

抓取 github.com/trending 的 daily / weekly 榜单，解析仓库结构化字段，
写入 data/daily|weekly/<date>.json，并附带关键词分类，便于「吸取灵感」。

用法：
    python scraper.py            # 抓日榜 + 周榜（默认）
    python scraper.py daily      # 仅日榜
    python scraper.py weekly     # 仅周榜
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# GitHub Linguist 常用语言配色（用于卡片语言色点）
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Go": "#00ADD8", "Rust": "#dea584", "C++": "#f34b7d", "C": "#555555",
    "C#": "#178600", "Java": "#b07219", "Ruby": "#701516", "Swift": "#F05138",
    "Kotlin": "#A97BFF", "PHP": "#4F5D95", "Shell": "#89e051", "HTML": "#e34c26",
    "CSS": "#563d7c", "Vue": "#41b883", "Jupyter Notebook": "#DA5B0B",
    "Lua": "#000080", "Zig": "#ec915c", "Dart": "#00B4AB", "Scala": "#c22d40",
    "Elixir": "#6e4a7e", "OCaml": "#ef7a08", "Haskell": "#5e5086",
    "R": "#198CE7", "TeX": "#3D6117", "PowerShell": "#012456", "Makefile": "#427819",
}

# 分类关键词（描述 / 名称 / topics 命中即归类，命中多个取第一个匹配）
CATEGORY_RULES = [
    ("AI / 大模型", ["ai", "llm", "gpt", "chatgpt", "agent", "rag", "diffusion",
                    "transformer", "neural", "stable-diffusion", "openai", "anthropic",
                    "pytorch", "tensorflow", "deeplearning", "machine learning",
                    "inference", "embedding", "prompt", "chat bot", "mlops", "generative"]),
    ("开发工具", ["cli", "tool", "debugger", "ide", "editor", "formatter", "linter",
                "devtools", "developer", "sdk", "scaffold", "build", "compiler",
                "terminal", "shell", "automation"]),
    ("前端 / Web", ["react", "vue", "next.js", "svelte", "frontend", "css", "tailwind",
                   "web", "browser", "ui kit", "component", "html"]),
    ("移动端", ["android", "ios", "flutter", "react-native", "swift", "kotlin",
               "mobile", "app"]),
    ("数据 / 数据库", ["database", "sql", "postgres", "sqlite", "redis", "etl",
                     "data pipeline", "clickhouse", "duckdb", "olap", "bi"]),
    ("安全", ["security", "vulnerability", "cve", "exploit", "pentest", "malware",
             "reverse", "ctf", "encryption", "auth"]),
    ("运维 / 云", ["kubernetes", "docker", "devops", "terraform", "cloud", "serverless",
                  "monitoring", "observability", "ci/cd", "infrastructure"]),
    ("游戏", ["game", "engine", "unity", "godot", "roguelike", "pixel"]),
    ("学习资源", ["tutorial", "course", "book", "cheatsheet", "roadmap", "awesome",
                 "interview", "learn"]),
]


def classify(text: str) -> str:
    t = " " + text.lower() + " "
    for label, kws in CATEGORY_RULES:
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", t):
                return label
    return "其他"


def parse_num(s: str) -> int:
    s = s.strip().replace(",", "")
    m = re.search(r"([\d.]+)\s*([kKmM]?)", s)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "k":
        val *= 1_000
    elif unit == "m":
        val *= 1_000_000
    return int(val)


def fetch(since: str) -> list[dict]:
    url = f"https://github.com/trending?since={since}"
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for rank, art in enumerate(soup.select("article.Box-row"), 1):
        h2 = art.select_one("h2.h3.lh-condensed")
        if not h2 or not h2.a:
            continue
        href = h2.a["href"].strip("/")
        parts = href.split("/")
        if len(parts) < 2:
            continue
        owner, name = parts[0], parts[1]
        desc_el = art.select_one("p")
        desc = desc_el.get_text(" ", strip=True) if desc_el else ""
        lang_el = art.select_one('span[itemprop="programmingLanguage"]')
        lang = lang_el.get_text(strip=True) if lang_el else None
        star_el = art.select_one('a[href$="/stargazers"]')
        total_stars = parse_num(star_el.get_text(" ", strip=True)) if star_el else 0
        fork_el = art.select_one('a[href$="/forks"]')
        forks = parse_num(fork_el.get_text(" ", strip=True)) if fork_el else 0
        period_el = art.select_one("span.d-inline-block.float-sm-right")
        period_text = period_el.get_text(" ", strip=True) if period_el else ""
        period_stars = parse_num(period_text)
        topics = [a.get_text(strip=True) for a in art.select("a.topic-tag__text")] or \
                 [a.get_text(strip=True) for a in art.select('a[href*="/topics/"]')]
        blob = " ".join([name, desc] + topics).lower()
        out.append({
            "rank": rank,
            "owner": owner,
            "name": name,
            "full_name": f"{owner}/{name}",
            "url": f"https://github.com/{owner}/{name}",
            "description": desc,
            "language": lang,
            "language_color": LANG_COLORS.get(lang, "#8b949e") if lang else None,
            "stars": total_stars,
            "forks": forks,
            "period_stars": period_stars,
            "period_label": "本周" if since == "weekly" else "今日",
            "topics": topics,
            "category": classify(blob),
        })
    return out


def save(since: str, repos: list[dict]) -> Path:
    sub = DATA / ("weekly" if since == "weekly" else "daily")
    if since == "weekly":
        # 周榜按「自然周」命名：本周一日期
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        fname = f"{monday.isoformat()}.json"
    else:
        fname = f"{date.today().isoformat()}.json"
    payload = {
        "since": since,
        "date": date.today().isoformat(),
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "count": len(repos),
        "repos": repos,
    }
    path = sub / fname
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main():
    if len(sys.argv) > 1:
        modes = [sys.argv[1]]
    else:
        modes = ["daily", "weekly"]
    for since in modes:
        repos = fetch(since)
        path = save(since, repos)
        print(f"[{since}] 抓取 {len(repos)} 个仓库 -> {path}")


if __name__ == "__main__":
    main()

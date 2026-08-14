#!/usr/bin/env python3
"""把一个仓库加入「高分精选 / Curated Classics」(data/classics.json)。

用法:
    python add_classic.py owner/repo "中文点评" "英文点评" "一分钟讲解(中文)" [分类]

会自动用 gh api 拉取 stars / 简介 / topics，并追加到 data/classics.json 的 repos[]。
其余双语字段（description_zh 等）留空则沿用英文，加入后跑 build.py 重新生成。

示例:
    python add_classic.py kepano/obsidian-skills "Obsidian 创始人亲写" "founder wrote it" "一分钟讲解文案" "Agent / 笔记"
"""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
FILE = DATA / "classics.json"


def gh_api(path: str) -> dict:
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    repo = sys.argv[1]
    note_zh = sys.argv[2] if len(sys.argv) > 2 else ""
    note_en = sys.argv[3] if len(sys.argv) > 3 else ""
    script_zh = sys.argv[4] if len(sys.argv) > 4 else ""
    category = sys.argv[5] if len(sys.argv) > 5 else "其他"

    d = gh_api(f"repos/{repo}")
    obj = json.load(open(FILE, encoding="utf-8"))
    repos = obj.get("repos", [])
    if any(r["full_name"] == d["full_name"] for r in repos):
        print(f"已存在，跳过：{d['full_name']}")
        return

    entry = {
        "full_name": d["full_name"],
        "url": d["html_url"],
        "stars": d.get("stargazers_count", 0),
        "description": d.get("description") or "",
        "description_zh": "",
        "category": category,
        "note_zh": note_zh,
        "note_en": note_en,
        "added": date.today().isoformat(),
        "script_zh": script_zh,
    }
    repos.append(entry)
    obj["repos"] = repos
    obj["updated_at"] = date.today().isoformat()
    json.dump(obj, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已加入：{entry['full_name']} (★{entry['stars']:,}) · 共 {len(repos)} 条")


if __name__ == "__main__":
    main()

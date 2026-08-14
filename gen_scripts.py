#!/usr/bin/env python3
"""为每个仓库生成「一分钟逐字稿」（口播稿：是什么 / 有什么用 / 为什么好）。

- 遍历 data/daily、data/weekly、data/classics.json 的所有仓库
- 缺 script_zh 的仓库调用本机 CLIProxyAPI 网关（127.0.0.1:8317）生成
- 缓存 script_cache.json（按 full_name），已生成的不重复调用
- 生成结果写回原 JSON 的 script_zh 字段

用法：
    python3 gen_scripts.py                 # 全量补缺
    python3 gen_scripts.py --no-cache      # 忽略缓存重新生成（慎用）
"""
from __future__ import annotations

import glob
import json
import os
import sys
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
CACHE_FILE = PROJECT / "script_cache.json"

LLM_BASE_URL = os.environ.get("GHRANK_LLM_URL", "http://127.0.0.1:8317/v1/chat/completions")
LLM_API_KEY = os.environ.get("GHRANK_LLM_KEY", "sk-123")
LLM_MODEL = os.environ.get("GHRANK_LLM_MODEL", "gemini-3.5-flash-low")
TIMEOUT = 45
USE_CACHE = "--no-cache" not in sys.argv

PROMPT = """你是技术内容讲解员。为下面这个 GitHub 开源项目写一段「一分钟逐字稿」，就像短视频口播稿，用口语、有节奏、不书面腔。讲清楚三件事：
1. 这是什么（一句话点明）
2. 有什么用（怎么用、解决什么问题）
3. 为什么好（亮点、为什么值得关注）

要求：
- 全文 120-180 字，中文
- 用「这个项目」「它」指代项目，不要用「大家好」「我们」开头
- 不要出现「逐字稿」「口播稿」字样，不要用破折号和冒号排比
- 像跟朋友聊天一样一口气讲完

项目：{full_name}（{stars:,} 星）
简介：{desc}"""


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def gen(full_name: str, desc: str, stars: int) -> str | None:
    prompt = PROMPT.format(full_name=full_name, stars=stars, desc=desc or "（无简介）")
    body = json.dumps({
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.7,
    }).encode("utf-8")
    req = urllib.request.Request(LLM_BASE_URL, data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {LLM_API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.loads(r.read().decode("utf-8"))
        text = d["choices"][0]["message"]["content"].strip()
        return text or None
    except Exception as e:
        print(f"  ⚠️ 生成失败 {full_name}: {type(e).__name__}: {e}")
        return None


def main():
    cache = load_cache()
    fresh = reused = 0
    touched_files: set[Path] = set()

    # 收集所有待处理文档（保持文件对象引用，最后统一写回）
    docs = []  # (Path, payload_dict)
    files = [Path(p) for p in sorted(glob.glob(str(DATA / "daily" / "*.json")))] + \
            [Path(p) for p in sorted(glob.glob(str(DATA / "weekly" / "*.json")))] + \
            [DATA / "classics.json"]
    for f in files:
        if f.exists():
            docs.append((f, json.loads(f.read_text(encoding="utf-8"))))

    for f, payload in docs:
        repos = payload.get("repos", [])
        for r in repos:
            if r.get("script_zh"):
                continue
            fn = r["full_name"]
            if USE_CACHE and fn in cache:
                r["script_zh"] = cache[fn]
                reused += 1
                touched_files.add(f)
                continue
            script = gen(fn, r.get("description", ""), r.get("stars", 0))
            if script:
                cache[fn] = script
                r["script_zh"] = script
                fresh += 1
                touched_files.add(f)
                print(f"  ✓ {fn}: {script[:30]}…")

    for f, payload in docs:
        if f in touched_files:
            f.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    save_cache(cache)
    total = sum(len(p.get("repos", [])) for _, p in docs)
    print(f"完成：新生成 {fresh} 条，缓存复用 {reused} 条，共 {total} 个仓库。")


if __name__ == "__main__":
    main()

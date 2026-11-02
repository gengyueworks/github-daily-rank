#!/usr/bin/env python3
"""整站仓库打标签（LLM 版）——github-daily-rank 全站标签化的第一步。

做什么：
- 汇总 data/daily/*.json、data/weekly/*.json、data/classics.json 里出现过的所有仓库
- 对每个仓库，用本机 CLIProxyAPI 网关（127.0.0.1:8317）按白名单多标签打标
- 结果写回各 JSON 的 `tags` 字段（list[str]），并缓存到 tag_cache.json（full_name → tags）
- 已打过的仓库走缓存不重复调用；新增仓库自动补

白名单标签（多选，1-4 个，保持小而准）：
    视频, 英语, 教育, 中小学, 科学实验, Agent, AI工具, 大模型,
    开发工具, 前端, 设计, 移动, 数据, 安全, 游戏, 系统工具,
    文档, 阅读, 笔记, 信息源, 音视频, 图片, 写作, 运维

用法：
    python3 tag_repos.py              # 全量补缺（走缓存）
    python3 tag_repos.py --no-cache   # 忽略缓存重新打（慎用，会调 LLM 数百次）
    python3 tag_repos.py --dry-run    # 只统计，不写文件不调 LLM
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
CACHE_FILE = PROJECT / "tag_cache.json"

LLM_BASE_URL = os.environ.get("GHRANK_LLM_URL", "http://127.0.0.1:8317/v1/chat/completions")
LLM_API_KEY = os.environ.get("GHRANK_LLM_KEY", "sk-123")


def _get_default_model() -> str:
    env_model = os.environ.get("GHRANK_LLM_MODEL")
    if env_model:
        return env_model
    cfg_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            gemini_models = cfg.get("provider", {}).get("gemini", {}).get("models", {})
            if "gemini-3.8-flash-high" in gemini_models:
                return "gemini-3.8-flash-high"
            if gemini_models:
                return next(iter(gemini_models.keys()))
        except Exception:
            pass
    return "gemini-3.8-flash-high"


LLM_MODEL = _get_default_model()
TIMEOUT = 45
USE_CACHE = "--no-cache" not in sys.argv
DRY_RUN = "--dry-run" in sys.argv

WHITELIST = [
    "视频", "英语", "教育", "中小学", "科学实验", "Agent", "AI工具", "大模型",
    "开发工具", "前端", "设计", "移动", "数据", "安全", "游戏", "系统工具",
    "文档", "阅读", "笔记", "信息源", "音视频", "图片", "写作", "运维",
]
WHITELIST_SET = set(WHITELIST)

PROMPT = """你是 GitHub 仓库分类员。根据仓库的英文名和简介，从下面这个白名单里挑 1 到 4 个最贴切的标签（多选）。

白名单（只能从这里选，不许自创）：
{whitelist}

规则：
- 只看仓库实际做什么，别看星数、别看名气
- 语言学习（雅思/托福/背单词/英语口语）→ 「英语」+「教育」
- 视频生成/剪辑/字幕/视频工具 → 「视频」
- AI 智能体 / agent / skill / MCP → 「Agent」
- 英语教学课件/中小学知识图谱/错题本/实验 → 「教育」+「中小学」或「科学实验」
- 没有合适标签就返回空数组 []

仓库：{full_name}
英文简介：{description}

只返回 JSON 数组，不要任何解释。例：["教育","科学实验"]"""


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def tag_with_llm(full_name: str, desc: str) -> list[str] | None:
    prompt = PROMPT.format(whitelist="、".join(WHITELIST), full_name=full_name, description=desc or "（无简介）")
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 60,
    }
    req = urllib.request.Request(
        LLM_BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"].strip()
        # 提取第一个 JSON 数组
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return None
        arr = json.loads(text[start:end + 1])
        if not isinstance(arr, list):
            return None
        # 只保留白名单内的标签，去重保序
        tags = []
        for t in arr:
            t = str(t).strip()
            if t in WHITELIST_SET and t not in tags:
                tags.append(t)
        return tags[:4]
    except Exception:
        return None


def _iter_repo_entries():
    """yield (json_path, repo_dict) for every repo entry in daily/weekly/classics."""
    for f in sorted(glob.glob(str(DATA / "daily" / "*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("repos", []):
            yield Path(f), d, r
    for f in sorted(glob.glob(str(DATA / "weekly" / "*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("repos", []):
            yield Path(f), d, r
    cf = DATA / "classics.json"
    if cf.exists():
        d = json.loads(cf.read_text(encoding="utf-8"))
        for r in d.get("repos", []):
            yield cf, d, r


def main():
    cache = _load_cache() if USE_CACHE else {}
    # 先收集所有唯一仓库（full_name → 最新的 description）
    uniq: dict[str, str] = {}
    for _, _, r in _iter_repo_entries():
        fn = r["full_name"]
        if fn not in uniq or r.get("description"):
            uniq[fn] = r.get("description") or ""

    need = [fn for fn in uniq if fn not in cache]
    print(f"共 {len(uniq)} 个唯一仓库；缓存已有 {len(uniq) - len(need)}，待打标 {len(need)}", flush=True)
    if DRY_RUN:
        from collections import Counter
        c = Counter()
        for fn, tags in cache.items():
            for t in tags:
                c[t] += 1
        print("缓存标签分布：", dict(c.most_common()))
        return

    ok = fail = 0
    for i, fn in enumerate(need, 1):
        tags = tag_with_llm(fn, uniq[fn])
        if tags is None:
            fail += 1
            print(f"  ✗ {fn}: LLM 失败，跳过", flush=True)
        else:
            cache[fn] = tags
            ok += 1
            print(f"  ✓ [{i}/{len(need)}] {fn}: {tags}", flush=True)
        if i % 10 == 0:
            _save_cache(cache)

    _save_cache(cache)

    # 写回所有 JSON 的 tags 字段
    touched: dict[Path, dict] = {}
    for path, d, r in _iter_repo_entries():
        fn = r["full_name"]
        if fn in cache:
            r["tags"] = cache[fn]
            touched[path] = d
    for path, d in touched.items():
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"完成：新打标 {ok}，失败 {fail}，缓存共 {len(cache)}，写回 {len(touched)} 个 JSON 文件", flush=True)


if __name__ == "__main__":
    main()

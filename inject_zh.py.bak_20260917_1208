#!/usr/bin/env python3
"""把中文翻译写回 data/*.json 的 description_zh 字段。

翻译来源（两级）：
1. ZH 表（人工校对，优先）——覆盖已知仓库，质量最高。
2. 自动翻译（fallback）——新上榜仓库没有人工翻译时，调用本机
   CLIProxyAPI 网关（127.0.0.1:8317）翻译，结果同时写回 ZH 表
   并持久化到 zh_cache.json，下次直接命中、不再调 API。

用法：
    python inject_zh.py            # 只注入人工 ZH 表
    python inject_zh.py --auto     # 人工表 + 自动翻译缺失项（默认开启，见 AUTO_TRANSLATE）
"""
from __future__ import annotations

import glob
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
CACHE = PROJECT / "zh_cache.json"

# ---- 自动翻译配置（本机 CLIProxyAPI 网关，OpenAI 兼容）----
AUTO_TRANSLATE = os.environ.get("GHRANK_AUTO_TRANSLATE", "1") == "1"
LLM_BASE_URL = os.environ.get("GHRANK_LLM_URL", "http://127.0.0.1:8317/v1/chat/completions")
LLM_API_KEY = os.environ.get("GHRANK_LLM_KEY", "sk-123")
LLM_MODEL = os.environ.get("GHRANK_LLM_MODEL", "gemini-3.5-flash-low")
TRANSLATE_TIMEOUT = 30

ZH = {
    "cathrynlavery/diagram-design": "面向 Claude Code 的 29 种编辑型图表。纯 HTML + SVG，自包含。无阴影、拒绝 Mermaid 流水账。",
    "macro-inc/macro": "Macro 是面向团队的 unified 工作空间：邮件、聊天、文档、任务、智能体、通话与 CRM，通过共享 AI 记忆以 @ 链接串在一起。",
    "semantica-agi/semantica": "面向上下文与可问责 AI 系统的图原生基础设施。",
    "stablyai/orca": "Orca 是管理一整队并行智能体的 ADE（智能体开发环境）。用你自己的订阅即可运行任意编程智能体，桌面、移动端与 VPS 均可用。",
    "msitarzewski/agency-agents": "指尖上的完整 AI 代理公司——从前端巫师到 Reddit 社群高手，从灵感注入器到现实校验员。每个智能体都是带个性、有流程、交付可验证成果的专精专家。",
    "shiyu-coder/Kronos": "Kronos：读懂金融市场「语言」的基础模型。",
    "NanmiCoder/MediaCrawler": "小红书笔记/评论、抖音视频/评论、快手视频/评论、B 站视频/评论、微博帖子/评论、百度贴吧帖子/评论回复、知乎问答文章/评论 爬虫。",
    "hugohe3/ppt-master": "AI 把文档或主题变成真正原生的 PowerPoint 演示稿——原生图形、转场与动画，按需生成数据驱动的图表与表格，从演讲备注生成语音旁白，并支持你自己的 .pptx 模板。",
    "infiniflow/ragflow": "RAGFlow 是领先的开源检索增强生成（RAG）引擎，将前沿 RAG 与智能体能力融合，为 LLM 打造更优的上下文层。",
    "paperclipai/paperclip": "人人都在用的开源应用，用来在工作中管理智能体。",
    "NVIDIA-NeMo/Switchyard": "NVIDIA 出品的 LLM 流量代理与路由库：跨多家模型后端分发请求，在 OpenAI Chat、Anthropic Messages 与 OpenAI Responses 协议间互译，让 Claude Code / Codex 等编程智能体直接对接开源模型与自托管端点。",
    "ZuodaoTech/everyone-can-use-english": "人人都能用英语。",
    "smicallef/spiderfoot": "SpiderFoot 自动化 OSINT（开源情报），用于威胁情报与攻击面测绘。",
    "localsend/localsend": "开源、跨平台的 AirDrop 替代品。",
    "Lightricks/LTX-2": "LTX-2 音视频生成模型的官方 Python 推理与 LoRA 训练包。",
    "embabel/embabel-agent": "JVM 上的智能体框架。发音 Em-BAY-bel。",
    "cactus-compute/needle": "面向微型设备的 14MB 基础模型：手机、可穿戴、智能家居与机器人。",
    "cloudflare/computer": "给你的智能体一台电脑 👾",
    "TencentCloud/TencentDB-Agent-Memory": "腾讯云 Agent Memory 是面向 AI 智能体的团队级记忆中枢——把对话、文档与代码转化为四类可复用记忆资产（对话记忆、技能、LLM 知识库、代码图谱），跨智能体与框架统一治理、共享与调用。",
    "huangruiteng/loopx": "面向长时运行 AI 智能体团队的轻量循环工程状态内核。跨 Codex、Claude Code 等编程智能体无关，具备持久目标、配额感知自动唤醒、可执行待办、证据日志与可验证交接。",
    "firecrawl/pdf-inspector": "用于 PDF 检查、分类与文本提取的高速 Rust 库。智能识别扫描件与文本型 PDF，支撑智能路由决策。",
    "google/skills": "面向 Google 产品与技术的智能体技能。",
    "vitali87/code-graph-rag": "为你的 monorepo 打造的终极 RAG。借助 AI 与知识图谱，查询、理解并编辑多语言代码库。",
    "zhaoxuya520/reverse-skill": "逆向工程 / 授权渗透测试 / 安全研究技能路由包：AI 自动路由 + 按需自举工具链 + 自动进化经验库，支持 Claude Code、Kiro、Cursor、Cline 等代码 AI 客户端。",
    "esengine/DeepSeek-Reasonix": "终端里的 DeepSeek 原生 AI 编程智能体。围绕前缀缓存稳定性打造——可长期挂机运行。",
    "drawdb-io/drawdb": "免费、简单、直观的在线数据库图编辑与 SQL 生成工具。",
    "virgiliojr94/book-to-skill": "把任意技术书 PDF 变成 Claude Code 技能——开箱即学、可随时查阅与使用。",
    "Comfy-Org/ComfyUI": "最强大、模块化的扩散模型 GUI、API 与后端，采用图/节点接口。",
    "LadybirdBrowser/ladybird": "真正独立的网页浏览器。",
    "addyosmani/agent-skills": "面向 AI 编程智能体的生产级工程技能。",
    "goauthentik/authentik": "你需要的身份认证粘合剂。",
}


def _load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def translate_with_llm(full_name: str, desc: str) -> str | None:
    """调本机 CLIProxyAPI 网关翻译仓库简介，失败返回 None（不中断流程）。"""
    if not desc.strip():
        return None
    prompt = (
        "你是 GitHub 仓库中文简介翻译器。把下面的英文仓库简介翻译成简洁自然的中文，"
        "只输出译文本身，不要加引号、不要解释、不要加任何前后缀。\n\n"
        f"仓库：{full_name}\n简介：{desc}"
    )
    body = json.dumps({
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.2,
    }).encode("utf-8")
    req = urllib.request.Request(
        LLM_BASE_URL, data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TRANSLATE_TIMEOUT) as r:
            d = json.loads(r.read().decode("utf-8"))
        text = d["choices"][0]["message"]["content"].strip()
        text = text.strip('"').strip("「」").strip("『』").strip()
        return text or None
    except Exception as e:
        print(f"  ⚠️ 自动翻译失败 {full_name}: {type(e).__name__}: {e}")
        return None


def main():
    count = 0
    auto_count = 0
    cache = _load_cache()
    for f in glob.glob(str(DATA / "daily" / "*.json")) + glob.glob(str(DATA / "weekly" / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        changed = False
        for r in d["repos"]:
            zh = ZH.get(r["full_name"])
            if zh is not None:
                r["description_zh"] = zh
                count += 1
                continue
            if not AUTO_TRANSLATE:
                continue
            # 已有自动翻译缓存 → 直接复用
            cached = cache.get(r["full_name"])
            if cached:
                r["description_zh"] = cached
                auto_count += 1
                changed = True
                continue
            # 调 LLM 翻译并写缓存
            zh2 = translate_with_llm(r["full_name"], r.get("description", ""))
            if zh2:
                cache[r["full_name"]] = zh2
                r["description_zh"] = zh2
                auto_count += 1
                changed = True
                print(f"  ✓ 自动翻译 {r['full_name']} → {zh2[:40]}…")
        if changed:
            Path(f).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    _save_cache(cache)
    print(f"已写入人工中文翻译 {count} 条仓库，自动翻译 {auto_count} 条。")


if __name__ == "__main__":
    main()

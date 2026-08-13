#!/usr/bin/env python3
"""把中文翻译写回 data/*.json 的 description_zh 字段。

翻译表（人工校对，覆盖当前日/周榜全部仓库）。新仓库由每日自动化负责补译。
用法：
    python inject_zh.py
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"

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
    "NVIDIA-NeMo/Switchyard": "",
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


def main():
    count = 0
    for f in glob.glob(str(DATA / "daily" / "*.json")) + glob.glob(str(DATA / "weekly" / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d["repos"]:
            zh = ZH.get(r["full_name"])
            if zh is not None:
                r["description_zh"] = zh
                count += 1
        Path(f).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入中文翻译 {count} 条仓库。")


if __name__ == "__main__":
    main()

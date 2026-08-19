#!/usr/bin/env python3
"""翻译最新日榜 / 周榜里缺 description_zh 的仓库（不覆盖已有翻译）。

- 优先用 inject_zh.py 的 ZH 人工校对表；
- 其余用本文件 MY_ZH 里手工校对的译文；
- 已有 description_zh 的仓库一律跳过，绝不覆盖；
- 新译文同时写入 zh_cache.json，供后续同周周榜重抓复用。
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import inject_zh as iz

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
CACHE = PROJECT / "zh_cache.json"

# 本次需补译的仓库（高质量人工校对译文）
MY_ZH = {
    "cordiverse/cordis": "面向时空可组合性的元框架。",
    "cursor/plugins": "Cursor 插件规范与官方插件。",
    "unslothai/unsloth": "本地图形界面，用于运行与训练大语言模型和扩散模型，涵盖 Qwen3.8、Kimi K3、MiniMax-H3、Gemma 4、DeepSeek-V4、FLUX 等。",
    "public-apis/public-apis": "免费 API 合集清单。",
    "MakazhanAlpamys/Soup": "用一份 YAML 微调大语言模型。分层流式训练可在一张 4GB 笔记本 GPU 上训练 8B 模型。",
    "github/spec-kit": "💫 帮助你上手规格驱动开发（Spec-Driven Development）的工具集。",
    "megadose/holehe": "holehe 可检测某邮箱是否在 Twitter、Instagram 等站点被注册，并能借助「忘记密码」功能从相关站点获取信息。",
    "altic-dev/FluidVoice": "速度最快、且唯一支持端侧语音识别（STT）与自训练 AI 增强模型的 macOS 听写应用，可作为本地版 Wispr Flow 替代。X 上私信我们获取彩蛋 😉 - https://x.com/fluidvoiceapp",
    "ToolJet/ToolJet": "ToolJet 是 ToolJet AI 的开源基座——一款用于构建内部工具、仪表盘、业务应用、工作流与 AI 智能体的企业级应用生成平台 🚀",
    "HKUDS/CLI-Anything": "「CLI-Anything：让所有软件都原生适配智能体」——CLI-Hub：https://clianything.cc/",
    "citrolabs/ego-lite": "为 AI 智能体打造的最快浏览器自动化工具，可把你的已登录浏览器状态共享给 Codex、Claude Code 等智能体，且不会打扰你。零成本、零配置。",
    "PrimeIntellect-ai/prime-agent": "面向编程工作流与长时间自主任务的自我进化型 RLM 智能体。",
    "3b1b/manim": "用于制作数学讲解动画的动画引擎。",
    "basecamp/omarchy": "美观、现代且高度定制化的 Linux 发行版。",
    "OpenCut-app/OpenCut": "开源版剪映（CapCut）替代品。",
    # 2026-08-18 日榜新增
    "harry0703/MoneyPrinterTurbo": "利用 AI 大模型和自动化工作流，根据主题或关键词一键生成高清短视频。",
    "usestrix/strix": "开源 AI 渗透测试工具，用于发现并修复你应用中的安全漏洞。",
    "nautechsystems/nautilus_trader": "生产级、原生 Rust 编写的交易引擎，采用确定性事件驱动架构。",
    "akitaonrails/ai-memory": "为智能体编程命令行工具提供长期记忆的解决方案，并便于在不同智能体厂商之间交接。",
    "mukul975/Anthropic-Cybersecurity-Skills": "面向 AI 智能体的 817 项结构化网络安全技能 · 对照 6 大框架：MITRE ATT&CK、NIST CSF 2.0、MITRE ATLAS、D3FEND、NIST AI RMF 与 MITRE F3（反欺诈）· 遵循 agentskills.io 标准 · 支持 Claude Code、GitHub Copilot、Codex CLI、Cursor、Gemini CLI 等 20+ 平台 · 覆盖 29 个安全领域 · Apache 2.0 协议。",
    "AlexsJones/llmfit": "数百种模型与供应商。一条命令找出能在你硬件上运行的模型。",
    "santifer/career-ops": "开源 AI 求职工具：扫描招聘门户，用结构化的 A-F 评分标准将岗位量化为 1.0-5.0 分，定制简历、追踪投递进度——可在本地 AI 编程命令行（Claude Code、Codex、OpenCode、Antigravity 等）中运行。",
    "jundot/omlx": "面向 Apple Silicon 的大语言模型推理服务器，支持连续批处理与 SSD 缓存——可从 macOS 菜单栏管理。",
    "immich-app/immich": "高性能自托管照片与视频管理方案。",
    "agalwood/Motrix": "一款功能齐全的下载管理器。",
    # 2026-08-17 周榜新增
    "lightningpixel/modly": "桌面应用，利用本地 AI 从图片或提示词生成 3D 模型——完全在你的 GPU 上运行。",
    "anthropics/skills": "Agent Skills 的公开仓库。",
    # 2026-08-19 日榜新增
    "chaitanyagiri/munder-difflin": "本地多智能体编排框架。",
    "volcengine/OpenViking": "面向 AI 智能体的自进化上下文数据库，统一智能体记忆、知识 RAG 与技能。",
    "NawfalMotii79/PLFM_RADAR": "开源、低成本的 10.5 GHz PLFM 相控阵雷达系统。",
    "bojieli/ai-agent-book": "《深入理解 AI Agent：设计原理与工程实践》（李博杰 著）开源主仓库：全书正文、编译版 PDF 与按章配套代码。",
    # 2026-08-19 周榜新增
    "superradcompany/microsandbox": "🧱 轻量、快速的本地优先 microVM 运行时与开发库。",
}


def latest(sub: str) -> str | None:
    files = sorted(glob.glob(str(DATA / sub / "*.json")))
    return files[-1] if files else None


def main():
    cache = iz._load_cache()
    total = 0
    for sub in ("daily", "weekly"):
        path = latest(sub)
        if not path:
            print(f"[{sub}] 无数据文件，跳过")
            continue
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        changed = False
        for r in d["repos"]:
            if r.get("description_zh"):
                continue  # 已有翻译，绝不覆盖
            zh = MY_ZH.get(r["full_name"]) or iz.ZH.get(r["full_name"])
            if zh:
                r["description_zh"] = zh
                cache[r["full_name"]] = zh  # 持久化，避免同周重抓丢失
                total += 1
                changed = True
        if changed:
            Path(path).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        missing = [r["full_name"] for r in d["repos"]
                   if not r.get("description_zh") and r.get("description")]
        print(f"[{sub}] {Path(path).name}：补译 {total} 条；仍缺译（无英文简介或待补）：{missing or '无'}")
    iz._save_cache(cache)


if __name__ == "__main__":
    main()

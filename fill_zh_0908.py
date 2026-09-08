#!/usr/bin/env python3
"""为 2026-09-08 日榜与 2026-09-07 周榜补齐 description_zh（仅补缺失项，不覆盖）。"""
from __future__ import annotations
import json
from pathlib import Path

PROJECT = Path("/Users/a0302/WorkBuddy/github-daily-rank")
DATA = PROJECT / "data"

ZH = {
    # ---- 日榜 2026-09-08 ----
    "heygen-com/hyperframes": "用 HTML 写，渲染成视频。为智能体而生。",
    "microsoft/markitdown": "将各类文件与办公文档转换为 Markdown 的 Python 工具。",
    "mksglu/context-mode": "面向 AI 编程智能体的上下文窗口优化。沙箱化工具输出（减少 98%），持久化会话记忆，并通过 MCP + hooks 在 17 个平台间强制路由。",
    "jo-inc/camofox-browser": "为 AI 智能体打造的隐形无头浏览器——可绕过 Cloudflare、机器人检测与反爬机制。可无缝替换 Puppeteer / Playwright。",
    "coreyhaines31/marketingskills": "面向 Claude Code 与 AI 智能体的营销技能集。涵盖转化率优化、文案写作、SEO、数据分析与增长工程。",
    "The-Swarm-Corporation/AutoHedge": "几分钟构建属于你的自动化对冲基金。AutoHedge 借助群体智能与 AI 智能体，自动化完成市场分析、风险管理与交易执行。",
    "BraveOPotato/FckSignups": "一份开源、浏览器内运行、且无需注册登录的工具清单！",
    "bytedance/deer-flow": "开源的长周期 SuperAgent 框架，能自主研究、写代码与创作。借助沙箱、记忆、工具、技能、子智能体与消息网关，可处理从几分钟到数小时的不同量级任务。",
    "openai/skills": "面向 Codex 的技能目录（Skills Catalog）。",
    "lightpanda-io/browser": "Lightpanda：专为 AI 与自动化设计的无头浏览器。",
    "pascalorg/editor": "创建并分享 3D 建筑项目。",
    # ---- 周榜 2026-09-07 ----
    "magnitudedev/magnitude": "开源推理服务器，为你的硬件运行最优质的本地模型，并接入你正在使用的智能体。兼容 Pi、OpenCode、Hermes、OpenClaw、Codex、Claude Code、Oh My Pi 与 Cline。",
    "tt-a1i/archify": "智能体技能：生成美观且可验证的架构图、流程图、时序图、数据流图与生命周期图——自包含 HTML，带动效且可高清导出。",
    "Gitlawb/openclaude": "可在任何环境运行，调用任意工具。",
    "THU-MAIC/OpenMAIC": "开放的多智能体互动课堂——一键获得沉浸式的多智能体学习体验。",
    "google-research/timesfm": "TimesFM（时间序列基础模型）是 Google Research 开发的预训练时序基础模型，用于时间序列预测。",
    "jingyaogong/minimind": "🧠 仅需 2 小时，从零训练一个 6400 万参数的大语言模型！",
    "pollen-robotics/microduck_rl": "面向 Microduck（mjlab）的强化学习训练环境。",
    "debpalash/VoiceStudio": "VoiceStudio 是开源、完全本地运行的 ElevenLabs 替代品——支持语音克隆、声音设计、视频配音、听写、转写与 646 种语言的有声书制作。",
    "fmtlib/fmt": "一个现代化的格式化库。",
    "DietrichGebert/ponytail": "让你的 AI 智能体像屋里最懒的高级工程师那样思考。最好的代码，是你从未写过的代码。",
    "zubair-trabzada/geo-seo-claude": "面向 Claude Code 的 GEO 优先 SEO 技能。为任意网站提供全面的 AI 搜索优化——可引用度评分、AI 爬虫分析、品牌权威、结构化标记、平台针对性优化与 PDF 报告。",
    "advaitpaliwal/feynman": "开源的 AI 科研智能体。",
    "Imbad0202/academic-research-skills": "面向 Claude Code 的学术研究技能：研究 → 撰写 → 评审 → 修订 → 定稿。",
    "colinhacks/zod": "以 TypeScript 优先的 schema 校验，支持静态类型推断。",
    "roboflow/rf-detr": "RF-DETR 是 Roboflow 开发的实时目标检测与分割模型架构，在 COCO 数据集上达到 SOTA，专为微调设计。[ICLR 2026]",
    "every-app/open-seo": "Semrush 与 Ahrefs 的开源替代品。",
    "tailscale/tailcat": "类似 netcat，但运行在 Tailscale 数据平面之上，且不依赖 Tailscale 控制平面。",
}

for sub, fname in (("daily", "2026-09-08.json"), ("weekly", "2026-09-07.json")):
    path = DATA / sub / fname
    d = json.loads(path.read_text(encoding="utf-8"))
    filled = 0
    for r in d["repos"]:
        if r.get("description_zh"):
            continue
        zh = ZH.get(r["full_name"])
        if zh is None:
            # 描述本身已是中文（含许可证说明等），直接沿用
            if r.get("description") and any('\u4e00' <= c <= '\u9fff' for c in r.get("description", "")):
                zh = r["description"]
            else:
                print(f"  [跳过] {r['full_name']}：无译文且非中文描述")
                continue
        r["description_zh"] = zh
        filled += 1
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    still = [r["full_name"] for r in d["repos"] if not r.get("description_zh")]
    print(f"[{sub}] {fname}：补充 {filled} 条；仍缺译：{still or '无'}")

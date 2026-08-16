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

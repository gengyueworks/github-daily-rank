#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 日榜 · 每日精选资料自动生成
每天 launchd 跑完主链路后调用：
  读当日榜单 data/daily/YYYY-MM-DD.json → 按规则选 3-5 个高影响力项目
  → 生成「今日精选资料」md（编辑腔：定位/亮点/值得说）→ 追加进资料库 md

用法: python3 gen_material.py [YYYY-MM-DD]   (缺省=最新一天)
产出: xhs-assets/GitHub经典项目资料库-YYYY-MM-DD.md (当日独立)
      xhs-assets/每日资料.md (滚动追加，去重)
"""
import json, os, sys, glob, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "daily")
OUT_MATERIAL = os.path.join(BASE, "xhs-assets", "GitHub经典项目资料库-{date}.md")
OUT_ROLLING = os.path.join(BASE, "xhs-assets", "每日资料.md")

def latest_date():
    fs = sorted(glob.glob(os.path.join(DATA, "*.json")))
    return os.path.basename(fs[-1]).replace(".json", "")

def pick_projects(repos):
    """选题规则：涨星最高必选 + 工具优先 + 品类不重复 + 数据存疑不选"""
    repos = [r for r in repos if r.get("description_zh") or r.get("description")]
    if not repos:
        return []
    repos.sort(key=lambda r: -r.get("period_stars", 0))
    picked = []
    used_cat = set()
    # 涨星第一必选
    top = repos[0]
    picked.append(top); used_cat.add(top.get("category", "其他"))
    # 按星数从高到低补到 5 个，品类尽量不重复
    for r in sorted(repos, key=lambda r: -r.get("stars", 0)):
        if len(picked) >= 5:
            break
        cat = r.get("category", "其他")
        if r["full_name"] == top["full_name"]:
            continue
        if cat in used_cat:
            continue
        picked.append(r); used_cat.add(cat)
    # 仍不足 5 个，补品类重复的（按星数）
    if len(picked) < 5:
        for r in sorted(repos, key=lambda r: -r.get("stars", 0)):
            if len(picked) >= 5:
                break
            if all(r["full_name"] != p["full_name"] for p in picked):
                picked.append(r)
    return picked

def one_project(r):
    """单项目资料行（编辑腔）"""
    fn = r["full_name"]
    stars = f"{r.get('stars', 0):,}"
    lang = r.get("language") or "—"
    desc = (r.get("description_zh") or r.get("description") or "").strip()
    cat = r.get("category", "其他")
    gain = r.get("period_stars", 0)
    # 亮点 = 人工编辑点评优先（编辑腔铁律：观察句不给吆喝）；缺失用定位描述兜底
    hl = HL_MANUAL.get(fn) or (desc[:50] if desc else "见仓库 README")
    return {
        "full_name": fn, "stars": stars, "lang": lang, "cat": cat,
        "desc": desc, "hl": hl, "gain": gain,
    }

# 人工编辑点评表（编辑腔）。新增项目在此追加，缺失时自动用定位描述兜底。
HL_MANUAL = {
    "cathrynlavery/diagram-design": "它解决的是一类很具体的审美问题：AI 图表不该有廉价阴影和流水账线条。",
    "github/spec-kit": "规范先行、代码文档永远同步，返工率下来，星数就上去了。",
    "infiniflow/ragflow": "RAG 的难点在「找得准」，它把检索和智能体工作流捏在一起解决。",
    "rustdesk/rustdesk": "十二万星换来的，是远程控制不再受制于人。",
    "OpenCut-app/OpenCut": "本地运行的免费剪辑，自动字幕和转场都不缺。",
    "cactus-compute/needle": "14MB 的模型装进手表，端侧 AI 的门槛被它打下来。",
    "megadose/holehe": "查别人的是工具，查自己的是警钟。",
    "macro-inc/macro": "协作工具的碎片，被共享记忆收拢了。",
    "smicallef/spiderfoot": "上百个数据源自动跑完的 OSINT，省的是手动搜集的时间。",
    "citrolabs/ego-lite": "登录态共享这一步，是 AI 自动化最头疼的一环。",
    "holaboss-ai/holaOS": "一百多种工具接入同一个智能体工作台，记忆还共享。",
    "lightningpixel/modly": "本地 GPU 跑 3D 生成，图片变模型不用上云。",
    "semantica-agi/semantica": "知识图谱让 AI 记住前因后果，回答有据可查。",
    "rustdesk/rustdesk": "远程控制不再受制于人，数据自己握着。",
    "unslothai/unsloth": "本地跑大模型的门槛，被显存优化砍下来了。",
    "ToolJet/ToolJet": "内部系统的活，交给拖拽就行。",
    "stablyai/orca": "多智能体协作的调度，一个界面搞定。",
    "paperclipai/paperclip": "AI 多了之后，缺的是管理它们的界面。",
    "anthropics/skills": "官方带头做开源，智能体技能的行业标准。",
    "msitarzewski/agency-agents": "一个人的公司，员工全是 AI。",
    "kepano/obsidian-skills": "笔记库配上 AI，整理这步自动省掉。",
    "ZuodaoTech/everyone-can-use-english": "它解决的不是词汇量，是不敢用。",
    "localsend/localsend": "AirDrop 的围墙，被它拆掉了。",
    "3b1b/manim": "科普视频的天花板，原来是开源引擎。",
    "Panniantong/Agent-Reach": "AI 从只会答，到会自己去看。",
    "DeusData/codebase-memory-mcp": "AI 改代码，不用每次重新理解项目。",
    "microsoft/markitdown": "喂给 AI 之前，所有文档先过它。",
}

def render(projects, date):
    lines = [f"# GitHub 经典项目资料 · {date}", "",
             "> 用途：小红书「GitHub 日榜」栏目素材源，Notion 作图部门按此资料统一制作图文。",
             f"> 数据源：当日榜单快照（data/daily/{date}.json），星数为抓取时点值。", ""]
    for i, p in enumerate(projects, 1):
        lines += [
            f"### {i}. {p['full_name']} ★{p['stars']} · {p['lang']} · {p['cat']}",
            f"- **定位**：{p['desc'][:60]}",
            f"- **亮点**：{p['hl']}",
            f"- **数据**：今日 +{p['gain']:,} ★",
            "",
        ]
    lines += ["---", "发布建议：每组 3-5 个、品类不重复；数据行以发布当日榜单为准；文案走编辑腔（数据进数据行、感叹号 ≤1、判断句给观察）。", ""]
    return "\n".join(lines)

def main():
    date = sys.argv[1] if len(sys.argv) > 1 else latest_date()
    f = os.path.join(DATA, f"{date}.json")
    if not os.path.exists(f):
        print(f"❌ 无 {date} 榜单"); sys.exit(1)
    repos = json.load(open(f))["repos"]
    picked = [one_project(r) for r in pick_projects(repos)]
    md = render(picked, date)
    out = OUT_MATERIAL.format(date=date)
    with open(out, "w") as fh:
        fh.write(md)
    print(f"✓ 当日资料: {out} ({len(picked)} 个项目)")
    # 滚动追加（去重）
    rolling = []
    if os.path.exists(OUT_ROLLING):
        rolling = open(OUT_ROLLING).read().split("<!--SPLIT-->")
    seen = set()
    for block in rolling:
        for line in block.splitlines():
            if line.startswith("### "):
                seen.add(line.split(" ", 2)[2].split("★")[0].strip())
    blocks = [b for b in rolling if b.strip()]
    new_block = render(picked, date) + "\n<!--SPLIT-->\n"
    if not any(f"### 1. {p['full_name']}" in b for p in picked for b in blocks):
        blocks.insert(0, new_block)
    with open(OUT_ROLLING, "w") as fh:
        fh.write("\n".join(blocks))
    print(f"✓ 滚动资料: {OUT_ROLLING}")

if __name__ == "__main__":
    main()

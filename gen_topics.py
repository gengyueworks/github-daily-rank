#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 经典项目 · 30 期选题批量生成
输入: 本地榜单(45) + API 候选(136) = 180+ 项目池
输出: 30 期 × 3 项目 选题清单 md + zip（给 Notion 作图）
规则: 品类尽量不重复; 星数优先; 每期 3 个
"""
import json, os, re, glob, subprocess, datetime

BASE = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank"
OUT = os.path.join(BASE, "xhs-assets", "选题")

# ============ 1. 收集候选池 ============
pool = {}  # full_name -> {full_name, stars, lang, desc, desc_zh, gain, cat}

# 本地榜单
for f in sorted(glob.glob(os.path.join(BASE, "data", "daily", "*.json"))):
    for r in json.load(open(f))["repos"]:
        fn = r["full_name"]
        if fn not in pool or r["stars"] > pool[fn]["stars"]:
            pool[fn] = {"full_name": fn, "stars": r["stars"], "lang": r.get("language") or "—",
                        "desc": r.get("description_zh") or r.get("description") or "",
                        "gain": r.get("period_stars", 0), "cat": r.get("category", "其他")}

# 6-8 月资料库
db = open(os.path.join(BASE, "xhs-assets", "GitHub经典项目资料库-2026-06至08.md")).read()
for m in re.finditer(r'### \d+\. (\S+) ★([\d,]+) · (\S+)\n- \*\*定位\*\*：(\S[^\n]*)', db):
    fn, stars, lang, desc = m.group(1), int(m.group(2).replace(",","")), m.group(3), m.group(4)
    if fn not in pool:
        pool[fn] = {"full_name": fn, "stars": stars, "lang": lang, "desc": desc, "gain": 0, "cat": "其他"}

# API 候选
api = json.load(open("/tmp/gh_pool.json"))
for r in api:
    fn = r["full_name"]
    if fn not in pool:
        pool[fn] = {"full_name": fn, "stars": r.get("stargazers_count", 0), "lang": r.get("language") or "—",
                    "desc": r.get("description") or "", "gain": 0, "cat": "其他"}

print(f"候选池总计: {len(pool)} 个")

# ============ 2. 品类粗分（按关键词） ============
def classify(fn, desc, lang):
    d = (fn + " " + desc).lower()
    if any(k in d for k in ["claude", "agent", "skill", "codex", "harness", "mcp", "openclaw", "superpowers", "coding agent"]):
        return "AI 智能体"
    if any(k in d for k in ["llm", "model", "rag", "fine-tun", "deepseek", "grok", "qwen", "kimi", "diffusion", "training"]):
        return "AI 模型"
    if any(k in d for k in ["design", "ui", "css", "frontend", "web", "svg", "图表", "design"]):
        return "设计/前端"
    if any(k in d for k in ["remote", "传输", "file", "sync", "share", "clipboard", "局域网"]):
        return "效率工具"
    if any(k in d for k in ["document", "pdf", "md", "markdown", "convert", "ocr", "word", "ppt", "excel"]):
        return "文档工具"
    if any(k in d for k in ["security", "privacy", "osint", "email", "密码", "安全", "泄露"]):
        return "安全/隐私"
    if any(k in d for k in ["video", "audio", "音乐", "剪辑", "动画", "manim", "image", "3d", "photo"]):
        return "媒体创作"
    if any(k in d for k in ["github", "git", "tool", "cli", "terminal", "命令行", "数据库", "server", "open source", "开源"]):
        return "开发工具"
    if any(k in d for k in ["english", "英语", "learn", "学习", "obsidian", "note", "笔记"]):
        return "学习/笔记"
    return "其他"

for fn in pool:
    pool[fn]["cat"] = classify(fn, pool[fn]["desc"], pool[fn]["lang"])

# ============ 3. 分组 30 期 × 3 ============
# 排序: 星数降序
cands = sorted(pool.values(), key=lambda r: -r["stars"])
# 打散品类: 每期尽量不同品类
groups = []
used_fn = set()
cats = {}
for r in cands:
    cats.setdefault(r["cat"], []).append(r)

# 轮转取品类的组合: 每次取 3 个不同品类
cat_names = list(cats.keys())
cat_idx = {c: 0 for c in cat_names}
while len(used_fn) < 90:
    # 取一轮不同品类（最多 3 个不同品类）
    round_pick = []
    for c in cat_names:
        while cat_idx[c] < len(cats[c]) and cats[c][cat_idx[c]]["full_name"] in used_fn:
            cat_idx[c] += 1
        if cat_idx[c] < len(cats[c]):
            round_pick.append(cats[c][cat_idx[c]])
            cat_idx[c] += 1
        if len(round_pick) >= 3:
            break
    if not round_pick:
        break
    group = []
    for r in round_pick[:3]:
        used_fn.add(r["full_name"])
        group.append(r)
    if len(group) == 3:
        groups.append(group)
    if len(groups) >= 30:
        break

print(f"生成 {len(groups)} 期, 用掉 {len(used_fn)} 个项目")

# ============ 4. 渲染清单 md ============
lines = ["# GitHub 经典项目选题 · 30 期（每期 3 个项目）", "",
         "> 给 Notion 作图部门：每期 = 1 封面 + 3 项目卡 + 文案。素材即选即做。",
         f"> 生成日期: {datetime.date.today()} · 候选池 {len(pool)} 个", ""]
for gi, g in enumerate(groups, 1):
    lines.append(f"## 第 {gi} 期")
    for r in g:
        lines += [
            f"- **{r['full_name']}** ★{r['stars']:,} · {r['lang']} · {r['cat']}",
            f"  - 定位: {r['desc'][:60]}",
            f"  - 数据: ★{r['stars']:,}（今日 +{r['gain']:,} 榜单时点值）",
            "",
        ]
    lines.append("---")
    lines.append("")
open(os.path.join(OUT, "30期选题清单.md"), "w").write("\n".join(lines))
print("✓ 清单: xhs-assets/选题/30期选题清单.md")

# ============ 5. 打包 zip ============
import zipfile
zout = os.path.join(BASE, "..", "GitHub经典项目选题-30期-2026-08-16.zip")
if os.path.exists(zout): os.remove(zout)
with zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(OUT, "30期选题清单.md"), "30期选题清单.md")
print("✓ zip:", zout)

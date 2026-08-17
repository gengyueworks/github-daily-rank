#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30 期选题清单 · 中文版生成（重写，稳健解析）
按 --- 分块 → 每块内用「- **fn** ★n」模式提取项目行（封面标题/判断句不含★，天然区分）
"""
import json, os, re, urllib.request, datetime

BASE = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank"
OUT = os.path.join(BASE, "xhs-assets", "选题")
SRC = os.path.join(OUT, "30期选题清单.md")

# 人工中文表（编辑腔）
ZH_MANUAL = {
    "openclaw/openclaw": "开源的个人 AI 助手，任何系统任何平台都能跑",
    "obra/superpowers": "智能体技能框架 + 软件开发方法论",
    "microsoft/markitdown": "微软出品：PDF/Word/PPT/Excel/音视频一键转干净的 Markdown",
    "NousResearch/hermes-agent": "会跟着你成长的智能体",
    "affaan-m/ECC": "智能体性能优化系统，技能/注入/工作流一站式管理",
    "mattpocock/skills": "真实工程师的 Claude Skills，来自一线实践",
    "multica-ai/andrej-karpathy-skills": "一份 CLAUDE.md 就能提升 Claude Code 表现的技能包",
    "anomalyco/opencode": "开源编程智能体",
    "anthropics/claude-code": "Claude 官方终端编程智能体",
    "google-gemini/gemini-cli": "谷歌开源的终端 AI 智能体",
    "openai/codex": "OpenAI 官方的轻量终端编程智能体",
    "karpathy/autoresearch": "Karpathy 出品：AI 智能体在单 GPU 上跑研究",
    "addyosmani/agent-skills": "生产级工程技能包，给 AI 编程用",
    "rtk-ai/rtk": "CLI 代理，把 LLM token 消耗降 60%",
    "datawhalechina/hello-agents": "《从零开始构建智能体》中文教程",
    "ComposioHQ/awesome-claude-skills": "精选 Claude Skills 资源合集",
    "colbymchenry/codegraph": "预索引代码知识图谱，自动同步",
    "headroomlabs-ai/headroom": "压缩工具输出/日志/文件，省 token",
    "Fission-AI/OpenSpec": "面向 AI 编程助手的规范驱动开发",
    "koala73/worldmonitor": "实时全球情报面板，AI 新闻聚合",
    "odysseus-dev/odysseus": "自托管的 AI 工作空间",
    "tobi/qmd": "文档/知识库/会议纪要的迷你命令行搜索引擎",
    "opendataloader-project/opendataloader-pdf": "PDF 文档解析库，喂给 AI 之前先过它",
    "shadcn/improve": "用最强模型审计你的代码库并写改进建议",
    "cloudflare/computer": "给智能体一台电脑",
    "deepseek-ai/DeepSeek-R1": "DeepSeek 推理模型，开源震撼全球",
    "bytedance/deer-flow": "字节开源的超长任务智能体框架",
    "Egonex-AI/Understand-Anything": "把任何东西变成知识图谱",
    "Leonxlnx/taste-skill": "给 AI 装上审美品味，告别塑料感界面",
    "shareAI-lab/learn-claude-code": "极简 Claude Code 教学",
    "666ghj/MiroFish": "通用群智能引擎",
    "ruvnet/ruflo": "智能体元框架，部署智能体工作流",
    "code-yeongyu/oh-my-openagent": "为 token 极限优化的编程智能体",
    "garrytan/gstack": "Garry Tan 的 Claude Code 配置：23 条工程观点",
    "farion1231/cc-switch": "跨平台桌面端 AI 全能助手",
    "nextlevelbuilder/ui-ux-pro-max-skill": "给 AI 的设计智能技能包",
    "VoltAgent/awesome-design-md": "热门项目 DESIGN.md 分析合集",
    "Graphify-Labs/graphify": "把代码库+文档+SQL 变成可查询图谱",
    "JuliusBrussee/caveman": "最少的 token 做最多的事",
    "earendil-works/pi": "AI 智能体工具包：统一 LLM API + 智能体循环",
    "thedotmack/claude-mem": "跨会话持久记忆",
    "ruvnet/RuView": "把 WiFi 信号变成实时感知的 AI 工具",
    "nexu-io/open-design": "DeepSeek 生态的设计插件",
    "x1xhlol/system-prompts-and-models-of-ai-tools": "各大 AI 工具的系统提示词合集",
    "ultraworkers/claw-code": "Rust 写的智能体托管项目",
    "Lightricks/LTX-2": "视频生成模型",
}

def translate(desc, fn):
    if fn in ZH_MANUAL:
        return ZH_MANUAL[fn]
    body = json.dumps({"model": "gemini-3-flash", "messages": [
        {"role": "system", "content": "把下面这条 GitHub 项目英文描述翻译成一句自然的中文（≤40字），不要引号和解释。"},
        {"role": "user", "content": desc}
    ]}).encode()
    try:
        req = urllib.request.Request("http://127.0.0.1:8317/v1/chat/completions", body,
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer sk-123"})
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return desc[:40] + "…"

def parse_periods(src):
    """按 --- 分隔成期块，每块提取项目"""
    raw = open(src).read()
    # 切出每期（## 第 N 期 到下一个 --- 或文件尾）
    chunks = re.split(r'^## 第 (\d+) 期$', raw, flags=re.M)
    periods = []
    for i in range(1, len(chunks), 2):
        num = chunks[i]
        body = chunks[i+1]
        # 项目行: - **fn** ★n · lang · cat\n  - 定位: xxx\n  - 数据: xxx
        projs = []
        for m in re.finditer(r'- \*\*([^\*]+?)\*\* ★([\d,]+) · ([^\n]+)', body):
            fn, stars, lang = m.group(1).strip(), m.group(2), m.group(3).strip()
            # 找该块后面跟随的定位行
            rest = body[m.end():]
            dm = re.search(r'定位:\s*([^\n]+)', rest[:200])
            desc = dm.group(1).strip() if dm else ""
            projs.append({"fn": fn, "stars": stars, "lang": lang, "desc": desc})
        if projs:
            periods.append((num, projs))
    return periods

def main():
    cache_path = os.path.join(OUT, "zh_translate_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path))

    periods = parse_periods(SRC)
    print(f"解析到 {len(periods)} 期")
    for num, projs in periods[:3]:
        print(f"  第{num}期: {len(projs)} 个项目: {[p['fn'] for p in projs]}")

    # 翻译缺失的
    todo = [(p["fn"], p["desc"]) for _, projs in periods for p in projs if p["fn"] not in cache and not re.search(r'[\u4e00-\u9fff]', p["desc"])]
    print(f"待翻译: {len(todo)} 条")
    if todo:
        import concurrent.futures as cf
        def do(item):
            fn, desc = item
            return fn, translate(desc, fn)
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for fn, zh in ex.map(do, todo):
                cache[fn] = zh
        json.dump(cache, open(cache_path, "w"), ensure_ascii=False)

    # 渲染
    lines = ["# GitHub 经典项目选题 · 30 期（中文版，可直接作图）", "",
             "> 每期 = 1 封面 + 3 项目卡 + 文案。封面标题/判断句已配好，Notion 直接照做。",
             f"> 生成日期: {datetime.date.today()}", ""]
    for num, projs in periods:
        lines.append(f"## 第 {num} 期")
        for p in projs:
            zh = cache.get(p["fn"]) or p["desc"]
            lines.append(f"- **{p['fn']}** ★{p['stars']} · {p['lang']}")
            lines.append(f"  - 定位: {zh}")
        first = projs[0]["fn"].split("/")[-1]
        lines.append(f"  - **封面标题**: 今天值得看的三个开源项目：{first} 领衔")
        lines.append(f"  - **判断句**: 第 {num} 期 · 好工具帮人省去重复造轮子的时间")
        lines.append("")
        lines.append("---")
        lines.append("")
    out_md = os.path.join(OUT, "30期选题清单-中文版.md")
    open(out_md, "w").write("\n".join(lines))
    print("✓ 中文版:", out_md)

    import zipfile
    zout = os.path.join(BASE, "..", "GitHub经典项目选题-30期-中文版-2026-08-16.zip")
    if os.path.exists(zout): os.remove(zout)
    with zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out_md, "30期选题清单-中文版.md")
    print("✓ zip:", zout)

if __name__ == "__main__":
    main()

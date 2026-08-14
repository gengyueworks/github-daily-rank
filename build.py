#!/usr/bin/env python3
"""日报 / 周报生成器（ainews 视觉风格 · 中英文双语）。

视觉 1:1 对齐 ainews 系列：克莱因蓝 #002FA7、Inter/Noto Sans SC/JetBrains Mono、
720px 容器、section-header 蓝色下划线、news-item/news-body/card-tag/source-line 结构。
内容中英文双语；不含小红书板块。

用法：
    python build.py
"""
from __future__ import annotations

import glob
import html
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
DATA = PROJECT / "data"
SITE = PROJECT / "site"

# ---- ainews 视觉规范（与原系列一致） ----
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --klein: #002FA7;
    --klein-bright: #0044FF;
    --white: #FFFFFF;
    --bg-light: #F8F9FB;
    --text-dark: #1A1A1A;
    --text-mid: #6B6B6B;
    --text-light: #9CA3AF;
    --border: #E5E7EB;
    --accent: #C41E3A;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Noto Sans SC', 'Inter', -apple-system, sans-serif;
    background: var(--white); color: var(--text-dark);
    line-height: 1.75; -webkit-font-smoothing: antialiased;
}
.container { max-width: 720px; margin: 0 auto; padding: 56px 28px 80px; }
.doc-title { font-size: 38px; font-weight: 700; color: var(--text-dark); letter-spacing: -0.5px; margin-bottom: 8px; text-wrap: balance; }
.doc-title span { color: var(--klein); }
.doc-date { font-family: 'Inter', sans-serif; font-size: 15px; color: var(--text-light); }
.divider { height: 1px; background: var(--border); margin: 36px 0; }
.section-header { font-size: 24px; font-weight: 600; color: var(--klein); margin-bottom: 24px; padding-bottom: 8px; border-bottom: 2px solid var(--klein); display: inline-block; text-wrap: balance; }
.section-header .en { font-family: 'Inter'; font-size: 13px; color: var(--text-light); font-weight: 400; margin-left: 10px; }
.section-block { margin-bottom: 48px; }
.news-item { margin-bottom: 52px; }
.news-item:last-child { margin-bottom: 0; }
.news-title { font-size: 21px; font-weight: 600; color: var(--text-dark); line-height: 1.5; margin-bottom: 14px; text-wrap: balance; }
.news-body { font-size: 16px; color: var(--text-dark); line-height: 1.9; margin-bottom: 16px; }
.news-label { font-size: 14px; color: var(--text-mid); line-height: 1.7; margin-bottom: 14px; }
.highlight { color: var(--klein); font-weight: 600; }
.accent { color: var(--accent); font-weight: 600; }
.turn { color: var(--klein); font-weight: 700; }
.intro-text { font-size: 16px; color: var(--text-dark); line-height: 1.9; margin-bottom: 14px; }
.source-line { font-size: 13px; color: var(--text-light); margin-top: 8px; }
.source-line a { color: var(--klein); text-decoration: none; }
.footer-block { font-size: 14px; color: var(--text-mid); line-height: 1.7; margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border); }
.card-tag { font-size: 12px; color: var(--text-mid); opacity: 0.55; margin-top: 8px; line-height: 1.6; }

.site-nav-lite { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.nav-back { font-size: 14px; color: var(--klein); text-decoration: none; font-weight: 500; }
.nav-back:hover { text-decoration: underline; }
.nav-date { font-size: 13px; color: var(--text-light); font-family: 'JetBrains Mono', monospace; }

/* ---- GitHub 榜专属（仍沿用 ainews 用词体系） ---- */
.rank { font-family: 'JetBrains Mono', monospace; color: var(--klein); font-weight: 700; margin-right: 8px; }
.repo-link { color: var(--text-dark); text-decoration: none; }
.repo-link:hover { color: var(--klein); }
.zh { color: var(--text-mid); }
.tr { font-size: 11px; color: #fff; background: var(--klein); border-radius: 4px; padding: 2px 6px; margin-right: 6px; font-family: 'Inter'; vertical-align: middle; }
.repo-meta { font-size: 14px; color: var(--text-mid); margin-top: 12px; line-height: 1.8; }
.repo-meta .lang-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin: 0 4px 0 2px; }
.repo-meta .cat { color: var(--klein); font-weight: 600; }
.riser-note { font-size: 13px; color: var(--text-light); margin-top: 8px; }
.script-block { font-size: 15px; color: var(--text-dark); line-height: 1.8; background: #EEF2FF; border-left: 3px solid var(--klein); border-radius: 8px; padding: 14px 18px; margin: 16px 0; }
.script-tag { font-size: 11px; color: #fff; background: var(--klein); border-radius: 4px; padding: 2px 7px; margin-right: 8px; font-family: 'Inter'; vertical-align: middle; white-space: nowrap; }
.script-text { color: var(--text-dark); }
.archive { columns: 2; column-gap: 24px; }
.archive a { display: block; color: var(--klein); text-decoration: none; padding: 3px 0; font-size: 15px; }
.archive a:hover { text-decoration: underline; }

/* classics 高分精选页专属：阅读型页面加宽容器，提升行宽舒适度 */
body.classics .container { max-width: 860px; }
"""

CAT_EN = {
    "AI / 大模型": "AI / LLM", "开发工具": "Dev Tools", "前端 / Web": "Frontend / Web",
    "移动端": "Mobile", "数据 / 数据库": "Data / DB", "安全": "Security",
    "运维 / 云": "Ops / Cloud", "游戏": "Game", "学习资源": "Learning", "其他": "Misc",
}


def esc(s):
    return html.escape(str(s or ""))


def bcat(cat):
    return f"{cat} · {CAT_EN.get(cat, cat)}"


def load_latest(sub):
    files = sorted(glob.glob(str(DATA / sub / "*.json")))
    return json.load(open(files[-1], encoding="utf-8")) if files else None


def load_week_dailies():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    out, d = [], monday
    while d <= today:
        f = DATA / "daily" / f"{d.isoformat()}.json"
        if f.exists():
            out.append(json.load(open(f, encoding="utf-8")))
        d += timedelta(days=1)
    return out


def weekday_cn(dt: date) -> str:
    return ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][dt.weekday()]


def script_block(r):
    """一分钟口播稿渲染片段（中文，120-180 字）。无 script_zh 字段时返回空串，兼容旧数据。"""
    s = r.get("script_zh")
    if not s:
        return ""
    return (f'<div class="script-block"><span class="script-tag">一分钟讲解 1-min</span>'
            f'<span class="script-text">{esc(s)}</span></div>')


def repo_item(r, show_riser=False):
    rank = f'<span class="rank">#{r["rank"]}</span>'
    link = f'<a class="repo-link" href="{esc(r["url"])}" target="_blank">{esc(r["full_name"])}</a>'
    en = esc(r["description"]) or '<span class="zh">（无简介 No description）</span>'
    zh = r.get("description_zh")
    zh_html = f'<p class="news-body zh"><span class="tr">译</span>{esc(zh)}</p>' if zh else ""
    lang = r["language"]
    lang_html = f'<span class="lang-dot" style="background:{esc(r.get("language_color") or "#8b949e")}"></span>{esc(lang)}' if lang else "—"
    meta = (f'★ {r["stars"]:,} <span class="accent">(+{r["period_stars"]} 今日 today)</span>'
            f' · ⑂ {r["forks"]:,} forks · {lang_html} · <span class="cat">{esc(bcat(r["category"]))}</span>')
    topics = (" · " + "、".join(esc(t) for t in r.get("topics", [])[:6])) if r.get("topics") else ""
    tag = f'<p class="card-tag">topics 标签{topics} · category 分类：{esc(bcat(r["category"]))}</p>'
    riser = ""
    if show_riser and r.get("_days", 0) > 1:
        riser = f'<p class="riser-note">本周累计上榜 <b>{r["_days"]}</b> 天 · appeared {r["_days"]} days this week</p>'
    return f"""
    <div class="news-item">
        <h3 class="news-title">{rank}{link}</h3>
        <p class="news-body">{en}</p>
        {zh_html}
        {script_block(r)}
        <p class="repo-meta">{meta}</p>
        {riser}
        {tag}
    </div>"""


def daily_intro(daily):
    repos = daily["repos"]
    cats = Counter(r["category"] for r in repos)
    top_cat = cats.most_common(1)[0][0] if cats else "—"
    mx = max(repos, key=lambda r: r["period_stars"])
    zh = (f'今日 <span class="accent">{len(repos)}</span> 个仓库登上 GitHub Trending，'
          f'最热分类 <span class="highlight">{esc(top_cat)}</span>，单日最高 '
          f'<span class="accent">+{mx["period_stars"]}★</span>（<span class="highlight">{esc(mx["full_name"])}</span>）。')
    en = (f'Today <span class="accent">{len(repos)}</span> repos trended on GitHub. Hottest category '
          f'<span class="highlight">{esc(CAT_EN.get(top_cat, top_cat))}</span>; top daily gain '
          f'<span class="accent">+{mx["period_stars"]}★</span> by <span class="highlight">{esc(mx["full_name"])}</span>.')
    return f'<p class="intro-text">{zh}</p><p class="intro-text">{en}</p>'


def render_daily(daily):
    d = date.fromisoformat(daily["date"])
    nav_date = f'{d.year}年{d.month:02d}月{d.day:02d}日'
    intro = daily_intro(daily)
    items = "\n".join(repo_item(r) for r in daily["repos"])
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub 日榜｜{daily['date']}</title><style>{CSS}</style></head>
<body><div class="container">
<nav class="site-nav-lite"><a href="../index.html" class="nav-back">← 首页 / Index</a><span class="nav-date">{nav_date}</span></nav>
<h1 class="doc-title">GitHub 日榜｜<span>{daily['date']}</span></h1>
<p class="doc-date">{nav_date} · {weekday_cn(d)} · Daily GitHub Trending</p>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">今日榜单 <span class="en">Today's Board</span></h2>
  {intro}
  {items}
</div>
<div class="footer-block">
  <p>GitHub 日榜 · 每日自动收录自 GitHub Trending · Daily auto-collected from GitHub Trending</p>
  <p>数据来源 Source：<a href="https://github.com/trending?since=daily" target="_blank">github.com/trending?since=daily</a> · 抓取时间 Fetched：{esc(daily['fetched_at'])}</p>
</div>
</div></body></html>"""


def render_weekly(week_dailies, weekly):
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    rng = f"{monday.month}月{monday.day}日 — {sunday.month}月{sunday.day}日"
    n_days = len(week_dailies)
    appear = defaultdict(list)
    for dd in week_dailies:
        for r in dd["repos"]:
            appear[r["full_name"]].append(dd["date"])
    all_repos = [r for dd in week_dailies for r in dd["repos"]]
    cat_dist = Counter(r["category"] for r in all_repos)
    lang_dist = Counter(r["language"] for r in all_repos if r["language"])
    weekly_repos = weekly["repos"] if weekly else []
    for r in weekly_repos:
        r["_days"] = len(appear.get(r["full_name"], []))
    picks = sorted(weekly_repos, key=lambda r: (-r["_days"], -r["period_stars"]))[:12]

    cat_html = " · ".join(f"{esc(k)} <b>{v}</b>" for k, v in cat_dist.most_common())
    lang_html = " · ".join(f"{esc(k or '—')} <b>{v}</b>" for k, v in lang_dist.most_common(6))
    if n_days <= 1:
        note = (f'<p class="intro-text">本周刚启动，目前仅收录 <span class="accent">{n_days}</span> 天日榜。'
                f'Just launched — only <span class="accent">{n_days}</span> day collected so far.</p>'
                f'<p class="intro-text">随每日抓取累积，蝉联榜与分类热度会自动变丰满。'
                f'As daily snapshots accumulate, the repeat-board and category heat will fill in automatically.</p>')
    else:
        uniq = len(set(r["full_name"] for r in all_repos))
        note = (f'<p class="intro-text">本周已收录 <span class="accent">{n_days}</span> 天日榜，共 <span class="accent">{uniq}</span> 个不同仓库上榜。</p>'
                f'<p class="intro-text">Collected <span class="accent">{n_days}</span> daily boards this week, <span class="accent">{uniq}</span> distinct repos in total.</p>')

    cat_line = f'<p class="intro-text">分类热度 Category heat：{cat_html}</p>'
    lang_line = f'<p class="intro-text">语言热度 Language heat：{lang_html}</p>'

    risers = [r for r in picks if r["_days"] > 1]
    riser_html = ""
    if risers:
        riser_items = "\n".join(repo_item(r, show_riser=True) for r in risers)
        riser_html = f'<div class="section-block"><h2 class="section-header">蝉联榜 <span class="en">Consistent Risers</span></h2>{riser_items}</div><div class="divider"></div>'

    picks_html = "\n".join(repo_item(r, show_riser=True) for r in picks)
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub 周报｜{rng}</title><style>{CSS}</style></head>
<body><div class="container">
<nav class="site-nav-lite"><a href="../index.html" class="nav-back">← 首页 / Index</a><span class="nav-date">{monday.isoformat()}</span></nav>
<h1 class="doc-title">GitHub 周报｜<span>{rng}</span></h1>
<p class="doc-date">{monday.year}年{rng} · Weekly GitHub Trending</p>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">本周概览 <span class="en">Weekly Overview</span></h2>
  {note}
  {cat_line}
  {lang_line}
</div>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">本周精选 <span class="en">Weekly Picks</span></h2>
  {picks_html}
</div>
{riser_html}
<div class="footer-block">
  <p>GitHub 周报 · 由本周每日快照聚合生成 · Aggregated from this week's daily snapshots</p>
  <p>数据来源 Source：<a href="https://github.com/trending?since=weekly" target="_blank">github.com/trending?since=weekly</a></p>
</div>
</div></body></html>"""


def render_classics(classics):
    updated = classics["updated_at"]
    y, m, d = updated.split("-")
    nav_date = f"{y}年{m}月{d}日"
    intro = (f'<p class="intro-text">{esc(classics["intro_zh"])}</p>'
             f'<p class="intro-text">{esc(classics["intro_en"])}</p>')
    items = []
    for i, r in enumerate(classics["repos"], start=1):
        rank = f'<span class="rank">#{i}</span>'
        link = f'<a class="repo-link" href="{esc(r["url"])}" target="_blank">{esc(r["full_name"])}</a>'
        en = esc(r["description"])
        zh = r.get("description_zh")
        zh_html = f'<p class="news-body zh"><span class="tr">译</span>{esc(zh)}</p>' if zh else ""
        meta = f'★ {r["stars"]:,} stars · <span class="cat">{esc(r["category"])}</span>'
        note = f'<p class="news-label">点评 Note：{esc(r.get("note_zh", ""))} · {esc(r.get("note_en", ""))}</p>'
        tag = f'<p class="card-tag">精选于 Curated on {esc(r.get("added", updated))}</p>'
        items.append(f"""
    <div class="news-item">
        <h3 class="news-title">{rank}{link}</h3>
        <p class="news-body">{en}</p>
        {zh_html}
        {script_block(r)}
        <p class="repo-meta">{meta}</p>
        {note}
        {tag}
    </div>""")
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub 高分精选｜Curated Classics</title><style>{CSS}</style></head>
<body class="classics"><div class="container">
<nav class="site-nav-lite"><a href="../index.html" class="nav-back">← 首页 / Index</a><span class="nav-date">Updated {updated}</span></nav>
<h1 class="doc-title">GitHub 高分精选｜<span>Curated Classics</span></h1>
<p class="doc-date">{nav_date} 更新 · 人工精选高分仓库 · Curated high-star repos</p>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">高分精选 <span class="en">Curated Classics</span></h2>
  {intro}
  {''.join(items)}
</div>
<div class="footer-block">
  <p>GitHub 高分精选 · 人工精选 · 数据来自 GitHub · 中英双语</p>
  <p>人工挑选 Human-curated · 更新时间 Last updated：{updated} · <a href="https://github.com/trending" target="_blank">数据来源 Source：github.com/trending</a></p>
</div>
</div></body></html>"""


def render_index(daily, weekly_stem, week_dailies):
    dailies = sorted(glob.glob(str(DATA / "daily" / "*.json")))
    weeklies = sorted(glob.glob(str(DATA / "weekly" / "*.json")))
    daily_links = "".join(f'<a href="daily/{Path(f).stem}.html">{Path(f).stem}</a>' for f in reversed(dailies[-14:]))
    weekly_links = "".join(f'<a href="weekly/{Path(f).stem}.html">{Path(f).stem}（周）</a>' for f in reversed(weeklies[-8:]))
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub 日榜收录</title><style>{CSS}</style></head>
<body><div class="container">
<nav class="site-nav-lite"><a href="index.html" class="nav-back">GitHub 日榜收录</a><span class="nav-date">Index</span></nav>
<h1 class="doc-title">GitHub 日榜收录 <span>Archive</span></h1>
<p class="doc-date">每天自动抓取 GitHub Trending · 中英文双语 · Auto-collected daily · Bilingual</p>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">最新日报 <span class="en">Latest Daily</span></h2>
  <div class="news-item"><p class="news-body"><a class="repo-link" href="daily/{esc(daily['date'])}.html" style="font-size:18px">→ 打开 {esc(daily['date'])} 日榜 / Open daily board</a></p>
  <p class="card-tag">当日 {daily['count']} 个仓库上榜 · {daily['count']} repos today</p></div>
</div>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">最新周报 <span class="en">Latest Weekly</span></h2>
  <div class="news-item"><p class="news-body"><a class="repo-link" href="weekly/{esc(weekly_stem)}.html" style="font-size:18px">→ 打开本周周报 / Open weekly report</a></p></div>
</div>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">高分精选 <span class="en">Curated Classics</span></h2>
  <div class="news-item"><p class="news-body"><a class="repo-link" href="classics/index.html" style="font-size:18px">→ 打开高分精选 / Open curated classics</a></p>
  <p class="card-tag">人工精选高分仓库 · 中英双语 · Human-curated high-star repos</p></div>
</div>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">日榜归档 <span class="en">Daily Archive</span></h2>
  <div class="archive">{daily_links}</div>
</div>
<div class="divider"></div>
<div class="section-block">
  <h2 class="section-header">周报归档 <span class="en">Weekly Archive</span></h2>
  <div class="archive">{weekly_links}</div>
</div>
<div class="footer-block">
  <p>GitHub 日榜收录 · 数据来自 GitHub Trending · 视觉对齐 ainews 系列</p>
  <p>开源 Open Source：<a href="https://github.com/gengyueworks/github-daily-rank" target="_blank">github.com/gengyueworks/github-daily-rank</a> · 自动更新 Auto-updated daily</p>
</div>
</div></body></html>"""


def main():
    daily = load_latest("daily")
    weekly = load_latest("weekly")
    week_dailies = load_week_dailies()
    if not daily:
        print("没有日榜数据，先跑 scraper.py")
        return
    (SITE / "daily").mkdir(parents=True, exist_ok=True)
    (SITE / "weekly").mkdir(parents=True, exist_ok=True)
    (SITE / "classics").mkdir(parents=True, exist_ok=True)

    (SITE / "daily" / f"{daily['date']}.html").write_text(render_daily(daily), encoding="utf-8")

    weekly_stem = None
    if weekly:
        weekly_files = sorted(glob.glob(str(DATA / "weekly" / "*.json")))
        weekly_stem = Path(weekly_files[-1]).stem
        (SITE / "weekly" / f"{weekly_stem}.html").write_text(render_weekly(week_dailies, weekly), encoding="utf-8")

    classics_file = DATA / "classics.json"
    if classics_file.exists():
        classics = json.load(open(classics_file, encoding="utf-8"))
        (SITE / "classics" / "index.html").write_text(render_classics(classics), encoding="utf-8")
        print("  ", SITE / "classics" / "index.html")

    (SITE / "index.html").write_text(render_index(daily, weekly_stem, week_dailies), encoding="utf-8")
    print("生成完成：")
    print(" ", SITE / "daily" / f"{daily['date']}.html")
    if weekly_stem:
        print(" ", SITE / "weekly" / f"{weekly_stem}.html")
    print(" ", SITE / "index.html")


if __name__ == "__main__":
    main()

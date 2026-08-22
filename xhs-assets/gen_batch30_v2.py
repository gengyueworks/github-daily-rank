#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 日榜 · 小红书 30 期批量渲染 v2
数据源: xhs-assets/选题/30期选题清单-富化v2.md（夜间返工富化版）
输出:   xhs-assets/batch_30-v2/30-N/  每期 cover.png + repo1-3.png + xhs_post.txt + zip
视觉权威源: xhs_render.py（不改任何视觉规格）
"""
import os
import re
import sys
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import xhs_render  # noqa: E402
from xhs_render import cover, repo_card  # noqa: E402
from PIL import ImageFont  # noqa: E402

# ---- 运行时补丁（不改 xhs_render.py 文件）----
# P0: Menlo 无 CJK 字形，页眉页脚中文变豆腐块 → 换 Hiragino Sans GB（含拉丁+CJK）
PINGFANG = "/System/Library/Fonts/Hiragino Sans GB.ttc"
def _mono_reg(size):
    return ImageFont.truetype(PINGFANG, size, index=0)
def _mono_bold(size):
    try:
        return ImageFont.truetype(PINGFANG, size, index=1)
    except Exception:
        return ImageFont.truetype(PINGFANG, size, index=0)
xhs_render.mono_reg = _mono_reg
xhs_render.mono_bold = _mono_bold

# P0: 原 draw_tracked 右对齐逐字从右往左排位，导致「每天更新」渲染成「新更天每」
#     修正：先算总宽，再从左往右正常绘制
def _draw_tracked_fixed(d, xy, text, font, fill, tracking=0, anchor=None):
    x, y = xy
    if anchor == "ra":
        total = sum(d.textlength(ch, font=font) for ch in text)
        total += tracking * max(0, len(text) - 1)
        x = x - total
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking
    return x
xhs_render.draw_tracked = _draw_tracked_fixed

# P1: 原逐字换行会把 PDF 这类英文词劈成两半 → 词安全的折行
def _wrap_safe(d, text, font, max_w):
    import re as _re
    tokens = _re.findall(r"[A-Za-z0-9]+(?:[.\-'][A-Za-z0-9]+)*|\s|.", text)
    lines, cur = [], ""
    for tk in tokens:
        if tk == "\n":
            lines.append(cur); cur = ""; continue
        if tk == " ":
            trial = cur + " "
            if d.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur); cur = ""
            continue
        trial = cur + tk
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = tk
    if cur:
        lines.append(cur)
    # 避头尾：句读点不许单独成行，并回上一行
    _punct = set("。，、；：！？）】」』%.")
    merged = []
    for ln in lines:
        if ln and all(ch in _punct for ch in ln) and merged:
            merged[-1] += ln
        else:
            merged.append(ln)
    return merged
xhs_render.wrap = _wrap_safe

LIST_PATH = os.path.join(BASE, "选题", "30期选题清单-富化v2.md")
OUT_ROOT = os.path.join(BASE, "batch_30-v2")

PERIOD_RE = re.compile(r"^## 第 (\d+) 期")
REPO_RE = re.compile(r"^- \*\*(.+?)\*\* ★([\d,]+) · (.+)$")
FIELD_RE = re.compile(r"^  - (定位|功能点|场景|判断句|图片要素): (.+)$")
COVER_TITLE_RE = re.compile(r"^  - \*\*封面标题\*\*: (.+)$")


def parse_list(path):
    periods = []
    cur = None
    repo = None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        m = PERIOD_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "repos": [], "cover_title": ""}
            periods.append(cur)
            repo = None
            continue
        if cur is None:
            continue
        m = REPO_RE.match(line)
        if m:
            repo = {"repo": m.group(1), "stars": m.group(2), "lang": m.group(3).strip()}
            cur["repos"].append(repo)
            continue
        m = FIELD_RE.match(line)
        if m and repo is not None:
            repo[m.group(1)] = m.group(2).strip()
            continue
        m = COVER_TITLE_RE.match(line)
        if m:
            cur["cover_title"] = m.group(1).strip()
    return periods


def short_hook(loc):
    """定位第一分句作大标题；超长时在空格/顿号等边界截断，禁止切半词。"""
    for sep in ("，", "。", "；"):
        if sep in loc:
            loc = loc.split(sep)[0]
            break
    if len(loc) <= 24:
        return loc
    cut = loc[:24]
    for b in (" ", "、", "/", "+"):
        pos = cut.rfind(b)
        if pos >= 8:
            return cut[:pos]
    return cut


def build_card(repo):
    loc = repo.get("定位", "")
    scene = repo.get("场景", "").rstrip("。")
    if scene.endswith("时"):
        scene = scene[:-1] + "的时候用"
    take = repo.get("判断句", "")
    sub = f"{loc}。{scene}。"
    return {
        "repo": repo["repo"].replace("/", " / "),
        "title": short_hook(loc),
        "sub": sub,
        "stats": f"★ {repo['stars']}　·　{repo['lang']}",
        "take": take,
        "use": short_hook(loc),
        "gain": f"★ {repo['stars']} · {repo['lang']}",
    }


def write_post(period, outdir):
    lines = ["今天值得加入收藏夹的三个项目："]
    for i, r in enumerate(period["repos"], 1):
        hook = short_hook(r.get("定位", ""))
        lines.append(f"{i}. {r['repo']}：{hook}。")
    tag_line = period.get("cover_title", "")
    lines.append("")
    lines.append(f"第 {period['n']} 期 · 好工具帮人省去重复造轮子的时间")
    lines.append("#GitHub #开源项目 #开发者工具")
    if tag_line:
        pass
    open(os.path.join(outdir, "xhs_post.txt"), "w", encoding="utf-8").write("\n".join(lines))


def main():
    periods = parse_list(LIST_PATH)
    print(f"解析到 {len(periods)} 期")
    assert len(periods) == 30, "期数不对"
    date_tag = "08 · 22"
    ok = 0
    for per in periods:
        n = per["n"]
        outdir = os.path.join(OUT_ROOT, f"30-{n}")
        os.makedirs(outdir, exist_ok=True)
        cards = [build_card(r) for r in per["repos"]]
        assert len(cards) == 3, f"第 {n} 期仓库数 {len(cards)} != 3"
        cover(cards, date=date_tag, outdir=outdir)
        for i, c in enumerate(cards, 1):
            repo_card(i, len(cards), c, date=date_tag, outdir=outdir)
        write_post(per, outdir)
        zout = os.path.join(OUT_ROOT, f"30-{n}.zip")
        with zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED) as z:
            for fn in sorted(os.listdir(outdir)):
                z.write(os.path.join(outdir, fn), fn)
        ok += 1
        print(f"✓ 第 {n} 期 完成 ({ok}/30)")


if __name__ == "__main__":
    main()

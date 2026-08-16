#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 日榜 · 小红书栏目 · fable5 模板精确复刻 (PIL)
视觉 tokens: 白底 #FFFFFF / IKB #002FA7 / 正文 #0A0A0A / 次级 #6B6B6B / 辅助 #8A8A8A / 细线 #E2E2E2
字体: 衬线 Songti SC (≈Noto Serif CJK SC) + mono Menlo (≈Liberation Mono)
尺寸铁律: 1242×1660 (3:4)
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank/xhs-assets/2026-08-15-fable5"
os.makedirs(OUT, exist_ok=True)

W, H = 1242, 1660
WHITE  = (255, 255, 255)
IKB    = (0, 47, 167)      # #002FA7
INK    = (10, 10, 10)      # #0A0A0A
SUB    = (107, 107, 107)   # #6B6B6B
FAINT  = (138, 138, 138)   # #8A8A8A
LINE   = (226, 226, 226)   # #E2E2E2

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"
MENO = "/System/Library/Fonts/Menlo.ttc"
# 衬线: 0=Black 1=Bold 3=Light (无 Regular, 用 Bold 做 600, Light 做常规正文)
serif_bold  = lambda s: ImageFont.truetype(SONG, s, index=1)
serif_light = lambda s: ImageFont.truetype(SONG, s, index=3)
mono_reg    = lambda s: ImageFont.truetype(MENO, s, index=0)
mono_bold   = lambda s: ImageFont.truetype(MENO, s, index=1)

def wrap(d, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        t = cur + ch
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines

def draw_tracked(d, xy, text, font, fill, tracking=0, anchor=None):
    """带字距的手绘文本 (tracking=px)"""
    x, y = xy
    for ch in text:
        if anchor == "ra":
            w = d.textlength(ch, font=font)
            d.text((x - w, y), ch, font=font, fill=fill)
            x -= w + tracking
        else:
            d.text((x, y), ch, font=font, fill=fill)
            x += d.textlength(ch, font=font) + tracking
    return x

def footer(d):
    """页脚三要素: IKB 方块 + YUE GENG 悦 · GitHub 日榜 + 每天更新"""
    y = H - 96 - 40
    d.line([(96, y-30), (W-96, y-30)], fill=LINE, width=1)
    d.rectangle([96, y, 96+22, y+22], fill=IKB)
    draw_tracked(d, (96+34, y+2), "YUE GENG 悦", font=mono_reg(24), fill=INK, tracking=3)
    d.text((96+34 + d.textlength("YUE GENG 悦", font=mono_reg(24)) + 3*11 + 10, y+2), "· GitHub 日榜", font=mono_reg(24), fill=FAINT)
    draw_tracked(d, (W-96, y+8), "每天更新", font=mono_reg(22), fill=FAINT, tracking=5, anchor="ra")

def top_bar(d, kicker, date="08 · 15"):
    d.text((96, 104), "", font=mono_reg(24), fill=IKB)
    draw_tracked(d, (96, 104), kicker, font=mono_bold(24), fill=IKB, tracking=7)
    draw_tracked(d, (W-96, 104), date, font=mono_reg(24), fill=FAINT, tracking=4, anchor="ra")

# ============ 封面 (5 行, 模板行距按比例压缩) ============
def cover(projects, date="08 · 15"):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    top_bar(d, "GITHUB 今日榜", date)
    # h1: 今天值得点开的，只有 <em>5</em> 个。
    hf = serif_bold(84)
    y = 104 + 60 + 40
    d.text((96, y), "今天值得点开的，只有 ", font=hf, fill=INK)
    x = 96 + d.textlength("今天值得点开的，只有 ", font=hf)
    d.text((x, y), "5", font=hf, fill=IKB)
    x += d.textlength("5", font=hf)
    d.text((x, y), " 个。", font=hf, fill=INK)
    # rows: 5 行
    row_top = y + 130
    rows_area = (H - 96) - row_top - 120   # 留页脚
    row_h = rows_area // 5
    for i, p in enumerate(projects, 1):
        ry = row_top + (i-1) * row_h
        if i > 1:
            d.line([(96, ry), (W-96, ry)], fill=LINE, width=1)
        # rank
        d.text((96, ry + 10), str(i), font=serif_bold(52), fill=IKB)
        # rbody
        bx = 96 + 110
        d.text((bx, ry + 6), p["repo"], font=mono_reg(28), fill=SUB)
        d.text((bx, ry + 44), p["use"], font=serif_bold(36), fill=INK)
        st = p["gain"]
        d.text((bx, ry + 92), st, font=mono_reg(22), fill=FAINT)
    footer(d)
    out = os.path.join(OUT, "cover.png")
    img.save(out); print("saved", out)

# ============ 项目卡 (模板原值: h1 92 / sub 36 / stats 27 / take 35) ============
def repo_card(idx, total, p, date="08 · 15"):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    top_bar(d, f"GITHUB 今日榜 · {idx}/{total}", date)
    # main 区垂直居中
    main_top = 104 + 70
    main_h = (H - 96) - main_top - 130
    y = main_top + 40
    # repo 框
    rf = mono_reg(36)
    rw = d.textlength(p["repo"], font=rf) + 52
    rh = 36 + 32
    d.rectangle([96, y, 96+rw, y+rh], outline=INK, width=2)
    d.text((96+26, y+16), p["repo"], font=rf, fill=INK)
    y += rh + 64
    # h1
    hf = serif_bold(92)
    for ln in wrap(d, p["title"], hf, W-192):
        d.text((96, y), ln, font=hf, fill=INK); y += 96*1.4
    y += 56 - 20
    # sub
    sf = serif_light(36)
    for ln in wrap(d, p["sub"], sf, 1000):
        d.text((96, y), ln, font=sf, fill=SUB); y += 36*1.9
    y += 60 - 30
    # stats
    sf_mono = mono_reg(27)
    s = p["stats"]  # e.g. ★ 17,273　·　今日 +3,646　·　HTML
    parts = s.split("　")
    x = 96
    for pi, part in enumerate(parts):
        if pi == 1:  # 今日 +N 部分用 IKB bold
            d.text((x, y), part, font=mono_bold(27), fill=IKB)
        else:
            d.text((x, y), part, font=sf_mono, fill=INK)
        x += d.textlength(part, font=sf_mono) + 24
    y += 27*1.5 + 30
    # take (左边框 8px IKB)
    d.rectangle([96, y, 96+8, y+100], fill=IKB)
    tkf = serif_light(35)
    ty = y
    for ln in wrap(d, p["take"], tkf, 950):
        d.text((96+40, ty), ln, font=tkf, fill=INK); ty += 35*1.75
    footer(d)
    out = os.path.join(OUT, f"card-{idx:02d}-{p['repo'].split('/')[-1]}.png")
    img.save(out); print("saved", out)

projects = [
    {"repo":"cathrynlavery / diagram-design","title":"让 Claude 画出能直接用的图表。",
     "sub":"你让 AI 画图，出来的总是歪的、丑的、还得返工。把这 29 个模板喂给 Claude，它直接产出能放进汇报和文章的矢量图，改改文字就能用。",
     "stats":"★ 17,273　·　今日 +3,646　·　HTML",
     "take":"今天涨星最快的项目，解决的不是技术问题，是审美问题。",
     "use":"让 Claude 画出能直接用的图表","gain":"★ 17,273 · 今日 +3,646"},
    {"repo":"cactus-compute / needle","title":"14MB 的大模型，手表上也能跑。",
     "sub":"想让设备离线也聪明，云端又贵又慢。这个 14MB 基础模型直接装进手机、手表、机器人，本地就能推理。",
     "stats":"★ 5,617　·　今日 +662　·　Python",
     "take":"端侧 AI 的门槛，被它打下来了。",
     "use":"14MB 的大模型，手表上也能跑","gain":"★ 5,617 · 今日 +662"},
    {"repo":"megadose / holehe","title":"一个邮箱，查出你注册过哪些网站。",
     "sub":"总担心账号泄露却无从查起。输入邮箱，它借找回密码机制反查你注册过的网站，隐私自查一目了然。",
     "stats":"★ 12,855　·　今日 +427　·　Python",
     "take":"查别人的是工具，查自己的是警钟。",
     "use":"一个邮箱，查出你注册过哪些网站","gain":"★ 12,855 · 今日 +427"},
    {"repo":"macro-inc / macro","title":"把团队工具缝进一个台面。",
     "sub":"邮件、聊天、文档、任务来回切太碎。Macro 用共享 AI 记忆把这些 @ 串起来，一个界面搞定团队协作。",
     "stats":"★ 3,038　·　今日 +436　·　Rust",
     "take":"协作的碎片，被它收拢了。",
     "use":"把团队工具缝进一个台面","gain":"★ 3,038 · 今日 +436"},
    {"repo":"github / spec-kit","title":"动工前先定规范，少返工。",
     "sub":"代码改来改去返工多。Spec-Kit 帮你落地规范驱动开发，自动生成接口和测试，文档和代码不再脱节。",
     "stats":"★ 128,527　·　今日 +1,160　·　Python",
     "take":"十二万星，靠的是少返工。",
     "use":"动工前先定规范，少返工","gain":"★ 128,527 · 今日 +1,160"},
]

cover(projects)
for i, p in enumerate(projects, 1):
    repo_card(i, len(projects), p)
print("ALL DONE")

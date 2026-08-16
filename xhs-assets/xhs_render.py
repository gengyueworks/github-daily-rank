#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 日榜 · 小红书栏目 · fable5 模板渲染核心 (PIL)
视觉 tokens: 白底 #FFFFFF / IKB #002FA7 / 正文 #0A0A0A / 次级 #6B6B6B / 辅助 #8A8A8A / 细线 #E2E2E2
字体: 衬线 Songti SC + mono Menlo
尺寸铁律: 1242×1660 (3:4)
用法: from xhs_render import cover, repo_card
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1242, 1660
WHITE  = (255, 255, 255)
IKB    = (0, 47, 167)
INK    = (10, 10, 10)
SUB    = (107, 107, 107)
FAINT  = (138, 138, 138)
LINE   = (226, 226, 226)

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"
MENO = "/System/Library/Fonts/Menlo.ttc"
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
    y = H - 96 - 40
    d.line([(96, y-30), (W-96, y-30)], fill=LINE, width=1)
    d.rectangle([96, y, 96+22, y+22], fill=IKB)
    draw_tracked(d, (96+34, y+2), "YUE GENG 悦", font=mono_reg(24), fill=INK, tracking=3)
    d.text((96+34 + d.textlength("YUE GENG 悦", font=mono_reg(24)) + 33 + 10, y+2), "· GitHub 日榜", font=mono_reg(24), fill=FAINT)
    draw_tracked(d, (W-96, y+8), "每天更新", font=mono_reg(22), fill=FAINT, tracking=5, anchor="ra")

def top_bar(d, kicker, date="08 · 15"):
    draw_tracked(d, (96, 104), kicker, font=mono_bold(24), fill=IKB, tracking=7)
    draw_tracked(d, (W-96, 104), date, font=mono_reg(24), fill=FAINT, tracking=4, anchor="ra")

def cover(projects, date="08 · 15", outdir="."):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    top_bar(d, "GITHUB 今日榜", date)
    hf = serif_bold(84)
    y = 104 + 60 + 40
    d.text((96, y), "今天值得点开的，只有 ", font=hf, fill=INK)
    x = 96 + d.textlength("今天值得点开的，只有 ", font=hf)
    d.text((x, y), str(len(projects)), font=hf, fill=IKB)
    x += d.textlength(str(len(projects)), font=hf)
    d.text((x, y), " 个。", font=hf, fill=INK)
    row_top = y + 130
    rows_area = (H - 96) - row_top - 120
    row_h = rows_area // len(projects)
    for i, p in enumerate(projects, 1):
        ry = row_top + (i-1) * row_h
        if i > 1:
            d.line([(96, ry), (W-96, ry)], fill=LINE, width=1)
        d.text((96, ry + 10), str(i), font=serif_bold(52), fill=IKB)
        bx = 96 + 110
        d.text((bx, ry + 6), p["repo"], font=mono_reg(28), fill=SUB)
        d.text((bx, ry + 44), p["use"], font=serif_bold(36), fill=INK)
        d.text((bx, ry + 92), p["gain"], font=mono_reg(22), fill=FAINT)
    footer(d)
    out = os.path.join(outdir, "cover.png")
    img.save(out); return out

def repo_card(idx, total, p, date="08 · 15", outdir="."):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    top_bar(d, f"GITHUB 今日榜 · {idx}/{total}", date)
    main_top = 104 + 70
    y = main_top + 40
    rf = mono_reg(36)
    rw = d.textlength(p["repo"], font=rf) + 52
    rh = 36 + 32
    d.rectangle([96, y, 96+rw, y+rh], outline=INK, width=2)
    d.text((96+26, y+16), p["repo"], font=rf, fill=INK)
    y += rh + 64
    hf = serif_bold(92)
    for ln in wrap(d, p["title"], hf, W-192):
        d.text((96, y), ln, font=hf, fill=INK); y += 96*1.4
    y += 56 - 20
    sf = serif_light(36)
    for ln in wrap(d, p["sub"], sf, 1000):
        d.text((96, y), ln, font=sf, fill=SUB); y += 36*1.9
    y += 60 - 30
    sf_mono = mono_reg(27)
    parts = p["stats"].split("　")
    x = 96
    for pi, part in enumerate(parts):
        if pi == 1:
            d.text((x, y), part, font=mono_bold(27), fill=IKB)
        else:
            d.text((x, y), part, font=sf_mono, fill=INK)
        x += d.textlength(part, font=sf_mono) + 24
    y += 27*1.5 + 30
    d.rectangle([96, y, 96+8, y+100], fill=IKB)
    tkf = serif_light(35)
    ty = y
    for ln in wrap(d, p["take"], tkf, 950):
        d.text((96+40, ty), ln, font=tkf, fill=INK); ty += 35*1.75
    footer(d)
    out = os.path.join(outdir, f"card-{idx:02d}-{p['repo'].split('/')[-1]}.png")
    img.save(out); return out

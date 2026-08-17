#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小红书每日发布包生成器
每天从素材库取「下一期未用的」素材，生成可直接存草稿的发布包。
素材库: ~/Downloads/图片素材/悦的 AI 书签-小红书账号/000N/
发布包: 同目录下 _每日发布包/YYYY-MM-DD-第N期-内容描述/

用法: python3 gen_xhs_pkg.py
产出: 01-04.png（按发布顺序）+ 文案.txt + 存草稿操作.txt
"""
import os, shutil, re, datetime

MAT_ROOT = os.path.expanduser("~/Downloads/图片素材/悦的 AI 书签-小红书账号")
PKG_ROOT = os.path.join(MAT_ROOT, "_每日发布包")
USED_LOG = os.path.join(PKG_ROOT, "_已用期数.txt")

def load_used():
    if not os.path.exists(USED_LOG):
        return set()
    return set(open(USED_LOG).read().split())

def main():
    # 找所有 000N 期
    periods = sorted(
        [d for d in os.listdir(MAT_ROOT) if re.match(r"^000\d+$", d)],
        key=lambda x: int(x)
    )
    used = load_used()
    # 选下一期未用的
    target = None
    for p in periods:
        if p not in used:
            target = p
            break
    if not target:
        print("⚠️ 素材库没有未用期数了，等待 Notion 提供新素材")
        return
    src = os.path.join(MAT_ROOT, target)
    # 内容描述 = 文案第一行关键词
    desc = "素材"
    txt_file = os.path.join(src, "文案.txt")
    if not os.path.exists(txt_file):
        # 兼容 xhs_classic.txt / xhs_a.txt / xhs_b.txt 等命名
        cands = [f for f in os.listdir(src) if f.endswith(".txt")]
        if cands:
            txt_file = os.path.join(src, sorted(cands)[0])
    if os.path.exists(txt_file):
        first = open(txt_file).read().strip().splitlines()[0]
        desc = first.replace("：", " ").replace(":", " ")[:20]
    # 生成发布包
    date = datetime.date.today().strftime("%Y-%m-%d")
    pkg = os.path.join(PKG_ROOT, f"{date}-第{int(target)}期-{desc}")
    os.makedirs(pkg, exist_ok=True)
    # 图片按序复制
    img_order = ["cover.png", "repo1.png", "repo2.png", "repo3.png"]
    for i, name in enumerate(img_order, 1):
        sp = os.path.join(src, name)
        if os.path.exists(sp):
            shutil.copy(sp, os.path.join(pkg, f"{i:02d}.png"))
    # 文案
    if os.path.exists(txt_file):
        shutil.copy(txt_file, os.path.join(pkg, "文案.txt"))
    guide = f"""【小红书存草稿 · 3 步】(第 {int(target)} 期)

1. 打开创作者中心：https://creator.xiaohongshu.com/publish/publish
2. 上传图片：按 01.png → 02.png → 03.png → 04.png 顺序选（封面是第 1 张）
3. 粘贴文案（文案.txt 全文）→ 点「存草稿」，不要点发布

⚠️ 确认账号是「悦的 AI 书签」小号，不是大号！
"""
    open(os.path.join(pkg, "存草稿操作.txt"), "w").write(guide)
    # 标记已用
    with open(USED_LOG, "a") as f:
        f.write(target + "\n")
    print(f"✓ 发布包已生成: {pkg}")
    print("  内容:", sorted(os.listdir(pkg)))

if __name__ == "__main__":
    main()

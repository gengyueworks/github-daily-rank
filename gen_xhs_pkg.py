#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小红书每日发布包生成器（2026-10-28 重构版）
从拓展坞素材库 xhs-assets/本地渲染-v4/第N期/ 取「下一期未用的」素材，
生成可直接存草稿的发布包（cover.jpg + card-01~03.jpg + xhs_post.txt → 01~04.png + 文案.txt）。

素材库（唯一正确位置，禁放 Downloads）:
  /Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank/xhs-assets/本地渲染-v4/第N期/
  每期 = cover.jpg + card-01.jpg + card-02.jpg + card-03.jpg + xhs_post.txt

用法: python3 gen_xhs_pkg.py [--date YYYY-MM-DD]
产出: 01-04.png + 文案.txt + 存草稿操作.txt
"""
import os, shutil, re, sys, datetime, argparse

# 🚨 2026-10-28 铁律：素材库在拓展坞 xhs-assets，不在 Downloads！
# （Downloads 时时清，素材库放那会被清掉——8-21 旧路径被清理后发布包静默失败至今）
XHS_ASSETS = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank/xhs-assets"
MAT_ROOT = os.path.join(XHS_ASSETS, "本地渲染-v4")
PKG_ROOT = os.path.join(XHS_ASSETS, "_每日发布包")
USED_LOG = os.path.join(PKG_ROOT, "_已用期数.txt")

def load_used():
    if not os.path.exists(USED_LOG):
        return set()
    return set(open(USED_LOG).read().split())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y-%m-%d"))
    args = ap.parse_args()

    if not os.path.isdir(MAT_ROOT):
        print(f"❌ 素材库不存在（禁放 Downloads，必须在拓展坞）: {MAT_ROOT}")
        sys.exit(1)

    # 找所有「第N期」目录
    periods = sorted(
        [d for d in os.listdir(MAT_ROOT) if re.match(r"^第\d+期$", d)],
        key=lambda x: int(re.search(r"\d+", x).group())
    )
    used = load_used()
    target = None
    for p in periods:
        if p not in used:
            target = p
            break
    if not target:
        print("⚠️ 素材库没有未用期数了，等待新一期出图")
        return
    src = os.path.join(MAT_ROOT, target)

    # 文案文件 = xhs_post.txt（优先）/ 其他 txt
    txt_file = os.path.join(src, "xhs_post.txt")
    if not os.path.exists(txt_file):
        cands = [f for f in os.listdir(src) if f.endswith(".txt") and f != "存草稿操作.txt"]
        if cands:
            txt_file = os.path.join(src, sorted(cands)[0])
    desc = "素材"
    if os.path.exists(txt_file):
        first = open(txt_file).read().strip().splitlines()
        desc = first[0][:20] if first else "素材"

    # 生成发布包
    date = args.date
    pkg = os.path.join(PKG_ROOT, f"{date}-{target}-{desc}")
    os.makedirs(pkg, exist_ok=True)

    # 图片按序复制：cover.jpg → 01.png；card-01~03.jpg → 02~04.png
    img_map = [
        ("cover.jpg", "01.png"),
        ("card-01.jpg", "02.png"),
        ("card-02.jpg", "03.png"),
        ("card-03.jpg", "04.png"),
    ]
    copied = 0
    for sp_name, dp_name in img_map:
        sp = os.path.join(src, sp_name)
        if os.path.exists(sp):
            shutil.copy(sp, os.path.join(pkg, dp_name))
            copied += 1
    if copied == 0:
        print(f"⚠️ {target} 无可用图片（需 cover.jpg + card-01~03.jpg），跳过并提示补图")
        return

    if os.path.exists(txt_file):
        shutil.copy(txt_file, os.path.join(pkg, "文案.txt"))

    guide = f"""【小红书存草稿 · 3 步】({target})

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
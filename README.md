# GitHub 日榜收录 · GitHub Daily Rank

每天自动抓取 **GitHub Trending** 的日榜 / 周榜，解析成结构化数据，渲染成
**中英文双语**、视觉对齐 **ainews 系列** 的静态站点；周末汇总成周报。
给自己找灵感，也分享给喜欢技术的人。

## 视觉规范

- 1:1 沿用 ainews：克莱因蓝 `#002FA7`、强调红 `#C41E3A`、Inter / Noto Sans SC / JetBrains Mono、
  720px 容器、`section-header` 蓝色下划线、`news-item` / `news-body` / `card-tag` / `source-line` 结构。
- 内容双语：标题/栏目/概览/页脚均中 + EN；每个仓库含英文简介 + 中文翻译（译）。

## 目录结构

```
github-daily-rank/
├── scraper.py           # 抓 GitHub Trending（daily/weekly）→ data/*.json
├── inject_zh.py         # 把中文翻译写入 data/*.json 的 description_zh
├── build.py             # 读 data/ → 渲染 site/（ainews 风格 · 双语）
├── run.sh               # 一键：抓榜 + 翻译 + 生成
├── data/
│   ├── daily/YYYY-MM-DD.json     # 每日日榜快照
│   └── weekly/YYYY-MM-DD.json   # 每周一存的周榜快照
└── site/                # 生成的静态站（可直接部署 / 预览）
    ├── index.html
    ├── daily/YYYY-MM-DD.html
    └── weekly/YYYY-MM-DD.html
```

## 日常使用

```bash
bash run.sh     # 抓取 → 注入中文 → 生成站点
```

## 自动化（已配置）

- **每日**：定时抓取日榜 + 周榜，注入中文翻译，重新生成站点。
- **每周一**：刷新周榜快照，重算本周周报（蝉联榜 / 分类热度随天数累积自动变丰满）。

## 分享

`site/` 是纯静态 HTML，可直接用任意静态托管（CloudStudio / GitHub Pages / EdgeOne）
部署成一个链接发给技术朋友；本地也能直接打开 `site/index.html` 看。

## 数据说明

- 来源：<https://github.com/trending?since=daily> 与 `?since=weekly>
- 分类是轻量关键词启发（前端 / AI / 开发工具…），仅作「灵感」筛选参考。
- 小红书灵感区已取消（保持报告专业感）。

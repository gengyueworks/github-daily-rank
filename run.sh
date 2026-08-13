#!/usr/bin/env bash
# 一键更新：抓日榜+周榜 → 注入中文翻译 → 重新生成站点
set -e
cd "$(dirname "$0")"
PY=/Users/a0302/.workbuddy/binaries/python/envs/ghrank/bin/python
"$PY" scraper.py
"$PY" inject_zh.py
"$PY" build.py
echo "✅ 站点已更新：site/index.html"

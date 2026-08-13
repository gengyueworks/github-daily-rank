#!/usr/bin/env bash
# github-daily-rank 每日定时任务（launchd 调用）
# 流程：抓榜 → 注入中文（人工表 + 本机网关自动翻译）→ 生成 → 提交 data → 部署 gh-pages
# 注意：launchd 环境 PATH 精简，全部用绝对路径；外置盘脚本用 Framework python（TCC）
set -e

PROJ="/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank"
PY="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

cd "$PROJ"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始 ==="

# 1) 抓榜（daily + weekly）
"$PY" scraper.py

# 2) 注入中文翻译（人工表优先；新仓库走本机 8317 网关自动翻译）
"$PY" inject_zh.py --auto

# 3) 生成站点
"$PY" build.py

# 4) 提交 data 快照 + zh_cache 到 main（自动翻译缓存持久化）
git add data zh_cache.json
if ! git diff --cached --quiet; then
  GIT_EDITOR=true git -c user.name="gengyueworks-bot" -c user.email="gengyueworks@users.noreply.github.com" commit -m "daily: update trending data $(date +%Y-%m-%d)" --quiet
fi
GIT_EDITOR=true git pull --rebase origin main 2>&1 | tail -1 || true
git push origin main 2>&1 | tail -2
echo "✓ data 已提交推送"

# 5) 部署 site/ 到 gh-pages
bash deploy_ghpages.sh

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 完成 ==="

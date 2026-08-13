#!/usr/bin/env bash
# 部署 github-daily-rank 的 site/ 到 GitHub Pages (gengyueworks 账号)
# 用法: bash deploy_ghpages.sh
# 注意：基于脚本自身位置定位项目目录，不依赖 WorkBuddy 路径。
set -e
PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO=github-daily-rank
OWNER=gengyueworks
cd "$PROJ"

# 0) 同步远端（防并发 push 冲突）
git fetch origin main 2>/dev/null || true
GIT_EDITOR=true git pull --rebase --autostash origin main 2>&1 | tail -1 || true

[ -d .git ] || git init -q

# 1) 远端仓库不存在则创建 (public)
if ! gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public -d "GitHub 每日趋势榜 · 中英双语收录与周报 (ainews 视觉风格)" >/dev/null
fi
git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$OWNER/$REPO.git"

# 2) main: 提交完整工程
git add -A
git commit -q -m "update: GitHub daily rank project (scraper + bilingual ainews-style reports)" || echo "main: nothing new to commit"
git branch -M main
git push -u origin main -q

# 3) gh-pages: 仅放 site/ 内容到根目录
rm -rf /tmp/ghrank_pages
cp -r site /tmp/ghrank_pages
git checkout --orphan gh-pages
git rm -rf . -q 2>/dev/null || true
cp -r /tmp/ghrank_pages/. .
git add -A
git commit -q -m "site: publish static reports to GitHub Pages"
git push -u origin gh-pages -q -f
git checkout main -q

# 4) 开启 GitHub Pages (已开启则忽略)
echo "{\"source\":{\"branch\":\"gh-pages\",\"path\":\"/\"}}" | gh api "repos/$OWNER/$REPO/pages" -X POST --input - >/dev/null 2>&1 || true

echo "DONE: https://$OWNER.github.io/$REPO/"

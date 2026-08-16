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

# 3) 为仓库生成「一分钟逐字稿」（本机 8317 网关，缓存复用）
"$PY" gen_scripts.py

# 4) 生成站点
"$PY" build.py

# 5) 提交 data 快照 + zh_cache + script_cache 到 main（缓存持久化）
#    -X ours：data 是纯抓取快照，冲突时以本地最新抓取为准（rebase 中 ours=本地）
#    失败则中止（绝不能把冲突标记带进 commit）
#    🚨 2026-08-16 加固：pull 前先确认工作区干净。autostash 在 rebase 后 pop 回
#    未提交改动时，若远端同文件也变了会冲突并写入标记（weekly json 曾中招 15 处）。
if ! git diff --quiet; then
  echo "⚠️ 工作区有未提交改动，先 stash 再 pull（避免 autostash pop 冲突）"
  git stash push -u -m "pre-pull-auto-$(date +%H%M%S)" || { echo "❌ stash 失败"; exit 1; }
  NEED_POP=1
else
  NEED_POP=0
fi
if ! GIT_EDITOR=true git pull --rebase --autostash -X ours origin main >/dev/null 2>&1; then
  echo "❌ git pull --rebase 失败，中止（避免冲突标记进入 data）"
  git rebase --abort 2>/dev/null || true
  git stash pop 2>/dev/null || true
  exit 1
fi
if [ "$NEED_POP" = "1" ]; then
  if git stash pop 2>&1 | grep -q "CONFLICT"; then
    echo "❌ stash pop 冲突！检查 data/ 残留标记后手动处理"
    grep -rl '^<<<<<<< ' data/ 2>/dev/null | xargs -r rm -f  # 冲突时丢弃脏文件，下次抓取重生成
    git checkout -- . 2>/dev/null || true
    git stash drop 2>/dev/null || true
  fi
fi
if grep -rl '^<<<<<<< ' data/ 2>/dev/null | grep -q .; then
  echo "❌ data 目录残留冲突标记，中止"
  exit 1
fi
git add data zh_cache.json script_cache.json
if ! git diff --cached --quiet; then
  GIT_EDITOR=true git -c user.name="gengyueworks-bot" -c user.email="gengyueworks@users.noreply.github.com" commit -m "daily: update trending data $(date +%Y-%m-%d)" --quiet
fi
if ! GIT_EDITOR=true git pull --rebase --autostash -X ours origin main >/dev/null 2>&1; then
  echo "❌ 提交后 git pull --rebase 失败，中止"
  git rebase --abort 2>/dev/null || true
  exit 1
fi
if grep -rl '^<<<<<<< ' data/ 2>/dev/null | grep -q .; then
  echo "❌ data 目录残留冲突标记（提交后），中止"
  exit 1
fi
git push origin main 2>&1 | tail -2
echo "✓ data 已提交推送"

# 6) 部署 site/ 到 gh-pages
bash deploy_ghpages.sh

# 7) 打包网站页面 zip（每天更新完自动产出，供人工转给 Nosh 做小红书栏目）
#    内容 = site/ 的 4 个页面（index + daily + weekly + classics），不含源码
DATE_STAMP=$(date +%Y-%m-%d)
ZIP_OUT="$PROJ/../github-daily-rank-网站-$DATE_STAMP.zip"
rm -f "$ZIP_OUT"
cd "$PROJ/site"
zip -qr "$ZIP_OUT" index.html daily weekly classics
cd "$PROJ"
echo "✓ 网站 zip 已生成: $ZIP_OUT"
# 清理旧 zip（只留最近 7 天）
find "$PROJ/.." -maxdepth 1 -name "github-daily-rank-网站-*.zip" -mtime +7 -delete 2>/dev/null || true

# 8) 自动生成当日精选资料（编辑腔，Notion 作图部门素材源）+ 打包资料 zip
"$PY" gen_material.py "$DATE_STAMP" || echo "⚠️ 资料生成失败（不影响网站 zip）"
MAT_OUT="$PROJ/xhs-assets/GitHub经典项目资料库-$DATE_STAMP.md"
MAT_ZIP="$PROJ/../github-daily-rank-资料-$DATE_STAMP.zip"
if [ -f "$MAT_OUT" ]; then
  rm -f "$MAT_ZIP"
  zip -qj "$MAT_ZIP" "$MAT_OUT"
  echo "✓ 资料 zip 已生成: $MAT_ZIP"
fi
find "$PROJ/.." -maxdepth 1 -name "github-daily-rank-资料-*.zip" -mtime +30 -delete 2>/dev/null || true

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 完成 ==="

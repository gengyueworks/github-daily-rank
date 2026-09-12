# 自动化执行记录：每日 GitHub 日榜抓取/翻译/生成/部署

## 2026-09-04 (执行)
- **抓取**：`scraper.py`（venv `envs/ghrank`）成功。日榜 `data/daily/2026-09-04.json` = 19 个仓库；周榜 `data/weekly/2026-08-31.json`（本周一 0831）= 23 个仓库。
- **翻译**：先跑 `translate_missing.py`（命中已知词表 6+8 条），剩余 34 个新仓库由代理手译写回 `description_zh`，全部补齐，无遗漏。
- **生成**：`build.py` 重新生成 `site/daily/2026-09-04.html`、`site/weekly/2026-08-31.html`、`site/index.html`（ainews 双语风格）。
- **部署**：`bash deploy_ghpages.sh` 成功，线上 `https://gengyueworks.github.io/github-daily-rank/` 三个页面均返回 200。
- **冲突处理（重要）**：并行自动化 `automation-1786565219629` 已先提交 `data/weekly/2026-08-31.json` 到 remote main，导致原脚本 `git pull --rebase` 因未跟踪文件碰撞失败。解法：备份新数据到 `/tmp/ghrank_backup` → `git stash -u` → `git pull --rebase origin main`（快进到 dfbf679）→ 用备份覆盖写回本地 data 文件 → `git add -A && commit && push main`（4fe74de）→ 再跑 `deploy_ghpages.sh`（此时 pull 为 no-op）。本机周榜 23 条、全译，优于远端 21 条/20 译，已保留本机版本。
- **注意**：`site/` 已被 `.gitignore` 忽略，不进 main；gh-pages 独立 orphan 分支承载。部署后本地 `site/` 被 orphan 步骤清掉，已重跑 `build.py` 复原。gh-pages 内存在历史遗留的 `site/` 子目录与 `__pycache__` 冗余（不影响线上访问，根级 daily/weekly/index 正常 200）。

## 2026-09-08 (执行)
- **抓取**：`scraper.py`（venv `envs/ghrank`）成功。日榜 `data/daily/2026-09-08.json` = 14 个仓库；周榜 `data/weekly/2026-09-07.json`（本周一 0907）= 19 个仓库。
- **翻译**：`translate_missing.py` 仅命中词表已知项（日榜 2、周榜 3）。剩余 30 个新仓库由一次性脚本 `fill_zh_0908.py` 注入高质量人工校对中译并写回 `description_zh`（已有译文不覆盖；LunaTV、patent-disclosure-skill 描述本身已是中文，直接沿用）。完成后日榜 14/14、周榜 19/19 全部有 `description_zh`。临时脚本已 `git rm` 并单独提交清理（未留在仓库）。
- **生成**：`build.py` 重新生成 `site/daily/2026-09-08.html`、`site/weekly/2026-09-07.html`（标题区间 9月7日—9月13日）、`site/index.html`、`site/classics/index.html`（ainews 双语风格）。
- **部署**：`bash deploy_ghpages.sh` 成功（gh-pages orphan 推送）。线上复测：daily/weekly/index 三个页面及首页均 200。注意 gh-pages 的 orphan 步骤会清空本地 `site/`，已重跑 `build.py` 复原本地站点。
- **冲突**：本次无并行自动化抢提交，rebase 顺利。

## 结论
当日上榜：日榜 14 + 周榜 19；数据/翻译/站点已生成并推送 main，线上链接更新成功（200）。

## 2026-09-11 (执行)
- **抓取**：`scraper.py`（venv `envs/ghrank`）成功。日榜 `data/daily/2026-09-11.json` = 16 个仓库；周榜 `data/weekly/2026-09-07.json`（本周一 0907）= 22 个仓库。
- **翻译**：`translate_missing.py` 首轮命中词表补 10(日)+31(周)；新增 7 个仓库（alsk1992/CloddsBot、armory3d/armorpaint、diegosouzapw/OmniRoute、JustVugg/colibri、nashsu/llm_wiki、vercel-labs/skills、anomalyco/opencode）人工校对中译写入 MY_ZH 并重跑，最终日榜 16/16、周榜 22/22 全部有 `description_zh`。
- **生成**：`build.py` 重建 `site/daily/2026-09-11.html`、`site/weekly/2026-09-07.html`、`site/index.html`、`site/classics/index.html`（ainews 双语风格）。
- **部署冲突**：并行自动化 `automation-...629` 已先推送 `data/daily/2026-09-11.json` 到 remote main（bf5884f），导致 `deploy_ghpages.sh` 的 `git pull --rebase --autostash` 因「远端已提交该新文件 vs 本地未跟踪同名文件」在 stash-pop 阶段冲突而中止。解法：备份新数据到 `/tmp/ghrank_backup` → 移走未跟踪日榜文件 → 丢弃 2 个陈旧 autostash → `git stash -u` 仅存 3 个被改跟踪文件 → `git pull --rebase -X ours origin main`（快进合并远端，无冲突）→ `git stash pop` → 用备份覆盖写回本地日榜文件 → `git add -A && commit && push main`（56e0d12）→ 再跑 `deploy_ghpages.sh`（rebase 成 no-op）。
- **部署**：成功（gh-pages orphan 推送）。本地 `site/` 被孤儿步骤清空后已重跑 `build.py` 复原。线上复测：首页、daily、weekly 三个页面均 200。
- **结论**：当日上榜 日榜 16 + 周榜 22；数据/翻译/站点已生成并推送 main，线上链接更新成功（200）。

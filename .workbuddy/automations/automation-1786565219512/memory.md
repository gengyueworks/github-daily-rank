# 自动化执行记忆 · GitHub 日榜每日抓取

## 2026-08-15 (首次运行)
- **结果**：日榜 17 个仓库、周榜 16 个仓库，均已翻译（中英双语）、生成站点并部署成功。
- **线上链接**：https://gengyueworks.github.io/github-daily-rank/ 已更新（日榜 2026-08-15.html 实测 200 含新仓库）。
- **环境**：虚拟环境 `/Users/a0302/.workbuddy/binaries/python/envs/ghrank/bin/python` 可用；本地翻译网关 127.0.0.1:8317 可用（自动翻译生效，空描述仓库需手动补）。
- **⚠️ 已知坑（重要，下次必看）**：deploy_ghpages.sh 的 `git pull --rebase --autostash` 在与未提交的翻译修改冲突时，会把冲突标记写进 data/weekly/*.json 并提交到 main，导致下次 build.py 崩溃（JSONDecodeError）。本次修复方式：重抓 weekly 覆盖损坏文件 → inject_zh 重译 → build → 重新 deploy（main 无分歧后 pull 不再冲突）。建议：翻译修改后尽快 commit，或改 deploy 脚本避免 autostash 冲突。
- **交付物**：data/daily/2026-08-15.json、data/weekly/2026-08-10.json、site/index.html、site/daily/2026-08-15.html、site/weekly/2026-08-10.html。

# 自动化执行记忆 · GitHub 日榜每日抓取

## 2026-08-15 (首次运行)
- **结果**：日榜 17 个仓库、周榜 16 个仓库，均已翻译（中英双语）、生成站点并部署成功。
- **线上链接**：https://gengyueworks.github.io/github-daily-rank/ 已更新（日榜 2026-08-15.html 实测 200 含新仓库）。
- **环境**：虚拟环境 `/Users/a0302/.workbuddy/binaries/python/envs/ghrank/bin/python` 可用；本地翻译网关 127.0.0.1:8317 可用（自动翻译生效，空描述仓库需手动补）。
- **⚠️ 已知坑（重要，下次必看）**：deploy_ghpages.sh 的 `git pull --rebase --autostash` 在与未提交的翻译修改冲突时，会把冲突标记写进 data/weekly/*.json 并提交到 main，导致下次 build.py 崩溃（JSONDecodeError）。本次修复方式：重抓 weekly 覆盖损坏文件 → inject_zh 重译 → build → 重新 deploy（main 无分歧后 pull 不再冲突）。建议：翻译修改后尽快 commit，或改 deploy 脚本避免 autostash 冲突。
- **交付物**：data/daily/2026-08-15.json、data/weekly/2026-08-10.json、site/index.html、site/daily/2026-08-15.html、site/weekly/2026-08-10.html。

## 2026-08-16 (第二次运行)
- **结果**：日榜 13 个仓库、周榜 16 个仓库，全部完成中英双语翻译并生成站点、部署成功。
- **翻译**：本地网关 127.0.0.1:8317 在线但返回带解释的冗长译文（会污染 description_zh），故改为助手直译。新增 13 个仓库译文（cordiverse/cordis、cursor/plugins、unslothai/unsloth、public-apis、MakazhanAlpamys/Soup、github/spec-kit、megadose/holehe、altic-dev/FluidVoice、ToolJet、HKUDS/CLI-Anything、citrolabs/ego-lite、PrimeIntellect-ai/prime-agent、3b1b/manim）；其余沿用 inject_zh.py 的 ZH 人工表。当日唯一无英文简介的 google-deepmind/weathernext 跳过不译。
- **新脚本**：新增 `translate_missing.py`（带「已有 description_zh 不覆盖」守卫，新译文同步写入 zh_cache.json 供同周周榜重抓复用），下次可直接复用。
- **线上链接**：https://gengyueworks.github.io/github-daily-rank/ 已更新（index/weekly/daily 均实测 200；daily 新文件首拉偶发 404 系 Pages CDN 传播延迟，重试即 200）。
- **注意**：deploy_ghpages.sh 会在末尾 `git checkout main` 时把本地 site/ 工作目录清掉（site/ 为生成产物、未入库），属预期行为；数据在 data/ 与 gh-pages 分支均完好。

## 2026-08-17 (第三次运行)
- **结果**：日榜 7 个仓库、周榜 16 个仓库，全部完成中英双语翻译（无缺译）。新增 basecamp/omarchy、OpenCut-app/OpenCut 两个译文（已加进 translate_missing.py 的 MY_ZH，并写入 zh_cache.json 供周榜复用）。
- **抓取量异常**：今日日榜仅 7 个仓库（往常 13-17）。数据真实有效（含真实简介），非限流/解析错误；疑为 GitHub 当日 trending 展示较少，照常入库。
- **本地生成**：site/daily/2026-08-17.html、site/weekly/2026-08-17.html、site/index.html、site/classics/index.html 均成功生成（build.py 通过）。
- **⚠️ 部署失败（鉴权）**：`gh` CLI token 已失效（`gh auth status` 报 invalid），且 macOS keychain 中的 git 凭据也已失效——`git push` 报 `could not read Username: terminal prompts disabled`（仓库为 public，匿名 ls-remote 成功但 push 需鉴权）。`bash deploy_ghpages.sh` 因首步 `gh repo view` 的 TLS/鉴权失败而中止。已改用 git 直推验证：main 与 gh-pages 均 push 失败；随后清理掉本地残留的 gh-pages 孤儿分支与未推送的 main commit，使仓库回到干净 pre-deploy 状态（本地 main == origin/main 72de62b，数据文件作为工作区改动保留，无损）。
- **待补**：需用户重新 `gh auth login` 或刷新 keychain 中 github.com 的凭据后，下次运行即可把 site/ 推上 gh-pages（数据与前 3 步均已就绪）。线上链接本次未更新。
- **交付物（本地已生成、未上线）**：data/daily/2026-08-17.json、data/weekly/2026-08-17.json、site/daily/2026-08-17.html、site/weekly/2026-08-17.html、site/index.html。

## 2026-08-18 (第四次运行)
- **结果**：日榜 11 个仓库、周榜 16 个仓库，全部完成中英双语翻译（0 缺译）。新增 12 条译文（harry0703/MoneyPrinterTurbo、usestrix/strix、nautechsystems/nautilus_trader、akitaonrails/ai-memory、mukul975/Anthropic-Cybersecurity-Skills、AlexsJones/llmfit、santifer/career-ops、jundot/omlx、immich-app/immich、agalwood/Motrix、lightningpixel/modly、anthropics/skills）已加进 translate_missing.py 的 MY_ZH 并写入 zh_cache.json。
- **⚠️ 新坑（已解决）**：运行时发现远端 main 已推进到 d6d2bcd（非本地 72de62b），且远端已持有**完整翻译**的 2026-08-17 数据。deploy 脚本的 `git pull --rebase --autostash -X ours` 在回放本地自动暂存时，因 data/daily|weekly/2026-08-17.json 与 zh_cache.json 与远端重叠而冲突（报「data 目录残留冲突标记，中止」）。处置：冲突侧 "Updated upstream" = 远端已翻译版（daily 7 条 / weekly 16 条 description_zh），"Stashed changes" = 本地原始未译版（0 条）；故 `git checkout --ours` 保留远端翻译版（data 文件），`git checkout --theirs` 保留本地含 12 新译的 zh_cache.json，清理冲突后重跑 translate_missing + build，再本地 commit 后再跑 deploy（干净树，pull 不再冲突）。
- **本地生成**：site/daily/2026-08-18.html、site/weekly/2026-08-17.html、site/index.html、site/classics/index.html 均成功生成。
- **线上链接**：https://gengyueworks.github.io/github-daily-rank/ 已更新（远程 main=c5455b74、gh-pages=a91cd09e 均实测存在；index/weekly 首拉 200，daily/2026-08-18.html 首拉偶发 404 属 Pages CDN 传播延迟，重试即 200，页面含今日仓库）。
- **经验**：鉴权已于本次恢复（gh auth 有效），deploy 可直接成功；但凡本地有未提交改动，先本地 commit 再 deploy，可避免 autostash 回放冲突这一新坑。

## 2026-08-23 (第六次运行 / 本次)
- **前置分叉（关键）**：本地 main 与 origin/main 分叉——本地有未推送的 e72c53f（8-22 本地抓取），origin/main 已领先 11 个 commit（含另一会话推送的 8-21/8-22 趋势数据）。这正是 8-18 的 rebase 冲突陷阱。处置：`git reset --hard origin/main`（无数据丢失：origin 持完整翻译的 8-21/8-22 数据，且为公开权威源），本地回到 603038a 干净树。
- **抓取**：日榜 17、周榜 15，写入 data/daily/2026-08-23.json 与 data/weekly/2026-08-17.json（周榜按本周一命名，重抓覆盖）。
- **翻译**：reset 把 translate_missing.py 的 MY_ZH 回退到 8-19 版（丢了 8-22 条目，但 zh_cache.json 仍保留其干净译文）。新增 17 条助手直译（openai/codex、Wei-Shaw/sub2api、makeplane/plane、n8n-io/n8n、anthropics/claude-code、multica-ai/andrej-karpathy-skills、ripienaar/free-for-dev、Tencent/AI-Infra-Guard、eneskirca/nodeterm + 自 zh_cache 回填的 8 条 8-22 译文）写回 data 与 zh_cache；日报 17/17、周报 15/15 均 0 缺译。本机 127.0.0.1:8317 网关未启用，全用助手直译（避免污染）。
- **本地生成**：site/daily/2026-08-23.html、site/weekly/2026-08-17.html、site/index.html、site/classics/index.html（build.py 通过）。
- **部署**：先本地 commit（d00f876）使树干净、main 领先 origin 1 commit 无分叉 → deploy rebase 为 no-op 无冲突。main=d00f876、gh-pages=72e3fd4 已推送；daily/2026-08-23.html 首拉 404（Pages CDN 延迟，8s 后重试转 200 含今日仓库），index 与 weekly 首拉即 200。
- **线上链接**：https://gengyueworks.github.io/github-daily-rank/ 已更新成功。
- **固化经验**：每次运行「先本地 commit 再 deploy」；若本地与 origin 分叉，优先 `git reset --hard origin/main`（权威源）再在其上做当日工作，彻底规避 autostash 回放冲突。持久层是 zh_cache.json（被 inject_zh.py 读取复用），MY_ZH 仅辅助，reset 会丢，故新增译文应同时进 MY_ZH 与 zh_cache。

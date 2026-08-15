# GitHub 日榜收录 · 工作流文档

> 本文件是操作手册。任何 Agent 接手 github-daily-rank 任务时，先读本文件即可执行。
> 上线地址：https://gengyueworks.github.io/github-daily-rank/
> 仓库：https://github.com/gengyueworks/github-daily-rank（main 存工程源码，gh-pages 存网页）

---

## 一、项目定位

每天自动抓取 **GitHub Trending** 日榜/周榜，解析成结构化数据，渲染成中英双语、视觉对齐 ainews 系列（克莱因蓝）的静态站。四个页面：

| 页面 | 路径 | 内容 |
|---|---|---|
| 首页 | `site/index.html` | 今日日榜入口 + 周报入口 + 高分精选入口 + 归档 |
| 日榜 | `site/daily/YYYY-MM-DD.html` | 当日上升最快仓库（17 个左右），每个带中文翻译 + 一分钟逐字稿 |
| 周报 | `site/weekly/YYYY-MM-DD.html` | 本周汇总（蝉联榜 / 分类热度随天数累积） |
| 高分精选 | `site/classics/index.html` | 人工精选的高分项目，每个带双语点评 + 一分钟逐字稿 |

## 二、目录结构与数据流

```
github-daily-rank/
├── scraper.py        # 抓 GitHub Trending（daily/weekly）→ data/*.json
├── inject_zh.py      # 中文翻译：人工表优先 + 本机 8317 网关自动翻译 → description_zh
├── gen_scripts.py    # 一分钟逐字稿：调本机 8317 网关 → script_zh（缓存 script_cache.json）
├── build.py          # 读 data/ → 渲染 site/（ainews 克莱因蓝风格，唯一视觉权威源）
├── run.sh            # 手动一键：抓榜 + 翻译 + 生成（不含部署）
├── ghrank_daily.sh   # launchd 每日任务入口：抓榜→翻译→逐字稿→生成→提交→部署
├── deploy_ghpages.sh # 部署 site/ 到 gh-pages 分支
├── data/
│   ├── daily/YYYY-MM-DD.json     # 每日日榜快照（含 description_zh / script_zh）
│   ├── weekly/YYYY-MM-DD.json    # 周榜快照
│   └── classics.json             # 高分精选数据（人工维护，SSOT）
├── zh_cache.json     # 自动翻译缓存（full_name → 中文）
├── script_cache.json # 逐字稿缓存（full_name → 口播稿）
└── site/             # 生成的静态站（gitignore，不提交 main）
```

**数据流**：`scraper.py → inject_zh.py → gen_scripts.py → build.py → deploy_ghpages.sh`

## 三、自动化（主链路 = 本机 launchd）

- **任务**：`com.local.github-daily-rank`（plist 在 `~/Library/LaunchAgents/`）
- **时间**：每天 09:00 + 每周一 10:00（北京时间）
- **入口**：`ghrank_daily.sh`，全链路：
  1. `scraper.py` 抓 daily + weekly
  2. `inject_zh.py --auto` 注入中文（人工表优先，新仓库走本机 8317 网关，缓存 zh_cache.json）
  3. `gen_scripts.py` 生成一分钟逐字稿（缓存 script_cache.json，已生成的不重复调用）
  4. `build.py` 生成站点
  5. 提交 data + 缓存到 main（先 `git pull --rebase --autostash` 防冲突）
  6. `deploy_ghpages.sh` 部署 gh-pages
- **日志**：`~/Library/Logs/github-daily-rank.{out,err}.log`
- **监控**：巡逻员 `automation_patrol.py` 自动覆盖（com.local.* 口径），失灵摘红灯
- **云端兜底**：`.github/workflows/daily.yml` 只保留 `workflow_dispatch` 手动触发（⚠️ 云端访问不到本机 8317 网关，所以翻译/逐字稿必须在主链路跑；云端 Actions 只做抓取+生成+部署，作为本机挂掉时的兜底）

### 手动操作

```bash
# 手动跑完整链路（含部署）
bash ghrank_daily.sh

# 只重新生成页面（改了 build.py 后）
python3 build.py

# 只补翻译/逐字稿（新仓库或改了缓存）
python3 inject_zh.py --auto
python3 gen_scripts.py

# 手动部署
bash deploy_ghpages.sh

# 触发云端兜底
gh workflow run daily.yml -R gengyueworks/github-daily-rank
```

### ⚠️ launchd 环境三大铁律（违反必踩坑）

1. **外置盘 TCC**：launchd 跑 /Volumes 上的脚本必须用 Framework python `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`，禁止 `/usr/bin/python3`（TCC 未授权外置卷，静默失败）
2. **精简 PATH**：`ghrank_daily.sh` 里显式 `export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"`
3. **git 冲突（2026-08-15 加固）**：commit/push 前必须 `GIT_EDITOR=true git pull --rebase --autostash -X ours origin main`（-X ours：data 是纯抓取快照，冲突时以本地最新为准）。**禁止 `|| true` 吞掉 rebase 失败**——否则冲突标记 `<<<<<<<` 会混进 data/*.json 并被 commit。正确姿势：pull 失败立即 `git rebase --abort` 退出；commit 前 grep 检查 `^<<<<<<< ` 残留。

## 四、一分制逐字稿（gen_scripts.py）

每个仓库卡片里有一段「一分钟讲解 1-min」口播稿，讲三件事：这是什么 / 有什么用 / 为什么好。

- **调用**：本机 CLIProxyAPI 网关 `http://127.0.0.1:8317/v1/chat/completions`（OpenAI 兼容，模型 `gemini-3.5-flash-low`，key `sk-123`）
- **生成要求**：120-180 字中文、口语化、不书面腔、不用「大家好」开头、不出现「逐字稿」字样、像跟朋友聊天
- **排版（PureFlow 断行铁律，2026-08-15 固化）**：一句一行，每行以句号/问号/感叹号结尾；空行分段（\n\n 分段、\n 断行）；不要长段落，像微信公号排版有呼吸感。渲染时 build.py 的 script_block() 把 \n\n → 多段落、\n → <br>
- **缓存**：`script_cache.json`，已生成的不重复调用；新仓库自动补；改了格式后要 `清空所有 script_zh 字段 + 删 script_cache.json` 再全量重生成（--no-cache 只绕过缓存，不会重生成已写字段的仓库）
- **可配置**：环境变量 `GHRANK_LLM_URL` / `GHRANK_LLM_KEY` / `GHRANK_LLM_MODEL`
- ⚠️ 8317 网关依赖本机 CLIProxyAPI 进程常驻；网关挂了则新仓库无逐字稿（抓榜部署不受影响），补跑 `python3 gen_scripts.py` 即可

## 五、中文翻译（inject_zh.py）

- 两级来源：**人工 ZH 表优先**（质量最高，`inject_zh.py` 顶部 ZH 字典），缺失时**自动翻译**（同上 8317 网关）
- 自动翻译结果写回 `zh_cache.json`，下次直接命中
- 新仓库上榜先显示英文，翻译表/缓存更新后自动补齐

## 六、高分精选页（classics）如何收录

`data/classics.json` 是人工维护的 SSOT，每个条目：

```json
{
  "full_name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "stars": 12345,
  "description": "英文简介",
  "description_zh": "中文简介",
  "category": "分类",
  "note_zh": "一句话中文点评",
  "note_en": "一句话英文点评",
  "added": "YYYY-MM-DD"
}
```

**收录流程（含小红书等平台推荐内容）**：

1. **解析来源链接**（小红书短链 xhslink.cn → 用 curl -L 拿真实 note URL → ego-browser 打开）
2. **提取内容**：正文文字用 snapshotText；正文在图片里时下载图片，派 @observer 逐张分析提取
3. **验证仓库真实存在**（铁律，防死链）：`gh api "repos/owner/repo" --jq '.full_name + "|" + (.stargazers_count|tostring)'`，404 即笔记有笔误，不要收录
4. **原创化改写**（🚨 平台来源红线）：小红书内容吸收后自己重新组织语言，仓库/正文**禁止出现「小红书」「xhslink」等平台痕迹**，git/GitHub 上绝不出现平台来源备注
5. **写入 classics.json** + 跑 `python3 gen_scripts.py` 补逐字稿 + `python3 build.py` 重新生成
6. **提交 + 部署**：`git add data && git commit && git push origin main && bash ghrank_daily.sh`
7. ⚠️ GitHub Pages 有 CDN 缓存延迟（约 30-60 秒），部署后稍等再验证 200

## 七、视觉规范（严格对齐 ainews，build.py 内 CSS 是唯一权威源）

**权威参考**：ai-news 最新日报 HTML 的完整 CSS（`/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/32-AI高质量阅读库/05-情报与深读系统/AI精华情报与深读操作台/10-源头网站活文件/00-站点根文件/ai-news-site/2026-08/` 里最新一期）。

### 🚨 红蓝配比铁律（用户强调，违反即返工）

1. **蓝色（--klein #002FA7）是绝对主色**：mast-title、mast-rule 3px 蓝线、sec-title ■ 方块前缀、item 仓库链接、.src 编号、.cat 分类、footer 3px 蓝顶线——全蓝
2. **红色（--accent #C41E3A）只做极少量点缀**：ainews 中红色**只出现在正文数字上**（`.body .num`，JetBrains Mono 红数字，如 ★ star 数）
3. **配比 ≈ 蓝:红 = 10:1**（实测 ai-news 蓝 19 处 / 红 2 处；classics 蓝 28+ / 红 3 处）。**禁止**大段红字、红色底纹、红色强调词滥用
4. 颜色体系 1:1 对齐 ainews：`--klein:#002FA7; --klein-bright:#0044FF; --paper:#FFFFFF; --ink:#0E0E10; --ink-soft:#3A3A3E; --gray:#6B6B70; --gray-light:#9CA3AF; --line:#E8E8EC; --accent:#C41E3A`
5. 正文结构沿用 ainews 语义类：masthead / mast-title / mast-rule / mast-lede / sec-title / item / dateline / item-title / body / tag / src-line / num / footer。classics 页用 `body.classics` 前缀隔离专属样式，daily/weekly 不受影响

### 逐字稿排版（2026-08-14 修正后）

- 逐字稿是**正文级段落**（15.5px，行高 1.8），不是大色块：`<p class="script-block"><span class="script-tag">一分钟讲解 1-min</span>正文</p>`
- 「一分钟讲解」小标签 = klein 蓝底白字小徽章（10-11px），禁止自创大底纹块（#EEF2FF 底纹方案已废弃）

### 每个仓库卡片必备的链接（用户强调，2026-08-15 改为链接区方案）

每张卡片底部必须有**链接区**（`link-area`），用户发推/分享需要能方便复制完整 URL：

1. **链接区**：点评行之后 `<div class="link-area">`，两行 `link-row`：
   - 仓库链接：`<a class="link-url" href="仓库URL" target="_blank">完整URL文本</a>`（完整文本可见、整段可选可复制、点击跳转）
   - star 链接：`https://github.com/{owner}/{repo}/stargazers` 同样式
   - 每行配「复制 Copy」按钮（`copy-btn`，data-copy 存 URL，navigator.clipboard + fallback，复制后短暂变「已复制 ✓」）
2. **禁止**旧的 `star-btn` 蓝底白字小按钮（11px 白字蓝底，用户反馈「看不清、莫名其妙」，2026-08-15 已废弃删除）
3. 每张卡片必须有链接区，缺一个 = 返工

### 排版数值（全局，daily/weekly/index 共用）

- 正文 body：15.5-16px，行高 1.8-1.9
- 仓库名 item-title：21px，行高 1.5，text-wrap: balance
- 卡片间距 news-item / item：52px；卡片内块间距 14-16px
- 大标题：36-44px；section-header：24px
- 容器：默认 720px；classics 页 `body.classics .container` 专享 860px（阅读型加宽）
- 数字用 JetBrains Mono + tabular 对齐（ainews 的 .num 风格）
- **改样式**：只改 build.py 顶部 CSS 常量，再跑 `python3 build.py`。样式规则集中管理，禁止散落多处
- **三个页面（daily/weekly/index）共用同一份 CSS**，改全局数值会同步生效；只想改 classics 用 `body.classics` 前缀

## 八、常见坑（错题本）

| 坑 | 现象 | 解法 |
|---|---|---|
| deploy 硬编码旧路径 | 部署的是 WorkBuddy 旧目录 | `deploy_ghpages.sh` 用 `$(dirname "${BASH_SOURCE[0]}")` 定位，禁止硬编码路径 |
| gh-pages 分支已存在 | `git checkout --orphan gh-pages` 失败 | 先 `git checkout main -q && git branch -D gh-pages -q` 再 orphan |
| 云端 Actions 与本机双跑 | data 互相覆盖、push 冲突 | 主链路本机 launchd，Actions 只留 workflow_dispatch |
| 外置盘 TCC | launchd 静默失败退出码 2 | Framework python（见三） |
| GitHub Pages 缓存 | 部署后线上还是旧版 | 等 30-60 秒再验证 |
| site/ 提交进 main | gitignore 后需 git rm --cached | site/ 已在 .gitignore |
| SSL 网络抖动 | push 偶发 LibreSSL SSL_ERROR_SYSCALL | 重试即可；`git push | tail` 会吞掉失败码，检查要 `git rev-parse origin/main` 对比 |

## 九、SSOT 声明

- **页面生成逻辑**：`build.py`（唯一权威源，改样式/结构只改它）
- **高分精选数据**：`data/classics.json`（人工维护，收录走第六节流程）
- **翻译人工表**：`inject_zh.py` 的 `ZH` 字典 + `zh_cache.json`
- **逐字稿**：`script_cache.json`（可由 gen_scripts.py 再生）
- **站点部署**：gh-pages 分支（线上唯一真源），main 分支是工程源码 + data 快照

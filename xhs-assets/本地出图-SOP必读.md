# 小红书本地出图 SOP（必读，2026-08-23 定稿）

> 出图唯一权威流程。踩坑细节见 `/_temp/agent-错题本/2026-08-23-xhs-v4本地出图六坑与定稿流程.md`。
> 交付定稿结构：`本地渲染-v4/第N期/` = cover.jpg + card-01~03.jpg + xhs_post.txt（5 个文件，一期一发）。

## 流程五步

1. **生成 HTML**：`gen_html_v4.py` 输出到 `xhs_render_html_v4/第N期/`（cover.html + card-01~03.html + xhs_post.txt）
2. **ego-browser 截图**：1242×1660，每批 3~5 期，断点续跑，每批磁盘验证
3. **PIL 转 JPG**：`quality=95, subsampling=0`（禁止 sips，见坑 5）
4. **文字稿归位**：xhs_post.txt 复制进每期图片文件夹
5. **更新发布记录**：`发布记录.md` 追加一行

## 截图代码模板（验证过的正确写法）

```bash
ego-browser nodejs <<'EOF'
import fs from 'fs'
await useOrCreateTaskSpace('xhs-local-render')
const base = '/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank/xhs-assets'
const enc = p => 'file://' + encodeURI(p)
const pages = ['cover.html','card-01.html','card-02.html','card-03.html']
for (let i = 起始期; i <= 结束期; i++) {
  const outDir = `目标目录/第${i}期`
  fs.mkdirSync(outDir, { recursive: true })
  for (const p of pages) {
    const name = p.replace('.html','.png')
    if (fs.existsSync(outDir + '/' + name) && fs.statSync(outDir + '/' + name).size > 50000) continue
    await gotoAndWait(enc(`${base}/xhs_render_html_v4/第${i}期/${p}`))
    await cdp('Emulation.setDeviceMetricsOverride', { width: 1242, height: 1660, deviceScaleFactor: 1, mobile: false })
    fs.copyFileSync(await captureScreenshot(), outDir + '/' + name)
  }
  cliLog(`第${i}期 done`)
}
EOF
```

## 六条铁律（违反必返工）

1. `captureScreenshot()` 返回**临时文件路径**，不是 base64，用 copyFileSync 落盘
2. heredoc 用 ESM：`import fs from 'fs'`，禁止 require
3. 每批最多 3~5 期；批次结束必须 ls 验证磁盘文件数和大小；断了从缺失文件续跑
4. 空白页都截不了 = ego lite 僵死，立即重启（`pkill -9 -f "ego lite"` + `open -a "ego lite"`），不要反复重试
5. PNG 转 JPG 只用 PIL `quality=95, subsampling=0`；sips 的 4:2:0 会糊掉蓝底白字；PNG 底稿确认转换成功前不删
6. 交付目录必须自包含：图 + xhs_post.txt 同文件夹；只留 JPG 一种格式；发布只认 `本地渲染-v4/`

## 收尾

- `completeTaskSpace('xhs-local-render', { keep: false })` 关 space
- 全量验证：`find 本地渲染-v4 -name "*.jpg" | wc -l` = 30×每期张数，无小于 30k 的文件

import re, os, sys, urllib.parse

BASE = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank"
PKG = f"{BASE}/xhs-assets/Notion出图包-2026-08-22"
OUT = "/Volumes/拓展坞 1T2022/2 Codex-Workspace/Codex-Workspace-Main/30-项目-网站/gengyueworks-Github/github-daily-rank/xhs-assets/xhs_render_html_v4"

cover_tpl = open(f"{PKG}/template_cover_v2.html").read()
card_tpl = open(f"{PKG}/template_repo_v2.html").read()
text = open(f"{PKG}/30期选题清单-富化v4.md").read()

issues = re.split(r'\n## 第 (\d+) 期\n', text)[1:]
# issues = [num1, body1, num2, body2, ...]

def parse_cards(body):
    cards = []
    for m in re.finditer(r'- \*\*([^*]+)\*\* ★([\d,]+) · ([^\n]+)\n((?:  - .*\n)+)', body):
        repo, star, lang, b = m.groups()
        def f(name):
            mm = re.search(rf'- {name}: (.+)', b)
            return mm.group(1).strip() if mm else ''
        cards.append(dict(repo=repo, star=star, lang=lang.strip(),
                          cover=f('封面短描'), title=f('卡片标题'), sub=f('副文'),
                          tag=f('卖点标签'), take=f('判断句')))
    return cards

def parse_post(body):
    m = re.search(r'### 小红书正文\n\n(.*?)(?=\n---|\Z)', body, re.S)
    return m.group(1).strip() if m else ''

def fmt_repo(repo):  # 斜杠两侧加空格
    return ' / '.join(repo.split('/'))

only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
count = 0
for i in range(0, len(issues), 2):
    num = int(issues[i]); body = issues[i+1]
    if only and num not in only: continue
    cards = parse_cards(body)
    assert len(cards) == 3, f"第{num}期卡数={len(cards)}"
    d = f"{OUT}/第{num}期"; os.makedirs(d, exist_ok=True)
    # 封面
    h = cover_tpl
    h = h.replace('今天值得点开的，只有 3 个。', '今天值得点开的，只有 3 个。')
    for n, c in enumerate(cards, 1):
        h = h.replace('{{repo%d_name}}' % n, fmt_repo(c['repo']))
        h = h.replace('{{repo%d_desc}}' % n, c['cover'])
        h = h.replace('{{repo%d_stars}}' % n, c['star'])
        h = h.replace('{{repo%d_gain}}' % n, c['lang'] if c['lang'] else '—')
    open(f"{d}/cover.html", 'w').write(h)
    # 项目卡
    for n, c in enumerate(cards, 1):
        h = card_tpl.replace('{{index}}', f'{n}/3')
        h = h.replace('{{repo_name}}', fmt_repo(c['repo']))
        h = h.replace('{{title}}', c['title'])
        h = h.replace('{{sub}}', c['sub'])
        h = h.replace('{{stars}}', c['star'])
        h = h.replace('{{gain}}', c['tag'])
        h = h.replace('{{language}}', c['lang'] if c['lang'] else '—')
        h = h.replace('{{take}}', c['take'])
        open(f"{d}/card-{n:02d}.html", 'w').write(h)
    # 正文
    open(f"{d}/xhs_post.txt", 'w').write(parse_post(body) + '\n')
    count += 1
print(f"生成期数: {count}")
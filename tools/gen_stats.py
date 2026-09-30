"""Builds the pixel stat cards from the GitHub GraphQL API (or --sample data for a design preview).

usage: python3 tools/gen_stats.py OUT_DIR [--sample]
env:   GITHUB_TOKEN, GITHUB_USER (default: repository owner)
"""
import datetime, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from pixelfont import THEMES, head, panel, ptext, runs, text_w

QUERY = """query($login:String!){ user(login:$login){
  followers{totalCount}
  repositories(ownerAffiliations:OWNER,isFork:false,first:100,orderBy:{field:PUSHED_AT,direction:DESC}){
    totalCount nodes{ stargazerCount languages(first:8,orderBy:{field:SIZE,direction:DESC}){ edges{size node{name}} } } }
  contributionsCollection{ contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } }
} }"""

def fetch(login, token):
    req = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': login}}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': 'pixel-profile'})
    u = json.load(urllib.request.urlopen(req, timeout=30))['data']['user']
    days = sorted((d['date'], d['contributionCount'])
                  for w in u['contributionsCollection']['contributionCalendar']['weeks'] for d in w['contributionDays'])
    today = datetime.date.today().isoformat()
    days = [d for d in days if d[0] <= today]
    cur = 0
    for i, (_, n) in enumerate(reversed(days)):
        if n > 0: cur += 1
        elif i == 0: continue
        else: break
    best = run = 0
    for _, n in days:
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    langs = {}
    for r in u['repositories']['nodes']:
        for e in r['languages']['edges']:
            langs[e['node']['name']] = langs.get(e['node']['name'], 0) + e['size']
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    return dict(contribs=u['contributionsCollection']['contributionCalendar']['totalContributions'],
                current=cur, longest=best, repos=u['repositories']['totalCount'],
                stars=sum(r['stargazerCount'] for r in u['repositories']['nodes']),
                followers=u['followers']['totalCount'],
                langs=[(n, round(b * 100 / total)) for n, b in top])

SAMPLE = dict(contribs=667, current=4, longest=15, repos=12, stars=3, followers=9,
              langs=[('Python', 46), ('TypeScript', 24), ('Shell', 14), ('Go', 9), ('C', 7)])

FLAME = ["...#...", "..##...", "..###..", ".#####.", "#######", "#######", ".#####."]

def streak_card(t, d):
    W, H = 880, 128
    css = ('.n { animation: rise .5s steps(4, end) both; } .n2 { animation-delay: .15s; } .n3 { animation-delay: .3s; }'
           '@keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }'
           '.fl { animation: fl 1s steps(1, end) infinite; } @keyframes fl { 0%,49% { transform: translateY(0); } 50%,100% { transform: translateY(-3px); } }')
    o = [head(W, H, 'GitHub streak', css), panel(0, 0, W, H, 4, t['raised'], t['fg'])]
    cols = [(d['contribs'], 'Contributions (1 year)'), (d['current'], 'Current streak (days)'), (d['longest'], 'Longest streak (days)')]
    cw = (W - 8) // 3
    for i, (n, lab) in enumerate(cols):
        cx = 4 + i * cw
        if i:
            o.append(f'<rect x="{cx}" y="24" width="4" height="{H-48}" fill="{t["line"]}"/>')
        num = str(n)
        nw = text_w(num, 6)
        x = cx + (cw - nw) // 2
        col = t['accent'] if i == 1 else t['fg']
        o.append(f'<g class="n n{i+1}">{ptext(num, x, 30, 6, col)}</g>')
        if i == 1:
            o.append(f'<g class="fl">{runs(FLAME, {"#": t["fill"]}, 3, x - 34, 36)}</g>')
        o.append(ptext(lab, cx + (cw - text_w(lab, 2)) // 2, 90, 2, t['muted']))
    return ''.join(o) + '</svg>'

def overview_card(t, d):
    W, H = 432, 176
    o = [head(W, H, 'GitHub stats'), panel(0, 0, W, H, 4, t['raised'], t['fg'])]
    o.append(ptext('>', 24, 20, 3, t['accent']) + ptext('Stats', 52, 20, 3, t['fg']))
    rows = [('Contributions (1 year)', d['contribs']), ('Repositories', d['repos']), ('Stars earned', d['stars']), ('Followers', d['followers'])]
    for i, (lab, v) in enumerate(rows):
        y = 62 + i * 26
        o.append(ptext(lab, 24, y, 2, t['muted']))
        vs = str(v)
        o.append(ptext(vs, W - 24 - text_w(vs, 2), y, 2, t['fg']))
        o.append(f'<rect x="24" y="{y+18}" width="{W-48}" height="2" fill="{t["line"]}" opacity=".6"/>')
    return ''.join(o) + '</svg>'

def langs_card(t, d):
    W, H = 432, 176
    css = '.b { animation: grow .6s steps(6, end) both; transform-box: fill-box; transform-origin: 0 50%; } @keyframes grow { from { transform: scaleX(0); } to { transform: none; } }'
    o = [head(W, H, 'Top languages', css), panel(0, 0, W, H, 4, t['raised'], t['fg'])]
    o.append(ptext('>', 24, 20, 3, t['accent']) + ptext('Top languages', 52, 20, 3, t['fg']))
    bx, bw = 156, 180
    for i, (name, pct) in enumerate(d['langs'][:5]):
        y = 60 + i * 22
        o.append(ptext(name, 24, y, 2, t['fg']))
        o.append(f'<rect x="{bx}" y="{y+2}" width="{bw}" height="10" fill="{t["line"]}"/>')
        fw = max(4, round(bw * pct / 100 / 4) * 4)
        o.append(f'<rect class="b" x="{bx}" y="{y+2}" width="{fw}" height="10" fill="{t["fill"]}"/>')
        ps = f'{pct}%'
        o.append(ptext(ps, W - 24 - text_w(ps, 2), y, 2, t['muted']))
    return ''.join(o) + '</svg>'

def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    if '--sample' in sys.argv:
        d = SAMPLE
    else:
        d = fetch(os.environ.get('GITHUB_USER') or os.environ['GITHUB_REPOSITORY_OWNER'], os.environ['GITHUB_TOKEN'])
    for name, t in THEMES.items():
        for fn, f in (('streak', streak_card), ('overview', overview_card), ('langs', langs_card)):
            with open(os.path.join(out, f'stats-{fn}-{name}.svg'), 'w') as fh:
                fh.write(f(t, d))
    print('stats ok')

if __name__ == '__main__':
    main()

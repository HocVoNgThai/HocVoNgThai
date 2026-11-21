"""Builds the profile SVGs: the live bento card and the link buttons, each in light and dark.

usage:
  python3 tools/gen_profile.py static assets         # link buttons (committed)
  python3 tools/gen_profile.py live dist [--sample]  # bento-dark.svg / bento-light.svg from GitHub data
env (live): GITHUB_TOKEN, GITHUB_USER
needs: pip install fonttools brotli  (text measuring)
"""
import base64, datetime, json, os, random, sys, urllib.request
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')

# ---------------------------------------------------------------- profile content
NAME = 'Thai Hoc'
ROLE = 'Security Engineer'
TEAM = 'SECURITY R&D · SNP'
NOW = ('Security R&D', 'at SNP')
AREAS = ['Security R&D', 'Security Solution', 'AI Security', 'DevOps']
ROLES = ['Security Architect', 'Security Solution']
ABOUT = ['Security Engineer in the Security R&D team at SNP.',
         'I design security architecture and build security solutions,',
         'with a growing focus on AI security and DevOps.']
LINKS = [('email', 'Email'), ('linkedin', 'LinkedIn'), ('facebook', 'Facebook')]

# ---------------------------------------------------------------- fonts (OFL, subset to ASCII + a few symbols)
FACES = [('PG', 500, 'SpaceGrotesk-500.woff2'), ('PG', 700, 'SpaceGrotesk-700.woff2'),
         ('PM', 400, 'JetBrainsMono-400.woff2'), ('PM', 700, 'JetBrainsMono-700.woff2'),
         ('PS', 400, 'Sora-400.woff2'), ('PS', 600, 'Sora-600.woff2')]

def _face(fam, weight, fn):
    with open(os.path.join(FONT_DIR, fn), 'rb') as f:
        b = base64.b64encode(f.read()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff2;base64,{b}) format('woff2')}}"

def fonts(*faces):
    return ''.join(_face(*f) for f in FACES if f[0] in faces or (f[0], f[1]) in faces)

BASE_CSS = ("text{font-family:'PG',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
            ".m,.m text{font-family:'PM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
            ".s,.s text{font-family:'PS',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}")
REDUCE = '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'

_metrics = {}
def width(text, fn, size):
    """Advance width of text in px (no kerning; close enough for layout)."""
    if fn not in _metrics:
        f = TTFont(os.path.join(FONT_DIR, fn))
        _metrics[fn] = (f.getBestCmap(), f['hmtx'].metrics, f['head'].unitsPerEm)
    cmap, hmtx, upm = _metrics[fn]
    return sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / upm

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def svg(w, h, title, css, body, font_css):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
            f'<style>{font_css}{BASE_CSS}{css}{REDUCE}</style>{body}</svg>')

# ---------------------------------------------------------------- themes
THEMES = {
    'dark': dict(card='#161b22', line='#30363d', fg='#e6edf3', muted='#9198a1', chip='#0d1117', track='#21262d',
                 heat=['#1b2230', '#0e3a75', '#1c5fb8', '#3b82f6', '#93c5fd'], live='#3fb950', glow='#4f8cff'),
    'light': dict(card='#f6f8fa', line='#d1d9e0', fg='#1f2328', muted='#59636e', chip='#ffffff', track='#e6eaef',
                  heat=['#e6eaef', '#c6dbff', '#8fb8ff', '#4f8cff', '#1d4ed8'], live='#1a7f37', glow='#1d4ed8'),
}
ACC = ['#4f8cff', '#ffb347', '#2bb9a0', '#a78bfa']

# ---------------------------------------------------------------- bento (live)
def bento(t, d):
    W, H = 1000, 630
    css = ('.cd{animation:cd .6s ease-out both}@keyframes cd{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}'
           '.ce{animation:ce .35s ease-out both}@keyframes ce{from{opacity:0}to{opacity:1}}'
           '.pg{transform-box:fill-box;transform-origin:center;animation:pg 1.8s ease-out infinite}'
           '@keyframes pg{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3);opacity:0}}'
           '.ty{transform-box:fill-box;transform-origin:left center}'
           '.fk{animation:fk .7s linear both}'
           '@keyframes fk{0%{opacity:.15}12%{opacity:1}22%{opacity:.3}34%{opacity:1}46%{opacity:.55}58%,100%{opacity:1}}'
           '.cu{animation:cu 1s steps(1,end) infinite}@keyframes cu{0%,50%{opacity:1}51%,100%{opacity:0}}'
           '.gl{animation:gl 3.2s ease-in-out infinite}@keyframes gl{0%,100%{stroke-opacity:.15}50%{stroke-opacity:.8}}'
           '.sc{animation:sc 4.5s cubic-bezier(.5,0,.5,1) 3.5s infinite both}'
           '@keyframes sc{0%{transform:translateX(-160px);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateX(1000px);opacity:0}}')
    card = lambda x, y, w, h: f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="18" fill="{t["card"]}" stroke="{t["line"]}"/>'
    label = lambda x, y, s: f'<text x="{x}" y="{y}" class="m" font-size="11" letter-spacing="2" fill="{t["muted"]}">{esc(s)}</text>'
    g = lambda i: f'<g class="cd" style="animation-delay:{i * .12:.2f}s">'
    o = [f'<defs><linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ACC[0]}"/><stop offset="1" stop-color="{ACC[2]}"/></linearGradient>'
         f'<linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0"/><stop offset=".5" stop-color="{t["glow"]}" stop-opacity=".14"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="ac"><rect x="0" y="460" width="1000" height="170" rx="18"/></clipPath>']

    # typing clips for the about panel
    ax, ay, lh, fs = 32, 538, 30, 19
    t0 = 1.0
    timings = []
    for i, line in enumerate(ABOUT):
        w = width(line, 'Sora-400.woff2', fs) + 4
        dur = max(.6, len(line) * .028)
        timings.append((t0, dur, w))
        o.append(f'<clipPath id="tc{i}"><rect class="ty" x="{ax}" y="{ay + i * lh - fs}" width="{w:.0f}" height="{fs + 8}" '
                 f'style="animation:ty{i} {dur:.2f}s steps({len(line)},end) {t0:.2f}s both"/></clipPath>')
        css += f'@keyframes ty{i}{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}'
        t0 += dur + .15
    o.append('</defs>')

    # A identity
    o += [g(0), card(0, 0, 400, 200),
          f'<circle cx="86" cy="100" r="50" fill="url(#mg)"/><text x="86" y="114" text-anchor="middle" font-size="38" font-weight="700" fill="#fff">TH</text>',
          f'<text x="158" y="94" font-size="40" font-weight="700" letter-spacing="-1" fill="{t["fg"]}">{esc(NAME)}</text>',
          f'<text x="160" y="124" font-size="17" font-weight="500" fill="{t["muted"]}">{esc(ROLE)}</text>',
          f'<text x="160" y="150" class="m" font-size="12" letter-spacing="1" fill="{t["muted"]}">{esc(TEAM)}</text></g>']
    # B now
    o += [g(1), card(420, 0, 220, 200), label(442, 38, 'NOW'),
          f'<circle cx="614" cy="34" r="5" fill="{t["live"]}"/><circle class="pg" cx="614" cy="34" r="5" fill="none" stroke="{t["live"]}" stroke-width="2"/>',
          f'<text x="442" y="112" font-size="26" font-weight="700" letter-spacing="-.5" fill="{t["fg"]}">{esc(NOW[0])}</text>',
          f'<text x="442" y="142" font-size="16" font-weight="500" fill="{t["muted"]}">{esc(NOW[1])}</text></g>']
    # C focus ring
    r = 46; C = 2 * 3.14159265 * r; cx, cy = 732, 112
    o += [g(2), card(660, 0, 340, 200), label(682, 38, 'FOCUS'),
          f'<g transform="translate({cx} {cy}) rotate(-90)" fill="none" stroke-width="14"><circle r="{r}" stroke="{t["track"]}"/>']
    share = 100 / len(AREAS)
    for i in range(len(AREAS)):
        seg = C * share / 100 - 4
        css += f'@keyframes s{i}{{from{{stroke-dashoffset:{seg:.1f}}}to{{stroke-dashoffset:0}}}}'
        o.append(f'<circle r="{r}" stroke="{ACC[i]}" stroke-dasharray="{seg:.1f} 1000" transform="rotate({i * share * 3.6:.1f})" '
                 f'style="animation:s{i} .7s cubic-bezier(.3,.1,.2,1) {.5 + i * .3:.2f}s both"/>')
    o.append('</g>')
    for i, name in enumerate(AREAS):
        yy = 72 + i * 28
        o.append(f'<rect x="808" y="{yy}" width="10" height="10" rx="3" fill="{ACC[i]}"/>'
                 f'<text x="828" y="{yy + 10}" font-size="15" font-weight="500" fill="{t["fg"]}">{esc(name)}</text>')
    o.append('</g>')
    # D roles
    o += [g(3), card(0, 220, 320, 220), label(22, 258, 'ROLE')]
    for i, s in enumerate(ROLES):
        yy = 284 + i * 70
        o.append(f'<rect x="22" y="{yy}" width="276" height="56" rx="12" fill="{t["chip"]}" stroke="{t["line"]}"/>'
                 f'<rect x="22" y="{yy + 14}" width="4" height="28" rx="2" fill="{ACC[i]}"/>'
                 f'<text x="42" y="{yy + 35}" font-size="19" font-weight="700" fill="{t["fg"]}">{esc(s)}</text>')
    o.append('</g>')
    # E activity heatmap
    ncol = 46
    o += [g(4), card(340, 220, 660, 220), label(362, 258, f'ACTIVITY · LAST {ncol} WEEKS')]
    weeks = d['weeks'][-ncol:]
    peak = max([n for wk in weeks for _, n in wk] + [1])
    for ci, wk in enumerate(weeks):
        for ri, (date, n) in enumerate(wk):
            lvl = 0 if n == 0 else 1 + min(3, int(4 * n / (peak + 1)))
            o.append(f'<rect class="ce" style="animation-delay:{.6 + ci * .02:.3f}s" x="{362 + ci * 13.6:.1f}" y="{276 + ri * 15}" '
                     f'width="11" height="11" rx="2.5" fill="{t["heat"][lvl]}"><title>{date}: {n}</title></rect>')
    o.append(f'<text x="362" y="418" font-size="15" font-weight="700" fill="{t["fg"]}">{d["contribs"]:,} '
             f'<tspan font-weight="500" fill="{t["muted"]}">contributions in the last year</tspan></text>'
             f'<text x="978" y="418" text-anchor="end" font-size="15" font-weight="700" fill="{t["fg"]}">{d["longest"]} '
             f'<tspan font-weight="500" fill="{t["muted"]}">day best streak</tspan></text></g>')
    # F about panel: lines type in, flicker, then a blinking cursor
    o += [g(5), card(0, 460, 1000, 170),
          f'<rect class="gl" x="1" y="461" width="998" height="168" rx="17" fill="none" stroke="{t["glow"]}" stroke-width="1.5"/>',
          f'<g clip-path="url(#ac)"><rect class="sc" x="0" y="460" width="160" height="170" fill="url(#sg)"/></g>',
          label(32, 498, 'ABOUT'),
          f'<circle class="cu" cx="96" cy="494" r="3.5" fill="{t["live"]}"/>']
    for i, line in enumerate(ABOUT):
        start, dur, w = timings[i]
        o.append(f'<g clip-path="url(#tc{i})"><text class="s fk" style="animation-delay:{start + dur:.2f}s" x="{ax}" y="{ay + i * lh}" '
                 f'font-size="{fs}" fill="{t["fg"]}">{esc(line)}</text></g>')
    end, dur, w = timings[-1]
    o.append(f'<rect class="cu" x="{ax + w + 4:.0f}" y="{ay + (len(ABOUT) - 1) * lh - fs + 2}" width="10" height="{fs + 2}" rx="1.5" fill="{t["glow"]}"/>')
    o.append('</g>')
    return svg(W, H, f'{NAME}: Security Engineer, Security R&D at SNP. ' + ' '.join(ABOUT), css, ''.join(o), fonts('PG', 'PM', 'PS'))

# ---------------------------------------------------------------- buttons (static)
def button(t, label):
    fs = 14
    w = round(width(label, 'SpaceGrotesk-700.woff2', fs) + 54)
    h = 40
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>'
            f'<text x="16" y="25" class="m" font-size="13" font-weight="700" fill="{t["glow"]}">→</text>'
            f'<text x="36" y="25" font-size="{fs}" font-weight="700" fill="{t["fg"]}">{esc(label)}</text>')
    return svg(w, h, label, '', body, fonts(('PG', 700), ('PM', 700)))

# ---------------------------------------------------------------- data
QUERY = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""

def _get(url, token=None, data=None):
    h = {'User-Agent': 'profile-builder'}
    if token: h['Authorization'] = f'Bearer {token}'
    if data is not None: h['Content-Type'] = 'application/json'
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=30).read().decode()

def _longest(days):
    best = run = 0
    for _, n in sorted(days):
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    return best

def fetch(login, token):
    body = json.dumps({'query': QUERY, 'variables': {'login': login}}).encode()
    res = json.loads(_get('https://api.github.com/graphql', token, body))
    cal = res['data']['user']['contributionsCollection']['contributionCalendar']
    weeks = [[(d['date'], d['contributionCount']) for d in w['contributionDays']] for w in cal['weeks']]
    return dict(contribs=cal['totalContributions'], weeks=weeks, longest=_longest([x for w in weeks for x in w]))

def sample():
    rnd = random.Random(7)
    start = datetime.date.today() - datetime.timedelta(weeks=52)
    weeks = [[((start + datetime.timedelta(days=w * 7 + i)).isoformat(), rnd.choice([0, 0, 0, 1, 2, 3, 5, 8]))
              for i in range(7)] for w in range(53)]
    days = [x for w in weeks for x in w]
    return dict(contribs=sum(n for _, n in days), weeks=weeks, longest=_longest(days))

def main():
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    def write(name, s):
        with open(os.path.join(out, name), 'w') as f: f.write(s)
    if mode == 'static':
        for key, lab in LINKS:
            for name, t in THEMES.items(): write(f'btn-{key}-{name}.svg', button(t, lab))
    else:
        d = sample() if '--sample' in sys.argv else fetch(os.environ.get('GITHUB_USER') or os.environ['GITHUB_REPOSITORY_OWNER'], os.environ['GITHUB_TOKEN'])
        for name, t in THEMES.items(): write(f'bento-{name}.svg', bento(t, d))
    print(f'{mode} ok')

if __name__ == '__main__':
    main()

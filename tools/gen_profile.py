"""Builds the profile SVGs: the blueprint header, the link buttons and the live bento card.

usage:
  python3 tools/gen_profile.py static assets         # header + buttons (committed)
  python3 tools/gen_profile.py live dist [--sample]  # bento-dark.svg / bento-light.svg from GitHub data
env (live): GITHUB_TOKEN, GITHUB_USER
"""
import base64, datetime, json, os, random, re, sys, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- profile content
NAME = 'Thai Hoc'
ROLE = 'Security Engineer'
TEAM = 'SECURITY R&D · SNP'
TAGLINE = 'DEVSECOPS · AI × SECURITY · SECURITY ENGINEERING'
NOW = ['DevSecOps', 'pipelines']
NOW_SUB = '+ AI for security research'
FOCUS = [('DevSecOps', 45), ('AI × Sec', 35), ('Deploy & tune', 20)]
STACK = ['GitHub Actions', 'GitLab CI', 'Docker', 'Kubernetes', 'Terraform', 'Semgrep', 'Trivy', 'Python', 'LLMs']
RESEARCH = ['Secure CI/CD gates', 'LLMs for SecOps triage', 'Tuning security controls']
LINKS = [('email', 'EMAIL'), ('linkedin', 'LINKEDIN'), ('facebook', 'FACEBOOK')]

# ---------------------------------------------------------------- fonts (OFL, subset to ASCII + a few symbols)
def _font(fam, weight, fn):
    with open(os.path.join(HERE, 'fonts', fn), 'rb') as f:
        b = base64.b64encode(f.read()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff2;base64,{b}) format('woff2')}}"

FONTS = ''.join([_font('PG', 500, 'SpaceGrotesk-500.woff2'), _font('PG', 700, 'SpaceGrotesk-700.woff2'),
                 _font('PM', 400, 'JetBrainsMono-400.woff2'), _font('PM', 700, 'JetBrainsMono-700.woff2')])
BASE_CSS = ("text{font-family:'PG',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
            ".m,.m text{font-family:'PM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}")
REDUCE = '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'
MONO_W = 0.6  # JetBrains Mono advance width in em

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def svg(w, h, title, css, body, fonts=FONTS):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
            f'<style>{fonts}{BASE_CSS}{css}{REDUCE}</style>{body}</svg>')

# ---------------------------------------------------------------- blueprint header
BP_BG, BP_INK, BP_HOT = '#0b2c5f', '#ffffff', '#ffb347'

def header():
    W, H = 1000, 400
    css = ('.nd{animation:nd .5s ease-out both}'
           '@keyframes nd{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}'
           '.dr{stroke-dasharray:400;animation:dr 1.4s ease-out both}'
           '@keyframes dr{from{stroke-dashoffset:400}to{stroke-dashoffset:0}}'
           '.fl{stroke-dasharray:7 7;animation:fl .9s linear infinite}'
           '@keyframes fl{to{stroke-dashoffset:-14}}'
           '.pg{transform-box:fill-box;transform-origin:center;animation:pg 2s ease-out infinite}'
           '@keyframes pg{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3.2);opacity:0}}'
           '.bl{animation:bl 1.2s steps(1,end) infinite}@keyframes bl{0%,55%{opacity:1}56%,100%{opacity:.25}}')
    o = [f'<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#fff" stroke-opacity=".06"/></pattern>'
         f'<pattern id="G" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#g)"/><path d="M100 0H0V100" fill="none" stroke="#fff" stroke-opacity=".13"/></pattern>'
         f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{BP_INK}"/></marker>'
         f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{BP_HOT}"/></marker>'
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
         f'<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3"/></filter></defs>',
         f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{BP_BG}"/><rect width="{W}" height="{H}" fill="url(#G)"/>',
         f'<rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="#fff" stroke-opacity=".5"/>',
         f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="#fff" stroke-opacity=".2"/>',
         f'<text x="48" y="58" class="m" font-size="11.5" letter-spacing="2.5" fill="#cfe0ff">FIG. 1 · SECURE DELIVERY PIPELINE</text>']

    # pipeline: (label, sub, x, w)
    nodes = [('CODE', 'git push', 48, 104), ('CI BUILD', 'actions', 192, 118), ('SEC GATES', 'sast·sca·iac', 350, 150),
             ('REGISTRY', 'signed image', 540, 118), ('DEPLOY', 'k8s · policy', 698, 110), ('RUNTIME', 'detect', 848, 110)]
    y, h = 100, 56
    for i, (lab, sub, x, w) in enumerate(nodes):
        cx = x + w / 2
        o.append(f'<g class="nd" style="animation-delay:{.1 + i * .18:.2f}s">'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BP_BG}" stroke="{BP_INK}"/>'
                 f'<text x="{cx}" y="{y+25}" text-anchor="middle" class="m" font-size="12.5" font-weight="700" letter-spacing="1.5" fill="{BP_INK}">{esc(lab)}</text>'
                 f'<text x="{cx}" y="{y+43}" text-anchor="middle" class="m" font-size="10.5" fill="#cfe0ff" fill-opacity=".8">{esc(sub)}</text></g>')
        if i:
            px = nodes[i - 1][2] + nodes[i - 1][3]
            o.append(f'<path class="dr" style="animation-delay:{.25 + i * .18:.2f}s" d="M{px} {y+h/2}H{x-2}" fill="none" stroke="{BP_INK}" stroke-width="1.3" marker-end="url(#a)"/>')

    # AI engine below the pipeline
    ax, ay, aw, ah = 420, 214, 220, 56
    o.append(f'<g class="nd" style="animation-delay:1.3s"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="{BP_BG}" stroke="{BP_HOT}" stroke-width="1.5"/>'
             f'<text x="{ax+aw/2}" y="{ay+25}" text-anchor="middle" class="m" font-size="12.5" font-weight="700" letter-spacing="1.5" fill="{BP_HOT}">AI TRIAGE ENGINE</text>'
             f'<text x="{ax+aw/2}" y="{ay+43}" text-anchor="middle" class="m" font-size="10.5" fill="#ffd9a8">llm-assisted · ranks findings</text></g>')
    # findings flow into the engine, feedback flows back to code
    o.append(f'<g fill="none" stroke="{BP_HOT}" stroke-width="2">'
             f'<path class="fl" d="M455 {y+h}V{ay-2}" marker-end="url(#ah)"/>'
             f'<path class="fl" d="M903 {y+h}V{ay+ah/2}H{ax+aw+2}" marker-end="url(#ah)"/>'
             f'<path class="fl" d="M{ax} {ay+ah/2}H100V{y+h+2}" marker-end="url(#ah)"/></g>')
    o.append(f'<text x="112" y="{ay+ah/2-8}" class="m" font-size="10.5" fill="#ffd9a8">feedback → fix PR</text>')
    o.append(f'<text x="652" y="{ay+ah/2-8}" class="m" font-size="10.5" fill="#ffd9a8">runtime signals</text>')

    # a build travelling down the pipeline
    o.append(f'<circle r="5" fill="{BP_HOT}" filter="url(#glow)"><animateMotion dur="5s" repeatCount="indefinite" path="M100 {y+h/2}H903"/></circle>'
             f'<circle r="3" fill="#fff"><animateMotion dur="5s" repeatCount="indefinite" path="M100 {y+h/2}H903"/></circle>')

    # finding callout on the gates
    o.append(f'<circle cx="500" cy="{y}" r="5" fill="{BP_HOT}"/><circle class="pg" cx="500" cy="{y}" r="5" fill="none" stroke="{BP_HOT}" stroke-width="2"/>'
             f'<path d="M500 {y-5}V70H516" fill="none" stroke="{BP_HOT}"/>'
             f'<text x="522" y="74" class="m" font-size="11.5" font-weight="700" fill="{BP_HOT}">F-01 · secret in image layer</text>'
             f'<text x="522" y="90" class="m bl" font-size="10.5" fill="#ffd9a8">status: blocked at gate</text>')

    # name + title block
    o.append(f'<text x="46" y="334" font-size="52" font-weight="700" letter-spacing="-1.2" fill="{BP_INK}">{esc(NAME)}</text>'
             f'<text x="48" y="362" class="m" font-size="11" letter-spacing="2.6" fill="#cfe0ff">{esc(TAGLINE)}</text>')
    tx, ty, tw = 606, 296, 366
    o.append(f'<g class="m" font-size="10.5" fill="{BP_INK}">'
             f'<rect x="{tx}" y="{ty}" width="{tw}" height="72" fill="none" stroke="#fff" stroke-opacity=".7"/>'
             f'<path d="M{tx} {ty+24}H{tx+tw}M{tx} {ty+48}H{tx+tw}M{tx+86} {ty}V{ty+72}M{tx+262} {ty+24}V{ty+72}" stroke="#fff" stroke-opacity=".5"/>'
             f'<text x="{tx+8}" y="{ty+16}" fill-opacity=".6">PROJECT</text><text x="{tx+94}" y="{ty+16}">github.com/HocVoNgThai</text>'
             f'<text x="{tx+8}" y="{ty+40}" fill-opacity=".6">DRAWN BY</text><text x="{tx+94}" y="{ty+40}">{esc(NAME)}, {esc(ROLE)}</text>'
             f'<text x="{tx+270}" y="{ty+40}" fill-opacity=".6">SHEET 1/1</text>'
             f'<text x="{tx+8}" y="{ty+64}" fill-opacity=".6">DEPT</text><text x="{tx+94}" y="{ty+64}">Security R&amp;D, SNP</text>'
             f'<text x="{tx+270}" y="{ty+64}" fill-opacity=".6">REV {datetime.date.today():%Y.%m}</text></g>')
    o.append('</g>')
    return svg(W, H, f'{NAME}, {ROLE}: DevSecOps, AI for security, security engineering', css, ''.join(o))

def button(label):
    w = round(len(label) * 12 * MONO_W + len(label) * 2 + 58)
    h = 38
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" fill="{BP_BG}" stroke="#fff" stroke-opacity=".6"/>'
            f'<text x="16" y="24" class="m" font-size="13" font-weight="700" fill="{BP_HOT}">→</text>'
            f'<text x="36" y="24" class="m" font-size="12" font-weight="700" letter-spacing="2" fill="#fff">{esc(label)}</text>')
    return svg(w, h, label.title(), '', body, _font('PM', 700, 'JetBrainsMono-700.woff2'))

# ---------------------------------------------------------------- bento (live)
THEMES = {
    'dark': dict(card='#161b22', line='#30363d', fg='#e6edf3', muted='#9198a1', chip='#0d1117', track='#21262d',
                 heat=['#1b2230', '#0e3a75', '#1c5fb8', '#3b82f6', '#93c5fd'], live='#3fb950'),
    'light': dict(card='#f6f8fa', line='#d1d9e0', fg='#1f2328', muted='#59636e', chip='#ffffff', track='#e6eaef',
                  heat=['#e6eaef', '#c6dbff', '#8fb8ff', '#4f8cff', '#1d4ed8'], live='#1a7f37'),
}
ACC = ['#4f8cff', '#ffb347', '#2bb9a0']

def bento(t, d):
    W, H = 1000, 440
    css = ('.cd{animation:cd .6s ease-out both}@keyframes cd{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}'
           '.ce{animation:ce .35s ease-out both}@keyframes ce{from{opacity:0}to{opacity:1}}'
           '.pg{transform-box:fill-box;transform-origin:center;animation:pg 1.8s ease-out infinite}'
           '@keyframes pg{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3);opacity:0}}')
    card = lambda x, y, w, h: f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="18" fill="{t["card"]}" stroke="{t["line"]}"/>'
    label = lambda x, y, s: f'<text x="{x}" y="{y}" class="m" font-size="11" letter-spacing="2" fill="{t["muted"]}">{esc(s)}</text>'
    o = [f'<defs><linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ACC[0]}"/><stop offset="1" stop-color="{ACC[2]}"/></linearGradient></defs>']
    g = lambda i: f'<g class="cd" style="animation-delay:{i * .12:.2f}s">'

    # A identity
    o += [g(0), card(0, 0, 490, 200),
          f'<circle cx="86" cy="100" r="50" fill="url(#mg)"/><text x="86" y="114" text-anchor="middle" font-size="38" font-weight="700" fill="#fff">TH</text>',
          f'<text x="158" y="94" font-size="40" font-weight="700" letter-spacing="-1" fill="{t["fg"]}">{esc(NAME)}</text>',
          f'<text x="160" y="124" font-size="17" font-weight="500" fill="{t["muted"]}">{esc(ROLE)}</text>',
          f'<text x="160" y="150" class="m" font-size="12" letter-spacing="1" fill="{t["muted"]}">{esc(TEAM)}</text></g>']
    # B now
    o += [g(1), card(510, 0, 230, 200), label(532, 38, 'NOW'),
          f'<circle cx="714" cy="34" r="5" fill="{t["live"]}"/><circle class="pg" cx="714" cy="34" r="5" fill="none" stroke="{t["live"]}" stroke-width="2"/>',
          f'<text x="532" y="98" font-size="22" font-weight="700" fill="{t["fg"]}">{esc(NOW[0])}</text>',
          f'<text x="532" y="125" font-size="22" font-weight="700" fill="{t["fg"]}">{esc(NOW[1])}</text>',
          f'<text x="532" y="162" font-size="14" font-weight="500" fill="{t["muted"]}">{esc(NOW_SUB)}</text></g>']
    # C focus ring
    r = 44; C = 2 * 3.14159265 * r
    o += [g(2), card(760, 0, 240, 200), label(782, 38, 'FOCUS'),
          f'<g transform="translate(828 116) rotate(-90)" fill="none" stroke-width="14"><circle r="{r}" stroke="{t["track"]}"/>']
    acc = 0
    for i, (_, pct) in enumerate(FOCUS):
        seg = C * pct / 100 - 3
        css += f'@keyframes s{i}{{from{{stroke-dashoffset:{seg:.1f}}}to{{stroke-dashoffset:0}}}}'
        o.append(f'<circle r="{r}" stroke="{ACC[i]}" stroke-dasharray="{seg:.1f} 1000" transform="rotate({acc * 3.6:.1f})" '
                 f'style="animation:s{i} .9s cubic-bezier(.3,.1,.2,1) {.5 + i * .45:.2f}s both"/>')
        acc += pct
    o.append('</g>')
    for i, (name, _) in enumerate(FOCUS):
        o.append(f'<circle cx="886" cy="{92 + i * 24}" r="4" fill="{ACC[i]}"/><text x="896" y="{96 + i * 24}" class="m" font-size="11" fill="{t["fg"]}">{esc(name)}</text>')
    o.append('</g>')
    # D stack chips (flow layout)
    o += [g(3), card(0, 220, 320, 220), label(22, 258, 'STACK')]
    x, y = 22, 274
    for s in STACK:
        w = round(len(s) * 12 * MONO_W + 22)
        if x + w > 298: x, y = 22, y + 38
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="15" fill="{t["chip"]}" stroke="{t["line"]}"/>'
                 f'<text x="{x + w / 2}" y="{y + 19.5}" text-anchor="middle" class="m" font-size="12" fill="{t["fg"]}">{esc(s)}</text>')
        x += w + 8
    o.append('</g>')
    # E activity heatmap (last 26 weeks)
    o += [g(4), card(340, 220, 400, 220), label(362, 258, 'ACTIVITY · LAST 26 WEEKS')]
    weeks = d['weeks'][-26:]
    peak = max([n for wk in weeks for _, n in wk] + [1])
    for ci, wk in enumerate(weeks):
        for ri, (date, n) in enumerate(wk):
            lvl = 0 if n == 0 else 1 + min(3, int(4 * n / (peak + 1)))
            o.append(f'<rect class="ce" style="animation-delay:{.7 + ci * .035:.3f}s" x="{362 + ci * 13.7:.1f}" y="{276 + ri * 15}" '
                     f'width="11" height="11" rx="2.5" fill="{t["heat"][lvl]}"><title>{date}: {n}</title></rect>')
    o.append(f'<text x="362" y="418" font-size="15" font-weight="700" fill="{t["fg"]}">{d["contribs"]:,} '
             f'<tspan font-weight="500" fill="{t["muted"]}">contributions / yr</tspan></text>'
             f'<text x="718" y="418" text-anchor="end" font-size="15" font-weight="700" fill="{t["fg"]}">{d["longest"]} '
             f'<tspan font-weight="500" fill="{t["muted"]}">day best streak</tspan></text></g>')
    # F research tracks
    o += [g(5), card(760, 220, 240, 220), label(782, 258, 'RESEARCH')]
    for i, s in enumerate(RESEARCH):
        yy = 302 + i * 40
        o.append(f'<text x="782" y="{yy}" class="m" font-size="13" font-weight="700" fill="{ACC[i]}">▸</text>'
                 f'<text x="800" y="{yy}" font-size="15" font-weight="700" fill="{t["fg"]}">{esc(s)}</text>')
    o.append('</g>')
    return svg(W, H, f'{NAME}: profile overview', css, ''.join(o))

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
        write('header.svg', header())
        for key, lab in LINKS: write(f'btn-{key}.svg', button(lab))
    else:
        d = sample() if '--sample' in sys.argv else fetch(os.environ.get('GITHUB_USER') or os.environ['GITHUB_REPOSITORY_OWNER'], os.environ['GITHUB_TOKEN'])
        for name, t in THEMES.items(): write(f'bento-{name}.svg', bento(t, d))
    print(f'{mode} ok')

if __name__ == '__main__':
    main()

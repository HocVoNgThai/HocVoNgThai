"""5x7 pixel font with lowercase and full Vietnamese diacritics, plus small SVG helpers.

Coordinates: row 0 is the top of a capital letter, row 6 the baseline, rows 7-8 descenders.
Marks are stacked above the letter (up to 4 rows), so callers keep ~4*scale of headroom.
"""
import unicodedata

def _g(start, s): return (start, s.split(','))

CAPS = {
 'A':"01110,10001,10001,11111,10001,10001,10001",'B':"11110,10001,10001,11110,10001,10001,11110",
 'C':"01110,10001,10000,10000,10000,10001,01110",'D':"11110,10001,10001,10001,10001,10001,11110",
 'E':"11111,10000,10000,11110,10000,10000,11111",'F':"11111,10000,10000,11110,10000,10000,10000",
 'G':"01110,10001,10000,10111,10001,10001,01111",'H':"10001,10001,10001,11111,10001,10001,10001",
 'I':"01110,00100,00100,00100,00100,00100,01110",'J':"00111,00010,00010,00010,00010,10010,01100",
 'K':"10001,10010,10100,11000,10100,10010,10001",'L':"10000,10000,10000,10000,10000,10000,11111",
 'M':"10001,11011,10101,10101,10001,10001,10001",'N':"10001,11001,10101,10011,10001,10001,10001",
 'O':"01110,10001,10001,10001,10001,10001,01110",'P':"11110,10001,10001,11110,10000,10000,10000",
 'Q':"01110,10001,10001,10001,10101,10010,01101",'R':"11110,10001,10001,11110,10100,10010,10001",
 'S':"01111,10000,10000,01110,00001,00001,11110",'T':"11111,00100,00100,00100,00100,00100,00100",
 'U':"10001,10001,10001,10001,10001,10001,01110",'V':"10001,10001,10001,10001,10001,01010,00100",
 'W':"10001,10001,10001,10101,10101,10101,01010",'X':"10001,10001,01010,00100,01010,10001,10001",
 'Y':"10001,10001,01010,00100,00100,00100,00100",'Z':"11111,00001,00010,00100,01000,10000,11111",
 'Đ':"11110,01001,01001,11101,01001,01001,11110",
 'Ơ':"01111,10001,10001,10001,10001,10001,01110",'Ư':"10011,10011,10001,10001,10001,10001,01110",
}
DIGITS = {
 '0':"01110,10001,10011,10101,11001,10001,01110",'1':"00100,01100,00100,00100,00100,00100,01110",
 '2':"01110,10001,00001,00010,00100,01000,11111",'3':"11110,00001,00001,01110,00001,00001,11110",
 '4':"00010,00110,01010,10010,11111,00010,00010",'5':"11111,10000,11110,00001,00001,10001,01110",
 '6':"00110,01000,10000,11110,10001,10001,01110",'7':"11111,00001,00010,00100,01000,01000,01000",
 '8':"01110,10001,10001,01110,10001,10001,01110",'9':"01110,10001,10001,01111,00001,00010,01100",
 '&':"01100,10010,10100,01000,10101,10010,01101",'$':"00100,01111,10100,01110,00101,11110,00100",
 '>':"10000,01000,00100,00010,00100,01000,10000",'+':"00000,00100,00100,11111,00100,00100,00000",
 '%':"11001,11010,00010,00100,01000,01011,10011",'!':"00100,00100,00100,00100,00100,00000,00100",
 '?':"01110,10001,00001,00110,00100,00000,00100",'/':"00001,00010,00010,00100,01000,01000,10000",
 '(':"00010,00100,01000,01000,01000,00100,00010",')':"01000,00100,00010,00010,00010,00100,01000",
}
# lowercase: (first row, rows). x-height letters start at row 2, ascenders at 0, descenders run to row 8.
LOW = {
 'a':_g(2,"01110,00001,01111,10001,01111"),'b':_g(0,"10000,10000,10110,11001,10001,10001,11110"),
 'c':_g(2,"01110,10001,10000,10001,01110"),'d':_g(0,"00001,00001,01101,10011,10001,10001,01111"),
 'e':_g(2,"01110,10001,11111,10000,01110"),'f':_g(0,"00110,01001,01000,11100,01000,01000,01000"),
 'g':_g(2,"01111,10001,10001,01111,00001,10001,01110"),'h':_g(0,"10000,10000,10110,11001,10001,10001,10001"),
 'i':_g(0,"00100,00000,01100,00100,00100,00100,01110"),'ı':_g(2,"01100,00100,00100,00100,01110"),
 'j':_g(0,"00010,00000,00110,00010,00010,00010,00010,10010,01100"),'k':_g(0,"10000,10000,10010,10100,11000,10100,10010"),
 'l':_g(0,"01100,00100,00100,00100,00100,00100,01110"),'m':_g(2,"11010,10101,10101,10101,10101"),
 'n':_g(2,"10110,11001,10001,10001,10001"),'o':_g(2,"01110,10001,10001,10001,01110"),
 'p':_g(2,"11110,10001,10001,11110,10000,10000,10000"),'q':_g(2,"01111,10001,10001,01111,00001,00001,00001"),
 'r':_g(2,"10110,11001,10000,10000,10000"),'s':_g(2,"01111,10000,01110,00001,11110"),
 't':_g(1,"01000,11110,01000,01000,01001,00110"),'u':_g(2,"10001,10001,10001,10011,01101"),
 'v':_g(2,"10001,10001,10001,01010,00100"),'w':_g(2,"10001,10001,10101,10101,01010"),
 'x':_g(2,"10001,01010,00100,01010,10001"),'y':_g(2,"10001,10001,10001,01111,00001,10001,01110"),
 'z':_g(2,"11111,00010,00100,01000,11111"),
 'đ':_g(0,"00111,00001,01101,10011,10001,10001,01111"),
 'ơ':_g(2,"01111,10001,10001,10001,01110"),'ư':_g(2,"10011,10011,10010,10010,01101"),
}
PUNCT = {
 '.':(6,["1"]),',':(6,["1","1"]),"'":(0,["1","1"]),'-':(3,["111"]),':':(3,["1","0","0","1"]),
 '’':(0,["1","1"]),
}
# marks: (rows) each 5 wide, drawn 2 rows tall directly above the letter
MARKS = {
 '́':["00010","00100"],'̀':["01000","00100"],'̉':["01100","00110"],
 '̃':["01001","10110"],'̂':["00100","01010"],'̆':["01010","00100"],
}
NO_HORN = {'o': 'ơ', 'u': 'ư', 'O': 'Ơ', 'U': 'Ư'}

def _table(ch):
    if ch in CAPS: return (0, CAPS[ch].split(','))
    if ch in DIGITS: return (0, DIGITS[ch].split(','))
    if ch in LOW: return LOW[ch]
    if ch in PUNCT: return PUNCT[ch]
    raise KeyError(ch)

_cache = {}
def glyph(ch):
    """-> (set of (col,row), advance) with columns trimmed to start at 0."""
    if ch in _cache: return _cache[ch]
    if ch == ' ':
        _cache[ch] = (frozenset(), 3); return _cache[ch]
    nfd = unicodedata.normalize('NFD', ch)
    base, marks = nfd[0], set(nfd[1:])
    if ch in ('đ', 'Đ'): base, marks = ch, set()
    if '̛' in marks: base = NO_HORN[base]; marks.discard('̛')
    if base == 'i' and marks: base = 'ı'
    start, rows = _table(base)
    px = {(c, start + r) for r, row in enumerate(rows) for c, v in enumerate(row) if v == '1'}
    last = start + len(rows) - 1
    mod = [m for m in marks if m in ('̂', '̆')]
    tone = [m for m in marks if m in ('́', '̀', '̉', '̃')]
    if mod:
        for r, row in enumerate(MARKS[mod[0]]):
            px |= {(c, start - 2 + r) for c, v in enumerate(row) if v == '1'}
    if tone:
        top = start - (4 if mod else 2)
        for r, row in enumerate(MARKS[tone[0]]):
            px |= {(c, top + r) for c, v in enumerate(row) if v == '1'}
    if '̣' in marks:
        px.add((2, last + 2))
    cols = [c for c, _ in px]
    lo, hi = min(cols), max(cols)
    out = frozenset((c - lo, r) for c, r in px)
    _cache[ch] = (out, hi - lo + 2)
    return _cache[ch]

def text_w(txt, s):
    return (sum(glyph(c)[1] for c in txt) - 1) * s

def ptext(txt, x, y, s, color):
    """Text as one <path>; y is the top of a capital letter."""
    rows = {}
    cx = 0
    for ch in txt:
        px, adv = glyph(ch)
        for c, r in px: rows.setdefault(r, set()).add(cx + c)
        cx += adv
    d = []
    for r, cols in rows.items():
        cs = sorted(cols); i = 0
        while i < len(cs):
            j = i
            while j + 1 < len(cs) and cs[j+1] == cs[j] + 1: j += 1
            d.append(f'M{x+cs[i]*s} {y+r*s}h{(cs[j]-cs[i]+1)*s}v{s}h-{(cs[j]-cs[i]+1)*s}z')
            i = j + 1
    return f'<path fill="{color}" d="{"".join(d)}"/>'

def wrap(txt, max_w, s):
    lines, cur = [], ''
    for w in txt.split(' '):
        t = (cur + ' ' + w) if cur else w
        if text_w(t, s) <= max_w or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def runs(rows, colors, s, ox=0, oy=0):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            if c in colors:
                x2 = x
                while x2 < len(row) and row[x2] == c: x2 += 1
                out.append(f'<rect x="{ox+x*s}" y="{oy+y*s}" width="{(x2-x)*s}" height="{s}" fill="{colors[c]}"/>')
                x = x2
            else: x += 1
    return ''.join(out)

def panel(x, y, w, h, px, fill, border):
    return (f'<rect x="{x+px}" y="{y}" width="{w-2*px}" height="{h}" fill="{border}"/>'
            f'<rect x="{x}" y="{y+px}" width="{w}" height="{h-2*px}" fill="{border}"/>'
            f'<rect x="{x+2*px}" y="{y+px}" width="{w-4*px}" height="{h-2*px}" fill="{fill}"/>'
            f'<rect x="{x+px}" y="{y+2*px}" width="{w-2*px}" height="{h-4*px}" fill="{fill}"/>')

THEMES = {
 'light': dict(bg='#c8cbcd', raised='#dcdee0', line='#8d9296', fg='#0d1012', muted='#3d4348',
               fill='#f9d630', accent='#7d2600', shadow='#8d9296', sky='#b5b8ba'),
 'dark':  dict(bg='#101214', raised='#181b1f', line='#2c3138', fg='#e8eaed', muted='#9aa1a8',
               fill='#ffb224', accent='#7cd4f5', shadow='#2c3138', sky='#1c2026'),
}
REDUCE = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

def head(w, h, title, css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{title}"><title>{title}</title>'
            f'<style>{css}{REDUCE}</style>')

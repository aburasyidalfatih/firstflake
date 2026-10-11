"""Builds familypack.html: the Junior Prospector Family Pack (16 pages, one <section class="page"> each).
Run:  python familypack/build.py   then   bash familypack/render.sh
"""
from pathlib import Path

HERE = Path(__file__).parent
pages = []  # (html, cover?)


def page(body, cover=False):
    pages.append((body, cover))


INK, RUST, SAGE, CREAM, TAN, LINE, GOLD, WATER = '#2b2118', '#a3562a', '#6f7a4c', '#f6efe2', '#efe4cf', '#d9c8ad', '#d4a020', '#a9c6cf'
GRAD = '<defs><radialGradient id="au" cx=".35" cy=".35"><stop offset="0" stop-color="#ffe58a"/><stop offset=".55" stop-color="#d4a020"/><stop offset="1" stop-color="#8a6410"/></radialGradient></defs>'


def svg(inner, w, vb='0 0 64 64', style=''):
    return f'<svg viewBox="{vb}" width="{w}" style="{style}" xmlns="http://www.w3.org/2000/svg">{GRAD}{inner}</svg>'


# ---------------------------------------------------------------- icons (64x64)
S = f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"'
ICON = {
    'pan': f'<ellipse cx="32" cy="36" rx="27" ry="13" fill="#2c5240" {S}/><ellipse cx="33" cy="37" rx="17" ry="7" fill="#1d1916"/><ellipse cx="38" cy="36" rx="3.2" ry="2" fill="url(#au)"/><ellipse cx="29" cy="38" rx="1.8" ry="1.2" fill="url(#au)"/><path d="M12 31 Q20 25 30 24" stroke="#3f6b55" stroke-width="2" fill="none"/>',
    'bucket': f'<path d="M14 22 L18 56 H46 L50 22 Z" fill="{WATER}" {S}/><ellipse cx="32" cy="22" rx="18" ry="5" fill="#d9e8ec" {S}/><path d="M14 22 Q32 -4 50 22" fill="none" {S}/>',
    'snuffer': f'<rect x="22" y="26" width="20" height="30" rx="8" fill="#e9eef0" {S}/><path d="M27 26 V20 H37 V26" fill="#cfd8dc" {S}/><path d="M32 20 V6 Q32 3 36 3" fill="none" {S}/>',
    'magnifier': f'<circle cx="26" cy="26" r="15" fill="#e8f2f5" {S}/><path d="M37 37 L55 55" stroke="{RUST}" stroke-width="7" stroke-linecap="round"/><path d="M19 20 Q22 15 28 15" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>',
    'hat': f'<ellipse cx="32" cy="42" rx="27" ry="8" fill="#c9a66b" {S}/><path d="M18 41 Q18 18 32 18 Q46 18 46 41" fill="#d9b97f" {S}/><path d="M19 35 H45" stroke="{RUST}" stroke-width="4"/>',
    'water': f'<rect x="21" y="16" width="22" height="42" rx="7" fill="#9fc9d6" {S}/><rect x="26" y="7" width="12" height="9" rx="2" fill="{RUST}" {S}/><path d="M21 30 H43" stroke="#fff" stroke-width="2" opacity=".7"/>',
    'snack': f'<path d="M32 20 C20 12 8 22 12 38 C15 50 24 58 32 54 C40 58 49 50 52 38 C56 22 44 12 32 20 Z" fill="#c8553d" {S}/><path d="M32 20 Q33 11 38 7" fill="none" {S}/><path d="M34 13 Q42 8 46 13 Q40 17 34 13 Z" fill="#7e9b4f" {S}/>',
    'magnet': f'<path d="M14 12 V34 A18 18 0 0 0 50 34 V12 H40 V34 A8 8 0 0 1 24 34 V12 Z" fill="#c8553d" {S}/><rect x="14" y="8" width="10" height="9" fill="#b9bec2" {S}/><rect x="40" y="8" width="10" height="9" fill="#b9bec2" {S}/>',
    'trowel': f'<path d="M30 6 L44 6 L46 30 L37 40 L28 30 Z" fill="#b9bec2" {S}/><rect x="33" y="40" width="8" height="18" rx="3" fill="{RUST}" {S}/>',
    'vial': f'<rect x="24" y="14" width="16" height="42" rx="7" fill="#eef5f7" {S}/><rect x="22" y="8" width="20" height="8" rx="2" fill="{SAGE}" {S}/><path d="M26 50 Q32 44 38 50 V52 Q32 56 26 52 Z" fill="url(#au)"/>',
    'vest': f'<path d="M20 8 L26 12 Q32 20 38 12 L44 8 L54 16 L50 58 H14 L10 16 Z" fill="#e8873a" {S}/><path d="M32 22 V58" {S}/><path d="M14 34 H50 M14 46 H50" stroke="{INK}" stroke-width="2"/>',
    'socks': f'<path d="M22 6 H36 V36 L50 44 Q56 50 50 56 Q46 60 38 56 L22 46 Z" fill="#c9d6a3" {S}/><path d="M22 14 H36" stroke="{RUST}" stroke-width="4"/>',
    'whistle': f'<path d="M10 28 H40 A14 14 0 1 1 26 42 H10 Z" fill="#f2c94c" {S}/><circle cx="40" cy="42" r="5" fill="#fff" {S}/><path d="M52 18 Q58 10 54 4" fill="none" stroke="{INK}" stroke-width="2"/>',
    'sun': f'<circle cx="32" cy="32" r="12" fill="#f2c94c" {S}/>' + ''.join(f'<path d="M32 6 V13" {S} transform="rotate({a} 32 32)"/>' for a in range(0, 360, 45)),
    'cloud': f'<path d="M16 46 A10 10 0 0 1 18 26 A14 14 0 0 1 44 22 A11 11 0 0 1 50 46 Z" fill="#e8edf0" {S}/>',
    'rain': f'<path d="M16 36 A10 10 0 0 1 18 16 A14 14 0 0 1 44 12 A11 11 0 0 1 50 36 Z" fill="#cdd6dc" {S}/><path d="M22 44 L19 52 M32 44 L29 56 M42 44 L39 52" stroke="#4d8ea3" stroke-width="3" stroke-linecap="round"/>',
    'wind': f'<path d="M8 24 H40 A7 7 0 1 0 33 17 M8 34 H50 A7 7 0 1 1 43 41 M8 44 H30" fill="none" {S}/>',
    'snow': ''.join(f'<path d="M32 10 V54" {S} transform="rotate({a} 32 32)"/>' for a in (0, 60, 120)) + ''.join(f'<path d="M26 16 L32 22 L38 16" fill="none" {S} transform="rotate({a} 32 32)"/>' for a in range(0, 360, 60)),
}


def face(kind):
    eyes = {'happy': '<circle cx="23" cy="27" r="3"/><circle cx="41" cy="27" r="3"/>',
            'wow': '<path d="M23 21 L25 26 L30 27 L25 29 L23 34 L21 29 L16 27 L21 26 Z"/><path d="M41 21 L43 26 L48 27 L43 29 L41 34 L39 29 L34 27 L39 26 Z"/>',
            'okay': '<circle cx="23" cy="27" r="3"/><circle cx="41" cy="27" r="3"/>',
            'tired': '<path d="M18 28 Q23 24 28 28 M36 28 Q41 24 46 28" fill="none" stroke="#2b2118" stroke-width="2.4"/>',
            'cold': '<circle cx="23" cy="27" r="3"/><circle cx="41" cy="27" r="3"/>'}[kind]
    mouth = {'happy': '<path d="M20 38 Q32 50 44 38" fill="none" stroke="#2b2118" stroke-width="2.6" stroke-linecap="round"/>',
             'wow': '<ellipse cx="32" cy="43" rx="6" ry="7" fill="#7f4019"/>',
             'okay': '<path d="M22 42 H42" stroke="#2b2118" stroke-width="2.6" stroke-linecap="round"/>',
             'tired': '<path d="M24 44 Q32 38 40 44" fill="none" stroke="#2b2118" stroke-width="2.6" stroke-linecap="round"/>',
             'cold': '<path d="M20 42 L24 39 L28 42 L32 39 L36 42 L40 39 L44 42" fill="none" stroke="#2b2118" stroke-width="2.2"/>'}[kind]
    fill = '#cfe3ea' if kind == 'cold' else '#f6d58a'
    return f'<circle cx="32" cy="32" r="27" fill="{fill}" {S}/><g fill="#2b2118">{eyes}</g>{mouth}'


def icon(name, w='0.8in'):
    return svg(ICON[name] if name in ICON else face(name), w)


def lines(n):
    return '<div class="lines">' + '<div class="line"></div>' * n + '</div>'


def josie(t): return f'<div class="josie"><b>Josie says</b>{t}</div>'
def ezra(t):  return f'<div class="ezra"><b>Grandpa Ezra says:</b> <span>"{t}"</span></div>'
def grown(t): return f'<div class="grown"><b>Grown-up note</b> &nbsp;{t}</div>'


def done(t):
    return f'<div class="badge-done"><span class="tick"></span>{t}</div>'


def kicker(t): return f'<p class="kicker">{t}</p>'


# ---------------------------------------------------------------- badges
BADGES = [
    ('Tub Champ', 'Trip 1', f'<rect x="12" y="30" width="40" height="18" rx="6" fill="{WATER}" stroke="{INK}" stroke-width="2.4"/><path d="M12 36 Q22 32 32 36 T52 36" stroke="#fff" stroke-width="2" fill="none"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#8d9599" stroke="{INK}" stroke-width="1"/>' for x, y in ((22, 42), (30, 44), (38, 41), (44, 44)))),
    ('River Reader', 'Trip 2', f'<path d="M8 46 C22 46 20 20 34 20 S46 40 58 32" stroke="{WATER}" stroke-width="10" fill="none" stroke-linecap="round"/><circle cx="30" cy="27" r="3" fill="url(#au)"/><circle cx="36" cy="25" r="2.4" fill="url(#au)"/>'),
    ('Bedrock Explorer', 'Trip 3', f'<path d="M8 50 L14 28 L30 22 L50 26 L58 50 Z" fill="#9e9a92" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/><path d="M30 22 L28 34 L33 42 L31 50" stroke="{INK}" stroke-width="2.4" fill="none"/><circle cx="31" cy="46" r="2.6" fill="url(#au)"/>'),
    ('Dirt Mover', 'Trip 4', ICON['bucket']),
    ('Black Sand Detective', 'Trip 5', ICON['magnifier'].replace('#e8f2f5', '#3a332d')),
    ('Sample Scientist', 'Trip 6', f'<rect x="12" y="38" width="9" height="14" fill="{SAGE}" stroke="{INK}" stroke-width="2"/><rect x="27" y="28" width="9" height="24" fill="{RUST}" stroke="{INK}" stroke-width="2"/><rect x="42" y="16" width="9" height="36" fill="{GOLD}" stroke="{INK}" stroke-width="2"/><path d="M8 52 H56" stroke="{INK}" stroke-width="2.4"/>'),
    ('First Flake Finder', 'Trip 7', f'<path d="M20 34 C20 22 34 16 44 24 C52 30 46 46 34 46 C26 48 20 42 20 34 Z" fill="url(#au)" stroke="#8a6410" stroke-width="2"/><path d="M50 10 L52 16 L58 18 L52 20 L50 26 L48 20 L42 18 L48 16 Z" fill="{GOLD}"/><path d="M14 44 L15 47 L18 48 L15 49 L14 52 L13 49 L10 48 L13 47 Z" fill="{GOLD}"/>'),
]


def badge(name, trip, art, size='1.55in', colored=True):
    """A round badge: outer rust ring, cream disc, art in the middle, ribbon with the name."""
    ring = RUST if colored else '#fff'
    disc = CREAM if colored else '#fff'
    art_g = art if colored else f'<g opacity=".18">{art}</g>'
    return svg(f'''<circle cx="60" cy="56" r="52" fill="{ring}" stroke="{INK}" stroke-width="2"/>
<circle cx="60" cy="56" r="44" fill="{disc}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="{"0" if colored else "4 4"}"/>
<text x="60" y="26" text-anchor="middle" font-family="Fredoka" font-weight="600" font-size="10" fill="{RUST if colored else '#b8a688'}" letter-spacing="1.5">{trip.upper()}</text>
<g transform="translate(36 30) scale(.75)">{art_g}</g>
<path d="M8 92 H112 L104 104 L112 116 H8 L16 104 Z" fill="{GOLD if colored else '#fff'}" stroke="{INK}" stroke-width="2"/>
<text x="60" y="108" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="{12.5 if len(name) <= 12 else 11}" fill="{INK}"{' textLength="78" lengthAdjust="spacingAndGlyphs"' if len(name) > 12 else ''}>{name}</text>''', size, vb='0 0 120 120')


# ---------------------------------------------------------------- 1. cover
COVER_SCENE = svg(f'''<path d="M0 150 L70 70 L120 115 L190 40 L260 120 L320 75 L400 135 L460 95 L520 140 L520 300 L0 300Z" fill="#e3d3b4"/>
<path d="M0 175 L90 120 L150 150 L230 95 L300 160 L380 120 L450 165 L520 150 L520 300 L0 300Z" fill="#cdb48c"/>
<path d="M0 210 C120 185 170 235 260 220 S420 190 520 215 L520 300 L0 300Z" fill="#8fb3bf"/>
<path d="M0 225 C110 205 180 250 260 238 S410 210 520 232" stroke="#fff" stroke-width="2" fill="none" opacity=".6"/>
<path d="M30 300 C120 262 200 300 260 270 L520 300Z" fill="#b99a6b"/>
<circle cx="430" cy="62" r="24" fill="#f2c94c"/>
<g transform="translate(260 222)"><ellipse rx="110" ry="33" fill="#1f3a2c"/><ellipse rx="97" ry="27" fill="#2c5240"/>
<ellipse cx="8" cy="3" rx="66" ry="16" fill="#3a2f27"/><ellipse cx="14" cy="5" rx="46" ry="10" fill="#1d1916"/>
<ellipse cx="28" cy="3" rx="11" ry="6" fill="url(#au)"/><ellipse cx="4" cy="8" rx="4" ry="2.5" fill="url(#au)"/><ellipse cx="-10" cy="2" rx="2.5" ry="1.6" fill="url(#au)"/></g>
<g fill="#ffe58a"><path d="M290 176 L293 186 L303 189 L293 192 L290 202 L287 192 L277 189 L287 186 Z"/><path d="M250 186 L252 192 L258 194 L252 196 L250 202 L248 196 L242 194 L248 192 Z"/></g>''', '6.6in', vb='0 0 520 300', style='display:block;margin:0 auto;border-radius:16px')

page(f'''<div class="center" style="padding-top:.15in">
<p class="kicker" style="font-size:11pt">A First Flake companion for families</p>
<div style="font:700 50pt/1 Fredoka,sans-serif;margin:8px 0 2px">Junior Prospector</div>
<div style="font:600 28pt/1 Fredoka,sans-serif;color:var(--rust)">Family Pack</div>
<p class="rule" style="margin-top:12px;font-size:15pt">Trip logs, games, badges and a real certificate<br>for little gold hunters, ages 5 to 12</p>
<div style="margin:.25in 0 .2in">{COVER_SCENE}</div>
<div style="display:flex;justify-content:center;gap:10px;margin-top:.12in">{''.join(badge(n, t, a, '0.95in') for n, t, a in BADGES)}</div>
<div style="margin:.32in auto 0;width:5.6in;border:2px dashed var(--line);border-radius:14px;padding:12px 16px;font:600 15pt Fredoka,sans-serif;text-align:left">This pack belongs to: <span style="display:inline-block;width:3.2in;border-bottom:1.6px solid var(--ink)"></span></div>
<p class="rule" style="position:absolute;left:0;right:0;bottom:.08in;font-size:12pt">Read the river. It already knows where the gold is.</p></div>''', cover=True)

# ---------------------------------------------------------------- 2. grown-ups
page(kicker('Read this first') + '''<div style="font-size:11.4pt"><h1>A Note for Grown-Ups</h1>
<p class="rule">This pack runs alongside the First Flake workbook, one kid page for every grown-up trip.</p>
<h2>How it works</h2>
<ul><li><b>Do the workbook trips as usual.</b> Each trip has a matching kid page in here: a game, a hunt, or a job to do.</li>
<li><b>After every trip,</b> your junior prospector fills in a <b>Junior Trip Log</b> (page 12) and colors in a badge on the <b>Badge Tracker</b> (page 14).</li>
<li><b>Trip 7 ends with a certificate.</b> Page 16 has two: one for the day they find a flake, one for finishing all seven trips. Not every family finds gold on the first try, so every kid still goes home proud.</li></ul>
<h2>Which pages go with which trip</h2>
<table class="grid tight"><tr><th style="width:1.15in">Trip</th><th>Kid page</th></tr>
<tr><td>Before you go</td><td>Safety Pledge (3) · How Gold Got Into the River (4) · My Prospector Kit (5)</td></tr>
<tr><td>Trip 1</td><td>The BB Rescue Challenge (6)</td></tr>
<tr><td>Trip 2</td><td>Creek Scavenger Hunt Bingo (7)</td></tr>
<tr><td>Trip 3</td><td>Bedrock Explorer (8)</td></tr>
<tr><td>Trip 4</td><td>Dirt Mover Tally (9)</td></tr>
<tr><td>Trip 5</td><td>Black Sand Detective (10) · Is It Gold? Junior Edition (11)</td></tr>
<tr><td>Trip 6</td><td>My Treasure Map (13)</td></tr>
<tr><td>Trip 7</td><td>Official Certificates (16)</td></tr>
<tr><td>Every trip</td><td>Junior Trip Log (12) · Badge Tracker (14) · Cut-Out Badges (15)</td></tr></table>
<h2>Printing tips</h2>
<ul><li>Print the <b>Junior Trip Log</b> once per trip, and <b>My Treasure Map</b> as often as you like.</li>
<li>Print <b>page 16</b> on card stock, then cut along the dashed line to get two certificates.</li>
<li>Print <b>page 15</b> on full-sheet sticker paper, or on card stock and stick the badges on with tape.</li>
<li>Younger kids (5 to 7): you read and write, they draw, color and count. Older kids (8 to 12) can run their own logs.</li></ul>
<p style="font-size:9.6pt;color:var(--sage)">Josie and Grandpa Ezra are the workbook\'s fictional guides, written with help from AI. Everything they teach is real. For personal and household use: print what your family needs, but please don\'t resell or share the file. hello@firstflake.com</p></div>''')

# ---------------------------------------------------------------- 3. safety pledge
RULES = [('happy', 'I always pan with a grown-up, and I stay where my grown-up can see me.'),
         ('water', 'I never go into the water alone. I stay in water below my knees.'),
         ('vest', 'I wear a life jacket near deep or fast water.'),
         ('trowel', 'I don\'t climb on wet rocks or dig under creek banks.'),
         ('hat', 'I wear a hat, drink water, and take breaks when my hands get cold.'),
         ('whistle', 'If I get lost, I stay put and blow my whistle three times.'),
         ('bucket', 'I fill my holes and take my trash home. The creek is for everyone.')]
page(kicker('Before your first trip') + '<h1>The Junior Prospector<br>Safety Pledge</h1><p class="rule">Real prospectors stay safe, so they can keep exploring.</p>' +
     ''.join(f'<div style="display:flex;align-items:center;gap:14px;margin:7px 0;font-size:13.6pt">{icon(i, "0.62in")}<span class="tick"></span><span>{t}</span></div>' for i, t in RULES) +
     '<p class="big-rule" style="margin:14px 0 6px">I promise to follow these rules on every trip.</p>' +
     '<div class="cols2" style="margin-top:12px"><div><div class="lab">Junior prospector</div><div class="line"></div></div><div><div class="lab">Grown-up</div><div class="line"></div></div></div>'
     '<div style="width:3in"><div class="lab">Date</div><div class="line"></div></div>' +
     grown('This page is a conversation starter, not a substitute for supervision. Cold water and current are the real dangers, so keep small kids within arm\'s reach and in a life jacket near any moving water.'))

# ---------------------------------------------------------------- 4. how gold got into the river
def panel(n, art, text):
    return (f'<div style="border:1.6px solid var(--line);border-radius:14px;overflow:hidden;background:#fff">'
            f'<div style="background:{CREAM};padding:6px 10px;font:600 11pt Fredoka,sans-serif;color:var(--rust)">{n}</div>'
            f'{svg(art, "100%", vb="0 0 240 130", style="display:block")}'
            f'<div style="padding:7px 12px 10px;font-size:11.8pt;line-height:1.35">{text}</div></div>')


MTN = '<path d="M0 130 L70 30 L110 70 L150 20 L240 130 Z" fill="#cdb48c" stroke="#2b2118" stroke-width="2"/>'
P1 = MTN + '<path d="M120 60 L135 75 L128 90 L145 105" stroke="url(#au)" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M60 80 L75 92 L70 110" stroke="url(#au)" stroke-width="4" fill="none" stroke-linecap="round"/><rect width="240" height="130" fill="none"/>'
P2 = MTN + '<path d="M140 40 L130 62 L146 80 M80 60 L90 82" stroke="#2b2118" stroke-width="2.2" fill="none"/>' + ''.join(f'<path d="M{x} {y} l-4 10" stroke="#4d8ea3" stroke-width="2.6" stroke-linecap="round"/>' for x, y in ((40, 8), (70, 14), (100, 4), (130, 10), (165, 6), (200, 14), (225, 4), (55, 30), (185, 30))) + '<path d="M150 108 l10 0 l-4 8 z M100 112 l8 -2 l2 8 z" fill="#9e9a92" stroke="#2b2118"/>'
P3 = '<rect width="240" height="130" fill="#e8dcc4"/><path d="M0 50 C70 40 120 95 240 70 L240 120 C130 140 70 90 0 105 Z" fill="#8fb3bf"/><path d="M0 75 C70 66 120 115 240 92" stroke="#fff" stroke-width="2" stroke-dasharray="8 8" fill="none"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9e9a92" stroke="#2b2118" stroke-width="1.4"/>' for x, y, r in ((40, 70, 6), (90, 82, 8), (150, 98, 5), (200, 86, 7))) + '<circle cx="120" cy="92" r="3.4" fill="url(#au)"/><circle cx="62" cy="80" r="2.6" fill="url(#au)"/><path d="M190 30 l26 0 m-8 -6 l8 6 -8 6" stroke="#4d6b75" stroke-width="2.4" fill="none"/>'
P4 = '<rect width="240" height="44" fill="#a9c6cf"/><path d="M0 44 H240" stroke="#fff" stroke-width="2"/><rect y="44" width="240" height="64" fill="#cdb48c"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9e9a92" stroke="#2b2118" stroke-width="1.2"/>' for x, y, r in ((20, 56, 6), (60, 64, 9), (110, 54, 5), (150, 66, 8), (200, 58, 7), (35, 84, 5), (90, 88, 7), (175, 90, 6), (222, 84, 5))) + '<rect y="108" width="240" height="22" fill="#6e6a63"/><path d="M118 108 L124 122 L130 108" fill="#3d3a35"/><ellipse cx="124" cy="112" rx="5" ry="3" fill="url(#au)"/><ellipse cx="60" cy="105" rx="4" ry="2.4" fill="url(#au)"/><path d="M124 60 V96" stroke="#7f4019" stroke-width="2" stroke-dasharray="4 4"/><path d="M119 92 L124 100 L129 92" fill="none" stroke="#7f4019" stroke-width="2"/>'

SINK = [('Steel BB', 'sinks'), ('Dry leaf', 'floats'), ('Gold flake', 'sinks'), ('Wine cork', 'floats'), ('Pebble', 'sinks'), ('Twig', 'floats')]
page(kicker('Before your first trip · The science, kid-sized') + '<h1>How Gold Got Into the River</h1>' +
     '<div class="cols2" style="gap:14px">' +
     panel('1. Long, long ago', P1, 'Gold was locked inside rocks, high up in the mountains.') +
     panel('2. Rain, ice and time', P2, 'Rain, ice and roots cracked the rocks into smaller and smaller pieces.') +
     panel('3. Floods move everything', P3, 'Big floods carried sand, rocks and tiny bits of gold down into the creek.') +
     panel('4. Gold is SO heavy', P4, 'Gold is about 7 times heavier than sand, so it sinks to the bottom and gets stuck.') + '</div>' +
     '<h2>Heavy or light? Circle what happens in a tub of water.</h2>' +
     '<div class="cols2" style="gap:6px 22px">' + ''.join(f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding:4px 0;font-size:13pt"><span>{n}</span><span><span class="circ">SINKS</span><span class="circ">FLOATS</span></span></div>' for n, _ in SINK) + '</div>' +
     '<p style="transform:rotate(180deg);text-align:center;font-size:9.5pt;color:var(--sage);margin-top:10px">Answers: ' + ' · '.join(f'{n} {a}' for n, a in SINK) + '</p>')

# ---------------------------------------------------------------- 5. kit
KIT = [('pan', 'Gold pan'), ('bucket', 'Bucket'), ('trowel', 'Small scoop'), ('snuffer', 'Snuffer bottle'), ('vial', 'Gold vial'),
       ('magnifier', 'Magnifying glass'), ('magnet', 'Magnet'), ('hat', 'Hat'), ('water', 'Water bottle'), ('snack', 'Snack'),
       ('vest', 'Life jacket'), ('socks', 'Dry socks'), ('whistle', 'Whistle')]
page(kicker('Before your first trip · Packing day') + '<h1>My Prospector Kit</h1><p class="rule">Check off each thing as it goes in the bag.</p>' +
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">' +
     ''.join(f'<div style="border:1.4px solid var(--line);border-radius:14px;padding:8px 6px 8px;text-align:center">{icon(k, "0.66in")}<div style="display:flex;align-items:center;justify-content:center;font:600 11pt Fredoka,sans-serif;margin-top:4px"><span class="tick" style="width:17px;height:17px"></span>{t}</div></div>' for k, t in KIT) +
     '<div style="border:2px dashed var(--line);border-radius:14px;display:flex;align-items:center;justify-content:center;text-align:center;font:500 10.5pt Fredoka,sans-serif;color:var(--sage);padding:8px">Draw one more thing you want to bring</div></div>' +
     '<h2>Draw your very own gold pan</h2><div class="sketch" style="height:1.75in">Give it a name, too!</div>' +
     josie('My first gold pan was named Biscuit. Don\'t ask me why. I was seven, and it seemed like a great name at the time.'))

# ---------------------------------------------------------------- 6. BB rescue (Trip 1)
def bb_row(n):
    return '<div style="display:flex;gap:5px;align-items:center">' + ''.join('<span style="width:19px;height:19px;border-radius:50%;border:1.6px solid #2b2118;display:inline-block;background:#fff"></span>' for _ in range(n)) + '</div>'


STAR = '<span style="display:inline-block;width:22px">' + svg('<path d="M32 6 L39 24 L58 24 L43 36 L49 55 L32 44 L15 55 L21 36 L6 24 L25 24 Z" fill="#fff" stroke="#2b2118" stroke-width="3" stroke-linejoin="round"/>', '22px') + '</span>'
page(kicker('Trip 1 · The Tub Rehearsal') + '<h1>The BB Rescue Challenge</h1><p class="rule">Ten BBs are hiding in the gravel. Can you rescue all of them?</p>' +
     '<div class="box"><h3>How to play</h3><ol style="margin:0"><li>A grown-up mixes 10 steel BBs into a pan of gravel.</li><li>Shake the pan under the water, then tilt and wash, just like the workbook shows.</li><li>Count the BBs left in your pan, and color in that many circles.</li><li>Try to beat your own score every round!</li></ol></div>' +
     '<table class="grid"><tr><th style="width:1in">Round</th><th>Color one circle for every BB you saved</th><th style="width:.8in">Score</th><th style="width:1.15in">Stars</th></tr>' +
     ''.join(f'<tr><td><b style="font:600 13pt Fredoka,sans-serif">Round {r}</b></td><td>{bb_row(10)}</td><td style="font:600 13pt Fredoka;color:var(--sage)">&nbsp;&nbsp;/10</td><td>{STAR * 3}</td></tr>' for r in range(1, 6)) + '</table>' +
     '<p style="font-size:11pt;color:var(--sage)">Stars: 1 star for 6 or more, 2 stars for 8 or more, 3 stars for all 10!</p>' +
     '<div class="lab">My best score was ____ out of 10. My secret trick:</div>' + lines(2) +
     ezra('I lost three BBs my first try in 1939. Pa made me find every one before supper.') +
     grown('Use steel BBs, not lead, and count them in and out so none end up on the floor.') +
     done('I can rescue BBs. Color in my Tub Champ badge!'))

# ---------------------------------------------------------------- 7. bingo (Trip 2)
BINGO = [('An inside bend', 'Where the creek curves'), ('A gravel bar', 'A beach of little rocks'), ('A giant boulder', 'Bigger than you!'), ('Black sand', 'Dark streaks in the sand'),
         ('A crack in the rock', 'Gold hides in cracks'), ('A dragonfly', 'Or any flying bug'), ('A heart-shaped rock', 'Look closely!'), ('An animal track', 'Bird, deer or raccoon'),
         ('Moss', 'Soft and green'), ('A fish', 'Watch the quiet water'), ('A rock with stripes', 'Lines of color'), ('A waterfall', 'Even a tiny one'),
         ('A pine cone', 'Or any seed'), ('Something sparkly', 'Gold? Mica? Check it!'), ('Quiet, slow water', 'Gold likes lazy water'), ('Your choice!', 'Draw it here')]
page(kicker('Trip 2 · Read the River') + '<h1>Creek Scavenger Hunt Bingo</h1><p class="rule">Walk the creek with your grown-up before anyone digs. Mark every square you find.</p>' +
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);border:2px solid var(--rust);border-radius:14px;overflow:hidden">' +
     ''.join(f'<div style="height:1.38in;border-right:{"0" if i % 4 == 3 else "1.2px solid var(--line)"};border-bottom:{"0" if i >= 12 else "1.2px solid var(--line)"};padding:8px 9px;position:relative;background:{"#fbf6ec" if (i // 4 + i) % 2 else "#fff"}"><div style="font:600 12.2pt/1.15 Fredoka,sans-serif">{t}</div><div style="font-size:9.8pt;color:var(--sage);font-style:italic;margin-top:3px">{s}</div><span class="tick" style="position:absolute;right:8px;bottom:8px;margin:0;width:24px;height:24px"></span></div>' for i, (t, s) in enumerate(BINGO)) +
     '</div><p style="margin-top:10px;font-size:12pt"><b>BINGO!</b> Four in a row, across, down or corner to corner. <b>BLACKOUT!</b> Every single square.</p>' +
     josie('The first four squares are the best gold spots on any creek. If you found them, you just did what real prospectors do: look first, dig second.') +
     done('I read the river. Color in my River Reader badge!'))

# ---------------------------------------------------------------- 8. bedrock (Trip 3)
CRACK = svg('''<rect width="520" height="200" fill="#a9c6cf"/><rect y="60" width="520" height="70" fill="#cdb48c"/>''' +
            ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9e9a92" stroke="#2b2118" stroke-width="1.4"/>' for x, y, r in ((40, 80, 9), (110, 96, 12), (190, 78, 7), (300, 92, 11), (380, 76, 8), (460, 100, 10), (240, 112, 6))) +
            '''<path d="M0 130 L160 128 L200 132 L228 190 L262 132 L340 128 L520 134 L520 200 L0 200 Z" fill="#6e6a63" stroke="#2b2118" stroke-width="2"/>
<path d="M200 132 L228 190 L262 132 Z" fill="#3d3a35"/><ellipse cx="243" cy="176" rx="7" ry="4" fill="url(#au)"/><ellipse cx="236" cy="165" rx="4" ry="2.6" fill="url(#au)"/><ellipse cx="250" cy="158" rx="3" ry="2" fill="url(#au)"/>
<text x="20" y="40" font-family="Fredoka" font-weight="600" font-size="15" fill="#2b2118">WATER</text><text x="20" y="122" font-family="Fredoka" font-weight="600" font-size="15" fill="#2b2118">GRAVEL</text><text x="20" y="160" font-family="Fredoka" font-weight="600" font-size="15" fill="#fff">BEDROCK</text>
<path d="M300 162 Q330 150 340 168" stroke="#7f4019" stroke-width="2.4" fill="none"/><text x="345" y="174" font-family="Fredoka" font-weight="600" font-size="14" fill="#fff">gold sinks into the crack!</text>''', '100%', vb='0 0 520 200', style='display:block;border-radius:14px;border:1.4px solid #d9c8ad')
page(kicker('Trip 3 · Down to Bedrock') + '<h1>Bedrock Explorer</h1><p class="rule">Gold sinks until it can\'t. Then it hides in the cracks.</p>' + CRACK +
     '<h2>Find three cracks. Draw each one.</h2><div class="cols3">' +
     ''.join(f'<div><div class="sketch" style="height:1.75in">Crack {n}</div><div style="font:500 10.5pt Fredoka,sans-serif;margin-top:6px">Did it have gold? &nbsp;<span class="circ">YES</span><span class="circ">NO</span></div></div>' for n in (1, 2, 3)) +
     '</div><div class="lab" style="margin-top:14px">My guess: where would YOU hide if you were a flake of gold?</div>' + lines(2) +
     grown('Bedrock work means kneeling at the water\'s edge. Keep kids out of fast water and away from undercut banks while you clean cracks.') +
     done('I explored the bedrock. Color in my Bedrock Explorer badge!'))

# ---------------------------------------------------------------- 9. dirt mover (Trip 4)
BUCKET_OUT = svg(f'<path d="M14 22 L18 56 H46 L50 22 Z" fill="#fff" {S}/><ellipse cx="32" cy="22" rx="18" ry="5" fill="#fff" {S}/><path d="M14 22 Q32 -4 50 22" fill="none" {S}/>', '0.62in')
page(kicker('Trip 4 · Classify & Concentrate') + '<h1>Dirt Mover Tally</h1><p class="rule">Move more dirt, not faster hands. Every bucket counts!</p>' +
     '<h2>Color one bucket every time you fill one</h2>' +
     '<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:4px 2px;justify-items:center">' + BUCKET_OUT * 20 + '</div>' +
     '<h2>My bucket chart</h2><p style="font-size:11.5pt;margin-bottom:6px">Color one box for each bucket, one column for each trip.</p>' +
     '<div style="display:flex;gap:10px;align-items:flex-end;margin-left:.15in">' +
     '<div style="display:flex;flex-direction:column;justify-content:space-between;height:3.6in;font:500 9.5pt Fredoka;color:var(--sage);text-align:right;padding:2px 0">' + ''.join(f'<span>{n}</span>' for n in range(10, 0, -1)) + '</div>' +
     ''.join(f'<div style="text-align:center"><div style="display:grid;grid-template-rows:repeat(10,1fr);width:.9in;height:3.6in;border:1.4px solid var(--ink);border-radius:6px;overflow:hidden">' + '<div style="border-bottom:1px solid var(--line)"></div>' * 9 + f'<div></div></div><div class="cap">{t}</div></div>' for t in ('Trip 4', 'Trip 5', 'Trip 6', 'Trip 7')) +
     '</div>' + ezra('A strong back moves dirt. A smart prospector moves the right dirt.') +
     done('I moved a LOT of dirt. Color in my Dirt Mover badge!'))

# ---------------------------------------------------------------- 10. black sand (Trip 5)
TAILPAN = svg('''<ellipse cx="130" cy="62" rx="118" ry="52" fill="#2f2a26"/><ellipse cx="130" cy="62" rx="104" ry="44" fill="#47403a"/>
<path d="M60 70 C90 40 150 38 190 60 C160 52 110 56 70 78Z" fill="#141210"/>
<path d="M70 78 C80 70 92 66 104 66 C96 70 86 74 76 80Z" fill="#e2b33a"/>
<circle cx="80" cy="76" r="2" fill="#ffe58a"/><circle cx="90" cy="71" r="1.6" fill="#ffe58a"/>
<text x="150" y="38" font-family="Fredoka" font-size="12" fill="#efe4cf">black sand</text>
<text x="56" y="100" font-family="Fredoka" font-size="12" fill="#ffe58a">the yellow tail!</text>''', '3.1in', vb='0 0 260 120', style='display:block;margin:0 auto')
COLOR_PAN = svg('''<ellipse cx="130" cy="62" rx="118" ry="52" fill="#fff" stroke="#2b2118" stroke-width="2.4"/><ellipse cx="130" cy="62" rx="104" ry="44" fill="#fff" stroke="#2b2118" stroke-width="1.4"/>
<path d="M60 70 C90 40 150 38 190 60 C160 52 110 56 70 78Z" fill="#fff" stroke="#2b2118" stroke-width="1.6" stroke-dasharray="4 3"/>
<path d="M70 78 C80 70 92 66 104 66 C96 70 86 74 76 80Z" fill="#fff" stroke="#2b2118" stroke-width="1.6"/>''', '2.6in', vb='0 0 260 120', style='display:block;margin:0 auto')
page(kicker('Trip 5 · Black Sand School') + '<h1>Black Sand Detective</h1><p class="rule">Where there\'s black sand, gold isn\'t far.</p>' +
     '<div class="cols2" style="align-items:center"><div>' + TAILPAN + '<div class="cap">Swirl the pan. The black sand slides away and the gold shows its yellow tail.</div></div>' +
     '<div class="box" style="margin:0"><h3>The magnet experiment</h3><ol style="margin:0;font-size:12.2pt"><li>Put your magnet in a zip-top bag.</li><li>Wave it just above the dry black sand in your pan.</li><li>Watch the black sand jump up and stick!</li><li>Gold never sticks. Whatever stays behind is worth a closer look.</li></ol></div></div>' +
     '<h2>Did it stick to the magnet?</h2><table class="grid"><tr><th>What I tested</th><th style="width:1.4in">Stuck?</th></tr>' +
     ''.join(f'<tr><td>{t}</td><td><span class="circ">YES</span><span class="circ">NO</span></td></tr>' for t in ('Black sand', 'A paper clip', 'A coin', '', '')) + '</table>' +
     '<h2>Color the pan: black sand black, gold tail yellow</h2>' + COLOR_PAN +
     grown('Keep magnets away from kids who still put things in their mouths. Swallowed magnets are a medical emergency.') +
     done('I\'m a Black Sand Detective. Color in my badge!'))

# ---------------------------------------------------------------- 11. is it gold?
GOLD_A = '<path d="M20 34 C20 22 34 16 44 24 C52 30 46 46 34 46 C26 48 20 42 20 34 Z" fill="url(#au)" stroke="#8a6410" stroke-width="2"/>'
PYR_A = '<rect x="14" y="20" width="18" height="18" fill="#c9b46b" stroke="#6d5f2c" stroke-width="2"/><rect x="30" y="28" width="20" height="20" fill="#d8c47a" stroke="#6d5f2c" stroke-width="2"/><path d="M14 20 L20 14 H38 L32 20 M32 20 V38 M38 14 V24" stroke="#6d5f2c" stroke-width="1.6" fill="none"/><path d="M52 10 L54 14 L58 15 L54 16 L52 20 L50 16 L46 15 L50 14 Z" fill="#fff8c4" stroke="#6d5f2c" stroke-width=".8"/>'
MICA_A = '<path d="M14 40 L26 22 L46 26 L50 42 L30 48 Z" fill="#d9d4c4" stroke="#7a7466" stroke-width="2" opacity=".9"/><path d="M20 36 L30 26 L44 30" stroke="#fff" stroke-width="2" fill="none"/><path d="M50 12 L52 16 L56 17 L52 18 L50 22 L48 18 L44 17 L48 16 Z" fill="#fff" stroke="#7a7466" stroke-width=".8"/>'


def mineral(name, sub, art, facts, good):
    border = 'var(--gold)' if good else 'var(--line)'
    return (f'<div style="border:2.4px solid {border};border-radius:14px;padding:10px 12px;background:{"#fffaf0" if good else "#fff"}">'
            f'{svg(art, "0.95in", style="display:block;margin:0 auto")}<div class="center" style="font:700 15pt Fredoka,sans-serif">{name}</div>'
            f'<div class="center" style="font-style:italic;color:var(--sage);font-size:10.5pt;margin-bottom:6px">{sub}</div>'
            '<ul style="font-size:11.4pt;padding-left:18px;margin:0">' + ''.join(f'<li>{f}</li>' for f in facts) + '</ul></div>')


QUIZ = [('It stays bright yellow, even in the shade.', 'Gold'), ('It flashes in the sun and crumbles when you poke it.', 'Pyrite'),
        ('It washes right out of the pan with the light sand.', 'Mica'), ('It\'s shaped like tiny boxes.', 'Pyrite'),
        ('It bends instead of breaking.', 'Gold'), ('It goes dull and silvery when you turn it.', 'Mica')]
page(kicker('Trips 5 to 7 · Real or fake?') + '<h1>Is It Gold? Junior Edition</h1><p class="rule">Lots of things sparkle. Only one of them is gold.</p>' +
     '<div class="cols3">' +
     mineral('Gold', 'the real deal', GOLD_A, ['Bright yellow in sun AND shade', 'Soft: bends or dents when poked', 'Heavy: stays in the pan'], True) +
     mineral('Pyrite', '"fool\'s gold"', PYR_A, ['Brassy, flashes in the sun', 'Hard and crumbly', 'Often shaped like little cubes'], False) +
     mineral('Mica', 'the sparkly trickster', MICA_A, ['Thin, shiny flakes', 'Looks dull from the side', 'Light: floats away easily'], False) + '</div>' +
     '<h2>Who am I? Circle the answer.</h2>' +
     ''.join(f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding:5px 0;font-size:12.4pt"><span>{i}. {q}</span><span style="white-space:nowrap"><span class="circ">Gold</span><span class="circ">Pyrite</span><span class="circ">Mica</span></span></div>' for i, (q, _) in enumerate(QUIZ, 1)) +
     '<p style="transform:rotate(180deg);text-align:center;font-size:9.5pt;color:var(--sage);margin-top:8px">Answers: ' + ' · '.join(f'{i}. {a}' for i, (_, a) in enumerate(QUIZ, 1)) + '</p>' +
     grown('The poke test uses a pin. Let a grown-up hold the pin, and never let kids bite or taste anything from the pan.'))

# ---------------------------------------------------------------- 12. trip log
page(kicker('Every trip · Print one for each trip') + '<h1>My Junior Trip Log</h1>' +
     '<div class="cols2"><div><div class="lab">Trip number</div><div style="display:flex;gap:6px;margin-top:4px">' + ''.join(f'<span style="width:30px;height:30px;border:1.6px solid var(--rust);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font:600 13pt Fredoka;color:var(--rust)">{n}</span>' for n in range(1, 8)) + '</div></div>'
     '<div><div class="lab">Date</div><div class="line"></div></div></div>' +
     '<div class="lab">The creek I went to</div><div class="line"></div>' +
     '<div class="lab">The weather was <span style="font-weight:400;font-size:10.5pt;color:var(--sage)">(circle it)</span></div><div style="display:flex;gap:18px;margin-top:2px">' +
     ''.join(f'<div class="center">{icon(w, "0.62in")}<div class="cap" style="margin:0">{t}</div></div>' for w, t in (('sun', 'Sunny'), ('cloud', 'Cloudy'), ('rain', 'Rainy'), ('wind', 'Windy'), ('snow', 'Chilly'))) + '</div>' +
     '<div class="cols2" style="margin-top:6px"><div><div class="lab">Pans I washed</div><div class="line"></div></div><div><div class="lab">Gold specks I saw</div><div class="line"></div></div></div>' +
     '<div class="lab">Draw the best thing you found today</div><div class="sketch" style="height:2.3in">Gold, a cool rock, a frog, anything!</div>' +
     '<div class="lab">Today I felt <span style="font-weight:400;font-size:10.5pt;color:var(--sage)">(circle one)</span></div><div style="display:flex;gap:18px;margin-top:2px">' +
     ''.join(f'<div class="center">{icon(f, "0.6in")}<div class="cap" style="margin:0">{t}</div></div>' for f, t in (('happy', 'Happy'), ('wow', 'Amazed'), ('okay', 'Okay'), ('tired', 'Tired'), ('cold', 'Cold'))) + '</div>' +
     '<div class="cols2"><div><div class="lab">One thing I learned</div>' + lines(2) + '</div><div><div class="lab">Grown-up\'s initials</div><div class="line"></div><div class="lab">Badge earned?</div><div style="display:flex;align-items:center;font:600 12pt Fredoka"><span class="tick"></span>Yes! I colored it in.</div></div></div>')

# ---------------------------------------------------------------- 13. treasure map (Trip 6)
LEGEND = svg('''<g font-family="Fredoka" font-size="13" fill="#2b2118">
<path d="M10 14 L22 26 M22 14 L10 26" stroke="#a3562a" stroke-width="3.4" stroke-linecap="round"/><text x="34" y="25">My best spot</text>
<circle cx="16" cy="54" r="9" fill="#9e9a92" stroke="#2b2118" stroke-width="1.6"/><text x="34" y="59">Big boulder</text>
<path d="M6 92 Q16 74 26 92" stroke="#4d8ea3" stroke-width="3.4" fill="none"/><text x="34" y="93">Inside bend</text>
<path d="M8 124 L24 124 M16 116 L16 132" stroke="#6f7a4c" stroke-width="3" stroke-linecap="round"/><text x="34" y="128">Where we parked</text>
<path d="M6 162 C10 152 22 152 26 162" stroke="#2b2118" stroke-width="2" fill="#cdb48c"/><text x="34" y="163">Gravel bar</text>
<path d="M16 184 L24 200 L8 200 Z" fill="#6f7a4c" stroke="#2b2118" stroke-width="1.4"/><text x="34" y="198">Tree</text>
<circle cx="16" cy="226" r="6" fill="url(#au)"/><text x="34" y="231">Pan with gold</text>
<circle cx="16" cy="260" r="6" fill="#fff" stroke="#2b2118" stroke-width="1.6"/><text x="34" y="265">Empty pan</text></g>''', '1.6in', vb='0 0 150 280')
page(kicker('Trip 6 · The Sample Line') + '<h1>My Treasure Map</h1><p class="rule">One pan is a guess. Ten pans are a map.</p>' +
     '<div style="display:grid;grid-template-columns:1fr 1.75in;gap:14px">' +
     '<div style="height:6.1in;border:2.4px solid var(--rust);border-radius:14px;background:repeating-linear-gradient(0deg,#fff 0 23px,#f3ece0 23px 24px),#fff;position:relative">' +
     '<span style="position:absolute;top:8px;left:12px;font:600 11pt Fredoka;color:var(--sage)">Draw the creek, then mark every pan you tried</span>' +
     svg('<circle cx="40" cy="40" r="34" fill="#fff" stroke="#2b2118" stroke-width="2"/><path d="M40 12 L46 40 L40 68 L34 40 Z" fill="#a3562a"/><path d="M40 40 L46 40 L40 68 L34 40 Z" fill="#fff" stroke="#2b2118" stroke-width="1"/><text x="40" y="10" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="11" fill="#2b2118" dy="-1">N</text>', '0.8in', vb='0 -6 80 90', style='position:absolute;right:10px;bottom:10px') +
     '</div><div><div style="font:600 13pt Fredoka;color:var(--rust);margin-bottom:6px">Map key</div>' + LEGEND + '</div></div>' +
     '<div class="cols2" style="margin-top:6px"><div><div class="lab">Name of my secret spot</div><div class="line"></div></div><div><div class="lab">Pans with gold ____ out of ____</div><div class="line" style="border:0"></div></div></div>' +
     done('I made a real prospector\'s map. Color in my Sample Scientist badge!'))

# ---------------------------------------------------------------- 14. badge tracker
page(kicker('Every trip') + '<h1>My Badge Tracker</h1><p class="rule">Finish a trip, then color in its badge. Collect all seven!</p>' +
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px 10px;justify-items:center;margin-top:10px">' +
     ''.join(f'<div class="center">{badge(n, t, a, "1.85in", colored=False)}<div style="font:500 10.5pt Fredoka;color:var(--sage);margin-top:4px">Earned on ________</div></div>' for n, t, a in BADGES[:6]) +
     '</div><div class="center" style="margin-top:14px">' + badge(*BADGES[6], size='2.2in', colored=False) + '<div style="font:600 12pt Fredoka;color:var(--rust);margin-top:4px">The big one. Earned on ________</div></div>')

# ---------------------------------------------------------------- 15. cut-out badges
CUT = 'border:1.6px dashed #b8a688;border-radius:50%;padding:6px'
page(kicker('Print on sticker paper or card stock') + '<h1>Cut-Out Badges</h1><p class="rule">Earned a badge? Cut it out and stick it on your hat, your bucket or this pack.</p>' +
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px 6px;justify-items:center;margin-top:10px">' +
     ''.join(f'<div style="{CUT}">{badge(n, t, a, "1.95in")}</div>' for n, t, a in BADGES) +
     ''.join(f'<div style="{CUT}">{badge(n, t, a, "1.95in")}</div>' for n, t, a in BADGES[:2]) +
     '</div><p class="center" style="font-size:10.5pt;color:var(--sage);margin-top:12px">Two spares at the bottom, for brothers, sisters and cousins. Grown-ups handle the scissors for little ones.</p>')

# ---------------------------------------------------------------- 16. certificates
def certificate(title, line1, line2, with_photo):
    photo = ('<div style="border:2px dashed var(--line);border-radius:10px;width:1.5in;height:1.25in;display:flex;align-items:center;justify-content:center;text-align:center;font:500 9.5pt Fredoka;color:var(--sage);padding:6px;flex:none">Tape a photo of your flake here</div>'
             if with_photo else f'<div style="flex:none">{badge(*BADGES[6], size="1.35in")}</div>')
    return f'''<div style="height:4.62in;border:3px double var(--rust);border-radius:16px;padding:.2in .3in;background:linear-gradient(#fffaf0,#fff);position:relative">
<div class="center"><div style="font:600 10pt Fredoka;letter-spacing:.2em;color:var(--rust)">FIRST FLAKE · OFFICIAL</div>
<div style="font:700 27pt/1.05 Fredoka;margin:4px 0 2px">{title}</div><div style="font-size:12pt;font-style:italic;color:var(--sage)">This certifies that</div>
<div style="width:4.6in;border-bottom:1.8px solid var(--ink);height:.42in;margin:0 auto 6px"></div></div>
<div style="display:flex;gap:16px;align-items:center"><div style="flex:1;font-size:12.6pt;line-height:1.5">{line1}</div>{photo}</div>
<div style="font-size:11.6pt;font-style:italic;color:var(--rust-d);margin-top:6px">{line2}</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;position:absolute;left:.3in;right:.3in;bottom:.18in;text-align:center;font:500 9.5pt Fredoka;color:var(--sage)">
<div><div class="sign" style="color:var(--ink);border-bottom:1.4px solid var(--ink);height:.36in">Josie</div>Josie McCall</div>
<div><div class="sign" style="color:var(--ink);border-bottom:1.4px solid var(--ink);height:.36in">Ezra</div>Grandpa Ezra</div>
<div><div style="border-bottom:1.4px solid var(--ink);height:.36in"></div>Grown-up witness</div></div></div>'''


page(certificate('First Flake Finder',
                 'found their very first flake of gold on <span style="display:inline-block;width:1.5in;border-bottom:1.4px solid var(--ink)"></span><br>at <span style="display:inline-block;width:3.3in;border-bottom:1.4px solid var(--ink)"></span> creek.',
                 'Read the river. It already knows where the gold is.', True) +
     '<div style="border-top:2px dashed #b8a688;margin:.14in -.3in;position:relative"><span style="position:absolute;left:50%;top:-10px;transform:translateX(-50%);background:#fff;padding:0 8px;font:500 9pt Fredoka;color:var(--sage)">cut here</span></div>' +
     certificate('Junior Prospector Graduate',
                 'finished all seven trips of the First Flake adventure, learned to read a river, and earned the title of Junior Prospector on <span style="display:inline-block;width:1.5in;border-bottom:1.4px solid var(--ink)"></span>.',
                 'Real prospectors keep going. The gold has waited thousands of years. It will wait for you.', False))

# ---------------------------------------------------------------- assemble
out = []
for i, (body, cover) in enumerate(pages, start=1):
    foot = '' if cover else f'<div class="foot"><span>First Flake · Junior Prospector Family Pack</span><span>{i}</span></div>'
    bg = ' style="background:#f6efe2"' if cover else ''
    out.append(f'<section class="page"{bg}><div class="frame"></div><div class="in">{body}</div>{foot}</section>')

html = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Junior Prospector Family Pack</title>'
        '<link rel="stylesheet" href="style.css"></head><body>' + ''.join(out) +
        '<script>document.fonts.ready.then(function(){document.querySelectorAll(".in").forEach(function(e,i){if(e.scrollHeight>e.clientHeight+1)document.body.setAttribute("data-overflow",(document.body.getAttribute("data-overflow")||"")+" p"+(i+1)+":"+(e.scrollHeight-e.clientHeight))});document.body.setAttribute("data-ready","1")});</script>'
        '</body></html>')
(HERE / 'familypack.html').write_text(html, encoding='utf-8')
print(len(pages), 'pages')

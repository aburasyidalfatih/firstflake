"""Build bonus-1.html from research-west.md + research-east.md."""
import re, html

def parse(path):
    states, cur = {}, None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip()
        if line.startswith('## '):
            cur = {'spots': [], 'notes': [], 'rules': '', 'check': ''}
            states[line[3:].strip()] = cur
        elif cur is None or not line:
            continue
        elif line.startswith('- '):
            cur['spots'].append(line[2:])
        elif line.startswith('Rules:'):
            cur['rules'] = line[6:].strip()
        elif line.startswith('Check first:'):
            cur['check'] = line[12:].strip()
        else:
            cur['notes'].append(line)
    return states

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub(r'(https?://[^\s,;)]+)', r'<span class="url">\1</span>', t)

def spot(s):
    parts = [p.strip() for p in s.split(' · ')]
    head = inline(parts[0])
    rest = parts[1:]
    url = rest.pop() if rest and re.match(r'https?://', rest[-1]) else ''
    if rest and 'http' in rest[-1]:  # url embedded with a note
        url, rest = rest[-1], rest[:-1]
    agency = inline(rest[0]) if rest else ''
    rules = inline(' · '.join(rest[1:])) if len(rest) > 1 else ''
    return (f'<div class="spot">{head}<div class="m">{agency}</div>'
            f'<div>{rules}</div>' + (f'<div class="url">{html.escape(url)}</div>' if url else '') + '</div>')

west, east = parse('research-west.md'), parse('research-east.md')
allst = {**west, **east}
names = sorted(allst)

toc = ''.join(f'<li>{n}</li>' for n in names)
body = []
for n in names:
    s = allst[n]
    region = 'West' if n in west else 'East &amp; Midwest'
    body.append(f'<section class="state"><p class="kicker">{region}</p><h2>{n}</h2>')
    if s['spots']:
        body.append('<h3>Where to pan</h3>' + ''.join(spot(x) for x in s['spots']))
    for note in s['notes']:
        body.append(f'<div class="box small">{inline(note)}</div>')
    if s['rules']:
        body.append(f'<h3>The rules in one paragraph</h3><p>{inline(s["rules"])}</p>')
    if s['check']:
        body.append(f'<div class="card"><b>Check before you go:</b><br>{inline(s["check"])}</div>')
    body.append('</section>')

page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Bonus 1: Public Panning Areas by State</title><link rel="stylesheet" href="style.css"></head><body>
<div class="cover">
  <div><p class="kicker">First Flake · Bonus 1</p></div>
  <div><div class="big">Public Panning<br>Areas by State</div>
  <p class="lead" style="margin-top:14px">Officially open places to pan for gold in {len(names)} states, the rules for each one, and the official page to check before you load the truck.</p></div>
  <p class="q">"The best creek is the one you're allowed to stand in." — Grandpa Ezra</p>
</div>

<p class="kicker">Read this first</p>
<h1>How to use this guide</h1>
<ol>
<li><b>Find your state.</b> States are in alphabetical order. Each one lists named spots, the managing agency, what tools are allowed, and a source link.</li>
<li><b>Read the rules paragraph.</b> It tells you whether a permit is needed and what's off limits, such as dredges, state parks, or fish spawning seasons.</li>
<li><b>Call or check the official link before you go.</b> Rules, fees and seasons change every year. A two-minute call to the ranger district is the professional move.</li>
<li><b>Check for claims.</b> Outside the specially set-aside areas, use Bonus 2 to make sure nobody holds a claim where you plan to dig.</li>
</ol>

<div class="box"><b>Words you'll see</b>
<ul>
<li><b>Casual use:</b> panning and hand tools that barely disturb the ground. Usually no permit needed on open BLM and Forest Service land.</li>
<li><b>Withdrawn area:</b> land closed to new mining claims, often set aside for the public to pan. These are the safest spots for beginners.</li>
<li><b>Pans only / hands and pans:</b> a gold pan and your hands. No shovels, sluices or detectors.</li>
<li><b>Pay-to-pan:</b> a private business that sells buckets of gravel or access to a creek. Great for families and for guaranteed color.</li>
</ul></div>

<div class="warn"><b>Honest note:</b> This list was compiled in October 2026 from agency websites (BLM, U.S. Forest Service, state natural resource and geological agencies, state parks), with a few well-known secondary sources where the agency page wasn't available. It is not legal advice and not every open creek is listed. Fees and seasons marked "confirm" are the ones most likely to change.</div>

<h2>States in this guide</h2>
<ul class="cols">{toc}</ul>

{''.join(body)}

<section class="state"><h2>Your state isn't listed?</h2>
<ul>
<li>Call the nearest <b>BLM field office</b> or <b>Forest Service ranger district</b> and ask: "Are there any areas open to recreational gold panning near me?"</li>
<li>Search your state's <b>geological survey</b> or <b>department of natural resources</b> site for "gold panning".</li>
<li>Join a local <b>GPAA chapter</b> or prospecting club. Many own claims their members can pan.</li>
<li>No gold nearby? Use Bonus 4 and practice at home with paydirt.</li>
</ul>
<div class="ezra">Ezra says: "Every creek I ever loved, I found by asking somebody who'd been there first."</div>
<p class="foot">First Flake: Josie's 7-Trip Field Workbook · Bonus 1. General information, not legal advice. Always confirm current rules with the managing agency.</p>
</section>
</body></html>'''
open('bonus-1.html', 'w', encoding='utf-8').write(page)
print(len(names), 'states')

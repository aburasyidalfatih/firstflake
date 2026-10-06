import sys, re, html
dom = open(sys.argv[1], encoding='utf-8', errors='replace').read()
ov = re.search(r'data-overflow="([^"]*)"', dom)
print('OVERFLOW:' + ov.group(1) if ov else 'no overflow')
m = re.search(r'data-fields="([^"]*)"', dom)
open(sys.argv[2], 'w', encoding='utf-8').write(html.unescape(m.group(1)))

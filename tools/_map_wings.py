import re

s = open('_design/_wings_page.html', encoding='utf-8', errors='ignore').read()
pat = re.compile(r'https://webstoreassets\.lunarclientprod\.com/packages/[^"\'\\ ]+\.(?:mp4|png|webm)')
for m in pat.finditer(s):
    ctx = s[max(0, m.start() - 1200):m.end() + 1200]
    names = re.findall(r'"(?:name|title|slug)"\s*:\s*"([^"]{2,60})"', ctx)
    ids = re.findall(r'"(?:id|productId)"\s*:\s*"?(\d{6,9})"?', ctx)
    print(m.group(0).split('/')[-1], '|', names[:8], '|', ids[:4])

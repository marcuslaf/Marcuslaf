import json
import urllib.request
from datetime import datetime, timedelta

username = 'marcuslaf'
url = f'https://github-contributions-api.jogruber.de/v4/{username}'
data = json.loads(urllib.request.urlopen(url).read())
contribs = data['contributions']

today = datetime.utcnow()
start = today - timedelta(days=364)
recent = [c for c in contribs if datetime.strptime(c['date'], '%Y-%m-%d') >= start]

colors_dark = ['#161b22', '#0a3d6b', '#1158a7', '#2477d6', '#58a6ff']

weeks = 53
cell_size = 10
cell_gap = 2
total_cell = cell_size + cell_gap
header_height = 20
month_height = 15
width = weeks * total_cell + 60
height = 7 * total_cell + header_height + month_height + 10

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
svg.append('<style>text { font: 10px sans-serif; fill: #8b949e; }</style>')

months = {}
for c in recent:
    dt = datetime.strptime(c['date'], '%Y-%m-%d')
    week_idx = (dt - start).days // 7
    if dt.day <= 7:
        months[week_idx] = dt.strftime('%b')

for idx, label in months.items():
    x = idx * total_cell + 60
    svg.append(f'<text x="{x}" y="{header_height - 5}">{label}</text>')

for i, name in enumerate(['Mon', 'Wed', 'Fri']):
    y = header_height + month_height + i * 2 * total_cell + cell_size
    svg.append(f'<text x="0" y="{y + 3}">{name}</text>')

for c in recent:
    dt = datetime.strptime(c['date'], '%Y-%m-%d')
    week_idx = (dt - start).days // 7
    day_idx = dt.weekday()
    x = week_idx * total_cell + 60
    y = header_height + month_height + day_idx * total_cell
    color = colors_dark[c['level']]
    svg.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}"/>')

svg.append('</svg>')

with open('assets/contribution-grid.svg', 'w') as f:
    f.write('\n'.join(svg))

total_contribs = sum(c['count'] for c in recent)
print(f'Generated contribution-grid.svg: {total_contribs} contributions')

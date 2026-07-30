"""Generate a clean contribution grid SVG — no streak stats, just the heatmap."""

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from collections import defaultdict

username = "marcuslaf"

url = f"https://github-contributions-api.jogruber.de/v4/{username}"
data = json.loads(urllib.request.urlopen(url).read())
contribs = data["contributions"]

today = datetime.now(timezone.utc).replace(tzinfo=None)
start = today - timedelta(days=364)
recent = [
    c for c in contribs if datetime.strptime(c["date"], "%Y-%m-%d") >= start
]

total_contribs = sum(c["count"] for c in recent)

# ── SVG config ──
colors_level = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
cell_size = 13
cell_gap = 3
total_cell = cell_size + cell_gap
weeks = 53
padding = 24
month_height = 18
day_label_width = 42
header_h = 36

grid_width = weeks * total_cell + day_label_width
width = grid_width + padding * 2
grid_height = 7 * total_cell
height = padding + header_h + month_height + grid_height + month_height + padding

svg_lines = []
S = svg_lines.append

S(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
S("<defs>")
S('<linearGradient id="bgCG" x1="0" y1="0" x2="0" y2="1">')
S('<stop offset="0%" stop-color="#0d1117"/>')
S('<stop offset="100%" stop-color="#161b22"/>')
S("</linearGradient>")
S("</defs>")

S(f'<rect width="{width}" height="{height}" rx="10" fill="url(#bgCG)" stroke="#21262d" stroke-width="1"/>')

# Header
S(f'<text x="{padding}" y="{padding + 14}" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="600" fill="#e6edf3">📈 Atividade nos últimos 12 meses</text>')
S(f'<text x="{width - padding}" y="{padding + 14}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#8b949e" text-anchor="end">{total_contribs} contribuições</text>')

x_start = padding + day_label_width
y_cursor = padding + header_h + month_height

# Month labels
month_first_weeks = {}
for c in recent:
    dt = datetime.strptime(c["date"], "%Y-%m-%d")
    week_idx = (dt - start).days // 7
    if week_idx not in month_first_weeks:
        month_first_weeks[week_idx] = dt.month

months_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
drawn = set()
for week_idx, mon in sorted(month_first_weeks.items()):
    if mon not in drawn:
        x = x_start + week_idx * total_cell
        S(f'<text x="{x}" y="{y_cursor - 4}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">{months_names[mon - 1]}</text>')
        drawn.add(mon)

# Day labels
for i, name in enumerate(["Seg", "", "Qua", "", "Sex", "", ""]):
    y = y_cursor + i * total_cell + cell_size // 2 + 3
    S(f'<text x="{padding + 2}" y="{y}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#8b949e" text-anchor="end">{name}</text>')

# Cells
for c in recent:
    dt = datetime.strptime(c["date"], "%Y-%m-%d")
    week_idx = (dt - start).days // 7
    day_idx = dt.weekday()
    x = x_start + week_idx * total_cell
    y = y_cursor + day_idx * total_cell
    color = colors_level[c["level"]]
    S(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3" fill="{color}"/>')

# Legend
legend_y = y_cursor + grid_height + 14
S(f'<text x="{x_start}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">Menos</text>')
for level in range(5):
    lx = x_start + 50 + level * (cell_size + cell_gap + 4)
    S(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{colors_level[level]}"/>')
S(f'<text x="{x_start + 50 + 5 * (cell_size + cell_gap + 4) + 4}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">Mais</text>')

S(f'<text x="{width - padding}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#586069" text-anchor="end">Atualizado via GitHub Actions</text>')

S("</svg>")

with open("assets/contribution-grid.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg_lines))

print(f"[OK] contribution-grid.svg gerado: {total_contribs} contribuicoes")

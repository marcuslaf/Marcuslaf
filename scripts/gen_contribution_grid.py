"""Generate a beautiful contribution grid SVG with stats summary."""

import json
import urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

username = "marcuslaf"

# Fetch contribution data
url = f"https://github-contributions-api.jogruber.de/v4/{username}"
data = json.loads(urllib.request.urlopen(url).read())
contribs = data["contributions"]

from datetime import timezone
today = datetime.now(timezone.utc).replace(tzinfo=None)
start = today - timedelta(days=364)
recent = [
    c for c in contribs if datetime.strptime(c["date"], "%Y-%m-%d") >= start
]

# Calculate stats
total_contribs = sum(c["count"] for c in recent)

# Current streak
streak = 0
for c in reversed(recent):
    if c["count"] > 0:
        streak += 1
    else:
        break

# Longest streak
longest_streak = 0
current = 0
for c in recent:
    if c["count"] > 0:
        current += 1
        longest_streak = max(longest_streak, current)
    else:
        current = 0

# Group by month for labels
month_groups = defaultdict(int)
for c in recent:
    dt = datetime.strptime(c["date"], "%Y-%m-%d")
    month_groups[dt.month] += c["count"]

# ── SVG Configuration ──
colors_level = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
cell_size = 12
cell_gap = 3
total_cell = cell_size + cell_gap

# We need 53 weeks (365 days / 7)
weeks = 53
stats_height = 60
header_height = 18
month_height = 16
day_label_width = 40
legend_height = 22
padding = 24

grid_width = weeks * total_cell + day_label_width
width = grid_width + padding * 2
grid_height = 7 * total_cell
height = stats_height + header_height + month_height + grid_height + legend_height + padding * 2

svg_lines = []
S = svg_lines.append

# ── SVG open ──
S(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
S("<defs>")
S('<linearGradient id="bgGradCG" x1="0" y1="0" x2="0" y2="1">')
S('<stop offset="0%" stop-color="#0d1117"/>')
S('<stop offset="100%" stop-color="#161b22"/>')
S("</linearGradient>")
S('<linearGradient id="statGlow" x1="0" y1="0" x2="1" y2="0">')
S('<stop offset="0%" stop-color="#39d353" stop-opacity="0.15"/>')
S('<stop offset="50%" stop-color="#39d353" stop-opacity="0.05"/>')
S('<stop offset="100%" stop-color="#39d353" stop-opacity="0.15"/>')
S("</linearGradient>")
S("</defs>")

# Background card
S(f'<rect width="{width}" height="{height}" rx="10" fill="url(#bgGradCG)" stroke="#21262d" stroke-width="1"/>')

x_start = padding + day_label_width
y_cursor = padding + stats_height + header_height + month_height

# ── STATS ROW ──
stat_items = [
    ("Total Contribuições", str(total_contribs), "#39d353"),
    ("Streak Atual", f"{streak} dias", "#26a641"),
    ("Maior Streak", f"{longest_streak} dias", "#006d32"),
]

stat_card_w = (width - padding * 2 - 20) // 3
stat_card_h = 42
stat_y = 18

for i, (label, value, color) in enumerate(stat_items):
    sx = padding + i * (stat_card_w + 10)
    S(f'<rect x="{sx}" y="{stat_y}" width="{stat_card_w}" height="{stat_card_h}" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>')
    S(f'<text x="{sx + 14}" y="{stat_y + 18}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">{label}</text>')
    S(f'<text x="{sx + 14}" y="{stat_y + 35}" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="700" fill="{color}">{value}</text>')

# ── MONTH LABELS ──
months_list = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Find which week each month starts
month_first_weeks = {}
for c in recent:
    dt = datetime.strptime(c["date"], "%Y-%m-%d")
    week_idx = (dt - start).days // 7
    if week_idx not in month_first_weeks:
        month_first_weeks[week_idx] = dt.month

month_labels_drawn = set()
for week_idx, month_num in sorted(month_first_weeks.items()):
    if month_num not in month_labels_drawn:
        x = x_start + week_idx * total_cell
        S(f'<text x="{x}" y="{y_cursor - 5}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">{months_list[month_num - 1]}</text>')
        month_labels_drawn.add(month_num)

# ── DAY LABELS ──
for i, name in enumerate(["Seg", "", "Qua", "", "Sex", "", ""]):
    y = y_cursor + i * total_cell + cell_size // 2 + 3
    S(f'<text x="{padding + 2}" y="{y}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#8b949e" text-anchor="end">{name}</text>')

# ── CONTRIBUTION CELLS ──
for c in recent:
    dt = datetime.strptime(c["date"], "%Y-%m-%d")
    week_idx = (dt - start).days // 7
    day_idx = dt.weekday()
    x = x_start + week_idx * total_cell
    y = y_cursor + day_idx * total_cell
    level = c["level"]
    color = colors_level[level]
    S(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3" fill="{color}"/>')

# ── LEGEND ──
legend_y = y_cursor + grid_height + 12
S(f'<text x="{x_start}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">Menos</text>')
for level in range(5):
    lx = x_start + 50 + level * (cell_size + cell_gap + 4)
    S(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{colors_level[level]}"/>')
S(f'<text x="{x_start + 50 + 5 * (cell_size + cell_gap + 4) + 4}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">Mais</text>')

S(f'<text x="{width - padding}" y="{legend_y + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#586069" text-anchor="end">Atualizado semanalmente via GitHub Actions</text>')

S("</svg>")

with open("assets/contribution-grid.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg_lines))

print(f"[OK] contribution-grid.svg gerado: {total_contribs} contribuicoes em 1 ano - streak: {streak} - longest: {longest_streak}")

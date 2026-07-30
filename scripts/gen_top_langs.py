"""Generate a beautiful top languages SVG with donut chart + bars + stars."""

import json
import urllib.request
from collections import defaultdict

username = "marcuslaf"

# Fetch repos
url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
repos = json.loads(urllib.request.urlopen(url).read())

# Aggregate language data: count, size in bytes, stars per language
lang_data = {}  # lang -> {count, bytes, stars}
for r in repos:
    lang = r.get("language")
    if not lang:
        continue
    if lang not in lang_data:
        lang_data[lang] = {"count": 0, "bytes": 0, "stars": 0}
    lang_data[lang]["count"] += 1
    lang_data[lang]["bytes"] += r.get("size", 0) * 1024  # approximate
    lang_data[lang]["stars"] += r.get("stargazers_count", 0)

# Sort by count descending
sorted_langs = sorted(lang_data.items(), key=lambda x: -x[1]["count"])
total_repos = sum(d["count"] for _, d in sorted_langs)
total_stars = sum(d["stars"] for _, d in sorted_langs)

# Language colors (GitHub Linguist colors)
lang_colors = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178C6",
    "CSS": "#563d7c", "Java": "#b07219", "HTML": "#e34c26",
    "C#": "#178600", "Shell": "#89e051", "C++": "#f34b7d",
    "C": "#555555", "Ruby": "#701516", "Go": "#00ADD8",
    "PHP": "#4F5D95", "Swift": "#F05138", "Kotlin": "#A97BFF",
    "Rust": "#DEA584", "Dart": "#00B4AB", "Lua": "#000080",
    "Scala": "#c22d40", "Elixir": "#6e4a7e", "HCL": "#006600",
}

# SVG dimensions
padding = 28
chart_area_width = 180
bar_area_left = padding + chart_area_width + 24
right_margin = 28
bar_area_width = 580 - bar_area_left - right_margin
width = 636  # wider to accommodate donut

# Calculate height dynamically
label_height = 24
bar_height = 10
gap = 10
n = len(sorted_langs)
header_h = 52
footer_h = 28
height = header_h + n * (label_height + bar_height + gap) + footer_h + 12

svg_lines = []
S = svg_lines.append

# ── SVG open ──
S(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
S("<defs>")
S('<linearGradient id="bgGradTL" x1="0" y1="0" x2="0" y2="1">')
S('<stop offset="0%" stop-color="#0d1117"/>')
S('<stop offset="100%" stop-color="#161b22"/>')
S("</linearGradient>")
S('<linearGradient id="barGlow" x1="0" y1="0" x2="1" y2="0">')
S('<stop offset="0%" stop-color="#58a6ff" stop-opacity="0.15"/>')
S('<stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>')
S("</linearGradient>")
S("</defs>")

# Background card
S(f'<rect width="{width}" height="{height}" rx="10" fill="url(#bgGradTL)" stroke="#21262d" stroke-width="1"/>')

# ── HEADER ──
S(f'<text x="{padding}" y="30" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="700" fill="#e6edf3">📊 Linguagens mais usadas</text>')
S(f'<text x="{padding + 190}" y="30" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#8b949e">⭐ {total_stars} stars · {total_repos} repositórios</text>')

# ── DONUT CHART ──
# Center and radius
cx = padding + chart_area_width // 2
cy = header_h + (height - header_h - footer_h) // 2 + 10
r = 72
inner_r = 38

# Filter top 5 for donut, rest as "Outros"
top_n = sorted_langs[:5]
other_count = sum(d["count"] for _, d in sorted_langs[5:])
if other_count > 0:
    top_n.append(("Outros", {"count": other_count, "bytes": 0, "stars": 0}))

# Calculate arc segments
total_for_donut = sum(d["count"] for _, d in top_n)
# Actually use total_repos since we want the complete picture
total_use = total_repos

# Draw donut segments
angle_start = -90  # start from top
for lang_name, data in top_n:
    pct = data["count"] / total_use * 100
    angle_sweep = 360 * data["count"] / total_use
    angle_end = angle_start + angle_sweep

    color = lang_colors.get(lang_name, "#586069")

    # Convert to radians
    import math

    a1_rad = math.radians(angle_start)
    a2_rad = math.radians(angle_end)

    x1 = cx + r * math.cos(a1_rad)
    y1 = cy + r * math.sin(a1_rad)
    x2 = cx + r * math.cos(a2_rad)
    y2 = cy + r * math.sin(a2_rad)

    large_arc = 1 if angle_sweep > 180 else 0
    S(
        f'<path d="M {cx + inner_r * math.cos(a1_rad)} {cy + inner_r * math.sin(a1_rad)} '
        f'L {x1} {y1} '
        f'A {r} {r} 0 {large_arc} 1 {x2} {y2} '
        f'L {cx + inner_r * math.cos(a2_rad)} {cy + inner_r * math.sin(a2_rad)} '
        f'A {inner_r} {inner_r} 0 {large_arc} 0 {cx + inner_r * math.cos(a1_rad)} {cy + inner_r * math.sin(a1_rad)} Z" '
        f'fill="{color}" opacity="0.9"/>'
    )

    angle_start = angle_end

# Center text
S(f'<text x="{cx}" y="{cy - 4}" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#8b949e" text-anchor="middle">{total_repos}</text>')
S(f'<text x="{cx}" y="{cy + 12}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#586069" text-anchor="middle">repos</text>')

# ── BAR CHART ──
y_pos = header_h
max_count = sorted_langs[0][1]["count"]

for i, (lang_name, data) in enumerate(sorted_langs):
    pct = data["count"] / total_repos * 100
    bar_w = (data["count"] / max_count) * bar_area_width
    color = lang_colors.get(lang_name, "#586069")

    # Donut legend indicator
    dot_y = y_pos + 6
    S(f'<circle cx="{bar_area_left - 10}" cy="{dot_y + label_height // 2 - 2}" r="4" fill="{color}" opacity="0.9"/>')

    # Language name
    S(f'<text x="{bar_area_left}" y="{y_pos + 16}" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#e6edf3" font-weight="500">{lang_name}</text>')

    # Count and percentage on the right
    S(f'<text x="{bar_area_left + bar_area_width}" y="{y_pos + 16}" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#8b949e" text-anchor="end">{data["count"]} repos · {pct:.0f}%</text>')

    # Bar background
    S(f'<rect x="{bar_area_left}" y="{y_pos + label_height - 4}" width="{bar_area_width}" height="{bar_height}" rx="5" fill="#161b22"/>')

    # Bar fill with gradient
    bar_w_actual = max(bar_w, 4)  # minimum visible width
    S(f'<rect x="{bar_area_left}" y="{y_pos + label_height - 4}" width="{bar_w_actual}" height="{bar_height}" rx="5" fill="{color}" opacity="0.85"/>')

    # Star count (right-aligned, after percentage text)
    if data["stars"] > 0:
        S(f'<text x="{bar_area_left + bar_area_width + 8}" y="{y_pos + 16}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#586069">⭐{data["stars"]}</text>')

    y_pos += label_height + bar_height + gap

# Footer
S(f'<text x="{padding}" y="{height - footer_h + 14}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#586069">Atualizado via GitHub Actions · Dados de {total_repos} repositórios públicos</text>')

S("</svg>")

with open("assets/top-langs.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg_lines))

print(f"[OK] top-langs.svg gerado: {n} linguagens, {total_repos} repos, {total_stars} stars, {height}px")

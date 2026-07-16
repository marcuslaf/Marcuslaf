import json
import urllib.request

username = 'marcuslaf'
url = f'https://api.github.com/users/{username}/repos?per_page=100'
repos = json.loads(urllib.request.urlopen(url).read())

langs = {}
for r in repos:
    lang = r.get('language')
    if lang:
        langs[lang] = langs.get(lang, 0) + 1

sorted_langs = sorted(langs.items(), key=lambda x: -x[1])
total = sum(v for _, v in sorted_langs)

lang_colors = {
    'Python': '#3572A5', 'JavaScript': '#f1e05a', 'CSS': '#563d7c',
    'Java': '#b07219', 'HTML': '#e34c26', 'C#': '#178600',
    'Shell': '#89e051', 'TypeScript': '#3178C6', 'C++': '#f34b7d',
    'C': '#555555', 'Ruby': '#701516', 'Go': '#00ADD8',
    'PHP': '#4F5D95', 'Swift': '#F05138', 'Kotlin': '#A97BFF',
}

width = 400
padding = 25
label_height = 22
bar_height = 8
gap = 12
n = len(sorted_langs)
height = 50 + n * (label_height + bar_height + gap) + 20

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
svg.append(f'<rect width="{width}" height="{height}" rx="6" fill="#0d1117"/>')
svg.append(f'<text x="{padding}" y="28" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="600" fill="#58a6ff">Most Used Languages</text>')

max_count = sorted_langs[0][1]
bar_area = width - padding * 2
y = 50

for lang, count in sorted_langs:
    pct = count / total * 100
    bar_w = (count / max_count) * bar_area
    color = lang_colors.get(lang, '#586069')

    svg.append(f'<text x="{padding}" y="{y + 14}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#e6edf3">{lang}</text>')
    svg.append(f'<text x="{width - padding}" y="{y + 14}" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#8b949e" text-anchor="end">{count} repos ({pct:.0f}%)</text>')
    svg.append(f'<rect x="{padding}" y="{y + label_height}" width="{bar_area}" height="{bar_height}" rx="4" fill="#161b22"/>')
    svg.append(f'<rect x="{padding}" y="{y + label_height}" width="{bar_w}" height="{bar_height}" rx="4" fill="{color}"/>')

    y += label_height + bar_height + gap

svg.append(f'<text x="{padding}" y="{height - 8}" font-family="Segoe UI, Arial, sans-serif" font-size="9" fill="#8b949e">Based on {total} public repositories</text>')
svg.append('</svg>')

with open('assets/top-langs.svg', 'w') as f:
    f.write('\n'.join(svg))

print(f'Generated: {n} languages, {total} repos, height={height}')

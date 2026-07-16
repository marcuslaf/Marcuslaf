import json
import urllib.request
import os

username = os.environ.get('GITHUB_REPOSITORY', 'marcuslaf').split('/')[0]
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
    'Dart': '#00B4AB', 'Rust': '#DEA584', 'Scala': '#c22d40',
}

width = 400
padding_x = 30
padding_top = 40
row_height = 30
bar_height = 10
n = len(sorted_langs)
height = padding_top + n * row_height + 30

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
svg.append(f'<rect width="{width}" height="{height}" rx="6" fill="#0d1117"/>')
svg.append(f'<text x="{padding_x}" y="28" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="600" fill="#58a6ff">Most Used Languages</text>')
svg.append(f'<text x="{padding_x}" y="{height - 12}" font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#8b949e">Based on {total} public repositories</text>')

max_count = sorted_langs[0][1]
max_bar_width = width - padding_x * 2 - 110

for i, (lang, count) in enumerate(sorted_langs):
    y = padding_top + i * row_height
    pct = count / total * 100
    bar_width = (count / max_count) * max_bar_width
    color = lang_colors.get(lang, '#586069')

    svg.append(f'<text x="{padding_x}" y="{y + 16}" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#e6edf3">{lang}</text>')
    svg.append(f'<rect x="{padding_x}" y="{y + 22}" width="{max_bar_width}" height="{bar_height}" rx="5" fill="#161b22"/>')
    svg.append(f'<rect x="{padding_x}" y="{y + 22}" width="{bar_width}" height="{bar_height}" rx="5" fill="{color}"/>')
    svg.append(f'<text x="{width - padding_x}" y="{y + 16}" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="600" fill="#8b949e" text-anchor="end">{count} repos ({pct:.0f}%)</text>')

svg.append('</svg>')

with open('assets/top-langs.svg', 'w') as f:
    f.write('\n'.join(svg))

print(f'Generated top-langs.svg: {n} languages, {total} repos')

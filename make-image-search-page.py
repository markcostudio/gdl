from pathlib import Path
from urllib.parse import quote

BAD_LIST = Path("still-bad-images-after-github.txt")

if not BAD_LIST.exists():
    BAD_LIST = Path("still-bad-images-after-ex3me.txt")

items = [Path(x.strip()).name for x in BAD_LIST.read_text().splitlines() if x.strip()]

html = ["<html><body><h1>Missing GDL Images Search</h1><ul>"]

for name in items:
    q1 = quote(f'"{name}"')
    q2 = quote(f'"{name}" "GDL"')
    q3 = quote(f'"{name}" "graphisoft"')
    q4 = quote(f'site:gdl.ex3me.ch "{name}"')
    q5 = quote(f'site:github.com "{name}"')

    html.append(f"""
    <li>
      <strong>{name}</strong><br>
      <a href="https://www.google.com/search?q={q1}" target="_blank">Google exact</a> |
      <a href="https://www.google.com/search?q={q2}" target="_blank">Google + GDL</a> |
      <a href="https://www.google.com/search?q={q3}" target="_blank">Google + Graphisoft</a> |
      <a href="https://www.google.com/search?q={q4}" target="_blank">ex3me mirror</a> |
      <a href="https://www.google.com/search?q={q5}" target="_blank">GitHub</a>
    </li>
    """)

html.append("</ul></body></html>")

Path("missing-image-search.html").write_text("\n".join(html))
print("Created missing-image-search.html")

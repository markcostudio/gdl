from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

ROOT = Path(".")
BASE = "/gdl/"

pages = []

for html in ROOT.rglob("index.html"):
    if "web.archive.org/web/20250518184039/https%3A/gdl.graphisoft.com/reference-guide" not in html.as_posix():
        continue

    text = html.read_text(errors="ignore")
    soup = BeautifulSoup(text, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else html.parent.name

    main = soup.find("main")
    content = main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)

    content = re.sub(r"\s+", " ", content)

    url = BASE + html.as_posix().replace("https%3A", "https%253A")

    pages.append({
        "title": title,
        "url": url,
        "text": content[:20000]
    })

Path("search-index.json").write_text(json.dumps(pages, ensure_ascii=False))
print(f"Indexed {len(pages)} pages")

from pathlib import Path
from urllib.parse import urlparse
import re
import subprocess

ROOT = Path(".")
PREFIX = "/gdl/web.archive.org/web"

# Finds Wayback image URLs like:
# https://web.archive.org/web/20250428084820im_/https://gdl.graphisoft.com/path/image.png
pattern = re.compile(
    r'https://web\.archive\.org/web/([0-9]+im_)/(https://[^"\'>\s)]+?\.(?:png|jpg|jpeg|gif|webp|svg))(?:\?[^"\'>\s)]*)?',
    re.IGNORECASE,
)

urls = set()

for html in ROOT.rglob("*.html"):
    text = html.read_text(errors="ignore")
    for match in pattern.finditer(text):
        full_url = match.group(0)
        timestamp = match.group(1)
        original_url = match.group(2)
        urls.add((full_url, timestamp, original_url))

print(f"Found {len(urls)} archived image links")

downloaded = 0
rewritten = 0

for full_url, timestamp, original_url in sorted(urls):
    parsed = urlparse(original_url)
    local_path = ROOT / "web.archive.org" / "web" / timestamp / "https%3A" / parsed.netloc / parsed.path.lstrip("/")
    local_path.parent.mkdir(parents=True, exist_ok=True)

    if not local_path.exists() or local_path.stat().st_size == 0:
        print(f"Downloading: {original_url}")
        subprocess.run(
            ["curl", "-L", full_url, "-o", str(local_path)],
            check=False
        )
        downloaded += 1

    local_url = f"{PREFIX}/{timestamp}/https%253A/{parsed.netloc}{parsed.path}"

    for html in ROOT.rglob("*.html"):
        text = html.read_text(errors="ignore")
        if full_url in text:
            html.write_text(text.replace(full_url, local_url))
            rewritten += 1

print(f"Downloaded or checked: {downloaded}")
print(f"Rewritten occurrences/files touched: {rewritten}")

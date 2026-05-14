from pathlib import Path
import re

ROOT = Path(".")
SITE_PREFIX = "/gdl/web.archive.org/web/20250518184039/https%253A/gdl.graphisoft.com"

# Find local pages and their WordPress ?p=ID
id_to_local = {}

for html in ROOT.rglob("*.html"):
    text = html.read_text(errors="ignore")

    ids = set(re.findall(r"https://(?:web\.archive\.org/web/\d+(?:mp_)?/https://)?gdl\.graphisoft\.com/\?p=(\d+)", text))
    if not ids:
        continue

    # Only map pages inside the local Graphisoft mirror
    parts = html.as_posix()
    marker = "web.archive.org/web/20250518184039/https%3A/gdl.graphisoft.com"
    if marker not in parts:
        continue

    local_path = parts.split(marker, 1)[1]

    if local_path.endswith("/index.html"):
        local_path = local_path[:-10]
    elif local_path.endswith("index.html"):
        local_path = local_path[:-10]

    if not local_path.startswith("/"):
        local_path = "/" + local_path

    local_url = SITE_PREFIX + local_path

    for pid in ids:
        id_to_local[pid] = local_url

print(f"Mapped {len(id_to_local)} post IDs")

# Replace Wayback ?p=ID links in all HTML files
changed = 0

pattern = re.compile(
    r"https://web\.archive\.org/web/\d+(?:mp_)?/https://gdl\.graphisoft\.com/\?p=(\d+)(#[A-Za-z0-9_\-]+)?"
)

for html in ROOT.rglob("*.html"):
    text = html.read_text(errors="ignore")
    original = text

    def repl(match):
        pid = match.group(1)
        anchor = match.group(2) or ""
        if pid in id_to_local:
            return id_to_local[pid] + "/" + anchor
        return match.group(0)

    text = pattern.sub(repl, text)

    if text != original:
        html.write_text(text)
        changed += 1

print(f"Changed {changed} files")

missing = sorted(set(
    m.group(1)
    for html in ROOT.rglob("*.html")
    for m in pattern.finditer(html.read_text(errors="ignore"))
))

if missing:
    print("Unmapped IDs still remaining:")
    print(", ".join(missing))
else:
    print("No remaining Wayback ?p= links found.")

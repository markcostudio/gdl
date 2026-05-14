from pathlib import Path
import re
import subprocess

ROOT = Path(".")
PREFIX = "/gdl/web.archive.org/web"

patterns = [
    re.compile(r'https://web\.archive\.org/web/([0-9]+im_)/https://([^"\'\s)]+?\.(?:png|jpg|jpeg|gif|webp|svg))', re.I),
    re.compile(r'/gdl/web\.archive\.org/web/([0-9]+im_)/https%253A/([^"\'\s)]+?\.(?:png|jpg|jpeg|gif|webp|svg))', re.I),
]

files = [
    p for p in (
        list(ROOT.rglob("*.html")) +
        list(ROOT.rglob("*.css")) +
        list(ROOT.rglob("*.js"))
    )
    if p.is_file()
]

found = 0
downloaded = 0
changed = 0

for file in files:
    text = file.read_text(errors="ignore")
    original = text

    for pattern in patterns:
        for match in list(pattern.finditer(text)):
            found += 1
            timestamp = match.group(1)
            host_path = match.group(2)
            original_url = f"https://{host_path}"
            wayback_url = f"https://web.archive.org/web/{timestamp}/https://{host_path}"

            parts = host_path.split("/", 1)
            host = parts[0]
            path = parts[1] if len(parts) > 1 else ""

            local_file = ROOT / "web.archive.org" / "web" / timestamp / "https%3A" / host / path
            local_file.parent.mkdir(parents=True, exist_ok=True)

            if not local_file.exists() or local_file.stat().st_size == 0:
                print(f"Downloading: {wayback_url}")
                subprocess.run(["curl", "-L", wayback_url, "-o", str(local_file)], check=False)
                downloaded += 1

            local_url = f"{PREFIX}/{timestamp}/https%253A/{host}/{path}"
            text = text.replace(match.group(0), local_url)

    if text != original:
        file.write_text(text)
        changed += 1

print(f"Found image refs: {found}")
print(f"Downloaded missing files: {downloaded}")
print(f"Changed files: {changed}")

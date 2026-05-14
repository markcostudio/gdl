from pathlib import Path
from urllib.parse import unquote
import re
import subprocess

ROOT = Path(".")
EXTS = r"(?:png|jpg|jpeg|gif|webp|svg)"

patterns = [
    # Full Wayback image URLs
    re.compile(r'https://web\.archive\.org/web/([0-9]+im_)/https://([^"\'\s)<>]+?\.' + EXTS + r')', re.I),

    # Local GitHub Pages image paths
    re.compile(r'/gdl/web\.archive\.org/web/([0-9]+im_)/https%253A/([^"\'\s)<>]+?\.' + EXTS + r')', re.I),
]

found = 0
downloaded = 0
missing = []

for html in ROOT.rglob("index.html"):
    if not html.is_file():
        continue

    text = html.read_text(errors="ignore")

    for pattern in patterns:
        for m in pattern.finditer(text):
            found += 1
            timestamp = m.group(1)
            host_path = unquote(m.group(2))

            parts = host_path.split("/", 1)
            host = parts[0]
            path = parts[1] if len(parts) > 1 else ""

            local_file = ROOT / "web.archive.org" / "web" / timestamp / "https%3A" / host / path
            wayback_url = f"https://web.archive.org/web/{timestamp}/https://{host}/{path}"

            if not local_file.exists() or local_file.stat().st_size < 1000:
                local_file.parent.mkdir(parents=True, exist_ok=True)
                print(f"Downloading: {wayback_url}")
                subprocess.run(["curl", "-L", wayback_url, "-o", str(local_file)], check=False)

                if local_file.exists() and local_file.stat().st_size >= 1000:
                    downloaded += 1
                else:
                    missing.append((str(html), wayback_url, str(local_file), local_file.stat().st_size if local_file.exists() else 0))

print(f"\nImage refs found: {found}")
print(f"Images downloaded: {downloaded}")
print(f"Still missing or suspicious: {len(missing)}")

if missing:
    Path("missing-images-report.txt").write_text(
        "\n".join(f"{page}\n  {url}\n  {local} size={size}\n" for page, url, local, size in missing)
    )
    print("Wrote missing-images-report.txt")

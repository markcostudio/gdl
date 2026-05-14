from pathlib import Path
import subprocess
import requests
import time
import os
import imghdr

BAD_LIST = Path("still-bad-images-after-ex3me.txt")

token = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.text-match+json",
}

if token:
    HEADERS["Authorization"] = f"Bearer {token}"

def is_valid_image(path):
    if not path.exists() or path.stat().st_size == 0:
        return False
    if path.suffix.lower() == ".svg":
        return "<svg" in path.read_text(errors="ignore")[:500]
    return imghdr.what(path) is not None

bad_paths = [Path(x.strip()) for x in BAD_LIST.read_text().splitlines() if x.strip()]

fixed = 0
failed = []

for bad_path in bad_paths:
    filename = bad_path.name
    query = f'"{filename}" in:path'
    url = "https://api.github.com/search/code"

    print(f"Searching GitHub for {filename}")

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            params={"q": query, "per_page": 10},
            timeout=30,
        )

        if r.status_code != 200:
            print(f"  GitHub API failed: {r.status_code}")
            print(f"  {r.text[:300]}")
            failed.append(str(bad_path))
            continue

        data = r.json()
        items = data.get("items", [])

        if not items:
            print("  No GitHub results")
            failed.append(str(bad_path))
            continue

        success = False

        for item in items:
            html_url = item.get("html_url", "")

            if "/blob/" not in html_url:
                continue

            raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            print(f"  Trying {raw_url}")

            result = subprocess.run(
                ["curl", "-L", "--fail", "--silent", "--show-error", raw_url, "-o", str(bad_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if result.returncode == 0 and is_valid_image(bad_path):
                print(f"  Fixed {filename}")
                fixed += 1
                success = True
                break

        if not success:
            failed.append(str(bad_path))

        time.sleep(2)

    except Exception as e:
        print(f"  Error: {e}")
        failed.append(str(bad_path))

Path("still-bad-images-after-github.txt").write_text("\n".join(failed))

print()
print(f"Recovered from GitHub: {fixed}")
print(f"Still failed: {len(failed)}")

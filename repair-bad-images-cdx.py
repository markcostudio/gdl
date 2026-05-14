from pathlib import Path
from urllib.parse import quote
import json
import subprocess
import imghdr
import time

BAD_LIST = Path("bad-images.txt")
FAILED_OUT = Path("still-bad-images-after-cdx.txt")

def is_valid_image(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False

    if path.suffix.lower() == ".svg":
        return "<svg" in path.read_text(errors="ignore")[:500]

    return imghdr.what(path) is not None

def wayback_cdx(original_url: str):
    cdx_url = (
        "https://web.archive.org/cdx?url="
        + quote(original_url, safe="")
        + "&output=json"
        + "&fl=timestamp,original,statuscode,mimetype"
        + "&collapse=digest"
    )

    try:
        result = subprocess.run(
            ["curl", "-L", "--max-time", "25", cdx_url],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return []

    try:
        data = json.loads(result.stdout)
    except Exception:
        return []

    if len(data) <= 1:
        return []

    rows = data[1:]

    # Prefer likely image records and successful captures, but keep others as fallback.
    def score(row):
        ts, original, status, mime = (row + ["", "", "", ""])[:4]
        s = 0
        if status == "200":
            s -= 100
        if "image" in mime:
            s -= 50
        # Prefer newer captures first.
        s -= int(ts[:8]) if ts[:8].isdigit() else 0
        return s

    return sorted(rows, key=score)

def try_download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", url, "-o", str(dest)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return is_valid_image(dest)

def main():
    if not BAD_LIST.exists():
        print("Missing bad-images.txt. Run validate-images.py first.")
        return

    bad_paths = [
        Path(line.strip())
        for line in BAD_LIST.read_text().splitlines()
        if line.strip()
    ]

    fixed = 0
    failed = []

    for path in bad_paths:
        parts = path.parts

        try:
            web_i = parts.index("web")
            host = parts[web_i + 3]
            rel_path = "/".join(parts[web_i + 4:])
        except Exception:
            failed.append(str(path))
            continue

        original_url = f"https://{host}/{rel_path}"
        print(f"Looking up: {original_url}")

        rows = wayback_cdx(original_url)

        if not rows:
            print("  No CDX captures found")
            failed.append(str(path))
            continue

        success = False

        for row in rows:
            ts = row[0]
            status = row[2] if len(row) > 2 else ""
            mime = row[3] if len(row) > 3 else ""

            # Try image mode first.
            test_urls = [
                f"https://web.archive.org/web/{ts}im_/{original_url}",
                f"https://web.archive.org/web/{ts}/{original_url}",
            ]

            for wayback_url in test_urls:
                print(f"  Trying {wayback_url} [{status} {mime}]")

                if try_download(wayback_url, path):
                    print(f"  Fixed: {path}")
                    fixed += 1
                    success = True
                    break

                time.sleep(0.1)

            if success:
                break

        if not success:
            failed.append(str(path))

    FAILED_OUT.write_text("\n".join(failed))

    print()
    print(f"Fixed: {fixed}")
    print(f"Failed: {len(failed)}")
    print(f"Wrote: {FAILED_OUT}")

if __name__ == "__main__":
    main()

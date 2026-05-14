from pathlib import Path
import subprocess
import imghdr

GOOD_TIMESTAMPS = [
    "20241012060049im_",
    "20250428084820im_",
    "20250518200702im_",
    "20250518184039im_",
]

bad_file = Path("bad-images.txt")

def is_valid_image(path):
    if not path.exists() or path.stat().st_size == 0:
        return False
    if path.suffix.lower() == ".svg":
        return "<svg" in path.read_text(errors="ignore")[:500]
    return imghdr.what(path) is not None

bad_paths = [Path(line.strip()) for line in bad_file.read_text().splitlines() if line.strip()]

fixed = 0
failed = []

for path in bad_paths:
    parts = path.parts

    try:
        web_i = parts.index("web")
        old_timestamp = parts[web_i + 1]
        encoded_scheme = parts[web_i + 2]
        host = parts[web_i + 3]
        rel_path = "/".join(parts[web_i + 4:])
    except Exception:
        failed.append(str(path))
        continue

    for ts in GOOD_TIMESTAMPS:
        wayback_url = f"https://web.archive.org/web/{ts}/https://{host}/{rel_path}"

        print(f"Trying: {wayback_url}")

        result = subprocess.run(
            ["curl", "-L", "--fail", wayback_url, "-o", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode == 0 and is_valid_image(path):
            print(f"Fixed: {path}")
            fixed += 1
            break
    else:
        failed.append(str(path))

print(f"\nFixed: {fixed}")
print(f"Failed: {len(failed)}")

Path("still-bad-images.txt").write_text("\n".join(failed))

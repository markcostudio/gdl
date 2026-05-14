from pathlib import Path
import subprocess
import imghdr

BAD_LIST = Path("still-bad-images-after-cdx.txt")
MIRROR_BASE = "https://www.gdl.ex3me.ch/Images/GDL_Images"

def is_valid_image(path):
    if not path.exists() or path.stat().st_size == 0:
        return False
    if path.suffix.lower() == ".svg":
        return "<svg" in path.read_text(errors="ignore")[:500]
    return imghdr.what(path) is not None

bad_paths = [Path(x.strip()) for x in BAD_LIST.read_text().splitlines() if x.strip()]

fixed = 0
failed = []

for path in bad_paths:
    filename = path.name
    url = f"{MIRROR_BASE}/{filename}"

    print(f"Trying mirror: {url}")

    result = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", url, "-o", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if result.returncode == 0 and is_valid_image(path):
        print(f"Fixed: {path}")
        fixed += 1
    else:
        failed.append(str(path))

Path("still-bad-images-after-ex3me.txt").write_text("\n".join(failed))

print(f"\nFixed: {fixed}")
print(f"Still failed: {len(failed)}")

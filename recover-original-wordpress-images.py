from pathlib import Path
import subprocess
import re
import imghdr

BAD_LIST = Path("still-bad-images-after-ex3me.txt")
MIRROR = "https://www.gdl.ex3me.ch/Images/GDL_Images"

def is_valid_image(path):
    if not path.exists() or path.stat().st_size == 0:
        return False
    return imghdr.what(path) is not None

bad_paths = [Path(x.strip()) for x in BAD_LIST.read_text().splitlines() if x.strip()]

fixed = 0
failed = []

for path in bad_paths:
    filename = path.name

    # Strip wordpress thumbnail suffixes
    original = re.sub(r'-\d+x\d+(?=\.)', '', filename)

    candidates = [
        filename,
        original,
        original.replace(".PNG", ".png"),
        original.replace(".png", ".PNG"),
    ]

    success = False

    for candidate in candidates:
        url = f"{MIRROR}/{candidate}"

        print(f"Trying: {url}")

        result = subprocess.run(
            ["curl", "-L", "--fail", "--silent", "--show-error", url, "-o", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode == 0 and is_valid_image(path):
            print(f"Fixed: {filename}")
            fixed += 1
            success = True
            break

    if not success:
        failed.append(str(path))

Path("still-bad-after-originals.txt").write_text("\n".join(failed))

print(f"\nFixed: {fixed}")
print(f"Still failed: {len(failed)}")

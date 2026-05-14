from pathlib import Path
import imghdr

bad = []

for f in Path("web.archive.org").rglob("*"):
    if f.is_file() and f.suffix.lower() in [".png",".jpg",".jpeg",".gif",".webp",".svg"]:
        try:
            if f.suffix.lower() == ".svg":
                text = f.read_text(errors="ignore")[:200]
                if "<svg" not in text:
                    bad.append(str(f))
            else:
                if imghdr.what(f) is None:
                    bad.append(str(f))
        except:
            bad.append(str(f))

print(f"Invalid images: {len(bad)}")

Path("bad-images.txt").write_text("\n".join(bad))

for b in bad[:50]:
    print(b)

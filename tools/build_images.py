"""Rebuild assets/img/ from the camera originals in originals/.

The originals are 1-7 MB camera files. Each project photo becomes a 1800px
lightbox copy and a 900px card copy, both WebP. Run from the repo root:

    python3 tools/build_images.py

Requires `cwebp` (brew install webp) and macOS `sips`. Pillow is only needed
for the plan-sheet crop.

To add a project: drop the photo in originals/, add an entry to GALLERIES with
the new slug, rerun, then add the matching card in index.html and the detail
entry in assets/js/projects.js.
"""
import os
import subprocess
import sys

SRC = "originals"
OUT = "assets/img"

# slug -> ordered source files; the first entry becomes the card image.
GALLERIES = {
    "ne-124th-subdivision": [
        "IMG_7035.JPG", "IMG_6725.JPG", "IMG_6731.JPG", "IMG_7040.JPG",
    ],
    "kalama-parking-trail": [
        "IMG_8036.JPG", "IMG_8016.jpeg", "IMG_8047.JPG", "IMG_8034.JPG",
    ],
    "burton-road-townhomes": ["IMG 22.JPG"],
    "iron-gate-4th": ["IMG 23.JPG"],
    "iron-gate-5th": ["IMG 24.JPG"],
    "longview-schools-pavement": ["IMG 17.JPG", "IMG 18.JPG", "IMG 16.JPG"],
    "longview-pedestrian-safety": ["IMG 19.JPG", "IMG 20.JPG"],
    "kalama-stair-repair": ["IMG 21.JPG"],
    "kalama-building-7412": ["IMG 10.JPG"],
    "kalama-pump-station": ["IMG 11.JPG"],
    "spcc-plans": ["IMG 12.JPG", "IMG 14.jpg", "IMG 15.JPG"],
    "alliance-industrial": ["IMG 2.JPG", "IMG 1.JPG"],
    "cooks-hill-substation": ["IMG 3.JPG"],
    "buchan-industrial": ["IMG 4.JPG"],
    "pud-pole-yard": ["IMG 5.JPG", "IMG 6.JPG"],
    "pud-parking-lot": ["IMG 7.JPG"],
    "pud-fuel-island": ["IMG 8.JPG", "IMG 9.JPG"],
}

# name -> (source, width, quality); these are referenced directly in index.html.
SINGLES = {
    "hero": ("IMG_8036.JPG", 2400, 74),
    "bob": ("bob_profile.jpg", 900, 84),
}

PLAN_SRC = "7-STORM PLAN.jpg"
# Fraction of the sheet to keep. The right-hand title block is cropped off
# because it carries the office address and email.
PLAN_BOX = (0.011, 0.012, 0.892, 0.988)

FULL_W, FULL_Q = 1800, 80
CARD_W, CARD_Q = 900, 76


def dims(path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        capture_output=True, text=True, check=True).stdout
    vals = dict(
        (k.strip(), v.strip())
        for k, v in (line.split(":", 1) for line in out.splitlines() if ":" in line))
    return int(vals["pixelWidth"]), int(vals["pixelHeight"])


def encode(src, dst, width, quality):
    w, _ = dims(src)
    subprocess.run(
        ["cwebp", "-quiet", "-q", str(quality), "-resize", str(min(width, w)), "0",
         "-m", "6", src, "-o", dst], check=True)


def build_plan_sheet():
    from PIL import Image

    src = os.path.join(SRC, PLAN_SRC)
    im = Image.open(src)
    w, h = im.size
    x0, y0, x1, y1 = PLAN_BOX
    crop = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    tmp = os.path.join(OUT, "_plan-crop.png")
    crop.save(tmp)
    encode(tmp, f"{OUT}/plan-sheet.webp", 2000, 84)
    os.remove(tmp)
    print("plan-sheet: cropped and encoded")


def main():
    os.makedirs(OUT, exist_ok=True)

    for slug, sources in GALLERIES.items():
        for i, name in enumerate(sources, 1):
            src = os.path.join(SRC, name)
            if not os.path.exists(src):
                sys.exit(f"missing source: {src}")
            encode(src, f"{OUT}/{slug}-{i}.webp", FULL_W, FULL_Q)
            encode(src, f"{OUT}/{slug}-{i}-sm.webp", CARD_W, CARD_Q)
        print(f"{slug}: {len(sources)} image(s)")

    for name, (source, width, quality) in SINGLES.items():
        encode(os.path.join(SRC, source), f"{OUT}/{name}.webp", width, quality)
        print(f"{name}: encoded")

    build_plan_sheet()


if __name__ == "__main__":
    main()

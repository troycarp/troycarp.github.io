"""Key the white background out of the CEI logo TIFs and emit transparent PNGs.

The source art is two flat brand colours antialiased over white, so we snap each
pixel back to its brand colour and derive alpha from how far it sits from white.
"""
import os
import sys

from PIL import Image

TAUPE = (0x59, 0x50, 0x4B)
CRIMSON = (0xA6, 0x22, 0x39)
# Luminance of the two brand colours -- the "fully opaque" reference point.
CORE_DISTANCE = 175.0


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def key(src, dst, force=None, scale=None):
    im = Image.open(src).convert("RGB")
    if scale:
        im = im.resize(scale, Image.LANCZOS)
    out = Image.new("RGBA", im.size)
    px, op = im.load(), out.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            dist = 255.0 - lum((r, g, b))
            if dist < 4:
                op[x, y] = (0, 0, 0, 0)
                continue
            alpha = min(255, round(dist * 255.0 / CORE_DISTANCE))
            chroma = max(r, g, b) - min(r, g, b)
            colour = force or (CRIMSON if chroma / dist > 0.3 else TAUPE)
            op[x, y] = (*colour, alpha)
    out.save(dst)
    print(f"{dst}  {w}x{h}")


SRC = "originals"

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "assets/brand"
    os.makedirs(base, exist_ok=True)
    key(f"{SRC}/CEI Logo.tif", f"{base}/logo.png")
    key(f"{SRC}/CEI Logo.tif", f"{base}/logo-white.png", force=(255, 255, 255))
    key(f"{SRC}/CEI Logomark.tif", f"{base}/logomark.png")
    key(f"{SRC}/CEI Logomark.tif", f"{base}/logomark-white.png", force=(255, 255, 255))

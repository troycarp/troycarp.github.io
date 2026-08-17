"""Generate favicons and the Open Graph share card from the brand assets."""
from PIL import Image, ImageDraw

TAUPE = (0x59, 0x50, 0x4B)
CRIMSON = (0xA6, 0x22, 0x39)
BRAND = "assets/brand"
IMG = "assets/img"


def favicon(size, pad_ratio=0.16):
    canvas = Image.new("RGBA", (size, size), (*TAUPE, 255))
    mark = Image.open(f"{BRAND}/logomark-white.png").convert("RGBA")
    inner = int(size * (1 - pad_ratio * 2))
    w = inner
    h = round(mark.height * w / mark.width)
    mark = mark.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(mark, ((size - w) // 2, (size - h) // 2))
    return canvas


def og_card():
    W, H = 1200, 630
    photo = Image.open(f"{IMG}/hero.webp").convert("RGB")
    scale = max(W / photo.width, H / photo.height)
    photo = photo.resize(
        (round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
    left = (photo.width - W) // 2
    top = round((photo.height - H) * 0.45)
    card = photo.crop((left, top, left + W, top + H)).convert("RGBA")

    # Darken from the bottom so the wordmark stays legible over the water.
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(scrim)
    for y in range(H):
        t = y / H
        dr.line([(0, y), (W, y)], fill=(26, 23, 22, int(235 * t ** 1.6)))
    card.alpha_composite(scrim)

    logo = Image.open(f"{BRAND}/logo-white.png").convert("RGBA")
    lw = 620
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    card.alpha_composite(logo, (80, H - 80 - logo.height - 46))

    rule = ImageDraw.Draw(card)
    rule.rectangle([80, H - 74, 80 + 96, H - 70], fill=(*CRIMSON, 255))
    return card.convert("RGB")


if __name__ == "__main__":
    favicon(32).save(f"{BRAND}/favicon-32.png")
    favicon(180, pad_ratio=0.20).save(f"{BRAND}/apple-touch-icon.png")
    favicon(512, pad_ratio=0.20).save(f"{BRAND}/icon-512.png")
    og_card().save(f"{IMG}/share-card.jpg", quality=88, optimize=True)
    print("meta assets written")

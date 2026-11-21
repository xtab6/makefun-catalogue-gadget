#!/usr/bin/env python3
"""Render the catalogue photograph: CHRONOTOAST Model CT-1.

A chrome toaster whose slots pop golden toast slices shaped like clock
faces, with a small analog clock dial on its side and a butter dish as the
single accessory. Studio product shot: soft warm-grey seamless backdrop,
pedestal, soft floor shadow, catalogue caption bar at the bottom.

Deterministic: no randomness, no timestamps in pixels. Run twice and the
output bytes must be identical. Visually verified 2026-11-21: chrome
toaster hero, clock-face toast slices, butter-dish accessory, caption bar
clear of the gadget.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.jpg")


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(size, bold=False):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rounded(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def clock_face(draw, cx, cy, r, hour_angle, minute_angle):
    """Cream clock face with ticks and two hands."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 244, 230),
                 outline=(60, 50, 35), width=3)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        inner = r - (10 if i % 3 == 0 else 6)
        x0, y0 = cx + inner * math.cos(a), cy + inner * math.sin(a)
        x1, y1 = cx + (r - 3) * math.cos(a), cy + (r - 3) * math.sin(a)
        draw.line([x0, y0, x1, y1], fill=(60, 50, 35), width=3 if i % 3 == 0 else 2)
    for ang, length, width in ((hour_angle, r * 0.48, 5),
                               (minute_angle, r * 0.72, 4)):
        a = math.radians(ang - 90)
        draw.line([cx, cy, cx + length * math.cos(a), cy + length * math.sin(a)],
                  fill=(40, 35, 30), width=width)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(40, 35, 30))


def toast_slice(draw, x, y, w, h, hour_angle, minute_angle):
    """Golden toast slice with a clock face baked into it."""
    # Crust
    rounded(draw, [x, y, x + w, y + h], radius=34,
            fill=(176, 118, 48), outline=(120, 76, 26), width=4)
    # Crumb
    rounded(draw, [x + 12, y + 12, x + w - 12, y + h - 12], radius=26,
            fill=(232, 190, 110))
    # Clock face in the middle
    clock_face(draw, x + w // 2, y + h // 2, min(w, h) // 2 - 26,
               hour_angle, minute_angle)


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- seamless studio backdrop: warm light-grey vertical gradient ---
    top, bottom = (238, 233, 226), (196, 188, 178)
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=lerp(top, bottom, y / H))

    # --- floor: slightly darker band from y=800 down, with a soft horizon ---
    for y in range(800, H):
        t = (y - 800) / (H - 800)
        draw.line([(0, y), (W, y)], fill=lerp((206, 198, 188), (178, 169, 158), t))
    draw.line([(0, 800), (W, 800)], fill=(170, 161, 150), width=2)

    # --- soft floor shadow under the pedestal (blurred ellipse) ---
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([212, 770, 812, 838], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- pedestal: light stone slab ---
    rounded(draw, [232, 700, 792, 806], radius=14, fill=(226, 221, 212),
            outline=(180, 172, 160), width=2)
    draw.line([(232, 712), (792, 712)], fill=(255, 255, 255), width=3)

    # --- toast slices popping out of the slots (behind the body top) ---
    toast_slice(draw, 372, 268, 118, 148, hour_angle=310, minute_angle=55)
    toast_slice(draw, 534, 252, 118, 164, hour_angle=55, minute_angle=340)

    # --- toaster body: polished chrome, vertical brushed gradient ---
    body = [332, 400, 692, 700]
    for y in range(body[1], body[3] + 1):
        t = (y - body[1]) / (body[3] - body[1])
        # chrome: bright top, mid sheen, darker base
        if t < 0.45:
            c = lerp((245, 246, 248), (196, 200, 206), t / 0.45)
        else:
            c = lerp((196, 200, 206), (148, 152, 160), (t - 0.45) / 0.55)
        draw.line([(body[0] + 14, y), (body[2] - 14, y)], fill=c)
    # chrome highlight stripe down the left third
    for x in range(372, 402):
        a = int(70 * (1 - abs(x - 387) / 15))
        draw.line([(x, 414), (x, 686)], fill=(255, 255, 255, a))
    # rounded outline + top slot plate
    draw.rounded_rectangle(body, radius=42, outline=(110, 114, 122), width=4)
    rounded(draw, [348, 400, 676, 436], radius=18, fill=(96, 100, 108))
    # slots
    rounded(draw, [380, 410, 500, 428], radius=8, fill=(30, 32, 36))
    rounded(draw, [524, 410, 644, 428], radius=8, fill=(30, 32, 36))

    # --- small analog clock dial on the toaster front ---
    clock_face(draw, 512, 560, 62, hour_angle=300, minute_angle=20)
    # dial label under the clock
    draw.text((512, 632), "CHRONO", font=font(20, bold=True),
              fill=(70, 72, 78), anchor="mm")

    # --- browning lever on the right side + red indicator ---
    rounded(draw, [692, 500, 716, 540], radius=8, fill=(70, 74, 82))
    draw.ellipse([700, 566, 716, 582], fill=(210, 60, 40), outline=(150, 30, 20), width=2)

    # --- feet ---
    rounded(draw, [372, 700, 412, 712], radius=5, fill=(60, 62, 66))
    rounded(draw, [612, 700, 652, 712], radius=5, fill=(60, 62, 66))

    # --- ONE accessory: butter dish with a pat of butter, right of pedestal ---
    # dish shadow
    dish_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dish_shadow)
    dd.ellipse([788, 756, 962, 792], fill=(0, 0, 0, 70))
    dish_shadow = dish_shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(Image.alpha_composite(img.convert("RGBA"), dish_shadow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    # white dish
    rounded(draw, [800, 716, 952, 766], radius=12, fill=(248, 247, 243),
            outline=(200, 194, 184), width=2)
    draw.line([(800, 730), (952, 730)], fill=(220, 214, 204), width=2)
    # pat of butter
    rounded(draw, [838, 686, 914, 722], radius=8, fill=(250, 214, 90),
            outline=(214, 164, 40), width=2)
    draw.line([(852, 694), (900, 694)], fill=(255, 236, 150), width=4)

    # --- caption bar: catalogue style, charcoal band at the bottom ---
    draw.rectangle([0, 884, W, H], fill=(44, 42, 40))
    draw.line([(0, 884), (W, 884)], fill=(250, 214, 90), width=4)
    draw.text((512, 922), "CHRONOTOAST  Model CT-1",
              font=font(40, bold=True), fill=(250, 246, 238), anchor="mm")
    draw.text((512, 972), "Toasts yesterday's bread, tomorrow.",
              font=font(30), fill=(196, 188, 176), anchor="mm")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "JPEG", quality=88, optimize=True, progressive=False)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()

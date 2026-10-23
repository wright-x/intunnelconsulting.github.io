#!/usr/bin/env python3
"""Builds uniform-print logo assets for The Theater x Indian Kitchen Sapa:

1. A VERTICAL combined lockup (THE THEATER on top, INDIAN KITCHEN below),
   subtext (the "INDIAN KITCHEN & BAR" tagline, "SAPA" and "SOUL OF INDIA"
   lines) stripped out so only the two main wordmarks remain.
2. A standalone vertical INDIAN KITCHEN logo (lotus mark + wordmark only,
   no subtext) sized for a service-staff shirt hem.

Each asset is exported as a transparent PNG and a print-ready PDF, in both
black ink (light fabric) and white ink (dark fabric).
"""
import io
import os

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont

ITALIC_FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
BOLD_FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
REGULAR_FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

THEATER_LOGO = "/home/user/intunnelconsulting.github.io/theater-menu-photography/references/brand-logo-alpha.png"
IK_LOGO_PDF = "/root/.claude/uploads/b07b59c1-87c7-5e01-8e75-ec8db4f2484f/2191dd6d-Indian_Kitchen_Sapa_Logo_Corrected_Print_Ready.pdf"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def recolor(im, ink, luminance_cutoff=235):
    """Flatten an RGBA logo to a single flat ink color, keeping its shape."""
    im = im.convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    luminance = rgb.mean(axis=2)
    mask = (alpha > 10) & (luminance < luminance_cutoff)
    out = np.zeros_like(arr)
    out[:, :, 0] = ink[0]
    out[:, :, 1] = ink[1]
    out[:, :, 2] = ink[2]
    out[:, :, 3] = np.where(mask, alpha, 0).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def ink_bands(im, gap=15):
    """Row ranges that contain any non-transparent ink, grouped into bands
    separated by vertical gaps (used to isolate wordmark lines from
    subtext lines stacked beneath them)."""
    alpha = np.array(im.split()[-1])
    rows = np.where(alpha.sum(axis=1) > 0)[0]
    bands, start, prev = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - prev > gap:
            bands.append((start, prev))
            start = r
        prev = r
    bands.append((start, prev))
    return bands


def crop_bands(im, keep, pad=20):
    bands = ink_bands(im)
    y0 = max(0, bands[0][0] - pad)
    y1 = min(im.height, bands[keep - 1][1] + pad)
    return im.crop((0, y0, im.width, y1))


def remove_star(im):
    """Clear the small star glyph beneath the 'A' in THE THEATER wordmark,
    identified by its isolated bounding box in the source asset."""
    im = im.copy()
    arr = np.array(im)
    arr[725:815, 925:1085, 3] = 0
    return Image.fromarray(arr, "RGBA")


def tight_crop(im, pad=20):
    alpha = np.array(im.split()[-1])
    ys, xs = np.where(alpha > 10)
    y0, y1 = max(0, ys.min() - pad), min(im.height, ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(im.width, xs.max() + pad)
    return im.crop((x0, y0, x1, y1))


def load_ik_logo():
    doc = pymupdf.open(IK_LOGO_PDF)
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(6, 6), alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def load_theater_logo():
    return Image.open(THEATER_LOGO)


def scale_to_width(im, target_w):
    w, h = im.size
    new_h = int(h * target_w / w)
    return im.resize((target_w, new_h), Image.LANCZOS)


def save_png_and_pdf(im, out_png, out_pdf, dpi=600):
    im.save(out_png, dpi=(dpi, dpi))
    print(f"Saved {out_png} ({im.width}x{im.height}px)")
    page_w_pt = im.width * 72 / dpi
    page_h_pt = im.height * 72 / dpi
    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page(width=page_w_pt, height=page_h_pt)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    page.insert_image(pymupdf.Rect(0, 0, page_w_pt, page_h_pt), stream=buf.getvalue())
    pdf_doc.save(out_pdf)
    print(f"Saved {out_pdf} ({page_w_pt/72:.2f}in x {page_h_pt/72:.2f}in @ {dpi}dpi)")


def build_vertical_combined(ink, suffix):
    # THE THEATER: keep "THE" + "THEATER", drop the star and the tagline.
    theater = recolor(load_theater_logo(), ink)
    theater = crop_bands(theater, keep=3)  # THE / THEATER / star band
    theater = remove_star(theater)
    theater = tight_crop(theater)

    # INDIAN KITCHEN: keep the lotus mark + "INDIAN KITCHEN", drop SAPA /
    # SOUL OF INDIA.
    ik = recolor(load_ik_logo(), ink)
    ik = crop_bands(ik, keep=2)  # lotus mark / INDIAN KITCHEN
    ik = tight_crop(ik)

    target_w = 1600
    theater = scale_to_width(theater, target_w)
    ik = scale_to_width(ik, target_w)

    # "x" divider between the two wordmarks, in place of a rule line.
    div_h = int(theater.height * 0.4)
    font = ImageFont.truetype(ITALIC_FONT, div_h)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)
    bbox = tdraw.textbbox((0, 0), "x", font=font)
    div_w = bbox[2] - bbox[0]
    divider = Image.new("RGBA", (div_w + 20, bbox[3] - bbox[1] + 20), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(divider)
    ddraw.text((10 - bbox[0], 10 - bbox[1]), "x", font=font, fill=ink)

    margin_v = 55
    total_h = theater.height + margin_v * 2 + divider.height + margin_v * 2 + ik.height
    canvas = Image.new("RGBA", (target_w, total_h), (0, 0, 0, 0))
    canvas.paste(theater, (0, 0), theater)

    div_y = theater.height + margin_v
    div_x = (target_w - divider.width) // 2
    canvas.paste(divider, (div_x, div_y), divider)

    ik_y = div_y + divider.height + margin_v
    ik_x = (target_w - ik.width) // 2
    canvas.paste(ik, (ik_x, ik_y), ik)

    margin = int(target_w * 0.12)
    framed = Image.new("RGBA", (canvas.width + margin * 2, canvas.height + margin * 2), (0, 0, 0, 0))
    framed.paste(canvas, (margin, margin), canvas)

    save_png_and_pdf(
        framed,
        os.path.join(OUT_DIR, f"theater-x-indian-kitchen-vertical-{suffix}.png"),
        os.path.join(OUT_DIR, f"theater-x-indian-kitchen-vertical-{suffix}.pdf"),
    )


def extract_lotus_mark(ink):
    """Just the lotus + bar icon from the IK logo, no wordmark at all."""
    ik = recolor(load_ik_logo(), ink)
    bands = ink_bands(ik)
    y0 = max(0, bands[0][0] - 10)
    y1 = min(ik.height, bands[0][1] + 10)
    lotus = ik.crop((0, y0, ik.width, y1))
    return tight_crop(lotus)


def build_ik_hem_logo(ink, suffix):
    """A truly vertical lockup for a shirt hem: the lotus mark on top,
    then every letter of 'INDIAN KITCHEN' stacked one below the other in
    a single narrow column, with a small gap between the two words."""
    lotus = extract_lotus_mark(ink)

    letter_w = 420
    font = ImageFont.truetype(BOLD_FONT, int(letter_w * 0.85))
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)

    def letter_img(ch):
        bbox = tdraw.textbbox((0, 0), ch, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 10
        glyph = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glyph)
        gdraw.text((pad - bbox[0], pad - bbox[1]), ch, font=font, fill=ink)
        return tight_crop(glyph, pad=4)

    word_gap = 36
    letter_gap = 14
    letters = []
    for word_i, word in enumerate("INDIAN KITCHEN".split(" ")):
        if word_i > 0:
            letters.append(None)  # marks an extra gap between words
        for ch in word:
            letters.append(letter_img(ch))

    col_w = max(g.width for g in letters if g is not None)
    rows = []
    for g in letters:
        if g is None:
            rows.append(("gap", word_gap))
        else:
            rows.append(("letter", g))

    total_h = sum(
        (r[1] if r[0] == "gap" else r[1].height) + (0 if r[0] == "gap" else letter_gap)
        for r in rows
    )
    letters_canvas = Image.new("RGBA", (col_w, total_h), (0, 0, 0, 0))
    y = 0
    for kind, val in rows:
        if kind == "gap":
            y += val
        else:
            x = (col_w - val.width) // 2
            letters_canvas.paste(val, (x, y), val)
            y += val.height + letter_gap
    letters_canvas = letters_canvas.crop((0, 0, col_w, max(0, y - letter_gap)))

    lotus = scale_to_width(lotus, int(col_w * 1.5))
    gap_lotus = 40
    total_w = max(lotus.width, letters_canvas.width)
    total_h2 = lotus.height + gap_lotus + letters_canvas.height
    canvas = Image.new("RGBA", (total_w, total_h2), (0, 0, 0, 0))
    canvas.paste(lotus, ((total_w - lotus.width) // 2, 0), lotus)
    canvas.paste(letters_canvas, ((total_w - letters_canvas.width) // 2, lotus.height + gap_lotus), letters_canvas)

    margin = int(total_w * 0.25)
    framed = Image.new("RGBA", (canvas.width + margin * 2, canvas.height + margin * 2), (0, 0, 0, 0))
    framed.paste(canvas, (margin, margin), canvas)

    save_png_and_pdf(
        framed,
        os.path.join(OUT_DIR, f"indian-kitchen-hem-logo-{suffix}.png"),
        os.path.join(OUT_DIR, f"indian-kitchen-hem-logo-{suffix}.pdf"),
    )


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for ink, suffix in [((20, 20, 20, 255), "black"), ((255, 255, 255, 255), "white")]:
        build_vertical_combined(ink, suffix)
        build_ik_hem_logo(ink, suffix)

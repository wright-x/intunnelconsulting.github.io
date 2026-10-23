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
from PIL import Image

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
    # THE THEATER: keep "THE" + "THEATER" + star, drop the tagline band.
    theater = recolor(load_theater_logo(), ink)
    theater = crop_bands(theater, keep=3)  # THE / THEATER / star
    theater = tight_crop(theater)

    # INDIAN KITCHEN: keep the lotus mark + "INDIAN KITCHEN", drop SAPA /
    # SOUL OF INDIA.
    ik = recolor(load_ik_logo(), ink)
    ik = crop_bands(ik, keep=2)  # lotus mark / INDIAN KITCHEN
    ik = tight_crop(ik)

    target_w = 1600
    theater = scale_to_width(theater, target_w)
    ik = scale_to_width(ik, target_w)

    gap = 70
    rule_h = 6
    rule_margin = 50
    total_h = theater.height + rule_margin * 2 + rule_h + rule_margin * 2 + ik.height
    canvas = Image.new("RGBA", (target_w, total_h), (0, 0, 0, 0))
    canvas.paste(theater, (0, 0), theater)

    rule_y = theater.height + rule_margin
    rule_w = int(target_w * 0.3)
    rule_x = (target_w - rule_w) // 2
    for yy in range(rule_y, rule_y + rule_h):
        for xx in range(rule_x, rule_x + rule_w):
            canvas.putpixel((xx, yy), ink)

    ik_y = rule_y + rule_h + rule_margin
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


def build_ik_hem_logo(ink, suffix):
    ik = recolor(load_ik_logo(), ink)
    ik = crop_bands(ik, keep=2)  # lotus mark / INDIAN KITCHEN only
    ik = tight_crop(ik)

    target_w = 1400
    ik = scale_to_width(ik, target_w)

    margin = int(target_w * 0.15)
    framed = Image.new("RGBA", (ik.width + margin * 2, ik.height + margin * 2), (0, 0, 0, 0))
    framed.paste(ik, (margin, margin), ik)

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

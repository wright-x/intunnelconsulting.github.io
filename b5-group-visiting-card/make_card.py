#!/usr/bin/env python3
"""Builds the B5 Group visiting card: a premium, flat-graphic, slim
vertical card listing all three group brands (Bottega5, The Theater,
Indian Kitchen Sapa) top to bottom, each with its logo mark, address,
phone, email and a scannable QR code to its Google Maps listing.

Exports a high-res PNG and a print-ready single-page PDF at 300dpi.
"""
import io
import os
import urllib.parse

import numpy as np
import pymupdf
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")
OUT_DIR = os.path.join(BASE, "output")

THEATER_LOGO = "/home/user/intunnelconsulting.github.io/theater-menu-photography/references/brand-logo-alpha.png"
IK_LOGO_PDF = "/root/.claude/uploads/b07b59c1-87c7-5e01-8e75-ec8db4f2484f/2191dd6d-Indian_Kitchen_Sapa_Logo_Corrected_Print_Ready.pdf"

DPI = 300
MM = DPI / 25.4
CARD_W = int(55 * MM)
CARD_H = int(170 * MM)

# ---- palette: warm charcoal + brass gold + cream, flat, no gradients ----
BG = (23, 20, 16, 255)
GOLD = (196, 160, 102, 255)
GOLD_DIM = (140, 114, 72, 255)
CREAM = (238, 229, 211, 255)
CREAM_DIM = (178, 170, 154, 255)
RULE = (90, 78, 58, 255)

F_MASTHEAD = os.path.join(FONTS, "BigShoulders-Bold.ttf")
F_BRAND = os.path.join(FONTS, "Gloock-Regular.ttf")
F_TAGLINE = os.path.join(FONTS, "CrimsonPro-Italic.ttf")
F_LABEL = os.path.join(FONTS, "WorkSans-Bold.ttf")
F_BODY = os.path.join(FONTS, "WorkSans-Regular.ttf")

BRANDS = [
    {
        "key": "bottega5",
        "wordmark": "BOTTEGA5",
        "tagline": "ITALIAN KITCHEN",
        "address": "106 Tran Bach Dang, Bac My An,\nNgu Hanh Son, Da Nang, Vietnam",
        "phone": "+84 917 963 400",
        "email": "infobottega5@gmail.com",
        "maps_query": "Bottega5, 106 Tran Bach Dang, Ngu Hanh Son, Da Nang, Vietnam",
    },
    {
        "key": "theater",
        "wordmark": None,  # drawn from the existing logo asset
        "tagline": "INDIAN KITCHEN & BAR",
        "address": "42 Ngo Thi Si, Bac My An,\nNgu Hanh Son, Da Nang, Vietnam",
        "phone": "+84 32 755 5786",
        "email": "indiankitchensapa@gmail.com",
        "maps_query": "The Theater Indian Kitchen & Bar, 42 Ngo Thi Si, Da Nang, Vietnam",
    },
    {
        "key": "indian_kitchen",
        "wordmark": None,  # drawn from the existing logo asset
        "tagline": "SOUL OF INDIA",
        "address": "42 Ngo Thi Si, Bac My An,\nNgu Hanh Son, Da Nang, Vietnam",
        "phone": "+84 034 818 0134",
        "email": "indiankitchensapa@gmail.com",
        "maps_query": "Indian Kitchen Sapa, 42 Ngo Thi Si, Da Nang, Vietnam",
    },
]


# ---------------------------------------------------------------- helpers
def recolor(im, ink, luminance_cutoff=235):
    im = im.convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    luminance = rgb.mean(axis=2)
    mask = (alpha > 10) & (luminance < luminance_cutoff)
    out = np.zeros_like(arr)
    out[:, :, 0], out[:, :, 1], out[:, :, 2] = ink[0], ink[1], ink[2]
    out[:, :, 3] = np.where(mask, alpha, 0).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def ink_bands(im, gap=15):
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


def remove_star(im):
    im = im.copy()
    arr = np.array(im)
    arr[725:815, 925:1085, 3] = 0
    return Image.fromarray(arr, "RGBA")


def scale_to_width(im, target_w):
    w, h = im.size
    return im.resize((target_w, int(h * target_w / w)), Image.LANCZOS)


def scale_to_height(im, target_h):
    w, h = im.size
    return im.resize((int(w * target_h / h), target_h), Image.LANCZOS)


def load_ik_logo():
    doc = pymupdf.open(IK_LOGO_PDF)
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(6, 6), alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def theater_wordmark(ink, target_w):
    im = recolor(Image.open(THEATER_LOGO), ink)
    im = crop_bands(im, keep=3)  # THE / THEATER / star band
    im = remove_star(im)
    im = tight_crop(im)
    return scale_to_width(im, target_w)


def ik_mark(ink, target_w):
    """Lotus mark + INDIAN KITCHEN wordmark, no SAPA/SOUL OF INDIA."""
    im = recolor(load_ik_logo(), ink)
    im = crop_bands(im, keep=2)
    im = tight_crop(im)
    return scale_to_width(im, target_w)


def text_img(text, font_path, size, fill, tracking=0, pad=6):
    font = ImageFont.truetype(font_path, size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    if tracking == 0:
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        glyph = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=fill)
        return glyph
    # manual letter-spacing
    widths = []
    for ch in text:
        bbox = d.textbbox((0, 0), ch, font=font)
        widths.append(bbox[2] - bbox[0])
    bbox_full = d.textbbox((0, 0), text, font=font)
    h = bbox_full[3] - bbox_full[1]
    total_w = sum(widths) + tracking * (len(text) - 1)
    glyph = Image.new("RGBA", (total_w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glyph)
    x = pad
    for ch, w in zip(text, widths):
        cb = d.textbbox((0, 0), ch, font=font)
        gd.text((x - cb[0], pad - bbox_full[1]), ch, font=font, fill=fill)
        x += w + tracking
    return glyph


def multiline_text_img(text, font_path, size, fill, line_gap=6, pad=4):
    font = ImageFont.truetype(font_path, size)
    lines = text.split("\n")
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    line_imgs = []
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        li = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        ld = ImageDraw.Draw(li)
        ld.text((pad - bbox[0], pad - bbox[1]), line, font=font, fill=fill)
        line_imgs.append(li)
    width = max(li.width for li in line_imgs)
    height = sum(li.height for li in line_imgs) + line_gap * (len(line_imgs) - 1)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    y = 0
    for li in line_imgs:
        out.paste(li, (0, y), li)
        y += li.height + line_gap
    return out


def make_qr(data, box_size=10, border=2):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(23, 20, 16), back_color=(238, 229, 211)).convert("RGBA")
    return img


def hline(draw, x0, x1, y, color, width=2):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


# ------------------------------------------------------------------ build
def build_front():
    """Cover side: B5 Group identity alone, generous negative space."""
    canvas = Image.new("RGBA", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(canvas)
    margin = int(5.5 * MM)
    content_w = CARD_W - margin * 2

    # small centerpiece lotus-free flat ornament: a thin diamond made of
    # two hairline rules, echoing the sister brands' gold linework.
    cx = CARD_W // 2
    top_y = int(46 * MM)
    diamond_r = int(3.2 * MM)
    draw.line([(cx - diamond_r, top_y), (cx, top_y - diamond_r), (cx + diamond_r, top_y), (cx, top_y + diamond_r), (cx - diamond_r, top_y)], fill=GOLD_DIM, width=2)

    y = top_y + diamond_r + int(7 * MM)
    masthead = text_img("B5", F_MASTHEAD, int(16 * MM), GOLD, tracking=int(1.6 * MM))
    canvas.paste(masthead, ((CARD_W - masthead.width) // 2, y), masthead)
    y += masthead.height + int(1 * MM)

    group_word = text_img("GROUP", F_MASTHEAD, int(6.4 * MM), GOLD, tracking=int(2.6 * MM))
    canvas.paste(group_word, ((CARD_W - group_word.width) // 2, y), group_word)
    y += group_word.height + int(5 * MM)

    hline(draw, cx - int(10 * MM), cx + int(10 * MM), y, RULE, width=2)
    y += int(5 * MM)

    tagline = text_img("HOSPITALITY · CATERING · RESTAURANTS", F_LABEL, int(2.5 * MM), CREAM_DIM, tracking=int(0.3 * MM))
    if tagline.width > content_w:
        tagline = scale_to_width(tagline, content_w)
    canvas.paste(tagline, ((CARD_W - tagline.width) // 2, y), tagline)
    y += tagline.height + int(16 * MM)

    hline(draw, cx - int(6 * MM), cx + int(6 * MM), y, RULE, width=1)
    y += int(16 * MM)

    desc = (
        "A Da Nang hospitality collective crafting\n"
        "distinctive restaurants, bars and catering\n"
        "experiences — BOTTEGA5, THE THEATER and\n"
        "INDIAN KITCHEN SAPA."
    )
    desc_img = multiline_text_img(desc, F_TAGLINE, int(3.0 * MM), CREAM_DIM, line_gap=int(1.3 * MM))
    if desc_img.width > content_w:
        desc_img = scale_to_width(desc_img, content_w)
    canvas.paste(desc_img, ((CARD_W - desc_img.width) // 2, y), desc_img)

    footer = text_img("DA NANG, VIETNAM", F_LABEL, int(2.2 * MM), CREAM_DIM, tracking=int(0.5 * MM))
    canvas.paste(footer, ((CARD_W - footer.width) // 2, CARD_H - margin - footer.height), footer)

    return canvas


def build_back():
    """Directory side: all three brands stacked top to bottom."""
    canvas = Image.new("RGBA", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(canvas)

    margin = int(5.5 * MM)
    content_w = CARD_W - margin * 2
    y = int(7 * MM)

    eyebrow = text_img("OUR BRANDS", F_LABEL, int(2.6 * MM), GOLD_DIM, tracking=int(0.8 * MM))
    canvas.paste(eyebrow, ((CARD_W - eyebrow.width) // 2, y), eyebrow)
    y += eyebrow.height + int(3.5 * MM)
    hline(draw, margin, CARD_W - margin, y, RULE, width=2)
    y += int(6 * MM)

    # ---- brand blocks ----
    qr_size = int(13.5 * MM)
    for i, b in enumerate(BRANDS):
        if b["key"] == "bottega5":
            wm = text_img(b["wordmark"], F_BRAND, int(7.2 * MM), GOLD, tracking=int(0.15 * MM))
            if wm.width > content_w:
                wm = scale_to_width(wm, content_w)
        elif b["key"] == "theater":
            wm = theater_wordmark(GOLD, content_w)
        else:
            wm = ik_mark(GOLD, int(content_w * 0.62))

        canvas.paste(wm, ((CARD_W - wm.width) // 2, y), wm)
        y += wm.height + int(1.6 * MM)

        tg = text_img(b["tagline"], F_LABEL, int(2.4 * MM), GOLD_DIM, tracking=int(0.45 * MM))
        canvas.paste(tg, ((CARD_W - tg.width) // 2, y), tg)
        y += tg.height + int(3.6 * MM)

        # address / phone / email block (left) + QR (right)
        block_top = y
        text_w = content_w - qr_size - int(4 * MM)

        addr_img = multiline_text_img(b["address"], F_BODY, int(2.55 * MM), CREAM, line_gap=int(1.0 * MM))
        if addr_img.width > text_w:
            addr_img = scale_to_width(addr_img, text_w)
        canvas.paste(addr_img, (margin, y), addr_img)
        y += addr_img.height + int(2.0 * MM)

        phone_img = text_img(b["phone"], F_BODY, int(2.6 * MM), CREAM)
        if phone_img.width > text_w:
            phone_img = scale_to_width(phone_img, text_w)
        canvas.paste(phone_img, (margin, y), phone_img)
        y += phone_img.height + int(1.6 * MM)

        email_img = text_img(b["email"], F_BODY, int(2.55 * MM), CREAM)
        if email_img.width > text_w:
            email_img = scale_to_width(email_img, text_w)
        canvas.paste(email_img, (margin, y), email_img)
        y += email_img.height

        text_block_h = y - block_top

        maps_url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(b["maps_query"])
        qr = make_qr(maps_url)
        qr = qr.resize((qr_size, qr_size), Image.NEAREST)
        qr_x = CARD_W - margin - qr_size
        qr_y = block_top + max(0, (text_block_h - qr_size) // 2)
        # cream tile behind the QR for a clean frame + reliable scan contrast
        tile_pad = int(1.0 * MM)
        tile = Image.new("RGBA", (qr_size + tile_pad * 2, qr_size + tile_pad * 2), CREAM)
        canvas.paste(tile, (qr_x - tile_pad, qr_y - tile_pad), tile)
        canvas.paste(qr, (qr_x, qr_y), qr)
        scan_label = text_img("SCAN FOR DIRECTIONS", F_LABEL, int(1.5 * MM), GOLD_DIM, tracking=int(0.15 * MM))
        scan_label = scale_to_width(scan_label, min(scan_label.width, qr_size + tile_pad * 2))
        canvas.paste(scan_label, (qr_x - tile_pad + (qr_size + tile_pad * 2 - scan_label.width) // 2, qr_y + qr_size + tile_pad + int(0.8 * MM)), scan_label)

        y = max(y, qr_y + qr_size + tile_pad + int(0.8 * MM) + scan_label.height)
        y += int(5.5 * MM)

        if i < len(BRANDS) - 1:
            hline(draw, margin, CARD_W - margin, y, RULE, width=1)
            y += int(6 * MM)

    print(f"  back content bottom at y={y}px of {CARD_H}px ({y/MM:.1f}mm of {CARD_H/MM:.1f}mm)")
    return canvas


def save_png_and_pdf(im, out_png, out_pdf, dpi=DPI):
    im.convert("RGB").save(out_png, dpi=(dpi, dpi))
    print(f"Saved {out_png} ({im.width}x{im.height}px, {im.width/MM:.1f}mm x {im.height/MM:.1f}mm)")
    page_w_pt = im.width * 72 / dpi
    page_h_pt = im.height * 72 / dpi
    doc = pymupdf.open()
    page = doc.new_page(width=page_w_pt, height=page_h_pt)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    page.insert_image(pymupdf.Rect(0, 0, page_w_pt, page_h_pt), stream=buf.getvalue())
    doc.save(out_pdf)
    print(f"Saved {out_pdf}")


def save_two_sided_pdf(front, back, out_pdf, dpi=DPI):
    page_w_pt = front.width * 72 / dpi
    page_h_pt = front.height * 72 / dpi
    doc = pymupdf.open()
    for im in (front, back):
        page = doc.new_page(width=page_w_pt, height=page_h_pt)
        buf = io.BytesIO()
        im.convert("RGB").save(buf, format="PNG")
        page.insert_image(pymupdf.Rect(0, 0, page_w_pt, page_h_pt), stream=buf.getvalue())
    doc.save(out_pdf)
    print(f"Saved {out_pdf} (2 pages: front, back)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Building front...")
    front = build_front()
    print("Building back...")
    back = build_back()

    save_png_and_pdf(front, os.path.join(OUT_DIR, "b5-group-card-front.png"), os.path.join(OUT_DIR, "b5-group-card-front.pdf"))
    save_png_and_pdf(back, os.path.join(OUT_DIR, "b5-group-card-back.png"), os.path.join(OUT_DIR, "b5-group-card-back.pdf"))
    save_two_sided_pdf(front, back, os.path.join(OUT_DIR, "b5-group-card-print.pdf"))

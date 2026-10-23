#!/usr/bin/env python3
"""Builds a simple, clean 'THE THEATER x INDIAN KITCHEN' lockup for chef
uniform embroidery/print: flat single-color silhouettes of each brand's
wordmark, separated by a thin '×', on a transparent background. Outputs a
high-res PNG and a vector-ish PDF at exact print size, in both black ink
(for light-colored uniforms) and white ink (for dark-colored uniforms)."""
import io
import os

import pymupdf
from PIL import Image, ImageDraw, ImageFont
import numpy as np

THEATER_LOGO = "/home/user/intunnelconsulting.github.io/theater-menu-photography/references/brand-logo-alpha.png"
IK_LOGO_PDF = "/root/.claude/uploads/b07b59c1-87c7-5e01-8e75-ec8db4f2484f/2191dd6d-Indian_Kitchen_Sapa_Logo_Corrected_Print_Ready.pdf"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def silhouette_from_rgba(im, ink, threshold=140):
    """Flatten any RGBA logo to a single ink color, keeping its alpha shape."""
    im = im.convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3].astype(np.float32)
    # Where alpha is low, treat as transparent regardless of color.
    rgb = arr[:, :, :3].astype(np.float32)
    luminance = rgb.mean(axis=2)
    # Darker pixels (the ink strokes) keep full alpha; keep original alpha
    # shape but drop near-white/light artifacts some renders leave behind.
    mask = (alpha > 10) & (luminance < 235)
    out = np.zeros_like(arr)
    out[:, :, 0] = ink[0]
    out[:, :, 1] = ink[1]
    out[:, :, 2] = ink[2]
    out[:, :, 3] = np.where(mask, alpha, 0).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def tight_crop(im, pad=20):
    alpha = np.array(im.split()[-1])
    ys, xs = np.where(alpha > 10)
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    y0 = max(0, y0 - pad)
    x0 = max(0, x0 - pad)
    y1 = min(im.height, y1 + pad)
    x1 = min(im.width, x1 + pad)
    return im.crop((x0, y0, x1, y1))


def load_ik_logo():
    doc = pymupdf.open(IK_LOGO_PDF)
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(6, 6), alpha=True)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    return im


def load_theater_logo():
    return Image.open(THEATER_LOGO)


def scale_to_height(im, target_h):
    w, h = im.size
    new_w = int(w * target_h / h)
    return im.resize((new_w, target_h), Image.LANCZOS)


def build_lockup(out_png, out_pdf, ink, dpi=600):
    theater = tight_crop(silhouette_from_rgba(load_theater_logo(), ink))
    ik = tight_crop(silhouette_from_rgba(load_ik_logo(), ink))

    # Match visual cap-height roughly by scaling both to the same height.
    target_h = 900
    theater = scale_to_height(theater, target_h)
    ik = scale_to_height(ik, target_h)

    # "x" divider, drawn as text in a clean serif, same ink color.
    divider_h = target_h
    gap = 70
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        int(target_h * 0.5),
    )
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)
    bbox = tdraw.textbbox((0, 0), "x", font=font)
    div_w = bbox[2] - bbox[0] + gap * 2
    divider = Image.new("RGBA", (div_w, divider_h), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(divider)
    tx = (div_w - (bbox[2] - bbox[0])) / 2 - bbox[0]
    ty = (divider_h - (bbox[3] - bbox[1])) / 2 - bbox[1]
    ddraw.text((tx, ty), "x", font=font, fill=ink)

    pad = 60
    total_w = theater.width + pad + divider.width + pad + ik.width
    total_h = target_h
    canvas = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))

    x = 0
    y = (total_h - theater.height) // 2
    canvas.paste(theater, (x, y), theater)
    x += theater.width + pad
    y = (total_h - divider.height) // 2
    canvas.paste(divider, (x, y), divider)
    x += divider.width + pad
    y = (total_h - ik.height) // 2
    canvas.paste(ik, (x, y), ik)

    # Frame with generous transparent margin for clean embroidery digitizing.
    margin = int(total_h * 0.15)
    framed = Image.new("RGBA", (canvas.width + margin * 2, canvas.height + margin * 2), (0, 0, 0, 0))
    framed.paste(canvas, (margin, margin), canvas)

    framed.save(out_png, dpi=(dpi, dpi))
    print(f"Saved {out_png} ({framed.width}x{framed.height}px)")

    # Print-ready single-page PDF at the same pixel size, embedded at `dpi`.
    page_w_pt = framed.width * 72 / dpi
    page_h_pt = framed.height * 72 / dpi
    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page(width=page_w_pt, height=page_h_pt)
    buf = io.BytesIO()
    framed.save(buf, format="PNG")
    page.insert_image(pymupdf.Rect(0, 0, page_w_pt, page_h_pt), stream=buf.getvalue())
    pdf_doc.save(out_pdf)
    print(f"Saved {out_pdf} ({page_w_pt/72:.2f}in x {page_h_pt/72:.2f}in @ {dpi}dpi)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    build_lockup(
        os.path.join(OUT_DIR, "theater-x-indian-kitchen-logo-black.png"),
        os.path.join(OUT_DIR, "theater-x-indian-kitchen-logo-black.pdf"),
        ink=(20, 20, 20, 255),
    )
    build_lockup(
        os.path.join(OUT_DIR, "theater-x-indian-kitchen-logo-white.png"),
        os.path.join(OUT_DIR, "theater-x-indian-kitchen-logo-white.pdf"),
        ink=(255, 255, 255, 255),
    )

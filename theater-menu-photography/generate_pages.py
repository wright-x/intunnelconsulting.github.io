#!/usr/bin/env python3
"""Generates full designed menu PAGES via Gemini (Nano Banana 2), using the
previously-generated dish photos as food-appearance references."""
import base64
import csv
import json
import os
import sys
import time

import requests
from PIL import Image

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "pages_output")

MIN_2K_DIM = 1536


def load_image_part(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return {"inlineData": {"mimeType": "image/png", "data": data}}


def call_gemini(prompt, ref_paths, max_retries=5):
    parts = []
    for p in ref_paths:
        parts.append(load_image_part(p))
    parts.append({"text": prompt})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"imageSize": "2K", "aspectRatio": "3:4"},
        },
    }
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    delay = 2
    for attempt in range(max_retries):
        resp = requests.post(URL, headers=headers, json=body, timeout=180)
        if resp.status_code == 429 or resp.status_code >= 500:
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}: {resp.text[:500]}"
        data = resp.json()
        try:
            for cand in data["candidates"]:
                for part in cand["content"]["parts"]:
                    if "inlineData" in part:
                        return base64.b64decode(part["inlineData"]["data"]), None
            return None, f"No image part: {json.dumps(data)[:500]}"
        except (KeyError, IndexError) as e:
            return None, f"Unexpected response ({e}): {json.dumps(data)[:500]}"
    return None, "Exhausted retries on 429/5xx"


COVER_BG_PROMPT = (
    "Design a full-bleed A4 portrait background photograph for a restaurant "
    "menu cover, flat and front-on (not a mockup, no page shadow, fills the "
    "entire frame). NO TEXT OF ANY KIND anywhere on the image — no words, "
    "no letters, no logo, no watermark. Just one single, continuous, "
    "beautiful elegant overhead flat-lay photograph filling the ENTIRE "
    "frame edge-to-edge with no seams or breaks: aromatic Indian spices "
    "(star anise, cinnamon sticks, cardamom pods, dried red chilies, "
    "coriander seeds, saffron threads, cloves) scattered artfully and "
    "evenly across a single warm marble surface with soft directional "
    "light and gentle shadow, consistent lighting and scale throughout — "
    "one continuous scene, not multiple stacked or repeated patterns."
)

STYLE_ANCHOR_NOTE = (
    "The FIRST attached reference image is a STYLE ANCHOR from an earlier "
    "page in this exact same menu set — match its precise typography (font "
    "choice, letter size, weight, spacing), header/footer layout, hairline "
    "rule style, icon style, and color palette exactly, so this page looks "
    "like part of the same printed document. The remaining attached "
    "reference images, in order, are the true food-appearance photos for "
    "this page's numbered items."
)


def composite_cover(bg_path, out_path):
    from PIL import ImageFilter

    logo = Image.open(os.path.join(BASE, "references", "brand-logo-alpha.png")).convert("RGBA")
    bg = Image.open(bg_path).convert("RGBA")

    target_w = int(bg.width * 0.62)
    scale = target_w / logo.width
    logo_resized = logo.resize((target_w, int(logo.height * scale)), Image.LANCZOS)
    x = (bg.width - logo_resized.width) // 2
    y = int(bg.height * 0.09)

    # soft translucent cream backing panel behind the logo for legibility,
    # feathered edges so it blends into the busy flat-lay with no hard seam
    pad_x, pad_y = 60, 50
    panel = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    panel_box = (
        x - pad_x, y - pad_y,
        x + logo_resized.width + pad_x, y + logo_resized.height + pad_y,
    )
    solid = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw_layer = Image.new("L", bg.size, 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(draw_layer)
    d.rounded_rectangle(panel_box, radius=40, fill=190)
    draw_layer = draw_layer.filter(ImageFilter.GaussianBlur(35))
    cream = Image.new("RGBA", bg.size, (246, 243, 236, 255))
    panel = Image.composite(cream, panel, draw_layer)

    bg = Image.alpha_composite(bg, panel)
    bg.paste(logo_resized, (x, y), logo_resized)
    bg.convert("RGB").save(out_path)


def main():
    only = sys.argv[1:]  # optional list of slugs to (re)generate
    with open(os.path.join(BASE, "menu_pages.json")) as f:
        pages = json.load(f)

    os.makedirs(OUT, exist_ok=True)
    manifest_rows = []
    successes = failures = flagged = 0
    style_anchor = None
    for p in pages:
        if p["type"] == "content":
            candidate = os.path.join(OUT, f"{p['page_num']:02d}-{p['slug']}.png")
            if os.path.exists(candidate):
                style_anchor = candidate
                break

    for p in pages:
        if only and p["slug"] not in only:
            continue
        filename = f"{p['page_num']:02d}-{p['slug']}.png"
        filepath = os.path.join(OUT, filename)

        print(f"[{p['page_num']}/{len(pages)}] {p['slug']} ({p['type']})", flush=True)

        if os.path.exists(filepath):
            try:
                with Image.open(filepath) as im:
                    w, h = im.size
                if max(w, h) >= MIN_2K_DIM:
                    print(f"  Already have {filename} ({w}x{h}), skipping", flush=True)
                    manifest_rows.append([p["page_num"], p["slug"], p["type"], p["title"],
                                           filename, f"{w}x{h}", "ok (pre-existing)"])
                    successes += 1
                    if p["type"] == "content" and style_anchor is None:
                        style_anchor = filepath
                    continue
            except Exception:
                pass

        if p["type"] == "cover":
            bg_path = os.path.join(OUT, "_cover_bg_tmp.png")
            img_bytes, err = call_gemini(COVER_BG_PROMPT, [])
            if img_bytes is None:
                print(f"  FAILED (cover bg): {err}", flush=True)
                manifest_rows.append([p["page_num"], p["slug"], p["type"], p["title"],
                                       "", "", "failed: " + (err or "unknown")])
                failures += 1
                continue
            with open(bg_path, "wb") as f:
                f.write(img_bytes)
            composite_cover(bg_path, filepath)
            os.remove(bg_path)
            with Image.open(filepath) as im:
                w, h = im.size
            print(f"  Saved {filename} ({w}x{h}) [composited]", flush=True)
            manifest_rows.append([p["page_num"], p["slug"], p["type"], p["title"],
                                   filename, f"{w}x{h}", "ok (composited logo)"])
            successes += 1
            time.sleep(1.2)
            continue

        prompt = p["prompt"]
        ref_paths = list(p["reference_photos"])
        if p["type"] == "content" and style_anchor and style_anchor != filepath:
            prompt = STYLE_ANCHOR_NOTE + "\n\n" + prompt
            ref_paths = [style_anchor] + ref_paths

        img_bytes, err = call_gemini(prompt, ref_paths)
        if img_bytes is None:
            print(f"  FAILED: {err}", flush=True)
            manifest_rows.append([p["page_num"], p["slug"], p["type"], p["title"],
                                   "", "", "failed: " + (err or "unknown")])
            failures += 1
            time.sleep(1.5)
            continue

        with open(filepath, "wb") as f:
            f.write(img_bytes)
        with Image.open(filepath) as im:
            w, h = im.size
        status = "ok"
        if max(w, h) < MIN_2K_DIM:
            print(f"  Got {w}x{h}, retrying once for 2K...", flush=True)
            time.sleep(1.5)
            img_bytes2, err2 = call_gemini(prompt, ref_paths)
            if img_bytes2 is not None:
                with open(filepath, "wb") as f:
                    f.write(img_bytes2)
                with Image.open(filepath) as im:
                    w, h = im.size
                status = "retried" if max(w, h) >= MIN_2K_DIM else "flagged_low_res"
            else:
                status = "flagged_low_res"

        if status == "flagged_low_res":
            flagged += 1
        else:
            successes += 1
            if p["type"] == "content" and style_anchor is None:
                style_anchor = filepath

        print(f"  Saved {filename} ({w}x{h}) [{status}]", flush=True)
        manifest_rows.append([p["page_num"], p["slug"], p["type"], p["title"],
                               filename, f"{w}x{h}", status])
        time.sleep(1.5)

    manifest_path = os.path.join(OUT, "manifest_pages.csv")
    mode = "a" if only and os.path.exists(manifest_path) else "w"
    with open(manifest_path, mode, newline="") as f:
        w_ = csv.writer(f)
        if mode == "w":
            w_.writerow(["page_num", "slug", "type", "title", "filename",
                         "actual_resolution", "status"])
        w_.writerows(manifest_rows)

    print("\n=== SUMMARY ===")
    print(f"Pages processed: {len(manifest_rows)}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Flagged low-res: {flagged}")


if __name__ == "__main__":
    main()

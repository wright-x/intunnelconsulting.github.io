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


COVER_PROMPT = (
    "Design a full-bleed A4 portrait restaurant menu COVER page, flat and "
    "front-on like a scanned printed page (not a 3D mockup, no page "
    "shadow, no tilt, no table beneath it, fills the entire frame "
    "edge-to-edge). Clean warm white/cream paper background (hex F6F3EC). "
    "Around all four edges of the page, an artful flat-lay border of "
    "aromatic Indian spices and ingredients: whole dried red chilies and "
    "fresh bay leaves in the top-left corner, a small ceramic bowl of "
    "whole cloves and a loose pile of coriander seeds and star anise "
    "clusters in the top-right corner, a pile of coriander seeds with "
    "fresh green leaves and small red flowers in the bottom-left corner, "
    "and star anise with cinnamon and fresh bay leaves in the "
    "bottom-right corner — the spices frame the page generously at the "
    "top and bottom and corners only, leaving the large central two-thirds "
    "of the page clean, empty, and uncluttered. In the exact center of "
    "the page, a large elegant round mandala flourish medallion made of "
    "fine thin warm-brown line-art petals. The attached reference image "
    "is the restaurant's exact logo lockup — reproduce this exact "
    "wordmark, exact letterforms, exact font, exact 'INDIAN KITCHEN & "
    "BAR' subtitle line and exact small star divider, pixel-faithful to "
    "the reference, centered inside the mandala medallion, sized so the "
    "medallion comfortably frames the whole logo lockup. To the right "
    "side of the page at roughly the same height as the medallion, a "
    "small fine black-ink line-art architectural sketch of an ornate "
    "South Indian temple gopuram tower. No other text anywhere on the "
    "page."
)


def main():
    only = sys.argv[1:]  # optional list of slugs to (re)generate
    with open(os.path.join(BASE, "menu_pages.json")) as f:
        pages = json.load(f)

    os.makedirs(OUT, exist_ok=True)
    manifest_rows = []
    successes = failures = flagged = 0

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
                    continue
            except Exception:
                pass

        if p["type"] == "cover":
            logo_path = os.path.join(BASE, "references", "brand-logo-alpha.png")
            prompt = COVER_PROMPT
            ref_paths = [logo_path]
        else:
            prompt = p["prompt"]
            ref_paths = list(p["reference_photos"])

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

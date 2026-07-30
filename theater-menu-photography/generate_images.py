#!/usr/bin/env python3
"""Generates menu photography for The Theater via Gemini (Nano Banana 2)."""
import base64
import csv
import json
import os
import re
import sys
import time

import requests
from PIL import Image
import io

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

BASE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(BASE, "references")
OUT = os.path.join(BASE, "output")

REFERENCE_IMAGES = {
    "oval_sauce_well": os.path.join(REFS, "oval-plate-sauce-well.jpeg"),
    "round_plain": os.path.join(REFS, "round-oval-plain-plate.jpeg"),
    "round_plain_large": os.path.join(REFS, "round-oval-plain-plate.jpeg"),
    "wooden_tray": os.path.join(REFS, "curved-wooden-tray.jpeg"),
    # copper_martini reference photo is a dimension-spec diagram with
    # measurement lines baked across the whole frame; relying on the text
    # prompt alone for it to avoid that bleeding into the output.
}

MIN_2K_DIM = 1536  # below this we treat the result as a silent 1K fallback


def category_slug(cat):
    return re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")


def load_ref_part(plateware_key):
    path = REFERENCE_IMAGES.get(plateware_key)
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    mime = "image/jpeg"
    return {"inlineData": {"mimeType": mime, "data": data}}


def call_gemini(prompt, ref_part, max_retries=5):
    parts = []
    if ref_part:
        parts.append(ref_part)
        parts.append({
            "text": (
                "Use the attached photo strictly as a style/shape reference for the "
                "plateware or glassware only (its material, color, form). Do not "
                "reproduce the photo's background, lighting, hands, or any other "
                "objects from it. " + prompt
            )
        })
    else:
        parts.append({"text": prompt})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"imageSize": "2K"},
        },
    }
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    delay = 2
    for attempt in range(max_retries):
        resp = requests.post(URL, headers=headers, json=body, timeout=120)
        if resp.status_code == 429:
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code >= 500:
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}: {resp.text[:500]}"
        data = resp.json()
        try:
            candidates = data["candidates"]
            for cand in candidates:
                for part in cand["content"]["parts"]:
                    if "inlineData" in part:
                        b64 = part["inlineData"]["data"]
                        return base64.b64decode(b64), None
            return None, f"No image part in response: {json.dumps(data)[:500]}"
        except (KeyError, IndexError) as e:
            return None, f"Unexpected response shape ({e}): {json.dumps(data)[:500]}"
    return None, "Exhausted retries on 429/5xx"


def main():
    with open(os.path.join(BASE, "menu_items.json")) as f:
        items = json.load(f)

    os.makedirs(OUT, exist_ok=True)
    manifest_rows = []
    successes = 0
    failures = 0
    flagged = 0

    for idx, it in enumerate(items, 1):
        cat_slug = category_slug(it["category"])
        cat_dir = os.path.join(OUT, cat_slug)
        os.makedirs(cat_dir, exist_ok=True)
        filename = f"{it['slug']}.png"
        filepath = os.path.join(cat_dir, filename)
        rel_path = os.path.join(cat_slug, filename)

        ref_part = load_ref_part(it["plateware"])
        print(f"[{idx}/{len(items)}] {it['name']} ({it['category']})", flush=True)

        if os.path.exists(filepath):
            try:
                with Image.open(filepath) as im:
                    w, h = im.size
                if max(w, h) >= MIN_2K_DIM:
                    print(f"  Already have {rel_path} ({w}x{h}), skipping", flush=True)
                    manifest_rows.append([
                        it["name"], it["category"], it["price_vnd_k"], rel_path,
                        it["prompt"], f"{w}x{h}", "ok (pre-existing)",
                    ])
                    successes += 1
                    continue
            except Exception:
                pass

        status = "ok"
        actual_res = ""
        img_bytes, err = call_gemini(it["prompt"], ref_part)

        if img_bytes is None:
            print(f"  FAILED: {err}", flush=True)
            manifest_rows.append([
                it["name"], it["category"], it["price_vnd_k"], "", it["prompt"],
                "", "failed: " + (err or "unknown"),
            ])
            failures += 1
            time.sleep(1.5)
            continue

        with open(filepath, "wb") as f:
            f.write(img_bytes)

        with Image.open(filepath) as im:
            w, h = im.size
        actual_res = f"{w}x{h}"

        if max(w, h) < MIN_2K_DIM:
            print(f"  Got {actual_res}, retrying once for 2K...", flush=True)
            time.sleep(1.5)
            img_bytes2, err2 = call_gemini(it["prompt"], ref_part)
            if img_bytes2 is not None:
                with open(filepath, "wb") as f:
                    f.write(img_bytes2)
                with Image.open(filepath) as im:
                    w, h = im.size
                actual_res = f"{w}x{h}"
                if max(w, h) < MIN_2K_DIM:
                    status = "flagged_low_res"
                    flagged += 1
                else:
                    status = "retried"
            else:
                status = "flagged_low_res"
                flagged += 1

        if status == "ok":
            successes += 1
        elif status == "retried":
            successes += 1

        print(f"  Saved {rel_path} ({actual_res}) [{status}]", flush=True)
        manifest_rows.append([
            it["name"], it["category"], it["price_vnd_k"], rel_path, it["prompt"],
            actual_res, status,
        ])

        time.sleep(1.2)

    manifest_path = os.path.join(OUT, "manifest.csv")
    with open(manifest_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dish_name", "category", "price_vnd_k", "filename", "prompt_used",
                    "actual_resolution", "status"])
        w.writerows(manifest_rows)

    print("\n=== SUMMARY ===")
    print(f"Total items: {len(items)}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Flagged low-res: {flagged}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()

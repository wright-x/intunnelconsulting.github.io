#!/usr/bin/env python3
"""Generates dish photography for the Indian Kitchen menu via Gemini
(Nano Banana 2)."""
import base64
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
OUT = os.path.join(BASE, "output")

MIN_2K_DIM = 1536


def call_gemini(prompt, max_retries=5):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"imageSize": "2K"},
        },
    }
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    delay = 2
    for attempt in range(max_retries):
        resp = requests.post(URL, headers=headers, json=body, timeout=120)
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


def main():
    only = sys.argv[1:]
    with open(os.path.join(BASE, "items.json")) as f:
        items = json.load(f)

    os.makedirs(OUT, exist_ok=True)
    successes = failures = 0

    for idx, it in enumerate(items, 1):
        if only and it["slug"] not in only:
            continue
        filepath = os.path.join(OUT, f"{it['slug']}.png")
        print(f"[{idx}/{len(items)}] {it['name']}", flush=True)

        if os.path.exists(filepath):
            with Image.open(filepath) as im:
                w, h = im.size
            if max(w, h) >= MIN_2K_DIM:
                print(f"  Already have {it['slug']}.png ({w}x{h}), skipping", flush=True)
                successes += 1
                continue

        img_bytes, err = call_gemini(it["prompt"])
        if img_bytes is None:
            print(f"  FAILED: {err}", flush=True)
            failures += 1
            time.sleep(1.5)
            continue

        with open(filepath, "wb") as f:
            f.write(img_bytes)
        with Image.open(filepath) as im:
            w, h = im.size
        print(f"  Saved {it['slug']}.png ({w}x{h})", flush=True)
        successes += 1
        time.sleep(1.5)

    print("\n=== SUMMARY ===")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")


if __name__ == "__main__":
    main()

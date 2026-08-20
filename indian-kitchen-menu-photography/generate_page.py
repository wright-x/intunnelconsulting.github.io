#!/usr/bin/env python3
"""Generates one sample menu page for Indian Kitchen using the burgundy/gold
template style, compositing dish photos from output/ onto it."""
import base64
import json
import os
import sys
import time

import requests
from PIL import Image

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")
PAGES_OUT = os.path.join(BASE, "pages_output")


def load_image_part(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return {"inlineData": {"mimeType": "image/png", "data": data}}


def call_gemini(prompt, ref_paths, max_retries=5):
    parts = [load_image_part(p) for p in ref_paths]
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
    return None, "Exhausted retries"


PAGE_PROMPT = (
    "Design a tall vertical portrait print restaurant menu page, full-bleed, "
    "flat and front-on like a scanned printed page, never a 3D mockup. "
    "Background: a deep, rich wine-burgundy color with a subtle plaster-like "
    "matte texture (like tinted concrete, not glossy), one soft light source "
    "from the upper left creating a gentle warmer burgundy glow in the upper "
    "left that fades to near-black in the corners, with a fine film-grain "
    "texture across the whole page for a tactile printed feel. "
    "The ONLY background graphic: one very large lotus flower drawn as an "
    "extremely faint, barely-perceptible thin gold outline (no fill), "
    "bleeding off the bottom-left corner of the page, so subtle it reads as "
    "texture and never competes with the food or text — do not add any "
    "other script, lettering, characters, or symbols to the background.\n\n"
    "Three dishes, each cut out cleanly from its reference photo with no "
    "background, floating directly on the burgundy: reference photo 1 is "
    "'Pani Puri Flight', reference photo 2 is 'Spiced Lamb Keema Samosas', "
    "reference photo 3 is 'Aloo Tikki Chaat' — match each exactly to its "
    "own text block below, never swap or combine them. Preserve each "
    "reference photo's exact plating, garnish, side condiments and "
    "composition precisely as shown — do not simplify, remove, or alter "
    "any element of the plate; the cutout must look identical to its "
    "reference, just extracted from its white background. All three plates "
    "are the same scale as each other, same elevated three-quarter camera "
    "angle looking down, same key light from the upper left matching the "
    "page lighting, each casting one soft diffuse elliptical shadow toward "
    "the lower right. Arrange them in a gentle S-curve down the page rather "
    "than a straight column: dish 1 (Pani Puri Flight) sits high and to "
    "the right, bleeding off the right edge of the page; dish 2 (Samosas) "
    "sits centered-left, bleeding off the left edge; dish 3 (Aloo Tikki "
    "Chaat) sits low and to the right, bleeding off the right edge. Each "
    "plate is tilted only a few degrees, never perfectly square, and the "
    "plates overlap each other's shadow pools slightly for depth.\n\n"
    "Props: a small scattering of whole spices near the bottom left of the "
    "page resting directly on the burgundy — one star anise, a few green "
    "cardamom pods, a few black peppercorns — each with its own tiny "
    "shadow toward the lower right. No cutlery, no hands, no linen, no "
    "table surface, no glassware anywhere on the page.\n\n"
    "Typography: the display type is a refined, high-contrast serif with "
    "generous letter spacing in a warm antique gold, with a faint engraved "
    "quality as if pressed into the page. Body copy is an elegant italic "
    "serif in soft cream. Prices use the same gold serif as the display "
    "type. Keep the tone restrained and fine-dining, never bold or heavy, "
    "with plenty of empty burgundy space around every text block.\n\n"
    "Layout: the word 'BEGINNINGS' (spelled B-E-G-I-N-N-I-N-G-S, ten letters, double N in the middle) set very large in gold, stacked "
    "vertically down the left edge of the page, one letter directly above "
    "the next. Beside that stacked title, ONCE only, at the top next to "
    "the first letter 'B', a short line of small gold text rotated "
    "vertically reading 'PART ONE' — this text must appear exactly once "
    "on the entire page, never repeated a second time anywhere else. Each "
    "of the three dishes has "
    "its own text block placed on the side of the page opposite its "
    "plate, containing, top to bottom: a small gold-outlined pill-shaped "
    "tag, the dish name in the gold display serif, a short thin gold "
    "hairline rule, the description in cream italic serif, then the price "
    "in gold serif. Text blocks align to the nearest page edge, with their "
    "ragged edge facing the food. At the very bottom of the page, centered, "
    "a single small gold line-icon of a lotus sitting in a bowl, sitting "
    "in a gap within a thin gold horizontal rule spanning the page width. "
    "Do not render any full logo lockup, brand name, or tagline at the top "
    "of the page.\n\n"
    "On the Samosas plate and the Aloo Tikki Chaat plate only: a small "
    "circular gold double-ring seal containing one small muted-red "
    "oil-lamp flame icon, no text of any kind inside or around the ring, "
    "overlapping the outer rim of the plate at its upper right, half on "
    "the plate and half on the burgundy, tilted slightly off upright.\n\n"
    "Render ONLY the following text, exactly as written, nowhere else on "
    "the page — no other words, numbers, letters, measurements, "
    "percentages, page numbers, or watermark text of any kind:\n"
    "Section title: 'BEGINNINGS'\n"
    "Kicker: 'PART ONE'\n"
    "Dish 1 — tag 'IK 01', name 'Pani Puri Flight', description 'Six crisp "
    "puris, spiced potato and chickpea, three chilled waters — mint, "
    "tamarind, raw mango', price '175K'\n"
    "Dish 2 — tag 'IK 02', name 'Spiced Lamb Keema Samosas', description "
    "'Crisp pastry, spiced minced lamb and peas, mint-coriander chutney', "
    "price '165K'\n"
    "Dish 3 — tag 'IK 03', name 'Aloo Tikki Chaat', description 'Golden "
    "potato patties, chickpea curry, yogurt, tamarind and mint chutney', "
    "price '145K'"
)


def main():
    os.makedirs(PAGES_OUT, exist_ok=True)
    refs = [
        os.path.join(OUT, "pani-puri-flight.png"),
        os.path.join(OUT, "spiced-lamb-keema-samosas.png"),
        os.path.join(OUT, "aloo-tikki-chaat.png"),
    ]
    img_bytes, err = call_gemini(PAGE_PROMPT, refs)
    if img_bytes is None:
        print(f"FAILED: {err}", file=sys.stderr)
        sys.exit(1)
    filepath = os.path.join(PAGES_OUT, "beginnings-1.png")
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    with Image.open(filepath) as im:
        print(f"Saved {filepath} {im.size}")


if __name__ == "__main__":
    main()

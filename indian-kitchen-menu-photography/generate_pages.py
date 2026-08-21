#!/usr/bin/env python3
"""Generates every section page (and the cover) for the Indian Kitchen menu,
using the burgundy/gold template established in generate_page.py, applied
consistently across all sections."""
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


with open(os.path.join(BASE, "items.json")) as f:
    ITEMS = json.load(f)
ITEMS_BY_NAME = {it["name"]: it for it in ITEMS}

DESCRIPTIONS = {
    "Pani Puri Flight": "Six crisp puris, spiced potato and chickpea, three chilled waters — mint, tamarind, raw mango",
    "Spiced Lamb Keema Samosas": "Crisp pastry, spiced minced lamb and peas, mint-coriander chutney",
    "Aloo Tikki Chaat": "Golden potato patties, chickpea curry, yogurt, tamarind and mint chutney",
    "Charred Sweet Potato & Chickpea Salad": "Charred sweet potato, crispy chickpeas, yogurt, tamarind-date glaze",
    "Charred Broccoli, Almond & Herb Cream": "Charred broccoli, toasted almonds, herb cream, curry-leaf oil",
    "Whole Roasted Cauliflower, Cashew Curry": "Whole roasted cauliflower, cashew curry, crisp curry leaves",
    "Charcoal Paneer Tikka": "Charcoal-grilled paneer, mint yogurt, pomegranate",
    "Tandoori Chicken Thigh, Kashmiri Chilli": "Charcoal-grilled chicken thigh, Kashmiri chilli marinade, yogurt",
    "Lamb Seekh Kebab, Pickled Onion": "Minced lamb kebab, mint chutney, pickled onion",
    "Charcoal Butter Chicken": "Charcoal-grilled chicken, tomato-butter gravy, cream",
    "Malabar Fish Curry, Banana Leaf": "White fish, coconut Malabar spice, curry leaf, banana leaf",
    "Lamb Rogan Josh, Kashmiri Chilli": "Braised lamb, Kashmiri chilli gravy, cream",
    "Hyderabadi Chicken Dum Biryani": "Saffron basmati, bone-in chicken, fried onion, dum-sealed",
    "Vegetable Dum Biryani, Saffron": "Saffron basmati, charred vegetables, paneer, dum-sealed",
    "Jeera Rice, Toasted Cumin": "Basmati rice, toasted cumin, dried chilli",
    "Deconstructed Gulab Jamun, Saffron Cream": "Saffron-soaked gulab jamun, chilled saffron cream, pistachio",
    "Pistachio Kulfi, Rose, Vermicelli": "Pistachio kulfi, rose petal, crisp vermicelli",
    "Chai-Spiced Crème Brûlée": "Chai-spiced custard, caramelized sugar, cinnamon",
}

SECTIONS = [
    ("beginnings-1", "BEGINNINGS", "PART ONE", "IK",
     ["Pani Puri Flight", "Spiced Lamb Keema Samosas", "Aloo Tikki Chaat"]),
    ("vegetable-garden-1", "VEGETABLE GARDEN", "PART TWO", "VG",
     ["Charred Sweet Potato & Chickpea Salad", "Charred Broccoli, Almond & Herb Cream", "Whole Roasted Cauliflower, Cashew Curry"]),
    ("tandoor-1", "FROM THE TANDOOR", "PART THREE", "TD",
     ["Charcoal Paneer Tikka", "Tandoori Chicken Thigh, Kashmiri Chilli", "Lamb Seekh Kebab, Pickled Onion"]),
    ("curries-mains-1", "CURRIES & MAINS", "PART FOUR", "CM",
     ["Charcoal Butter Chicken", "Malabar Fish Curry, Banana Leaf", "Lamb Rogan Josh, Kashmiri Chilli"]),
    ("rice-biryani-1", "RICE & BIRYANI", "PART FIVE", "RB",
     ["Hyderabadi Chicken Dum Biryani", "Vegetable Dum Biryani, Saffron", "Jeera Rice, Toasted Cumin"]),
    ("sweet-endings-1", "SWEET ENDINGS", "PART SIX", "SE",
     ["Deconstructed Gulab Jamun, Saffron Cream", "Pistachio Kulfi, Rose, Vermicelli", "Chai-Spiced Crème Brûlée"]),
]


def build_section_prompt(title, kicker, tag_prefix, dish_names):
    d1, d2, d3 = dish_names
    lines = []
    for i, name in enumerate(dish_names, 1):
        it = ITEMS_BY_NAME[name]
        lines.append(
            f"Dish {i} — tag '{tag_prefix} {i:02d}', name '{name}', "
            f"description '{DESCRIPTIONS[name]}', price '{it['price_k']}K'"
        )
    dish_text_block = "\n".join(lines)

    return (
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
        f"background, floating directly on the burgundy: reference photo 1 is "
        f"'{d1}', reference photo 2 is '{d2}', reference photo 3 is '{d3}' — "
        "match each exactly to its own text block below, never swap or combine "
        "them. Preserve each reference photo's exact plating, garnish, side "
        "condiments and composition precisely as shown — do not simplify, "
        "remove, or alter any element of the plate; the cutout must look "
        "identical to its reference, just extracted from its white background. "
        "All three plates are the same scale as each other, same elevated "
        "three-quarter camera angle looking down, same key light from the "
        "upper left matching the page lighting, each casting one soft diffuse "
        "elliptical shadow toward the lower right. Arrange them in a gentle "
        "S-curve down the page rather than a straight column: dish 1 sits high "
        "and to the right, bleeding off the right edge of the page; dish 2 "
        "sits centered-left, bleeding off the left edge; dish 3 sits low and "
        "to the right, bleeding off the right edge. Each plate is tilted only "
        "a few degrees, never perfectly square, and the plates overlap each "
        "other's shadow pools slightly for depth.\n\n"
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
        f"Layout: the words '{title}' (render this exact spelling, letter by "
        "letter, double-check every letter before finalizing) set very large "
        "in gold, stacked vertically down the left edge of the page, one line "
        "of the title directly above the next if it wraps. Beside that "
        f"stacked title, ONCE only, at the very top, a short line of small "
        f"gold text rotated vertically reading exactly '{kicker}' and "
        f"nothing else — render precisely these words, no more, no fewer, "
        f"no substituted or added words. This text must appear exactly once "
        "on the entire page, never repeated a second time anywhere else. "
        "Each of the three dishes has its own text block "
        "placed on the side of the page opposite its plate, containing, top "
        "to bottom: a small gold-outlined pill-shaped tag, the dish name in "
        "the gold display serif, a short thin gold hairline rule, the "
        "description in cream italic serif, then the price in gold serif. "
        "Text blocks align to the nearest page edge, with their ragged edge "
        "facing the food. At the very bottom of the page, centered, a single "
        "small gold line-icon of a lotus sitting in a bowl, sitting in a gap "
        "within a thin gold horizontal rule spanning the page width. Do not "
        "render any full logo lockup, brand name, or tagline at the top of "
        "the page.\n\n"
        "On the dish 2 plate and the dish 3 plate only: a small circular gold "
        "double-ring seal containing one small muted-red oil-lamp flame icon, "
        "no text of any kind inside or around the ring, overlapping the outer "
        "rim of the plate at its upper right, half on the plate and half on "
        "the burgundy, tilted slightly off upright.\n\n"
        "Render ONLY the following text, exactly as written, nowhere else on "
        "the page — no other words, numbers, letters, measurements, "
        "percentages, page numbers, or watermark text of any kind:\n"
        f"Section title: '{title}'\n"
        f"Kicker: '{kicker}'\n"
        f"{dish_text_block}"
    )


COVER_PROMPT = (
    "Design a tall vertical portrait print restaurant menu COVER page, "
    "full-bleed, flat and front-on like a scanned printed page, never a 3D "
    "mockup. Background: a deep, rich wine-burgundy color with a subtle "
    "plaster-like matte texture (like tinted concrete, not glossy), soft "
    "light glowing gently from the center, fading to near-black at the "
    "corners, with a fine film-grain texture across the whole page for a "
    "tactile printed feel. In the exact center of the page, one large, "
    "elegant lotus flower drawn as a thin gold outline (no fill), acting as "
    "a decorative frame. Inside the lotus, centered, the restaurant name "
    "'INDIAN KITCHEN' set in a refined, high-contrast gold serif with "
    "generous letter spacing and a faint engraved quality, and directly "
    "beneath it, smaller, a thin gold hairline rule and small tracked-out "
    "gold capital text reading 'MODERN INDIAN KITCHEN'. Near the bottom of "
    "the page, centered, a single small gold line-icon of a lotus sitting "
    "in a bowl, sitting in a gap within a thin gold horizontal rule spanning "
    "about half the page width. A small scattering of whole spices — one "
    "star anise, a few green cardamom pods, a few black peppercorns — rests "
    "near the bottom of the page, each with its own tiny soft shadow. No "
    "photograph of food anywhere on this page, no other text, no other "
    "graphic elements, no watermark, no page number."
)


def gen(slug, prompt, ref_paths):
    filepath = os.path.join(PAGES_OUT, f"{slug}.png")
    print(f"Generating {slug}...", flush=True)
    img_bytes, err = call_gemini(prompt, ref_paths)
    if img_bytes is None:
        print(f"  FAILED: {err}", flush=True)
        return False
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    with Image.open(filepath) as im:
        print(f"  Saved {slug}.png {im.size}", flush=True)
    return True


def main():
    os.makedirs(PAGES_OUT, exist_ok=True)
    only = sys.argv[1:]

    if not only or "cover" in only:
        gen("cover", COVER_PROMPT, [])

    for slug, title, kicker, tag_prefix, dish_names in SECTIONS:
        if only and slug not in only:
            continue
        prompt = build_section_prompt(title, kicker, tag_prefix, dish_names)
        refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[n]['slug']}.png") for n in dish_names]
        gen(slug, prompt, refs)


if __name__ == "__main__":
    main()

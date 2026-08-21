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
    "Crispy Okra Fries, Chaat Masala": "Crisp fried okra strips, chaat masala, cooling mint yogurt",
    "Corn Bhel, Puffed Rice & Peanut": "Puffed rice, sweet corn, peanuts, tamarind and mint chutney",
    "Papadum Trio, Three Chutneys": "Three roasted papadums, mango pickle, chilli-garlic, mint yogurt",
    "Charred Sweet Potato & Chickpea Salad": "Charred sweet potato, crispy chickpeas, yogurt, tamarind-date glaze",
    "Charred Broccoli, Almond & Herb Cream": "Charred broccoli, toasted almonds, herb cream, curry-leaf oil",
    "Whole Roasted Cauliflower, Cashew Curry": "Whole roasted cauliflower, cashew curry, crisp curry leaves",
    "Charred Baby Eggplant, Peanut Curry": "Charred baby eggplant, peanut curry, crushed peanuts",
    "Tandoori Mushroom, Garlic Yogurt": "Charcoal-grilled king oyster mushroom, roasted garlic yogurt",
    "Beetroot Tikki, Goat Cheese": "Beetroot and potato tikki, soft goat cheese, toasted walnuts",
    "Charcoal Paneer Tikka": "Charcoal-grilled paneer, mint yogurt, pomegranate",
    "Tandoori Chicken Thigh, Kashmiri Chilli": "Charcoal-grilled chicken thigh, Kashmiri chilli marinade, yogurt",
    "Lamb Seekh Kebab, Pickled Onion": "Minced lamb kebab, mint chutney, pickled onion",
    "Tandoori Prawns, Chilli-Garlic": "Charcoal-grilled jumbo prawns, chilli-garlic marinade, garlic yogurt",
    "Malai Chicken Tikka, Cashew Cream": "Charcoal-grilled chicken tikka, malai marinade, cashew cream",
    "Charcoal Lamb Chops, Mint": "Charcoal-grilled French-trimmed lamb chops, mint chutney",
    "Charcoal Butter Chicken": "Charcoal-grilled chicken, tomato-butter gravy, cream",
    "Malabar Fish Curry, Banana Leaf": "White fish, coconut Malabar spice, curry leaf, banana leaf",
    "Lamb Rogan Josh, Kashmiri Chilli": "Braised lamb, Kashmiri chilli gravy, cream",
    "Goan Prawn Curry, Coconut": "Prawns, golden coconut curry, curry leaf, mustard seed",
    "Dal Makhani, Smoked Butter": "Slow-cooked black lentils, cream, smoked butter",
    "Palak Paneer, Charred Spinach": "Paneer, charred spinach gravy, cream, toasted pine nuts",
    "Hyderabadi Chicken Dum Biryani": "Saffron basmati, bone-in chicken, fried onion, dum-sealed",
    "Vegetable Dum Biryani, Saffron": "Saffron basmati, charred vegetables, paneer, dum-sealed",
    "Jeera Rice, Toasted Cumin": "Basmati rice, toasted cumin, dried chilli",
    "Lamb Biryani, Dum-Sealed": "Saffron basmati, braised lamb, fried onion, dum-sealed",
    "Prawn Biryani, Coastal Spice": "Saffron basmati, coastal-spiced prawns, curry leaf, fried onion",
    "Curd Rice, Pomegranate & Curry Leaf": "Creamy curd rice, curry-leaf tempering, pomegranate",
    "Deconstructed Gulab Jamun, Saffron Cream": "Saffron-soaked gulab jamun, chilled saffron cream, pistachio",
    "Pistachio Kulfi, Rose, Vermicelli": "Pistachio kulfi, rose petal, crisp vermicelli",
    "Chai-Spiced Crème Brûlée": "Chai-spiced custard, caramelized sugar, cinnamon",
    "Mango Cheesecake, Cardamom": "Mango cheesecake, biscuit base, cardamom",
    "Chocolate Samosa, Salted Caramel": "Molten chocolate samosa, salted caramel",
    "Saffron Rice Pudding, Pistachio": "Saffron rice pudding, pistachio, almond",
    "Smoked Old Fashioned, Chai Bitters": "Smoked whisky old fashioned, chai bitters, orange peel",
    "Tamarind Margarita": "Tamarind margarita, salt-chilli rim, lime",
    "Rose Lassi Martini": "Rose-yogurt martini, foam, pistachio",
    "Cucumber Mint Cooler": "Cucumber, mint, non-alcoholic cooler",
    "Spiced Chai": "Rich milky spiced chai, cinnamon, star anise",
    "Mango Lassi": "Mango yogurt, cardamom",
    "Papad & The Pickle Pantry": "Roasted urad papad, mango pickle, chilli-garlic chutney, mint yogurt",
    "Charred Pineapple Chaat": "Fire-roasted pineapple, tamarind, coconut, mustard seed, curry leaf",
    "Smoked Sweet Potato Chaat": "Charred sweet potato, date-tamarind, whipped yogurt, peanut, crispy chickpea",
    "Dahi Kachori": "Moong-filled kachori, chilled yogurt, mint, tamarind, pomegranate",
    "Three Faces of Paneer Tikka": "Charcoal paneer, three marinades — saffron, achari, green herb",
    "Kasundi Broccoli": "Charred broccoli, mustard kasundi, hung yogurt, toasted almond",
    "Gobi Musallam": "Whole charred cauliflower, makhani glaze, cashew, fenugreek",
    "House Tandoori Chicken": "Half chicken, Kashmiri chilli marinade, smoked ghee",
    "Kashmiri Lamb Chops": "Charcoal lamb chops, Kashmiri chilli, black cardamom, tamarind-shallot chutney",
    "Guntur Chilli King Prawns": "King prawns, Guntur chilli, curry leaf, lime, smoked butter",
    "Tandoori Da Nang Oysters": "Charcoal-grilled oysters, coconut-chilli butter, mustard, curry leaf",
    "Banana Leaf Sea Bass Pollichathu": "Sea bass, shallot, coconut, curry leaf, black pepper, banana leaf",
    "Malabar Lobster Moilee": "Lobster, coconut milk, turmeric, ginger, green chilli, curry leaf",
    "Mud Crab Chettinad": "Mud crab, black pepper, fennel, roasted coconut, curry leaf",
    "18-Hour Black Dal": "Black lentils slow-cooked overnight, cultured butter, smoked ghee tadka",
    "Chicken Tikka Masala": "Charred chicken tikka, tomato, onion, toasted spices",
    "Old Delhi Chole": "Dark chickpeas, black tea, amchur, ginger, green chilli",
    "Paneer Makhani": "Paneer, silky tomato-cashew gravy, fenugreek butter",
    "Malai Kofta": "Paneer-vegetable kofta, saffron cashew gravy, pomegranate",
    "Goat Keema Methi": "Goat mince, fenugreek, green peas, ginger",
    "Awadhi Chicken Dum Biryani": "Aged basmati, chicken, saffron, mint, fried onion, raita",
    "Jackfruit & Wild Mushroom Dum Biryani": "Young jackfruit, wild mushrooms, saffron, mint, fried onion",
    "Steamed Aged Basmati": "Aged basmati rice, steamed long-grain and fluffy",
    "Tandoori Roti": "Whole-wheat flatbread, tandoor-charred",
    "Butter Naan": "Soft tandoor naan, melted butter",
    "Garlic & Coriander Naan": "Soft naan, garlic, coriander, butter",
    "Laccha Paratha": "Flaky layered whole-wheat paratha",
    "Amul Chilli Cheese Kulcha": "Tandoor kulcha, Amul cheese, green chilli",
    "Saffron Sheermal": "Lightly sweet saffron-scented flatbread",
    "Cucumber & Cumin Raita": "Chilled yogurt, cucumber, roasted cumin, herbs",
    "Kachumber Salad": "Cucumber, tomato, onion, herbs, lime",
    "Da Nang Coffee Kulfi": "Vietnamese coffee cardamom kulfi, cacao nib brittle, jaggery caramel",
    "Tender Coconut Rasmalai": "Soft chenna, coconut rabri, pistachio, rose",
    "Hot Jalebi & Saffron Rabri": "Hot jalebi, saffron milk, pistachio",
    "Vietnam Mango Shrikhand": "Mango, saffron yogurt, pistachio, chilli-lime granita",
    "Dark Chocolate & Cardamom Tart": "Dark chocolate, cardamom, salted jaggery, vanilla ice cream",
    "Da Nang Nimbu": "Fresh lime, citrus, lightly spiced house soda",
    "Kokum & Ginger Fizz": "Kokum, fresh ginger, lime, sparkling soda",
    "Salted Masala Chaas": "Spiced buttermilk, roasted cumin, coriander, black salt",
    "Passion Fruit Jaljeera": "Passion fruit, mint, cumin, lime, jaljeera spice",
    "Monsoon in Da Nang": "Tropical Da Nang fruit, Indian spice",
    "Old Delhi Sour": "Indian-spiced whisky sour, citrus, bitters",
    "Filter Coffee Old Fashioned": "Old fashioned, Indian filter-coffee character, bitters",
    "Mango & Chilli Margarita": "Mango margarita, chilli heat, tequila, lime",
    "Malabar Highball": "Malabar-spiced highball, coastal citrus, soda",
}

CATEGORIES = [
    ("BEGINNINGS", "BEGINNINGS", "PART ONE", "IK", "beginnings"),
    ("VEGETABLE GARDEN", "VEGETABLE GARDEN", "PART TWO", "VG", "vegetable-garden"),
    ("TANDOOR", "FROM THE TANDOOR", "PART THREE", "TD", "tandoor"),
    ("CURRIES & MAINS", "CURRIES & MAINS", "PART FOUR", "CM", "curries-mains"),
    ("RICE & BIRYANI", "RICE & BIRYANI", "PART FIVE", "RB", "rice-biryani"),
    ("SWEET ENDINGS", "SWEET ENDINGS", "PART SIX", "SE", "sweet-endings"),
    ("DRINKS", "DRINKS", "PART SEVEN", "DR", "drinks"),
    ("BREADS & SIDES", "BREADS & SIDES", "PART EIGHT", "BS", "breads-sides"),
]

SECTIONS = []
for cat_key, title, kicker, tag_prefix, slug_prefix in CATEGORIES:
    cat_items = [it["name"] for it in ITEMS if it["category"] == cat_key]
    for page_idx in range(0, len(cat_items), 3):
        chunk = cat_items[page_idx:page_idx + 3]
        page_num = page_idx // 3 + 1
        start_tag = page_idx + 1
        SECTIONS.append(
            (f"{slug_prefix}-{page_num}", title, kicker, tag_prefix, chunk, start_tag)
        )


def build_section_prompt(title, kicker, tag_prefix, dish_names, start_tag):
    n = len(dish_names)
    lines = []
    badge_lines = []
    for i, name in enumerate(dish_names, 1):
        it = ITEMS_BY_NAME[name]
        tag_num = start_tag + i - 1
        veg_txt = "yes" if it["veg"] else "no"
        badge = it.get("badge")
        badge_txt = f"'{badge}'" if badge else "none"
        lines.append(
            f"Dish {i} — tag '{tag_prefix} {tag_num:02d}', name '{name}', "
            f"description '{DESCRIPTIONS[name]}', price '{it['price_k']}K', "
            f"vegetarian: {veg_txt}, spice level: {it['spice']} (0-3, 0 means no chilli icons), "
            f"badge: {badge_txt}"
        )
        if badge:
            badge_lines.append(f"Dish {i} badge text: '{badge}'")
    dish_text_block = "\n".join(lines)
    badge_text_block = ("\n" + "\n".join(badge_lines)) if badge_lines else ""

    letters = title.replace(" ", "")
    spelled = "-".join(letters)

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
        f"{'One dish' if n == 1 else ('Two dishes' if n == 2 else 'Three dishes')}, "
        "each cut out cleanly from its reference photo with no background, "
        "floating directly on the burgundy: " +
        "; ".join(f"reference photo {i} is '{name}'" for i, name in enumerate(dish_names, 1)) +
        " — match each exactly to its own text block below, never swap or "
        "combine them. Preserve each reference photo's exact plating, garnish, "
        "side condiments and composition precisely as shown — do not simplify, "
        "remove, or alter any element of the plate; the cutout must look "
        "identical to its reference, just extracted from its white background. "
        f"{'The plates are the same scale as each other, all with the ' if n > 1 else 'Shot at the '}"
        "same elevated three-quarter camera angle looking down, same key "
        "light from the upper left matching the page lighting, each casting "
        "one soft diffuse elliptical shadow toward the lower right. " + (
            "Arrange them in a gentle S-curve down the page rather than a "
            "straight column: dish 1 sits high and to the right, bleeding off "
            "the right edge of the page; dish 2 sits centered-left, bleeding "
            "off the left edge; dish 3 sits low and to the right, bleeding off "
            "the right edge. Each plate is tilted only a few degrees, never "
            "perfectly square, and the plates overlap each other's shadow "
            "pools slightly for depth.\n\n"
            if n == 3 else
            "Arrange them one above the other with generous burgundy space "
            "between: dish 1 sits high and to the right, bleeding off the "
            "right edge of the page; dish 2 sits lower and to the left, "
            "bleeding off the left edge. Each plate is tilted only a few "
            "degrees, never perfectly square.\n\n"
            if n == 2 else
            "The single dish is large and confident, positioned right of "
            "center and bleeding off the right edge of the page, tilted only "
            "a few degrees, never perfectly square, with generous empty "
            "burgundy space to its left for the text block.\n\n"
        ),
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
        f"Layout: the words '{title}', spelled exactly {spelled} "
        f"({len(letters)} letters, double-check every single letter including "
        "any doubled letters before finalizing — do not drop or merge any "
        "letter), set very large in gold, stacked vertically down the left "
        "edge of the page, one line "
        "of the title directly above the next if it wraps. Beside that "
        f"stacked title, at the very top, a single short line of small "
        f"gold text rotated vertically reading exactly '{kicker}' and "
        f"nothing else — render precisely these words, no more, no fewer, "
        f"no substituted or added words. This text must appear exactly once "
        "on the entire page, never repeated a second time anywhere else. "
        f"{'The dish has' if n == 1 else f'Each of the {n} dishes has'} its own text block "
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
        "Icon system: for every dish that is vegetarian, place one small "
        "gold-outlined circular icon of a single leaf directly to the left "
        "of that dish's tag, immediately followed by the small gold tracked "
        "capital word 'VEG' — for non-vegetarian dishes, render no leaf icon "
        "and no VEG word at all. For every dish with a spice level above "
        "zero, place that many small solid red chilli-pepper icons (one "
        "icon per spice level, one to three icons total, never more) "
        "directly to the right of that dish's tag, with no text or numbers "
        "beside them — for dishes with spice level zero, render no chilli "
        "icons at all. For any dish with a badge listed below, render one "
        "small gold-outlined pill-shaped badge containing that dish's exact "
        "badge text in small gold tracked-out capitals, overlapping the "
        "upper corner of that dish's photo, half on the photo and half on "
        "the burgundy background, tilted slightly — dishes with badge "
        "'none' get no pill badge anywhere on their photo.\n\n"
        "Render ONLY the following text, exactly as written, nowhere else on "
        "the page — no other words, numbers, letters, measurements, "
        "percentages, page numbers, or watermark text of any kind:\n"
        f"Section title: '{title}'\n"
        f"Kicker: '{kicker}'\n"
        f"{dish_text_block}"
        f"{badge_text_block}"
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

    for slug, title, kicker, tag_prefix, dish_names, start_tag in SECTIONS:
        if only and slug not in only:
            continue
        prompt = build_section_prompt(title, kicker, tag_prefix, dish_names, start_tag)
        refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[n]['slug']}.png") for n in dish_names]
        gen(slug, prompt, refs)


if __name__ == "__main__":
    main()

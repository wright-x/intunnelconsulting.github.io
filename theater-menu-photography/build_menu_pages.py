#!/usr/bin/env python3
"""Groups menu_items.json into full designed menu PAGES using an asymmetric
editorial layout (hero dish + cascading secondary dishes, cutout photography
with soft contact shadows, fixed A4 typography/color system), plus standalone
hero/background pages. Writes menu_pages.json with a JSON-structured Nano
Banana prompt per page."""
import json
import math
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "menu_items.json")) as f:
    ITEMS = json.load(f)

BY_CATEGORY = {}
for it in ITEMS:
    BY_CATEGORY.setdefault(it["category"], []).append(it)

NON_VEG_KEYWORDS = ["chicken", "prawn", "fish", "mutton", "lamb", "egg", "seafood"]


def category_slug(cat):
    return re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")


def is_veg(item):
    text = (item["name"] + " " + item["description"]).lower()
    return not any(k in text for k in NON_VEG_KEYWORDS)


HIGH_SPICE_KEYWORDS = ["chilli", "chili", "peri peri", "achari"]
MEDIUM_SPICE_KEYWORDS = [
    "masala", "tandoori", "curry", "manchurian", "65", "tikka", "kadhai",
    "kadai", "vindaloo",
]
ZERO_SPICE_CATEGORIES = {
    "Breads", "Rice & Khichdi", "Drinks", "Coffee",
    "Juices, Smoothies & Iced Tea", "Desserts",
}
ZERO_SPICE_KEYWORDS = ["salad", "raita", "papad", "lassi", "biryani", "khichdi", "rice"]


def spice_level(item):
    if item["category"] in ZERO_SPICE_CATEGORIES:
        return 0
    text = (item["name"] + " " + item["description"]).lower()
    if any(k in text for k in ZERO_SPICE_KEYWORDS):
        return 0
    if any(k in text for k in HIGH_SPICE_KEYWORDS):
        return 3
    if any(k in text for k in MEDIUM_SPICE_KEYWORDS):
        return 2
    return 1


CHEF_RECOMMENDED = {
    "Butter Chicken", "Tandoori Chicken", "Chicken Biryani", "Dal Makhani",
    "Paneer Tikka Skewers", "Chole Bhature", "Gulab Jamun with Vanilla Ice Cream",
    "Mixed Tandoori Platter", "Goan Prawn Curry", "Pani Puri Shots",
    "Mango Lassi", "Kadai Chicken",
}

TAGLINES = {
    "Small Plates & Bar Bites": "Light, bold and made for sharing.",
    "Chaat & Fast Sellers": "India's most loved street food classics.",
    "Tandoor & Grill": "Fire-grilled flavors. Timeless indulgence.",
    "Main Curries": "Slow-cooked Indian classics prepared with rich spices and traditional recipes.",
    "Seafood Curries": "Coastal Indian flavors featuring fresh seafood and aromatic spices.",
    "Breads": "Freshly baked in our tandoor; soft, flavorful and made to perfection.",
    "Rice & Khichdi": "Fragrant basmati rice and traditional Indian rice specialties.",
    "Biryani": "Traditional dum-cooked biryanis layered with aromatic spices and premium ingredients.",
    "Drinks": "Refreshing beverages to complement your meal.",
    "Coffee": "Freshly brewed coffee crafted for every mood.",
    "Juices, Smoothies & Iced Tea": "Refreshing sips for every moment.",
    "Desserts": "The perfect finale to your meal.",
}


def photo_path(item):
    p = os.path.join(BASE, "output", category_slug(item["category"]), f"{item['slug']}.png")
    return p if os.path.exists(p) else None


def balanced_chunks(lst, max_size):
    n = len(lst)
    if n == 0:
        return []
    num_pages = math.ceil(n / max_size)
    base, rem = divmod(n, num_pages)
    sizes = [base + 1] * rem + [base] * (num_pages - rem)
    out, i = [], 0
    for s in sizes:
        out.append(lst[i:i + s])
        i += s
    return out


PAGE_MAX_ITEMS = 6

NEGATIVE_PROMPT = (
    "no watermark, no stock logo, no placeholder text, no white background "
    "box behind photos, no uniform symmetric grid, no flat gray drop shadow, "
    "no generic clipart icons, do not change page size or aspect ratio, no "
    "3D mockup / no tilted book rendering / no drop shadow around the page "
    "edges — the image IS the flat page itself, viewed straight-on."
)

PAGE_SPEC_HEADER = {
    "format": "A4 portrait — LOCKED",
    "dimensions_mm": [210, 297],
    "dimensions_px_at_300dpi": [2480, 3508],
    "orientation": "portrait, do not rotate or crop to any other aspect ratio",
    "background_color": "#F6F3EC",
    "background_texture": "subtle warm paper tone, faint radial gradient top-right only, no grain, no noise",
}

TYPOGRAPHY = {
    "note": "Use this exact pairing on every page for brand consistency",
    "display_serif": "Fraunces or Canela — for numerals, taglines, italic accents",
    "sans": "Neue Haas Grotesk or General Sans — for dish names, prices, headline",
    "mood": "soft, warm, boutique restaurant",
    "sizes_pt": {
        "eyebrow": 10, "main_title": 30, "tagline": 11.5,
        "hero_dish_name": 21, "hero_description": 10.5, "hero_price": 13,
        "secondary_dish_name": 13.5, "secondary_description": 9, "footer": 7.5,
    },
    "colors": {
        "ink": "#1A1714", "muted_text": "#5c564c", "faint_gray": "#8a8377",
        "veg_green": "#4b7a4a", "spice_red": "#b3402a", "hairline": "#d8d2c4",
    },
    "rules": [
        "all dish names uppercase, bold weight",
        "all descriptions in the serif at light/regular weight, never bold",
        "numerals (1., 2., 3...) always in the display serif at light weight, pale gray, never black",
        "no more than 2 font families total on the page",
    ],
}

PHOTO_TREATMENT = {
    "background_removal": (
        "Each attached reference photo shows the true appearance of that "
        "plated dish (plate/glass, food, garnish, dip). Extract ONLY the "
        "plate/glass and its food contents as a clean cutout — completely "
        "remove the reference photo's own white/light background so nothing "
        "of it remains as a box, square or frame. Preserve the plate, dip "
        "bowls and garnish exactly as photographed."
    ),
    "shadow_only": (
        "soft realistic contact shadow beneath the plate, warm dark "
        "brown-black (~#14100A), heavily blurred, slight downward offset — "
        "never a hard-edged or flat gray shadow"
    ),
    "crop": "trimmed tightly to content bounding box, no frame, no border",
    "size_variation": {
        "hero": "large, ~45% of page width",
        "secondary_items": "medium, ~28-32% of page width each, slightly varied so no two feel identical",
    },
}

BRAND_MARKS_ROW = {
    "count": 3,
    "style": "small thin-line icon above a 2-line micro caption, all caps, letter-spaced, gray-brown",
    "labels": ["Fresh Sourced", "Hand Crafted", "Made With Care"],
}

OVERALL_MOOD = (
    "premium editorial restaurant menu, generous negative space, confident "
    "asymmetry, dishes floating with only a soft shadow grounding them, "
    "refined mixed serif/sans typography, art-directed not templated"
)


def veg_tag(is_v):
    return "small green outlined square + 'VEGETARIAN' label" if is_v else None


def spice_tag(level):
    if level <= 0:
        return None
    return f"{level} small outlined chili-pepper icon(s) in {TYPOGRAPHY['colors']['spice_red']}, labeled 'SPICE LEVEL' beneath in micro caption"


def build_item_block(it, num, side=None, hero=False):
    block = {
        ("number_mark" if hero else "num"): f"{num}." if hero else num,
        "name": it["name"],
        "price": f"{it['price_vnd_k']}K",
        "description": it["description"],
        "reference_photo_note": (
            "Food styling reference for this exact dish is attached as an "
            "image; use it as the true appearance of the plated dish — do "
            "not invent a different dish."
        ),
    }
    if side:
        block["side"] = side
    vt = veg_tag(it["_veg"])
    if vt:
        block["veg_tag"] = vt
    st = spice_tag(it["_spice"])
    if st:
        block["spice_tag"] = st
    if hero and it["_chef_rec"]:
        block["badge"] = {
            "text": "CHEF'S RECOMMENDED",
            "style": "small solid black pill, white bold uppercase text, overlapping top-left of photo",
        }
    return block


def build_content_prompt(category, page_items, page_num_in_cat, total_pages_in_cat):
    # pick hero: prefer a chef-recommended item, else first item
    hero_idx = 0
    for i, it in enumerate(page_items):
        if it["_chef_rec"]:
            hero_idx = i
            break
    hero_item = page_items[hero_idx]
    secondary = [it for i, it in enumerate(page_items) if i != hero_idx]

    secondary_blocks = []
    for i, it in enumerate(secondary):
        side = "left" if i % 2 == 0 else "right"
        secondary_blocks.append(build_item_block(it, num=i + 2, side=side))

    title = category.upper()
    if total_pages_in_cat > 1:
        title += f" ({page_num_in_cat}/{total_pages_in_cat})"

    spec = {
        "page": PAGE_SPEC_HEADER,
        "negative_prompt": NEGATIVE_PROMPT,
        "layout_logic": (
            "asymmetric editorial composition — one large hero dish at top, "
            "remaining dishes staggered in an alternating left/right cascade "
            "down the page, connected to their text block via a short thin "
            "leader line. NOT a symmetric grid."
        ),
        "header": {
            "brand_marks_row": BRAND_MARKS_ROW,
            "eyebrow": {
                "text": "THE THEATER — INDIAN KITCHEN & BAR",
                "note": "use this exact text, do not substitute a generic placeholder",
            },
            "title": {"text": title, "position": "top-right block, right-aligned"},
            "tagline": {
                "text": TAGLINES.get(category, ""),
                "position": "left-aligned below header row, divider line beneath",
            },
        },
        "typography": TYPOGRAPHY,
        "photo_treatment": PHOTO_TREATMENT,
        "hero_item": build_item_block(hero_item, num=1, hero=True),
        "secondary_items": secondary_blocks,
        "footer": {
            "text": (
                "All prices are in thousand VND (d). VAT and service charge "
                "is extra. Images are for representation purposes only."
            ),
            "style": "small italic serif, centered, muted gray, thin hairline divider above",
        },
        "overall_mood": OVERALL_MOOD,
    }
    prompt_text = (
        "Design this restaurant menu page precisely according to the "
        "following JSON art-direction spec. Render all specified text "
        "exactly as given (dish names, prices, descriptions, header/footer "
        "copy) — do not invent different names or prices. Attached images, "
        "in the same order as hero_item then secondary_items, are the true "
        "food-styling references for each dish.\n\n"
        + json.dumps(spec, indent=2, ensure_ascii=False)
    )
    ordered_items = [hero_item] + secondary
    return prompt_text, ordered_items


HERO_PROMPTS = [
    ("cover", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "FRONT COVER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, NOT a "
        "3D book/spine rendering, NO drop shadow around the page edges, NO "
        "gray backdrop behind the page — the image itself IS the flat "
        "printed page, filling the entire frame edge-to-edge). Top area: "
        "centered, the wordmark 'THE THEATER' in the display serif "
        "(Fraunces/Canela), ink color #1A1714, with small tracked caps "
        "subtitle beneath 'INDIAN KITCHEN & BAR', and smaller italic type "
        "beneath that: 'Duong Dong, Phu Quoc'. Below that, filling most of "
        "the page, one beautiful photograph: an elegant overhead flat-lay of "
        "aromatic Indian spices (star anise, cinnamon sticks, cardamom pods, "
        "dried red chilies, coriander seeds, saffron threads) scattered "
        "artfully on a warm marble surface with soft directional light and "
        "gentle shadow, trimmed tightly with no border or frame. No other "
        "text, no dish photos, no prices, no watermark, no stock logo."
    )),
    ("divider-small-plates", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "SECTION DIVIDER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, no page "
        "shadow, fills the entire frame). No dish list, no prices — just one "
        "beautiful photograph: a close-up of golden crispy fried snacks and "
        "small plates being plated, steam and texture visible, shallow depth "
        "of field, shot on a warm paper-toned surface. Render only a small "
        "elegant section label near the bottom in the serif/sans pairing "
        "(Fraunces/Canela + Neue Haas Grotesk), ink color #1A1714: 'SMALL "
        "PLATES, BAR BITES & CHAAT'. No watermark, no stock logo, no other text."
    )),
    ("divider-tandoor", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "SECTION DIVIDER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, no page "
        "shadow, fills the entire frame). No dish list, no prices — just one "
        "beautiful photograph: glowing charcoal embers inside a traditional "
        "clay tandoor oven with a skewer of char-grilled tikka just visible "
        "at the edge of frame, warm dramatic light, shallow depth of field. "
        "Render only a small elegant section label near the bottom in the "
        "serif/sans pairing (Fraunces/Canela + Neue Haas Grotesk), ink color "
        "#1A1714: 'TANDOOR, GRILL & MAIN CURRIES'. No watermark, no stock "
        "logo, no other text."
    )),
    ("divider-rice", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "SECTION DIVIDER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, no page "
        "shadow, fills the entire frame). No dish list, no prices — just one "
        "beautiful photograph: a dramatic close-up of fragrant basmati "
        "biryani rice being served from a hammered copper handi with steam "
        "rising, on a warm paper-toned surface. Render only a small elegant "
        "section label near the bottom in the serif/sans pairing "
        "(Fraunces/Canela + Neue Haas Grotesk), ink color #1A1714: 'RICE, "
        "KHICHDI & BIRYANI'. No watermark, no stock logo, no other text."
    )),
    ("divider-bar", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "SECTION DIVIDER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, no page "
        "shadow, fills the entire frame). No dish list, no prices — just one "
        "beautiful photograph: an elegant flat-lay of drink glassware — a "
        "copper mug, a tall glass of iced lassi, fresh mint and citrus — on "
        "a warm paper-toned surface with soft light. Render only a small "
        "elegant section label near the bottom in the serif/sans pairing "
        "(Fraunces/Canela + Neue Haas Grotesk), ink color #1A1714: 'DRINKS, "
        "COFFEE & JUICES'. No watermark, no stock logo, no other text."
    )),
    ("divider-desserts", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "SECTION DIVIDER page, background color #F6F3EC with a subtle warm "
        "radial gradient top-right, flat and front-on (not a mockup, no page "
        "shadow, fills the entire frame). No dish list, no prices — just one "
        "beautiful photograph: a close-up of glossy gulab jamun in saffron "
        "syrup with a scoop of vanilla ice cream, soft bright light, shallow "
        "depth of field, on a warm paper-toned surface. Render only a small "
        "elegant section label near the bottom in the serif/sans pairing "
        "(Fraunces/Canela + Neue Haas Grotesk), ink color #1A1714: "
        "'DESSERTS'. No watermark, no stock logo, no other text."
    )),
    ("closing", (
        "Design a full-bleed A4 portrait (2480x3508px @300dpi) restaurant menu "
        "CLOSING / thank-you page, background color #F6F3EC with a subtle "
        "warm radial gradient top-right, flat and front-on (not a mockup, no "
        "page shadow, fills the entire frame). Top-to-bottom, in this exact "
        "order, with EACH element appearing EXACTLY ONCE on the page (do not "
        "repeat any text block, do not duplicate the title anywhere else on "
        "the page): (1) centered near the top, the display serif "
        "(Fraunces/Canela), ink color #1A1714, large: 'DHANYAWAD', with "
        "smaller italic type directly beneath it: 'Thank you for dining with "
        "us.' — (2) below that, centered, a softly lit photograph of an "
        "empty premium table setting — folded linen napkin, cutlery, a "
        "single small candle lantern — on a warm paper-toned surface, "
        "trimmed tightly with a soft contact shadow, no background box — "
        "(3) below the photograph, centered, the wordmark 'THE THEATER' with "
        "small tracked caps subtitle 'INDIAN KITCHEN & BAR' — (4) at the "
        "very bottom, centered, small type: '152 Duong Tran Hung Dao, Duong "
        "Dong, Phu Quoc'. That is the complete page: no dish photos, no "
        "prices, no watermark, no stock logo, and absolutely no repeated or "
        "duplicated text anywhere."
    )),
]

CATEGORY_ORDER = [
    "Small Plates & Bar Bites",
    "Chaat & Fast Sellers",
    "Tandoor & Grill",
    "Main Curries",
    "Seafood Curries",
    "Breads",
    "Rice & Khichdi",
    "Biryani",
    "Drinks",
    "Coffee",
    "Juices, Smoothies & Iced Tea",
    "Desserts",
]

DIVIDER_BEFORE = {
    "Small Plates & Bar Bites": "divider-small-plates",
    "Tandoor & Grill": "divider-tandoor",
    "Rice & Khichdi": "divider-rice",
    "Drinks": "divider-bar",
    "Desserts": "divider-desserts",
}

pages = []
page_num = 1


def add_hero(key):
    global page_num
    prompt = dict(HERO_PROMPTS)[key]
    pages.append({
        "page_num": page_num, "type": "hero", "slug": key, "title": key,
        "items": [], "reference_photos": [], "prompt": prompt,
    })
    page_num += 1


add_hero("cover")

for cat in CATEGORY_ORDER:
    if cat in DIVIDER_BEFORE:
        add_hero(DIVIDER_BEFORE[cat])

    cat_items = BY_CATEGORY[cat]
    for it in cat_items:
        it["_veg"] = is_veg(it)
        it["_spice"] = spice_level(it)
        it["_chef_rec"] = it["name"] in CHEF_RECOMMENDED

    page_groups = balanced_chunks(cat_items, PAGE_MAX_ITEMS)
    total_pages_in_cat = len(page_groups)
    for i, group in enumerate(page_groups, 1):
        prompt_text, ordered_items = build_content_prompt(cat, group, i, total_pages_in_cat)
        refs = [photo_path(it) for it in ordered_items]
        pages.append({
            "page_num": page_num,
            "type": "content",
            "slug": f"{category_slug(cat)}-{i}",
            "title": cat,
            "items": [
                {
                    "name": it["name"], "price_vnd_k": it["price_vnd_k"],
                    "description": it["description"], "veg": it["_veg"],
                    "spice": it["_spice"], "chef_recommended": it["_chef_rec"],
                    "photo": photo_path(it),
                }
                for it in ordered_items
            ],
            "reference_photos": [r for r in refs if r],
            "prompt": prompt_text,
        })
        page_num += 1

add_hero("closing")

with open(os.path.join(BASE, "menu_pages.json"), "w") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

n_content = sum(1 for p in pages if p["type"] == "content")
n_hero = sum(1 for p in pages if p["type"] == "hero")
print(f"Wrote {len(pages)} pages ({n_content} content, {n_hero} hero) to menu_pages.json")

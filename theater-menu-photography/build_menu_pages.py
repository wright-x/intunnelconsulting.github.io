#!/usr/bin/env python3
"""Groups menu_items.json into full designed menu PAGES (layout + typography +
prices + icons baked into one image), plus standalone hero/background pages,
and writes menu_pages.json with a Nano Banana prompt per page."""
import json
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


def photo_path(item):
    p = os.path.join(BASE, "output", category_slug(item["category"]), f"{item['slug']}.png")
    return p if os.path.exists(p) else None


def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


STYLE_GUIDE = (
    "Render this as a FLAT, front-on, full-bleed page design filling the "
    "entire frame edge-to-edge — NOT a 3D mockup, NOT shown at an angle or "
    "propped up, NO drop shadow around the page edges, NO book/binder/table "
    "framing. The image itself IS the printed page, viewed perfectly "
    "straight-on like a scanned document. "
    "Premium editorial restaurant menu page design, bright and clean. Soft "
    "white/light warm-marble background with subtle natural texture, generous "
    "whitespace, delicate thin gold-black hairline rules and dotted price "
    "leaders. Elegant modern serif headline typography for the restaurant "
    "wordmark 'THE THEATER' with small refined tracked-out caps subtitle "
    "'INDIAN KITCHEN & BAR', and a clean modern sans-serif for dish names, "
    "descriptions and prices. High-end food photography styling for every "
    "dish shown, shot in soft bright studio light, shallow depth of field. "
    "Small minimal line-art icons: a tiny green circle outline with a leaf "
    "for vegetarian dishes placed beside the dish name, one to three small "
    "red chili-pepper outline icons beside the dish name indicating spice "
    "level, and a small elegant gold star-ribbon badge labeled 'CHEF'S "
    "RECOMMENDED' beside any dish marked as recommended. Consistent premium "
    "restaurant branding throughout, magazine-quality layout, no clutter. "
    "2K quality, ultra-detailed, photorealistic food, sharp typography. No "
    "spelling mistakes. No stray watermarks, no phone UI, no random extra text."
)


def build_content_prompt(category, page_items, page_num, total_pages_in_cat):
    lines = [STYLE_GUIDE]
    lines.append(
        f"This page is titled '{category.upper()}' (page {page_num} of "
        f"{total_pages_in_cat} for this section) — render the section title "
        "prominently near the top of the page beneath the restaurant wordmark."
    )
    lines.append(
        "Lay out the following dishes on this single page, each with its own "
        "photo, name, price and description rendered EXACTLY as given below "
        "(render this precise text, do not invent different names/prices):"
    )
    for it in page_items:
        veg_txt = "VEGETARIAN (show the green leaf icon)" if it["_veg"] else "non-vegetarian (no leaf icon)"
        spice = it["_spice"]
        spice_txt = f"{spice} chili icon(s)" if spice > 0 else "no chili icon"
        chef_txt = " Mark this dish with the CHEF'S RECOMMENDED gold ribbon badge." if it["_chef_rec"] else ""
        lines.append(
            f"- \"{it['name']}\" — {it['price_vnd_k']}K VND — \"{it['description']}\". "
            f"{veg_txt}. Spice level: {spice_txt}.{chef_txt} "
            f"Food styling reference for this exact dish is attached as an image; "
            f"use it as the true appearance of the plated dish in this layout."
        )
    lines.append(
        "Footnote at the bottom in small type: 'All prices are in thousand VND "
        "(d). VAT and service charge is extra.'"
    )
    return " ".join(lines)


HERO_PROMPTS = [
    ("cover", (
        STYLE_GUIDE + " This is the FRONT COVER of the menu: a full-bleed, "
        "atmospheric, single beautiful hero image with no dish list. Show an "
        "elegant overhead flat-lay of aromatic Indian spices (star anise, "
        "cinnamon sticks, cardamom pods, dried red chilies, saffron threads) "
        "scattered artfully on a warm marble surface with soft directional "
        "light and gentle shadow. Centered near the top, render the restaurant "
        "wordmark 'THE THEATER' in elegant serif type with the small tracked "
        "caps subtitle 'INDIAN KITCHEN & BAR' beneath it, and beneath that in "
        "small italic type: 'Dương Đông, Phú Quốc'. No other text, no dish "
        "photos, no menu items on this page."
    )),
    ("divider-small-plates", (
        STYLE_GUIDE + " This is a SECTION DIVIDER page with no dish list and "
        "no prices — just one beautiful full-bleed atmospheric photograph: a "
        "close-up of golden crispy fried snacks and small plates being "
        "plated, steam and texture visible, shallow depth of field, on a "
        "bright marble surface. Render only a small elegant section label "
        "near the bottom: 'SMALL PLATES, BAR BITES & CHAAT'."
    )),
    ("divider-tandoor", (
        STYLE_GUIDE + " This is a SECTION DIVIDER page with no dish list and "
        "no prices — just one beautiful full-bleed atmospheric photograph: "
        "glowing charcoal embers inside a traditional clay tandoor oven with "
        "a skewer of char-grilled tikka just visible at the edge of frame, "
        "warm dramatic light, shallow depth of field. Render only a small "
        "elegant section label near the bottom: 'TANDOOR, GRILL & MAIN "
        "CURRIES'."
    )),
    ("divider-rice", (
        STYLE_GUIDE + " This is a SECTION DIVIDER page with no dish list and "
        "no prices — just one beautiful full-bleed atmospheric photograph: a "
        "dramatic close-up of fragrant basmati biryani rice being served from "
        "a hammered copper handi with steam rising, on a bright marble "
        "surface. Render only a small elegant section label near the bottom: "
        "'RICE, KHICHDI & BIRYANI'."
    )),
    ("divider-bar", (
        STYLE_GUIDE + " This is a SECTION DIVIDER page with no dish list and "
        "no prices — just one beautiful full-bleed atmospheric photograph: an "
        "elegant flat-lay of drink glassware — a copper mug, a tall glass of "
        "iced lassi, fresh mint and citrus — on a bright marble surface with "
        "soft light. Render only a small elegant section label near the "
        "bottom: 'DRINKS, COFFEE & JUICES'."
    )),
    ("divider-desserts", (
        STYLE_GUIDE + " This is a SECTION DIVIDER page with no dish list and "
        "no prices — just one beautiful full-bleed atmospheric photograph: a "
        "close-up of glossy gulab jamun in saffron syrup with a scoop of "
        "vanilla ice cream, soft bright light, shallow depth of field, on a "
        "bright marble surface. Render only a small elegant section label "
        "near the bottom: 'DESSERTS'."
    )),
    ("closing", (
        STYLE_GUIDE + " This is the CLOSING / thank-you page of the menu: a "
        "full-bleed, elegant, softly lit photograph of an empty premium table "
        "setting — folded linen napkin, cutlery, a single small candle lantern "
        "— on a warm marble surface. Centered, render in elegant serif type: "
        "'DHANYAWAD' with smaller italic type beneath: 'Thank you for dining "
        "with us.' and beneath that the wordmark 'THE THEATER' with small "
        "caps subtitle 'INDIAN KITCHEN & BAR', and small type: '152 Đường Trần "
        "Hưng Đạo, Dương Đông, Phú Quốc'. No dish photos, no prices."
    )),
]

PAGE_ITEMS_PER_PAGE = {
    "Small Plates & Bar Bites": 4,
    "Chaat & Fast Sellers": 4,
    "Tandoor & Grill": 3,
    "Main Curries": 4,
    "Seafood Curries": 3,
    "Breads": 4,
    "Rice & Khichdi": 3,
    "Biryani": 5,
    "Drinks": 6,
    "Coffee": 4,
    "Juices, Smoothies & Iced Tea": 4,
    "Desserts": 5,
}

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

# where hero dividers get inserted, keyed by the category they precede
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
        "page_num": page_num,
        "type": "hero",
        "slug": key,
        "title": key,
        "items": [],
        "reference_photos": [],
        "prompt": prompt,
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

    size = PAGE_ITEMS_PER_PAGE[cat]
    page_groups = list(chunk(cat_items, size))
    total_pages_in_cat = len(page_groups)
    for i, group in enumerate(page_groups, 1):
        refs = [photo_path(it) for it in group]
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
                for it in group
            ],
            "reference_photos": [r for r in refs if r],
            "prompt": build_content_prompt(cat, group, i, total_pages_in_cat),
        })
        page_num += 1

add_hero("closing")

with open(os.path.join(BASE, "menu_pages.json"), "w") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

n_content = sum(1 for p in pages if p["type"] == "content")
n_hero = sum(1 for p in pages if p["type"] == "hero")
print(f"Wrote {len(pages)} pages ({n_content} content, {n_hero} hero) to menu_pages.json")

#!/usr/bin/env python3
"""Groups menu_items.json into full designed menu PAGES using a simple,
reliable uniform-list layout (photo + text row per item, same treatment for
every item) instead of the earlier hero+cascade approach — the cascade's
"leader line" concept was causing stray arrows and leaked instruction text
in generation. Prompts are plain prose (no JSON dumps, no field labels) to
avoid the model rendering internal instruction text onto the page."""
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

# categories where every item shares the same veg/spice status — skip the
# per-item tags entirely rather than showing redundant/inconsistent icons
NO_TAGS_CATEGORIES = {
    "Breads", "Rice & Khichdi", "Drinks", "Coffee",
    "Juices, Smoothies & Iced Tea", "Desserts",
}


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


PAGE_MAX_ITEMS = 4

STYLE_PROSE = (
    "This is one page of a printed restaurant menu, A4 portrait, full-bleed, "
    "flat and front-on like a scanned printed page — never a 3D mockup, never "
    "tilted, no drop shadow around the page edges, no table or background "
    "behind the page. The page background is a warm off-white/cream color "
    "(hex F6F3EC) with a very subtle warm gradient in the top-right corner "
    "only, otherwise a clean flat color, no visible texture or noise. "
    "Typography: use exactly ONE elegant modern serif typeface for numerals "
    "and small italic accents, and exactly ONE clean modern sans-serif "
    "typeface for dish names, prices and body text — the same two typefaces, "
    "same weights, same sizes, same spacing as every other page in this "
    "menu set, so the whole set reads as one consistent printed document. "
    "Ink color for headings and prices is a near-black warm brown (hex "
    "1A1714); body/description text is a muted warm gray-brown (hex "
    "5C564C); thin hairline rules are a pale warm gray (hex D8D2C4)."
)

NEGATIVE_PROSE = (
    "Do not include any watermark, stock-photo logo, placeholder lorem "
    "ipsum text, or UI elements. Do not draw any arrows, pointer lines, "
    "leader lines, or connector lines anywhere on the page — dish photos "
    "sit directly beside their own text with no line connecting them. Do "
    "not render any internal instruction text, field labels, brackets, or "
    "quotation marks anywhere on the page — only the restaurant copy "
    "specified below should appear as visible text. Do not add any page "
    "number, page count, or fraction like '(1/3)' anywhere on the page. Do "
    "not add any decorative background food, extra copies of a dish, or "
    "any item that is not explicitly listed below — the background stays "
    "clean and empty apart from the listed items."
)


def build_header_prose(title, tagline):
    return (
        f"At the very top of the page: a small row of three tiny line-icon "
        f"marks (a leaf, a hand, and a heart), each with a short two-word "
        f"caption beneath in tiny tracked-out capitals reading 'FRESH "
        f"SOURCED', 'HAND CRAFTED', and 'MADE WITH CARE'. To the right of "
        f"that row, right-aligned: the small eyebrow text 'THE THEATER — "
        f"INDIAN KITCHEN & BAR', and directly beneath it in much larger bold "
        f"capitals, right-aligned, the section title '{title}' — render "
        f"this exact title text and nothing else, no page numbers or "
        f"fractions next to it. Beneath that row, a thin horizontal hairline "
        f"rule spanning the page width. Beneath the rule, left-aligned in "
        f"small italic text: '{tagline}'."
    )


FOOTER_PROSE = (
    "At the very bottom of the page: a thin horizontal hairline rule "
    "spanning the page width, and beneath it, centered, small italic gray "
    "text reading exactly: 'All prices are in thousand VND (d). VAT and "
    "service charge is extra. Images are for representation purposes "
    "only.'"
)

TAG_SPEC_PROSE = (
    "Vegetarian icon: a small solid green leaf silhouette immediately "
    "followed by the word 'VEGETARIAN' in small bold green tracked-out "
    "capitals — use this exact same leaf icon and same wording, same size, "
    "every single time it appears, never a different veg symbol. Spice "
    "icon: small solid red chili-pepper silhouettes, one icon per spice "
    "level (1 icon = mild, 2 = medium, 3 = hot) — use this exact same chili "
    "silhouette shape every single time, never dots, never a different "
    "shape, and never a text label next to it."
)


def build_item_block_prose(num, item, hero=False):
    parts = [f"Item {num}: '{item['name']}' — {item['price_vnd_k']}K."]
    parts.append(f"Description: {item['description']}")
    if item.get("_chef_rec"):
        parts.append(
            "This item carries a small solid black pill badge reading "
            "'CHEF'S RECOMMENDED' in white bold small caps, placed "
            "overlapping the top-left corner of its photo."
        )
    tags = []
    if item.get("_show_tags"):
        if item["_veg"]:
            tags.append("it is VEGETARIAN (show the leaf icon)")
        if item["_spice"] > 0:
            tags.append(f"its spice level is {item['_spice']} (show {item['_spice']} chili icon(s))")
    if tags:
        parts.append("Tags: " + "; ".join(tags) + ".")
    return " ".join(parts)


def build_content_prompt(category, page_items, page_num_in_cat, total_pages_in_cat):
    for it in page_items:
        it["_show_tags"] = category not in NO_TAGS_CATEGORIES

    title = category.upper()

    item_blocks = []
    for i, it in enumerate(page_items, 1):
        item_blocks.append(build_item_block_prose(i, it))

    prompt = (
        STYLE_PROSE + " " + NEGATIVE_PROSE + " " + TAG_SPEC_PROSE + "\n\n"
        + build_header_prose(title, TAGLINES.get(category, "")) + "\n\n"
        + "Below the header, lay out the following " + str(len(page_items))
        + " menu items as a simple vertical list, one row per item, evenly "
        + "spaced down the page. Every item's photo is the exact same size "
        + "as every other item's photo on this page — no item is enlarged "
        + "or treated as a hero, they are all equal. Each row: the numbered "
        + "photo on the left (attached as a reference image, in the same "
        + "order as listed below — use each reference photo only for its "
        + "own numbered item, do not mix reference photos between items), "
        + "and beside it on the right: the item number, the dish name in "
        + "bold capitals with its price bold and right-aligned on the same "
        + "line, the description in regular weight beneath, and beneath "
        + "that any vegetarian/spice tags exactly as specified. Each dish's "
        + "name, price and description belong only to that one dish — never "
        + "swap or mix text between different items on the page.\n\n"
        + " ".join(item_blocks) + "\n\n"
        + FOOTER_PROSE
    )
    return prompt, page_items


HERO_PROMPTS = [
    ("divider-small-plates", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page, background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: a "
        "close-up of golden crispy fried snacks and small plates being "
        "plated, steam and texture visible, shallow depth of field, shot on "
        "a warm paper-toned surface. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals: 'SMALL PLATES, BAR BITES & "
        "CHAAT'. No other text anywhere."
    )),
    ("divider-tandoor", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page, background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: glowing "
        "charcoal embers inside a traditional clay tandoor oven with a "
        "skewer of char-grilled tikka just visible at the edge of frame, "
        "warm dramatic light, shallow depth of field. Near the bottom, a "
        "solid dark ink-black bar spanning the page width containing one "
        "line of small elegant bold white tracked-out capitals: 'TANDOOR, "
        "GRILL & MAIN CURRIES'. No other text anywhere."
    )),
    ("divider-rice", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page, background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: a "
        "dramatic close-up of fragrant basmati biryani rice being served "
        "from a hammered copper handi with steam rising, on a warm "
        "paper-toned surface. Near the bottom, a solid dark ink-black bar "
        "spanning the page width containing one line of small elegant bold "
        "white tracked-out capitals: 'RICE, KHICHDI & BIRYANI'. No other "
        "text anywhere."
    )),
    ("divider-bar", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page, background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: an "
        "elegant flat-lay of drink glassware — a copper mug, a tall glass "
        "of iced lassi, fresh mint and citrus — on a warm paper-toned "
        "surface with soft light. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals: 'DRINKS, COFFEE & JUICES'. No "
        "other text anywhere."
    )),
    ("divider-desserts", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page, background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: a "
        "close-up of glossy gulab jamun in saffron syrup with a scoop of "
        "vanilla ice cream, soft bright light, shallow depth of field, on a "
        "warm paper-toned surface. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals: 'DESSERTS'. No other text "
        "anywhere."
    )),
    ("closing", (
        "Design a full-bleed A4 portrait restaurant menu CLOSING page, "
        "background color F6F3EC with a subtle warm radial gradient "
        "top-right, flat and front-on (not a mockup, no page shadow, fills "
        "the entire frame). No arrows, no watermark, no stock logo. "
        "Top-to-bottom, in this exact order, with EACH element appearing "
        "EXACTLY ONCE (never repeat any text block): (1) centered near the "
        "top, large elegant serif text: 'DHANYAWAD', with smaller italic "
        "text directly beneath: 'Thank you for dining with us.' — (2) "
        "below that, centered, a softly lit photograph of an empty premium "
        "table setting — folded linen napkin, cutlery, a single small "
        "candle lantern — on a warm paper-toned surface, trimmed tightly "
        "with a soft contact shadow, no background box — (3) below the "
        "photograph, centered, small bold text 'THE THEATER' with small "
        "tracked caps subtitle 'INDIAN KITCHEN & BAR' beneath — (4) at the "
        "very bottom, centered, small gray text: '152 Duong Tran Hung Dao, "
        "Duong Dong, Phu Quoc'. That is the complete page."
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

# Page 1 is the cover — background art generated separately, real logo
# composited on top locally (not AI-rendered text), so no prompt here.
pages.append({
    "page_num": page_num, "type": "cover", "slug": "cover", "title": "cover",
    "items": [], "reference_photos": [], "prompt": None,
})
page_num += 1


def add_hero(key):
    global page_num
    prompt = dict(HERO_PROMPTS)[key]
    pages.append({
        "page_num": page_num, "type": "hero", "slug": key, "title": key,
        "items": [], "reference_photos": [], "prompt": prompt,
    })
    page_num += 1


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
n_cover = sum(1 for p in pages if p["type"] == "cover")
print(f"Wrote {len(pages)} pages ({n_content} content, {n_hero} hero, {n_cover} cover) to menu_pages.json")

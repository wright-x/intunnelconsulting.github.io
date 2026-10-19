#!/usr/bin/env python3
"""Generates every page for SAPA PREMIUM INDIAN KITCHEN: cover, 8 hero
spotlight pages, and 1-3-dish S-curve pages for every other item — the
proven burgundy/gold cutout template, with a subtle mountain-range motif."""
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
REFS = os.path.join(BASE, "references")


def load_image_part(path, mime="image/png"):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return {"inlineData": {"mimeType": mime, "data": data}}


def call_gemini(prompt, ref_parts, max_retries=5):
    parts = list(ref_parts) + [{"text": prompt}]
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

BACKGROUND = (
    "Design a tall vertical portrait print restaurant menu page, full-bleed, "
    "flat and front-on like a scanned printed page, never a 3D mockup. "
    "Background: a deep, rich wine-burgundy color with a subtle plaster-like "
    "matte texture (like tinted concrete, not glossy), one soft light source "
    "from the upper left creating a gentle warmer burgundy glow that fades "
    "to near-black in the corners, with a fine film-grain texture across "
    "the whole page for a tactile printed feel. The ONLY background "
    "graphic: a faint, barely-perceptible thin gold outline of a "
    "mountain-range silhouette running low along the bottom edge of the "
    "page, with one small gold line-art lotus flower sitting directly "
    "above a short plain horizontal bar (the brand mark, no cup or bowl "
    "shape beneath it) sitting just above the peaks in the bottom-left "
    "corner — both so subtle they read as texture and never compete with "
    "the food or text. Do not add any other script, lettering, "
    "characters, or symbols to the background.\n\n"
    "Typography: the display type is a refined, high-contrast serif with "
    "generous letter spacing in a warm antique gold, with a faint engraved "
    "quality as if pressed into the page. Body copy is an elegant italic "
    "serif in soft cream. Prices use the same gold serif as the display "
    "type. Keep the tone warm and inviting, never bold or heavy, with "
    "plenty of empty burgundy space around every text block.\n\n"
)

ICON_SYSTEM = (
    "Icon system, used consistently for every item: if an item is "
    "vegetarian, place one small gold-outlined circular icon of a single "
    "leaf directly beside its tag, immediately followed by the small gold "
    "tracked capital word 'VEG' — non-vegetarian items get no leaf icon "
    "and no VEG word at all. If an item can be prepared Jain, place a "
    "small gold-outlined circle containing the letter 'J' directly after "
    "the veg icon — items without this note get no J icon. For items "
    "with a spice level above zero, place that many small solid red "
    "chilli-pepper icons (one icon per spice level, one to three total, "
    "never more) after the tag, with no text or numbers beside them — "
    "items with spice level zero get no chilli icons at all.\n\n"
)

TOTAL_PAGES = 44


def footer(page_num):
    return (
        "At the very bottom of the page, centered, a single small gold "
        "line-icon of a lotus flower sitting directly above a short plain "
        "horizontal bar (the brand mark, no cup or bowl shape beneath it), "
        "sitting in a gap within a thin gold horizontal rule spanning the "
        "page width. Below that rule, a slim footer row with three small "
        "elements on one line: at the far left, a small green-outlined "
        "circular icon of a single leaf immediately followed by small gold "
        "text reading 'VEG = Vegetarian'; centered, small gold italic text "
        "reading 'VAT will be charged extra'; at the far right, small gold "
        f"text reading '{page_num}/{TOTAL_PAGES}'. Do "
        "not render any full logo lockup, brand name, or tagline elsewhere on "
        "this page.\n\n"
    )


def footer_render_lines(page_num):
    return (
        f"Footer left: 'VEG = Vegetarian' (with small leaf icon)\n"
        f"Footer center: 'VAT will be charged extra'\n"
        f"Footer right page number: '{page_num}/{TOTAL_PAGES}'\n"
    )


RENDER_DISCIPLINE = (
    "Render ONLY the text explicitly listed below, exactly as written, "
    "nowhere else on the page — no other words, numbers, letters, "
    "measurements, percentages, or watermark text of any "
    "kind. Double-check every letter of the section title before "
    "finalizing — do not drop, merge, or duplicate any letter or word.\n\n"
)


def title_spelling(title):
    letters = title.replace(" ", "").replace("&", "AND").replace("—", "")
    return "-".join(letters), len(letters)


HERO_VISIBILITY_OVERRIDE = {
    "Daal Bukhara": (
        "The dish must be at least 90% visible within the page — only the "
        "very edge of the pot's far rim may bleed off the right side, "
        "never a third or more of the pot. Scale and position it so "
        "nearly the entire balti bowl, both handles, and its contents "
        "are clearly in frame."
    ),
}


def build_hero_prompt(name, tag_prefix, tag_num, title, kicker, page_num):
    it = ITEMS_BY_NAME[name]
    spelled, n_letters = title_spelling(title)
    veg_txt = "yes" if it["veg"] else "no"
    jain_txt = "yes" if it.get("jain") else "no"
    visibility_note = HERO_VISIBILITY_OVERRIDE.get(name, "")
    return (
        BACKGROUND +
        "One single dish, cut out cleanly from its reference photo with no "
        f"background, floating large and confident on the burgundy: "
        f"reference photo 1 is '{name}'. Preserve the reference photo's "
        "exact plating and composition precisely as shown — do not "
        "simplify, remove, or alter any element of the plate; the cutout "
        "must look identical to its reference, just extracted from its "
        "white background. The dish sits right of center, bleeding off "
        "the right edge of the page, shot at the same elevated "
        "three-quarter camera angle looking down as the page lighting, "
        "casting one soft diffuse elliptical shadow toward the lower "
        "right, tilted only a few degrees, never perfectly square. "
        f"Generous empty burgundy space to its left for the text block. {visibility_note}\n\n"
        "Props: a small scattering of whole spices near the bottom left "
        "of the page resting directly on the burgundy — one star anise, a "
        "few green cardamom pods, a few black peppercorns. No cutlery, no "
        "hands, no linen, no table surface, no glassware.\n\n" +
        f"Layout: the words '{title}', spelled exactly {spelled} "
        f"({n_letters} letters, double-check every letter including any "
        "doubled letters), set very large in gold, stacked vertically "
        "down the left edge of the page. Beside that stacked title, at "
        f"the very top, a single short line of small gold text rotated "
        f"vertically reading exactly '{kicker}' and nothing else, "
        "appearing exactly once on the page. Below the title, a bold gold "
        "filled pill badge reading 'CHEF'S RECOMMENDED' in tracked-out "
        "dark serif capitals. The dish's text block sits on the left "
        "side of the page, containing top to bottom: a small "
        "gold-outlined pill tag, the dish name in large gold display "
        "serif, a short thin gold hairline rule, the description in "
        "cream italic serif, then the price in large gold serif.\n\n" +
        ICON_SYSTEM + footer(page_num) + RENDER_DISCIPLINE +
        f"Section title: '{title}'\nKicker: '{kicker}'\nBadge: 'CHEF'S RECOMMENDED'\n"
        f"Dish — tag '{tag_prefix} {tag_num:02d}', name '{name}', "
        f"description '{it['description']}', price '{it['price_k']}K', "
        f"vegetarian: {veg_txt}, jain-adaptable: {jain_txt}, spice level: {it['spice']} (0-3)\n" +
        footer_render_lines(page_num)
    )


def build_section_prompt(title, kicker, tag_prefix, dish_names, start_tag, page_num, note=None):
    n = len(dish_names)
    spelled, n_letters = title_spelling(title)
    lines = []
    for i, name in enumerate(dish_names, 1):
        it = ITEMS_BY_NAME[name]
        tag_num = start_tag + i - 1
        veg_txt = "yes" if it["veg"] else "no"
        jain_txt = "yes" if it.get("jain") else "no"
        lines.append(
            f"Dish {i} — tag '{tag_prefix} {tag_num:02d}', name '{name}', "
            f"description '{it['description']}', price '{it['price_k']}K', "
            f"vegetarian: {veg_txt}, jain-adaptable: {jain_txt}, "
            f"spice level: {it['spice']} (0-3, 0 means no chilli icons)"
        )
    dish_text_block = "\n".join(lines)
    refs_line = "; ".join(f"reference photo {i} is '{name}'" for i, name in enumerate(dish_names, 1))

    arrange = (
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
    )

    return (
        BACKGROUND +
        f"{'One dish' if n == 1 else ('Two dishes' if n == 2 else 'Three dishes')}, "
        "each cut out cleanly from its reference photo with no background, "
        f"floating directly on the burgundy: {refs_line} — match each "
        "exactly to its own text block below, never swap or combine them. "
        "Preserve each reference photo's exact plating, garnish, side "
        "condiments and composition precisely as shown — do not simplify, "
        "remove, or alter any element of the plate; the cutout must look "
        "identical to its reference, just extracted from its white "
        "background. "
        f"{'The plates are the same scale as each other, all with the ' if n > 1 else 'Shot at the '}"
        "same elevated three-quarter camera angle looking down, same key "
        "light from the upper left matching the page lighting, each "
        "casting one soft diffuse elliptical shadow toward the lower "
        "right. " + arrange +
        "Props: a small scattering of whole spices near the bottom left "
        "of the page resting directly on the burgundy — one star anise, "
        "a few green cardamom pods, a few black peppercorns — each with "
        "its own tiny shadow toward the lower right. No cutlery, no "
        "hands, no linen, no table surface, no glassware anywhere on the "
        "page.\n\n" +
        f"Layout: the words '{title}', spelled exactly {spelled} "
        f"({n_letters} letters, double-check every single letter "
        "including any doubled letters before finalizing — do not drop "
        "or merge any letter), set very large in gold, stacked "
        "vertically down the left edge of the page, one line of the "
        "title directly above the next if it wraps. Beside that stacked "
        f"title, at the very top, a single short line of small gold text "
        f"rotated vertically reading exactly '{kicker}' and nothing "
        "else — render precisely these words, no more, no fewer, no "
        "substituted or added words. This text must appear exactly once "
        "on the entire page, never repeated a second time anywhere "
        f"else. {'The dish has' if n == 1 else f'Each of the {n} dishes has'} "
        "its own text block placed on the side of the page opposite its "
        "plate, containing, top to bottom: a small gold-outlined "
        "pill-shaped tag, the dish name in the gold display serif, a "
        "short thin gold hairline rule, the description in cream italic "
        "serif, then the price in gold serif. Text blocks align to the "
        "nearest page edge, with their ragged edge facing the food.\n\n" +
        (f"Below the dish text blocks, a single small line of cream "
         f"italic serif text reading exactly '{note}', appearing once "
         "only.\n\n" if note else "") +
        ICON_SYSTEM + footer(page_num) + RENDER_DISCIPLINE +
        f"Section title: '{title}'\nKicker: '{kicker}'\n{dish_text_block}" +
        (f"\nFooter note: '{note}'" if note else "") +
        "\n" + footer_render_lines(page_num)
    )


COVER_PROMPT = (
    "Design a tall vertical portrait print restaurant menu COVER page, "
    "full-bleed, flat and front-on like a scanned printed page, never a 3D "
    "mockup. Background: a deep, rich wine-burgundy color with a subtle "
    "plaster-like matte texture, soft light glowing gently from the "
    "center, fading to near-black at the corners, fine film grain for a "
    "tactile printed feel. The attached reference image is the "
    "restaurant's exact logo lockup — reproduce it pixel-faithful, "
    "simply recolored from black to the same warm antique gold used "
    "throughout this menu (with a faint engraved quality as if pressed "
    "into the page): the same thin line-art lotus flower sitting "
    "directly above a short plain horizontal bar (no cup or bowl shape "
    "beneath the lotus, no mandala pattern, nothing added), the exact "
    "wordmark 'INDIAN KITCHEN' in the same serif letterforms, the same "
    "'SAPA' line with its flanking hairline dashes beneath it, and the "
    "same 'SOUL OF INDIA' line beneath that — centered in the upper half "
    "of the page, sized generously. Do not add any other text, line, or "
    "tagline beneath the logo. Near the very bottom of the page, a faint "
    "thin gold outline of a mountain-range silhouette spanning the page "
    "width, with a small scattering of whole spices — one star anise, a "
    "few green cardamom pods, a few black peppercorns — resting just "
    "above it, and directly above that, one line of small cream italic "
    "serif text reading 'Freshly prepared. Warmly served. Made for the "
    "mountains.' This tagline sentence must appear exactly ONCE on the "
    "entire page — never repeated a second time anywhere else, never "
    "printed twice, never duplicated above, below, or overlapping "
    "itself. Directly beneath that tagline, in even smaller plain cream "
    "italic serif text, one more line reading exactly 'A 3% surcharge "
    "applies to credit card payments.' — this line also appears exactly "
    "ONCE, never duplicated. No photograph of food anywhere on this "
    "page, no other text, no other graphic elements, no watermark, no "
    "page number.\n\n"
    "Render ONLY this exact text, nowhere else, and each line exactly "
    "once: the reproduced logo lockup exactly as in the reference image "
    "(recolored gold), 'Freshly prepared. Warmly served. Made for the "
    "mountains.', and 'A 3% surcharge applies to credit card payments.'"
)

def closing_prompt(page_num):
    return (
    BACKGROUND +
    "This is a text-only closing information page, no food photography "
    "anywhere on it. Layout: the words 'THANK YOU', stacked vertically "
    "down the left edge of the page in large gold display serif. To the "
    "right, a vertically centered column with generous spacing containing "
    "four text blocks in order, each with a short gold serif heading "
    "followed by cream italic serif body text beneath it:\n"
    "Block 1 heading 'SPICE YOUR WAY', body 'Most curries can be prepared "
    "mild, medium, or Indian hot. Please tell our team your preference "
    "when ordering.'\n"
    "Block 2 heading 'VEGETARIAN & JAIN DINING', body 'A wide selection "
    "of vegetarian dishes is available. Selected dishes can be prepared "
    "without onion and garlic when requested.'\n"
    "Block 3 heading 'GET IN TOUCH', body two lines: "
    "'indiankitchensapa@gmail.com' then on its own line "
    "'+84 034 818 0134'\n"
    "Block 4: a thin gold hairline rule, then centered beneath it in "
    "small gold tracked-out capitals: 'FROM INDIA, WITH WARMTH. FROM "
    "SAPA, WITH A VIEW.', then directly beneath that in small plain "
    "cream italic serif text, one more line reading exactly 'A 3% "
    "surcharge applies to credit card payments.' — this line appears "
    "exactly ONCE, never duplicated.\n\n" +
    footer(page_num) + RENDER_DISCIPLINE +
    "Heading 1: 'SPICE YOUR WAY'\nBody 1: 'Most curries can be prepared "
    "mild, medium, or Indian hot. Please tell our team your preference "
    "when ordering.'\nHeading 2: 'VEGETARIAN & JAIN DINING'\nBody 2: 'A "
    "wide selection of vegetarian dishes is available. Selected dishes "
    "can be prepared without onion and garlic when requested.'\nHeading "
    "3: 'GET IN TOUCH'\nBody 3 line 1: 'indiankitchensapa@gmail.com'\n"
    "Body 3 line 2: '+84 034 818 0134'\nClosing "
    "line: 'FROM INDIA, WITH WARMTH. FROM SAPA, WITH A VIEW.'\nSurcharge "
    "note: 'A 3% surcharge applies to credit card payments.'\nStacked "
    "title: 'THANK YOU'\nRender the email address and phone number "
    "exactly once each, exactly as written, with no extra characters.\n" +
    footer_render_lines(page_num)
)


def spirits_prompt(page_num):
    title = "SPIRITS, WINES & BEERS"
    kicker = "PART EIGHTEEN"
    spelled, n_letters = title_spelling(title)
    return (
        BACKGROUND +
        "This is a text-only pricing list page, no food or drink "
        "photography, no cutout images, no glassware illustrations of "
        "any kind anywhere on it.\n\n"
        f"Layout: the words '{title}', spelled exactly {spelled} "
        f"({n_letters} letters, double-check every letter before "
        "finalizing — do not drop, merge, or duplicate any letter or "
        "word), set very large in gold, stacked vertically down the "
        "left edge of the page. Beside that stacked title, at the very "
        f"top, a single short line of small gold text rotated "
        f"vertically reading exactly '{kicker}' and nothing else, "
        "appearing exactly once on the page.\n\n"
        "To the right of the title, a clean two-column price list "
        "filling the rest of the page: each column heading in gold "
        "tracked-out serif capitals with a thin gold hairline rule "
        "beneath it, and each item below it as one line in cream serif "
        "with the item name on the left and its price in gold serif "
        "aligned to the right, generous line spacing between items and "
        "between sections, no table borders or boxes.\n\n"
        "LEFT COLUMN, top to bottom, in this exact order:\n"
        "Heading 'WHISKY'\n"
        "  Johnnie Walker Red Label — 130K (30ml) / 240K (60ml)\n"
        "  Johnnie Walker Black Label — 160K / 290K (60ml)\n"
        "  Jameson — 140K (30ml) / 250K (60ml)\n"
        "  Jack Daniel's — 150K (30ml) / 270K (60ml)\n"
        "  Glenfiddich 12 Years — 280K (30ml) / 500K (60ml)\n"
        "Heading 'GIN & TEQUILA'\n"
        "  Bombay Sapphire — 160K (30ml) / 290K (60ml)\n"
        "  Jose Cuervo Gold — 130K (30ml) / 230K (60ml)\n"
        "Heading 'RUM'\n"
        "  Bacardi — 120K (30ml) / 200K (60ml)\n"
        "  Captain Morgan — 120K (30ml) / 200K (60ml)\n"
        "Heading 'VODKA'\n"
        "  Smirnoff — 120K (30ml) / 200K (60ml)\n"
        "  Absolut — 140K (30ml) / 250K (60ml)\n"
        "  Grey Goose — 250K (30ml) / 450K (60ml)\n\n"
        "RIGHT COLUMN, top to bottom, in this exact order:\n"
        "Heading 'WINES'\n"
        "  Red Wine (Glass) — 150K\n"
        "  White Wine (Glass) — 150K\n"
        "Heading 'BEERS'\n"
        "  Red Saigon Beer — 85K\n"
        "  Green Saigon Beer — 95K\n"
        "  Heineken — 100K\n"
        "  Budweiser — 100K\n"
        "  Pale Ale — 119K\n"
        "  Good Times — 139K\n\n"
        "The right column ends well above the bottom of the page, "
        "leaving generous empty burgundy space beneath it — never "
        "stretch or pad the right column to match the left column's "
        "height.\n\n"
        "Props: a small scattering of whole spices near the bottom "
        "left of the page resting directly on the burgundy — one star "
        "anise, a few green cardamom pods, a few black peppercorns.\n\n" +
        footer(page_num) + RENDER_DISCIPLINE +
        f"Section title: '{title}'\nKicker: '{kicker}'\n"
        "Left column heading 1: 'WHISKY'\n"
        "  Johnnie Walker Red Label — 130K (30ml) / 240K (60ml)\n"
        "  Johnnie Walker Black Label — 160K (30ml) / 290K (60ml)\n"
        "  Jameson — 140K (30ml) / 250K (60ml)\n"
        "  Jack Daniel's — 150K (30ml) / 270K (60ml)\n"
        "  Glenfiddich 12 Years — 280K (30ml) / 500K (60ml)\n"
        "Left column heading 2: 'GIN & TEQUILA'\n"
        "  Bombay Sapphire — 160K (30ml) / 290K (60ml)\n"
        "  Jose Cuervo Gold — 130K (30ml) / 230K (60ml)\n"
        "Left column heading 3: 'RUM'\n"
        "  Bacardi — 120K (30ml) / 200K (60ml)\n"
        "  Captain Morgan — 120K (30ml) / 200K (60ml)\n"
        "Left column heading 4: 'VODKA'\n"
        "  Smirnoff — 120K (30ml) / 200K (60ml)\n"
        "  Absolut — 140K (30ml) / 250K (60ml)\n"
        "  Grey Goose — 250K (30ml) / 450K (60ml)\n"
        "Right column heading 1: 'WINES'\n"
        "  Red Wine (Glass) — 150K\n"
        "  White Wine (Glass) — 150K\n"
        "Right column heading 2: 'BEERS'\n"
        "  Red Saigon Beer — 85K\n"
        "  Green Saigon Beer — 95K\n"
        "  Heineken — 100K\n"
        "  Budweiser — 100K\n"
        "  Pale Ale — 119K\n"
        "  Good Times — 139K\n" +
        footer_render_lines(page_num)
    )


CATEGORIES = [
    ("BREAKFAST", "BREAKFAST IN THE MOUNTAINS", "PART ONE", "BR", "breakfast", None),
    ("SOUTH INDIAN", "SOUTH INDIAN CLASSICS", "PART TWO", "SI", "south-indian", None),
    ("WARMERS", "SAPA WARMERS", "PART THREE", "SW", "warmers", None),
    ("SMALL PLATES", "SMALL PLATES & CHAAT", "PART FOUR", "SP", "small-plates", None),
    ("CHINESE", "CHINESE SPECIALS", "PART FIVE", "CN", "chinese", None),
    ("TANDOOR VEG", "FROM THE TANDOOR — VEGETARIAN", "PART SIX", "TV", "tandoor-veg", None),
    ("TANDOOR NONVEG", "FROM THE TANDOOR — NON-VEGETARIAN", "PART SEVEN", "TN", "tandoor-nonveg", None),
    ("DALS", "OUR SIGNATURE DALS", "PART EIGHT", "DL", "dals", None),
    ("VEG CURRIES", "VEGETARIAN CURRIES", "PART NINE", "VC", "veg-curries", None),
    ("MEAT CURRIES", "CHICKEN & MEAT CURRIES", "PART TEN", "MC", "meat-curries", None),
    ("BREADS", "BREADS FROM THE TANDOOR", "PART ELEVEN", "BD", "breads", None),
    ("RICE", "RICE & COMFORT BOWLS", "PART TWELVE", "RC", "rice", None),
    ("BIRYANI", "DUM BIRYANI", "PART THIRTEEN", "DB", "biryani", "All biryanis served with raita."),
    ("SWEETS", "SOMETHING SWEET", "PART FOURTEEN", "SS", "sweets", None),
    ("CHAI", "CHAI & MOUNTAIN WARMERS", "PART FIFTEEN", "CH", "chai", None),
    ("COLD DRINKS", "LASSI & COLD DRINKS", "PART SIXTEEN", "CD", "cold-drinks", None),
    ("ZERO PROOF", "SIGNATURE ZERO-PROOF DRINKS", "PART SEVENTEEN", "ZP", "zero-proof", None),
]

BREAKFAST_TIME_NOTE = "Poha, omelette and Maggi are served 9:00 AM - 12:00 PM only."


def balanced_chunks(lst, max_size):
    n = len(lst)
    if n == 0:
        return []
    num_pages = -(-n // max_size)
    base, rem = divmod(n, num_pages)
    chunks, idx = [], 0
    for i in range(num_pages):
        size = base + (1 if i < rem else 0)
        chunks.append(lst[idx:idx + size])
        idx += size
    return chunks


PAGES = []

for cat_key, title, kicker, tag_prefix, slug_prefix, note in CATEGORIES:
    cat_items = [it for it in ITEMS if it["category"] == cat_key]
    heroes = [it for it in cat_items if it["hero"]]
    normal = [it["name"] for it in cat_items if not it["hero"]]
    name_to_idx = {it["name"]: i + 1 for i, it in enumerate(cat_items)}

    for h in heroes:
        PAGES.append({
            "slug": f"{slug_prefix}-hero", "kind": "hero", "name": h["name"],
            "tag_prefix": tag_prefix, "tag_num": name_to_idx[h["name"]],
            "title": title, "kicker": kicker,
        })

    if cat_key == "BREAKFAST":
        all_day = [n for n in normal if n in ("Aloo Paratha", "Paneer Paratha", "Chole Bhature")]
        timed = [n for n in normal if n not in all_day]
        chunks = [(all_day, None)] + [(c, BREAKFAST_TIME_NOTE) for c in balanced_chunks(timed, 3)]
    else:
        chunks = [(c, note if i == len(balanced_chunks(normal, 3)) else None)
                  for i, c in enumerate(balanced_chunks(normal, 3), 1)]

    for page_num, (chunk, page_note) in enumerate(chunks, 1):
        if not chunk:
            continue
        PAGES.append({
            "slug": f"{slug_prefix}-{page_num}", "kind": "section", "names": chunk,
            "tag_prefix": tag_prefix, "start_tag": name_to_idx[chunk[0]],
            "title": title, "kicker": kicker,
            "note": page_note,
        })


PAGES.append({"slug": "spirits-1", "kind": "list", "title": "SPIRITS, WINES & BEERS", "kicker": "PART EIGHTEEN"})


PAGE_NUMBER = {"cover": 1}
for _i, _p in enumerate(PAGES, start=2):
    PAGE_NUMBER[_p["slug"]] = _i
PAGE_NUMBER["closing"] = len(PAGES) + 2


def gen(slug, prompt, ref_paths):
    filepath = os.path.join(PAGES_OUT, f"{slug}.png")
    print(f"Generating {slug}...", flush=True)
    ref_parts = [load_image_part(p) for p in ref_paths]
    img_bytes, err = call_gemini(prompt, ref_parts)
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
        gen("cover", COVER_PROMPT, [os.path.join(REFS, "sapa-logo.png")])

    if not only or "closing" in only:
        gen("closing", closing_prompt(PAGE_NUMBER["closing"]), [])

    for p in PAGES:
        if only and p["slug"] not in only:
            continue
        if p["kind"] == "hero":
            prompt = build_hero_prompt(p["name"], p["tag_prefix"], p["tag_num"], p["title"], p["kicker"], PAGE_NUMBER[p["slug"]])
            refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[p['name']]['slug']}.png")]
        elif p["kind"] == "list":
            prompt = spirits_prompt(PAGE_NUMBER[p["slug"]])
            refs = []
        else:
            prompt = build_section_prompt(p["title"], p["kicker"], p["tag_prefix"], p["names"], p["start_tag"], PAGE_NUMBER[p["slug"]], p.get("note"))
            refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[n]['slug']}.png") for n in p["names"]]
        gen(p["slug"], prompt, refs)


if __name__ == "__main__":
    main()

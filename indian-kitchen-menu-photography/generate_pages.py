#!/usr/bin/env python3
"""Generates every page for SAPA PREMIUM INDIAN KITCHEN: cover, 8 hero
spotlight pages, and grid pages for every other item, all sharing one
burgundy/gold template with a subtle mountain-range motif."""
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
    "page, with one small gold lotus-flower-above-a-cup emblem (echoing "
    "the brand mark) sitting just above the peaks in the bottom-left "
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

FOOTER = (
    "At the very bottom of the page, centered, a single small gold "
    "line-icon of a lotus sitting in a bowl (the brand mark), sitting in "
    "a gap within a thin gold horizontal rule spanning the page width. Do "
    "not render any full logo lockup, brand name, or tagline elsewhere on "
    "this page.\n\n"
)

RENDER_DISCIPLINE = (
    "Render ONLY the text explicitly listed below, exactly as written, "
    "nowhere else on the page — no other words, numbers, letters, "
    "measurements, percentages, page numbers, or watermark text of any "
    "kind. Double-check every letter of the section title before "
    "finalizing — do not drop, merge, or duplicate any letter or word.\n\n"
)


def title_spelling(title):
    letters = title.replace(" ", "").replace("&", "AND")
    return "-".join(letters), len(letters)


def build_hero_prompt(name, tag_prefix, tag_num, title, kicker):
    it = ITEMS_BY_NAME[name]
    spelled, n_letters = title_spelling(title)
    veg_txt = "yes" if it["veg"] else "no"
    jain_txt = "yes" if it.get("jain") else "no"
    return (
        BACKGROUND +
        "One single dish, cut out cleanly from its reference photo with no "
        f"background, floating large and confident on the burgundy: "
        f"reference photo 1 is '{name}'. Preserve the reference photo's "
        "exact plating and composition precisely as shown — the cutout "
        "must look identical to its reference, just extracted from its "
        "white background. The dish sits right of center, bleeding off "
        "the right edge of the page, shot at the same elevated "
        "three-quarter camera angle looking down as the page lighting, "
        "casting one soft diffuse elliptical shadow toward the lower "
        "right, tilted only a few degrees, never perfectly square. "
        "Generous empty burgundy space to its left for the text block.\n\n"
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
        ICON_SYSTEM + FOOTER + RENDER_DISCIPLINE +
        f"Section title: '{title}'\nKicker: '{kicker}'\nBadge: 'CHEF'S RECOMMENDED'\n"
        f"Dish — tag '{tag_prefix} {tag_num:02d}', name '{name}', "
        f"description '{it['description']}', price '{it['price_k']}K', "
        f"vegetarian: {veg_txt}, jain-adaptable: {jain_txt}, spice level: {it['spice']} (0-3)"
    )


def build_grid_prompt(title, kicker, tag_prefix, dish_names, start_tag, note=None):
    n = len(dish_names)
    spelled, n_letters = title_spelling(title)
    lines = []
    for i, name in enumerate(dish_names, 1):
        it = ITEMS_BY_NAME[name]
        tag_num = start_tag + i - 1
        veg_txt = "yes" if it["veg"] else "no"
        jain_txt = "yes" if it.get("jain") else "no"
        lines.append(
            f"Item {i} — tag '{tag_prefix} {tag_num:02d}', name '{name}', "
            f"description '{it['description']}', price '{it['price_k']}K', "
            f"vegetarian: {veg_txt}, jain-adaptable: {jain_txt}, "
            f"spice level: {it['spice']} (0-3)"
        )
    dish_text_block = "\n".join(lines)
    refs_line = "; ".join(f"reference photo {i} is '{name}'" for i, name in enumerate(dish_names, 1))
    note_line = f"\n\nAt the bottom of the item list, small italic cream text reading exactly: '{note}'" if note else ""
    note_render = f"\nFooter note: '{note}'" if note else ""

    return (
        BACKGROUND +
        f"{n} small dishes, each cut out cleanly from its reference photo "
        f"with no background: {refs_line} — match each exactly to its own "
        "row below, never swap or combine them. Preserve each reference "
        "photo's exact plating precisely as shown, just extracted from "
        "its white background.\n\n"
        f"Layout: a clean two-column list grid of {n} rows (fill down "
        "the left column top to bottom, then the right column), each row "
        "containing a small square photo of that dish on one side and, "
        "beside it, its own text block: a small gold-outlined pill tag, "
        "the item name in gold serif, the description in cream italic "
        "serif underneath, then the price in gold serif, with the veg/"
        "jain/spice icon row directly beneath the price. Generous even "
        "spacing between rows, no dish photo touching another. " +
        f"The words '{title}', spelled exactly {spelled} ({n_letters} "
        "letters, double-check every letter), set very large in gold, "
        "stacked vertically down the left edge of the page. Beside that "
        "stacked title, at the very top, a single short line of small "
        f"gold text rotated vertically reading exactly '{kicker}' and "
        "nothing else, appearing exactly once on the page." + note_line + "\n\n" +
        ICON_SYSTEM + FOOTER + RENDER_DISCIPLINE +
        f"Section title: '{title}'\nKicker: '{kicker}'\n{dish_text_block}{note_render}"
    )


COVER_PROMPT = (
    "Design a tall vertical portrait print restaurant menu COVER page, "
    "full-bleed, flat and front-on like a scanned printed page, never a 3D "
    "mockup. Background: a deep, rich wine-burgundy color with a subtle "
    "plaster-like matte texture, soft light glowing gently from the "
    "center, fading to near-black at the corners, fine film grain for a "
    "tactile printed feel. The attached reference image is the "
    "restaurant's exact logo lockup — reproduce it pixel-faithful: the "
    "same gold lotus-flower-above-a-cup emblem, the exact wordmark "
    "'INDIAN KITCHEN' in the same serif letterforms, the same 'SAPA' "
    "line with its flanking hairline dashes beneath it, and the same "
    "'SOUL OF INDIA' line beneath that — centered in the upper two-thirds "
    "of the page, sized generously. Beneath the reproduced logo, in "
    "smaller tracked-out gold capitals, three centered lines of text: "
    "'SAPA PREMIUM INDIAN KITCHEN', then a thin gold hairline rule, then "
    "'INDIAN COMFORT FOOD · TANDOOR · CHAI', then a line of small cream "
    "italic serif text reading 'Freshly prepared. Warmly served. Made "
    "for the mountains.' Near the very bottom of the page, a faint thin "
    "gold outline of a mountain-range silhouette spanning the page width, "
    "with a small scattering of whole spices — one star anise, a few "
    "green cardamom pods, a few black peppercorns — resting just above "
    "it. No photograph of food anywhere on this page, no other text, no "
    "other graphic elements, no watermark, no page number.\n\n"
    "Render ONLY this exact text, nowhere else: the reproduced logo "
    "lockup exactly as in the reference image, 'SAPA PREMIUM INDIAN "
    "KITCHEN', 'INDIAN COMFORT FOOD · TANDOOR · CHAI', and 'Freshly "
    "prepared. Warmly served. Made for the mountains.'"
)

CLOSING_PROMPT = (
    BACKGROUND +
    "This is a text-only closing information page, no food photography "
    "anywhere on it. Layout: the words 'THANK YOU', stacked vertically "
    "down the left edge of the page in large gold display serif. To the "
    "right, a vertically centered column with generous spacing containing "
    "three text blocks in order, each with a short gold serif heading "
    "followed by cream italic serif body text beneath it:\n"
    "Block 1 heading 'SPICE YOUR WAY', body 'Most curries can be prepared "
    "mild, medium, or Indian hot. Please tell our team your preference "
    "when ordering.'\n"
    "Block 2 heading 'VEGETARIAN & JAIN DINING', body 'A wide selection "
    "of vegetarian dishes is available. Selected dishes can be prepared "
    "without onion and garlic when requested.'\n"
    "Block 3: a thin gold hairline rule, then centered beneath it in "
    "small gold tracked-out capitals: 'FROM INDIA, WITH WARMTH. FROM "
    "SAPA, WITH A VIEW.'\n\n" +
    FOOTER + RENDER_DISCIPLINE +
    "Heading 1: 'SPICE YOUR WAY'\nBody 1: 'Most curries can be prepared "
    "mild, medium, or Indian hot. Please tell our team your preference "
    "when ordering.'\nHeading 2: 'VEGETARIAN & JAIN DINING'\nBody 2: 'A "
    "wide selection of vegetarian dishes is available. Selected dishes "
    "can be prepared without onion and garlic when requested.'\nClosing "
    "line: 'FROM INDIA, WITH WARMTH. FROM SAPA, WITH A VIEW.'\nStacked "
    "title: 'THANK YOU'"
)

CATEGORIES = [
    ("BREAKFAST", "BREAKFAST IN THE MOUNTAINS", "PART ONE", "BR", "breakfast", None),
    ("WARMERS", "SAPA WARMERS", "PART TWO", "SW", "warmers", None),
    ("MAGGI", "MAGGI IN THE MOUNTAINS", "PART THREE", "MG", "maggi", None),
    ("SMALL PLATES", "SMALL PLATES & CHAAT", "PART FOUR", "SP", "small-plates", None),
    ("TANDOOR VEG", "FROM THE TANDOOR — VEGETARIAN", "PART FIVE", "TV", "tandoor-veg", None),
    ("TANDOOR NONVEG", "FROM THE TANDOOR — NON-VEGETARIAN", "PART SIX", "TN", "tandoor-nonveg", None),
    ("DALS", "OUR SIGNATURE DALS", "PART SEVEN", "DL", "dals", None),
    ("VEG CURRIES", "VEGETARIAN CURRIES", "PART EIGHT", "VC", "veg-curries", None),
    ("MEAT CURRIES", "CHICKEN & MEAT CURRIES", "PART NINE", "MC", "meat-curries", None),
    ("BREADS", "BREADS FROM THE TANDOOR", "PART TEN", "BD", "breads", None),
    ("RICE", "RICE & COMFORT BOWLS", "PART ELEVEN", "RC", "rice", None),
    ("BIRYANI", "DUM BIRYANI", "PART TWELVE", "DB", "biryani", "All biryanis served with raita."),
    ("SWEETS", "SOMETHING SWEET", "PART THIRTEEN", "SS", "sweets", None),
    ("CHAI", "CHAI & MOUNTAIN WARMERS", "PART FOURTEEN", "CH", "chai", None),
    ("COLD DRINKS", "LASSI & COLD DRINKS", "PART FIFTEEN", "CD", "cold-drinks", None),
    ("ZERO PROOF", "SIGNATURE ZERO-PROOF DRINKS", "PART SIXTEEN", "ZP", "zero-proof", None),
]


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


PAGES = []  # list of (slug, kind, prompt_fn_args, ref_names)

for cat_key, title, kicker, tag_prefix, slug_prefix, note in CATEGORIES:
    cat_items = [it for it in ITEMS if it["category"] == cat_key]
    heroes = [it for it in cat_items if it["hero"]]
    normal = [it["name"] for it in cat_items if not it["hero"]]
    # index within category (1-based) preserved for tag numbering
    name_to_idx = {it["name"]: i + 1 for i, it in enumerate(cat_items)}

    for h in heroes:
        PAGES.append({
            "slug": f"{slug_prefix}-hero",
            "kind": "hero",
            "name": h["name"],
            "tag_prefix": tag_prefix,
            "tag_num": name_to_idx[h["name"]],
            "title": title,
            "kicker": kicker,
        })

    for page_num, chunk in enumerate(balanced_chunks(normal, 6), 1):
        PAGES.append({
            "slug": f"{slug_prefix}-{page_num}",
            "kind": "grid",
            "names": chunk,
            "tag_prefix": tag_prefix,
            "start_tag": name_to_idx[chunk[0]],
            "title": title,
            "kicker": kicker,
            "note": note if page_num == len(balanced_chunks(normal, 6)) else None,
        })


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
        gen("cover", COVER_PROMPT, [os.path.join(REFS, "sapa-logo.jpg")])

    if not only or "closing" in only:
        gen("closing", CLOSING_PROMPT, [])

    for p in PAGES:
        if only and p["slug"] not in only:
            continue
        if p["kind"] == "hero":
            prompt = build_hero_prompt(p["name"], p["tag_prefix"], p["tag_num"], p["title"], p["kicker"])
            refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[p['name']]['slug']}.png")]
        else:
            prompt = build_grid_prompt(p["title"], p["kicker"], p["tag_prefix"], p["names"], p["start_tag"], p.get("note"))
            refs = [os.path.join(OUT, f"{ITEMS_BY_NAME[n]['slug']}.png") for n in p["names"]]
        gen(p["slug"], prompt, refs)


if __name__ == "__main__":
    main()

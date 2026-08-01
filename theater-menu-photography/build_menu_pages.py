#!/usr/bin/env python3
"""Groups menu_items.json into full designed menu PAGES using an asymmetric
hero+cascade layout. Prompts are plain prose (no JSON dumps, no field
labels) to avoid the model rendering internal instruction text onto the
page. Veg and non-veg items are NEVER mixed on the same page. Categories
that are uniformly vegetarian/non-spicy get no per-item tags at all."""
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

ITEMS_BY_NAME = {it["name"]: it for it in ITEMS}

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


SPICE_OVERRIDE = {
    "Samosa with Mint Chutney": 2,
    "Masala Papad": 2,
    "Papad": 1,
    "Dal Tadka": 1,
    "Egg Bhurji": 2,
}


def spice_level(item):
    if item["name"] in SPICE_OVERRIDE:
        return SPICE_OVERRIDE[item["name"]]
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
    "Tandoori Chicken", "Chicken Biryani",
    "Paneer Tikka Skewers", "Chole Bhature", "Gulab Jamun with Vanilla Ice Cream",
    "Non-Veg Mixed Platter", "Goan Prawn Curry", "Pani Puri Shots",
    "Mango Lassi", "Kadai Chicken",
}

TAGLINES = {
    "Theater Signatures": "Our most celebrated dishes, presented with a little drama.",
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


def cap_sentence(s):
    """Capitalize the first letter of the string and after each '. '."""
    parts = re.split(r"(\. )", s)
    out = []
    cap_next = True
    for part in parts:
        if cap_next and part and part not in (". ",):
            part = part[0].upper() + part[1:]
            cap_next = False
        if part == ". ":
            cap_next = True
        out.append(part)
    return "".join(out)


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


def veg_split_chunks(items, max_size):
    """Split into veg-only and non-veg-only chunks — a page never mixes
    vegetarian and non-vegetarian items."""
    veg = [it for it in items if it["_veg"]]
    nonveg = [it for it in items if not it["_veg"]]
    return balanced_chunks(veg, max_size) + balanced_chunks(nonveg, max_size)


PAGE_MAX_ITEMS = 4

STYLE_PROSE = (
    "This is one page of a printed restaurant menu, A4 portrait, full-bleed, "
    "flat and front-on like a scanned printed page — never a 3D mockup, never "
    "tilted, no drop shadow around the page edges, no table or background "
    "behind the page. The page background is a warm off-white/cream color "
    "(hex F6F3EC) with a very subtle warm gradient in the top-right corner "
    "only, otherwise a clean flat color, no visible texture or noise. "
    "Typography: use exactly ONE elegant premium serif typeface for "
    "EVERYTHING on the page — the section title, dish names, prices, "
    "numerals, and the smaller description paragraphs — the same serif "
    "family, same weights, same spacing as every other page in this menu "
    "set, so the whole set reads as one consistent printed document. Do not "
    "use a plain sans-serif anywhere; the whole page including the small "
    "description text is set in the elegant serif. Every line of text uses "
    "correct sentence capitalization (capital letter at the start of each "
    "sentence), never all-lowercase. Ink color for headings, dish names and "
    "prices is a near-black warm brown (hex 1A1714); description text is a "
    "muted warm gray-brown (hex 5C564C); thin hairline rules are a pale warm "
    "gray (hex D8D2C4)."
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
    "clean and empty apart from the listed items. Never repeat the same "
    "photo twice for two different items. Each item's name, price and "
    "description must appear EXACTLY ONCE on the page — never print any "
    "dish name, price or description text twice, even in a different "
    "position. Never print the words 'hero' or 'secondary' anywhere on "
    "the page — those describe layout roles only, never visible text. "
    "Never print the words 'Spice level' or 'Spice:' or any label before "
    "the chili icons — the chili icons must appear completely on their "
    "own with no preceding word or colon of any kind. All body text must "
    "use the same solid ink-brown/gray-brown color at full, consistent "
    "opacity as every other line on the page — never render any text in "
    "a faded, washed-out, low-contrast, or lighter shade than the rest. "
    "Print each dish name exactly as given, character for character — "
    "never append extra words after it, never merge it with another "
    "item's name or description, never invent a second title for the "
    "same dish. Never add an apostrophe, quotation mark, or any other "
    "stray punctuation mark to a dish name that isn't part of the name "
    "itself. Every item number on this page must use the exact same "
    "format: a plain arabic numeral followed by a period, like '1.', "
    "'2.', '3.' — never a leading zero like '01.', never a numeral "
    "without its period, never a different numbering style for "
    "different items on the same page. Every price on this page must "
    "use the exact same format: the item name, then an em dash '—', "
    "then the price, like 'Item Name — 199K' — never omit the dash for "
    "some items while using it for others. The vegetarian leaf tag (when "
    "present) and the chili icons (when present) always sit together on "
    "their own single line placed directly beneath the price line, in "
    "this fixed order every single time: the leaf icon and 'VEGETARIAN' "
    "first, then any chili icons after — never place these tags in a "
    "different position, order, or line from one item to another on the "
    "same page."
)


def build_header_prose(title, tagline, spice_legend=False):
    legend_note = ""
    if spice_legend:
        legend_note = (
            " Directly beneath the tagline, one small line explaining the "
            "spice icons, set in the same plain serif body font as the "
            "rest of the page (not italic, not tracked-out capitals, "
            "small and simple, muted gray-brown color), with three groups "
            "spaced generously apart left to right: group one shows "
            "exactly ONE small red chili-pepper icon followed by the "
            "word 'Mild'; group two shows exactly TWO small red "
            "chili-pepper icons side by side followed by the word "
            "'Medium'; group three shows exactly THREE small red "
            "chili-pepper icons side by side followed by the word 'Hot'. "
            "Double-check the icon count in each group before finalizing "
            "— group one has 1 icon, group two has 2 icons, group three "
            "has 3 icons, never any other count."
        )
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
        f"small italic text: '{tagline}'." + legend_note
    )


FOOTER_PROSE = (
    "At the very bottom of the page: a thin horizontal hairline rule "
    "spanning the page width, and beneath it, centered, small italic gray "
    "text reading exactly: 'All prices are in thousand VND (d). VAT and "
    "service charge are extra. Images are for representation purposes "
    "only.'"
)

TAG_SPEC_PROSE = (
    "Vegetarian icon (ONLY for items explicitly marked VEGETARIAN below): a "
    "small solid green leaf silhouette immediately followed by the word "
    "'VEGETARIAN' in small bold green tracked-out capitals — use this exact "
    "same leaf icon and same wording, same size, every single time. The "
    "leaf icon must NEVER appear by itself without the word 'VEGETARIAN' "
    "beside it — every vegetarian item on this page gets the exact same "
    "leaf-plus-word treatment, with zero exceptions and zero inconsistency "
    "between items on the same page. For any "
    "item that is explicitly marked NOT VEGETARIAN below (chicken, prawn, "
    "fish, egg, or any meat/seafood dish), you must NOT show the leaf icon, "
    "the word VEGETARIAN, or anything green near it — leave that space "
    "completely blank instead, do not write any other word there either "
    "(no 'non-veg', no 'mild', no 'medium', nothing). Spice icon (only "
    "when a spice level is given below): small solid red chili-pepper "
    "silhouettes, one icon per spice level (1 icon = mild, 2 = medium, 3 = "
    "hot) — use this exact same chili silhouette shape every single time, "
    "never dots, never a different shape, and never any text label next to "
    "the chili icons — just the icons alone, no words like 'mild' or "
    "'medium' anywhere, and absolutely never the words 'Spice level' or "
    "'Spice:' either — print ONLY the bare chili-pepper glyphs with no "
    "word or punctuation before or after them."
)

NO_TAGS_PROSE = (
    "IMPORTANT: every item on this page is plain and mild by default — do "
    "NOT show any vegetarian leaf icon, the word VEGETARIAN, any chili "
    "icon, or any spice-level indicator anywhere on this page, for any "
    "item. No tags of any kind appear near any dish on this page."
)

PHOTO_TREATMENT_PROSE = (
    "Each numbered reference photo shows the true appearance of that exact "
    "dish on its plate or glass — extract it as a clean cutout with its own "
    "background completely removed, and place it on the page floating "
    "on a soft realistic warm dark-brown contact shadow beneath it. Even if "
    "the reference photo has a plain gray, white, or studio-backdrop "
    "rectangular background, you must cut the dish/glass/vessel out of it "
    "and completely discard that rectangular background — never leave any "
    "trace of the reference photo's own canvas, frame, or background edges "
    "visible on the page (no hard-edged box, no visible white or gray "
    "rectangle, no rounded-corner card, no drop shadow shaped like a "
    "rectangle — only the soft irregular contact shadow directly under the "
    "object itself). Preserve the full object shown in each reference "
    "photo exactly as it appears — if a glass has a stem, keep the stem "
    "visible; if a dish is on a tray or in a bowl, keep the whole vessel "
    "visible; do not crop off any part of the reference object. Position "
    "every floating photo so it sits entirely within the page with "
    "comfortable margin on all sides — never let a dish, its plate, bowl, "
    "or stand touch or run off the top, bottom, or side edge of the page."
)


def build_item_block_prose(num, item, hero=False, show_tags=True):
    size_note = "LARGE (about 45% of the page width)" if hero else "smaller (about 28% of the page width, same size as the other secondary photos)"
    desc = cap_sentence(item["description"])
    parts = [f"Item {num}: '{item['name']}' — {item['price_vnd_k']}K. Photo size: {size_note}."]
    parts.append(f"Description: {desc}")
    if item.get("_chef_rec"):
        parts.append(
            "This item carries a small solid black pill badge reading "
            "'CHEF'S RECOMMENDED' in white bold small caps, placed "
            "overlapping the top-left corner of its photo."
        )
    if show_tags:
        if item["_veg"]:
            parts.append(f"This item IS VEGETARIAN — show the leaf icon and the word VEGETARIAN next to it.")
        else:
            parts.append(f"This item is NOT VEGETARIAN (it contains meat, egg, or seafood) — do not show any vegetarian tag or leaf icon near it, leave that space blank.")
        if item["_spice"] > 0:
            parts.append(f"Its spice level is {item['_spice']} out of 3 — show exactly {item['_spice']} chili icon(s), no text label.")
    return " ".join(parts)


def build_content_prompt(category, page_items, show_tags, spice_legend=False, title=None, tagline=None):
    for it in page_items:
        it["_show_tags"] = show_tags

    title = title or category.upper()
    hero_idx = 0
    for i, it in enumerate(page_items):
        if it.get("_chef_rec"):
            hero_idx = i
            break
    hero = page_items[hero_idx]
    secondary = [it for i, it in enumerate(page_items) if i != hero_idx]

    item_blocks = [build_item_block_prose(1, hero, hero=True, show_tags=show_tags)]
    for i, it in enumerate(secondary, 2):
        item_blocks.append(build_item_block_prose(i, it, hero=False, show_tags=show_tags))

    ordered_items = [hero] + secondary

    ref_names = [f"{i}) {it['name']}" for i, it in enumerate(ordered_items, 1)]
    ref_recap = (
        f"There are exactly {len(ordered_items)} reference photos attached "
        f"to this request, in this exact order: " + "; ".join(ref_names) + ". "
        "Match reference photo 1 to item 1, photo 2 to item 2, and so on in "
        "strict order — never skip one, never reuse one for a different "
        "item, never combine two reference photos into one item's photo. "
        "Every item listed below must have its own distinct photo visible "
        "on the page — do not omit any item. "
        f"This page contains EXACTLY {len(ordered_items)} menu item(s) — "
        f"not one more, not one less. Do not invent, duplicate, split, or "
        f"repeat any item to fill space; do not create a second variant of "
        f"any item with a different or misspelled name. If the layout "
        f"looks sparse with only {len(ordered_items)} item(s), leave the "
        f"extra space empty and elegant — never pad the page with an "
        f"extra invented dish."
    )

    tags_prose = TAG_SPEC_PROSE if show_tags else NO_TAGS_PROSE

    prompt = (
        STYLE_PROSE + " " + NEGATIVE_PROSE + " " + tags_prose + " "
        + PHOTO_TREATMENT_PROSE + " " + ref_recap + "\n\n"
        + build_header_prose(title, tagline if tagline is not None else TAGLINES.get(category, ""), spice_legend=spice_legend) + "\n\n"
        + "Below the header, use a confident asymmetric editorial layout, "
        + "generous negative space, dishes floating with only a soft shadow "
        + "grounding them — art-directed, not a rigid grid. These layout "
        + "roles (item 1 being the featured dish, the rest being smaller "
        + "supporting dishes) are for YOUR layout planning only — never "
        + "print any role name as text on the page. Item 1's large photo "
        + "sits near the top of the content area, with its number, name, "
        + "price and description in larger type beside it. The remaining "
        + str(len(secondary)) + " item(s) have smaller photos (all the "
        + "same smaller size as each other) staggered down the rest of "
        + "the page, alternating left and right sides for visual rhythm, "
        + "each with its own number, name, price and description in "
        + "normal type directly beside its own photo — normal spacing "
        + "only, absolutely NO line, arrow, or connector drawn between "
        + "any photo and its text.\n\n"
        + " ".join(item_blocks) + "\n\n"
        + FOOTER_PROSE
    )
    return prompt, ordered_items


SPOTLIGHT_ALLERGENS = {
    "Daal Bukhara": "Dairy",
    "Royal Butter Chicken": "Dairy, Nuts",
    "Shahi Dum Biryani": "Dairy, Gluten",
}

SPOTLIGHT_BACKDROP = (
    "Background: a rich, dark, moody restaurant ambiance filling the "
    "entire page edge-to-edge — deep charcoal-brown tones, soft warm "
    "bokeh lights blurred in the background suggesting a dim elegant "
    "dining room. In each of the four corners, a small, thin, elegant "
    "gold ornamental line-art flourish (a corner mark only, not a full "
    "border or frame)."
)


def build_spotlight_prompt(item):
    allergens = SPOTLIGHT_ALLERGENS.get(item["name"], "")
    return (
        "Design a full-bleed A4 portrait DISH SPOTLIGHT page — a dramatic "
        "single-dish showcase page, not a standard menu list page. "
        + SPOTLIGHT_BACKDROP + " The attached reference photo shows the true "
        "appearance of this dish — feature it large, prominent and "
        "dramatically lit in the lower half of the page, extracted "
        "cleanly from its own reference background and placed naturally "
        "into this dark moody scene with a realistic shadow and soft warm "
        f"rim lighting. In the upper third of the page, centered, the dish "
        f"name '{item['name']}' in large elegant white premium serif type; "
        f"directly beneath it, smaller gold tracked-out capital text "
        f"reading '{item['price_vnd_k']}K'; directly beneath that, in "
        f"small light gray serif type spanning no more than four lines, "
        f"the description '{cap_sentence(item['description'])}'; and "
        f"directly beneath the description, in small muted gold italic "
        f"text, 'Contains: {allergens}.' Each of these four text blocks "
        "appears EXACTLY ONCE, in this order, nowhere else on the page. "
        "No other text, no watermark, no page number, no arrows anywhere."
    )


def build_biryani_spotlight_prompt(chicken_item, veg_item):
    allergens = SPOTLIGHT_ALLERGENS.get("Shahi Dum Biryani", "")
    return (
        "Design a full-bleed A4 portrait DISH SPOTLIGHT page — a dramatic "
        "single-dish showcase page with TWO menu options, not a standard "
        "menu list page. " + SPOTLIGHT_BACKDROP + " The attached reference "
        "photo shows the true appearance of this dish — feature it large, "
        "prominent and dramatically lit in the lower half of the page, "
        "extracted cleanly from its own reference background and placed "
        "naturally into this dark moody scene with a realistic shadow and "
        "soft warm rim lighting. In the upper third of the page, centered, "
        "the dish name 'Shahi Dum Biryani' in large elegant white premium "
        "serif type. Directly beneath it, two option blocks side by side "
        "or stacked, clearly separated by a thin gold hairline: LEFT/FIRST "
        f"option in gold tracked-out capitals 'CHICKEN — {chicken_item['price_vnd_k']}K', "
        f"with small light gray serif text beneath it (no more than three "
        f"lines) reading '{cap_sentence(chicken_item['description'])}'; "
        f"RIGHT/SECOND option in gold tracked-out capitals 'VEGETARIAN "
        f"(PANEER) — {veg_item['price_vnd_k']}K', with small light gray "
        f"serif text beneath it (no more than three lines) reading "
        f"'{cap_sentence(veg_item['description'])}'. Beneath both options, "
        f"in small muted gold italic text, 'Contains: {allergens}.' Each "
        "text block appears EXACTLY ONCE. No other text, no watermark, no "
        "page number, no arrows anywhere."
    )


SPOTLIGHT_BEFORE_SLUG = {
    "main-curries-1": "Daal Bukhara",
    "main-curries-4": "Royal Butter Chicken",
    "biryani-1": "__biryani_spotlight__",
}

HERO_PROMPTS = [
    ("divider-small-plates", (
        "Design a full-bleed restaurant menu SECTION DIVIDER page. There is "
        "NO cream or off-white background color anywhere on this page — "
        "the photograph itself is the entire page, covering literally "
        "every pixel from edge to edge, corner to corner, with NO border, "
        "no frame, no card, no mat, no inset margin, no cream padding "
        "around it of any kind. Flat and front-on, not a mockup, no page "
        "shadow. No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: a "
        "close-up of golden crispy fried snacks and small plates being "
        "plated, steam and texture visible, shallow depth of field, shot on "
        "a warm paper-toned surface. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals in a premium serif typeface: "
        "'SMALL PLATES, BAR BITES & CHAAT'. No other text anywhere."
    )),
    ("divider-tandoor", (
        "Design a full-bleed A4 portrait restaurant menu SECTION DIVIDER "
        "page. The photograph fills the ENTIRE page edge-to-edge with NO "
        "border, no frame, no card, no inset, no margin, no cream padding "
        "around it anywhere — the photo IS the full page, corner to "
        "corner, exactly like a full-bleed magazine page (not a photo "
        "placed on a background). Flat and front-on, not a mockup, no page "
        "shadow. No dish list, no prices, no arrows, no watermark, no "
        "stock logo — just one beautiful mouth-watering photograph: "
        "multiple luscious skewers of char-grilled tandoori paneer tikka, "
        "glistening with charred edges and vivid red-orange marinade, held "
        "vertically right in front of the glowing open mouth of a "
        "traditional clay tandoor oven (bhatti) — the tandoor's charcoal "
        "embers glow bright orange-red inside the dark clay interior "
        "directly behind the skewers, with wisps of smoke rising, so the "
        "oven itself is clearly visible and recognizable behind the food, "
        "not just a plain background. Fresh mint and lemon wedges "
        "scattered in the immediate foreground, warm dramatic firelit "
        "tandoor-style lighting, shallow depth of field with the tandoor "
        "mouth still identifiable. Near the bottom, a solid dark "
        "ink-black bar spanning the full page width edge-to-edge "
        "containing one line of small elegant bold white tracked-out "
        "capitals in a premium serif typeface: 'TANDOOR, GRILL & MAIN "
        "CURRIES'. No other text anywhere."
    )),
    ("divider-rice", (
        "Design a full-bleed restaurant menu SECTION DIVIDER page. There is "
        "NO cream or off-white background color anywhere on this page — "
        "the photograph itself is the entire page, covering literally "
        "every pixel from edge to edge, corner to corner, with NO border, "
        "no frame, no card, no mat, no inset margin, no cream padding "
        "around it of any kind. Flat and front-on, not a mockup, no page "
        "shadow. No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful, authentic-looking "
        "photograph: a dramatic close-up of real fragrant basmati biryani "
        "rice, layered long golden-yellow saffron-stained grains next to "
        "paler rice, with visible whole spices scattered through it (bay "
        "leaves, whole cloves, green cardamom pods, a cinnamon stick, "
        "strands of saffron) and fried onions and fresh mint leaves on "
        "top, served in a well-worn traditional hammered copper biryani "
        "handi with a partially lifted lid resting beside it, gentle "
        "steam rising, shot with warm natural light on a rustic dark wood "
        "surface — the rice must look genuinely home-cooked and real, not "
        "generic or stock-photo-like. Near the bottom, a solid dark ink-black bar "
        "spanning the page width containing one line of small elegant bold "
        "white tracked-out capitals in a premium serif typeface: 'RICE, "
        "KHICHDI & BIRYANI'. No other text anywhere."
    )),
    ("divider-desserts", (
        "Design a full-bleed restaurant menu SECTION DIVIDER page. There is "
        "NO cream or off-white background color anywhere on this page — "
        "the photograph itself is the entire page, covering literally "
        "every pixel from edge to edge, corner to corner, with NO border, "
        "no frame, no card, no mat, no inset margin, no cream padding "
        "around it of any kind. Flat and front-on, not a mockup, no page "
        "shadow. No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: a "
        "close-up of glossy gulab jamun in saffron syrup with a scoop of "
        "vanilla ice cream, soft bright light, shallow depth of field, on a "
        "warm paper-toned surface. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals in a premium serif typeface: "
        "'DESSERTS'. No other text anywhere."
    )),
    ("divider-bar", (
        "Design a full-bleed restaurant menu SECTION DIVIDER page. There is "
        "NO cream or off-white background color anywhere on this page — "
        "the photograph itself is the entire page, covering literally "
        "every pixel from edge to edge, corner to corner, with NO border, "
        "no frame, no card, no mat, no inset margin, no cream padding "
        "around it of any kind. Flat and front-on, not a mockup, no page "
        "shadow. No dish list, no prices, no arrows, no "
        "watermark, no stock logo — just one beautiful photograph: an "
        "elegant flat-lay of drink glassware — a copper mug, a tall glass "
        "of iced lassi, fresh mint and citrus — on a warm paper-toned "
        "surface with soft light. Near the bottom, a solid dark ink-black "
        "bar spanning the page width containing one line of small elegant "
        "bold white tracked-out capitals in a premium serif typeface: "
        "'DRINKS & SPIRITS'. No other text anywhere."
    )),
    ("back-cover", (
        "Design a full-bleed A4 portrait restaurant menu BACK COVER page, "
        "clean warm white/cream paper background (hex F6F3EC) with a very "
        "subtle warm radial gradient top-right, flat and front-on like a "
        "scanned printed page, not a mockup, no page shadow. This is the "
        "final page of the menu — both a warm thank-you and a commercially "
        "useful closing page. Behind all the text described below, very "
        "faint and subtle in the background (light warm-gray, low "
        "contrast, watermark-like, not competing with the text in front "
        "of it), a large detailed fine line-art illustration of the Taj "
        "Mahal with its reflecting pool, positioned so it fills much of "
        "the lower two-thirds of the page as a gentle atmospheric "
        "backdrop. "
        "Top-to-bottom in front of that backdrop, in this exact order, "
        "each element appearing EXACTLY ONCE: "
        "(1) Centered near the top: the attached reference image is the "
        "restaurant's exact logo lockup — reproduce it exactly "
        "(letterforms, font, 'INDIAN KITCHEN & BAR' subtitle, small star "
        "divider), pixel-faithful, sized to about 40% of the page width, "
        "with small elegant italic text directly beneath reading 'Phu "
        "Quoc'. "
        "(2) Below that, centered, large elegant premium serif text "
        "reading exactly 'DHANYAWAD', with smaller tracked-out capital "
        "text directly beneath reading 'THANK YOU FOR DINING WITH US.' "
        "(3) Below that, centered, elegant italic serif text in two "
        "lines: 'From India, with warmth.' and beneath it 'From The "
        "Theater, with a little drama.' "
        "(4) Below that, two square QR-code-style graphics placed "
        "side by side with generous space between them — each a crisp "
        "black-and-white square QR-code pattern (a generic decorative "
        "QR-code-like grid of small black modules on white, not required "
        "to be a real scannable code), each with a small tracked-out "
        "capital caption centered beneath it: the left one captioned "
        "'FOLLOW US ON INSTAGRAM', the right one captioned 'LEAVE US A "
        "GOOGLE REVIEW'. "
        "(5) Below that, a thin horizontal hairline rule spanning about "
        "half the page width, centered. "
        "(6) Below the rule, centered, small bold tracked-out capital "
        "text: 'RESERVATIONS & WHATSAPP' with the phone number '0836 320 "
        "002' directly beneath it in slightly larger serif type. "
        "(7) Below that, centered, small tracked-out capital text on one "
        "or two lines: 'PRIVATE DINING   ·   WEDDINGS & GROUP DINING   ·  "
        " GALA DINNERS   ·   DMC & TOUR GROUPS' with generous letter "
        "spacing and thin dot separators exactly as shown. "
        "(8) At the very bottom, centered, small gray serif text: '152 "
        "Đường Trần Hưng Đạo, Cửa Lấp, Phú Quốc, An Giang 92000'. "
        "No other text, no watermark logo, no page number anywhere on the "
        "page — every element listed above appears exactly once and "
        "nowhere else."
    )),
]

SPIRITS_MENU = [
    ("WHISKY", True, [
        ("Johnnie Walker Red Label", 130, 240),
        ("Johnnie Walker Black Label", 160, 290),
        ("Jameson", 140, 250),
        ("Jack Daniel's", 150, 270),
        ("Glenfiddich 12 Years", 280, 500),
    ]),
    ("GIN & TEQUILA", True, [
        ("Bombay Sapphire", 160, 290),
        ("Jose Cuervo Gold", 130, 230),
    ]),
    ("RUM", True, [
        ("Bacardi", 120, 200),
        ("Captain Morgan", 120, 200),
    ]),
    ("VODKA", True, [
        ("Smirnoff", 120, 200),
        ("Absolut", 140, 250),
        ("Grey Goose", 250, 450),
    ]),
    ("WINES", False, [
        ("Red Wine (Glass)", 150, None),
        ("White Wine (Glass)", 150, None),
    ]),
    ("BEERS", False, [
        ("Red Saigon Beer", 85, None),
        ("Green Saigon Beer", 95, None),
        ("Heineken", 100, None),
        ("Budweiser", 100, None),
        ("Pale Ale", 119, None),
        ("Good Times", 139, None),
    ]),
]


def build_spirits_prompt():
    sections = []
    for name, has_two_col, rows in SPIRITS_MENU:
        if has_two_col:
            row_strs = [f"'{n}' — {p30}K (30ml) / {p60}K (60ml)" for n, p30, p60 in rows]
        else:
            row_strs = [f"'{n}' — {p30}K" for n, p30, _ in rows]
        sections.append(f"Section '{name}': " + "; ".join(row_strs) + ".")

    return (
        STYLE_PROSE + " " + NEGATIVE_PROSE + "\n\n"
        + build_header_prose("SPIRITS, WINES & BEERS", "Premium spirits, fine wines and refreshing beers.") + "\n\n"
        + "Below the header, this page is a clean elegant two-column TEXT "
        + "PRICE LIST — no photographs, no dish images anywhere. Lay out "
        + "the following sections as bold serif category headers, each "
        + "followed by a thin dotted or hairline divider, then each item's "
        + "name left-aligned with its price(s) right-aligned on the same "
        + "line, generous line spacing, arranged in two columns across the "
        + "page width (left column: WHISKY, GIN & TEQUILA, RUM, VODKA; "
        + "right column: WINES, BEERS) so the whole list fits on one page. "
        + "For sections with two prices (30ml and 60ml), show both prices "
        + "with small 'ml' labels above the price columns as column "
        + "headers. Render every single item name and price exactly as "
        + "given, spelled correctly, no invented items. Each item is a "
        + "SINGLE line: name and price(s) only — do NOT add any second "
        + "line, subtitle, description, or extra text of any kind beneath "
        + "any item name. There is no description for any item on this "
        + "page, only the name and price.\n\n"
        + " ".join(sections) + "\n\n"
        + FOOTER_PROSE
    )


COCKTAILS_MENU = [
    ("The Maharaja", 219, "Whisky, saffron, honey and fresh citrus, finished with a subtle touch of Indian spice. Rich, smooth and regal."),
    ("Bombay Sunset", 219, "Vodka, passion fruit, orange and lime blended into a bright tropical cocktail with a refreshing citrus finish."),
    ("Jaipur Rose", 219, "Gin, rose, lychee and fresh lemon. Floral, elegant and beautifully refreshing."),
    ("Spiced Mango Margarita", 219, "Tequila, ripe mango, fresh lime and a gentle chilli kick. Sweet, tangy and perfectly balanced."),
    ("Theater Masala Mule", 219, "Vodka, ginger, lime and aromatic Indian spices topped with sparkling ginger ale. Fresh, spicy and lively."),
]

MOCKTAILS_MENU = [
    ("Mango Maharaja", 149, "Ripe mango, fresh lime and a touch of mint. Rich, tropical and refreshing."),
    ("Jaipur Rose Cooler", 149, "Rose, lychee, lemon and soda. Light, floral and beautifully refreshing."),
    ("Bombay Berry Fizz", 149, "Mixed berries, fresh lime and sparkling soda. Fruity, vibrant and refreshing."),
    ("Masala Mojito", 149, "Fresh mint, lime, Indian spices and soda. A refreshing Indian twist on a classic favourite."),
    ("Passion of India", 149, "Passion fruit, orange, lime and sparkling soda. Tropical, tangy and full of flavour."),
]


def build_drink_list_prompt(title, tagline, items_subset, page_note):
    rows = []
    for name, price, desc in items_subset:
        rows.append(f"'{name}' — {price}K. Description: {desc}")
    return (
        STYLE_PROSE + " " + NEGATIVE_PROSE + "\n\n"
        + build_header_prose(title, tagline) + "\n\n"
        + "Below the header, this page is a clean elegant single-column TEXT "
        + "LIST — no photographs, no dish images, no icons of any kind "
        + "anywhere on this page, including no vegetarian leaf icon, no "
        + "'VEGETARIAN' word, and no chili-pepper spice icons — those tags "
        + "are used elsewhere in this menu for food dishes only, never on "
        + "this drinks list page. List "
        + f"exactly {len(items_subset)} items, generously spaced down the "
        + "page. Each entry: the drink name in bold serif type with its "
        + "price right-aligned on the same line (name left-aligned, price "
        + "right-aligned, joined visually by a short thin dotted leader "
        + "line or generous spacing — never a plain hyphen), and directly "
        + "beneath it, in smaller italic gray type, its one-sentence "
        + "description exactly as given. Render every name, price and "
        + "description exactly as given, spelled correctly, no invented "
        + "items, no invented extra text. A thin hairline rule separates "
        + "each entry from the next.\n\n"
        + " ".join(rows) + "\n\n"
        + FOOTER_PROSE
    )


CATEGORY_ORDER = [
    "Small Plates & Bar Bites",
    "Chaat & Fast Sellers",
    "Tandoor & Grill",
    "Main Curries",
    "Seafood Curries",
    "Breads",
    "Rice & Khichdi",
    "Biryani",
    "Desserts",
]

DIVIDER_BEFORE = {
    "Small Plates & Bar Bites": "divider-small-plates",
    "Tandoor & Grill": "divider-tandoor",
    "Rice & Khichdi": "divider-rice",
    "Desserts": "divider-desserts",
}

# Explicit page groupings for categories where the default veg/spice
# auto-chunking doesn't match the requested layout — overrides
# veg_split_chunks entirely when a category key is present here.
MANUAL_GROUPS = {
    "Desserts": [
        ["Gulab Jamun with Vanilla Ice Cream", "Kheer", "Gajar Halwa"],
        ["Ice Cream (Vanilla)", "Ice Cream (Chocolate)"],
    ],
}

pages = []
page_num = 1

pages.append({
    "page_num": page_num, "type": "cover", "slug": "cover", "title": "cover",
    "items": [], "reference_photos": [], "prompt": None,
})
page_num += 1


LOGO_PATH = os.path.join(BASE, "references", "brand-logo-alpha.png")

HERO_REFS = {
    "back-cover": [LOGO_PATH],
}


def add_hero(key):
    global page_num
    prompt = dict(HERO_PROMPTS)[key]
    pages.append({
        "page_num": page_num, "type": "hero", "slug": key, "title": key,
        "items": [], "reference_photos": HERO_REFS.get(key, []), "prompt": prompt,
    })
    page_num += 1


first_content_page_used = False

for cat in CATEGORY_ORDER:
    if cat in DIVIDER_BEFORE:
        add_hero(DIVIDER_BEFORE[cat])

    cat_items = BY_CATEGORY[cat]
    for it in cat_items:
        it["_veg"] = is_veg(it)
        it["_spice"] = spice_level(it)
        it["_chef_rec"] = it["name"] in CHEF_RECOMMENDED

    show_tags = cat not in NO_TAGS_CATEGORIES
    if cat in MANUAL_GROUPS:
        by_name = {it["name"]: it for it in cat_items}
        page_groups = [[by_name[n] for n in names] for names in MANUAL_GROUPS[cat]]
    else:
        page_groups = veg_split_chunks(cat_items, PAGE_MAX_ITEMS)
    for i, group in enumerate(page_groups, 1):
        if not group:
            continue
        slug = f"{category_slug(cat)}-{i}"
        if slug in SPOTLIGHT_BEFORE_SLUG:
            target = SPOTLIGHT_BEFORE_SLUG[slug]
            if target == "__biryani_spotlight__":
                chicken_item = ITEMS_BY_NAME["Shahi Dum Biryani (Chicken)"]
                veg_item = ITEMS_BY_NAME["Shahi Dum Biryani (Vegetarian, Paneer)"]
                pages.append({
                    "page_num": page_num, "type": "spotlight",
                    "slug": "spotlight-shahi-dum-biryani",
                    "title": "Shahi Dum Biryani", "items": [],
                    "reference_photos": [p for p in [photo_path(chicken_item), photo_path(veg_item)] if p],
                    "prompt": build_biryani_spotlight_prompt(chicken_item, veg_item),
                })
            else:
                spot_item = ITEMS_BY_NAME[target]
                pages.append({
                    "page_num": page_num, "type": "spotlight",
                    "slug": f"spotlight-{category_slug(spot_item['name'])}",
                    "title": spot_item["name"], "items": [],
                    "reference_photos": [p for p in [photo_path(spot_item)] if p],
                    "prompt": build_spotlight_prompt(spot_item),
                })
            page_num += 1
        spice_legend = show_tags and not first_content_page_used
        first_content_page_used = first_content_page_used or spice_legend
        prompt_text, ordered_items = build_content_prompt(cat, group, show_tags, spice_legend=spice_legend)
        refs = [photo_path(it) for it in ordered_items]
        pages.append({
            "page_num": page_num,
            "type": "content",
            "slug": slug,
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

def add_drink_list(slug, title, tagline, menu):
    global page_num
    pages.append({
        "page_num": page_num, "type": "drinklist", "slug": slug,
        "title": title, "items": [], "reference_photos": [],
        "prompt": build_drink_list_prompt(title, tagline, menu, 1),
    })
    page_num += 1


def add_bar_page(slug, title, tagline, category, names):
    global page_num
    by_name = {it["name"]: it for it in BY_CATEGORY[category]}
    group = [by_name[n] for n in names]
    for it in group:
        it["_veg"] = is_veg(it)
        it["_spice"] = spice_level(it)
        it["_chef_rec"] = it["name"] in CHEF_RECOMMENDED
    show_tags = category not in NO_TAGS_CATEGORIES
    prompt_text, ordered_items = build_content_prompt(
        category, group, show_tags, title=title, tagline=tagline)
    refs = [photo_path(it) for it in ordered_items]
    pages.append({
        "page_num": page_num, "type": "content", "slug": slug, "title": title,
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


add_hero("divider-bar")

add_drink_list("signature-cocktails", "SIGNATURE COCKTAILS",
                "Original creations bringing Indian flavors to the bar.",
                COCKTAILS_MENU)
add_drink_list("signature-mocktails", "SIGNATURE MOCKTAILS",
                "All the flavor, none of the alcohol.",
                MOCKTAILS_MENU)
add_bar_page("chai-lassi", "CHAI, LASSI & CHAAS",
             "Traditional Indian drinks, freshly made.",
             "Drinks", ["Masala Tea", "Mango Lassi", "Lassi", "Masala Chaas"])
add_bar_page("smoothies", "SMOOTHIES",
             "Thick, fruity and freshly blended.",
             "Juices, Smoothies & Iced Tea",
             ["Mango Magic Smoothie", "Berry Bliss Smoothie", "Chocolate Mocha Smoothie", "Strawberry Delight Smoothie"])
add_bar_page("juices", "JUICES",
             "Fresh-squeezed, every time.",
             "Juices, Smoothies & Iced Tea",
             ["Orange Juice", "Watermelon Juice", "Pineapple Juice", "Mixed Fruit Juice"])
add_bar_page("iced-tea", "ICED TEA",
             "Chilled and refreshing.",
             "Juices, Smoothies & Iced Tea", ["Lemon Iced Tea", "Peach Iced Tea"])
add_bar_page("sparkling-water", "SOFT DRINKS & WATER",
             "Refreshing beverages to complement your meal.",
             "Drinks", ["Cold Drink", "Water / Sparkling Water"])
add_bar_page("coffee", "COFFEE",
             "Freshly brewed coffee crafted for every mood.",
             "Coffee", ["Cappuccino", "Latte", "Espresso", "Americano"])

# Spirits, Wines & Beers — text-only price list, no dish photos
pages.append({
    "page_num": page_num, "type": "spirits", "slug": "spirits-wines-beers",
    "title": "Spirits, Wines & Beers", "items": [], "reference_photos": [],
    "prompt": build_spirits_prompt(),
})
page_num += 1

add_hero("back-cover")

with open(os.path.join(BASE, "menu_pages.json"), "w") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

n_content = sum(1 for p in pages if p["type"] == "content")
n_hero = sum(1 for p in pages if p["type"] == "hero")
n_cover = sum(1 for p in pages if p["type"] == "cover")
n_spirits = sum(1 for p in pages if p["type"] == "spirits")
print(f"Wrote {len(pages)} pages ({n_content} content, {n_hero} hero, {n_cover} cover, {n_spirits} spirits) to menu_pages.json")

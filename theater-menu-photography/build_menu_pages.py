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
    "same dish."
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


def build_content_prompt(category, page_items, show_tags):
    for it in page_items:
        it["_show_tags"] = show_tags

    title = category.upper()
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
        + build_header_prose(title, TAGLINES.get(category, "")) + "\n\n"
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
    ("closing", (
        "Design a full-bleed A4 portrait restaurant menu CLOSING page, "
        "clean warm white/cream paper background (hex F6F3EC), flat and "
        "front-on like a scanned printed page, not a mockup, no page "
        "shadow, no arrows, no watermark, no photograph of any kind on "
        "this page. In the exact center of the page, a large ornate round "
        "mandala flourish medallion made of fine thin warm-brown line-art "
        "petals radiating outward, with a scalloped oval badge shape cut "
        "into the very center of the medallion containing large bold "
        "premium serif text reading exactly 'DHANYAWAD'. Directly beneath "
        "that, inside or just below the badge, small tracked-out capital "
        "text reading exactly 'THANK YOU FOR DINING WITH US.' Below the "
        "medallion, small elegant centered serif text in two lines: '152 "
        "Đường Trần Hưng Đạo, Cửa Lấp, Phú Quốc, An Giang 92000' on the "
        "first line and 'Phone: 0836 320 002' on the second line. Near "
        "the very bottom of the page, a small fine black-ink line-art "
        "architectural sketch of an ornate Indian temple archway/gateway, "
        "centered. Each text element appears EXACTLY ONCE — no repeats. "
        "No other text or imagery anywhere on the page."
    )),
    ("back-cover", (
        "Design a full-bleed A4 portrait page, clean warm white/cream "
        "paper background (hex F6F3EC), flat and front-on like a scanned "
        "printed page, not a mockup, no page shadow. This page has NO "
        "logo, NO restaurant name, NO price text, NO menu text of any "
        "kind whatsoever — it is a purely decorative illustration and "
        "spice flat-lay collage page. Scattered artfully across the page: "
        "a generous pile of vivid orange-yellow turmeric powder in the "
        "upper-left corner; a couple of cinnamon sticks and a small "
        "ceramic bowl of whole white peppercorns in the lower-left "
        "corner; a cluster of star anise pods and a few whole cloves near "
        "the bottom center; a sprig of fresh curry leaves on the left "
        "side. In the upper-left-center area, a small fine black-ink "
        "line-art architectural sketch of an ornate South Indian temple. "
        "In the lower-right area, a larger, more detailed fine black-ink "
        "line-art sketch of the Taj Mahal complete with its reflecting "
        "pool and rows of cypress trees. In the exact center of the page, "
        "a fine, thin, light warm-brown line-art outline map of the "
        "country of India (just the outer border outline, no cities or "
        "state lines labeled, subtle and faint). No text, no logo, no "
        "watermark, no page number anywhere on the page."
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
    "Coffee",
    "Juices, Smoothies & Iced Tea",
    "Drinks",
]

DIVIDER_BEFORE = {
    "Small Plates & Bar Bites": "divider-small-plates",
    "Tandoor & Grill": "divider-tandoor",
    "Rice & Khichdi": "divider-rice",
    "Desserts": "divider-desserts",
    "Coffee": "divider-bar",
}

# Explicit page groupings for categories where the default veg/spice
# auto-chunking doesn't match the requested layout — overrides
# veg_split_chunks entirely when a category key is present here.
MANUAL_GROUPS = {
    "Desserts": [
        ["Gulab Jamun with Vanilla Ice Cream", "Kheer", "Gajar Halwa"],
        ["Ice Cream (Vanilla)", "Ice Cream (Chocolate)"],
    ],
    "Juices, Smoothies & Iced Tea": [
        ["Orange Juice", "Watermelon Juice", "Pineapple Juice", "Mixed Fruit Juice"],
        ["Lemon Iced Tea", "Peach Iced Tea"],
        ["Mango Magic Smoothie", "Berry Bliss Smoothie", "Chocolate Mocha Smoothie", "Strawberry Delight Smoothie"],
    ],
    "Drinks": [
        ["Masala Tea", "Mango Lassi", "Lassi", "Masala Chaas"],
        ["Cold Drink", "Water / Sparkling Water"],
    ],
}

pages = []
page_num = 1

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

    show_tags = cat not in NO_TAGS_CATEGORIES
    if cat in MANUAL_GROUPS:
        by_name = {it["name"]: it for it in cat_items}
        page_groups = [[by_name[n] for n in names] for names in MANUAL_GROUPS[cat]]
    else:
        page_groups = veg_split_chunks(cat_items, PAGE_MAX_ITEMS)
    for i, group in enumerate(page_groups, 1):
        if not group:
            continue
        prompt_text, ordered_items = build_content_prompt(cat, group, show_tags)
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

# Spirits, Wines & Beers — text-only price list, no dish photos
pages.append({
    "page_num": page_num, "type": "spirits", "slug": "spirits-wines-beers",
    "title": "Spirits, Wines & Beers", "items": [], "reference_photos": [],
    "prompt": build_spirits_prompt(),
})
page_num += 1

add_hero("closing")
add_hero("back-cover")

with open(os.path.join(BASE, "menu_pages.json"), "w") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

n_content = sum(1 for p in pages if p["type"] == "content")
n_hero = sum(1 for p in pages if p["type"] == "hero")
n_cover = sum(1 for p in pages if p["type"] == "cover")
n_spirits = sum(1 for p in pages if p["type"] == "spirits")
print(f"Wrote {len(pages)} pages ({n_content} content, {n_hero} hero, {n_cover} cover, {n_spirits} spirits) to menu_pages.json")

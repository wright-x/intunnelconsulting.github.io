#!/usr/bin/env python3
"""Builds items.json for the Indian Kitchen menu photo shoot (new project,
separate from The Theater). White studio background for all dish photos so
they can be cleanly cut out and composited onto the burgundy/gold page
layouts later."""
import json
import re

STYLE_SUFFIX = (
    "Bright, premium, LIGHT and WHITE studio background: clean white "
    "seamless backdrop, soft even studio lighting, minimal soft shadow, "
    "high-end editorial food photography look, elevated three-quarter "
    "angle looking down at the plate. Shallow depth of field, tack-sharp "
    "focus on the food. No text, no logos, no hands, no cutlery unless "
    "specified, no watermarks, no candles, no glassware, no restaurant "
    "background of any kind — pure white studio only. Photorealistic, "
    "professional restaurant menu photography, ultra-detailed, 2K quality."
)

PLATEWARE = {
    "speckled_pale_bowl": (
        "Presented on a wide, shallow, matte artisanal stoneware bowl "
        "with a pale oat/cream speckled glaze and a slightly darker "
        "raw-clay rim, exactly the kind of handmade ceramic bowl used "
        "for elevated modern restaurant salads and roasted vegetables."
    ),
    "speckled_charcoal_plate": (
        "Presented on a dark charcoal/deep-green speckled matte stoneware "
        "plate with a glossy dark glazed rim, the kind of moody artisanal "
        "plate used for fried starters and shareable bites."
    ),
    "speckled_tan_bowl": (
        "Presented on a wide, shallow tan/khaki speckled matte stoneware "
        "bowl with a raw-clay rim, the kind of earthy handmade bowl used "
        "for chaat and street-food style dishes."
    ),
    "clay_biryani_pot": (
        "Served in a traditional dark clay handi pot with a thick "
        "dough-sealed rim, the lid propped open beside it."
    ),
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, plateware_key, subject):
    plateware = PLATEWARE[plateware_key]
    prompt = f"A premium editorial food photograph of {name}: {subject} {plateware} {STYLE_SUFFIX}"
    return {"name": name, "slug": slug(name), "plateware": plateware_key, "prompt": prompt}


items = [
    item(
        "Charred Sweet Potato & Chickpea Salad",
        "speckled_pale_bowl",
        "Thick roasted sweet potato wedges with deeply charred edges, tossed with crispy roasted chickpeas, "
        "dolloped with swirls of thick yogurt, drizzled with a glossy dark tamarind-date glaze, scattered with "
        "fresh micro herbs and a few edible purple flowers for color.",
    ),
    item(
        "Spiced Lamb Keema Samosas",
        "speckled_charcoal_plate",
        "Two large golden-fried triangular samosas with a crisp blistered shell, one cut open to reveal a "
        "rich spiced minced lamb filling studded with peas, served with a small copper bowl of vivid green "
        "mint-coriander chutney and a few micro herb leaves scattered on the plate.",
    ),
    item(
        "Aloo Tikki Chaat",
        "speckled_tan_bowl",
        "Four golden-crusted potato tikki patties nestled in a bed of spiced chickpea curry, generously "
        "drizzled with thick yogurt, tangy tamarind chutney and vivid green mint chutney, topped with fine "
        "crispy sev and finely diced red onion.",
    ),
    item(
        "Charred Broccoli, Almond & Herb Cream",
        "speckled_pale_bowl",
        "Deeply charred broccoli florets with blistered edges mounded over a smooth pale herb cream, "
        "scattered with toasted sliced almonds and a few fresh micro herb leaves.",
    ),
    item(
        "Whole Roasted Cauliflower, Cashew Curry",
        "speckled_pale_bowl",
        "One whole roasted cauliflower head with a deeply charred golden-brown spiced crust, sitting in a "
        "pool of rich creamy cashew curry sauce, scattered with whole roasted cashews and fresh coriander.",
    ),
]

if __name__ == "__main__":
    with open("items.json", "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to items.json")

#!/usr/bin/env python3
"""Builds items.json for the Indian Kitchen menu photo shoot (new project,
separate from The Theater). White studio background for all dish photos so
they can be cleanly cut out and composited onto the burgundy/gold page
layouts later. Plating aims for the level of craft seen at top modern
Indian restaurants (Semma, Bungalow, Dhamaka) — multi-vessel compositions,
not a single pile of food in one bowl."""
import json
import re

STYLE_SUFFIX = (
    "Ultra-premium, fine-dining editorial food photography in the style "
    "of top modern Indian restaurants like Semma, Bungalow and Dhamaka — "
    "thoughtfully composed, multi-component plating with genuine "
    "restaurant craft, never a single generic pile of food in one bowl. "
    "Bright, clean white studio background: seamless white backdrop, "
    "soft directional studio lighting from one side, soft natural "
    "shadow, elevated three-quarter angle looking down at the full "
    "composition. Intentional asymmetry in the arrangement, a mix of "
    "serving vessels where appropriate (small ceramic cups, "
    "compartmented dip trays, a banana leaf accent), a few deliberate, "
    "well-placed garnishes (fresh microgreens, one or two edible "
    "flowers, toasted nuts) that read as chef styling, not scattered "
    "decoration. Sauces and chutneys look vivid and freshly made. "
    "Photorealistic, shot on a full-frame camera, ultra-detailed, "
    "natural food texture, 2K quality. No text, no logos, no hands, no "
    "watermark, no restaurant background of any kind — pure white "
    "studio only."
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
        "dolloped with swirls of thick yogurt and a glossy dark tamarind-date glaze, finished with a scatter "
        "of toasted cashews and bright pomegranate arils for pops of color, a small copper cup of extra "
        "tamarind-date chutney set beside the bowl, a few fresh micro herbs and one or two edible flowers, "
        "plated with confident intentional asymmetry rather than centered.",
    ),
    item(
        "Spiced Lamb Keema Samosas",
        "speckled_charcoal_plate",
        "Two large golden-fried triangular samosas with a crisp blistered shell, one cut open to reveal a "
        "rich spiced minced lamb filling studded with peas, served alongside a small three-compartment "
        "ceramic dip tray holding tamarind chutney, mint-coriander chutney and quick-pickled red onion, "
        "garnished with a few coriander microgreens and one edible flower.",
    ),
    item(
        "Aloo Tikki Chaat",
        "speckled_tan_bowl",
        "Four golden-crusted potato tikki patties nestled in a bed of spiced chickpea curry, generously "
        "drizzled with thick yogurt, tangy tamarind chutney and vivid green mint chutney, topped with fine "
        "crispy sev, finely diced red onion and a scatter of pomegranate arils, a small copper cup of extra "
        "tamarind chutney set beside the bowl, finished with coriander microgreens and one edible flower.",
    ),
    item(
        "Charred Broccoli, Almond & Herb Cream",
        "speckled_pale_bowl",
        "Deeply charred broccoli florets with blistered edges mounded over a smooth pale herb cream, "
        "scattered with toasted sliced almonds and cashews, a small side cup of sizzling curry-leaf and "
        "mustard-seed tempering oil to drizzle, finished with a few fresh micro herb leaves and one edible "
        "flower.",
    ),
    item(
        "Whole Roasted Cauliflower, Cashew Curry",
        "speckled_pale_bowl",
        "One whole roasted cauliflower head with a deeply charred golden-brown spiced crust, sitting in a "
        "pool of rich creamy cashew curry sauce, topped with crisp-fried curry leaves and whole roasted "
        "cashews, a lime wedge and a small copper cup of extra curry sauce set beside the bowl, finished "
        "with fresh coriander and one edible flower.",
    ),
    item(
        "Pani Puri Flight",
        "speckled_charcoal_plate",
        "Six crisp round puri shells, each with a small opening on top filled with spiced potato, chickpea "
        "and a sprig of micro herb, arranged on a fresh banana leaf accent, beside them three small ceramic "
        "cups each holding a different colored pani — vivid green mint-jaljeera, deep reddish-brown tamarind, "
        "and pale yellow-green raw mango-coriander — each dotted with a few boondi and a floating mint leaf, "
        "plus a small three-compartment ceramic tray holding tamarind chutney, mint chutney and finely diced "
        "onion, finished with a scatter of coriander microgreens and two edible flowers (yellow and purple).",
    ),
]

if __name__ == "__main__":
    with open("items.json", "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to items.json")

#!/usr/bin/env python3
"""Builds items.json for the Indian Kitchen menu photo shoot. White studio
background for all dish photos so they can be cleanly cut out and
composited onto the burgundy/gold page layouts later. Plating is inspired
by top modern Indian restaurants (Semma, Bungalow, Dhamaka) but stays on
ONE plate — no side cups/trays except where a dish genuinely requires
separate vessels (pani puri's waters)."""
import json
import re

STYLE_SUFFIX = (
    "Ultra-premium, fine-dining editorial food photography in the style "
    "of top modern Indian restaurants like Semma, Bungalow and Dhamaka — "
    "thoughtful, confident plating, everything composed on the ONE plate "
    "(no side cups, no extra dishes, no props scattered around it) with "
    "intentional asymmetry, sauce swooshed or pooled with a spoon, height "
    "and texture contrast, a few deliberate garnishes (fresh herbs, one "
    "or two edible flowers, toasted nuts) placed like a chef would place "
    "them, never scattered randomly. Bright, clean white studio "
    "background: seamless white backdrop, soft directional studio "
    "lighting from one side, soft natural shadow, elevated three-quarter "
    "angle looking down at the plate. Photorealistic, shot on a "
    "full-frame camera, ultra-detailed, natural food texture, 2K "
    "quality. No text, no logos, no hands, no watermark, no restaurant "
    "background of any kind — pure white studio only."
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
        "dough-sealed rim, the lid propped open beside it, resting on a "
        "dark wooden board."
    ),
    "earthy_curry_plate": (
        "Presented on a wide, shallow, matte speckled stoneware plate in "
        "a warm earthy tan glaze, the kind of rustic handmade plate used "
        "for whole-piece fish and curry preparations."
    ),
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, price, plateware_key, subject):
    plateware = PLATEWARE[plateware_key]
    prompt = f"A premium editorial food photograph of {name}: {subject} {plateware} {STYLE_SUFFIX}"
    return {"name": name, "price_k": price, "slug": slug(name), "plateware": plateware_key, "prompt": prompt}


items = [
    item(
        "Charred Sweet Potato & Chickpea Salad", 155, "speckled_pale_bowl",
        "Thick roasted sweet potato wedges with deeply charred edges, tossed with crispy roasted chickpeas, "
        "toasted cashews and bright pomegranate arils, swooshed thick yogurt across the base of the bowl "
        "with a spoon, a dark glossy tamarind-date glaze drizzled over the top, finished with a few fresh "
        "mint and coriander leaves and one edible flower, plated with confident intentional asymmetry.",
    ),
    item(
        "Spiced Lamb Keema Samosas", 165, "speckled_charcoal_plate",
        "Two large golden-fried triangular samosas with a crisp blistered shell, one cut open to reveal a "
        "rich spiced minced lamb filling studded with peas, resting over a swooshed pool of vivid green "
        "mint-coriander chutney and a small drizzle of tamarind chutney directly on the same plate, finished "
        "with a few coriander microgreens and one edible flower — everything on the one plate, no side bowls.",
    ),
    item(
        "Aloo Tikki Chaat", 145, "speckled_tan_bowl",
        "Exactly TWO large golden-crusted potato tikki patties set over a bed of spiced chickpea curry, "
        "drizzled with thick yogurt, tangy tamarind chutney and vivid green mint chutney, topped with fine "
        "crispy sev, finely diced red onion and a scatter of pomegranate arils, finished with coriander "
        "microgreens and one edible flower, all within the one bowl.",
    ),
    item(
        "Charred Broccoli, Almond & Herb Cream", 135, "speckled_pale_bowl",
        "Deeply charred broccoli florets with blistered edges mounded over a smooth pale herb cream "
        "swooshed across the plate, scattered with toasted sliced almonds and cashews, a light drizzle of "
        "sizzling curry-leaf and mustard-seed tempering oil directly over the top, finished with a few fresh "
        "micro herb leaves and one edible flower.",
    ),
    item(
        "Whole Roasted Cauliflower, Cashew Curry", 175, "speckled_pale_bowl",
        "One whole roasted cauliflower head with a deeply charred golden-brown spiced crust, sitting in a "
        "pool of rich creamy cashew curry sauce on the same plate, topped with crisp-fried curry leaves, "
        "whole roasted cashews and a wedge of lime tucked beside it, finished with fresh coriander and one "
        "edible flower.",
    ),
    item(
        "Pani Puri Flight", 175, "speckled_charcoal_plate",
        "Six crisp round puri shells, each with a small opening on top filled with spiced potato, chickpea "
        "and a sprig of micro herb, arranged in a tight cluster on the plate beside three small ceramic cups "
        "(the only vessels this dish needs, since three separate waters cannot be poured together) each "
        "holding a different colored pani — vivid green mint-jaljeera, deep reddish-brown tamarind, and pale "
        "yellow-green raw mango-coriander — each dotted with a few boondi and a floating mint leaf, with a "
        "small quenelle of tamarind chutney, mint chutney and a scatter of finely diced onion placed directly "
        "on the same plate rather than in a separate tray, finished with coriander microgreens and two "
        "edible flowers.",
    ),
    item(
        "Malabar Fish Curry, Banana Leaf", 265, "earthy_curry_plate",
        "One thick, skin-on white fish fillet generously coated in a rich reddish-brown coconut-based "
        "Malabar spice paste with visible curry leaves pressed into the crust, nestled in a bed of the same "
        "glossy curry sauce, plated directly on a single fresh banana leaf that lines the plate, finished "
        "with a scatter of fried curry leaves and one edible flower, gentle wisps of steam rising.",
    ),
    item(
        "Hyderabadi Chicken Dum Biryani", 245, "clay_biryani_pot",
        "Fragrant saffron and turmeric basmati rice generously layered with tender bone-in chicken pieces, "
        "topped with golden fried onions, fresh mint and coriander leaves, whole star anise and green "
        "cardamom pods visible on top, gentle wisps of steam rising, the dough-sealed clay lid propped open "
        "beside the pot to reveal the biryani inside.",
    ),
]

if __name__ == "__main__":
    with open("items.json", "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to items.json")

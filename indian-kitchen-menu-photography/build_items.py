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

DRINK_STYLE_SUFFIX = (
    "Ultra-premium, fine-dining editorial beverage photography in the "
    "style of a top modern Indian restaurant bar program — the glass "
    "styled thoughtfully with a well-placed garnish, never cluttered. "
    "Bright, clean white studio background: seamless white backdrop, "
    "soft directional studio lighting from one side, soft natural "
    "shadow, straight-on eye-level angle. Photorealistic, shot on a "
    "full-frame camera, ultra-detailed, natural condensation and ice "
    "clarity where relevant, 2K quality. No text, no logos, no hands, "
    "no watermark, no restaurant background of any kind — pure white "
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
        "dough-sealed rim, the lid propped open beside it, resting on a "
        "dark wooden board."
    ),
    "earthy_curry_plate": (
        "Presented on a wide, shallow, matte speckled stoneware plate in "
        "a warm earthy tan glaze, the kind of rustic handmade plate used "
        "for whole-piece fish and curry preparations."
    ),
    "charcoal_tandoor_board": (
        "Presented on a dark charcoal speckled matte stoneware plate "
        "resting on a dark wooden board, the kind of rustic plate used "
        "for tandoor-grilled dishes."
    ),
    "curry_karahi_bowl": (
        "Served in a small hammered copper karahi bowl with polished "
        "brass ring handles, resting on a round dark wooden coaster."
    ),
    "copper_rice_bowl": (
        "Served in a hammered copper bowl, resting on a round dark "
        "wooden coaster."
    ),
    "dessert_slate": (
        "Presented on a dark slate-grey matte stoneware plate, the kind "
        "of moody plate used for a modern plated dessert."
    ),
    "rocks_glass": "Served in a heavy cut-crystal rocks glass over one large clear ice cube.",
    "coupe_glass": "Served in an elegant crystal coupe glass.",
    "martini_glass": "Served in a classic crystal martini glass.",
    "tall_glass": "Served in a tall clear glass over ice.",
    "chai_cup": "Served in a small speckled ceramic cup and saucer.",
    "lassi_glass": "Served in a tall clear glass, no ice.",
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, price, plateware_key, subject, category, veg=True, spice=0, badge=None, drink=False):
    plateware = PLATEWARE[plateware_key]
    style = DRINK_STYLE_SUFFIX if drink else STYLE_SUFFIX
    prompt = f"A premium editorial {'beverage' if drink else 'food'} photograph of {name}: {subject} {plateware} {style}"
    return {
        "name": name, "price_k": price, "slug": slug(name), "plateware": plateware_key,
        "category": category, "veg": veg, "spice": spice, "badge": badge, "prompt": prompt,
    }


items = [
    # ---------------- BEGINNINGS ----------------
    item(
        "Pani Puri Flight", 175, "speckled_charcoal_plate",
        "Six crisp round puri shells, each with a small opening on top filled with spiced potato, chickpea "
        "and a sprig of micro herb, arranged in a tight cluster on the plate beside three small ceramic cups "
        "(the only vessels this dish needs, since three separate waters cannot be poured together) each "
        "holding a different colored pani — vivid green mint-jaljeera, deep reddish-brown tamarind, and pale "
        "yellow-green raw mango-coriander — each dotted with a few boondi and a floating mint leaf, with a "
        "small quenelle of tamarind chutney, mint chutney and a scatter of finely diced onion placed directly "
        "on the same plate rather than in a separate tray, finished with coriander microgreens and two "
        "edible flowers.", "BEGINNINGS", True, 1, "RECOMMENDED",
    ),
    item(
        "Spiced Lamb Keema Samosas", 165, "speckled_charcoal_plate",
        "Two large golden-fried triangular samosas with a crisp blistered shell, one cut open to reveal a "
        "rich spiced minced lamb filling studded with peas, resting over a swooshed pool of vivid green "
        "mint-coriander chutney and a small drizzle of tamarind chutney directly on the same plate, finished "
        "with a few coriander microgreens and one edible flower — everything on the one plate, no side bowls.",
        "BEGINNINGS", False, 2,
    ),
    item(
        "Aloo Tikki Chaat", 145, "speckled_tan_bowl",
        "Exactly TWO large golden-crusted potato tikki patties set over a bed of spiced chickpea curry, "
        "drizzled with thick yogurt, tangy tamarind chutney and vivid green mint chutney, topped with fine "
        "crispy sev, finely diced red onion and a scatter of pomegranate arils, finished with coriander "
        "microgreens and one edible flower, all within the one bowl.", "BEGINNINGS", True, 1,
    ),
    item(
        "Crispy Okra Fries, Chaat Masala", 125, "speckled_charcoal_plate",
        "A tall mound of thin, crisp-fried okra strips dusted with vivid red chaat masala, resting on a "
        "smear of cooling mint yogurt, finished with fresh coriander and a lime wedge tucked beside it.",
        "BEGINNINGS", True, 2,
    ),
    item(
        "Corn Bhel, Puffed Rice & Peanut", 115, "speckled_tan_bowl",
        "A generous mound of puffed rice tossed with sweet corn, roasted peanuts, diced onion and tomato, "
        "tamarind and mint chutney, finished with crispy sev, fresh coriander and one edible flower.",
        "BEGINNINGS", True, 1,
    ),
    item(
        "Papadum Trio, Three Chutneys", 105, "speckled_charcoal_plate",
        "Three large crisp roasted lentil papadums leaning against each other, with three small quenelles "
        "along the front of the plate — glossy amber mango pickle, bright red chilli-garlic chutney, pale "
        "green mint yogurt — finished with fresh coriander.", "BEGINNINGS", True, 0,
    ),
    # ---------------- VEGETABLE GARDEN ----------------
    item(
        "Charred Sweet Potato & Chickpea Salad", 155, "speckled_pale_bowl",
        "Thick roasted sweet potato wedges with deeply charred edges, tossed with crispy roasted chickpeas, "
        "toasted cashews and bright pomegranate arils, swooshed thick yogurt across the base of the bowl "
        "with a spoon, a dark glossy tamarind-date glaze drizzled over the top, finished with a few fresh "
        "mint and coriander leaves and one edible flower, plated with confident intentional asymmetry.",
        "VEGETABLE GARDEN", True, 1,
    ),
    item(
        "Charred Broccoli, Almond & Herb Cream", 135, "speckled_pale_bowl",
        "Deeply charred broccoli florets with blistered edges mounded over a smooth pale herb cream "
        "swooshed across the plate, scattered with toasted sliced almonds and cashews, a light drizzle of "
        "sizzling curry-leaf and mustard-seed tempering oil directly over the top, finished with a few fresh "
        "micro herb leaves and one edible flower.", "VEGETABLE GARDEN", True, 0,
    ),
    item(
        "Whole Roasted Cauliflower, Cashew Curry", 175, "speckled_pale_bowl",
        "One whole roasted cauliflower head with a deeply charred golden-brown spiced crust, sitting in a "
        "pool of rich creamy cashew curry sauce on the same plate, topped with crisp-fried curry leaves, "
        "whole roasted cashews and a wedge of lime tucked beside it, finished with fresh coriander and one "
        "edible flower.", "VEGETABLE GARDEN", True, 2,
    ),
    item(
        "Charred Baby Eggplant, Peanut Curry", 165, "speckled_pale_bowl",
        "Two halved baby eggplants with deeply charred skin, nestled in a rich reddish-brown peanut curry "
        "sauce, topped with crushed roasted peanuts, fresh coriander and one edible flower.",
        "VEGETABLE GARDEN", True, 2,
    ),
    item(
        "Tandoori Mushroom, Garlic Yogurt", 175, "speckled_pale_bowl",
        "Whole charcoal-grilled king oyster mushrooms with a deep red tandoori marinade and visible char, "
        "fanned over a smear of roasted garlic yogurt, finished with fresh coriander, toasted sesame and one "
        "edible flower.", "VEGETABLE GARDEN", True, 1,
    ),
    item(
        "Beetroot Tikki, Goat Cheese", 155, "speckled_pale_bowl",
        "Two golden-crusted beetroot and potato tikki patties with a vivid magenta interior just visible at "
        "the cut edge, resting on a quenelle of soft goat cheese, finished with micro herbs, toasted walnuts "
        "and one edible flower.", "VEGETABLE GARDEN", True, 1,
    ),
    # ---------------- FROM THE TANDOOR ----------------
    item(
        "Charcoal Paneer Tikka", 185, "charcoal_tandoor_board",
        "Skewered cubes of charcoal-grilled paneer with deeply charred edges and a vivid orange-red marinade, "
        "off the skewer and fanned across the plate, resting on a smear of pale mint-yogurt sauce, finished "
        "with a scatter of pomegranate arils, fresh coriander and one edible flower, a lime wedge tucked "
        "beside it.", "TANDOOR", True, 2,
    ),
    item(
        "Tandoori Chicken Thigh, Kashmiri Chilli", 225, "charcoal_tandoor_board",
        "One large boneless charcoal-grilled chicken thigh with a deep red Kashmiri chilli marinade and "
        "visible char, sliced and fanned open, resting on a smear of pale yogurt sauce, finished with fresh "
        "coriander, a scatter of fried curry leaves and one edible flower, a lime wedge tucked beside it.",
        "TANDOOR", False, 3,
    ),
    item(
        "Lamb Seekh Kebab, Pickled Onion", 245, "charcoal_tandoor_board",
        "Two long charcoal-grilled minced lamb seekh kebabs with a deeply charred crust, sliced on the "
        "diagonal, resting on a smear of vivid green mint chutney with a small scatter of quick-pickled red "
        "onion directly on the plate, finished with fresh coriander and one edible flower.",
        "TANDOOR", False, 2,
    ),
    item(
        "Tandoori Prawns, Chilli-Garlic", 285, "charcoal_tandoor_board",
        "Skewered jumbo prawns off the skewer, charcoal-grilled with a vivid red chilli-garlic marinade and "
        "visible char, fanned across a smear of pale garlic yogurt, finished with fresh coriander, a scatter "
        "of chilli flakes and a lime wedge.", "TANDOOR", False, 2, "RECOMMENDED",
    ),
    item(
        "Malai Chicken Tikka, Cashew Cream", 235, "charcoal_tandoor_board",
        "Skewered boneless chicken pieces off the skewer, charcoal-grilled with a pale creamy malai marinade "
        "and light char, fanned over a smear of cashew cream, finished with fresh coriander, toasted cashews "
        "and one edible flower.", "TANDOOR", False, 1,
    ),
    item(
        "Charcoal Lamb Chops, Mint", 325, "charcoal_tandoor_board",
        "Three charcoal-grilled French-trimmed lamb chops with a deep char and visible bone, fanned across "
        "a smear of vivid green mint chutney, finished with flaky salt, fresh coriander and one edible "
        "flower.", "TANDOOR", False, 2, "CHEF'S SPECIAL",
    ),
    # ---------------- CURRIES & MAINS ----------------
    item(
        "Charcoal Butter Chicken", 265, "curry_karahi_bowl",
        "Tender charcoal-grilled chicken pieces in a smooth, rich tomato-butter gravy with a swirl of cream "
        "and a small pat of butter melting on top, finished with fresh coriander and a light scatter of "
        "toasted cashews, gentle wisps of steam rising.", "CURRIES & MAINS", False, 1, "CHEF'S SPECIAL",
    ),
    item(
        "Malabar Fish Curry, Banana Leaf", 265, "earthy_curry_plate",
        "One thick, skin-on white fish fillet generously coated in a rich reddish-brown coconut-based "
        "Malabar spice paste with visible curry leaves pressed into the crust, nestled in a bed of the same "
        "glossy curry sauce, plated directly on a single fresh banana leaf that lines the plate, finished "
        "with a scatter of fried curry leaves and one edible flower, gentle wisps of steam rising.",
        "CURRIES & MAINS", False, 2, "CHEF'S SPECIAL",
    ),
    item(
        "Lamb Rogan Josh, Kashmiri Chilli", 285, "curry_karahi_bowl",
        "Tender braised lamb pieces in a deep reddish-brown Kashmiri chilli gravy, glossy and rich, finished "
        "with fresh coriander and a light drizzle of cream, gentle wisps of steam rising.",
        "CURRIES & MAINS", False, 3,
    ),
    item(
        "Goan Prawn Curry, Coconut", 285, "curry_karahi_bowl",
        "Plump prawns in a golden-yellow coconut curry sauce flecked with fresh curry leaves and mustard "
        "seed, finished with fresh coriander, gentle wisps of steam rising.", "CURRIES & MAINS", False, 2,
    ),
    item(
        "Dal Makhani, Smoked Butter", 145, "curry_karahi_bowl",
        "Deep brown creamy black lentils slow-cooked until velvety, finished with a swirl of cream and a "
        "small pat of smoked butter melting on top, finished with fresh coriander, gentle wisps of steam "
        "rising.", "CURRIES & MAINS", True, 1,
    ),
    item(
        "Palak Paneer, Charred Spinach", 175, "curry_karahi_bowl",
        "Soft paneer cubes set in a smooth vivid green charred-spinach gravy, finished with a swirl of "
        "cream, a few toasted pine nuts and one edible flower.", "CURRIES & MAINS", True, 1,
    ),
    # ---------------- RICE & BIRYANI ----------------
    item(
        "Hyderabadi Chicken Dum Biryani", 245, "clay_biryani_pot",
        "Fragrant saffron and turmeric basmati rice generously layered with tender bone-in chicken pieces, "
        "topped with golden fried onions, fresh mint and coriander leaves, whole star anise and green "
        "cardamom pods visible on top, gentle wisps of steam rising, the dough-sealed clay lid propped open "
        "beside the pot to reveal the biryani inside.", "RICE & BIRYANI", False, 2,
    ),
    item(
        "Vegetable Dum Biryani, Saffron", 195, "clay_biryani_pot",
        "Fragrant saffron and turmeric basmati rice generously layered with charred mixed vegetables and "
        "paneer, topped with golden fried onions, fresh mint and coriander leaves, whole star anise visible "
        "on top, gentle wisps of steam rising, the dough-sealed clay lid propped open beside the pot.",
        "RICE & BIRYANI", True, 1,
    ),
    item(
        "Jeera Rice, Toasted Cumin", 95, "copper_rice_bowl",
        "Fluffy long-grain basmati rice tempered with visible toasted cumin seeds and a dried red chilli, "
        "mounded gently, finished with a single fresh coriander leaf.", "RICE & BIRYANI", True, 0,
    ),
    item(
        "Lamb Biryani, Dum-Sealed", 285, "clay_biryani_pot",
        "Fragrant saffron basmati rice generously layered with tender braised lamb pieces, topped with "
        "golden fried onions, fresh mint and whole spices, gentle wisps of steam rising, the dough-sealed "
        "clay lid propped open beside the pot.", "RICE & BIRYANI", False, 2, "CHEF'S SPECIAL",
    ),
    item(
        "Prawn Biryani, Coastal Spice", 265, "clay_biryani_pot",
        "Fragrant saffron basmati rice generously layered with plump coastal-spiced prawns, topped with "
        "golden fried onions, fresh mint and curry leaves, gentle wisps of steam rising, the dough-sealed "
        "clay lid propped open beside the pot.", "RICE & BIRYANI", False, 2,
    ),
    item(
        "Curd Rice, Pomegranate & Curry Leaf", 125, "copper_rice_bowl",
        "Smooth, creamy curd rice tempered with mustard seed and crisp curry leaves, topped with a scatter "
        "of bright pomegranate arils, finished with a single fresh coriander leaf.", "RICE & BIRYANI", True, 0,
    ),
    # ---------------- SWEET ENDINGS ----------------
    item(
        "Deconstructed Gulab Jamun, Saffron Cream", 135, "dessert_slate",
        "Two warm glossy gulab jamun dumplings soaked in saffron syrup, set beside a quenelle of chilled "
        "saffron cream, finished with a scatter of chopped pistachios, a few saffron strands and one edible "
        "flower.", "SWEET ENDINGS", True, 0, "RECOMMENDED",
    ),
    item(
        "Pistachio Kulfi, Rose, Vermicelli", 125, "dessert_slate",
        "One elegant cone of dense pistachio kulfi standing upright, finished with crushed pistachios, a "
        "scatter of crisp golden vermicelli, a few dried rose petals and one edible flower.",
        "SWEET ENDINGS", True, 0,
    ),
    item(
        "Chai-Spiced Crème Brûlée", 145, "dessert_slate",
        "One chai-spiced crème brûlée in a shallow dish with a glossy, cracked caramelized sugar top, "
        "finished with a light dusting of cinnamon, a small sprig of mint and one edible flower.",
        "SWEET ENDINGS", True, 0,
    ),
    item(
        "Mango Cheesecake, Cardamom", 155, "dessert_slate",
        "One neat wedge of pale golden mango cheesecake with a visible biscuit base, topped with a smooth "
        "mango glaze, a light dusting of ground cardamom and one edible flower.", "SWEET ENDINGS", True, 0,
    ),
    item(
        "Chocolate Samosa, Salted Caramel", 145, "dessert_slate",
        "Two small golden-fried triangular samosas with a crisp shell, one cut open to reveal a molten dark "
        "chocolate filling, resting beside a swooshed pool of glossy salted caramel sauce, finished with a "
        "light dusting of powdered sugar.", "SWEET ENDINGS", True, 0,
    ),
    item(
        "Saffron Rice Pudding, Pistachio", 125, "dessert_slate",
        "A smooth, creamy pale saffron-hued rice pudding, topped with slivered pistachios, almonds and a "
        "few saffron strands, finished with one edible flower.", "SWEET ENDINGS", True, 0,
    ),
    # ---------------- DRINKS ----------------
    item(
        "Smoked Old Fashioned, Chai Bitters", 245, "rocks_glass",
        "A deep amber whisky cocktail over one large clear ice cube, a light wisp of smoke still lingering "
        "in the glass, garnished with an orange peel twist and a star anise pod.", "DRINKS", True, 0,
        "RECOMMENDED", True,
    ),
    item(
        "Tamarind Margarita", 225, "coupe_glass",
        "A cloudy amber-orange tamarind margarita with a fine salt-chilli rim, garnished with a lime wheel "
        "and a small tamarind pod.", "DRINKS", True, 1, None, True,
    ),
    item(
        "Rose Lassi Martini", 205, "martini_glass",
        "A pale pink, creamy rose-yogurt martini with a delicate foam top, garnished with a few dried rose "
        "petals and a light dusting of ground pistachio.", "DRINKS", True, 0, None, True,
    ),
    item(
        "Cucumber Mint Cooler", 145, "tall_glass",
        "A pale green non-alcoholic cooler over ice, visibly studded with cucumber ribbons and fresh mint "
        "leaves, garnished with a mint sprig and a thin cucumber wheel on the rim.", "DRINKS", True, 0,
        None, True,
    ),
    item(
        "Spiced Chai", 95, "chai_cup",
        "A cup of rich, milky spiced chai with a thin layer of froth, a cinnamon stick and a star anise pod "
        "resting on the saucer beside it.", "DRINKS", True, 0, None, True,
    ),
    item(
        "Mango Lassi", 105, "lassi_glass",
        "A thick, bright orange-yellow mango yogurt drink, topped with a light dusting of ground cardamom "
        "and a small mint sprig.", "DRINKS", True, 0, None, True,
    ),
]

if __name__ == "__main__":
    with open("items.json", "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to items.json")

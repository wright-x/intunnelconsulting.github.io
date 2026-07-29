#!/usr/bin/env python3
"""Builds menu_items.json for The Theater Indian Kitchen & Bar photo shoot."""
import json
import re

STYLE_SUFFIX = (
    "Bright, premium, LIGHT and WHITE studio background: clean white seamless "
    "backdrop, soft even studio lighting, minimal soft shadow, high-end editorial "
    "food/product photography look. Shallow depth of field, tack-sharp focus on "
    "the food with a softly blurred background. Natural, fresh garnish exactly as "
    "described. No text, no logos, no hands, no plate labels, no watermarks. "
    "Photorealistic, professional restaurant menu photography, ultra-detailed, "
    "2K quality."
)

PLATEWARE = {
    "oval_sauce_well": (
        "Presented on a matte white/off-white ceramic oval plate (NOT dark, "
        "NOT black, NOT charcoal - the plate itself is white/cream colored) "
        "with a small built-in triangular sauce well on one side holding a "
        "matching chutney or dip, exactly like the reference plate provided."
    ),
    "round_plain": (
        "Presented on a plain matte white/cream ceramic oval plate (NOT dark, "
        "NOT black, NOT charcoal - the plate itself is white/cream colored) "
        "with a subtle organic hand-thrown rim texture, exactly like the "
        "reference plate provided."
    ),
    "wooden_tray": (
        "Presented on a curved dark walnut wooden serving tray with several "
        "round wells, each component resting in its own well, exactly like the "
        "reference tray provided."
    ),
    "copper_martini": (
        "Served in a polished copper martini glass with a wide tapered conical "
        "bowl on a slender stem and round copper base, exactly like the "
        "reference glass provided."
    ),
    "rattan_basket": (
        "Presented in a small rectangular woven rattan/wicker bread basket "
        "lined with a neutral linen napkin."
    ),
    "shot_glasses": (
        "Served as a neat row of small clear glass shot glasses filled with "
        "tangy, colorful pani puri flavored water, alongside crisp golden "
        "puris filled with potato and chickpea stuffing arranged beside them."
    ),
    "copper_karahi": (
        "Served in a small hammered copper karahi (traditional Indian "
        "wok-shaped serving bowl) with polished brass ring handles, resting on "
        "a round wooden coaster."
    ),
    "copper_handi_rice": (
        "Served in a small hammered copper handi bowl (rounded, no handles), "
        "the rice mounded gently, resting on a round wooden coaster."
    ),
    "copper_biryani_handi": (
        "Served in a hammered copper biryani handi (rounded pot) with a domed "
        "hammered-copper lid propped partially open beside it, fragrant rice "
        "visibly steaming, resting on a round wooden coaster."
    ),
    "glass_tumbler": (
        "Served in a clear glass tumbler, resting on a small round copper "
        "coaster."
    ),
    "copper_mug": (
        "Served in a hammered copper mug with a small handle, resting on a "
        "matching hammered copper saucer."
    ),
    "ceramic_cup": (
        "Served in a light speckled ceramic cup and saucer."
    ),
    "tall_glass": (
        "Served in a tall clear glass, resting on a small round wooden coaster."
    ),
    "mason_jar": (
        "Served in a clear glass mason jar with a handle, filled with ice."
    ),
    "dessert_bowl": (
        "Served in a small light matte ceramic bowl."
    ),
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, price, desc, category, plateware_key, garnish_note=""):
    plateware = PLATEWARE[plateware_key]
    subject = f"A premium editorial food photograph of {name}: {desc}"
    if garnish_note:
        subject += f" {garnish_note}"
    prompt = f"{subject} {plateware} {STYLE_SUFFIX}"
    return {
        "name": name,
        "price_vnd_k": price,
        "description": desc,
        "category": category,
        "plateware": plateware_key,
        "slug": slug(name),
        "prompt": prompt,
    }


items = []

# ---------------- Small Plates & Bar Bites ----------------
cat = "Small Plates & Bar Bites"
items += [
    item("French Fries", 125, "crispy golden fries seasoned with sea salt", cat, "oval_sauce_well",
         "Fries stacked neatly with a light dusting of sea salt flakes, sauce well filled with garlic aioli."),
    item("Peri Peri Fries", 135, "crispy fries tossed in spicy peri peri seasoning", cat, "oval_sauce_well",
         "Fries with a vivid red-orange peri peri dusting, sauce well filled with a creamy dip, fresh curry leaf garnish."),
    item("Masala Peanut Bowl", 75, "roasted peanuts tossed with curry leaves and aromatic spices", cat, "oval_sauce_well",
         "Glossy roasted peanuts flecked with crispy fried curry leaves and mustard seeds, sauce well filled with a lemon wedge."),
    item("Crispy Bhindi", 150, "crispy finger-cut okra strips coated in light besan batter, deep-fried to golden perfection", cat, "oval_sauce_well",
         "Thin golden okra strips piled loosely for height and crunch, sauce well filled with a red chilli dip, a few whole dried red chillies scattered nearby."),
    item("Samosa with Mint Chutney", 120, "spiced potato pastry served with fresh mint chutney", cat, "oval_sauce_well",
         "Two golden triangular samosas with visible flaky layers, sauce well filled with vivid green mint chutney."),
    item("Hara Bhara Kebab", 165, "spinach and pea kebabs served with mint chutney", cat, "oval_sauce_well",
         "Deep green herbed kebab patties with a lightly charred crust, thin red onion rings on the side, sauce well filled with mint chutney."),
    item("Chilli Paneer", 199, "cottage cheese cubes tossed in a spicy Indo-Chinese chilli sauce with bell peppers, onions and spring onions", cat, "oval_sauce_well",
         "Glossy red-brown sauce coating golden-fried paneer cubes with vivid red and green bell pepper pieces and scattered spring onion, sauce well filled with a light yogurt dip."),
    item("Paneer 65", 199, "crispy cottage cheese tossed with curry leaves, garlic and South Indian spices", cat, "oval_sauce_well",
         "Bright red-orange crispy paneer cubes flecked with fried curry leaves and garlic slivers, sauce well filled with a cooling yogurt dip."),
    item("Honey Chilli Potato", 150, "crispy potato fingers tossed in honey, chilli and aromatic spices", cat, "oval_sauce_well",
         "Glossy honey-glazed potato fingers with sesame seeds and scattered spring onion, sauce well filled with a light dip."),
    item("Gobhi 65", 165, "crispy cauliflower florets tossed with aromatic spices and curry leaves", cat, "oval_sauce_well",
         "Bright red-orange crispy cauliflower florets flecked with fried curry leaves, sauce well filled with a cooling yogurt dip."),
    item("Veg Manchurian (Dry)", 195, "crispy vegetable balls tossed with garlic, peppers and a savoury sauce", cat, "oval_sauce_well",
         "Glossy dark-glazed vegetable balls with diced bell pepper and spring onion, sauce well filled with a light dip."),
    item("Hakka Noodles", 180, "stir-fried noodles with fresh vegetables, garlic and aromatic seasoning", cat, "oval_sauce_well",
         "Glossy stir-fried noodles tangled with julienned carrot, cabbage and bell pepper, sauce well filled with a light chilli-vinegar dip."),
    item("Chicken 65", 220, "crispy fried chicken tossed with curry leaves, garlic and aromatic South Indian spices", cat, "oval_sauce_well",
         "Deep red crispy chicken pieces flecked with fried curry leaves and garlic slivers, sauce well filled with a cooling yogurt dip."),
    item("Chilli Chicken", 220, "crispy chicken tossed in a bold chilli sauce", cat, "oval_sauce_well",
         "Glossy dark-red sauced chicken pieces with charred bell pepper and onion petals, sauce well filled with a light dip."),
    item("Butter Garlic Prawns", 250, "juicy prawns sauteed with garlic, herbs and butter", cat, "oval_sauce_well",
         "Plump pink-orange prawns glistening in garlic butter with visible garlic slivers and chopped parsley, sauce well filled with a lemon wedge."),
    item("Fish Amritsari", 245, "crispy fish fingers coated in gram flour and Amritsari spices", cat, "oval_sauce_well",
         "Golden-battered fish fingers stacked neatly, thin red onion rings and a lemon wedge beside them, sauce well filled with mint chutney."),
]

# ---------------- Chaat & Fast Sellers ----------------
cat = "Chaat & Fast Sellers"
items += [
    item("Masala Papad", 55, "crispy papad topped with onion, tomato and fresh herbs", cat, "oval_sauce_well",
         "A large thin crisp papad generously topped with finely diced onion, tomato and cilantro, sauce well filled with mint chutney."),
    item("Pani Puri Shots", 90, "crispy puris served with tangy flavored waters and chutneys", cat, "shot_glasses",
         "Round hollow crisp puris filled with mashed potato and chickpeas arranged beside a row of small glasses filled with tangy mint-green and tamarind-brown flavored water."),
    item("Dahi Papdi Chaat", 150, "crispy wafers topped with yogurt, chutneys and spices", cat, "oval_sauce_well",
         "Crisp round papdi wafers layered under a generous swirl of thick white yogurt, drizzled with tamarind and mint chutneys and dusted with spice, sauce well filled with extra chutney."),
    item("Aloo Tikki Chaat", 155, "crispy potato patties topped with yogurt and chutneys", cat, "oval_sauce_well",
         "Golden-crusted potato patties topped with thick yogurt, tamarind and mint chutney swirls and a few chickpeas, sauce well filled with extra chutney."),
    item("Papad", 45, "crispy lentil wafers served as a light and crunchy starter", cat, "oval_sauce_well",
         "A single large thin golden roasted lentil papad with a light cracked texture, sauce well filled with mint chutney."),
    item("Green Salad", 100, "fresh and crisp salad with cucumbers, tomatoes, onions and carrots", cat, "oval_sauce_well",
         "Crisp cucumber rounds, tomato wedges, thin red onion rings and julienned carrot arranged in a fresh colorful pile, sauce well filled with a light lemon dressing."),
    item("Crispy Corn", 125, "crispy sweet corn tossed with spices, herbs and chilli", cat, "oval_sauce_well",
         "Golden crispy corn kernels tossed with herbs and a light chilli dusting, sauce well filled with a light dip."),
    item("Chole Bhature", 185, "spiced chickpea curry served with fluffy fried bhature bread", cat, "oval_sauce_well",
         "A rich dark-brown spiced chickpea curry beside a large puffed golden fried bhature bread, thin red onion rings and a lemon wedge, sauce well filled with pickled chilli."),
    item("Mix Raita", 95, "refreshing yogurt with vegetables and roasted spices", cat, "oval_sauce_well",
         "Thick white yogurt studded with finely diced cucumber, tomato and onion, dusted with roasted cumin, sauce well filled with mint garnish."),
    item("Mix Veg Pakora", 160, "crispy mixed vegetable fritters served with mint chutney", cat, "oval_sauce_well",
         "Irregular golden-brown crispy vegetable fritters piled loosely for height, sauce well filled with vivid green mint chutney."),
    item("Samosa Chaat", 150, "crushed samosas topped with yogurt, chutneys and spices", cat, "oval_sauce_well",
         "Crushed golden samosa pieces topped with thick yogurt, tamarind and mint chutney drizzles and fine sev, sauce well filled with extra chutney."),
]

# ---------------- Tandoor & Grill ----------------
cat = "Tandoor & Grill"
items += [
    item("Paneer Tikka Skewers", 220, "cottage cheese cubes marinated in yogurt and aromatic Indian spices, grilled in the traditional tandoor", cat, "round_plain",
         "Skewers of char-grilled marinated paneer cubes with bell pepper and onion pieces, visible smoky char marks, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Mushroom Tikka", 190, "mushrooms marinated in yogurt and blended Indian spices, grilled to smoky perfection in the tandoor", cat, "round_plain",
         "Skewers of char-grilled whole marinated mushrooms with visible smoky char marks, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Achari Paneer Tikka", 220, "cottage cheese marinated with traditional Indian pickling spices and grilled over charcoal", cat, "round_plain",
         "Skewers of char-grilled paneer cubes with a mustard-yellow pickled-spice crust, bell pepper and onion pieces, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Chicken Tikka", 230, "tender boneless chicken marinated with yogurt, spices and grilled in the tandoor", cat, "round_plain",
         "Skewers of char-grilled deep-red marinated chicken pieces with smoky char marks, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Chicken Malai Tikka", 240, "creamy cheese and cream-marinated chicken grilled until lightly charred", cat, "round_plain",
         "Skewers of char-grilled pale creamy-white chicken pieces with light char marks, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Tangdi Kebab", 250, "three tandoor-grilled chicken drumsticks marinated with aromatic Indian spices", cat, "round_plain",
         "Three deep-red char-grilled chicken drumsticks fanned out, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Tandoori Chicken", 265, "half chicken with one breast and one leg, marinated overnight and roasted in the tandoor", cat, "round_plain",
         "A vivid red-orange tandoori half chicken (one breast, one leg) with visible char marks, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Tandoori Fish Tikka", 265, "six boneless fish cubes marinated with spices and grilled in the tandoor", cat, "round_plain",
         "Six golden-orange char-grilled fish cubes arranged neatly, thin red onion rings, a lemon wedge and a small metal cup of mint chutney beside."),
    item("Mixed Tandoori Platter", 399, "Chicken Tikka, Chicken Malai Tikka, Paneer Tikka and Achari Paneer Tikka served on one sizzling platter with mint chutney", cat, "wooden_tray",
         "A generous assortment of char-grilled chicken tikka, chicken malai tikka, paneer tikka and achari paneer tikka skewer pieces arranged across the tray's wells, with mint chutney in one well and a lemon wedge tucked alongside, gentle wisps of steam suggesting it just came off the grill."),
]

# ---------------- Main Curries ----------------
cat = "Main Curries"
items += [
    item("Dal Makhani", 165, "creamy black lentils slow-cooked with butter and aromatic spices", cat, "copper_karahi",
         "Deep brown creamy lentils with a swirl of cream on top and a small pat of melting butter in the center, finished with fresh cilantro."),
    item("Paneer Butter Masala", 199, "cottage cheese cooked in a rich tomato and butter gravy", cat, "copper_karahi",
         "Soft paneer cubes in a smooth vivid orange-red tomato-butter gravy, finished with a swirl of cream and fresh cilantro."),
    item("Dal Tadka", 150, "yellow lentils tempered with garlic, cumin and spices", cat, "copper_karahi",
         "Smooth golden-yellow lentils topped with a sizzling tempering of garlic slivers, cumin seeds and dried red chilli in ghee, finished with fresh cilantro."),
    item("Kadhai Paneer", 199, "cottage cheese cooked with bell peppers, onions and traditional spices", cat, "copper_karahi",
         "Golden paneer cubes tossed with colorful bell pepper and onion pieces in a thick reddish-brown masala, finished with fresh cilantro."),
    item("Palak Paneer", 199, "cottage cheese simmered in a creamy spinach gravy", cat, "copper_karahi",
         "Soft paneer cubes set in a smooth vivid green spinach gravy, finished with a swirl of cream and a fresh cilantro leaf."),
    item("Malai Kofta", 195, "vegetable dumplings served in a rich creamy curry", cat, "copper_karahi",
         "Golden-fried vegetable dumplings submerged in a smooth creamy orange gravy, finished with a drizzle of cream, toasted nuts and fresh cilantro."),
    item("Veg Jalfrezi", 165, "mixed vegetables tossed in a spiced tomato-based gravy", cat, "copper_karahi",
         "Colorful bell pepper, carrot, baby corn and bean pieces in a light spiced tomato gravy, finished with fresh cilantro."),
    item("Jeera Aloo", 155, "potatoes sauteed with cumin and aromatic spices", cat, "copper_karahi",
         "Golden baby potatoes tossed with visible cumin seeds and dried red chilli, finished with fresh cilantro."),
    item("Dum Aloo", 185, "baby potatoes simmered in a rich spiced gravy", cat, "copper_karahi",
         "Whole baby potatoes in a rich reddish-orange spiced gravy, finished with fresh cilantro."),
    item("Bhindi Masala", 165, "okra cooked with onions, tomatoes and aromatic spices", cat, "copper_karahi",
         "Sliced okra sauteed with onion and tomato in a dry masala coating, finished with fresh cilantro."),
    item("Aloo Gobhi", 170, "potatoes and cauliflower cooked with traditional Indian spices", cat, "copper_karahi",
         "Golden potato and cauliflower florets tossed in a light turmeric-spiced dry masala, finished with fresh cilantro."),
    item("Butter Chicken", 245, "tender chicken cooked in a rich tomato and butter gravy", cat, "copper_karahi",
         "Tender chicken pieces in a smooth vivid orange-red tomato-butter gravy, finished with a swirl of cream and fresh cilantro."),
    item("Chicken Tikka Masala", 235, "grilled chicken tikka simmered in a rich spiced tomato gravy", cat, "copper_karahi",
         "Char-grilled chicken tikka pieces with visible smoky edges in a thick spiced tomato gravy, finished with fresh cilantro."),
    item("Kadai Chicken", 225, "chicken cooked with onions, bell peppers and aromatic Indian spices", cat, "copper_karahi",
         "Chicken pieces tossed with colorful bell pepper and onion in a thick reddish-brown masala, finished with fresh cilantro."),
    item("Egg Curry", 175, "two whole boiled eggs simmered in a rich traditional Indian curry", cat, "copper_karahi",
         "Two halved or whole boiled eggs submerged in a rich reddish-orange curry, finished with fresh cilantro."),
    item("Egg Bhurji", 175, "Indian-style scrambled eggs cooked with onions, tomatoes, green chili and aromatic spices", cat, "copper_karahi",
         "Soft golden-yellow scrambled eggs studded with diced onion, tomato and green chilli, finished with fresh cilantro."),
]

# ---------------- Seafood Curries ----------------
cat = "Seafood Curries"
items += [
    item("Fish Curry Coastal Style", 240, "fresh fish simmered in a rich coastal-style curry", cat, "copper_karahi",
         "Firm white fish pieces in a golden-orange coconut-spiced coastal curry, finished with fresh curry leaves."),
    item("Prawn Masala", 260, "prawns cooked in a spiced onion and tomato gravy", cat, "copper_karahi",
         "Plump prawns in a thick reddish-brown onion-tomato masala, finished with fresh cilantro."),
    item("Goan Prawn Curry", 260, "prawns cooked in a coconut-based coastal curry with aromatic spices", cat, "copper_karahi",
         "Plump prawns in a golden-yellow coconut curry, finished with fresh curry leaves."),
]

# ---------------- Breads ----------------
cat = "Breads"
items += [
    item("Tandoori Roti / Tawa Roti", 55, "soft whole wheat bread baked in the tandoor", cat, "rattan_basket",
         "A round char-flecked whole wheat flatbread with a lightly blistered surface."),
    item("Garlic Naan", 85, "soft naan bread topped with garlic and fresh coriander", cat, "rattan_basket",
         "A pillowy oval naan with charred blister spots, topped with chopped garlic and fresh coriander."),
    item("Laccha Parantha", 80, "multi-layered whole wheat bread cooked on a tawa with a touch of ghee", cat, "rattan_basket",
         "A round layered flatbread with visible spiral flaky layers and a light ghee sheen."),
    item("Plain Naan", 75, "soft and pillowy white flour bread baked in the tandoor", cat, "rattan_basket",
         "A pillowy oval white-flour naan with light charred blister spots."),
    item("Cheese Garlic Naan", 95, "soft naan topped with garlic and melted cheese, baked in the tandoor", cat, "rattan_basket",
         "An oval naan topped with melted golden cheese and chopped garlic, cut into wedges."),
    item("Chilli Cheese Naan", 95, "soft naan loaded with cheese, garlic and a touch of chili, baked in the tandoor", cat, "rattan_basket",
         "A round naan topped with melted cheese, chopped garlic and red chilli flakes, cut into wedges."),
    item("Stuffed Naan (Aloo / Mix / Paneer)", 110, "soft naan stuffed with your choice of aloo, mix or paneer, baked to perfection in the tandoor", cat, "rattan_basket",
         "A pillowy naan cut into triangular wedges revealing a golden spiced potato stuffing inside."),
    item("Parantha", 110, "traditional layered flatbread with a soft, flaky texture, cooked on a griddle", cat, "rattan_basket",
         "A round griddle-cooked layered flatbread with a light golden-brown flaky surface and a touch of ghee sheen."),
]

# ---------------- Rice & Khichdi ----------------
cat = "Rice & Khichdi"
items += [
    item("Dal Khichdi", 180, "comforting rice and lentils cooked together with mild spices", cat, "copper_handi_rice",
         "Soft golden-yellow rice and lentils mounded gently with a small pat of melting butter on top, finished with fresh cilantro."),
    item("Steamed Basmati Rice", 85, "light and fragrant long-grain basmati rice", cat, "copper_handi_rice",
         "Fluffy separate long-grain white basmati rice mounded gently, finished with a single fresh cilantro leaf."),
    item("Jeera Rice", 99, "basmati rice tempered with cumin and aromatic spices", cat, "copper_handi_rice",
         "Fluffy basmati rice flecked with visible toasted cumin seeds, finished with a dried red chilli and fresh cilantro."),
]

# ---------------- Biryani ----------------
cat = "Biryani"
items += [
    item("Paneer Biryani", 210, "aromatic basmati rice layered with paneer and traditional spices", cat, "copper_biryani_handi",
         "Fragrant saffron-streaked basmati rice layered with golden-seared paneer cubes, fried onions, mint leaves and whole spices."),
    item("Veg Biryani", 190, "fragrant basmati rice layered with vegetables and traditional spices", cat, "copper_biryani_handi",
         "Fragrant saffron-streaked basmati rice layered with colorful mixed vegetables, fried onions, mint leaves and whole spices."),
    item("Egg Biryani", 195, "fragrant basmati rice layered with eggs and aromatic spices", cat, "copper_biryani_handi",
         "Fragrant saffron-streaked basmati rice topped with halved boiled eggs, fried onions, mint leaves and whole spices."),
    item("Chicken Biryani", 230, "slow-cooked basmati rice layered with chicken and aromatic spices", cat, "copper_biryani_handi",
         "Fragrant saffron-streaked basmati rice layered with tender bone-in chicken pieces, fried onions, mint leaves and whole spices."),
    item("Prawn Biryani", 250, "fragrant basmati rice layered with prawns and traditional spices", cat, "copper_biryani_handi",
         "Fragrant saffron-streaked basmati rice layered with plump prawns, fried onions, mint leaves and whole spices."),
]

# ---------------- Drinks ----------------
cat = "Drinks"
items += [
    item("Masala Tea", 60, "traditional Indian tea brewed with aromatic spices", cat, "copper_mug",
         "Warm reddish-brown spiced milk tea with a light steam rising, a few whole spices (cardamom, cinnamon stick) resting beside the mug."),
    item("Mango Lassi", 110, "creamy yogurt drink blended with ripe mango", cat, "tall_glass",
         "A thick, bright orange creamy mango yogurt drink, topped with a light dusting of cardamom and a small mint sprig."),
    item("Lassi", 110, "traditional yogurt drink served chilled", cat, "tall_glass",
         "A thick pale creamy-white yogurt drink, topped with a light dusting of cardamom and a small mint sprig."),
    item("Cold Drink", 50, "choice of Coca-Cola, Sprite or Fanta", cat, "glass_tumbler",
         "A fizzy cola-colored soft drink over ice cubes with visible rising bubbles, a lemon wedge on the rim."),
    item("Masala Chaas", 85, "refreshing spiced buttermilk blended with roasted cumin and traditional Indian seasonings", cat, "tall_glass",
         "A pale frothy spiced buttermilk drink, topped with a light dusting of roasted cumin and a small mint sprig."),
    item("Water / Sparkling Water", 25, "chilled bottled still or sparkling water", cat, "glass_tumbler",
         "A clear glass filled with chilled still water with visible condensation, ice cubes and a light mint sprig, unbranded plain glass bottle beside it."),
]

# ---------------- Coffee ----------------
cat = "Coffee"
items += [
    item("Cappuccino", 85, "espresso with steamed milk and velvety foam", cat, "ceramic_cup",
         "A cappuccino with a delicate latte-art rosette in the velvety foam, a few coffee beans scattered beside the cup."),
    item("Latte", 85, "smooth espresso blended with silky steamed milk", cat, "tall_glass",
         "A layered latte in a tall clear glass showing espresso, milk and a light foam cap, a few coffee beans scattered beside."),
    item("Espresso", 60, "rich and intense single-shot coffee", cat, "ceramic_cup",
         "A small shot of dark espresso with a thin golden crema layer on top, a few coffee beans scattered beside the cup."),
    item("Americano", 75, "espresso balanced with hot water for a smooth finish", cat, "ceramic_cup",
         "A cup of dark americano coffee with a thin crema swirl on the surface, a few coffee beans scattered beside the cup."),
]

# ---------------- Juices, Smoothies & Iced Tea ----------------
cat = "Juices, Smoothies & Iced Tea"
items += [
    item("Orange Juice", 95, "fresh-squeezed orange juice", cat, "tall_glass",
         "Vivid orange fresh juice, garnished with an orange wedge on the rim, condensation on the glass."),
    item("Watermelon Juice", 95, "fresh watermelon juice", cat, "tall_glass",
         "Vivid pink-red watermelon juice, garnished with a small watermelon wedge on the rim, condensation on the glass."),
    item("Pineapple Juice", 95, "fresh pineapple juice", cat, "tall_glass",
         "Golden-yellow pineapple juice, garnished with a pineapple wedge and leaf on the rim, condensation on the glass."),
    item("Mixed Fruit Juice", 95, "fresh mixed fruit juice", cat, "tall_glass",
         "Vivid orange-red mixed fruit juice, garnished with an apple slice and mint sprig, condensation on the glass."),
    item("Lemon Iced Tea", 80, "chilled lemon iced tea", cat, "mason_jar",
         "Amber iced tea over ice cubes, garnished with fresh lemon slices and a mint sprig."),
    item("Peach Iced Tea", 80, "chilled peach iced tea", cat, "mason_jar",
         "Amber iced tea over ice cubes, garnished with fresh peach slices and a mint sprig."),
    item("Mango Magic Smoothie", 110, "mango, yogurt, honey and a touch of vanilla", cat, "tall_glass",
         "A thick bright orange mango smoothie topped with a small diced mango garnish."),
    item("Berry Bliss Smoothie", 110, "mixed berries, yogurt, honey and apple juice", cat, "tall_glass",
         "A thick vivid purple-pink berry smoothie topped with fresh blueberries and raspberries."),
    item("Banana Nut Smoothie", 110, "banana, peanut butter, milk and honey", cat, "tall_glass",
         "A thick pale beige banana-peanut butter smoothie topped with banana slices and chopped peanuts."),
    item("Chocolate Mocha Smoothie", 110, "chocolate, coffee, banana, milk and cocoa powder", cat, "tall_glass",
         "A thick rich brown chocolate-coffee smoothie topped with chocolate shavings."),
    item("Strawberry Delight Smoothie", 110, "strawberry, yogurt, banana and a touch of honey", cat, "tall_glass",
         "A thick vivid pink strawberry smoothie topped with a fresh strawberry half."),
]

# ---------------- Desserts ----------------
cat = "Desserts"
items += [
    item("Gulab Jamun with Vanilla Ice Cream", 90, "soft milk dumplings soaked in saffron syrup, served with creamy vanilla ice cream", cat, "copper_martini",
         "Two glossy deep-brown gulab jamun dumplings soaked in golden saffron syrup, nestled beside a scoop of creamy vanilla ice cream, garnished with chopped pistachios and a few saffron strands, syrup pooling gently in the base of the glass."),
    item("Ice Cream (Vanilla)", 60, "classic vanilla ice cream served chilled", cat, "dessert_bowl",
         "A single neat scoop of creamy white vanilla ice cream, garnished with a small mint leaf."),
    item("Ice Cream (Chocolate)", 60, "classic chocolate ice cream served chilled", cat, "dessert_bowl",
         "A single neat scoop of rich dark chocolate ice cream, garnished with chocolate shavings."),
    item("Kheer", 90, "creamy rice pudding slow-cooked with milk, garnished with nuts and saffron", cat, "dessert_bowl",
         "Creamy pale rice pudding topped with slivered almonds, pistachios and a few saffron strands."),
    item("Gajar Halwa", 110, "classic carrot pudding cooked with milk, garnished with nuts", cat, "dessert_bowl",
         "Rich glossy orange-red carrot pudding topped with slivered almonds and pistachios."),
]

with open("menu_items.json", "w") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(items)} items to menu_items.json")

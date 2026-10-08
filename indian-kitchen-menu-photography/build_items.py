#!/usr/bin/env python3
"""Builds items.json for the SAPA PREMIUM INDIAN KITCHEN menu photo shoot.
White studio background for all dish photos so they can be cleanly cut out
and composited onto the burgundy/gold page layouts later. Plating is the
ORIGINAL premium, elevated style — thoughtful composition, confident
garnish — just with the SAPA dish list and mountain-town vessel touches."""
import json
import re

STYLE_SUFFIX = (
    "Ultra-premium, fine-dining editorial food photography — thoughtful, "
    "confident plating, everything composed on the ONE plate (no side "
    "cups, no extra dishes, no props scattered around it) with "
    "intentional asymmetry, height and texture contrast, a few "
    "deliberate garnishes (fresh herbs, one or two edible flowers, "
    "toasted nuts) placed like a chef would place them, never scattered "
    "randomly. Absolutely no painted sauce swooshes, smears, purée "
    "brushstrokes, or dragged dots of sauce anywhere on the plate or "
    "bowl — any chutney, yoghurt or dip is served neatly spooned into a "
    "small side ramekin or quenelle, never painted directly onto the "
    "plate's surface. Bright, clean white studio "
    "background: seamless white backdrop, soft directional studio "
    "lighting from one side, soft natural shadow, elevated three-quarter "
    "angle looking down at the plate. Photorealistic, shot on a "
    "full-frame camera, ultra-detailed, natural food texture, 2K "
    "quality. No text, no logos, no hands, no watermark, no restaurant "
    "background of any kind — pure white studio only."
)

DRINK_STYLE_SUFFIX = (
    "Ultra-premium, fine-dining editorial beverage photography — the "
    "glass or cup styled thoughtfully with a well-placed garnish, never "
    "cluttered. Bright, clean white studio background: seamless white "
    "backdrop, soft directional studio lighting from one side, soft "
    "natural shadow, straight-on eye-level angle. Photorealistic, shot "
    "on a full-frame camera, ultra-detailed, natural condensation and "
    "ice clarity where relevant, 2K quality. No text, no logos, no "
    "hands, no watermark, no restaurant background of any kind — pure "
    "white studio only."
)

CATEGORY_VESSEL = {
    "BREAKFAST": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "WARMERS": "a plain white ceramic soup bowl, wide and shallow with a simple rim — a proper restaurant soup bowl shape, NOT a teacup, NOT a mug, no handle",
    "MAGGI": "a plain white ceramic bowl with a simple rim",
    "SMALL PLATES": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "TANDOOR VEG": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "TANDOOR NONVEG": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "DALS": "a plain white ceramic bowl with a simple matte finish",
    "VEG CURRIES": "a plain white ceramic bowl with a simple matte finish",
    "MEAT CURRIES": "a plain white ceramic bowl with a simple matte finish",
    "BREADS": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "RICE": "a plain white ceramic bowl with a simple matte finish",
    "BIRYANI": "a plain white ceramic bowl with a simple matte finish",
    "SWEETS": "a plain white ceramic plate with a simple matte finish and a clean rim",
    "CHAI": "a traditional handmade clay kulhad cup resting on a small wooden saucer",
    "COLD DRINKS": "a tall clear glass or brushed steel tumbler over ice",
    "ZERO PROOF": "an elegant tall glass or coupe glass",
}

CATEGORY_GARNISH = {
    "BREAKFAST": "finished with a few fresh coriander leaves, with yoghurt and pickle served neatly in small side ramekins rather than on the plate itself",
    "WARMERS": "finished with a swirl of cream, a scatter of fresh coriander and one edible flower",
    "MAGGI": "finished with a scatter of fresh coriander only — absolutely no sesame seeds anywhere on the dish",
    "SMALL PLATES": "finished with fresh coriander and one edible flower, any chutney served neatly in a small side ramekin rather than painted on the plate",
    "TANDOOR VEG": "finished with a scatter of pomegranate arils and fresh coriander, a lime wedge tucked beside it, any yoghurt dip served neatly in a small side ramekin rather than smeared on the plate",
    "TANDOOR NONVEG": "finished with a scatter of pomegranate arils and fresh coriander, a lime wedge tucked beside it, any yoghurt dip served neatly in a small side ramekin rather than smeared on the plate",
    "DALS": "finished with a swirl of cream, a pat of butter melting on top and fresh coriander, gentle wisps of steam rising",
    "VEG CURRIES": "finished with a swirl of cream, toasted nuts and fresh coriander, gentle wisps of steam rising",
    "MEAT CURRIES": "finished with a swirl of cream, toasted cashews and fresh coriander, gentle wisps of steam rising",
    "BREADS": "brushed lightly with ghee, a light dusting of flour, fresh from the tandoor with charred blister spots",
    "RICE": "finished with a single fresh coriander leaf",
    "BIRYANI": "topped with golden fried onions, fresh mint and coriander leaves, whole star anise and green cardamom visible on top, gentle wisps of steam rising",
    "SWEETS": "finished with a scatter of chopped nuts, a few saffron strands and one edible flower — no sauce, caramel, or paste of any kind drizzled or swooshed on the plate",
    "CHAI": "with a thin layer of froth, a cinnamon stick or star anise resting beside it",
    "COLD DRINKS": "garnished with a mint sprig and a citrus wheel on the rim",
    "ZERO PROOF": "garnished thoughtfully with a fresh herb sprig and a citrus twist",
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/&]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, price, category, description, veg=True, jain=False, spice=0, hero=False, extra=""):
    drink = category in ("CHAI", "COLD DRINKS", "ZERO PROOF")
    vessel = CATEGORY_VESSEL[category]
    garnish = CATEGORY_GARNISH[category]
    style = DRINK_STYLE_SUFFIX if drink else STYLE_SUFFIX
    extra_text = f" {extra}" if extra else ""
    prompt = (
        f"A premium editorial {'beverage' if drink else 'food'} photograph of {name}: "
        f"{description} Presented in/on {vessel}, {garnish}.{extra_text} {style}"
    )
    return {
        "name": name, "price_k": price, "slug": slug(name), "category": category,
        "veg": veg, "jain": jain, "spice": spice, "hero": hero, "description": description,
        "prompt": prompt,
    }


items = [
    # ---------------- BREAKFAST ----------------
    item("Aloo Paratha", 115, "BREAKFAST", "Flaky whole-wheat paratha stuffed with spiced potato, served with yoghurt and pickle."),
    item("Paneer Paratha", 145, "BREAKFAST", "Whole-wheat paratha generously filled with seasoned cottage cheese."),
    item("Poha", 105, "BREAKFAST", "Light flattened rice cooked with vegetables, peanuts, curry leaves and fresh lime."),
    item("Masala Omelette & Toast", 120, "BREAKFAST", "Indian-style omelette with onion, tomato, coriander and green chilli.", veg=False),
    item("Chole Bhature", 185, "BREAKFAST", "Spiced chickpea curry with hot, fluffy bhature."),
    # ---------------- SAPA WARMERS ----------------
    item("Tomato Dhaniya Shorba", 95, "WARMERS", "Slow-cooked tomato soup finished with coriander and warming Indian spices.", jain=True),
    item("Vegetable Manchow Soup", 105, "WARMERS", "Hot Indo-Chinese vegetable soup with garlic, chilli and crispy noodles.", spice=1),
    item("Chicken Shorba", 120, "WARMERS", "Comforting Indian chicken broth with ginger, coriander and aromatic spices.", veg=False),
    # ---------------- MAGGI IN THE MOUNTAINS ----------------
    item("Masala Maggi", 105, "MAGGI", "Classic Indian-style masala instant noodles.", hero=True,
         extra="No sesame seeds anywhere on the dish."),
    item("Vegetable Masala Maggi", 125, "MAGGI", "Masala Maggi cooked with fresh vegetables."),
    item("Cheese & Vegetable Maggi", 145, "MAGGI", "Hot masala noodles with vegetables and melted cheese."),
    # ---------------- SMALL PLATES & CHAAT ----------------
    item("Vegetable Samosa with Mint Chutney", 99, "SMALL PLATES", "Crisp pastry stuffed with spiced potato and peas."),
    item("Pani Puri Shots", 95, "SMALL PLATES", "Crispy puris with potato filling, chutneys and tangy flavoured waters."),
    item("Aloo Tikki Chaat", 145, "SMALL PLATES", "Crispy potato patties with yoghurt and chutneys."),
    item("Mix Vegetable Pakora", 149, "SMALL PLATES", "Crispy vegetable fritters served with mint chutney."),
    item("Honey Chilli Potato", 150, "SMALL PLATES", "Crispy potato fingers tossed with honey, chilli and aromatic spices.", spice=2),
    item("Gobi 65", 165, "SMALL PLATES", "Crispy cauliflower tossed with curry leaves and South Indian spices.", spice=2),
    item("Chilli Paneer", 199, "SMALL PLATES", "Cottage cheese tossed with peppers, onion and chilli sauce.", spice=2),
    item("Chilli Chicken", 220, "SMALL PLATES", "Crispy chicken tossed in a bold Indo-Chinese chilli sauce.", veg=False, spice=2),
    # ---------------- FROM THE TANDOOR — VEGETARIAN ----------------
    item("Paneer Tikka", 220, "TANDOOR VEG", "Paneer marinated in yoghurt and aromatic spices, grilled in the tandoor.", hero=True,
         extra="A generous portion: the skewered paneer pieces arranged in two full rows side by side rather than a single row — a substantial, generous serving."),
    item("Achari Paneer Tikka", 220, "TANDOOR VEG", "Paneer marinated with traditional Indian pickling spices.", spice=1,
         extra="A generous portion: the skewered paneer pieces arranged in two full rows side by side rather than a single row — a substantial, generous serving."),
    item("Mushroom Tikka", 190, "TANDOOR VEG", "Yoghurt-marinated mushrooms grilled until smoky and tender.",
         extra="A generous portion: the skewered mushrooms arranged in two full rows side by side rather than a single row — a substantial, generous serving."),
    item("Vegetarian Tandoori Platter", 349, "TANDOOR VEG", "Paneer tikka, mushroom tikka and assorted vegetable kebabs."),
    # ---------------- FROM THE TANDOOR — NON-VEGETARIAN ----------------
    item("Chicken Tikka", 230, "TANDOOR NONVEG", "Boneless chicken marinated in yoghurt and Indian spices.", veg=False,
         extra="A generous portion: the skewered chicken pieces arranged in two full rows side by side rather than a single row — a substantial, generous serving."),
    item("Chicken Malai Tikka", 240, "TANDOOR NONVEG", "Creamy, delicately spiced chicken grilled until lightly charred.", veg=False, hero=True,
         extra="A generous portion: the skewered chicken pieces arranged in two full rows side by side rather than a single row — a substantial, generous serving."),
    item("Tandoori Chicken", 265, "TANDOOR NONVEG", "Half chicken marinated overnight and roasted in the tandoor.", veg=False,
         extra="A generous, substantial portion of half chicken."),
    item("Royal Mixed Grill", 399, "TANDOOR NONVEG", "Chicken tikka, malai tikka, tandoori chicken and chef's kebab selection.", veg=False),
    # ---------------- OUR SIGNATURE DALS ----------------
    item("Daal Bukhara", 195, "DALS", "Black lentils slowly simmered until velvety and rich, finished with butter and cream.", hero=True),
    item("Dal Tadka", 159, "DALS", "Yellow lentils tempered with garlic, cumin and spices."),
    item("Rajma Masala", 175, "DALS", "Red kidney beans simmered in a traditional North Indian masala."),
    item("Chana Masala", 175, "DALS", "Chickpeas cooked with tomato, ginger and aromatic spices."),
    # ---------------- VEGETARIAN CURRIES ----------------
    item("Paneer Butter Masala", 209, "VEG CURRIES", "Paneer simmered in silky tomato-butter gravy."),
    item("Kadai Paneer", 209, "VEG CURRIES", "Paneer with onions and bell peppers in aromatic kadai masala.", spice=2),
    item("Palak Paneer", 209, "VEG CURRIES", "Paneer cooked in smooth, lightly spiced spinach gravy."),
    item("Malai Kofta", 199, "VEG CURRIES", "Vegetable dumplings served in rich, creamy curry."),
    item("Veg Jalfrezi", 175, "VEG CURRIES", "Fresh vegetables tossed in a vibrant tomato-spice gravy.", spice=1),
    item("Jeera Aloo", 155, "VEG CURRIES", "Potatoes sautéed with cumin and aromatic spices.", jain=True),
    # ---------------- CHICKEN & MEAT CURRIES ----------------
    item("Royal Butter Chicken", 279, "MEAT CURRIES", "Tandoor-grilled chicken simmered in a silky tomato-butter gravy enriched with cashew and a touch of cream.", veg=False, hero=True),
    item("Chicken Tikka Masala", 239, "MEAT CURRIES", "Tandoori chicken tikka simmered in a rich spiced tomato gravy.", veg=False, spice=2),
    item("Kadai Chicken", 229, "MEAT CURRIES", "Chicken cooked with onion, bell pepper and traditional kadai spices.", veg=False, spice=2),
    item("Home-Style Chicken Curry", 219, "MEAT CURRIES", "Comforting Indian chicken curry cooked slowly with traditional spices.", veg=False),
    item("Kashmiri Fish Curry", 259, "MEAT CURRIES", "Tender fish slow-cooked in a fragrant Kashmiri-style gravy.", veg=False, spice=1),
    item("Goan Fish Curry", 249, "MEAT CURRIES", "Fish simmered in a tangy coconut and tomato curry.", veg=False, spice=2),
    item("Egg Curry", 175, "MEAT CURRIES", "Boiled eggs simmered in a traditional Indian curry.", veg=False),
    # ---------------- BREADS FROM THE TANDOOR ----------------
    item("Tandoori Roti", 55, "BREADS", "Whole-wheat flatbread baked in the tandoor.",
         extra="Authentic tandoor-baked roti, cooked by slapping the dough onto the inside wall of a clay tandoor oven: noticeably puffed up with a light char and smoky blistered dark spots across the surface, a rustic uneven round shape with a slightly irregular edge — it must NOT look flat, pale, or griddle-cooked like a tawa roti or chapati."),
    item("Plain Naan", 75, "BREADS", "Classic soft tandoor-baked naan.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Butter Naan", 80, "BREADS", "Soft tandoor-baked naan finished with melted butter.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Garlic Naan", 85, "BREADS", "Soft tandoor-baked naan topped with fresh garlic and coriander.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Lachha Paratha", 80, "BREADS", "Flaky layered whole-wheat paratha."),
    item("Cheese Garlic Naan", 95, "BREADS", "Tandoor-baked naan topped with melted cheese and fresh garlic.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Chilli Cheese Naan", 95, "BREADS", "Tandoor-baked naan topped with melted cheese and green chilli.", spice=1,
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Stuffed Aloo Naan", 110, "BREADS", "Tandoor-baked naan stuffed with spiced potato.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    item("Stuffed Paneer Naan", 145, "BREADS", "Tandoor-baked naan stuffed with seasoned cottage cheese.",
         extra="Traditional naan shape: a wide teardrop, elongated oval that tapers to a rounder point at one end — not a perfectly round or circular bread."),
    # ---------------- RICE & COMFORT BOWLS ----------------
    item("Steamed Basmati Rice", 85, "RICE", "Fluffy steamed basmati rice."),
    item("Jeera Rice", 99, "RICE", "Basmati rice tempered with toasted cumin."),
    item("Dal Khichdi", 180, "RICE", "Basmati rice and lentils cooked together into warming Indian comfort food."),
    item("Curd Rice & Pickle", 179, "RICE", "Cooling yoghurt rice tempered with mustard seeds and curry leaves."),
    item("Rajma Chawal", 195, "RICE", "North Indian kidney-bean curry served with steamed basmati rice.", hero=True),
    # ---------------- DUM BIRYANI ----------------
    item("Vegetable Dum Biryani", 190, "BIRYANI", "Fragrant basmati rice, layered and slow-cooked with charred vegetables."),
    item("Paneer Dum Biryani", 239, "BIRYANI", "Fragrant basmati rice, layered and slow-cooked with paneer."),
    item("Chicken Dum Biryani", 259, "BIRYANI", "Fragrant basmati rice, layered and slow-cooked with tender chicken.", veg=False, hero=True),
    item("Fish Dum Biryani", 269, "BIRYANI", "Fragrant basmati rice, layered and slow-cooked with tender fish.", veg=False),
    # ---------------- SOMETHING SWEET ----------------
    item("Hot Gulab Jamun", 85, "SWEETS", "Warm milk dumplings soaked in saffron-cardamom syrup."),
    item("Gulab Jamun with Vanilla Ice Cream", 95, "SWEETS", "Warm gulab jamun with cold vanilla ice cream."),
    item("Gajar Halwa", 110, "SWEETS", "Traditional warm carrot pudding cooked with milk, cardamom and nuts.", hero=True),
    item("Kheer", 90, "SWEETS", "Slow-cooked Indian rice pudding with cardamom and nuts."),
    # ---------------- CHAI & MOUNTAIN WARMERS ----------------
    item("Masala Chai", 60, "CHAI", "Indian milk tea brewed with aromatic spices."),
    item("Adrak Ginger Chai", 65, "CHAI", "Strong Indian tea brewed with fresh ginger."),
    item("Kashmiri Kahwa", 75, "CHAI", "Fragrant warming tea with saffron and traditional spices."),
    item("Kesar Badam Milk", 95, "CHAI", "Warm saffron milk with almond and cardamom."),
    item("Hot Chocolate", 90, "CHAI", "Rich warm hot chocolate."),
    # ---------------- LASSI & COLD DRINKS ----------------
    item("Traditional Sweet Lassi", 105, "COLD DRINKS", "Traditional sweetened yoghurt drink."),
    item("Mango Lassi", 110, "COLD DRINKS", "Thick mango and yoghurt drink."),
    item("Masala Chaas", 85, "COLD DRINKS", "Chilled spiced buttermilk."),
    item("Fresh Lime Soda", 75, "COLD DRINKS", "Fresh lime with soda, sweet or salted."),
    item("Lemon Iced Tea", 80, "COLD DRINKS", "Chilled lemon iced tea."),
    item("Soft Drink", 50, "COLD DRINKS", "Choice of soft drink."),
    item("Still / Sparkling Water", 25, "COLD DRINKS", "Still or sparkling water."),
    # ---------------- SIGNATURE ZERO-PROOF DRINKS ----------------
    item("Mango Maharaja", 129, "ZERO PROOF", "Mango, fresh lime and mint."),
    item("Masala Mojito", 129, "ZERO PROOF", "Fresh mint, lime, Indian spices and soda."),
    item("Sapa Berry Fizz", 129, "ZERO PROOF", "Mixed berries, citrus and sparkling soda."),
]

if __name__ == "__main__":
    with open("items.json", "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to items.json ({sum(1 for i in items if i['hero'])} heroes)")

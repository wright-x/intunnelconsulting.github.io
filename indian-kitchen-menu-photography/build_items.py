#!/usr/bin/env python3
"""Builds items.json for the SAPA PREMIUM INDIAN KITCHEN menu photo shoot.
White studio background for all photos so they can be cleanly cut out.
Plating is deliberately LESS elaborate than fine-dining — warm, comforting,
mountain-lodge home-style Indian food, simple honest garnish, not editorial."""
import json
import re

STYLE_SUFFIX = (
    "Warm, comforting home-style Indian restaurant food photography — "
    "natural and appetizing but simply, honestly plated rather than "
    "elaborate fine-dining: minimal garnish (at most a few fresh herb "
    "leaves, a lime wedge, or a light dusting of spice), no sauce "
    "artwork, no scattered edible flowers, no multi-element compositions. "
    "Bright, clean white studio background: seamless white backdrop, "
    "soft natural lighting, gentle soft shadow, elevated three-quarter "
    "angle looking down at the dish. Photorealistic, natural food "
    "texture, 2K quality. No text, no logos, no hands, no watermark, no "
    "restaurant background of any kind — pure white studio only."
)

DRINK_STYLE_SUFFIX = (
    "Warm, comforting home-style Indian restaurant beverage photography — "
    "simple, honest presentation, at most one small garnish. Bright, "
    "clean white studio background: seamless white backdrop, soft "
    "natural lighting, gentle shadow, straight-on eye-level angle. "
    "Photorealistic, natural condensation and ice clarity where "
    "relevant, 2K quality. No text, no logos, no hands, no watermark, no "
    "restaurant background of any kind — pure white studio only."
)

CATEGORY_VESSEL = {
    "BREAKFAST": "a simple round white ceramic plate",
    "WARMERS": "a simple white ceramic soup bowl with a small side handle",
    "MAGGI": "a simple round steel bowl with two small loop handles",
    "SMALL PLATES": "a simple round white ceramic plate",
    "TANDOOR VEG": "a simple dark steel plate resting on a wooden board",
    "TANDOOR NONVEG": "a simple dark steel plate resting on a wooden board",
    "DALS": "a simple steel karahi bowl resting on a wooden coaster",
    "VEG CURRIES": "a simple steel karahi bowl resting on a wooden coaster",
    "MEAT CURRIES": "a simple steel karahi bowl resting on a wooden coaster",
    "BREADS": "a simple round steel plate lined with a folded cloth",
    "RICE": "a simple round steel bowl",
    "BIRYANI": "a simple steel handi pot with its lid resting open beside it",
    "SWEETS": "a simple round white ceramic bowl",
    "CHAI": "a traditional clay kulhad cup",
    "COLD DRINKS": "a simple tall steel tumbler",
    "ZERO PROOF": "a simple tall clear glass over ice",
}


def slug(name):
    s = name.lower()
    s = re.sub(r"[()/&]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def item(name, price, category, description, veg=True, jain=False, spice=0, hero=False):
    drink = category in ("CHAI", "COLD DRINKS", "ZERO PROOF")
    vessel = CATEGORY_VESSEL[category]
    style = DRINK_STYLE_SUFFIX if drink else STYLE_SUFFIX
    prompt = (
        f"A simple, appetizing photograph of {name}: {description} Served in/on "
        f"{vessel}. {style}"
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
    item("Masala Maggi", 105, "MAGGI", "Classic Indian-style masala instant noodles.", hero=True),
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
    item("Paneer Tikka", 220, "TANDOOR VEG", "Paneer marinated in yoghurt and aromatic spices, grilled in the tandoor.", hero=True),
    item("Achari Paneer Tikka", 220, "TANDOOR VEG", "Paneer marinated with traditional Indian pickling spices.", spice=1),
    item("Mushroom Tikka", 190, "TANDOOR VEG", "Yoghurt-marinated mushrooms grilled until smoky and tender."),
    item("Vegetarian Tandoori Platter", 349, "TANDOOR VEG", "Paneer tikka, mushroom tikka and assorted vegetable kebabs."),
    # ---------------- FROM THE TANDOOR — NON-VEGETARIAN ----------------
    item("Chicken Tikka", 230, "TANDOOR NONVEG", "Boneless chicken marinated in yoghurt and Indian spices.", veg=False),
    item("Chicken Malai Tikka", 240, "TANDOOR NONVEG", "Creamy, delicately spiced chicken grilled until lightly charred.", veg=False, hero=True),
    item("Tandoori Chicken", 265, "TANDOOR NONVEG", "Half chicken marinated overnight and roasted in the tandoor.", veg=False),
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
    item("Mutton Rogan Josh", 299, "MEAT CURRIES", "Tender mutton slow-cooked in a fragrant Kashmiri-style gravy.", veg=False, spice=1),
    item("Traditional Mutton Curry", 289, "MEAT CURRIES", "Slow-cooked mutton in a rich North Indian onion and tomato masala.", veg=False, spice=2),
    item("Egg Curry", 175, "MEAT CURRIES", "Boiled eggs simmered in a traditional Indian curry.", veg=False),
    # ---------------- BREADS FROM THE TANDOOR ----------------
    item("Tandoori Roti", 55, "BREADS", "Whole-wheat flatbread baked in the tandoor."),
    item("Plain Naan", 75, "BREADS", "Classic soft tandoor-baked naan."),
    item("Butter Naan", 80, "BREADS", "Soft tandoor-baked naan finished with melted butter."),
    item("Garlic Naan", 85, "BREADS", "Soft tandoor-baked naan topped with fresh garlic and coriander."),
    item("Lachha Paratha", 80, "BREADS", "Flaky layered whole-wheat paratha."),
    item("Cheese Garlic Naan", 95, "BREADS", "Tandoor-baked naan topped with melted cheese and fresh garlic."),
    item("Chilli Cheese Naan", 95, "BREADS", "Tandoor-baked naan topped with melted cheese and green chilli.", spice=1),
    item("Stuffed Aloo Naan", 110, "BREADS", "Tandoor-baked naan stuffed with spiced potato."),
    item("Stuffed Paneer Naan", 145, "BREADS", "Tandoor-baked naan stuffed with seasoned cottage cheese."),
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
    item("Mutton Dum Biryani", 299, "BIRYANI", "Fragrant basmati rice, layered and slow-cooked with tender mutton.", veg=False),
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

#!/usr/bin/env python3
"""Precomputes per-page Canva layout: text/shape operations (ready to submit)
and image slots (need an uploaded asset_id before they become insert_fill
operations). Canvas is 794x1123 (A4 @ 96dpi), matching the live Canva design.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "menu_pages.json")) as f:
    PAGES = json.load(f)

W, H = 794, 1123
MARGIN = 48
INK = "#1A1714"
MUTED = "#5c564c"
FAINT = "#8a8377"
VEG_GREEN = "#4b7a4a"
SPICE_RED = "#b3402a"
HAIRLINE = "#d8d2c4"
CREAM = "#F6F3EC"

PAGE_ORDER_SLUGS = [
    "cover", "divider-small-plates", "small-plates-bar-bites-1",
    "small-plates-bar-bites-2", "small-plates-bar-bites-3",
    "chaat-fast-sellers-1", "chaat-fast-sellers-2", "divider-tandoor",
    "tandoor-grill-1", "tandoor-grill-2", "main-curries-1", "main-curries-2",
    "main-curries-3", "seafood-curries-1", "breads-1", "breads-2",
    "divider-rice", "rice-khichdi-1", "biryani-1", "divider-bar",
    "drinks-1", "coffee-1", "juices-smoothies-iced-tea-1",
    "juices-smoothies-iced-tea-2", "divider-desserts", "desserts-1", "closing",
]


def hline(page_id, top, left=MARGIN, width=W - 2 * MARGIN, color=HAIRLINE):
    return {"type": "insert_shape", "page_id": page_id, "top": top, "left": left,
            "width": width, "height": 1.5, "path": "M0,0 H%d V1.5 H0 Z" % width,
            "view_box_width": width, "view_box_height": 1.5, "color": color}


def rect(page_id, top, left, width, height, color, corner=0, stroke_color=None, stroke_weight=0):
    op = {"type": "insert_shape", "page_id": page_id, "top": top, "left": left,
          "width": width, "height": height,
          "path": "M0,0 H%d V%d H0 Z" % (width, height),
          "view_box_width": width, "view_box_height": height,
          "color": color, "corner_rounding": corner}
    if stroke_color:
        op["stroke_color"] = stroke_color
        op["stroke_weight"] = stroke_weight
    return op


def circle(page_id, top, left, d, color):
    r = d / 2
    path = f"M0,{r} A{r},{r} 0 1 1 {d},{r} A{r},{r} 0 1 1 0,{r} Z"
    return {"type": "insert_shape", "page_id": page_id, "top": top, "left": left,
            "width": d, "height": d, "path": path, "view_box_width": d,
            "view_box_height": d, "color": color}


def text(page_id, txt, top, left, width, size, color=INK, weight="normal",
          style="normal", align="start", line_height=1.3):
    return {"type": "add_text", "page_id": page_id, "text": txt, "top": top,
            "left": left, "width": width,
            "_format": {"font_size": size, "color": color, "font_weight": weight,
                        "font_style": style, "text_align": align,
                        "line_height": line_height}}


def build_header(page_id, title, tagline):
    ops = []
    # brand marks row (3 simple circle icons + labels)
    labels = ["Fresh Sourced", "Hand Crafted", "Made With Care"]
    for i, label in enumerate(labels):
        x = MARGIN + i * 90
        ops.append(circle(page_id, MARGIN, x, 22, "#FFFFFF"))
        ops.append(rect(page_id, MARGIN, x, 22, 22, "#FFFFFF", corner=11,
                         stroke_color=MUTED, stroke_weight=1.2))
        ops.append(text(page_id, label, MARGIN + 28, x - 10, 80, 7.5, color=MUTED,
                         align="center", line_height=1.1))
    ops.append(text(page_id, "THE THEATER — INDIAN KITCHEN & BAR", MARGIN,
                     W - MARGIN - 300, 300, 9.5, color=INK, weight="bold", align="end"))
    ops.append(text(page_id, title, MARGIN + 16, W - MARGIN - 350, 350, 22,
                     color=INK, weight="bold", align="end"))
    ops.append(hline(page_id, 108))
    ops.append(text(page_id, tagline, 116, MARGIN, 500, 11, color=MUTED,
                     style="italic"))
    return ops


def build_footer(page_id):
    ops = [hline(page_id, H - 56)]
    ops.append(text(page_id, "All prices are in thousand VND (d). VAT and "
                     "service charge is extra. Images are for "
                     "representation purposes only.", H - 48, MARGIN,
                     W - 2 * MARGIN, 7.5, color=FAINT, style="italic",
                     align="center"))
    return ops


def build_item_tags(page_id, item, top, left, width):
    """veg square + spice dots + optional chef badge label, returns (ops, extra_height)"""
    ops = []
    x = left
    if item["veg"]:
        ops.append(rect(page_id, top, x, 12, 12, CREAM, stroke_color=VEG_GREEN, stroke_weight=1.5))
        ops.append(text(page_id, "VEGETARIAN", top - 2, x + 16, 90, 7, color=VEG_GREEN, weight="bold"))
        x += 110
    if item["spice"] > 0:
        for i in range(item["spice"]):
            ops.append(circle(page_id, top + 1, x + i * 12, 10, SPICE_RED))
        x += item["spice"] * 12 + 8
    return ops


def build_content_page(page_id, page):
    ops = []
    cat = page["title"]
    tagline_map = {
        "Small Plates & Bar Bites": "Light, bold and made for sharing.",
        "Chaat & Fast Sellers": "India's most loved street food classics.",
        "Tandoor & Grill": "Fire-grilled flavors. Timeless indulgence.",
        "Main Curries": "Slow-cooked Indian classics prepared with rich spices.",
        "Seafood Curries": "Coastal Indian flavors with fresh seafood and aromatic spices.",
        "Breads": "Freshly baked in our tandoor; soft and made to perfection.",
        "Rice & Khichdi": "Fragrant basmati rice and traditional rice specialties.",
        "Biryani": "Traditional dum-cooked biryanis layered with aromatic spices.",
        "Drinks": "Refreshing beverages to complement your meal.",
        "Coffee": "Freshly brewed coffee crafted for every mood.",
        "Juices, Smoothies & Iced Tea": "Refreshing sips for every moment.",
        "Desserts": "The perfect finale to your meal.",
    }
    items = page["items"]
    title_text = cat.upper()
    ops += build_header(page_id, title_text, tagline_map.get(cat, ""))
    ops += build_footer(page_id)

    hero = items[0]
    secondary = items[1:]

    # hero block
    hero_top = 150
    photo_w = 300
    ops.append({"__image_slot__": True, "photo": hero["photo"], "page_id": page_id,
                "top": hero_top, "left": MARGIN, "width": photo_w})
    if hero.get("chef_recommended"):
        ops.append(rect(page_id, hero_top - 4, MARGIN - 4, 150, 24, "#1A1714", corner=12))
        ops.append(text(page_id, "CHEF'S RECOMMENDED", hero_top + 1, MARGIN + 2, 142, 8,
                         color="#FFFFFF", weight="bold", align="center"))
    text_x = MARGIN + photo_w + 24
    text_w = W - MARGIN - text_x
    ops.append(text(page_id, "1.", hero_top, text_x, 30, 20, color=FAINT))
    ops.append(text(page_id, hero["name"].upper(), hero_top + 2, text_x + 34, text_w - 34, 15,
                     color=INK, weight="bold"))
    ops.append(text(page_id, f"{hero['price_vnd_k']}K", hero_top + 2, text_x + 34, text_w - 34, 15,
                     color=INK, weight="bold", align="end"))
    ops.append(text(page_id, hero["description"], hero_top + 34, text_x + 34, text_w - 34, 10,
                     color=MUTED, line_height=1.35))
    ops += build_item_tags(page_id, hero, hero_top + 110, text_x + 34, text_w - 34)

    # secondary rows
    row_h = 128
    row_top0 = hero_top + 300
    photo_s = 96
    for i, it in enumerate(secondary):
        rt = row_top0 + i * row_h
        ops.append({"__image_slot__": True, "photo": it["photo"], "page_id": page_id,
                     "top": rt, "left": MARGIN, "width": photo_s, "height": photo_s})
        tx = MARGIN + photo_s + 20
        tw = W - MARGIN - tx
        ops.append(text(page_id, f"{i + 2}.", rt, tx, 20, 12, color=FAINT))
        ops.append(text(page_id, it["name"].upper(), rt, tx + 26, tw - 90, 12.5,
                         color=INK, weight="bold"))
        ops.append(text(page_id, f"{it['price_vnd_k']}K", rt, tx + tw - 60, 60, 12.5,
                         color=INK, weight="bold", align="end"))
        ops.append(text(page_id, it["description"], rt + 22, tx + 26, tw - 30, 9,
                         color=MUTED, line_height=1.3))
        ops += build_item_tags(page_id, it, rt + 66, tx + 26, tw - 30)

    return ops


HERO_TITLES = {
    "cover": None,  # handled specially
    "divider-small-plates": "SMALL PLATES, BAR BITES & CHAAT",
    "divider-tandoor": "TANDOOR, GRILL & MAIN CURRIES",
    "divider-rice": "RICE, KHICHDI & BIRYANI",
    "divider-bar": "DRINKS, COFFEE & JUICES",
    "divider-desserts": "DESSERTS",
    "closing": None,  # handled specially
}


def build_divider_page(page_id, slug):
    ops = [rect(page_id, 0, 0, W, H, CREAM)]
    label = HERO_TITLES[slug]
    ops.append({"__image_slot__": True, "photo": f"__HERO_BG__:{slug}", "page_id": page_id,
                "top": 0, "left": 0, "width": W, "height": H})
    ops.append(rect(page_id, H - 90, 0, W, 90, "#1A1714", corner=0))
    ops.append(text(page_id, label, H - 66, MARGIN, W - 2 * MARGIN, 16, color="#FFFFFF",
                     weight="bold", align="center"))
    return ops


def build_cover_page(page_id):
    ops = [rect(page_id, 0, 0, W, H, CREAM)]
    ops.append(text(page_id, "THE THEATER", 90, 0, W, 40, color=INK, weight="bold", align="center"))
    ops.append(text(page_id, "INDIAN KITCHEN & BAR", 148, 0, W, 13, color=INK, align="center"))
    ops.append(text(page_id, "Duong Dong, Phu Quoc", 178, 0, W, 12, color=MUTED, style="italic", align="center"))
    ops.append({"__image_slot__": True, "photo": "__HERO_BG__:cover", "page_id": page_id,
                "top": 220, "left": MARGIN, "width": W - 2 * MARGIN, "height": H - 220 - MARGIN})
    return ops


def build_closing_page(page_id):
    ops = [rect(page_id, 0, 0, W, H, CREAM)]
    ops.append(text(page_id, "DHANYAWAD", 90, 0, W, 34, color=INK, weight="bold", align="center"))
    ops.append(text(page_id, "Thank you for dining with us.", 138, 0, W, 13,
                     color=MUTED, style="italic", align="center"))
    ops.append({"__image_slot__": True, "photo": "__HERO_BG__:closing", "page_id": page_id,
                "top": 180, "left": W / 2 - 200, "width": 400, "height": 420})
    ops.append(text(page_id, "THE THEATER", 630, 0, W, 20, color=INK, weight="bold", align="center"))
    ops.append(text(page_id, "INDIAN KITCHEN & BAR", 656, 0, W, 11, color=INK, align="center"))
    ops.append(text(page_id, "152 Duong Tran Hung Dao, Duong Dong, Phu Quoc", 690, 0, W, 10,
                     color=MUTED, align="center"))
    return ops


def build_all(page_id_map):
    """page_id_map: slug -> canva page_id"""
    all_ops = {}
    for p in PAGES:
        slug = p["slug"]
        pid = page_id_map[slug]
        if slug == "cover":
            all_ops[slug] = build_cover_page(pid)
        elif slug == "closing":
            all_ops[slug] = build_closing_page(pid)
        elif p["type"] == "hero":
            all_ops[slug] = build_divider_page(pid, slug)
        else:
            all_ops[slug] = build_content_page(pid, p)
    return all_ops


if __name__ == "__main__":
    # smoke test with fake page ids
    fake_map = {s: f"PAGE_{s}" for s in PAGE_ORDER_SLUGS}
    all_ops = build_all(fake_map)
    for slug, ops in all_ops.items():
        n_img = sum(1 for o in ops if o.get("__image_slot__"))
        n_other = len(ops) - n_img
        print(f"{slug}: {n_other} shape/text ops, {n_img} image slots")

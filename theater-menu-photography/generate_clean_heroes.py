#!/usr/bin/env python3
"""Generates clean (no baked-in text) hero/divider background photos for the
Canva rebuild, where text will be added as real Canva text elements instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_images as g

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "canva_hero_photos")
os.makedirs(OUT, exist_ok=True)

STYLE = (
    "Bright, premium, LIGHT and WHITE studio background: clean warm marble "
    "or paper-toned seamless backdrop, soft even studio lighting, minimal "
    "soft shadow, high-end editorial food/product photography look. "
    "Shallow depth of field. No text, no logos, no watermarks, no hands, "
    "no UI elements of any kind. Photorealistic, ultra-detailed, 2K quality."
)

PROMPTS = {
    "cover": (
        "An elegant overhead flat-lay of aromatic Indian spices (star anise, "
        "cinnamon sticks, cardamom pods, dried red chilies, coriander seeds, "
        "saffron threads, cloves) scattered artfully on a warm marble "
        "surface with soft directional light and gentle shadow. " + STYLE
    ),
    "divider-small-plates": (
        "A close-up of golden crispy fried Indian snacks and small plates "
        "being plated, steam and texture visible, shallow depth of field, "
        "shot on a warm marble surface. " + STYLE
    ),
    "divider-tandoor": (
        "Glowing charcoal embers inside a traditional clay tandoor oven "
        "with a skewer of char-grilled tikka just visible at the edge of "
        "frame, warm dramatic light, shallow depth of field. " + STYLE
    ),
    "divider-rice": (
        "A dramatic close-up of fragrant basmati biryani rice being served "
        "from a hammered copper handi with steam rising, on a warm marble "
        "surface. " + STYLE
    ),
    "divider-bar": (
        "An elegant flat-lay of drink glassware — a copper mug, a tall "
        "glass of iced lassi, fresh mint and citrus — on a warm marble "
        "surface with soft light. " + STYLE
    ),
    "divider-desserts": (
        "A close-up of glossy gulab jamun in saffron syrup with a scoop of "
        "vanilla ice cream, soft bright light, shallow depth of field, on a "
        "warm marble surface. " + STYLE
    ),
    "closing": (
        "A softly lit photograph of an empty premium restaurant table "
        "setting — folded linen napkin, cutlery, a single small candle "
        "lantern — on a warm marble surface. " + STYLE
    ),
}

if __name__ == "__main__":
    for slug, prompt in PROMPTS.items():
        filepath = os.path.join(OUT, f"{slug}.png")
        print(f"Generating {slug}...", flush=True)
        img_bytes, err = g.call_gemini(prompt, None, max_retries=4)
        if img_bytes is None:
            print(f"  FAILED: {err}", flush=True)
            continue
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        from PIL import Image
        with Image.open(filepath) as im:
            print(f"  Saved {slug}.png {im.size}", flush=True)

#!/usr/bin/env python3
"""Given a page slug + canva page_id + asset_id map, prints the batch1 ops
(shapes+images+unformatted text) and, separately, expects text_ids captured
from the batch1 response to be piped in later to produce format ops.
Usage:
  python3 canva_prep_page.py batch1 <slug> <page_id> <assets.json>
  python3 canva_prep_page.py format <slug> <text_ids.txt>
"""
import json
import sys
import canva_layout as cl


def get_page(slug):
    return next(p for p in cl.PAGES if p["slug"] == slug)


def photo_key(path):
    return path.replace(
        "/home/user/intunnelconsulting.github.io/theater-menu-photography/", "")


def batch1(slug, page_id, assets_path):
    page = get_page(slug)
    assets = json.load(open(assets_path))
    ops = cl.build_content_page(page_id, page)
    out = []
    formats = []
    for o in ops:
        if o.get("__image_slot__"):
            key = photo_key(o["photo"])
            asset_id = assets[key]
            h = o.get("height", o["width"])
            out.append({"type": "insert_fill", "page_id": o["page_id"],
                        "asset_type": "image", "asset_id": asset_id,
                        "alt_text": "dish photo", "top": o["top"],
                        "left": o["left"], "width": o["width"], "height": h})
        elif o["type"] == "add_text":
            fmt = o.pop("_format")
            formats.append(fmt)
            out.append(o)
        else:
            out.append(o)
    print(json.dumps(out))
    with open(f"/tmp/{slug}_formats.json", "w") as f:
        json.dump(formats, f)
    sys.stderr.write(f"{len(out)} ops, {len(formats)} text elements to format\n")


def format_ops(slug, text_ids_path):
    ids = [l.strip() for l in open(text_ids_path) if l.strip()]
    formats = json.load(open(f"/tmp/{slug}_formats.json"))
    assert len(ids) == len(formats), (len(ids), len(formats), "mismatch")
    ops = [{"type": "format_text", "element_id": i, "formatting": f}
           for i, f in zip(ids, formats)]
    print(json.dumps(ops))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "batch1":
        batch1(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "format":
        format_ops(sys.argv[2], sys.argv[3])
    elif cmd == "photos":
        # list dish photo paths needed for a page, for upload staging
        page = get_page(sys.argv[2])
        for it in page["items"]:
            print(photo_key(it["photo"]))

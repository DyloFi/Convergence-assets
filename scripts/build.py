#!/usr/bin/env python3
"""Rebuild every derived asset from masters/ and crops/.
Usage: python3 scripts/build.py   (needs: pip install pillow vtracer)
Never hand-edit web/, social/ or svg/ - rerun this instead."""
import json, os, re
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
MASTERS, CROPS = ROOT / "masters", ROOT / "crops"
WEB, SOCIAL, SVG = ROOT / "web", ROOT / "social", ROOT / "svg"
WIDTHS = [480, 960, 1600]
for d in (WEB, SOCIAL, SVG):
    d.mkdir(exist_ok=True)

REPORT = [  # filename prefix -> report it belongs to
    ("fourth-turning", "4th Turning"), ("sheet-changing-world-orders", "Changing World Orders"),
    ("world-orders", "Changing World Orders"), ("worldorders", "Changing World Orders"),
    ("sheet-kondratiev", "Kondratiev Waves"), ("kondratiev", "Kondratiev Waves"), ("waves", "Kondratiev Waves"),
    ("sheet-law-of", "LoAR"), ("loar", "LoAR"), ("acceleration", "LoAR"),
    ("technological-singularity", "Technological Singularity"), ("singularity", "Technological Singularity"),
    ("master-synthesis", "Master Synthesis"), ("sheet-observer", "Observer Effect"), ("observer", "Observer Effect"),
    ("sheet-chainlink", "Chainlink"), ("protocol", "Chainlink"), ("cube", "Chainlink"),
]
def report_for(name):
    for p, r in REPORT:
        if name.startswith(p):
            return r
    return "Unassigned"

def role_for(name, src):
    for r in ("hero", "banner", "strip", "vignette", "icon", "chart", "diagram", "map", "logo", "figure"):
        if r in name:
            return r
    return "sheet" if name.startswith("sheet-") else ("hero" if src == "masters" else "detail")

def alt_for(name):
    return re.sub(r"[-_]+", " ", name).replace(" clean", "").strip().capitalize() + ", monochrome retro-futurist pencil concept art"

def web_sizes(img, stem):
    out = []
    for w in WIDTHS:
        if img.width < w and w != WIDTHS[0]:
            continue
        im = img if img.width <= w else img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        p = WEB / f"{stem}-{im.width}.webp"
        if not p.exists():
            im.convert("RGB").save(p, "WEBP", quality=82, method=6)
        out.append(str(p.relative_to(ROOT)))
    return out

def social_card(img, stem):
    p = SOCIAL / f"{stem}-og.jpg"
    if not p.exists():
        ImageOps.fit(img.convert("RGB"), (1200, 630), Image.LANCZOS, centering=(0.5, 0.4)).save(p, "JPEG", quality=85)
    return str(p.relative_to(ROOT))

def trace_svg(img, stem):
    """Icons and logos only: threshold to clean black line art, then vector-trace."""
    import vtracer
    p = SVG / f"{stem}.svg"
    if p.exists():
        return str(p.relative_to(ROOT))
    g = ImageOps.grayscale(img)
    scale = max(1, 512 // max(g.size))
    g = g.resize((g.width * scale, g.height * scale), Image.LANCZOS).filter(ImageFilter.MedianFilter(3))
    bw = g.point(lambda v: 0 if v < 150 else 255).convert("RGB")
    tmp = SVG / f".{stem}.png"
    bw.save(tmp)
    vtracer.convert_image_to_svg_py(str(tmp), str(p), colormode="binary", filter_speckle=6,
                                    corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=2)
    tmp.unlink()
    s = p.read_text()  # black strokes -> currentColor so CSS can recolour buttons
    p.write_text(s.replace('fill="#000000"', 'fill="currentColor"').replace('fill="#000"', 'fill="currentColor"'))
    return str(p.relative_to(ROOT))

manifest = []
for src in ("masters", "crops"):
    for f in sorted((ROOT / src).glob("*.png")):
        stem, img = f.stem, Image.open(f)
        role = role_for(stem, src)
        e = {"id": stem, "report": report_for(stem), "role": role, "source": f"{src}/{f.name}",
             "size": [img.width, img.height], "alt": alt_for(stem), "web": web_sizes(img, stem)}
        if src == "masters" and not stem.startswith("sheet-"):
            e["social"] = social_card(img, stem)
        if role in ("icon", "logo") and not stem.endswith("s-icons"):  # strips of many tiny icons trace badly
            e["svg"] = trace_svg(img, stem)
        manifest.append(e)

(ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"{len(manifest)} assets, {sum(len(e['web']) for e in manifest)} web files, "
      f"{sum('svg' in e for e in manifest)} svgs, {sum('social' in e for e in manifest)} social cards")

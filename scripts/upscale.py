#!/usr/bin/env python3
"""Real-ESRGAN x4plus upscale of small crops and sub-1536 heroes into upscaled/ (originals untouched).
Usage: python3 scripts/upscale.py MODEL.pth   (pip install torch spandrel pillow)"""
import sys, torch, numpy as np
from pathlib import Path
from PIL import Image
from spandrel import ModelLoader
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "upscaled"; OUT.mkdir(exist_ok=True)
model = ModelLoader().load_from_file(sys.argv[1]).eval()
torch.set_num_threads(2)
TARGET = 1600  # don't go past this width

def up(img):
    x = torch.from_numpy(np.asarray(img.convert("RGB"), dtype=np.float32) / 255).permute(2, 0, 1)[None]
    tile, pad, s = 256, 16, 4
    _, _, h, w = x.shape
    out = torch.zeros(1, 3, h * s, w * s)
    with torch.no_grad():
        for y0 in range(0, h, tile):
            for x0 in range(0, w, tile):
                ya, yb = max(0, y0 - pad), min(h, y0 + tile + pad)
                xa, xb = max(0, x0 - pad), min(w, x0 + tile + pad)
                r = model(x[:, :, ya:yb, xa:xb])
                ty, tx = (y0 - ya) * s, (x0 - xa) * s
                th, tw = (min(h, y0 + tile) - y0) * s, (min(w, x0 + tile) - x0) * s
                out[:, :, y0*s:y0*s+th, x0*s:x0*s+tw] = r[:, :, ty:ty+th, tx:tx+tw]
    a = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(a).convert("L").convert("RGB")  # keep it strictly monochrome

dirs = sys.argv[2:] or ["crops", "masters"]
files = [f for d in dirs for f in sorted((ROOT / d).glob("*.png"))]
for f in files:
    o = OUT / f.name
    img = Image.open(f)
    if o.exists() or img.width >= 1536 or f.stem.startswith("sheet-"):
        continue
    src = img if img.width < 400 else img.resize((img.width // 2, img.height // 2), Image.LANCZOS)  # big ones: 2x net, 4x faster
    r = up(src)
    if r.width > TARGET:
        r = r.resize((TARGET, round(r.height * TARGET / r.width)), Image.LANCZOS)
    # blend 65% ESRGAN with 35% plain Lanczos so the pencil grain survives
    soft = img.convert("L").convert("RGB").resize(r.size, Image.LANCZOS)
    r = Image.blend(soft, r, 0.65).convert("L")
    r.save(o, optimize=True)
    print(f.name, img.size, "->", r.size, flush=True)

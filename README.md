# Convergence Assets

Art library for the Convergence research reports. Monochrome retro-futurist pencil concept art, GPT Image 2.

| Folder | What | Edit? |
|---|---|---|
| `masters/` | Full-res originals: `sheet-*` concept sheets, `*-clean` cleaned heroes, single report heroes | Never. Add only |
| `crops/` | Pieces cut from the sheets (heroes, banners, vignettes, icons, charts) | Add only |
| `web/` | WebP at 480/960/1600 px wide (only sizes up to the source width) | Generated |
| `social/` | 1200x630 share cards for every hero | Generated |
| `svg/` | Vector-traced icons and logos, `fill="currentColor"` so CSS sets the colour | Generated |
| `manifest.json` | One entry per asset: report, role, sizes, alt text, file paths | Generated |

Rebuild everything after adding art:

```bash
pip install pillow vtracer
python3 scripts/build.py
```

## Using on the site

```html
<img src="web/kondratiev-sixth-wave-960.webp"
     srcset="web/kondratiev-sixth-wave-480.webp 480w, web/kondratiev-sixth-wave-960.webp 960w, web/kondratiev-sixth-wave-1536.webp 1536w"
     sizes="(max-width: 700px) 100vw, 960px" alt="Kondratiev sixth wave, monochrome retro-futurist pencil concept art">
<meta property="og:image" content="social/kondratiev-sixth-wave-og.jpg">
<button class="icon"><img src="svg/protocol-logo.svg" alt=""> Chainlink</button>
```

Inline an SVG (rather than `<img>`) when you want `currentColor` to follow text colour or hover states.

## Naming

`<report-subject>-<role>[-variant].png`, e.g. `world-orders-reserve-currency.png`, `waves-icon-train.png`.

## Known fixes needed

- `master-synthesis.png` labels Dalio's Big Cycle ~250-400 yrs; should be ~100-250 (v2 is correct).
- `fourth-turning-archetypes.png` wheel shows the four turnings out of sequence.

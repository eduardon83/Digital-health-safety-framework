"""Render the HDSF brand PNGs from brand/svg with a headless browser (Playwright and Chromium).

  pip install playwright && python3 -m playwright install chromium
  python3 tooling/make_brand_png.py

Writes brand/png/* and the site icons in docs/ (favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png,
social-preview.png). Run it after changing tooling/brand.py and commit the results. Licence: Apache-2.0
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG, PNG, DOCS = ROOT / "brand" / "svg", ROOT / "brand" / "png", ROOT / "docs"
JOBS = [("hdsf-icon-on-light.svg", "hdsf-icon-32.png", 32, 32), ("hdsf-icon-on-light.svg", "hdsf-icon-180.png", 180, 180),
        ("hdsf-icon-on-light.svg", "hdsf-icon-192.png", 192, 192), ("hdsf-icon-on-light.svg", "hdsf-icon-512.png", 512, 512),
        ("hdsf-icon-on-dark.svg", "hdsf-icon-on-dark-512.png", 512, 512),
        ("hdsf-lockup-on-light.svg", "hdsf-lockup-on-light.png", 1040, 240), ("hdsf-lockup-on-dark.svg", "hdsf-lockup-on-dark.png", 1040, 240),
        ("hdsf-social-preview-on-light.svg", "hdsf-social-preview-on-light.png", 1280, 640),
        ("hdsf-social-preview-on-dark.svg", "hdsf-social-preview-on-dark.png", 1280, 640)]
SITE = {"hdsf-icon-32.png": "favicon-32.png", "hdsf-icon-180.png": "apple-touch-icon.png", "hdsf-icon-192.png": "icon-192.png",
        "hdsf-icon-512.png": "icon-512.png", "hdsf-social-preview-on-light.png": "social-preview.png"}


def main() -> int:
    from playwright.sync_api import sync_playwright
    PNG.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for src, dst, w, h in JOBS:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            svg = (SVG / src).read_text(encoding="utf-8")
            pg.set_content(f'<html><body style="margin:0;background:transparent">'
                           f'<div style="width:{w}px;height:{h}px">{svg.replace("<svg ", f"<svg style=\"width:{w}px;height:{h}px\" ", 1)}</div></body></html>')
            pg.screenshot(path=str(PNG / dst), omit_background=True, clip={"x": 0, "y": 0, "width": w, "height": h})
            pg.close()
        b.close()
    for src, dst in SITE.items():
        shutil.copy(PNG / src, DOCS / dst)
    print(f"{len(JOBS)} PNG files in brand/png; site icons copied to docs/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""HDSF brand: the shield mark (a shield holding a plus of rounded blocks), colours and logo files.

The mark is drawn here once. build.py writes the SVG files in brand/svg and an inline, themable copy into every
site page; tooling/make_brand_png.py renders the PNGs (favicons, social preview) with a headless browser.
Licence of the logo files: CC BY 4.0, as the rest of the content. Licence of this code: Apache-2.0
"""
from __future__ import annotations

NAME = "Health Data Safety Framework"
TAGLINE = "Open, checkable rules for digital health products in the EU"

LIGHT = {"bg": "#fbfcfc", "ink": "#12232e", "muted": "#4b5d68", "teal": "#0f6e6e", "sky": "#5DA9DD", "indigo": "#4A5FC1",
         "lilac": "#9A7AD0", "coral": "#E2674A", "line": "#d9e2e6"}
DARK = {"bg": "#0f1a20", "ink": "#e6eef0", "muted": "#a6b8c0", "teal": "#3fb8a8", "sky": "#5DA9DD", "indigo": "#8A9BEA",
        "lilac": "#B59BE6", "coral": "#E2674A", "line": "#2a3d47"}


def mark_shapes(c: dict) -> str:
    """The mark in a 100 x 110 box. c maps ink, teal, sky, indigo, lilac and coral to colours or CSS var() values."""
    sq = lambda x, y, col: f'<rect x="{x}" y="{y}" width="16" height="16" rx="4" fill="{col}"/>'  # noqa: E731
    return (f'<path d="M50 6 L90 20 V52 C90 78 72 96 50 104 C28 96 10 78 10 52 V20 Z" fill="none" stroke="{c["ink"]}" '
            f'stroke-width="7" stroke-linejoin="round"/>'
            + sq(42, 26, c["teal"]) + sq(24, 44, c["sky"]) + sq(60, 44, c["indigo"]) + sq(42, 62, c["lilac"])
            + f'<circle cx="50" cy="52" r="8" fill="{c["coral"]}"/>')


def svg_mark(c: dict, size: int = 110) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size * 100 // 110}" height="{size}" viewBox="0 0 100 110" '
            f'role="img" aria-label="HDSF"><title>HDSF</title>{mark_shapes(c)}</svg>\n')


def svg_icon(c: dict) -> str:
    """Square app icon and favicon: the mark on a rounded tile."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="HDSF">'
            f'<title>HDSF</title><rect width="512" height="512" rx="112" fill="{c["bg"]}"/>'
            f'<g transform="translate(96 72) scale(3.2)">{mark_shapes(c)}</g></svg>\n')


def svg_lockup(c: dict) -> str:
    """Mark, HDSF wordmark and full name, side by side."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="120" viewBox="0 0 520 120" role="img" aria-label="HDSF, {NAME}">'
            f'<title>HDSF, {NAME}</title><g transform="translate(4 5)">{mark_shapes(c)}</g>'
            f'<text x="124" y="66" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-weight="700" '
            f'font-size="52" letter-spacing="2" fill="{c["ink"]}">HD<tspan fill="{c["teal"]}">SF</tspan></text>'
            f'<text x="126" y="98" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="20" '
            f'fill="{c["muted"]}">{NAME}</text></svg>\n')


def svg_social(c: dict) -> str:
    """Social preview, 1280 x 640 (GitHub and link previews)."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-label="HDSF, {NAME}">'
            f'<title>HDSF, {NAME}</title><rect width="1280" height="640" fill="{c["bg"]}"/>'
            f'<rect x="0" y="0" width="1280" height="14" fill="{c["teal"]}"/>'
            f'<g transform="translate(110 150) scale(3.1)">{mark_shapes(c)}</g>'
            f'<text x="510" y="300" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-weight="700" '
            f'font-size="132" letter-spacing="6" fill="{c["ink"]}">HD<tspan fill="{c["teal"]}">SF</tspan></text>'
            f'<text x="514" y="370" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="42" '
            f'fill="{c["ink"]}">{NAME}</text>'
            f'<text x="514" y="440" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="28" '
            f'fill="{c["muted"]}"><tspan x="514">Open, checkable rules for digital health</tspan><tspan x="514" dy="40">products in the EU</tspan></text>'
            f'<text x="514" y="560" font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="26" '
            f'fill="{c["teal"]}">hdsf.kendirstudios.pt</text></svg>\n')


# Inline mark for site pages: colours follow the page's CSS variables, so it switches with dark mode.
THEMED = {"ink": "var(--ink)", "teal": "var(--teal)", "sky": "var(--sky)", "indigo": "var(--indigo)",
          "lilac": "var(--lilac)", "coral": "var(--coral)"}


def inline_mark(height: int = 30) -> str:
    return (f'<svg width="{height * 100 // 110}" height="{height}" viewBox="0 0 100 110" aria-hidden="true" focusable="false">'
            f'{mark_shapes(THEMED)}</svg>')


def files() -> dict[str, str]:
    out = {}
    for mode, c in (("light", LIGHT), ("dark", DARK)):
        on = "on-light" if mode == "light" else "on-dark"
        out[f"hdsf-mark-{on}.svg"] = svg_mark(c)
        out[f"hdsf-icon-{on}.svg"] = svg_icon(c)
        out[f"hdsf-lockup-{on}.svg"] = svg_lockup(c)
        out[f"hdsf-social-preview-{on}.svg"] = svg_social(c)
    return out

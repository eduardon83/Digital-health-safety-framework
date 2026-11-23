# HDSF brand

The mark is a shield holding a plus of rounded blocks. The shield stands for data safety, the plus for health. The
rounded blocks and the colours come from the CSEF family, so the two frameworks read as siblings.

| File | Use |
|---|---|
| `svg/hdsf-mark-on-light.svg`, `svg/hdsf-mark-on-dark.svg` | The mark alone |
| `svg/hdsf-lockup-on-light.svg`, `svg/hdsf-lockup-on-dark.svg` | Mark, HDSF wordmark and full name |
| `svg/hdsf-icon-on-light.svg`, `svg/hdsf-icon-on-dark.svg` | App icon and favicon (mark on a rounded tile) |
| `svg/hdsf-social-preview-on-light.svg`, `-on-dark.svg` | Link previews and the GitHub social preview (1280 x 640) |
| `png/` | PNG renders of the above: icons at 32, 180, 192 and 512 px, lockups, social previews |

## Colours

| Name | Light | Dark |
|---|---|---|
| Ink | `#12232e` | `#e6eef0` |
| Teal | `#0f6e6e` | `#3fb8a8` |
| Sky | `#5DA9DD` | `#5DA9DD` |
| Indigo | `#4A5FC1` | `#8A9BEA` |
| Lilac | `#9A7AD0` | `#B59BE6` |
| Coral | `#E2674A` | `#E2674A` |
| Paper | `#fbfcfc` | `#0f1a20` |

Wordmark: "HD" in ink, "SF" in teal, Inter bold.

## Changing it

The mark is drawn once in `tooling/brand.py`. `python3 tooling/build.py` writes the SVG files and the inline mark on
every site page; `python3 tooling/make_brand_png.py` renders the PNGs. Licence: CC BY 4.0.

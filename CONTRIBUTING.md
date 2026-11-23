# Contributing to HDSF

Thank you for helping. The most useful contributions right now:

1. **Verify a source.** `framework/legislation.md` lists sources marked `verified: pending`. Check one against the
   official text, fix its status and url in `framework/sources.yaml`, set `verified` to today's date.
2. **Country packs.** Add your country as `packs/<code>.yaml` (start from `packs/_template.yaml`, see
   [framework/04-packs.md](framework/04-packs.md)): health information law, authorities, helplines, app assessment schemes.
3. **Real cases.** Tell us where a rule was wrong, unclear or missing for a real product.

## How

- Edit `framework/rules.yaml`, `framework/sources.yaml` or `framework/watch.yaml`, then run
  `python3 tooling/build.py`. Never edit generated files by hand; CI checks them.
- Run `python3 -m pytest -q`.
- Follow [STYLE.md](STYLE.md) and the [glossary](framework/glossary.md). Run `python3 tooling/stylecheck.py`.
- Every rule needs a source; every source needs a date in its status.
- The engine (`engine/sfe`) lives in the CSEF repository; change it there.

By contributing you agree that your contribution is licensed under the licences in `LICENSE`.

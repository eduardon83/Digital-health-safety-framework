<img src="brand/svg/hdsf-lockup-on-light.svg" alt="HDSF, Health Data Safety Framework" width="360">

# Health Data Safety Framework (HDSF)

Open, checkable rules for digital health products in the European Union: wellness and lifestyle apps, medical device
software, electronic health record systems, research platforms and telehealth.

> **Status:** v0.3.1, draft for public comment (November 2026). Not legal or regulatory advice.

Digital health sits where the GDPR (RGPD), the MDR and IVDR, the European Health Data Space, the AI Act, the Cyber
Resilience Act, NIS2, the Data Act and the new Product Liability Directive meet. HDSF puts what they ask of a product
in one place, with sources and dates. It also checks what can be checked.

## What you get

| Part | What it is |
|---|---|
| **Rules** | 94 rules on three levels (law; EU recommendations; research on design and UX) in [framework/catalogue/](framework/catalogue/index.md). Each says what to do, why (with sources), how to improve, the effort and how it is checked. |
| **The device question** | [framework/02-qualification.md](framework/02-qualification.md): is your software a medical device? Everything else depends on it. |
| **Regulatory map** | [framework/01-regulatory-map.md](framework/01-regulatory-map.md): which law applies to which product, from when. Portugal included. |
| **Manifest** | [templates/hdsf.yaml](templates/hdsf.yaml): the product on one page: intended purpose, qualification, data flows, documents. |
| **Workbench** | <https://hdsf.kendirstudios.pt/workbench/>: for designers, decision makers and researchers. Describe the product, add documents, get checks, a document review, design recommendations and reports. No code; nothing uploaded. |
| **GDPR (RGPD) map** | [framework/gdpr-map.md](framework/gdpr-map.md): each article and the rules that apply it. |
| **Scanner** | `tooling/scan.py`: reads the manifest and the code; Markdown, JSON and SARIF; `--docs` adds the document review (`tooling/docreview.py`); `--export html,pdf,docx` writes an interactive dashboard, PDF and Word (`tooling/export.py`). |
| **Checklists** | [self-assessment/](self-assessment/core.md): tick by hand, per profile and level. |
| **Packs** | [framework/04-packs.md](framework/04-packs.md): the Portugal pack (loads when `countries` lists PT), the ACME company pack example and a template. |
| **Sources** | [framework/legislation.md](framework/legislation.md): 61 sources with status, date and verification. |
| **Claude skill** | `skill/hdsf-review/`: runs the scan with you and drafts missing documents. |

## Profiles and levels

Every product meets the **core** rules, then adds profiles: **W** wellness and lifestyle, **M** medical device
software, **E** EHR systems and the EHDS, **R** research and secondary use, **T** telehealth and care delivery.

Levels: **1** law (meet now); **2** EU recommendations and forward compliance (EDPB, Commission, WHO, standards; EHDS,
CRA and AI Act dates); **3** best practice from research on design, UX, aesthetics and evidence.

## Quick start

```bash
pip install pyyaml
cp templates/hdsf.yaml /path/to/your-product/hdsf.yaml     # then fill it in
python3 tooling/scan.py --repo /path/to/your-product --level 1 --out-dir hdsf-report --format md,json,sarif
```

Try the examples:

```bash
python3 tooling/scan.py --repo examples/noncompliant-app --level 2
python3 tooling/scan.py --repo examples/compliant-app --level 3
```

No code, only documents? Add `--description-only`. Details: [framework/03-using-hdsf.md](framework/03-using-hdsf.md).

## Children

Health products used by children also apply the [Child-Safe EdTech Framework (CSEF)](https://csef.kendirstudios.pt).
Both frameworks run on the same engine.

## Repository layout

```
framework/        framework.yaml, rules.yaml, sources.yaml, watch.yaml (sources of truth), guides, generated catalogue
                  and legislation.md
templates/        hdsf.yaml, hdsf-portugal.yaml, qualification record, DPIA outline
packs/            country packs (pt.yaml) and the pack template
self-assessment/  generated checklists
tooling/          scan.py, checks.py (manifest checks), docreview.py, export.py, workbench.py (+ page template), build.py,
                  sync_engine.py, generated Semgrep rules
engine/           pinned copy of the Safety Framework Engine (sfe) from CSEF, with ENGINE.lock
brand/            logo files and colours (brand/README.md)
skill/            hdsf-review skill for Claude (SKILL.md + generated copies)
examples/         compliant and non-compliant example apps (fictional)
tests/            test suite
docs/             website (generated)
```

Edit `framework/rules.yaml`, `framework/sources.yaml` or `framework/watch.yaml`, then run `python3 tooling/build.py`.
CI checks that generated files are up to date.

## Limitations

- Automated checks find signs. A person confirms them. A clean report does not mean a product is compliant.
- HDSF does not decide whether software is a medical device. That is the manufacturer's decision, often with a
  regulatory expert or a notified body.
- Some sources are marked `verified: pending`: written from the maintainers' knowledge and not yet checked against
  the official text in this version. Do not rely on them alone.
- EU-level first; national rules are notes, starting with Portugal.

## Contributing and licence

See [CONTRIBUTING.md](CONTRIBUTING.md) and the writing style in [STYLE.md](STYLE.md). Content CC BY 4.0, code Apache-2.0 ([LICENSE](LICENSE)). Maintained by Kendir
Studios (Worlds4Education, Lda.) with contributors.

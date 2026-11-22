# Health Data Safety Framework (HDSF)

Open, checkable rules for digital health products in the European Union: wellness and lifestyle apps, medical device
software, electronic health record systems, research platforms and telehealth.

> **Status:** v0.1.0, first draft for public comment (November 2026). Not legal or regulatory advice.

Digital health sits where the GDPR, the MDR and IVDR, the European Health Data Space, the AI Act, the Cyber
Resilience Act, NIS2, the Data Act and the new Product Liability Directive meet. HDSF puts what they ask of a product
in one place, with sources and dates, and checks what can be checked.

## What you get

| Part | What it is |
|---|---|
| **Rules** | 73 rules in [framework/catalogue/](framework/catalogue/index.md). Each says what to do, why (with sources), how to improve, the effort, and how it is checked. |
| **The device question** | [framework/02-qualification.md](framework/02-qualification.md): is your software a medical device? Everything else depends on it. |
| **Regulatory map** | [framework/01-regulatory-map.md](framework/01-regulatory-map.md): which law applies to which product, from when. Portugal included. |
| **Manifest** | [templates/hdsf.yaml](templates/hdsf.yaml): the product on one page: intended purpose, qualification, data flows, documents. |
| **Scanner** | `tooling/scan.py`: reads the manifest and the code; Markdown, JSON and SARIF reports. |
| **Checklists** | [self-assessment/](self-assessment/core.md): tick by hand, per profile and level. |
| **Sources** | [framework/legislation.md](framework/legislation.md): 44 sources with status, date and verification. |
| **Claude skill** | `skill/hdsf-review/`: runs the scan with you and drafts missing documents. |

## Profiles and levels

Every product meets the **core** rules, then adds profiles: **W** wellness and lifestyle, **M** medical device
software, **E** EHR systems and the EHDS, **R** research and secondary use, **T** telehealth and care delivery.

Levels: **1** legal baseline (meet now), **2** forward-compliant (EHDS, CRA and AI Act dates, guidance, standards),
**3** best practice.

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
templates/        hdsf.yaml, qualification record, DPIA outline
self-assessment/  generated checklists
tooling/          scan.py, checks.py (manifest checks), build.py, sync_engine.py, generated Semgrep rules
engine/           pinned copy of the Safety Framework Engine (sfe) from CSEF, with ENGINE.lock
skill/            hdsf-review skill for Claude (SKILL.md + generated copies)
examples/         compliant and non-compliant example apps (fictional)
tests/            test suite
docs/             website (generated)
```

Edit `framework/rules.yaml`, `framework/sources.yaml` or `framework/watch.yaml`, then run `python3 tooling/build.py`.
CI checks that generated files are up to date.

## Limitations

- Automated checks find signs, not proof. A clean report does not mean a product is compliant.
- HDSF does not decide whether software is a medical device. That is the manufacturer's decision, often with a
  regulatory expert or a notified body.
- Some sources are marked `verified: pending`: written from the maintainers' knowledge and not yet checked against
  the official text in this version. Do not rely on them alone.
- EU-level first; national rules are notes, starting with Portugal.

## Contributing and licence

See [CONTRIBUTING.md](CONTRIBUTING.md). Content CC BY 4.0, code Apache-2.0 ([LICENSE](LICENSE)). Maintained by Kendir
Studios (Worlds4Education, Lda.) with contributors.

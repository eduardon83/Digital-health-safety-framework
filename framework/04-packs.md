# Packs: countries, sectors and companies

HDSF covers EU law. Packs add the rest: national law, a health system's rules, research you want cited or your own
company's red lines. A pack can add sources and rules and make rules stricter. It can never weaken or remove a rule.

## The two packs that ship with HDSF

| Pack | File | How it loads | What it does |
|---|---|---|---|
| Portugal | [packs/pt.yaml](../packs/pt.yaml) ([rules](catalogue/pack-pt.md)) | By itself when `hdsf.yaml` lists `PT` in `countries` | Consent age 13; CNPD, INFARMED, CEIC and CNCS; 112 and SNS 24 in the urgent help route; information in Portuguese as a level 1 rule; texts in European Portuguese |
| ACME (example) | [examples/company-packs/acme.yaml](../examples/company-packs/acme.yaml) | Listed under `packs:` in `hdsf.yaml`, or `--pack` | Fictional company: minimum level 2; four no-go rules; forbidden packages and wording; decision records for AI and research; a review every 180 days; two ACME rules |

Start a new product in Portugal from [templates/hdsf-portugal.yaml](../templates/hdsf-portugal.yaml). In the
Workbench, use "Start from the Portugal template" and "Add the ACME company pack (example)".

## What a pack can contain

| Section | Use it for |
|---|---|
| `parameters` | Values shown in reports: consent age, authorities, helplines, language |
| `sources` | Laws, guidance, standards and research to cite |
| `rules` | New rules; ids start with the pack id in capitals (`PT-LNG-01`) |
| `amend` | Make an HDSF rule stricter: `add_sources`, `note`, `level` (SHOULD to MUST only), `tier` (a lower number only), `add_patterns` |
| `policy` | Company decisions: `minimum_level`, `no_go`, `forbid_dependencies`, `forbid_phrases`, `forbid_patterns`, `require_decision_for_features`, `review_every_days` |

A `policy` section creates rules named `<ID>-POL-01`, `-02` and so on, and a source `<ID>-POLICY`, so reports show
which findings come from your policy and which from law.

## Write your own

1. Copy [packs/_template.yaml](../packs/_template.yaml).
2. Give each source a type, a dated status, a link and a `verified` date (or `pending`).
3. Check it: `python3 tooling/build.py --validate-pack path/to/pack.yaml`.
4. Country packs go in `packs/<code>.yaml` in this repository; open a pull request with a note on who reviewed it.
   Company packs stay in your own repository, for example `.hdsf/packs/acme.yaml`.

Packs use the same engine as CSEF packs, so a company with products for children and health can keep the same
policy shape in both.

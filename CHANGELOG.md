# Changelog

Newest first. Open items and what we are watching: [legislation.md, watch list](framework/legislation.md#open-discussions-and-watch-list).

## v0.2.0 (2026-11-23)

- **Three layers, as in CSEF.** Level 1 law; level 2 EU recommendations and forward compliance; level 3 best practice from research.
  21 new rules (94 in total) and 17 new sources (61 in total).
- **GDPR (RGPD).** New rules for records of processing (Art. 30), automated decisions (Art. 22), roles and EU representatives
  (Art. 24 to 28), people's requests and complaints (Art. 12, 16, 18, 21, 77) and data protection by design (Art. 25). Every
  rule now lists the GDPR articles it applies, and a new [GDPR (RGPD) map](framework/gdpr-map.md) shows which rules cover each article.
- **Layer 2, EU recommendations:** EDPB Opinion 28/2024 on AI models, EDPB Guidelines 03/2026 on web scraping (draft) and on
  anonymisation (draft), 03/2022 on deceptive design, 05/2020 on consent and 4/2019 on data protection by design; WHO guidance on
  large multi-modal models; Commission Recommendation (EU) 2019/243 on the EHR exchange format; the Commission's clear writing
  guide and the Publications Office plain language and Easy-to-read guide; IEC 62366-1 usability engineering. New rules on AI
  built with personal data, scraped health data, testing AI with users, plain language, languages, health recommendations,
  deceptive consent design, the EHR exchange format and usability engineering.
- **Layer 3, research on design, UX and aesthetics:** MARS (app quality), icon arrays for risk (Galesic 2009), consent design
  (Nouwens 2020), aesthetics and perceived usability (Tractinsky 2000), health literacy in Europe (HLS-EU 2015), NICE evidence
  standards. New rules on risk numbers, equal consent choices, calm and honest visual design, quality rating, inclusive testing,
  no guilt or fear mechanics, and evidence plans.
- **Workbench** ([hdsf.kendirstudios.pt/workbench](https://hdsf.kendirstudios.pt/workbench/)): for designers, decision makers and
  researchers. Describe the product in a form, add documents (PDF, Word, Markdown, text, HTML), and get the description check, a
  document review, EU recommendations and design recommendations, with reports. Runs in the browser; nothing is uploaded. Same
  engine on a computer: `tooling/workbench.py`.
- **Document review** (`tooling/docreview.py`): privacy notice against GDPR (RGPD) Art. 13 and 14; medical claims; urgent help and
  AI wording; readability and medical terms (English and Portuguese); confirmshaming, false urgency, guilt, fear, pre-selected
  consent, percentage-only risks, notifications that reveal health.
- **Exports, as in CSEF:** interactive HTML dashboard (search, filters, print), PDF and Word, from `tooling/scan.py --export` or
  `tooling/export.py`. Built on the shared engine (sfe 0.2.0, new `export` module).

## v0.1.0 (2026-11-22)

First public draft.

- 73 rules: 44 core, plus profiles W wellness and lifestyle (8), M medical device software (10), E EHR systems and
  the EHDS (6), R research and secondary use (5), T telehealth and care delivery (5); some rules sit in two profiles. Three levels: legal baseline, forward-compliant,
  best practice. Rules scope by users (public, patients, professionals, children) and features.
- 44 sources: GDPR and CJEU case law (Lindenapotheke, SRB), ePrivacy, DSA, EHDS, MDR, IVDR, MDCG 2019-11 rev. 1,
  2025-4, 2025-6 and 2020-1, the MDR and IVDR revision proposal, AI Act and AI Omnibus with Commission guidelines,
  NIS2 and its Portuguese transposition, CRA, Data Act, Product Liability Directive, accessibility law, Portuguese
  health information law, ISO and IEC standards, and research on health app privacy. Sources not yet checked
  against the official text are marked pending.
- Guides: introduction, regulatory map, the device question, using HDSF.
- `hdsf.yaml` manifest, qualification record and DPIA outline templates; self-assessment checklists.
- Scanner (`tooling/scan.py`): 28 manifest checks, code patterns for trackers, health data in logs and analytics,
  plain storage, plain http, secrets and medical claims; Markdown, JSON and SARIF reports; description-only mode;
  inline ignores and dated waivers. Semgrep rules.
- Claude skill `skill/hdsf-review`.
- Runs on the Safety Framework Engine shared with CSEF (pinned in `engine/ENGINE.lock`).

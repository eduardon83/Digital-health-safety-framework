# Changelog

Newest first. Open items and what we are watching: [legislation.md, watch list](framework/legislation.md#open-discussions-and-watch-list).

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

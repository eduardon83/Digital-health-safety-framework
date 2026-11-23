# Using HDSF

Four ways to use HDSF. You do not need to code for the first three.

## 1. The Workbench (no code)

For designers, product owners, decision makers and researchers. Open the [Workbench](https://hdsf.kendirstudios.pt/workbench/),
describe the product in a form, and add your documents: privacy notice, store listing, onboarding and help texts, design documents,
DPIA, qualification record. PDF, Word, Markdown, text and HTML all work. Nothing is uploaded: the tools run in your browser.

You get one report with:

- the rules that apply and what your description shows (BLOCK, REVIEW, WARN, HUMAN);
- a review of your documents: the privacy notice against GDPR (RGPD) Art. 13 and 14, medical claims, safety and AI wording, plain
  language and readability (English and Portuguese), and wording that steers people (confirmshaming, false urgency, guilt, fear,
  percentage-only risks, notifications that reveal health);
- the EU recommendations that apply to your product (layer 2);
- design recommendations from research (layer 3).

Open the report in the browser (search, filters, "Print or save as PDF"), download it as Word, or download everything as a zip. The
zip keeps your `hdsf.yaml`, so you can come back and continue.

## 2. Read and tick

Read the [core rules](catalogue/core.md) and the profiles that fit your product, then tick the
[self-assessment checklist](../self-assessment/core.md). Keep evidence next to each tick. No tools needed.

## 3. Describe your product

Copy [templates/hdsf.yaml](../templates/hdsf.yaml) to the root of your repository and fill it in. It takes about an
hour and answers most questions a reviewer, a buyer or an authority will ask first: the intended purpose, the device
question, where data goes, who receives health data, and which documents exist.

## 4. Run the scanner (developers)

```bash
git clone https://github.com/eduardon83/Digital-health-safety-framework hdsf
pip install pyyaml
python3 hdsf/tooling/scan.py --repo path/to/your/product --level 1 --out-dir hdsf-report --format md,json,sarif
```

With a document review and exports (interactive HTML dashboard, PDF and Word, as in CSEF):

```bash
pip install python-docx      # for Word; PDF uses Chrome or Chromium, or pip install weasyprint
python3 hdsf/tooling/scan.py --repo path/to/your/product --level 2 --out-dir hdsf-report \
  --docs path/to/your/product/docs --export html,pdf,docx
```

From an earlier scan: `python3 hdsf/tooling/export.py --input hdsf-report/findings.json --review hdsf-report/review.json --formats html,pdf,docx`.

Without code, on a computer (the Workbench's engine): `python3 hdsf/tooling/workbench.py --work folder-with-hdsf.yaml-and-documents`.
Or only the manifest: `python3 hdsf/tooling/scan.py --repo folder-with-hdsf.yaml --description-only`.

### Reading the report

| Severity | Meaning |
|---|---|
| BLOCK | A MUST rule with a strong sign of a problem. Fix it before launch. |
| REVIEW | A MUST rule with a sign that needs a person to decide. |
| WARN | A SHOULD rule with a sign. Fix it or record why not. |
| HUMAN | A rule that applies but only a person can check. Keep the evidence. |
| WAIVED | A finding covered by an inline comment or a dated waiver. |

Automated checks find signs, not proof. A clean report does not mean a product is compliant.

### In CI

Add the scan to your pipeline and fail on blocking findings:

```bash
python3 hdsf/tooling/scan.py --repo . --level 1 --fail-on block --format sarif --out-dir hdsf-report
```

Upload `hdsf-report/hdsf.sarif` to GitHub code scanning to see findings next to the code. Semgrep users can also use
`tooling/semgrep/hdsf.yml`.

### Ignoring a finding

When a finding is wrong, add a comment on the line or the line above, with a reason:

```js
console.log("condition picker opened"); // hdsf-ignore: CORE-DAT-10 because no health value is logged
```

For a whole rule, add a dated waiver in `hdsf.yaml`:

```yaml
waivers:
  - {rule: CORE-SEC-05, reason: "SBOM pipeline ships in March", until: 2027-03-31}
```

## With Claude

The `skill/hdsf-review/` folder is a skill for Claude. It runs the scanner, reads the report with you and drafts the
missing documents (qualification record, DPIA outline, AI inventory).

## The engine

HDSF runs on the Safety Framework Engine (`engine/sfe`), shared with the
[Child-Safe EdTech Framework](https://csef.kendirstudios.pt). The engine lives in the CSEF repository; HDSF keeps a
pinned copy and records the commit in `engine/ENGINE.lock`.

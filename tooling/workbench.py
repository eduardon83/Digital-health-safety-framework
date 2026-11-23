"""HDSF Workbench: describe a product in a form, add documents, and get the description check, the document review,
design recommendations and reports. No code is read.

The same module runs in the browser (docs/workbench/, with Pyodide; nothing is uploaded) and on a computer:

  python3 tooling/workbench.py --work FOLDER [--out DIR]

FOLDER holds hdsf.yaml and the documents (any subfolder). Results: report.html (dashboard), report.docx, Markdown
reports, findings.json, review.json and a zip with everything. Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import docreview  # noqa: E402
import scan  # noqa: E402
from sfe import export as sfe_export  # noqa: E402
from sfe import scanner  # noqa: E402

PROFILE_HELP = {"W": "Wellness and lifestyle (no medical purpose)", "M": "Medical device software (MDR or IVDR)",
                "E": "EHR system or patient portal (EHDS)", "R": "Research or secondary use of health data",
                "T": "Telehealth or care delivery"}
USER_HELP = {"public": "People managing their own health", "patients": "Patients under care",
             "professionals": "Health and care professionals", "children": "Children (under 18)"}
FEATURE_HELP = {"accounts": "User accounts", "health_records": "Stores health records", "sensors": "Phone or device sensors",
                "wearables": "Wearables", "symptom_input": "People enter symptoms", "medication": "Medication or reminders",
                "mental_health": "Mental health", "reproductive_health": "Cycle, fertility or sexual health", "genetic": "Genetic data",
                "location": "Location", "notifications": "Notifications", "chat": "Chat between people", "community": "Community or forum",
                "telehealth": "Video or remote consultations", "payments": "Payments", "ads": "Shows advertising",
                "analytics": "Product analytics", "ai_generative": "Generative AI (chatbot, summaries)",
                "ai_clinical": "AI with a clinical purpose (risk scores, triage, imaging)",
                "sharing_with_professionals": "Sharing with professionals", "research_use": "Data used for research",
                "emergency_content": "Emergency or crisis content"}
DOCS = [("qualification.rationale", "Qualification record (is it a medical device?)"), ("data.dpia", "DPIA"),
        ("data.records", "Record of processing activities (GDPR Art. 30)"), ("security.policy", "Security policy"),
        ("security.incident_plan", "Incident and breach plan"), ("safety.content_review", "Health content review register"),
        ("ai.inventory", "AI inventory"), ("ai.risk_file", "AI risk file (medical device AI)"), ("clinical.qms", "Quality management system"),
        ("clinical.evaluation", "Clinical or performance evaluation"), ("clinical.pms_plan", "Post-market surveillance plan"),
        ("ehds.label", "EHDS label and EU database entry"), ("ehds.conformity", "EHDS conformity evidence"),
        ("children.csef_report", "CSEF report (products for children)")]

# key, label, kind, options or help
FIELDS = [
    ("product.name", "Product name", "text", ""),
    ("product.maker", "Maker (company)", "text", ""),
    ("product.contact", "Privacy contact (email)", "text", ""),
    ("intended_purpose", "Intended purpose", "textarea", "One or two full sentences: what it is for, for whom, what it claims. Everything else depends on it."),
    ("countries", "Countries where it is used", "text", "Two-letter codes, separated by commas, for example PT, ES"),
    ("profiles", "What kind of product", "checks", PROFILE_HELP),
    ("users", "Who uses it", "checks", USER_HELP),
    ("features", "What it does", "checks", FEATURE_HELP),
    ("qualification.medical_device", "Is it a medical device?", "select",
     {"undecided": "Not decided yet", "none": "No", "mdsw": "Yes, medical device software (MDR)", "ivd": "Yes, in vitro diagnostic software (IVDR)",
      "annex_xvi": "Annex XVI product"}),
    ("qualification.class", "Device class", "select", {"": "Not a device", "I": "MDR class I", "IIa": "MDR class IIa", "IIb": "MDR class IIb",
                                                       "III": "MDR class III", "A": "IVDR class A", "B": "IVDR class B", "C": "IVDR class C", "D": "IVDR class D"}),
    ("qualification.notified_body", "Notified body", "text", "Name and number, or 'planned'"),
    ("data.gdpr_role", "Your GDPR (RGPD) role", "select", {"": "Choose", "controller": "Controller", "processor": "Processor (for clinics or others)",
                                                            "joint_controller": "Joint controller", "mixed": "Different roles per purpose"}),
    ("data.purposes", "Purposes of processing", "lines", "One per line: purpose | legal basis | Art. 9 condition | uses health data (yes or no). For example: provide the service | contract | explicit_consent | yes"),
    ("data.retention", "How long data is kept", "text", ""),
    ("data.storage_regions", "Where data is stored", "text", "Regions or countries, separated by commas, for example eu-west-1"),
    ("data.third_parties", "Who receives data", "lines", "One per line: name | purpose | country | health data yes or no | contract (DPA) document"),
    ("data.tracking_on_health_screens", "Trackers or ad SDKs on screens with health data?", "select", {"": "Choose", "false": "No", "true": "Yes"}),
    ("data.ads", "Advertising", "select", {"none": "No advertising", "contextual": "Contextual only (not based on the person)", "targeted": "Targeted"}),
    ("data.rights.access", "Where people see their data", "text", "For example: in the app, Profile > My data"),
    ("data.rights.export", "Where people download their data", "text", ""),
    ("data.rights.delete", "Where people delete their account and data", "text", ""),
    ("safety.emergency_route", "Route to urgent help", "text", "Where the product shows how to get urgent help"),
    ("security.sbom", "Software bill of materials", "text", "A document, or 'ci' if your build produces it"),
    ("ehds.ehr_system", "Is it an EHR system?", "select", {"false": "No", "true": "Yes"}),
    ("ehds.claims_ehr_interoperability", "Does it claim it works with health records?", "select", {"false": "No", "true": "Yes"}),
    ("nis2.status", "NIS2 status (care providers, some manufacturers)", "select", {"": "Choose", "not_in_scope": "Not in scope", "important": "Important entity", "essential": "Essential entity"}),
    ("review.last_reviewed", "Last reviewed", "date", ""),
] + [(k, label, "doc", "") for k, label in DOCS]


def _get(d, path):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _set(d, path, value):
    ks = path.split(".")
    for k in ks[:-1]:
        if not isinstance(d.get(k), dict):
            d[k] = {}
        d = d[k]
    d[ks[-1]] = value


def manifest_to_form(text: str) -> dict:
    m = yaml.safe_load(text or "") or {}
    f = {}
    for key, _, kind, _ in FIELDS:
        v = _get(m, key)
        if kind == "checks":
            f[key] = [x for x in (v or []) if x != "core"]
        elif kind == "lines":
            rows = []
            for x in v or []:
                if key == "data.purposes" and isinstance(x, dict):
                    rows.append(" | ".join(str(x.get(k, "")) for k in ("name", "basis", "art9")) + " | " + ("no" if x.get("health_data") is False else "yes"))
                elif isinstance(x, dict):
                    rows.append(" | ".join(str(x.get(k, "")) for k in ("name", "purpose", "jurisdiction"))
                                + " | " + ("yes" if x.get("receives_health_data") else "no") + " | " + str(x.get("dpa") or ""))
            f[key] = "\n".join(rows)
        elif key in ("countries", "data.storage_regions"):
            f[key] = ", ".join(v or [])
        elif isinstance(v, bool):
            f[key] = "true" if v else "false"
        else:
            f[key] = "" if v is None else str(v)
    return f


def form_to_manifest(text: str, f: dict) -> str:
    m = yaml.safe_load(text or "") or {}
    m.setdefault("hdsf_version", "0.2")
    for key, _, kind, _ in FIELDS:
        if key not in f:
            continue
        v = f[key]
        if kind == "checks":
            v = (["core"] if key == "profiles" else []) + list(v or [])
        elif kind == "lines":
            rows = [[c.strip() for c in ln.split("|")] for ln in str(v or "").splitlines() if ln.strip()]
            if key == "data.purposes":
                v = [{"name": r[0], "basis": r[1] if len(r) > 1 else "", "art9": r[2] if len(r) > 2 else "",
                      **({"health_data": False} if len(r) > 3 and r[3].lower() in ("no", "n", "não", "nao", "false") else {})} for r in rows]
            else:
                v = [{"name": r[0], "purpose": r[1] if len(r) > 1 else "", "jurisdiction": (r[2] if len(r) > 2 else "").upper(),
                      "receives_health_data": (r[3].lower() in ("yes", "y", "sim", "true")) if len(r) > 3 else False,
                      **({"dpa": r[4]} if len(r) > 4 and r[4] else {})} for r in rows]
        elif key in ("countries", "data.storage_regions"):
            v = [x.strip() for x in str(v or "").split(",") if x.strip()]
        elif kind == "select" and v in ("true", "false"):
            v = v == "true"
        elif v == "":
            v = None
        _set(m, key, v)
    return yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=120)


def check_form(text: str) -> list[str]:
    m = yaml.safe_load(text or "") or {}
    gaps = []
    if len(str(m.get("intended_purpose") or "").strip()) < 40:
        gaps.append("Write the intended purpose in one or two full sentences.")
    if _get(m, "qualification.medical_device") in (None, "undecided"):
        gaps.append("Answer the device question (read the guide 'Is my software a medical device?').")
    if not _get(m, "data.purposes"):
        gaps.append("List the purposes of processing with their legal basis and Art. 9 condition.")
    return gaps


def _files(d: Path) -> list[dict]:
    kinds = {".html": "html", ".zip": "zip", ".json": "json", ".md": "md", ".docx": "docx", ".yaml": "yaml", ".pdf": "pdf"}
    order = {"html": 0, "docx": 1, "md": 2, "json": 3, "yaml": 4, "zip": 5}
    fs = [{"path": str(p), "name": p.name, "kind": kinds.get(p.suffix.lower(), "file")} for p in sorted(d.iterdir()) if p.is_file()]
    return sorted(fs, key=lambda x: (order.get(x["kind"], 9), x["name"]))


def _has_docx() -> bool:
    try:
        import docx  # noqa: F401
        return True
    except ImportError:
        return False


def run(work: str | Path, out: str | Path, opts: dict | None = None) -> dict:
    """Run the description check and the document review. Returns {"results": [...], "zip": path, "summary": {...}}."""
    opts = opts or {}
    work, out = Path(work), Path(out)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    mp = work / "hdsf.yaml"
    level = int(opts.get("level") or 2)
    cfg, rules, sources, result, product = scan.run(work, level, str(mp) if mp.exists() else None, description_only=True)
    (out / "findings.json").write_text(scanner.to_json(cfg, result, product), encoding="utf-8")
    (out / "hdsf-report.md").write_text(scanner.render_markdown(cfg, result, sources, product), encoding="utf-8")
    docs = [p for p in sorted(work.rglob("*")) if p.is_file() and p.suffix.lower() in docreview.DOC_EXT and p.name != "hdsf.yaml"]
    sections = docreview.run([work], str(mp) if mp.exists() else None)
    (out / "review.json").write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "review.md").write_text(docreview.to_markdown(sections), encoding="utf-8")
    formats = ["html"] + (["docx"] if _has_docx() else [])
    sfe_export.export(cfg, json.loads((out / "findings.json").read_text(encoding="utf-8")), {r["id"]: r for r in rules},
                      sources, formats, out, sections, scan.ACCENT)
    if mp.exists():
        shutil.copy(mp, out / "hdsf.yaml")
    z = out.parent / "hdsf-results.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.iterdir()):
            zf.write(p, p.name)
    c = result["counts"]
    gaps = sum(i["status"] == "gap" for s in sections for i in s["items"])
    recs = sum(len(s["items"]) for s in sections if "layer" in s["title"])
    summary = {"verdict": scanner.verdict(result), "counts": c, "rules": len(result["rules_in_scope"]), "docs": len(docs),
               "doc_gaps": gaps, "recommendations": recs, "docx": "docx" in formats}
    return {"results": _files(out), "zip": str(z), "summary": summary}


# --------------------------------------------------------------------------- web bundle and form
BUNDLE = ["tooling/scan.py", "tooling/checks.py", "tooling/docreview.py", "tooling/workbench.py",
          "framework/framework.yaml", "framework/rules.yaml", "framework/sources.yaml", "templates/hdsf.yaml"]


def web_bundle(root: Path = ROOT) -> str:
    files = {f: (root / f).read_text(encoding="utf-8") for f in BUNDLE}
    for p in sorted((root / "engine" / "sfe").glob("*.py")):
        files[f"engine/sfe/{p.name}"] = p.read_text(encoding="utf-8")
    return json.dumps({"files": files}, ensure_ascii=False, sort_keys=True) + "\n"


def example_bundle(root: Path = ROOT) -> str:
    ex = root / "examples" / "compliant-app"
    files = {"hdsf.yaml": (ex / "hdsf.yaml").read_text(encoding="utf-8"), "SECURITY.md": (ex / "SECURITY.md").read_text(encoding="utf-8")}
    for p in sorted((ex / "texts").glob("*")) + sorted((ex / "docs").glob("*")):
        files[str(p.relative_to(ex))] = p.read_text(encoding="utf-8")
    return json.dumps(files, ensure_ascii=False, sort_keys=True) + "\n"


def form_html() -> str:
    import html as h
    out, group = [], None
    groups = {"product.name": "About the product", "profiles": "What kind of product", "qualification.medical_device": "The device question",
              "data.gdpr_role": "Data (GDPR / RGPD)", "safety.emergency_route": "Safety, security and health records",
              DOCS[0][0]: "Documents you have"}
    for key, label, kind, opt in FIELDS:
        if key in groups:
            if group:
                out.append("</fieldset>")
            group = groups[key]
            out.append(f'<fieldset><legend>{h.escape(group)}</legend>')
            if key == DOCS[0][0]:
                out.append('<p class="note">Pick the file from your documents (step 2), or type a link. Leave empty if you do not have it yet.</p>')
        fid = "f-" + key.replace(".", "-").replace("_", "-")
        hint = f'<span class="hint">{h.escape(opt)}</span>' if isinstance(opt, str) and opt else ""
        if kind == "checks":
            boxes = "".join(f'<label class="chk"><input type="checkbox" data-f="{key}" value="{k}"> {h.escape(v)}</label>' for k, v in opt.items())
            out.append(f'<div class="field"><span class="lab">{h.escape(label)}</span><div class="chks">{boxes}</div></div>')
        elif kind == "select":
            opts = "".join(f'<option value="{k}">{h.escape(v)}</option>' for k, v in opt.items())
            out.append(f'<div class="field"><label class="lab" for="{fid}">{h.escape(label)}</label><select id="{fid}" data-f="{key}">{opts}</select>{hint}</div>')
        elif kind in ("textarea", "lines"):
            out.append(f'<div class="field wide"><label class="lab" for="{fid}">{h.escape(label)}</label>{hint}<textarea id="{fid}" data-f="{key}" rows="3"></textarea></div>')
        elif kind == "doc":
            out.append(f'<div class="field"><label class="lab" for="{fid}">{h.escape(label)}</label><input id="{fid}" data-f="{key}" list="doclist" placeholder="docs/..."></div>')
        else:
            t = "date" if kind == "date" else "text"
            out.append(f'<div class="field"><label class="lab" for="{fid}">{h.escape(label)}</label><input id="{fid}" type="{t}" data-f="{key}">{hint}</div>')
    out.append("</fieldset>")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="HDSF Workbench on a computer")
    ap.add_argument("--work", required=True, help="folder with hdsf.yaml and documents")
    ap.add_argument("--out", default="hdsf-workbench")
    ap.add_argument("--level", type=int, default=2, choices=[1, 2, 3])
    a = ap.parse_args(argv)
    res = run(a.work, a.out, {"level": a.level})
    s = res["summary"]
    print(f"{s['verdict']} {s['docs']} document(s), {s['doc_gaps']} document gap(s), {s['recommendations']} recommendation(s).")
    print(f"Reports in {a.out}; everything in {res['zip']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

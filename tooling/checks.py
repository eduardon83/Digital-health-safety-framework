"""HDSF manifest checks: what hdsf.yaml says, or fails to say.

Each check takes (manifest, repo, pattern) and returns a list of problems (empty = fine). The rules in
framework/rules.yaml name these checks. Licence: Apache-2.0
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

EEA = {"EU", "EEA", "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "EL", "HU", "IE", "IT", "LV",
       "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"}
EEA_REGION = re.compile(r"(^eu\b|\beu-|-eu\b|europe|frankfurt|ireland|dublin|paris|stockholm|milan|madrid|lisbon|"
                        r"amsterdam|warsaw|vienna|brussels|helsinki|copenhagen|oslo)", re.I)
# Adequacy decisions and other Chapter V tools accepted as a recorded transfer tool.
TRANSFER_TOOLS = {"adequacy", "scc", "bcr", "derogation", "dpf"}
MEDICAL_WORDS = re.compile(r"\b(diagnos\w*|treat(s|ment|ing)?|therap\w*|cure\w*|monitor\w* (a |the )?(disease|condition)|"
                           r"predict\w* (the )?(risk|disease)|dose|dosing|detect\w* (cancer|disease|arrhythmia|atrial))\b", re.I)
DEVICE_KINDS = {"mdsw", "ivd", "annex_xvi"}
VALID_KINDS = DEVICE_KINDS | {"none", "undecided"}
REVIEW_MAX_DAYS = 400


def _get(m, path, default=None):
    cur = m or {}
    for k in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return default if cur is None else cur


def _exists(repo: Path, value) -> bool:
    if not value:
        return False
    v = str(value)
    if v.startswith(("http://", "https://")):
        return True
    return (Path(repo) / v).exists()


def _need_doc(m, repo, key, what):
    v = _get(m, key)
    if not v:
        return [f"{key} is not set: link {what}"]
    if not _exists(repo, v):
        return [f"{key} points to {v}, which does not exist"]
    return []


def _features(m):
    return set(_get(m, "features", []) or [])


def _kind(m):
    return _get(m, "qualification.medical_device")


# --------------------------------------------------------------------------- checks
def manifest_missing(m, repo, p):
    return [] if m else ["no hdsf.yaml found: copy templates/hdsf.yaml to the repository root"]


def intended_purpose_missing(m, repo, p):
    t = str(_get(m, "intended_purpose", "")).strip()
    if len(t) < 40:
        return ["intended_purpose is missing or too short to decide the qualification (one or two full sentences)"]
    return []


def qualification_missing(m, repo, p):
    k = _kind(m)
    if k is None:
        return ["qualification.medical_device is not set (none, mdsw, ivd, annex_xvi)"]
    if k not in VALID_KINDS:
        return [f"qualification.medical_device has an unknown value: {k}"]
    if k == "undecided":
        return ["qualification.medical_device is 'undecided': decide before launch"]
    if k in DEVICE_KINDS and "M" not in set(_get(m, "profiles", []) or []):
        return [f"qualification.medical_device is {k}, but profile M is not declared"]
    return []


def qualification_rationale_missing(m, repo, p):
    if _kind(m) in (None, "undecided"):
        return []
    return _need_doc(m, repo, "qualification.rationale", "the written qualification reasoning (templates/qualification.md)")


def wellness_purpose_sounds_medical(m, repo, p):
    if _kind(m) != "none":
        return []
    t = str(_get(m, "intended_purpose", ""))
    hits = sorted({x.group(0).lower() for x in MEDICAL_WORDS.finditer(t)})
    if hits:
        return [f"intended_purpose uses medical wording ({', '.join(hits)}) while qualification.medical_device is none: check the qualification or the wording"]
    return []


def device_class_missing(m, repo, p):
    k = _kind(m)
    if k not in DEVICE_KINDS:
        return []
    c = _get(m, "qualification.class")
    allowed = {"mdsw": {"I", "IIa", "IIb", "III"}, "annex_xvi": {"I", "IIa", "IIb", "III"}, "ivd": {"A", "B", "C", "D"}}[k]
    if c not in allowed:
        return [f"qualification.class must be one of {sorted(allowed)} for {k}"]
    out = []
    if not (k == "mdsw" and c == "I") and not (k == "ivd" and c == "A") and not _get(m, "qualification.notified_body"):
        out.append(f"class {c} needs a notified body: set qualification.notified_body (or 'planned')")
    return out


def device_docs_missing(m, repo, p):
    if _kind(m) not in DEVICE_KINDS:
        return []
    return _need_doc(m, repo, "clinical.qms", "the quality management system manual")


def clinical_evaluation_missing(m, repo, p):
    if _kind(m) not in DEVICE_KINDS:
        return []
    return (_need_doc(m, repo, "clinical.evaluation", "the clinical or performance evaluation")
            + _need_doc(m, repo, "clinical.pms_plan", "the post-market surveillance plan"))


def art9_condition_missing(m, repo, p):
    purposes = _get(m, "data.purposes", []) or []
    if not purposes:
        return ["data.purposes is empty: list each purpose with its basis (Art. 6) and art9 condition (Art. 9(2))"]
    out = []
    for i, x in enumerate(purposes):
        name = x.get("name", f"#{i + 1}") if isinstance(x, dict) else str(x)
        if not isinstance(x, dict) or not x.get("basis") or not x.get("art9"):
            out.append(f"purpose '{name}' lacks basis or art9")
        elif str(x.get("art9")).lower() in ("none", "n/a", "no"):
            if x.get("health_data", True):
                out.append(f"purpose '{name}' uses health data with art9: none")
    return out


def dpia_missing(m, repo, p):
    return _need_doc(m, repo, "data.dpia", "the DPIA")


def retention_missing(m, repo, p):
    return [] if _get(m, "data.retention") else ["data.retention is not set"]


def health_processor_without_dpa(m, repo, p):
    out = []
    for t in _get(m, "data.third_parties", []) or []:
        if not isinstance(t, dict):
            continue
        if t.get("receives_health_data") and not t.get("dpa"):
            out.append(f"{t.get('name', '?')} receives health data but has no dpa")
        if "receives_health_data" not in t:
            out.append(f"{t.get('name', '?')}: say whether it receives health data (receives_health_data)")
    return out


def transfer_outside_eea(m, repo, p):
    out = []
    for r in _get(m, "data.storage_regions", []) or []:
        if not EEA_REGION.search(str(r)):
            out.append(f"storage region {r} looks outside the EEA")
    for t in _get(m, "data.third_parties", []) or []:
        if not isinstance(t, dict):
            continue
        j = str(t.get("jurisdiction", "")).upper()
        if not j:
            out.append(f"{t.get('name', '?')}: jurisdiction not given")
        elif j not in EEA and str(t.get("transfer_tool", "")).lower() not in TRANSFER_TOOLS:
            out.append(f"{t.get('name', '?')} is in {j} without a transfer_tool ({', '.join(sorted(TRANSFER_TOOLS))})")
    return out


def data_rights_missing(m, repo, p):
    r = _get(m, "data.rights", {}) or {}
    missing = [k for k in ("access", "export", "delete") if not r.get(k)]
    return [f"data.rights does not show {', '.join(missing)}"] if missing else []


def trackers_on_health_screens(m, repo, p):
    v = _get(m, "data.tracking_on_health_screens")
    if v is None:
        return ["data.tracking_on_health_screens is not declared (true or false)"]
    return ["data.tracking_on_health_screens is true"] if v else []


def ads_with_health_data(m, repo, p):
    ads = str(_get(m, "data.ads", "none")).lower()
    if ads in ("targeted", "health_based", "health-based"):
        return [f"data.ads is {ads}: health data must not be used for advertising"]
    if "ads" in _features(m) and ads not in ("none", "contextual"):
        return ["the product shows ads: declare data.ads as none or contextual"]
    return []


def records_missing(m, repo, p):
    return _need_doc(m, repo, "data.records", "the record of processing activities (Art. 30)")


def roles_missing(m, repo, p):
    r = _get(m, "data.gdpr_role")
    if r not in ("controller", "processor", "joint_controller", "mixed"):
        return ["data.gdpr_role is not set (controller, processor, joint_controller or mixed)"]
    return []


def security_policy_missing(m, repo, p):
    return _need_doc(m, repo, "security.policy", "SECURITY.md or a security page")


def incident_plan_missing(m, repo, p):
    return _need_doc(m, repo, "security.incident_plan", "the incident and breach plan")


def sbom_missing(m, repo, p):
    return [] if _get(m, "security.sbom") else ["security.sbom is not set (a file, or 'ci' if CI produces it)"]


def ai_without_inventory(m, repo, p):
    return _need_doc(m, repo, "ai.inventory", "the AI inventory")


def medical_ai_without_risk_file(m, repo, p):
    if _kind(m) not in DEVICE_KINDS or "ai_clinical" not in _features(m):
        return []
    return _need_doc(m, repo, "ai.risk_file", "the AI risk file for the AI Act high-risk requirements")


def emergency_route_missing(m, repo, p):
    return [] if _get(m, "safety.emergency_route") else ["safety.emergency_route is not set: say where the urgent help route is"]


def content_review_missing(m, repo, p):
    return _need_doc(m, repo, "safety.content_review", "the content review register")


def ehr_without_ehds_conformity(m, repo, p):
    if not _get(m, "ehds.ehr_system", "E" in set(_get(m, "profiles", []) or [])):
        return []
    return _need_doc(m, repo, "ehds.conformity", "the EHDS conformity plan or evidence")


def wellness_interop_without_label(m, repo, p):
    if not _get(m, "ehds.claims_ehr_interoperability"):
        return []
    return _need_doc(m, repo, "ehds.label", "the EHDS wellness application label and EU database entry")


def research_without_approval(m, repo, p):
    studies = _get(m, "research.studies", []) or []
    if not studies:
        return ["feature research_use is declared but research.studies is empty"]
    out = []
    for s in studies:
        name = s.get("name", "?") if isinstance(s, dict) else str(s)
        for k in ("basis", "art9", "approval", "protocol"):
            if not isinstance(s, dict) or not s.get(k):
                out.append(f"study '{name}' lacks {k}")
    return out


def children_without_csef(m, repo, p):
    return _need_doc(m, repo, "children.csef_report", "the CSEF report or Workbench result")


def nis2_status_missing(m, repo, p):
    s = _get(m, "nis2.status")
    if s not in ("not_in_scope", "important", "essential"):
        return ["nis2.status is not set (not_in_scope, important or essential)"]
    return []


def review_stale(m, repo, p):
    d = _get(m, "review.last_reviewed")
    if not d:
        return ["review.last_reviewed is not set"]
    try:
        day = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d))
    except ValueError:
        return [f"review.last_reviewed is not a date: {d}"]
    age = (dt.date.today() - day).days
    return [f"last review was {age} days ago"] if age > REVIEW_MAX_DAYS else []


CHECKS = {name: fn for name, fn in list(globals().items())
          if callable(fn) and not name.startswith("_") and fn.__module__ == __name__}

"""HDSF: catalogue, manifest checks, scanner and generated files."""
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "tooling"))

import build  # noqa: E402
import checks  # noqa: E402
import scan  # noqa: E402
from sfe import catalogue, config  # noqa: E402

EX = ROOT / "examples"


def test_build_check_passes():
    assert build.main(["--check"]) == 0
    assert not build.errors


def test_every_manifest_check_is_used_and_exists():
    rules = yaml.safe_load((ROOT / "framework" / "rules.yaml").read_text())["rules"]
    used = {p["check"] for r in rules for p in (r["detection"].get("patterns") or []) if p["type"] == "manifest"}
    assert used <= set(checks.CHECKS)
    assert set(checks.CHECKS) - used == {"manifest_missing"}


def test_rule_ids_and_profiles():
    cfg = config.load(ROOT / "framework" / "framework.yaml")
    rules = yaml.safe_load((ROOT / "framework" / "rules.yaml").read_text())["rules"]
    for r in rules:
        prefix = r["id"].split("-")[0]
        assert prefix == "CORE" or prefix in r["profiles"], r["id"]
        assert set(r["users"]) <= set(cfg.dimension_values) | {"all"}


def test_compliant_example_is_clean_at_level_3():
    _, _, _, res, _ = scan.run(EX / "compliant-app", level=3)
    c = res["counts"]
    assert c["BLOCK"] == c["REVIEW"] == c["WARN"] == 0, [(f.rule, f.detail) for f in res["findings"] if f.severity != "HUMAN"]
    assert c["HUMAN"] > 0


def test_noncompliant_example_finds_the_planted_problems():
    _, _, _, res, _ = scan.run(EX / "noncompliant-app", level=2)
    found = {(f.rule, f.severity) for f in res["findings"]}
    for rid in ("CORE-QUA-02", "CORE-TRK-02", "CORE-TRK-03", "CORE-SEC-06", "CORE-DAT-02", "W-EHD-01", "R-DAT-01"):
        assert (rid, "BLOCK") in found, rid
    for rid in ("CORE-TRK-01", "CORE-DAT-10", "CORE-DAT-12", "CORE-SEC-02", "W-QUA-02", "CORE-CHD-01", "CORE-DAT-08"):
        assert (rid, "REVIEW") in found, rid


def test_description_only_reads_no_code():
    _, _, _, res, _ = scan.run(EX / "noncompliant-app", level=2, description_only=True)
    assert all(f.where in ("", "manifest") for f in res["findings"])


def test_missing_manifest_blocks(tmp_path):
    (tmp_path / "app.js").write_text("console.log('hi')\n")
    _, _, _, res, _ = scan.run(tmp_path, level=1)
    assert res["findings"][0].detail.startswith("no hdsf.yaml")


def test_inline_ignore_and_waiver(tmp_path):
    m = yaml.safe_load((EX / "compliant-app" / "hdsf.yaml").read_text())
    m["waivers"] = [{"rule": "CORE-SEC-02", "reason": "test server", "until": (dt.date.today() + dt.timedelta(days=30)).isoformat()}]
    (tmp_path / "hdsf.yaml").write_text(yaml.safe_dump(m))
    for d in ("docs",):
        (tmp_path / d).mkdir()
    for f in ("qualification", "dpia", "incident-plan", "content-review", "dpa-hosting", "dpa-email"):
        (tmp_path / "docs" / f"{f}.md").write_text("x")
    (tmp_path / "SECURITY.md").write_text("x")
    (tmp_path / "a.ts").write_text('const u = "http://test.example";\nconsole.log("diagnosis", d); // hdsf-ignore: CORE-DAT-10 because test\n')
    _, _, _, res, _ = scan.run(tmp_path, level=1)
    sev = {f.rule: f.severity for f in res["findings"] if f.where.startswith("a.ts")}
    assert sev == {"CORE-SEC-02": "WAIVED", "CORE-DAT-10": "WAIVED"}


def test_manifest_checks_edge_cases(tmp_path):
    assert checks.qualification_missing({"qualification": {"medical_device": "mdsw"}, "profiles": ["core"]}, tmp_path, {})
    assert checks.device_class_missing({"qualification": {"medical_device": "mdsw", "class": "IIa"}}, tmp_path, {})
    assert not checks.device_class_missing({"qualification": {"medical_device": "mdsw", "class": "I"}}, tmp_path, {})
    assert checks.wellness_purpose_sounds_medical({"qualification": {"medical_device": "none"},
                                                  "intended_purpose": "Helps people monitor their condition and adjust the dose."}, tmp_path, {})
    assert not checks.transfer_outside_eea({"data": {"third_parties": [{"name": "x", "jurisdiction": "US", "transfer_tool": "dpf"}]}}, tmp_path, {})


def test_reports_render(tmp_path):
    assert scan.main(["--repo", str(EX / "noncompliant-app"), "--out-dir", str(tmp_path), "--format", "md,json,sarif"]) == 0
    sarif = json.loads((tmp_path / "hdsf.sarif").read_text())
    assert sarif["runs"][0]["results"]
    assert (tmp_path / "hdsf-report.md").read_text().startswith("# HDSF report")
    assert scan.main(["--repo", str(EX / "noncompliant-app"), "--fail-on", "block"]) == 1


def test_skill_copy_runs_on_its_own(tmp_path):
    import shutil
    import subprocess
    sk = tmp_path / "hdsf-review"
    shutil.copytree(ROOT / "skill" / "hdsf-review", sk)
    out = subprocess.run([sys.executable, str(sk / "scripts" / "scan.py"), "--repo", str(EX / "compliant-app"), "--level", "3"],
                         capture_output=True, text=True, cwd=tmp_path)
    assert out.returncode == 0, out.stderr
    assert "# HDSF report" in out.stdout


# --------------------------------------------------------------------------- v0.2: GDPR map, layers, review, exports, Workbench
import docreview  # noqa: E402
import workbench  # noqa: E402
from sfe import export as sfe_export  # noqa: E402


def _rules():
    return yaml.safe_load((ROOT / "framework" / "rules.yaml").read_text())["rules"]


def test_gdpr_map_covers_key_articles():
    text = (ROOT / "framework" / "gdpr-map.md").read_text()
    for art in ("9", "13", "22", "25", "30", "35", "89"):
        row = next(ln for ln in text.splitlines() if ln.startswith(f"| Art. {art} |"))
        assert "CORE-" in row or "R-" in row, art
    assert "RGPD" in text


def test_three_layers_have_rules_and_fitting_sources():
    srcs = {s["id"]: s for s in yaml.safe_load((ROOT / "framework" / "sources.yaml").read_text())["sources"]}
    rules = _rules()
    l2 = [r for r in rules if r["tier"] == 2 and any(srcs[s]["type"] == "guidance" for s in r["sources"])]
    l3 = [r for r in rules if r["tier"] == 3]
    assert len(l2) >= 10 and len(l3) >= 8
    assert all(r["level"] == "SHOULD" for r in l3)
    assert {"CORE-DES-01", "CORE-DES-02", "CORE-DES-03", "CORE-AI-06", "CORE-AI-07", "CORE-LNG-01"} <= {r["id"] for r in rules}


def test_review_finds_problems_in_the_bad_texts():
    s = docreview.run([EX / "noncompliant-app" / "texts"], EX / "noncompliant-app" / "hdsf.yaml")
    items = [(i["status"], i.get("rule")) for sec in s for i in sec["items"]]
    for st, rule in [("gap", "CORE-COM-01"), ("gap", "CORE-QUA-03"), ("gap", "CORE-SAF-01"), ("gap", "CORE-AI-03"),
                     ("gap", "CORE-COM-04"), ("gap", "CORE-DES-06"), ("review", "CORE-DES-01"), ("review", "CORE-COM-03"),
                     ("gap", "CORE-LNG-01")]:
        assert (st, rule) in items, (st, rule)


def test_review_is_clean_on_the_good_texts():
    s = docreview.run([EX / "compliant-app"], EX / "compliant-app" / "hdsf.yaml")
    gaps = [(sec["title"], i["title"]) for sec in s for i in sec["items"] if i["status"] == "gap"]
    assert gaps == []
    titles = [sec["title"] for sec in s]
    assert any("layer 2" in t for t in titles) and any("layer 3" in t for t in titles)


def test_review_reads_portuguese(tmp_path):
    (tmp_path / "privacidade.md").write_text(
        "Política de privacidade. O responsável pelo tratamento é a Exemplo, Lda. Tratamos dados de saúde com o seu consentimento "
        "explícito, que pode retirar a qualquer momento. Pode apresentar uma reclamação à CNPD. " * 3, encoding="utf-8")
    s = docreview.run([tmp_path], None)
    notice = next(sec for sec in s if sec["title"].startswith("Privacy notice"))
    found = {i["title"].split(" (Art.")[0] for i in notice["items"] if i["status"] == "ok"}
    assert {"Who the controller is and how to contact them", "How health data is handled", "How to withdraw consent",
            "Right to complain to the authority"} <= found
    assert docreview.language(notice["items"][0].get("evidence", "") or "dados de saúde para") in ("pt", "en")


def test_exports_html_and_docx(tmp_path):
    assert scan.main(["--repo", str(EX / "noncompliant-app"), "--out-dir", str(tmp_path), "--format", "json",
                      "--docs", str(EX / "noncompliant-app" / "texts"), "--export", "html,docx", "--fail-on", "never"]) == 0
    h = (tmp_path / "report.html").read_text()
    assert "HDSF report" in h and 'data-sev="BLOCK"' in h and "Privacy notice" in h and "<script>" in h
    import docx
    d = docx.Document(str(tmp_path / "report.docx"))
    text = "\n".join(p.text for p in d.paragraphs)
    assert "CORE-QUA-02" in text and "Design recommendations" in text


def test_pdf_export_when_chrome_is_available(tmp_path):
    import pytest
    if not sfe_export.find_chrome():
        pytest.skip("no Chrome")
    assert scan.main(["--repo", str(EX / "compliant-app"), "--out-dir", str(tmp_path), "--format", "json", "--export", "pdf"]) == 0
    assert (tmp_path / "report.pdf").read_bytes()[:4] == b"%PDF"


def test_workbench_form_round_trip_and_run(tmp_path):
    y = (EX / "compliant-app" / "hdsf.yaml").read_text()
    m2 = yaml.safe_load(workbench.form_to_manifest("", workbench.manifest_to_form(y)))
    m1 = yaml.safe_load(y)
    for k in ("intended_purpose", "profiles", "users", "features", "countries", "qualification", "data", "security", "safety"):
        assert m1[k] == m2[k], k
    res = workbench.run(EX / "compliant-app", tmp_path / "out", {"level": 2})
    assert res["summary"]["counts"]["BLOCK"] == 0 and res["summary"]["docs"] >= 3
    names = {f["name"] for f in res["results"]}
    assert {"report.html", "review.md", "findings.json", "hdsf.yaml"} <= names
    assert Path(res["zip"]).exists()


def test_workbench_page_and_bundle_are_built():
    page = (ROOT / "docs" / "workbench" / "index.html").read_text()
    assert 'data-f="intended_purpose"' in page and "hdsf-bundle.json" in page and "{form}" not in page
    b = json.loads((ROOT / "docs" / "workbench" / "hdsf-bundle.json").read_text())
    assert {"tooling/workbench.py", "tooling/docreview.py", "engine/sfe/export.py"} <= set(b["files"])
    assert (ROOT / "docs" / "workbench" / "vendor" / "pypdf-5.1.0-py3-none-any.whl").exists()

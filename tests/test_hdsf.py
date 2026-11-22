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

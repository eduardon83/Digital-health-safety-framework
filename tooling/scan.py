"""Check a digital health product against HDSF.

  python3 tooling/scan.py --repo PATH [--level 1|2|3] [--out-dir DIR] [--format md,json,sarif]
                          [--description-only] [--fail-on block|review]

Reads the product's hdsf.yaml (templates/hdsf.yaml), works out which rules apply (profiles, users, features,
level), looks for signs in the code (regex and dependencies) and in the manifest, and writes a report. With
--description-only it reads the manifest and linked documents only, not the code.

Automated checks find signs, not proof. Not legal or regulatory advice. Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "engine", HERE):  # repository layout, then the skill layout (scripts/sfe)
    if (p / "sfe").is_dir():
        sys.path.insert(0, str(p))
        break
sys.path.insert(0, str(HERE))
from sfe import config as sfe_config  # noqa: E402
from sfe import patterns, scanner  # noqa: E402

import checks  # noqa: E402

TOOL_VERSION = "0.1.0"


def load_framework(root: Path):
    cfg = sfe_config.load(root / "framework" / "framework.yaml")
    rules = yaml.safe_load((root / "framework" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    sources = {s["id"]: s for s in yaml.safe_load((root / "framework" / "sources.yaml").read_text(encoding="utf-8"))["sources"]}
    return cfg, rules, sources


def find_manifest(repo: Path, names, explicit=None):
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    for n in names:
        if (repo / n).exists():
            return repo / n
    return None


def run(repo: Path, level=1, manifest_path=None, description_only=False, root: Path = ROOT):
    cfg, rules, sources = load_framework(root)
    mp = find_manifest(repo, cfg.manifest_names, manifest_path)
    manifest = yaml.safe_load(mp.read_text(encoding="utf-8")) if mp else None
    result = scanner.run(cfg, repo, rules, manifest, level, manifest_checks=checks.CHECKS,
                         ignore=patterns.Ignore(cfg.ignore_token), description_only=description_only)
    if manifest is None:
        f = scanner.Finding(rule="CORE-QUA-01", severity="BLOCK", title="No hdsf.yaml found", strength="MUST", tier=1,
                            where="manifest", detail=checks.manifest_missing(None, repo, None)[0],
                            improvement="Copy templates/hdsf.yaml to the repository root and fill it in.", sources=["MDR", "GDPR"])
        result["findings"].insert(0, f)
        result["counts"]["BLOCK"] += 1
    product = ((manifest or {}).get("product") or {}).get("name", repo.name)
    return cfg, rules, sources, result, product


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check a digital health product against HDSF")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--level", type=int, default=1, choices=[1, 2, 3])
    ap.add_argument("--out-dir")
    ap.add_argument("--format", default="md")
    ap.add_argument("--description-only", action="store_true")
    ap.add_argument("--fail-on", choices=["block", "review"], default=None)
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    cfg, rules, sources, result, product = run(repo, a.level, a.manifest, a.description_only)
    out = {"md": scanner.render_markdown(cfg, result, sources, product),
           "json": scanner.to_json(cfg, result, product),
           "sarif": scanner.to_sarif(cfg, result, {r["id"]: r for r in rules})}
    fmts = [f.strip() for f in a.format.split(",") if f.strip()]
    if a.out_dir:
        d = Path(a.out_dir)
        d.mkdir(parents=True, exist_ok=True)
        names = {"md": "hdsf-report.md", "json": "findings.json", "sarif": "hdsf.sarif"}
        for f in fmts:
            (d / names[f]).write_text(out[f], encoding="utf-8")
        print(f"{scanner.verdict(result)} Report in {d}")
    else:
        print(out[fmts[0]])
    c = result["counts"]
    if a.fail_on == "block" and c["BLOCK"]:
        return 1
    if a.fail_on == "review" and (c["BLOCK"] or c["REVIEW"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

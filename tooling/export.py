"""Export an HDSF scan to an interactive HTML dashboard, PDF and Word.

  python3 tooling/export.py --input hdsf-report/findings.json --formats html,pdf,docx [--review hdsf-report/review.json] [--out-dir DIR]

PDF needs Chrome or Chromium (set CHROME=/path) or WeasyPrint; Word needs python-docx. Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scan  # noqa: E402  (sets up the engine path)
from sfe import export as sfe_export  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Export an HDSF scan")
    ap.add_argument("--input", required=True, help="findings.json from tooling/scan.py")
    ap.add_argument("--formats", default="html")
    ap.add_argument("--review", help="review.json from tooling/docreview.py")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    cfg, rules, sources = scan.load_framework(scan.ROOT)
    result = json.loads(Path(a.input).read_text(encoding="utf-8"))
    sections = json.loads(Path(a.review).read_text(encoding="utf-8")) if a.review else None
    out = Path(a.out_dir) if a.out_dir else Path(a.input).parent
    formats = [f.strip() for f in a.formats.split(",") if f.strip()]
    bad = set(formats) - {"html", "pdf", "docx", "json"}
    if bad:
        ap.error(f"unknown format(s): {', '.join(sorted(bad))}")
    written = sfe_export.export(cfg, result, {r["id"]: r for r in rules}, sources, formats, out, sections, scan.ACCENT)
    for k, p in written.items():
        print(f"{k}: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

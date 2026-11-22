"""Copy the Safety Framework Engine from a CSEF checkout and record the commit.

  python3 tooling/sync_engine.py --from ../child-safe-edtech-framework
  python3 tooling/sync_engine.py --verify ../child-safe-edtech-framework   (CI: copy must match the locked commit)

The engine's home is the CSEF repository (engine/sfe). HDSF keeps a pinned copy so it runs on its own.
Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "engine" / "ENGINE.lock"


def files(d: Path):
    return sorted(p.name for p in d.glob("*.py"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from", dest="src")
    g.add_argument("--verify")
    a = ap.parse_args(argv)
    if a.src:
        csef = Path(a.src).resolve()
        src = csef / "engine" / "sfe"
        dst = ROOT / "engine" / "sfe"
        shutil.rmtree(dst, ignore_errors=True)
        dst.mkdir(parents=True)
        for f in files(src):
            shutil.copy2(src / f, dst / f)
        commit = subprocess.run(["git", "-C", str(csef), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        version = next(ln.split('"')[1] for ln in (src / "__init__.py").read_text().splitlines() if ln.startswith("ENGINE_VERSION"))
        LOCK.write_text(f"source: https://github.com/eduardon83/child-safe-edtech-framework\ncommit: {commit}\nengine_version: {version}\n")
        print(f"engine {version} copied from {commit[:10]}")
        return 0
    src = Path(a.verify).resolve() / "engine" / "sfe"
    dst = ROOT / "engine" / "sfe"
    bad = [f for f in sorted(set(files(src)) | set(files(dst)))
           if not ((src / f).exists() and (dst / f).exists() and filecmp.cmp(src / f, dst / f, shallow=False))]
    if bad:
        print("engine copy differs from the locked CSEF commit:", ", ".join(bad), file=sys.stderr)
        return 1
    print("engine copy matches")
    return 0


if __name__ == "__main__":
    sys.exit(main())

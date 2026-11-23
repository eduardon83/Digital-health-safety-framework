"""Check HDSF's own texts against STYLE.md.

  python3 tooling/stylecheck.py          list problems (exit 1 if any)

Checks: em-dashes, the Oxford comma, contrast frames ("not X, but Y"), inflated words, empty signposting, stacked
hedges, mixed terms for the same thing, and Brazilian Portuguese forms in Portuguese text. Some findings need a
person; add `<!-- style-ok -->` (Markdown) or `# style-ok` (YAML, Python) at the end of a line to accept it.
Licence: Apache-2.0
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FILES = (["README.md", "CONTRIBUTING.md", "STYLE.md", "templates/hdsf.yaml", "templates/hdsf-portugal.yaml",
          "templates/qualification.md", "templates/dpia-health.md", "skill/hdsf-review/SKILL.md", "packs/_template.yaml",
          "packs/pt.yaml", "examples/company-packs/acme.yaml", "tooling/workbench.template.html", "framework/watch.yaml"]
         + [f"framework/{p.name}" for p in sorted((ROOT / "framework").glob("0*.md"))] + ["framework/glossary.md"])
# Texts inside code: only string literals are checked.
CODE = ["tooling/docreview.py", "tooling/checks.py", "tooling/workbench.py", "tooling/build.py", "engine/sfe/export.py",
        "engine/sfe/scanner.py"]

CHECKS = [
    ("em-dash", re.compile("[—–]| -- ")),
    ("Oxford comma", re.compile(r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3}, (?:and|or) ")),
    ("contrast frame", re.compile(r"\b(not (?:just|only|merely) [^.;]{1,40}, (?:but|it)|isn't [^.;]{1,30}, it's|is not [^.;]{1,30}, it is"
                                  r"|[Ss]igns, not proof|not [a-z]+, but [a-z]+)")),
    ("inflated word", re.compile(r"\b(revolution\w*|transformative|crucial|pivotal|seamless\w*|robust|leverag\w+|cutting[- ]edge|"
                                 r"game[- ]chang\w+|unlock\w*|empower\w*|unprecedented|state[- ]of[- ]the[- ]art|world[- ]class|"
                                 r"best[- ]in[- ]class|holistic|synerg\w+)\b", re.I)),
    ("signposting", re.compile(r"\b(it is (important|worth) (to note|noting)|it's worth noting|needless to say|it should be noted|"
                               r"importantly,|notably,)", re.I)),
    ("stacked hedge", re.compile(r"\b(may possibly|might possibly|could potentially|may potentially|might perhaps|could possibly)\b", re.I)),
    ("mixed term", re.compile(r"\blayers?\b", re.I)),
    ("pt-BR form", re.compile(r"\b(equipe|registro|contato|celular|usuári[oa]s?|aplicativo|você)\b")),
]
# Lines where a check does not apply: regexes, word lists and examples of what to avoid.
SKIP_LINE = re.compile(r"(style-ok|pattern:|PT_BR|CLAIMS|PATTERNS|JARGON|forbid_phrases|re\.compile|\br\")")


def string_literals(text: str) -> list[tuple[int, str]]:
    out = []
    for m in re.finditer(r'(?s)("""|\'\'\'|"|\')(.*?)(?<!\\)\1', text):
        line = text.count("\n", 0, m.start()) + 1
        for i, ln in enumerate(m.group(2).splitlines() or [""]):
            out.append((line + i, ln))
    return out


def lines_of(path: Path):
    text = path.read_text(encoding="utf-8")
    raw = text.splitlines()
    if path.suffix == ".py":
        return [(n, s, raw[n - 1] if n - 1 < len(raw) else "") for n, s in string_literals(text)]
    return [(i + 1, ln, ln) for i, ln in enumerate(raw)]


def rule_texts():
    out = []
    doc = yaml.safe_load((ROOT / "framework" / "rules.yaml").read_text(encoding="utf-8"))
    for r in doc["rules"]:
        for k in ("title", "requirement", "rationale", "improvement"):
            out.append((f"rules.yaml {r['id']} {k}", str(r.get(k, ""))))
        for n in r.get("notes", []) or []:
            out.append((f"rules.yaml {r['id']} note", n))
    return out


PAGES = ["docs/index.html", "docs/workbench/index.html"]


def page_text(path: Path) -> list[tuple[int, str, str]]:
    import html as h
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", path.read_text(encoding="utf-8"))
    text = h.unescape(re.sub(r"<[^>]+>", "\\n", text))
    return [(i + 1, ln.strip(), ln) for i, ln in enumerate(text.splitlines()) if ln.strip()]


def check() -> list[str]:
    problems = []
    for rel in PAGES:
        p = ROOT / rel
        if p.exists():
            for n, ln, raw in page_text(p):
                for name, rx in CHECKS:
                    if name == "pt-BR form":
                        continue
                    m = rx.search(ln)
                    if m:
                        problems.append(f"{rel} (text line {n}): {name}: ...{ln[max(0, m.start() - 30):m.end() + 30]}...")
    for rel in FILES + CODE:
        p = ROOT / rel
        if not p.exists():
            continue
        for n, ln, raw in lines_of(p):
            if SKIP_LINE.search(raw) or SKIP_LINE.search(ln):
                continue
            for name, rx in CHECKS:
                if name == "pt-BR form" and "pt" not in rel:
                    continue
                m = rx.search(ln)
                if m:
                    problems.append(f"{rel}:{n}: {name}: ...{ln[max(0, m.start() - 30):m.end() + 30].strip()}...")
    for where, text in rule_texts():
        for name, rx in CHECKS:
            if name == "pt-BR form":
                continue
            m = rx.search(text)
            if m:
                problems.append(f"{where}: {name}: ...{text[max(0, m.start() - 30):m.end() + 30].strip()}...")
    return problems


def main() -> int:
    probs = check()
    for p in probs:
        print(p)
    print(f"{len(probs)} style problem(s)." if probs else "OK: no style problems.")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())

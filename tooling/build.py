"""Validate the HDSF catalogue and regenerate derived files.

  python3 tooling/build.py          regenerate everything
  python3 tooling/build.py --check  fail if a generated file is out of date (CI)

Generated:
  framework/catalogue/*.md      rule catalogue, by profile
  framework/legislation.md      sources by type, with the rules citing each, and the watch list
  self-assessment/*.md          checklists
  tooling/semgrep/hdsf.yml      Semgrep rules from the regex patterns
  docs/                         the website (hdsf.kendirstudios.pt)
  skill/hdsf-review/            copies for the Claude skill (scripts, engine, framework files, template)

Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "tooling"))
from sfe import ENGINE_VERSION  # noqa: E402
from sfe import catalogue as cat  # noqa: E402
from sfe import config as sfe_config  # noqa: E402
from sfe import markdown as md  # noqa: E402

import brand  # noqa: E402
import checks  # noqa: E402
import workbench  # noqa: E402

PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"

CFG = sfe_config.load(ROOT / "framework" / "framework.yaml")
errors: list[str] = []
PROFILE_FILES = {"core": "core", "W": "profile-w", "M": "profile-m", "E": "profile-e", "R": "profile-r", "T": "profile-t"}
GDPR_ARTICLES = [
    ("4", "Definitions: pseudonymisation (5), consent (11), data concerning health (15)"), ("5", "Principles"),
    ("6", "Lawfulness of processing"), ("7", "Conditions for consent"), ("8", "Child's consent for online services"),
    ("9", "Special categories, including health, genetic and biometric data"),
    ("12", "Transparent information, clear and plain language, answer within a month"),
    ("13", "Information when data is collected from the person"), ("14", "Information when data comes from elsewhere"),
    ("15", "Right of access"), ("16", "Right to rectification"), ("17", "Right to erasure"), ("18", "Right to restriction"),
    ("20", "Right to data portability"), ("21", "Right to object"), ("22", "Automated individual decisions"),
    ("24", "Responsibility of the controller"), ("25", "Data protection by design and by default"),
    ("26", "Joint controllers"), ("27", "Representatives of controllers outside the EU"), ("28", "Processors"),
    ("30", "Records of processing activities"), ("32", "Security of processing"),
    ("33", "Notifying a breach to the authority"), ("34", "Telling people about a breach"),
    ("35", "Data protection impact assessment"), ("36", "Prior consultation"),
    ("37", "Data protection officer: when"), ("38", "Data protection officer: position"), ("39", "Data protection officer: tasks"),
    ("44", "Transfers: general principle"), ("45", "Transfers on the basis of an adequacy decision"),
    ("46", "Transfers subject to appropriate safeguards"), ("49", "Derogations for specific situations"),
    ("77", "Right to lodge a complaint with a supervisory authority"), ("89", "Safeguards for research and statistics"),
]
GUIDES = [("framework/00-introduction.md", "introduction"), ("framework/01-regulatory-map.md", "regulatory-map"),
          ("framework/02-qualification.md", "qualification"), ("framework/03-using-hdsf.md", "using-hdsf"),
          ("framework/04-packs.md", "packs"), ("framework/glossary.md", "glossary")]
TYPE_SECTIONS = [("law", "Law in force"), ("law-pending", "Adopted, applying later"), ("proposal", "Proposals"),
                 ("guidance", "Guidance"), ("standard", "Standards"), ("policy", "Policy"),
                 ("literature", "Research and other frameworks"), ("news", "News")]


def load():
    rules_doc = yaml.safe_load((ROOT / "framework" / "rules.yaml").read_text(encoding="utf-8"))
    src_doc = yaml.safe_load((ROOT / "framework" / "sources.yaml").read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in src_doc["sources"]}
    if len(sources) != len(src_doc["sources"]):
        errors.append("duplicate source id")
    rules = rules_doc["rules"]
    ids = [r.get("id") for r in rules]
    if len(set(ids)) != len(ids):
        errors.append("duplicate rule id")
    for r in rules:
        cat.validate_rule(CFG, r, sources, "rules", errors.append, (), set(checks.CHECKS))
        if r.get("level") == "MUST" and r.get("tier") == 3:
            errors.append(f"rules {r['id']}: a level 3 rule should be SHOULD")
    cat.validate_sources(CFG, sources, "sources", errors.append)
    cited = {s for r in rules for s in r["sources"]}
    for sid in sources:
        if sid not in cited:
            errors.append(f"source {sid} is not cited by any rule")
    validate_packs(rules, sources)
    watch = yaml.safe_load((ROOT / "framework" / "watch.yaml").read_text(encoding="utf-8"))["watch"]
    return rules_doc["version"], sorted(rules, key=lambda r: r["id"]), sources, watch


# --------------------------------------------------------------------------- markdown
def catalogue_files(version, rules, sources):
    files = {}
    d = ROOT / "framework" / "catalogue"
    intro = {k: f"{CFG.profile_names[k]}. HDSF v{version}. Rules marked `core` apply to every product; read them first."
             for k in PROFILE_FILES}
    for prof, fn in PROFILE_FILES.items():
        sub = [r for r in rules if prof in r["profiles"]]
        title = "Core rules" if prof == "core" else f"Profile {prof}: {CFG.profile_names[prof]}"
        files[d / f"{fn}.md"] = cat.catalogue_page(CFG, title, intro[prof], sub, sources)
    lines = [cat.header(CFG) + "# Rule catalogue", "",
             f"HDSF v{version}: {len(rules)} rules. Level 1 = {CFG.levels[1]}, 2 = {CFG.levels[2]}, 3 = {CFG.levels[3]}.", "",
             "| Profile | File | Rules |", "|---|---|---|"]
    for prof, fn in PROFILE_FILES.items():
        n = sum(1 for r in rules if prof in r["profiles"])
        lines.append(f"| {prof}: {CFG.profile_names[prof]} | [{fn}.md]({fn}.md) | {n} |")
    lines += ["", "| ID | Rule | Profiles | Strength | Level | Users |", "|---|---|---|---|---|---|"]
    for r in rules:
        lines.append(f"| {r['id']} | {r['title']} | {', '.join(r['profiles'])} | {r['level']} | {r['tier']} | {cat.dimension_txt(CFG, r) if r['users'] != ['all'] else 'all'} |")
    files[d / "index.md"] = "\n".join(lines) + "\n"
    sa = ROOT / "self-assessment"
    for prof, fn in PROFILE_FILES.items():
        sub = [r for r in rules if prof in r["profiles"] and (prof == "core" or r["profiles"] != ["core"])]
        title = "Core (every product)" if prof == "core" else f"Profile {prof}, {CFG.profile_names[prof].lower()} (use with core.md)"
        files[sa / f"{fn}.md"] = cat.checklist_page(CFG, title, sub)
    return files


def legislation(version, rules, sources, watch):
    cites = {}
    for r in rules:
        for s in r["sources"]:
            cites.setdefault(s, []).append(r["id"])
    lines = [cat.header(CFG).replace("rules.yaml", "sources.yaml and framework/watch.yaml") + "# Legislation, guidance and evidence", "",
             f"Every source HDSF v{version} cites, grouped by type, with the rules that cite it. Statuses carry dates; "
             "check the link before you rely on one. This page is not legal advice.", ""]
    pending = [sid for sid, s in sources.items() if str(s.get("verified")) == "pending"]
    if pending:
        lines += ["## Still to verify", "",
                  "These entries were written from the maintainers' knowledge and have not yet been checked against the "
                  "source in this version. Help by checking one and opening a pull request.", "",
                  ", ".join(f"`{p}`" for p in pending), ""]
    lines += ["## Summary", "", "| Source | Type | Jurisdiction | Verified | Rules |", "|---|---|---|---|---|"]
    for sid, s in sources.items():
        lines.append(f"| [{sid}](#{sid.lower()}) | {s['type']} | {s['jurisdiction']} | {s['verified']} | {len(cites.get(sid, []))} |")
    lines.append("")
    for t, heading in TYPE_SECTIONS:
        sub = [(sid, s) for sid, s in sources.items() if s["type"] == t]
        if not sub:
            continue
        lines += [f"## {heading}", ""]
        for sid, s in sub:
            lines += [f"### {sid}", "", f"**{s['title']}**", "", f"**Status.** {s['status']}", "",
                      f"**Jurisdiction.** {s['jurisdiction']} · **Verified.** {s['verified']}", ""]
            if s.get("notes"):
                lines += [f"**Notes.** {s['notes']}", ""]
            lines += [f"**Rules citing it.** {', '.join(f'`{x}`' for x in cites.get(sid, [])) or 'none'}", ""]
            if s.get("url"):
                lines += [f"**Link.** [{s['url']}]({s['url']})", ""]
    lines += ["## Open discussions and watch list", "", "| Item | What to watch | Effect on HDSF |", "|---|---|---|"]
    for w in watch:
        lines.append(f"| {w['item']} | {w['watch']} | {w['effect']} |")
    return "\n".join(lines) + "\n"


def validate_packs(rules, sources):
    from sfe import packs
    for f in sorted((ROOT / "packs").glob("*.yaml")) + sorted((ROOT / "examples" / "company-packs").glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        packs.validate(CFG, yaml.safe_load(f.read_text(encoding="utf-8")), rules, sources,
                       lambda e, f=f: errors.append(f"{f.relative_to(ROOT)}: {e}"), set(checks.CHECKS))


def pack_page(path, rules, sources):
    from sfe import packs
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    m = packs.merged(rules, sources)
    packs.apply(CFG, m, doc, str(path), set(checks.CHECKS))
    meta = doc["pack"]
    lines = [cat.header(CFG).replace("framework/rules.yaml", f"packs/{path.name}") + f"# {meta['title']} pack", "",
             f"Version {meta['version']} · {meta.get('status', '')}. Loads by itself when `hdsf.yaml` lists "
             f"`{meta['jurisdiction']}` in `countries`. A pack can only add to HDSF or make it stricter.", "",
             "## Parameters", "", "| Parameter | Value |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in (doc.get("parameters") or {}).items()]
    lines += ["", "## Changes to HDSF rules", "", "| Rule | Change |", "|---|---|"]
    for a in doc.get("amend") or []:
        ch = []
        if a.get("level"):
            ch.append(f"strength {a['level']}")
        if a.get("tier"):
            ch.append(f"level {a['tier']}")
        if a.get("add_sources"):
            ch.append("adds " + ", ".join(a["add_sources"]))
        if a.get("note"):
            ch.append(a["note"])
        lines.append(f"| {a['rule']}: {m.rules[a['rule']]['title']} | {'; '.join(ch)} |")
    new = [m.rules[r["id"]] for r in doc.get("rules") or []]
    lines += ["", "## Rules added by the pack", "", "| ID | Rule | Strength | Level |", "|---|---|---|---|"]
    lines += [f"| [{r['id']}](#{cat.anchor(r)}) | {r['title']} | {r['level']} | {r['tier']} |" for r in new]
    lines.append("")
    for r in new:
        lines += cat.rule_block(CFG, r, m.sources)
    lines += ["## Sources added by the pack", ""]
    for s in doc.get("sources") or []:
        lines += [f"- **{s['id']}**: {s['title']}. {s['status']} Verified: {s['verified']}." + (f" [Link]({s['url']})" if s.get("url") else "")]
    return "\n".join(lines) + "\n"


def gdpr_map(version, rules):
    by, rid_rule = {}, {r["id"]: r for r in rules}
    for r in rules:
        for a in r.get("gdpr", []) or []:
            by.setdefault(str(a).split("(")[0], []).append((r["id"], str(a)))
    lines = [cat.header(CFG) + "# GDPR (RGPD) map", "",
             f"Which HDSF v{version} rules apply each article of the General Data Protection Regulation (in Portuguese, RGPD: "
             "Regulamento Geral sobre a Proteção de Dados) to digital health products. "
             "Health data is a special category (Art. 9), so most of the GDPR applies with extra care.", "",
             "In Portugal, Lei n.º 58/2019 adds national rules (Art. 29 on health and genetic data) and the CNPD supervises.", "",
             "| Article | What it covers | HDSF rules |", "|---|---|---|"]
    for art, title in GDPR_ARTICLES:
        hits = by.pop(art, [])
        cell = ", ".join(f"[{rid}](catalogue/{'core' if rid.startswith('CORE') else 'profile-' + rid[0].lower()}.md#{cat.anchor(rid_rule[rid])})"
                         + (f" ({a})" if a != art else "") for rid, a in hits) or "not a product rule (organisation-level)"
        lines.append(f"| Art. {art} | {title} | {cell} |")
    if by:
        errors.append(f"gdpr articles without a title in GDPR_ARTICLES: {sorted(by)}")
    lines += ["", "A rule can apply several articles; the article in brackets is the precise paragraph. "
              "Articles marked organisation-level still apply to the maker; HDSF covers them through its documents "
              "(DPIA, records, contracts) rather than product rules.", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- site
LIGHT = {"ink": "#12232e", "muted": "#4b5d68", "paper": "#fbfcfc", "panel": "#ffffff", "line": "#d9e2e6", "code": "#eef3f4",
         "teal": "#0f6e6e", "teal-t": "#0b5757", "on-teal": "#ffffff", "tint": "#e8f3f2", "warn": "#8a4b00", "note-bg": "#fff8ec",
         "note-line": "#f0d9b5", "field": "#b9c7cd", "ok-bg": "#e8f5ec", "err-bg": "#fdecea", "danger": "#b42318", "drop": "#9fb3bb",
         "sky": brand.LIGHT["sky"], "indigo": brand.LIGHT["indigo"], "lilac": brand.LIGHT["lilac"], "coral": brand.LIGHT["coral"]}
DARK = {"ink": "#e6eef0", "muted": "#a6b8c0", "paper": "#0f1a20", "panel": "#16252d", "line": "#2a3d47", "code": "#1d2f38",
        "teal": "#3fb8a8", "teal-t": "#6fd3c4", "on-teal": "#0b1418", "tint": "#16343a", "warn": "#f2c47a", "note-bg": "#2e2616",
        "note-line": "#5a4520", "field": "#3d5560", "ok-bg": "#173b2b", "err-bg": "#45201f", "danger": "#ff8a80", "drop": "#4f6872",
        "sky": brand.DARK["sky"], "indigo": brand.DARK["indigo"], "lilac": brand.DARK["lilac"], "coral": brand.DARK["coral"]}


def _vars(d):
    return ";".join(f"--{k}:{v}" for k, v in d.items())


TOKENS = (":root{" + _vars(LIGHT) + ";color-scheme:light}"
          "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){" + _vars(DARK) + ";color-scheme:dark}}"
          ":root[data-theme=dark]{" + _vars(DARK) + ";color-scheme:dark}"
          "@media print{:root,:root[data-theme=dark]{" + _vars(LIGHT) + ";color-scheme:light}.theme{display:none}}\n")
BRAND_LINK = '<a class="brand" href="{home}" aria-label="HDSF home">' + brand.inline_mark(30) + '<span class="wm">HD<span>SF</span></span></a>'


def head_meta(home, title, description, path=""):
    e = html.escape
    return (f'<link rel="icon" href="{home}favicon.svg" type="image/svg+xml"><link rel="icon" href="{home}favicon-32.png" sizes="32x32">'
            f'<link rel="apple-touch-icon" href="{home}apple-touch-icon.png"><meta name="theme-color" content="#0f6e6e">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="HDSF">'
            f'<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">'
            f'<meta property="og:image" content="{CFG.site}/social-preview.png">'
            f'<meta property="og:image:width" content="1280"><meta property="og:image:height" content="640">'
            f'<meta name="twitter:card" content="summary_large_image">')


THEME_HEAD = ("<script>try{var t=localStorage.getItem('hdsf-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>")
THEME_JS = ("<script>(function(){var r=document.documentElement,b=document.querySelector('[data-theme-toggle]');if(!b)return;"
            "function dark(){return r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches}"
            "function show(){var d=dark();b.setAttribute('aria-pressed',d);b.setAttribute('aria-label',d?'Switch to light mode':'Switch to dark mode');"
            "b.textContent=d?'\\u2600 Light':'\\u263E Dark'}"
            "b.addEventListener('click',function(){r.dataset.theme=dark()?'light':'dark';try{localStorage.setItem('hdsf-theme',r.dataset.theme)}catch(e){}show()});show()})()</script>")

CSS = TOKENS + """*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--teal-t)}a:focus-visible{outline:3px solid var(--teal);outline-offset:2px}
.in{max-width:1080px;margin:0 auto;padding:0 24px}header.top{border-bottom:1px solid var(--line);background:var(--panel)}
header.top .in{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:14px 24px}
.brand{font-weight:700;letter-spacing:.02em;color:var(--ink);text-decoration:none;font-size:20px}.brand span{color:var(--teal)}
nav{display:flex;gap:4px 16px;flex-wrap:wrap;font-size:.96rem}nav a{color:var(--ink);text-decoration:none;font-weight:500;padding:8px 0}@media (min-width:1000px){header.top .in{flex-wrap:nowrap}}nav a:hover{color:var(--teal)}
main{padding:32px 0 64px}article{max-width:820px}h1{font-size:2.1rem;line-height:1.2;margin:.2em 0 .5em}h2{margin-top:2em;font-size:1.45rem}h3{font-size:1.1rem;margin-top:1.6em}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.92rem;margin:1em 0}th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--tint)}td:first-child a{white-space:nowrap}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.9em}pre{background:#0f1c24;color:#e6eef2;padding:14px;border-radius:8px;overflow-x:auto}pre code{background:none;color:inherit;padding:0}
blockquote{margin:1em 0;padding:8px 16px;border-left:4px solid var(--teal);background:var(--tint)}
.meta{color:var(--muted);font-size:.9rem}.pill{display:inline-block;background:var(--tint);color:var(--teal-t);border-radius:99px;padding:2px 10px;font-weight:600;font-size:.82rem}
.hero{padding:48px 0 24px}.hero p.lead{font-size:1.2rem;color:var(--muted);max-width:760px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px}.card h3{margin-top:0}.card p{margin:.4em 0 0;color:var(--muted);font-size:.95rem}
.note{border:1px solid var(--note-line);background:var(--note-bg);color:var(--warn);border-radius:8px;padding:12px 16px;font-size:.95rem}
footer{border-top:1px solid var(--line);padding:24px 0;color:var(--muted);font-size:.88rem}
@media (prefers-reduced-motion:no-preference){a{transition:color .15s}}
.brand{display:inline-flex;align-items:center;gap:10px}.brand svg{flex:0 0 auto}.brand .wm{color:var(--ink)}.brand .wm span{color:var(--teal)}
.theme{font:inherit;font-size:.9rem;font-weight:600;padding:6px 12px;border:1px solid var(--line);border-radius:99px;background:var(--panel);color:var(--ink);cursor:pointer}
.theme:hover{border-color:var(--teal)}
"""
NAV = [("", "Home"), ("introduction/", "Introduction"), ("regulatory-map/", "Regulatory map"), ("qualification/", "Device question"),
       ("catalogue/", "Rules"), ("gdpr/", "GDPR"), ("workbench/", "Workbench"), ("using-hdsf/", "Use it"), ("legislation/", "Sources")]


def page(title, body, version, home, description):
    e = html.escape
    nav = "".join(f'<a href="{home}{h}">{e(t)}</a>' for h, t in NAV)
    return ("<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{e(title)} · HDSF</title><meta name=\"description\" content=\"{e(description)}\">"
            f"<link rel=\"stylesheet\" href=\"{home}style.css\">{head_meta(home, title + ' · HDSF', description)}{THEME_HEAD}</head>\n"
            f'<body><header class="top"><div class="in">{BRAND_LINK.replace("{home}", home)}<nav aria-label="Main">{nav}</nav><button class="theme" type="button" data-theme-toggle>Dark</button></div></header>\n'
            f'<main class="in"><article>{body}</article></main>\n'
            f'<footer><div class="in">Health Data Safety Framework (HDSF) v{e(version)}, maintained by Kendir Studios with contributors. '
            f'Content CC BY 4.0, code Apache-2.0. Not legal or regulatory advice. '
            f'<a href="{CFG.repo}">Repository</a> · Engine sfe {ENGINE_VERSION}, shared with <a href="https://csef.kendirstudios.pt">CSEF</a>.</div></footer>'
            f"{THEME_JS}</body></html>\n")


def _strip(text):
    return re.sub(r"<!--.*?-->\s*", "", text, flags=re.S)


def site(version, rules, sources, generated):
    files = {}
    docs = ROOT / "docs"
    links = {g: f"../{s}/" for g, s in GUIDES}
    links.update({"framework/legislation.md": "../legislation/", "framework/catalogue/index.md": "../catalogue/",
                  "framework/gdpr-map.md": "../gdpr/", "framework/catalogue/core.md": "../catalogue/core/",
                  "framework/catalogue/pack-pt.md": "../catalogue/pack-pt/"})
    for prof, fn in PROFILE_FILES.items():
        links[f"framework/catalogue/{fn}.md"] = f"../catalogue/{fn}/"
    for path, slug in GUIDES:
        t, body, _ = md.render((ROOT / path).read_text(encoding="utf-8"), "framework", links, None, CFG.repo, "hdsf.kendirstudios.pt")
        files[docs / slug / "index.html"] = page(t, f'<p class="meta"><span class="pill">HDSF v{version} guide</span></p>' + body, version, "../", t)
    cat_links = {f"framework/catalogue/{fn}.md": f"{fn}/" for fn in PROFILE_FILES.values()}
    t, body, _ = md.render(_strip(generated[ROOT / "framework" / "catalogue" / "index.md"]), "framework/catalogue", cat_links, None, CFG.repo, "hdsf.kendirstudios.pt")
    files[docs / "catalogue" / "index.html"] = page(t, body, version, "../", "All HDSF rules")
    sub_links = {f"framework/catalogue/{fn}.md": f"../{fn}/" for fn in PROFILE_FILES.values()}
    for prof, fn in PROFILE_FILES.items():
        t, body, _ = md.render(_strip(generated[ROOT / "framework" / "catalogue" / f"{fn}.md"]), "framework/catalogue", sub_links, None, CFG.repo, "hdsf.kendirstudios.pt")
        files[docs / "catalogue" / fn / "index.html"] = page(t, body, version, "../../", t)
    t, body, _ = md.render(_strip(generated[ROOT / "framework" / "legislation.md"]), "framework", links, None, CFG.repo, "hdsf.kendirstudios.pt")
    files[docs / "legislation" / "index.html"] = page(t, body, version, "../", "Sources cited by HDSF")
    t, body, _ = md.render(_strip(generated[ROOT / "framework" / "gdpr-map.md"]), "framework", links, None, CFG.repo, "hdsf.kendirstudios.pt")
    files[docs / "gdpr" / "index.html"] = page(t, body, version, "../", "GDPR (RGPD) articles and HDSF rules")
    n = len(rules)
    by = {p: sum(1 for r in rules if p in r["profiles"]) for p in PROFILE_FILES}
    cards = "".join(
        f'<a class="card" href="catalogue/{fn}/" style="text-decoration:none;color:inherit"><h3>{"Core" if p == "core" else "Profile " + p}</h3>'
        f'<p>{html.escape(CFG.profile_names[p])}. {by[p]} rules.</p></a>' for p, fn in PROFILE_FILES.items())
    home = (f'<section class="hero"><p class="meta"><span class="pill">v{version}, draft for comment</span></p>'
            "<h1>Health Data Safety Framework</h1>"
            '<p class="lead">Open, checkable rules for digital health products in the EU: wellness apps, medical device software, '
            "health records, research platforms and telehealth. One place to see which law applies, what it asks for "
            "and how to check your product.</p>"
            f"<p>{n} rules, {len(sources)} sources. Each rule says what to do, why (with its source), how to improve and how "
            "it is checked: in the code, in a short manifest (<code>hdsf.yaml</code>) or by a person.</p>"
            '<p><a href="introduction/">Start with the introduction</a> · <a href="qualification/">Is my software a medical device?</a> · '
            '<a href="using-hdsf/">Run the checks</a></p></section>'
            f'<h2>Profiles</h2><div class="cards">{cards}</div>'
            '<p class="note">HDSF is a draft and not legal or regulatory advice. Whether software is a medical device is the '
            "manufacturer's decision under the MDR or IVDR; ask a regulatory expert or a notified body when in doubt.</p>"
            '<h2>Built with CSEF</h2><p>HDSF shares its engine with the <a href="https://csef.kendirstudios.pt">Child-Safe EdTech '
            "Framework</a>. Health products used by children apply both.</p>")
    files[docs / "index.html"] = page("Health Data Safety Framework", home, version, "", "Open rules for digital health products in the EU")
    nav = "".join(f'<a href="../{h}">{html.escape(tt)}</a>' for h, tt in NAV)
    tpl = (ROOT / "tooling" / "workbench.template.html").read_text(encoding="utf-8")
    files[docs / "workbench" / "index.html"] = (tpl.replace("{version}", version).replace("{form}", workbench.form_html())
                                                .replace("{nav}", nav).replace("{pyodide}", PYODIDE)
                                                .replace("{theme_head}", head_meta("../", "Workbench · HDSF", "Check a digital health product without code. Nothing is uploaded.", "workbench/") + THEME_HEAD)
                                                .replace("{theme_js}", THEME_JS).replace("{brand}", BRAND_LINK.replace("{home}", "../")))
    files[docs / "workbench" / "hdsf-bundle.json"] = workbench.web_bundle(ROOT)
    files[docs / "workbench" / "example.json"] = workbench.example_bundle(ROOT)
    files[docs / "workbench" / "templates.json"] = workbench.templates_bundle(ROOT)
    for fn, title in (("pack-pt", "Portugal pack"),):
        t2, body, _ = md.render(_strip(generated[ROOT / "framework" / "catalogue" / f"{fn}.md"]), "framework/catalogue", sub_links, None, CFG.repo, "hdsf.kendirstudios.pt")
        files[docs / "catalogue" / fn / "index.html"] = page(t2, body, version, "../../", title)
    files[docs / "style.css"] = CSS
    files[docs / "favicon.svg"] = brand.svg_icon(brand.LIGHT)
    for name, text in brand.files().items():
        files[ROOT / "brand" / "svg" / name] = text
    files[docs / "CNAME"] = "hdsf.kendirstudios.pt\n"
    files[docs / ".nojekyll"] = ""
    return files


def skill_files():
    files = {}
    sk = ROOT / "skill" / "hdsf-review"
    for f in ("scan.py", "checks.py", "docreview.py", "export.py"):
        files[sk / "scripts" / f] = (ROOT / "tooling" / f).read_text(encoding="utf-8")
    for f in sorted((ROOT / "engine" / "sfe").glob("*.py")):
        files[sk / "scripts" / "sfe" / f.name] = f.read_text(encoding="utf-8")
    for f in ("framework.yaml", "rules.yaml", "sources.yaml"):
        files[sk / "framework" / f] = (ROOT / "framework" / f).read_text(encoding="utf-8")
    for f in sorted((ROOT / "packs").glob("*.yaml")):
        files[sk / "packs" / f.name] = f.read_text(encoding="utf-8")
    files[sk / "templates" / "hdsf.yaml"] = (ROOT / "templates" / "hdsf.yaml").read_text(encoding="utf-8")
    return files


def generate():
    version, rules, sources, watch = load()
    files = catalogue_files(version, rules, sources)
    files[ROOT / "framework" / "legislation.md"] = legislation(version, rules, sources, watch)
    files[ROOT / "framework" / "gdpr-map.md"] = gdpr_map(version, rules)
    files[ROOT / "framework" / "catalogue" / "pack-pt.md"] = pack_page(ROOT / "packs" / "pt.yaml", rules, sources)
    files[ROOT / "tooling" / "semgrep" / "hdsf.yml"] = cat.semgrep_yaml(CFG, rules)
    files.update(site(version, rules, sources, files))
    files.update(skill_files())
    return version, rules, sources, files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--validate-pack", metavar="PATH", help="check one pack file and stop")
    a = ap.parse_args(argv)
    if a.validate_pack:
        version, rules, sources, _ = load()
        from sfe import packs
        packs.validate(CFG, yaml.safe_load(Path(a.validate_pack).read_text(encoding="utf-8")), rules, sources, errors.append, set(checks.CHECKS))
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        print("OK: pack is valid." if not errors else f"{len(errors)} problem(s).")
        return 1 if errors else 0
    version, rules, sources, files = generate()
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    stale = []
    for path, text in files.items():
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != text:
            stale.append(path)
            if not a.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    if a.check:
        if stale:
            for p in stale:
                print("STALE:", p.relative_to(ROOT), file=sys.stderr)
            print("Run python3 tooling/build.py", file=sys.stderr)
            return 1
        print(f"OK: {len(rules)} rules, {len(sources)} sources; generated files up to date.")
    else:
        print(f"OK: {len(rules)} rules, {len(sources)} sources; {len(stale)} file(s) regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

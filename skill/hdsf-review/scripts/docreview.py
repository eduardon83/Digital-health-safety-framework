"""Review a product's documents against HDSF: privacy notice (GDPR/RGPD Art. 13 and 14), claims, safety and AI
wording, plain language, risk numbers, deceptive wording, and design recommendations from layers 2 and 3.

  python3 tooling/docreview.py --input docs/ [--input texts/] [--manifest hdsf.yaml] [--out-dir DIR]

Reads .md, .txt, .html, .json, .yaml, .strings, .po, .xml, .docx (python-docx) and .pdf (pypdf). English and
Portuguese wording is recognised. Signs, not proof; not legal advice. Licence: Apache-2.0
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import sys
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOC_EXT = {".md", ".txt", ".html", ".htm", ".json", ".yaml", ".yml", ".strings", ".po", ".xml", ".arb", ".docx", ".pdf", ".csv"}


# --------------------------------------------------------------------------- reading
def read_doc(p: Path) -> str:
    s = p.suffix.lower()
    try:
        if s == ".docx":
            try:
                import docx  # type: ignore
                d = docx.Document(str(p))
                parts = [x.text for x in d.paragraphs]
                for t in d.tables:
                    for row in t.rows:
                        parts.append(" | ".join(c.text for c in row.cells))
                return "\n".join(parts)
            except ImportError:
                with zipfile.ZipFile(p) as z:
                    xml = z.read("word/document.xml").decode("utf-8", "ignore")
                return htmlmod.unescape(re.sub(r"<[^>]+>", " ", xml.replace("</w:p>", "\n")))
        if s == ".pdf":
            from pypdf import PdfReader  # type: ignore
            return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
        t = p.read_text(encoding="utf-8", errors="ignore")
        if s in (".html", ".htm", ".xml"):
            t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
            t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
        return t
    except Exception as e:  # a broken file must not stop the review
        return f"[could not read: {e}]"


def collect(inputs) -> list[tuple[str, str]]:
    out = []
    for i in inputs:
        i = Path(i)
        files = [i] if i.is_file() else sorted(x for x in i.rglob("*") if x.is_file())
        for f in files:
            if f.suffix.lower() in DOC_EXT and f.name not in ("hdsf.yaml", "hdsf.yml"):
                out.append((str(f.relative_to(i.parent if i.is_file() else i)), read_doc(f)))
    return out


PT_WORDS = {"de", "que", "não", "para", "os", "uma", "com", "dados", "saúde", "você", "seus", "pelo", "são", "também"}
EN_WORDS = {"the", "and", "to", "of", "your", "data", "health", "you", "with", "for", "are", "this", "we"}


def language(text: str) -> str:
    w = re.findall(r"[a-zà-ú]+", text.lower())
    pt, en = sum(x in PT_WORDS for x in w), sum(x in EN_WORDS for x in w)
    return "pt" if pt > en else "en"


def snippet(text: str, m: re.Match, width: int = 90) -> str:
    a, b = max(0, m.start() - width // 2), min(len(text), m.end() + width // 2)
    return ("..." if a else "") + re.sub(r"\s+", " ", text[a:b]).strip() + ("..." if b < len(text) else "")


def find(docs, rx):
    for name, text in docs:
        m = re.search(rx, text, re.I)
        if m:
            return name, snippet(text, m)
    return None


# --------------------------------------------------------------------------- privacy notice
NOTICE_ITEMS = [
    ("Who the controller is and how to contact them", r"\b(data controller|controller is|responsável pelo tratamento|responsável do tratamento)\b|[\w.+-]+@[\w-]+\.[\w.]+", "CORE-COM-01", "13(1)(a)"),
    ("Contact of the data protection officer", r"\b(data protection officer|DPO|encarregad[oa] (da|de) proteção de dados)\b", "CORE-GOV-01", "13(1)(b)"),
    ("Purposes of processing", r"\b(purposes?|we use your (data|information) (to|for)|finalidades?|utilizamos os (seus )?dados para)\b", "CORE-COM-01", "13(1)(c)"),
    ("Legal basis for each purpose", r"\b(legal basis|lawful basis|legitimate interest|fundamento (jurídico|de licitude)|base (legal|jurídica)|interesse legítimo)\b", "CORE-DAT-02", "13(1)(c)"),
    ("How health data is handled (Art. 9 condition)", r"\b(health data|data concerning health|special categor\w+|explicit consent|dados (de|relativos à) saúde|categorias especiais|consentimento explícito)\b", "CORE-DAT-02", "9"),
    ("Who receives the data", r"\b(recipients?|third[- ]part(y|ies)|processors?|(service |hosting )?providers?|(we|do not|don.t) share|shared with|destinatários?|terceiros|subcontratantes?|prestadores? de serviços|partilhamos)\b", "CORE-DAT-07", "13(1)(e)"),
    ("Transfers outside the EU", r"\b(outside the (EU|EEA|European)|international transfers?|adequacy decision|standard contractual clauses|fora da (UE|União Europeia|EEE)|transferências? internacionais?|cláusulas contratuais)\b", "CORE-DAT-08", "13(1)(f)"),
    ("How long data is kept", r"\b(retain|retention|kept for|keep your data|store your data for|delete (your )?(data|account) after|conservação|prazo de conservação|conservados durante|guardamos os (seus )?dados)\b", "CORE-DAT-06", "13(2)(a)"),
    ("People's rights (access, correction, deletion, portability, objection)", r"\b(right (of|to) access|rectif\w+|erasure|portability|right to object|direito de acesso|retificação|apagamento|portabilidade|oposição)\b", "CORE-DAT-16", "13(2)(b)"),
    ("How to withdraw consent", r"\b(withdraw(n|al)?\b|retirar o (seu )?consentimento|revogar o consentimento|pode retirar)", "CORE-DAT-04", "13(2)(c)"),
    ("Right to complain to the authority", r"\b(supervisory authority|lodge a complaint|data protection authority|CNPD|autoridade de controlo|apresentar (uma )?reclamação)\b", "CORE-DAT-16", "13(2)(d)"),
    ("Automated decisions and profiling", r"\b(automated decisions?|automated decision-making|profiling|decisões? (individuais )?automatizadas?|definição de perfis)\b", "CORE-DAT-14", "13(2)(f)"),
]
NOTICE_HINT = re.compile(r"(privacy|privacidade|data protection|proteção de dados|rgpd|gdpr)", re.I)


def review_notice(docs):
    notice = [(n, t) for n, t in docs if NOTICE_HINT.search(n) or re.search(r"\b(privacy (policy|notice)|política de privacidade|aviso de privacidade)\b", t[:3000], re.I)]
    sec = {"title": "Privacy notice (GDPR / RGPD Art. 12 to 14)",
           "intro": "What people must be told when their data is collected. Checked by looking for the topics in your privacy notice; "
                    "a 'Found' means the topic is mentioned, not that the text is right.", "items": []}
    if not notice:
        sec["items"].append({"status": "gap", "title": "No privacy notice found", "rule": "CORE-COM-01",
                             "detail": "Add your privacy notice (a file named privacy or privacidade, or one that starts with 'Privacy policy' or 'Política de privacidade')."})
        return sec
    names = ", ".join(n for n, _ in notice)
    for title, rx, rule, art in NOTICE_ITEMS:
        hit = find(notice, rx)
        sec["items"].append({"status": "ok" if hit else "gap", "title": f"{title} (Art. {art})", "rule": rule,
                             "detail": f"Mentioned in {hit[0]}." if hit else f"Not found in {names}.",
                             "evidence": hit[1] if hit else ""})
    return sec


# --------------------------------------------------------------------------- claims, safety, AI
CLAIMS = r"\b(diagnos(e|es|is|ing)|detects? (cancer|diabetes|arrhythmia|atrial fibrillation|depression|disease)|cures?\b|treats? (depression|anxiety|diabetes|insomnia)|clinically (proven|validated)|medical[- ]grade|diagnostica|diagnóstico|deteta (o |a )?(cancro|diabetes|doença|depressão)|cura (a |o )?|trata (a |o )?(depressão|ansiedade|diabetes|insónia)|clinicamente (comprovad|validad)\w*)"
EMERGENCY = r"(\b112\b|emergency|emergência|urgência|SNS 24|808 24 24 24|crisis line|linha de crise|SOS Voz Amiga|not an emergency service|não é um serviço de emergência)"
AI_DISCLOSE = r"(\bAI\b|artificial intelligence|inteligência artificial|\bIA\b|chatbot|assistente virtual)"
NOT_CLINICIAN = r"(not a (doctor|clinician|medical professional)|does not replace (a |your )?(doctor|professional|medical advice)|não (é|substitui) (um |o |a )?(médico|profissional|aconselhamento médico))"


def review_claims_safety(docs, m):
    kind = ((m or {}).get("qualification") or {}).get("medical_device")
    feats = set((m or {}).get("features") or [])
    sec = {"title": "Claims, safety and AI wording", "intro": "Medical claims decide the device question; safety and AI wording protect people.", "items": []}
    hits, seen = [], set()
    for name, text in docs:
        for mm in re.finditer(CLAIMS, text, re.I):
            key = (name, mm.group(0).lower())
            if key not in seen:
                seen.add(key)
                hits.append((name, f"\"{mm.group(0)}\": " + snippet(text, mm)))
    if hits:
        st = "gap" if kind in ("none", None, "undecided") else "info"
        for name, ev in hits[:8]:
            sec["items"].append({"status": st, "title": "Medical claim" if st == "gap" else "Medical claim (check it matches the intended purpose)",
                                 "rule": "CORE-QUA-03", "detail": f"In {name}." + (" The product is not qualified as a medical device: rewrite or re-check the qualification." if st == "gap" else ""),
                                 "evidence": ev})
        if len(hits) > 8:
            sec["items"].append({"status": "info", "title": f"{len(hits) - 8} more medical claims", "detail": "See the documents."})
    else:
        sec["items"].append({"status": "ok", "title": "No medical claims found", "rule": "CORE-QUA-03", "detail": "None of the usual claim phrases appear in your documents."})
    if feats & {"symptom_input", "mental_health", "chat", "ai_generative", "emergency_content"}:
        hit = find(docs, EMERGENCY)
        sec["items"].append({"status": "ok" if hit else "gap", "title": "Route to urgent help", "rule": "CORE-SAF-01",
                             "detail": f"Mentioned in {hit[0]}." if hit else "No mention of 112, emergency services or a crisis line. Add a one-tap urgent help route and say the product is not an emergency service.",
                             "evidence": hit[1] if hit else ""})
    if feats & {"ai_generative", "ai_clinical"}:
        a, b = find(docs, AI_DISCLOSE), find(docs, NOT_CLINICIAN)
        sec["items"].append({"status": "ok" if a else "gap", "title": "Tells people they are dealing with AI", "rule": "CORE-AI-02",
                             "detail": f"Mentioned in {a[0]}." if a else "No AI disclosure found in the texts.", "evidence": a[1] if a else ""})
        sec["items"].append({"status": "ok" if b else "gap", "title": "Says the AI is not a clinician", "rule": "CORE-AI-03",
                             "detail": f"Mentioned in {b[0]}." if b else "Add a plain statement that the AI is not a doctor and does not replace medical advice.",
                             "evidence": b[1] if b else ""})
    return sec


# --------------------------------------------------------------------------- language
JARGON = {
    "en": {"hypertension": "high blood pressure", "myocardial infarction": "heart attack", "hypoglycaemia": "low blood sugar",
           "hypoglycemia": "low blood sugar", "hyperglycaemia": "high blood sugar", "hyperglycemia": "high blood sugar",
           "contraindicated": "should not be used", "adverse event": "side effect or harm", "prophylaxis": "prevention",
           "comorbidit": "other health conditions", "asymptomatic": "without symptoms", "benign": "not cancer", "chronic": "long-term",
           "acute": "sudden or short-term", "oral administration": "by mouth", "efficacy": "how well it works", "prognosis": "likely course",
           "cardiovascular": "heart and blood vessels", "pharmacological": "with medicines", "titrat": "adjust the dose step by step"},
    "pt": {"hipertensão": "tensão arterial alta", "enfarte do miocárdio": "ataque cardíaco", "hipoglicemia": "açúcar baixo no sangue",
           "hiperglicemia": "açúcar alto no sangue", "contraindicado": "não deve ser usado", "evento adverso": "efeito indesejado",
           "profilaxia": "prevenção", "comorbilidade": "outras doenças", "assintomático": "sem sintomas", "patologia": "doença",
           "administração oral": "pela boca", "eficácia": "quão bem funciona", "prognóstico": "evolução provável",
           "cardiovascular": "do coração e dos vasos", "farmacológico": "com medicamentos", "posologia": "como e quanto tomar"},
}
SENT = re.compile(r"[^.!?\n]+[.!?]")


def syllables(word: str) -> int:
    return max(1, len(re.findall(r"[aeiouyáàâãéêíóôõúü]+", word.lower())))


def readability(text: str, lang: str) -> dict | None:
    sents = [s.strip() for s in SENT.findall(text) if len(s.split()) >= 3]
    words = re.findall(r"[A-Za-zÀ-ú]+", " ".join(sents))
    if len(sents) < 5 or len(words) < 60:
        return None
    asl = len(words) / len(sents)
    asw = sum(syllables(w) for w in words) / len(words)
    score = 206.835 - 1.015 * asl - 84.6 * asw if lang == "en" else 248.835 - 1.015 * asl - 84.6 * asw
    long_s = sorted(sents, key=lambda s: -len(s.split()))
    return {"sentences": len(sents), "words": len(words), "avg_sentence": round(asl, 1), "score": round(score),
            "long_share": round(100 * sum(len(s.split()) > 25 for s in sents) / len(sents)), "longest": long_s[0][:240]}


def review_language(docs):
    sec = {"title": "Language and readability", "intro": "Plain language helps everyone, and almost half of people in an EU survey had limited health "
           "literacy (HLS-EU). Scores use Flesch reading ease (English) or its Portuguese adaptation: 60 or more is plain; below 40 is hard. "
           "Aim for sentences of 15 to 20 words on average.", "items": []}
    for name, text in docs:
        lang = language(text)
        r = readability(text, lang)
        if r:
            st = "ok" if r["score"] >= 60 and r["avg_sentence"] <= 20 else ("review" if r["score"] >= 40 else "gap")
            sec["items"].append({"status": st, "title": f"{name} ({'Portuguese' if lang == 'pt' else 'English'})", "rule": "CORE-LNG-01",
                                 "detail": f"Readability {r['score']} · {r['avg_sentence']} words per sentence · {r['long_share']}% of sentences over 25 words.",
                                 "evidence": f"Longest sentence: {r['longest']}" if st != "ok" else ""})
        found = [(t, alt) for t, alt in JARGON[lang].items() if re.search(r"\b" + re.escape(t), text, re.I)]
        if found:
            sec["items"].append({"status": "review", "title": f"Medical terms in {name}", "rule": "CORE-LNG-01",
                                 "detail": "Explain or replace: " + "; ".join(f"{t} → {alt}" for t, alt in found[:10]) + "."})
    if not sec["items"]:
        sec["items"].append({"status": "info", "title": "Not enough running text to score", "detail": "Add longer texts (onboarding, help, notices) to get readability scores."})
    return sec


# --------------------------------------------------------------------------- design and wording patterns
PATTERNS = [
    ("Confirmshaming (making people feel bad for saying no)", r"(no thanks,? I (don'?t|do not) (care|want to (be|get) (healthy|better))|I prefer to stay unhealthy|não,? obrigad[oa],? (não quero|prefiro não) (cuidar|melhorar))", "CORE-COM-04", "gap"),
    ("False urgency", r"\b(only today|last chance|offer ends (soon|today)|só hoje|última oportunidade|oferta termina hoje)\b", "CORE-COM-04", "gap"),
    ("Guilt or loss streaks about health", r"\b(you (failed|let yourself down)|you broke your streak|don'?t lose your streak|falhaste|perdeste a tua sequência|não percas a tua sequência)\b", "CORE-DES-06", "gap"),
    ("Fear to drive action", r"\b(before it'?s too late|you could die|antes que seja tarde|pode(s|rá)? morrer)\b", "CORE-DES-06", "gap"),
    ("Pre-selected consent", r"\b(pre-?ticked|checked by default|selecionad[oa] por defeito|pré-?selecionad[oa])\b", "CORE-DAT-04", "review"),
]
RISK_PCT = r"(\d+([.,]\d+)?\s?%[^.\n]{0,60}\b(risk|chance|likel|risco|probabilidade|hipótese)|\b(risk|risco)[^.\n]{0,60}\d+([.,]\d+)?\s?%|reduces? (the )?risk by|reduz o risco em)"
NOTIF = r"(notif|reminder|lembrete|push)[^\n]{0,80}\b(insulin|insulina|HIV|VIH|antidepress\w*|chemotherapy|quimioterapia|contracepti\w*|pílula|pregnan\w*|grávida)"


def review_patterns(docs):
    sec = {"title": "Design and wording patterns", "intro": "Wording that steers people, and how numbers and notifications are shown.", "items": []}
    for title, rx, rule, st in PATTERNS:
        hit = find(docs, rx)
        if hit:
            sec["items"].append({"status": st, "title": title, "rule": rule, "detail": f"In {hit[0]}.", "evidence": hit[1]})
    hit = find(docs, RISK_PCT)
    if hit:
        sec["items"].append({"status": "review", "title": "Risk shown as a percentage", "rule": "CORE-DES-01",
                             "detail": f"In {hit[0]}. Add natural frequencies (\"3 in 100 people\") and an icon array; avoid relative risk alone.",
                             "evidence": hit[1]})
    hit = find(docs, NOTIF)
    if hit:
        sec["items"].append({"status": "review", "title": "A notification may reveal health on the lock screen", "rule": "CORE-COM-03",
                             "detail": f"In {hit[0]}. Use a neutral default text.", "evidence": hit[1]})
    if not sec["items"]:
        sec["items"].append({"status": "ok", "title": "No problem patterns found", "detail": "No confirmshaming, false urgency, guilt, fear, pre-selected consent, percentage-only risks or revealing notifications were found."})
    return sec


# --------------------------------------------------------------------------- recommendations from layers 2 and 3
def _in_scope(r, m):
    profiles = set((m or {}).get("profiles") or ["core"]) | {"core"}
    users = set((m or {}).get("users") or [])
    feats = set((m or {}).get("features") or [])
    if not set(r["profiles"]) & profiles:
        return False
    if r.get("users", ["all"]) != ["all"] and users and not set(r["users"]) & users:
        return False
    if r.get("features") and not set(r["features"]) & feats:
        return False
    return True


def recommendations(m, rules, sources, tier: int, title: str, intro: str):
    sec = {"title": title, "intro": intro, "items": []}
    for r in sorted(rules, key=lambda r: r["id"]):
        if r["tier"] != tier or not _in_scope(r, m):
            continue
        if tier == 2 and not any(sources.get(s, {}).get("type") in ("guidance", "standard") for s in r["sources"]):
            continue
        sec["items"].append({"status": "info", "title": r["title"], "rule": r["id"], "detail": str(r["improvement"]).strip(),
                             "evidence": "Why: " + re.sub(r"\s+", " ", str(r["rationale"])).strip() + " Sources: " + ", ".join(r["sources"])})
    return sec


def run(inputs, manifest_path=None, root: Path = ROOT) -> list[dict]:
    rules = yaml.safe_load((root / "framework" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    sources = {s["id"]: s for s in yaml.safe_load((root / "framework" / "sources.yaml").read_text(encoding="utf-8"))["sources"]}
    m = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8")) if manifest_path and Path(manifest_path).exists() else {}
    docs = collect(inputs)
    read = {"title": "Documents read", "intro": f"{len(docs)} document(s). Nothing was sent anywhere.",
            "items": [{"status": "info", "title": n, "detail": f"{len(t.split())} words, {'Portuguese' if language(t) == 'pt' else 'English'}"
                       + (" (could not read)" if t.startswith("[could not read") else "")} for n, t in docs]}
    sections = [read]
    if docs:
        sections += [review_notice(docs), review_claims_safety(docs, m), review_language(docs), review_patterns(docs)]
    sections.append(recommendations(m, rules, sources, 2, "EU recommendations and guidance that apply (layer 2)",
                                    "What EU bodies, the WHO and standards recommend for a product like yours, beyond the law."))
    sections.append(recommendations(m, rules, sources, 3, "Design recommendations from research (layer 3)",
                                    "Best practice for design, UX, aesthetics and evidence, from peer-reviewed research and health app quality frameworks."))
    return sections


def to_markdown(sections) -> str:
    lines = ["# HDSF document review", ""]
    mark = {"ok": "Found", "gap": "Missing", "review": "Check", "info": "Note"}
    for s in sections:
        lines += [f"## {s['title']}", "", s.get("intro", ""), ""]
        for i in s["items"]:
            lines.append(f"- **{mark.get(i['status'], i['status'])}: {i['title']}**" + (f" ({i['rule']})" if i.get("rule") else "") + f". {i.get('detail', '')}")
            if i.get("evidence"):
                lines.append(f"  > {i['evidence']}")
        lines.append("")
    lines += ["Signs, not proof. Not legal or regulatory advice.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Review documents against HDSF")
    ap.add_argument("--input", action="append", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    sections = run(a.input, a.manifest)
    if a.out_dir:
        d = Path(a.out_dir)
        d.mkdir(parents=True, exist_ok=True)
        (d / "review.json").write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        (d / "review.md").write_text(to_markdown(sections), encoding="utf-8")
        gaps = sum(i["status"] == "gap" for s in sections for i in s["items"])
        print(f"Document review: {gaps} gap(s). Report in {d}")
    else:
        print(to_markdown(sections))
    return 0


if __name__ == "__main__":
    sys.exit(main())

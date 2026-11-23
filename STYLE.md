# HDSF writing style

Read this before you write or change any HDSF text: rules, guides, tool messages, reports, templates. It adapts the
maintainer's writing guide to a framework that people use to make decisions. `python3 tooling/stylecheck.py` checks
the parts a machine can check, and CI runs it.

## 1. Three jobs

1. **Keep the claim.** Say what the law, the guidance or the research says, at the strength it says it.
2. **Strip default style.** Remove the habits listed in section 3.
3. **Stay plain.** Write for a product owner who reads in a second language, not for a lawyer.

Never add a fact, a date, a number or a source that you did not check. If you cannot check it, mark the source
`verified: pending`.

## 2. Voice

- Short declarative sentences. One idea per sentence.
- Numbers first: dates, counts, article numbers, deadlines.
- Precise references: the article, the document, the date ("GDPR Art. 9(2)(a)", "applies from 2 Aug 2026").
- Say who does what ("The maker keeps a record", not "A record should be kept").
- Concrete nouns: manifest, DPIA, store listing, consent screen.
- No em-dashes. No Oxford comma. No "not X, but Y" frames. No self-praise and no overselling.

## 3. Habits to strip

| Habit | Example | Fix |
|---|---|---|
| Em-dash or spaced dash | "the app (and its SDKs) sends..." written with a dash | Comma, colon or two sentences |
| Contrast frame | "Signs, not proof" | State what it is: "The checks find signs. A person confirms them." | <!-- style-ok -->
| Tricolon by reflex | "fast, safe and simple" | Keep only what the source supports |
| Inflated words | crucial, pivotal, seamless, robust, leverage, unlock | "needed", "works", "uses" | <!-- style-ok -->
| Empty signposting | "It is important to note that" | Delete | <!-- style-ok -->
| Stacked hedges | "may possibly suggest" | One hedge, sized to the evidence | <!-- style-ok -->
| Summary echo | A last paragraph that repeats the section | Delete, or state the consequence |
| Abstract noun piles | "the implementation of the optimisation" | Use the verb |
| Oxford comma | "access, export, and delete" | "access, export and delete" | <!-- style-ok -->

## 4. Claims

Mark where a statement comes from and size the verb to it.

| Source | Verbs |
|---|---|
| Law (level 1) | "requires", "bans", "applies from" |
| Guidance, recommendations, standards (level 2) | "recommends", "reads the law as", "sets out" |
| Research and quality frameworks (level 3) | "found", "suggests", "is compatible with" |
| Automated checks | "finds a sign of", "may", "check" |

- A finding is a sign. A person confirms it. Never write that a scan "proves" anything or that a product "is compliant".
- One study "found" something; it does not "prove" it.
- Each rule cites at least one source; level 1 needs law, level 2 needs at least guidance or a standard.

## 5. Same thing, same word

Use the terms in the [glossary](framework/glossary.md) and keep them fixed. HDSF has **levels** (1, 2, 3), not
layers or tiers in text. A **maker** makes the product; a **person** uses it (not "user" in rules, except in field <!-- style-ok -->
names). **Health data** means data concerning health in the GDPR sense.

## 6. Numbers and dates

- English texts: decimal point, comma for thousands (15,838), dates as "2 Aug 2026" in rules and statuses.
- Portuguese texts: decimal comma, space for thousands (15 838), dates as "2 de agosto de 2026".
- Percentages with their base where the source gives it: "28.1% of 15,838 apps".

## 7. Portuguese

Texts in Portuguese use European Portuguese (pt-PT): equipa, registo, contacto, telemóvel, ecrã, utilizador,
ficheiro, "está a fazer". The Portugal pack and the document review flag Brazilian forms.

## 8. Neutrality

Describe what each law, body or study says. Do not take sides in open debates (for example the Digital Omnibus);
record them in the watch list.

## 9. Changing a text

1. Change the text.
2. Run `python3 tooling/stylecheck.py` and `python3 tooling/build.py`.
3. In the pull request, list each change to a number, date, article or source. Say why.

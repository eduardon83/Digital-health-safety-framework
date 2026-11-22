# Introduction

The Health Data Safety Framework (HDSF) is an open set of checkable rules for digital health products used in the
European Union. It covers wellness and lifestyle apps, medical device software, electronic health record systems,
research platforms and telehealth.

HDSF is a draft for public comment. It is not legal or regulatory advice.

## Why HDSF

Digital health sits where several EU laws meet. The GDPR treats health data as a special category. The MDR and IVDR
decide whether software is a medical device. The European Health Data Space (EHDS) adds rules for health records and
for wellness apps that connect to them, applying in stages from 2027. The AI Act, the Cyber Resilience Act, NIS2, the
Data Act and the new Product Liability Directive add more. Each law is clear on its own; together they are hard to
follow, above all for small teams.

The evidence shows why it matters. A study of 15,838 free health apps found that 28% had no privacy policy, and only
47% of the data they sent matched the policy they had ([Tangari 2021](https://doi.org/10.1136/bmj.n1248)). Of 36
top apps for depression and smoking cessation, 29 sent data to Facebook or Google services, and only 12 said so
([Huckvale 2019](https://doi.org/10.1001/jamanetworkopen.2019.2542)).

## What HDSF gives you

- **Rules** ([catalogue](catalogue/index.md)). Each rule says what to do, why (with its legal or other source), how
  to improve, how much effort it takes, and how it is checked.
- **A first question**: is your software a medical device? ([guide](02-qualification.md)). Every other answer depends on it.
- **A regulatory map** ([guide](01-regulatory-map.md)): which law applies to which kind of product, and from when.
- **A manifest**, `hdsf.yaml` ([template](../templates/hdsf.yaml)), that describes the product in one page.
- **A scanner** that reads the manifest and the code and writes a report ([how to use it](03-using-hdsf.md)).
- **Checklists** for a self-assessment by hand ([self-assessment](../self-assessment/core.md)).
- **Sources** with dates and their verification status ([legislation and evidence](legislation.md)).

## Profiles

Every product meets the **core** rules. Then it adds the profiles that fit; a product can have several.

| Profile | For | Examples |
|---|---|---|
| core | Every digital health product | Anything that processes health data |
| W | Wellness and lifestyle, no medical purpose | Fitness, sleep, diet, mood, cycle tracking |
| M | Medical device software (MDR or IVDR) | Symptom checkers that suggest a diagnosis, insulin dose calculators, AI that reads scans |
| E | EHR systems and the EHDS | Clinic and hospital record systems, patient portals |
| R | Research and secondary use | Study platforms, registries, data sharing for research |
| T | Telehealth and care delivery | Video consultations, remote monitoring services, care platforms |

Rules also depend on who uses the product (the public, patients, professionals, children) and on its features
(wearables, AI, chat, research use and others).

## Levels

| Level | Name | What it means |
|---|---|---|
| 1 | Legal baseline | Law in force, or adopted law. Meet it now. |
| 2 | Forward-compliant | Adopted law applying later (EHDS, CRA, AI Act high-risk dates), guidance and standards. Plan for it. |
| 3 | Best practice | What good products do beyond the law. |

**MUST** rules are required at their level. **SHOULD** rules are strongly recommended; skip one only with a
recorded reason.

## Children

Health products used by children also apply the [Child-Safe EdTech Framework (CSEF)](https://csef.kendirstudios.pt).
HDSF and CSEF share the same engine, so their reports look alike and can be read together.

## How HDSF is made

HDSF is maintained by Kendir Studios with contributors, under CC BY 4.0 (content) and Apache-2.0 (code). Every source
has a "verified" date or is marked "pending"; pending entries are listed first in the
[legislation page](legislation.md) and need a check. Contributions are welcome, above all national notes, checked
sources and real product cases.

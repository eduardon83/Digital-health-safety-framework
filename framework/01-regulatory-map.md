# Regulatory map

Which EU law applies to which kind of digital health product, and from when. Dates are as of November 2026; check
the [sources](legislation.md) for the current status. Not legal advice.

## The laws at a glance

| Law | What it covers in digital health | Applies | Profiles |
|---|---|---|---|
| GDPR | Health data as a special category (Art. 9); DPIA; security; rights | Since 2018 | all |
| ePrivacy Art. 5(3) | Any access to the user's device: SDKs, trackers, identifiers | In force | all |
| MDR | Software with a medical intended purpose (Rule 11) | Since 2021, transitional periods for legacy devices | M |
| IVDR | Software that analyses data from samples for a medical purpose | Since 2022, transitional periods | M |
| EHDS | EHR systems; wellness apps that claim interoperability; people's rights; secondary use | Stages from 26 Mar 2027, then 2029, 2031, 2035 | E, W, R |
| AI Act | Transparency (Art. 50); prohibitions; high-risk rules for medical device AI | Art. 50 from 2 Aug 2026; medical device AI from 2 Aug 2028 | all with AI, M |
| Cyber Resilience Act | Products with digital elements; not MDR or IVDR devices | Reporting from 11 Sep 2026; full from 11 Dec 2027 | W, E |
| NIS2 and national law | Health entities: care providers, some manufacturers | In force (Portugal: DL 125/2025, from 3 Apr 2026) | T, E |
| Data Act | Data from connected products (wearables); switching cloud services | Since 12 Sep 2025; design duty from 12 Sep 2026 | W, E |
| Product Liability Directive | Software as a product; psychological harm; missing updates | Products placed from 9 Dec 2026 | all |
| DSA | No ads based on health profiling on platforms; no dark patterns | Since 2024 | all platforms |
| Accessibility (WAD, EAA) | Public sector apps; some consumer services | In force | all |

## Start with the device question

The MDR and IVDR decide the most. If your software is a medical device, it needs CE marking, a quality management
system, clinical evidence and, above class I, a notified body. If it is not, you must keep it that way: your claims
and features must not give it a medical purpose. Read [the device question](02-qualification.md) first.

## The European Health Data Space

The EHDS ([Regulation (EU) 2025/327](https://eur-lex.europa.eu/eli/reg/2025/327/oj)) came into force on
26 March 2025 and applies in stages.

- **EHR systems** must have the European interoperability and logging components, pass testing and carry CE marking
  (rules E-INT-01, E-LOG-01).
- **Wellness applications** that claim they work with EHR systems must meet the same requirements, inform users,
  carry a label and be registered in an EU database. Interoperability never means automatic sharing; the person
  decides (W-EHD-01, W-EHD-02).
- **People** get rights over their electronic health data: access, export, restriction, information on who accessed
  it (CORE-DAT-09, E-ACC-01).
- **Secondary use**: health data holders, wellness apps included, may have to make data available to health data
  access bodies for research and policy (R-EHD-01).

## AI in health

- Any AI that talks to people says it is AI, from the first message (AI Act Art. 50, from 2 Aug 2026; CORE-AI-02).
- A general chatbot that gives personal diagnosis or treatment advice has a medical purpose. Either it is qualified as
  a device, or it must not do this (CORE-AI-03).
- AI that is a medical device and needs a notified body is a high-risk AI system. The AI Act adds its requirements on
  top of the MDR from 2 Aug 2028; the MDR class does not change (MDCG 2025-6; M-AI-01).

## Portugal

| Topic | Law or body |
|---|---|
| Health information | Lei n.º 12/2005 (information belongs to the person; access to the clinical record) |
| GDPR in Portugal | Lei n.º 58/2019 (Art. 29 on health and genetic data); CNPD supervises |
| Medical devices | INFARMED is the competent authority |
| Cybersecurity | Decreto-Lei n.º 125/2025 and CNCS Regulamento n.º 756/2026 (NIS2) |
| National health data services | SPMS (SNS digital services, national EHR) |

National notes for other Member States are welcome as contributions.

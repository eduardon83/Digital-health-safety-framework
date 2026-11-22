# The device question

Is your software a medical device? Every other HDSF answer depends on this one. This guide helps you ask it well
and record the answer. It does not answer it for you: the decision is the manufacturer's, under the MDR or IVDR,
and it often needs a regulatory expert or a notified body.

## The key idea: intended purpose

Qualification depends almost entirely on the intended purpose you claim, not on how the software works (MDCG
2019-11 rev. 1, June 2025). The same algorithm can be wellness in one app and a medical device in another, because
of what each app says it does.

So write the intended purpose first (CORE-QUA-01), and make every text match it (CORE-QUA-03): store listings,
website, onboarding, notifications, AI answers.

## The questions, in order

Follow the decision trees in [MDCG 2019-11 rev. 1](https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en)
and record your answer to each step.

1. **Is it software?** Not just data, a document or a database used as such.
2. **Does it drive or influence a hardware medical device?** Then it follows that device.
3. **Does it do more than store, archive, communicate or simply search data?** Software that only stores or sends
   data, without changing it for a medical result, is usually not a device.
4. **Is it for individual patients?** Software for population statistics or general knowledge usually is not a device.
5. **Does it have a medical purpose in MDR Article 2(1)?** Diagnosis, prevention, monitoring, prediction, prognosis,
   treatment or alleviation of disease; or of an injury or disability; and some other listed purposes.
6. **Does it analyse data from samples (in vitro)?** Then the IVDR applies instead of the MDR.
7. **Is it modular?** Some modules may be devices and others not. Mark the boundary clearly.
8. **Does it contain AI?** It qualifies the same way; if it is a device, the AI Act adds requirements (MDCG 2025-6).

## Signs you have a medical purpose

- It suggests a diagnosis, or a likely condition, for one person.
- It calculates a dose, or tells someone to change a treatment.
- It monitors a disease and alerts when values cross clinical thresholds.
- It predicts a disease risk for one person and suggests what to do.
- It claims to detect, treat, cure or prevent a disease.

## Signs you probably do not

- General fitness, sleep, diet or wellbeing tips, for people in general.
- Logging and showing data the person enters, without medical interpretation.
- Booking, payment, messaging or record keeping without changing the data for a medical result.

These are signs, not answers. Disease prevention software can fall under Rule 11; read the MDCG examples closely.

## If it is a device

- Find the class (MDR Annex VIII, Rule 11 for most software; IVDR Annex VIII).
- Set up the quality management system (ISO 13485) and software life cycle (IEC 62304), risk management (ISO
  14971), clinical evaluation (MDCG 2020-1) and post-market surveillance.
- Above class I (MDR) or class A (IVDR), you need a notified body.
- In app stores, show the device information before download, and list the app as a medical device (MDCG 2025-4).
- Profile M applies. Add `M` to `profiles` in `hdsf.yaml`.

## If it is not

- Profile W usually applies. Keep the product inside its purpose (W-QUA-01) and its texts free of medical claims
  (W-QUA-02).
- Check the qualification again at each release that adds a feature, a claim, an AI model or a user group
  (CORE-QUA-04).

## Record it

Copy [templates/qualification.md](../templates/qualification.md) to `docs/qualification.md`, answer each step, sign
and date it, and set in `hdsf.yaml`:

```yaml
qualification:
  medical_device: none      # none | mdsw | ivd | annex_xvi
  class: null
  rationale: docs/qualification.md
```

"Undecided" is a valid state while you build, but not a launch state: the scanner blocks it.

## Watch

The Commission proposed a targeted revision of the MDR and IVDR on 16 December 2025, which changes software
classification rules (MDR-REV). HDSF will update this guide when the text is adopted.

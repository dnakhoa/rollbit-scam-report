# Report 2: Complaint Corpus
## Rollbit / Bull Gaming N.V. — Canonical Public Complaint Record
**Date:** April 19, 2026 | **Classification:** Forensic Investigation
**Companion:** ← [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md) | → [Report 6: Evidence Register](./REPORT_6_EVIDENCE_REGISTER.md) | → [Report 7: Technical Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md) | → [Report 8: Public Records Capture](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md)

---

## Executive Summary

This report consolidates the public complaint record into one canonical corpus through **April 19, 2026**. After removing one explicit cross-post duplicate and excluding one X-only corroboration thread from the complaint totals, the corpus contains:

| Metric | Value |
|--------|-------|
| Counted public complaints | **80** |
| Quantified complaints | **74** |
| Total quantified amount | **$562,081.08** |
| More fully documented forum / mediation amount | **$295,178.56** |
| Trustpilot-style claimed amount | **$266,902.52** |
| Publicly resolved cases | **4** |
| Resolution rate | **5.0%** |
| Largest counted case | **$55,000** (`BTC-005`) |

The main corpus observation is not that every complaint proves wrongdoing on its own. It is that the same withdrawal-block, KYC-escalation, and multi-account language appears across **Bitcointalk, Trustpilot, Casino Guru, AskGamblers, and CasinoListings** over multiple years. The pattern is recurrent enough to justify source preservation and case-level review after the corpus is trimmed for explicit duplicates and labeled by confidence.

Anchor claims for this report are listed in [Report 6](./REPORT_6_EVIDENCE_REGISTER.md), especially `ER-01` through `ER-08`.

---

## 1. Corpus Rules

This complaint record is intentionally conservative:

- `80` cases are **counted in totals**.
- `74` of those cases contain an explicit public amount.
- Amounts are labeled either `confirmed` or `claimed`.
- `confirmed` means the amount comes from a more fully documented forum or mediation source such as Bitcointalk, Casino Guru, AskGamblers, or CasinoListings.
- `claimed` means the amount comes from a public review source such as Trustpilot where the amount is explicit but the supporting record is thinner.
- One explicit cross-post (`AG-002`) is preserved for provenance but excluded from totals because it duplicates `CL-001`.
- The X lawsuit/escalation item (`X-001`) is retained for corroboration but excluded from complaint totals so the social-media report does not become a parallel counting system.

Source breakdown for counted complaints:

| Source | Cases | Quantified Amount |
|--------|------:|------------------:|
| Bitcointalk | 20 | $257,797.00 |
| Trustpilot | 51 | $266,902.52 |
| Casino Guru | 7 | $27,481.56 |
| AskGamblers | 1 | $3,400.00 |
| CasinoListings | 1 | $6,500.00 |

This means the complaint totals should be read as a **publicly documented floor**, not a full measure of all disputed funds.

---

## 2. Observed Patterns

Across the counted corpus, the repeated behavior clusters into a small set of recurring categories:

| Category | Cases | Quantified Amount |
|----------|------:|------------------:|
| Multiple-account accusation | 31 | $152,867.56 |
| Account closure / balance made inaccessible | 18 | $62,868.52 |
| Win-triggered block | 12 | $193,970.00 |
| KYC / compliance delay loop | 9 | $52,705.00 |
| Sportsbook abuse label | 4 | $21,070.00 |
| Restricted-country enforcement at withdrawal stage | 3 | $34,100.00 |
| Futures pricing/trading allegation | 2 | $500.00 |
| Maintenance-window trading dispute | 1 | $44,000.00 |

**Observed facts**

- The single most common pattern is the **multiple-account accusation**, which appears in older Bitcointalk cases (`BTC-002`, `BTC-003`) and continues in newer 2025-2026 matters such as `BT-016`, `CG-006`, and `TP-049`.
- Several complaints describe a **clean operating period while the user is depositing or losing**, followed by KYC escalation or account restriction only after a larger withdrawal request or profitable streak (`BTC-005`, `BT-017`, `BT-018`, `TP-047`).
- Public mediation pages from Casino Guru repeatedly end with **non-cooperation / no-reaction language**, including `CG-004`, `CG-005`, and `CG-006`.

**Inference**

- The corpus is consistent with a post-withdrawal control pattern in which compliance, KYC, geography, or sportsbook-provider flags appear at the point where customer liabilities become more expensive.
- That inference is supported by the recurrence of similar language and timing, but it should still be stated as an inference rather than as a conclusively proven internal policy.

---

## 3. Technical Signal Extraction

[Report 7](./REPORT_7_TECHNICAL_DEEP_DIVE.md) adds a second layer on top of the category labels: keyword and compound-pattern extraction.

| Marker | Case Hits | Amount Linked |
|--------|----------:|--------------:|
| Withdrawal-control language | 48 | $316,929.08 |
| KYC/compliance escalation | 33 | $275,060.56 |
| Win/profit context | 35 | $390,931.00 |
| Multi-account / linked-account language | 29 | $178,402.56 |
| Named staff/team language | 8 | $69,287.56 |

Compound markers are more useful for triage than single keywords:

| Compound Pattern | Cases | Amount Linked |
|------------------|------:|--------------:|
| Withdrawal control + KYC escalation | 24 | $153,330.56 |
| Withdrawal control + win/profit context | 18 | $212,431.00 |
| Win/profit context + KYC escalation | 14 | $192,931.00 |
| Multi-account script + KYC escalation | 15 | $104,345.56 |
| Withdrawal control + KYC escalation + win/profit context | 7 | $83,401.00 |

These markers are not verdicts. They are a triage system for deciding which cases deserve raw-source re-capture, screenshot preservation, page hashing, and timeline reconstruction.

---

## 4. Timeline

Counted complaints and quantified public amounts by year:

| Year | Counted Cases | Quantified Amount |
|------|--------------:|------------------:|
| 2022 | 2 | $10,330.00 |
| 2023 | 4 | $45,961.00 |
| 2024 | 9 | $177,449.00 |
| 2025 | 47 | $257,513.00 |
| 2026 YTD | 13 | $46,017.08 |

Three timeline points matter most:

1. The complaint record did not stop in 2025. It remained active into **February, March, and April 2026**, including recent Trustpilot complaints `TP-046` through `TP-050`, Bitcointalk entries `BT-018` / `BT-019`, and Casino Guru entry `CG-006`.
2. The corpus is heaviest in **2025**, which is also the year in which broader custody, reserve-verification, and public-verification questions intensified elsewhere in the report set.
3. Even after the most recent refresh, the complaint record still shows only **four public resolutions**.

---

## 5. Representative Cases

The table below is not exhaustive. It is a cross-section chosen to show the complaint pattern across source types and dates.

| Case ID | Date | Source | Amount | What It Shows |
|---------|------|--------|-------:|---------------|
| `BTC-005` | 2024-07-20 | Bitcointalk | $55,000.00 | Major sports-betting win followed by KYC escalation and an indefinite third-party review claim |
| `BT-017` | 2025-04-21 | Bitcointalk | $30,000.00 | User says a winning streak was followed by a multi-account accusation after full KYC |
| `CG-004` | 2025-06-19 | Casino Guru | $3,189.00 | Public mediation record for a verified user whose withdrawal was blocked and account disabled |
| `BT-020` | 2025-11-24 | Bitcointalk | $530.00 | Smaller-balance case showing the same multi-account script even at lower dollar amounts |
| `CG-006` | 2026-02-03 | Casino Guru | $5,346.56 | Level-4-verified user says withdrawals were blocked for months without proof of linked accounts |
| `BT-018` | 2026-02-10 | Bitcointalk | $17,700.00 | Long-time user says services froze after KYC; thread later appeared as resolved |
| `BT-019` | 2026-02-11 | Bitcointalk | $3,000.00 | Account frozen after sports wins despite prior KYC approval |
| `TP-047` | 2026-04-12 | Trustpilot | $850.00 | Reviewer says funds were frozen after full KYC and returned to a shared deposit address |

These cases matter because they span:

- different public venues
- different balance sizes
- different years
- both sportsbook and casino-related activity

That supports cross-source review rather than a single-venue explanation.

---

## 6. Outcomes, Limits, and Interpretation

### Public outcomes

The public record currently shows four counted cases marked resolved:

- `BTC-007`
- `BTC-010`
- `BTC-014`
- `BT-018`

That does **not** prove there were no private resolutions. It does show that only a small share of the public record ends with a public resolution marker.

### Limits of the corpus

- Public complaints are not a random sample of all users.
- Trustpilot entries are real public signals, but they are generally weaker than forum threads with screenshots, timestamps, or mediation records.
- Some large public allegations were **not** pulled into the counted totals during this refresh because they lacked enough structured detail or risked double counting.
- Absence of a counted case is not proof that a complaint is false; it means the current public record was not specific enough to include cleanly.

### Analyst interpretation standard

The safest data-analysis phrasing is:

> The complaint corpus documents a recurrent pattern of reported withholding, account restriction, or post-win verification escalation. The pattern is enough to prioritize further collection, but individual allegations should still be evaluated on their own evidence.

Operationally, the next step is not legal argument. It is source preservation:

- re-capture high-value forum and mediation pages
- store screenshots and raw HTML
- hash captured pages
- separate confirmed, claimed, and unquantified cases in every chart
- manually adjudicate duplicate candidates before changing totals

---

## 7. Data Files and Cross-References

- [cases_database.json](./cases_database.json) — canonical complaint corpus with provenance fields
- [output/rollbit_cases.csv](./output/rollbit_cases.csv) — flat spreadsheet export
- [output/corpus_metrics.json](./output/corpus_metrics.json) — summary metrics used in this report
- [output/evidence_register.csv](./output/evidence_register.csv) — machine-readable claim register
- [output/technical_deep_dive.json](./output/technical_deep_dive.json) — technical signal extraction
- [output/forensic_indicators.csv](./output/forensic_indicators.csv) — analyst findings register
- [output/public_record_capture.json](./output/public_record_capture.json) — raw public-source capture summary
- [output/public_record_index.csv](./output/public_record_index.csv) — captured source index with hashes and file paths
- [Report 6: Evidence Register](./REPORT_6_EVIDENCE_REGISTER.md) — human-readable claim-to-source appendix

*Continue to [Report 3: Public X Evidence](./REPORT_3_X_TWITTER_EVIDENCE.md) for social-media corroboration, or back to [Report 1](./REPORT_1_ONCHAIN_FORENSICS.md) for the on-chain custody and reserve-verification analysis.*

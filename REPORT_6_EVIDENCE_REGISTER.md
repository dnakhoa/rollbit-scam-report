# Report 6: Evidence Register
## Claim-to-Source Appendix
**Date:** April 19, 2026 | **Classification:** Forensic Appendix

This appendix maps the main report-set claims to their supporting case IDs and public sources.

Machine-readable version: [output/evidence_register.csv](./output/evidence_register.csv)

---

| Claim ID | Report Section | Claim | Confidence |
|----------|----------------|-------|------------|
| `ER-01` | Report 2 / Executive summary | The complaint corpus contains **80 counted public complaints** through April 19, 2026. | High |
| `ER-02` | Report 2 / Executive summary | **74 counted complaints** include explicit amounts totaling **$562,081.08**. | High |
| `ER-03` | Report 2 / Executive summary | The quantified corpus splits into **$295,178.56** from more fully documented forum / mediation cases and **$266,902.52** from Trustpilot-style claimed amounts. | High |
| `ER-04` | Report 2 / Outcomes | Only **4 of 80** counted complaints are publicly marked resolved (**5.0%**). | High |
| `ER-05` | Report 2 / Pattern analysis | Multiple-account accusations recur across Bitcointalk, Casino Guru, and Trustpilot complaints. | High |
| `ER-06` | Report 2 / Pattern analysis | Several complaints describe KYC or compliance escalation only after a withdrawal request or winning period. | High |
| `ER-07` | Report 2 / Source quality | Casino Guru repeatedly described Rollbit complaints as unresolved under a no-reaction or non-cooperation pattern. | High |
| `ER-08` | Report 2 / Timeline | Counted complaints continued into **April 2026**. | Medium |
| `ER-09` | Report 3 / X corroboration | Selected X threads mirror the same withdrawal-block, KYC, and staff-conduct themes seen in the complaint corpus but are not counted as separate complaint totals. | Medium |
| `ER-10` | Report 0 / Synthesis | The complaint corpus is consistent with a counterparty-risk thesis even without claiming that public treasury wallets are empty. | High |

---

## Source Notes

### `ER-01` / `ER-02` / `ER-03`

- Derived from the canonical corpus in [cases_database.json](./cases_database.json) and its machine-readable summary file [output/corpus_metrics.json](./output/corpus_metrics.json).
- Totals exclude:
  - `X-001`, which is retained as corroboration only
  - `AG-002`, which is retained for provenance but excluded because it cross-posts `CL-001`

### `ER-04`

Resolved counted cases:

- `BTC-007` — https://bitcointalk.org/index.php?topic=5489049.0
- `BTC-010` — https://bitcointalk.org/index.php?topic=5489760.60
- `BTC-014` — https://bitcointalk.org/index.php?topic=5538532.0
- `BT-018` — https://bitcointalk.org/index.php?topic=5574081.0

### `ER-05`

Representative multi-account cases:

- `BTC-002` — https://bitcointalk.org/index.php?topic=5463996.40
- `BT-016` — https://bitcointalk.org/index.php?topic=5543348.0;wap
- `CG-004` — https://casino.guru/complaints/rollbit-casino-player-s-account-has-been-closed
- `CG-006` — https://casino.guru/complaints/rollbit-casino-player-s-withdrawal-is-blocked-for
- `TP-049` — https://www.trustpilot.com/review/www.rollbit.com

### `ER-06`

Representative post-withdrawal KYC / compliance escalations:

- `BTC-005` — https://bitcointalk.org/index.php?topic=5503600.0
- `BT-017` — https://bitcointalk.org/index.php?topic=5539143.0;wap
- `CG-006` — https://casino.guru/complaints/rollbit-casino-player-s-withdrawal-is-blocked-for
- `BT-018` — https://bitcointalk.org/index.php?topic=5574081.0
- `TP-047` — https://www.trustpilot.com/review/www.rollbit.com

### `ER-07`

Casino Guru complaints with public non-cooperation / unresolved language:

- `CG-004` — https://casino.guru/complaints/rollbit-casino-player-s-account-has-been-closed
- `CG-005` — https://casino.guru/complaints/rollbit-casino-player-s-withdrawals-are-blocked-by
- `CG-006` — https://casino.guru/complaints/rollbit-casino-player-s-withdrawal-is-blocked-for

### `ER-08`

April 2026 counted complaints:

- `TP-046`
- `TP-047`
- `TP-048`
- `TP-049`

Public source page: https://www.trustpilot.com/review/www.rollbit.com

### `ER-09`

Selected corroborating X threads:

- https://x.com/robertgambaskr/status/2029872445662937303
- https://x.com/robertgambaskr/status/1947015657050009696
- https://x.com/YtZlashy/status/1731639780713103506

These are used for corroboration only and are not counted as separate complaint totals.

### `ER-10`

Synthesis claim derived from:

- [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md)
- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 6: Evidence Register](./REPORT_6_EVIDENCE_REGISTER.md)

---

For line-by-line machine-readable claim data, use [output/evidence_register.csv](./output/evidence_register.csv).

# Publishing Notes
**Purpose:** keep the public repo forensic, reproducible, and carefully worded.

This repository should publish technical findings and testable suspicion. It should not present public complaints, attributed wallets, or token-market indicators as proof beyond what the artifacts show.

---

## Public Thesis

The strongest publishable finding is:

> Rollbit-linked public wallet balances exist, but they are not verified reserves.

The strongest publishable suspicion is:

> Public complaints repeatedly describe funds becoming inaccessible after withdrawals, wins, KYC/compliance escalation, or multiple-account accusations, while the public artifact set does not let an outside analyst reconstruct reserves, liabilities, exchange custody, withdrawal decisioning, RLB control, or token-market support.

That suspicion is enough to justify deeper forensic investigation. It does not prove intent, validate every complaint, or establish a complete custody map.

---

## Wording Rules

Use:

- "attributed public wallets"
- "visible wallet snapshot"
- "reported off-wallet custody event"
- "public-source complaint corpus"
- "claimed" vs "confirmed" complaint amounts
- "reasonable forensic suspicion"
- "not verified reserves"

Avoid:

- calling attributed wallets "reserves"
- implying every complaint is verified
- treating market cap as usable liquidity
- treating raw complaint count as proof of misconduct
- mixing direct outflows with mixed-flow alerts
- making legal conclusions in the technical reports

---

## Publication Checklist

Before publishing:

1. Confirm `.env*`, `.vscode/`, `.claude/`, `.cursor/`, `.idea/`, `.venv/`, caches, and raw captures are ignored.
2. Review firsthand victim material for consent and private identifiers.
3. Keep `output/captures/` local unless there is a separate rights/privacy review.
4. Publish summary artifacts: reports, charts, `output/*.json`, and `output/*.csv`.
5. Re-run `python3 scripts/run_investigation.py --quick` after report edits.
6. Treat `LEGAL_SUBMISSION_TEMPLATE.md` as optional downstream packaging, not the center of the repo.

---

## Raw Captures

`output/captures/` is intentionally ignored by git. It can contain raw HTML, headers, challenge pages, and extracted text from third-party public pages. For public release, the repo should publish the machine-readable indexes and hashes:

- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)
- [output/web_surface_capture.json](./output/web_surface_capture.json)

Raw captures can be regenerated with:

```bash
python3 scripts/web_surface_capture.py
python3 scripts/public_record_capture.py
```

# Rollbit Forensic Investigation
**Operator:** Bull Gaming N.V. (Curaçao No. 157086) | **Platform:** Rollbit.com
**Investigation Date:** April 19, 2026

This repo is an evidence pack, not a slogan. It combines live on-chain analysis, a canonical complaint corpus, website-technical inspection, and a source-backed news timeline to evaluate Rollbit's custody transparency, token-market structure, complaint patterns, and regulatory risk.

---

## Investigation Reports

### [Report 1: On-Chain Financial Forensics →](./REPORT_1_ONCHAIN_FORENSICS.md)
Live wallet state, treasury-flow review, RLB market-structure analysis, and source-backed corrections to earlier chain claims.

| Finding | Value |
|---------|-------|
| Visible known wallets (Apr 19, 2026) | **~$67.7M** |
| Ukraine-linked seizure reporting | **$123M** |
| RLB top 4 DEX pool liquidity | **~$4.7M** |
| RLB market cap | **~$101.2M** |
| Main conclusion | **High custody / counterparty opacity** |

### [Report 2: Complaint Corpus →](./REPORT_2_VICTIM_EVIDENCE.md)
Canonical public complaint record with provenance fields, explicit dedupe rules, and amount-status labeling.

| Finding | Value |
|---------|-------|
| Counted public complaints | **80** |
| Quantified complaints | **74** |
| Total quantified amount | **$562,081.08** |
| Public resolution rate | **5.0%** |
| Largest counted case | **$55,000** |
| Most common category | **Multiple-account accusation** |

### [Report 3: Public X Evidence →](./REPORT_3_X_TWITTER_EVIDENCE.md)
Selected X threads used as corroboration for timing, public escalation, and staff conduct. X posts are **not** counted as a separate complaint-total system.

### [Synthesis: Executive Summary & Forensic Hypothesis →](./REPORT_0_EXECUTIVE_SYNTHESIS.md)
High-level synthesis tying the on-chain, complaint, website, and timeline evidence together.

### [Report 4: Website Technical Investigation →](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md)
DNS, edge, TLS, stack, and public license-verification findings for `rollbit.com`, `blog.rollbit.com`, and `rollbot.rollbit.com`.

### [Report 5: News and Regulatory Timeline →](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md)
Dated chronology of public reporting, operator activity, treasury alerts, and regulatory developments.

### [Report 6: Evidence Register →](./REPORT_6_EVIDENCE_REGISTER.md)
Human-readable claim-to-source appendix. Machine-readable version: [output/evidence_register.csv](./output/evidence_register.csv).

---

## Key Evidence

1. **Known public wallets still show roughly `$67.7M`** as of April 19, 2026. The sharper issue is incomplete reserve visibility, not a public-wallet balance of zero.
2. **A Ukraine-linked seizure reported at `$123M`** remains central because it points to material off-wallet or exchange-linked custody exposure.
3. **RLB remains thin relative to its headline valuation** with only about `$4.7M` in top-pool DEX liquidity against roughly `$101.2M` market cap.
4. **The complaint corpus now has one canonical count**: `80` counted public complaints, `74` quantified, `$562,081.08` total quantified.
5. **Only four counted cases are publicly marked resolved**, which keeps the complaint record materially unresolved.
6. **The website and licensing picture remains incomplete enough to require manual verification**, especially for public certificate checks.

---

## Repository Structure

```text
rollbit_forensic/
├── REPORT_0_EXECUTIVE_SYNTHESIS.md
├── REPORT_1_ONCHAIN_FORENSICS.md
├── REPORT_2_VICTIM_EVIDENCE.md
├── REPORT_3_X_TWITTER_EVIDENCE.md
├── REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md
├── REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md
├── REPORT_6_EVIDENCE_REGISTER.md
├── LEGAL_SUBMISSION_TEMPLATE.md
│
├── scripts/
│   ├── blockchain_analyzer.py
│   ├── build_case_corpus.py
│   ├── generate_visualizations.py
│   ├── run_investigation.py
│   ├── treasury_monitor.py
│   └── victim_collector.py
│
├── output/
│   ├── blockchain_analysis.json
│   ├── corpus_metrics.json
│   ├── evidence_register.csv
│   ├── rollbit_analysis.json
│   ├── rollbit_cases.csv
│   └── charts/
│
├── cases_database.json
└── requirements.txt
```

---

## Running The Analysis

```bash
pip install -r requirements.txt

# Rebuild the canonical complaint corpus and evidence register
python scripts/build_case_corpus.py

# Generate charts from the current corpus and on-chain data
python scripts/generate_visualizations.py

# Run the on-chain investigation workflow
python scripts/run_investigation.py --quick
python scripts/run_investigation.py --full
```

---

## Filing / Reporting

Use [LEGAL_SUBMISSION_TEMPLATE.md](./LEGAL_SUBMISSION_TEMPLATE.md) as a starting point for a regulator, consumer-protection, or law-enforcement complaint. The most important attachments for a filing are:

- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 6: Evidence Register](./REPORT_6_EVIDENCE_REGISTER.md)
- [cases_database.json](./cases_database.json)
- [output/evidence_register.csv](./output/evidence_register.csv)
- [output/rollbit_cases.csv](./output/rollbit_cases.csv)

---

*Primary sources used in the current report set include Blockstream API, Solana RPC, CoinGecko, DEXScreener, dev.ua, ChainCatcher, official Rollbit blog pages, CGA policy pages, urlscan, Bitcointalk, Trustpilot, and Casino Guru.*

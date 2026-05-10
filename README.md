# Rollbit Forensic Investigation: Public Evidence Pack
**Operator:** Bull Gaming N.V. (Curaçao No. 157086) | **Platform:** Rollbit.com
**Investigation Date:** April 19, 2026

This repo is a technical forensic workspace. It combines on-chain analysis, custody-visibility modeling, token-market snapshots, website/infrastructure inspection, and a canonical public complaint corpus. Legal/regulatory material is downstream context, not the analytical center of gravity.

---

## Publication Lead

**Primary finding:** the repo has attributed public wallet balances, but it does **not** have Rollbit's verified reserve. Known BTC/SOL wallets showed about **$67.62M** on April 19, 2026, yet there is no liability-matched proof-of-reserves, complete custody inventory, exchange-balance attestation, or customer-fund segregation proof in the public artifact set.

**Analysis posture:** the repo should show what was observed, what could not be verified, and what data would be needed next. It should not ask readers to accept an opinion about intent.

**Most important correction:** do not describe attributed wallets as "reserves." The stronger finding is that the public wallet set is incomplete as a solvency, custody, or withdrawal-reliability model.

**External review attribution:** X user `Defi3000` flagged the need to remove opinion-led framing, re-check the treasury-flow interpretation, and correct the RLB liquidity venue framing. Those points are reflected in the current evidence-first wording.

Publication guidance lives in [PUBLISHING_NOTES.md](./PUBLISHING_NOTES.md).

---

## Investigation Reports

### [Report 1: On-Chain Financial Forensics →](./REPORT_1_ONCHAIN_FORENSICS.md)
Live wallet state, treasury-flow review, RLB public-market snapshot, and source-backed corrections to earlier chain claims.

| Finding | Value |
|---------|-------|
| Visible known wallets (Apr 19, 2026) | **~$67.7M** |
| Ukraine-linked seizure reporting | **$123M** |
| RLB tracked public DEX liquidity | **~$4.7M** |
| RLB market cap | **~$101.2M** |
| Main data gap | **Reserves, liabilities, venue depth, and operating controls are not publicly reconstructable** |

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

### [Synthesis: Executive Summary & Data Gaps →](./REPORT_0_EXECUTIVE_SYNTHESIS.md)
High-level synthesis tying the on-chain, complaint, website, and timeline evidence together.

### [Report 4: Website Technical Investigation →](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md)
DNS, edge, TLS, stack, and public license-verification findings for `rollbit.com`, `blog.rollbit.com`, and `rollbot.rollbit.com`.

### [Report 5: Public Event and Flow Timeline →](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md)
Dated chronology of public reporting, operator activity, treasury alerts, and source-backed context.

### [Report 6: Evidence Register →](./REPORT_6_EVIDENCE_REGISTER.md)
Human-readable claim-to-source appendix. Machine-readable version: [output/evidence_register.csv](./output/evidence_register.csv).

### [Report 7: Technical Forensic Deep Dive →](./REPORT_7_TECHNICAL_DEEP_DIVE.md)
Computed technical indicators across custody visibility, RLB market data scope, complaint-pattern signals, duplicate review, and web acquisition gaps.

| Finding | Value |
|---------|-------|
| Attributed public wallet snapshot | **$67.62M** |
| Direct outflows / visible wallet snapshot | **25.7%** |
| Reported off-wallet event / visible wallet snapshot | **181.9%** |
| Tracked public DEX liquidity / market cap | **4.7%** |
| Withdrawal-control keyword hits | **48 cases** |
| KYC/compliance keyword hits | **33 cases** |

### [Report 8: Public Records and Complaint Capture →](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md)
Raw public-source preservation layer for complaint pages, public reporting, operator publications, verification pages, passive scans, and social corroboration links.

| Finding | Value |
|---------|-------|
| Deduplicated public targets captured | **53** |
| HTTP captures written | **52** |
| Bitcointalk complaint threads captured | **21 / 21** |
| Trustpilot automated capture result | **HTTP 403 challenge** |
| Casino Guru automated capture result | **7 URLs returned 404** |

### [Report 9: External Review Fact-Check Matrix →](./REPORT_9_EXTERNAL_REVIEW_FACT_CHECK.md)
Quality-control appendix mapping `Defi3000` feedback to corrected report language and remaining collection tasks.

---

## Key Technical Evidence

1. **Known public wallets still show roughly `$67.7M`** as of April 19, 2026, but those balances are **not verified reserves**. The sharper issue is the absence of a liability-matched proof-of-reserves view.
2. **A Ukraine-linked seizure reported at `$123M`** remains central because it points to material off-wallet or exchange-linked custody exposure.
3. **RLB market data is incomplete in this repo.** The current snapshot captures about `$4.7M` in tracked public DEX liquidity against roughly `$101.2M` market cap, but it does **not** quantify Rollbit app/on-platform liquidity, order-book depth, or custody-side token inventory. It should not describe Uniswap as the only RLB trading or liquidity venue.
4. **The complaint corpus now has one canonical count**: `80` counted public complaints, `74` quantified, `$562,081.08` total quantified.
5. **Only four counted cases are publicly marked resolved**, which keeps the complaint record materially unresolved.
6. **The technical deep-dive now extracts process signatures**: withdrawal-control language appears in `48` counted cases, KYC/compliance escalation in `33`, and win/profit context in `35`.
7. **The website surface requires split acquisition** because the main app is Cloudflare challenge-gated while the public blog is separately hosted and indexable.
8. **The key unresolved intersection is cross-dataset, not a single artifact:** user-reported fund restrictions, no public reserve proof, unclear operating controls, unknown token-control attribution, and incomplete venue-depth data for RLB.

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
├── REPORT_7_TECHNICAL_DEEP_DIVE.md
├── REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md
├── REPORT_9_EXTERNAL_REVIEW_FACT_CHECK.md
├── LEGAL_SUBMISSION_TEMPLATE.md
├── PUBLISHING_NOTES.md
├── .gitignore
│
├── scripts/
│   ├── blockchain_analyzer.py
│   ├── build_case_corpus.py
│   ├── generate_visualizations.py
│   ├── public_record_capture.py
│   ├── run_investigation.py
│   ├── technical_deep_dive.py
│   ├── treasury_monitor.py
│   ├── complainant_collector.py
│   └── web_surface_capture.py
│
├── output/
│   ├── blockchain_analysis.json
│   ├── corpus_metrics.json
│   ├── evidence_register.csv
│   ├── forensic_indicators.csv
│   ├── public_record_capture.json
│   ├── public_record_index.csv
│   ├── technical_deep_dive.json
│   ├── web_surface_capture.json
│   ├── captures/              # local raw captures; ignored by git
│   ├── rollbit_analysis.json     # superseded legacy stub
│   ├── rollbit_cases.csv
│   └── charts/
│
├── cases_database.json
└── requirements.txt
```

---

## Publishable vs Local Artifacts

Publishable artifacts:

- reports `REPORT_0` through `REPORT_8`
- source index and computed outputs under `output/*.json` and `output/*.csv`
- charts under `output/charts/`
- scripts needed to reproduce captures and indicators

Local/private artifacts:

- `output/captures/` raw HTML/headers/bodies are ignored by git by default
- `.env*`, `.vscode/`, `.claude/`, `.cursor/`, `.idea/`, `.venv/`, caches, and OS files are ignored by git
- firsthand complainant material should be reviewed for consent and private identifiers before publishing

---

## Running The Analysis

```bash
pip install -r requirements.txt

# Rebuild the canonical complaint corpus and evidence register
python scripts/build_case_corpus.py

# Generate charts from the current corpus and on-chain data
python scripts/generate_visualizations.py

# Generate technical forensic indicators
python scripts/technical_deep_dive.py

# Capture DNS/TLS/HTTP web-surface artifacts
python scripts/web_surface_capture.py

# Capture complaint/public-record source pages
python scripts/public_record_capture.py

# Run the on-chain investigation workflow
python scripts/run_investigation.py --quick
python scripts/run_investigation.py --full
python scripts/run_investigation.py --capture-public-records
```

---

## Forensic Analyst Workflow

Start with the technical artifacts, not the legal template:

- [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md)
- [Report 4: Website Technical Investigation](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md)
- [Report 7: Technical Forensic Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)
- [cases_database.json](./cases_database.json)
- [output/blockchain_analysis.json](./output/blockchain_analysis.json)
- [output/technical_deep_dive.json](./output/technical_deep_dive.json)
- [output/forensic_indicators.csv](./output/forensic_indicators.csv)
- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)
- [output/web_surface_capture.json](./output/web_surface_capture.json)
- [output/rollbit_cases.csv](./output/rollbit_cases.csv)

The legal submission template remains available as an optional downstream packaging aid, but it should not drive the investigation. The core job is to preserve artifacts, classify flows correctly, separate confirmed from claimed complaint data, and identify testable data gaps.

---

*Primary sources used in the current report set include Blockstream API, Solana RPC, CoinGecko, DEXScreener, dev.ua, ChainCatcher, official Rollbit blog pages, CGA policy pages, urlscan, Bitcointalk, Trustpilot, and Casino Guru.*

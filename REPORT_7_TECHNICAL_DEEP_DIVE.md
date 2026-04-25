# Report 7: Technical Forensic Deep Dive
## Artifact Quality, Custody Visibility, Liquidity Stress, and Complaint Signal Extraction
**Generated:** April 25, 2026 | **Data Freeze:** April 19, 2026 | **Classification:** Technical Forensic Work Product

This report is deliberately technical. It does not try to argue a legal theory. It turns the repository's existing artifacts into forensic indicators that can be tested, re-run, contradicted, or expanded.

Machine-readable outputs:

- [output/technical_deep_dive.json](./output/technical_deep_dive.json)
- [output/forensic_indicators.csv](./output/forensic_indicators.csv)
- [output/web_surface_capture.json](./output/web_surface_capture.json)
- [output/public_record_capture.json](./output/public_record_capture.json)

---

## 1. Analyst Scope

The objective is to answer technical questions:

- What is directly observable from attributed public wallets?
- What is not observable about reserves, liabilities, and operating controls?
- Which high-value flow claims are direct outflows, inflows, mixed-flow alerts, or off-wallet custody events?
- How thin is RLB liquidity relative to market capitalization?
- Which complaint patterns repeat as structured signals rather than isolated anecdotes?
- Which artifacts need re-capture before relying on them further?

Legal and regulatory references are treated only as source context or custody-location signals.

---

## 2. Technical Findings Register

| ID | Severity | Confidence | Finding |
|----|----------|------------|---------|
| `TF-01` | High | High | Known public wallets are **not verified reserves**. The loaded wallet snapshot shows **$67,620,165.30**, but there is no proof-of-reserves system tying those balances to customer liabilities or segregated custody. |
| `TF-02` | Medium | High | Direct published outflows are bounded at **$17,400,000.00**, equal to **25.7%** of the visible wallet snapshot. Mixed BTC alerts must stay separated from direct outflows. |
| `TF-03` | High | High | RLB top-four DEX pool liquidity is **$4,713,083.87**, only **4.7%** of the **$101,223,201** market cap. |
| `TF-04` | High | Medium | Seven counted cases mention withdrawal control, KYC/compliance escalation, and win/profit context together, totaling **$83,401.00**. |
| `TF-05` | High | High | Multiple-account accusation is the dominant dispute script: **31 of 80** counted complaints by category, and **29** keyword hits for linked-account language. |
| `TF-06` | Medium | High | Corpus fidelity must be split by evidence class: **27** quantified cases are confirmed and **47** are claimed. |
| `TF-07` | Medium | High | Duplicate risk is bounded but not zero: the heuristic found **3** candidate pairs for manual review. |
| `TF-08` | Medium | High | Web acquisition should preserve Cloudflare-gated app artifacts separately from Ghost/Fastly blog artifacts. |
| `TF-09` | High | Medium | Operating controls and token-control attribution remain insufficiently mapped in this repo. Public material does not yet establish who controls exchange custody, RLB market operations, or withdrawal decisioning. |
| `TF-10` | Medium | High | Complaint/public-record acquisition is now reproducible, but some public sources require browser-aware follow-up. |

**Highest-signal suspicion:** the strongest concern is not any single wallet, complaint, or token metric. It is the overlap between user-reported locked funds, repeated multiple-account/KYC scripts, no public liability-matched reserve proof, incomplete custody visibility, and incomplete RLB control attribution.

---

## 3. On-Chain Custody Visibility Model

The central correction is simple:

> The repo has attributed public wallet balances. It does **not** have Rollbit's reserve.

A reserve claim would require, at minimum:

- a complete address and exchange-account inventory
- customer-liability totals at the same timestamp
- proof that customer assets are segregated from operating capital
- signatures or attestations proving control of claimed wallets
- reconciliation between on-chain assets, exchange balances, and user balances
- repeatable snapshots with raw evidence preserved

None of that exists in the current public artifact set.

### 3.1 Loaded wallet snapshot

The corrected cached analyzer now preserves the April 19 wallet snapshot instead of treating missing live API data as zero.

| Metric | Value |
|--------|-------|
| Attributed public wallet value | **$67,620,165.30** |
| BTC treasury value | **$48,758,133.54** |
| SOL treasury value | **$18,862,031.76** |
| Tracked ETH wallet value | **$0.00** |
| Direct published outflows | **$17,400,000.00** |
| January 2026 direct outflows | **$7,230,000.00** |
| Known published inflow | **$45,190,000.00** |
| Mixed-flow BTC alerts | **$56,120,000.00** |
| Reported off-wallet custody event | **$123,000,000.00** |

### 3.2 Ratio tests

| Ratio | Value | Interpretation |
|-------|-------|----------------|
| Direct outflows / visible wallet snapshot | **25.7%** | Material, but not a reserve-coverage result |
| January 2026 direct outflows / visible wallet snapshot | **10.7%** | Large enough to track, too small to call a full drain |
| Reported off-wallet event / visible wallet snapshot | **181.9%** | Strong custody-location signal; public wallets are not a reserve map |

### 3.3 Working custody hypotheses

| Hypothesis | Current Status | Required Test |
|------------|----------------|---------------|
| Public treasury wallets are operational hot/treasury wallets, not verified reserves | Plausible | Compare sustained wallet balances against known liabilities, exchange custody, and public flow alerts |
| Some material reserves historically sat in exchange or proxy custody | Plausible from public reporting | Preserve court/news source text, exchange-account details, and any linked chain traces |
| Mixed BTC alerts prove Rollbit outflows | Not supported as stated | Require transaction graph directionality and counterparty ownership evidence |

The technical point is narrower and stronger than a legal framing: the visible wallet set is an incomplete custody graph, not proof of reserves.

---

## 4. RLB Market Structure Stress

| Metric | Value |
|--------|-------|
| RLB price | **$0.059523** |
| Market cap | **$101,223,201** |
| Top-four DEX pool liquidity | **$4,713,083.87** |
| Top-four 24h volume | **$153,106.24** |
| Liquidity / market cap | **4.66%** |
| 24h volume / liquidity | **3.25%** |
| Days to turn visible liquidity at 24h volume | **30.8 days** |
| 1% market-cap notional / liquidity | **21.5%** |
| 5% market-cap notional / liquidity | **107.4%** |

Forensic implication: RLB market cap is not usable as a reserve proxy. The token may have a nine-figure headline valuation while the visible exit surface is only a few million dollars across top pools.

The same caution applies to token governance and attribution. This repo does not yet contain a complete, independently verified map of:

- RLB deployer/admin control paths
- top holder clusters
- market-making wallets
- buy-and-burn execution wallets
- exchange custody paths for token inventory
- team, founder, or affiliate wallets tied to token operations

Until that map exists, RLB should be treated as an opaque market surface rather than a transparent balance-sheet asset.

Next technical work:

- Capture pool reserves, fee tiers, ticks, and pool addresses.
- Build a slippage model for 1%, 2.5%, 5%, and 10% market-cap exits.
- Compare buy-and-burn claims against on-chain burn/buy transactions and actual pool depth.
- Track holder concentration and top-wallet movement around promotion windows.

---

## 5. Complaint Corpus Signal Extraction

The complaint corpus is not treated as proof of each allegation. It is treated as a structured signal dataset with provenance and evidence-class labels.

### 5.1 Keyword marker extraction

| Marker | Case Hits | Amount Linked |
|--------|-----------|---------------|
| Withdrawal-control language | **48** | **$316,929.08** |
| KYC/compliance escalation | **33** | **$275,060.56** |
| Win/profit context | **35** | **$390,931.00** |
| Multi-account / linked-account language | **29** | **$178,402.56** |
| Named staff/team language | **8** | **$69,287.56** |
| Support silence / ignored language | **6** | **$39,746.00** |
| Return-to-origin-address issue | **1** | **$5,200.00** |
| Maintenance/futures/market-event language | **3** | **$44,500.00** |

### 5.2 Compound trigger patterns

| Compound Pattern | Cases | Amount Linked |
|------------------|-------|---------------|
| Withdrawal control + KYC escalation | **24** | **$153,330.56** |
| Withdrawal control + win/profit context | **18** | **$212,431.00** |
| Win/profit context + KYC escalation | **14** | **$192,931.00** |
| Multi-account script + KYC escalation | **15** | **$104,345.56** |
| Withdrawal control + KYC escalation + win/profit context | **7** | **$83,401.00** |

The compound patterns are more useful than raw complaint count. They identify repeatable process signatures: a user reports a withdrawal or profit event, then verification/compliance or linked-account language appears.

### 5.3 Source fidelity

| Source | Tier | Cases | Quantified | Confirmed | Claimed | Amount |
|--------|------|-------|------------|-----------|---------|--------|
| Trustpilot | Review-page claim | 51 | 47 | 0 | 47 | **$266,902.52** |
| Bitcointalk | Direct forum thread | 20 | 19 | 19 | 0 | **$257,797.00** |
| Casino Guru | Mediated complaint page | 7 | 6 | 6 | 0 | **$27,481.56** |
| AskGamblers | Mediated complaint page | 1 | 1 | 1 | 0 | **$3,400.00** |
| CasinoListings | Mediated complaint page | 1 | 1 | 1 | 0 | **$6,500.00** |

This split matters. Trustpilot is high-volume but lower-fidelity. Bitcointalk and mediation pages are lower-volume but stronger for technical case reconstruction.

### 5.4 Category severity ranking

The technical severity score weights amount, unresolved rate, and evidence class. It is not a legal conclusion.

| Rank | Category | Cases | Amount | Unresolved Rate |
|------|----------|-------|--------|-----------------|
| 1 | Winning block | 12 | **$193,970.00** | **100.0%** |
| 2 | Multiple-account accusation | 31 | **$152,867.56** | **93.6%** |
| 3 | Maintenance-window trading dispute | 1 | **$44,000.00** | **100.0%** |
| 4 | Account closure | 18 | **$62,868.52** | **100.0%** |
| 5 | KYC delay tactic | 9 | **$52,705.00** | **88.9%** |

---

## 6. Duplicate Review Queue

The generator does not auto-delete duplicate candidates. It flags them for analyst review.

| Candidate A | Candidate B | Amount | Date Delta | Reason To Review |
|-------------|-------------|--------|------------|------------------|
| `TP-011` | `TP-012` | $5,000 / $5,000 | 8 days | Same source, same amount, same category |
| `TP-027` | `TP-026` | $600 / $600 | 21 days | Same source, same amount, same category |
| `CG-005` | `TP-019` | $1,935 / $1,935 | 13 days | Cross-source amount/category match |

Until manually adjudicated, these remain candidates only. Corpus totals should not change automatically.

---

## 7. Web and Infrastructure Acquisition Plan

The web surface has two different capture problems:

| Surface | Observed Pattern | Acquisition Priority |
|---------|------------------|----------------------|
| `rollbit.com` | Cloudflare challenge-gated application edge | Preserve DNS, TLS, edge headers, challenge HTML, challenge scripts, and response hashes |
| `rollbot.rollbit.com` | Same Cloudflare edge IPs as main site | Preserve DNS and TLS alongside main domain |
| `blog.rollbit.com` | Ghost on Fastly, public HTML | Preserve full HTML, RSS, post metadata, authorship data, and article timestamps |
| `cert.cga.cw` path | Public verification path inconclusive on snapshot date | Preserve request URL, redirect chain, response body, screenshot, and timestamp |

The new capture utility [scripts/web_surface_capture.py](./scripts/web_surface_capture.py) produced a current capture bundle at:

- [output/web_surface_capture.json](./output/web_surface_capture.json)
- local raw-capture directory: `output/captures/web/20260425T104619Z`

The raw capture directory is ignored by git for public release. Publish the JSON summary and hashes; keep raw bodies local or private.

April 25, 2026 capture highlights:

| Target | HTTP Result | Body SHA-256 Prefix |
|--------|-------------|---------------------|
| `rollbit.com` | HTTP/2 403 | `4be5da3178ba0422` |
| `blog.rollbit.com` | HTTP/2 200 | `234ca47b237f4ab9` |
| `rollbot.rollbit.com` | HTTP/2 200 | `a18a6c7921ee03fa` |
| `cert.cga.cw/page/certification_policy` | HTTP/2 200 | `8c138281c463af80` |

Minimum acquisition bundle per web capture:

- raw request command and exact timestamp
- DoH JSON for A, AAAA, CNAME, NS, and TXT where available
- TLS certificate output with subject, issuer, validity window, SANs, and fingerprint
- HTTP status, headers, redirect chain, and body hash
- screenshot where browser rendering matters
- urlscan or archive reference where live capture is blocked

---

## 8. Priority Technical Work Queue

1. Re-run live wallet snapshots and store raw API responses under `output/captures/`.
2. Add transaction graph exports for the January 2026 SOL outflows with source, destination, slot/signature, and known labels.
3. Build RLB pool-depth and slippage modeling from Uniswap pool state, not only DEXScreener aggregate fields.
4. Re-capture high-value direct forum and mediation cases with HTML hashes and screenshots.
5. Manually adjudicate the three duplicate candidates.
6. Follow up on [Report 8](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md) capture gaps: Trustpilot browser capture, Casino Guru 404 review, and archived missing pages.
7. Add a reproducible web capture script for DNS, TLS, headers, challenge HTML, and blog metadata.
8. Build an RLB control map: deployer, admin rights, burn wallets, top holders, LP wallets, and known affiliate/team clusters.
9. Maintain a separate "legal submission" file as a downstream use case only; do not let it drive the forensic report structure.

---

## Sources And Artifacts

- [cases_database.json](./cases_database.json)
- [output/corpus_metrics.json](./output/corpus_metrics.json)
- [output/blockchain_analysis.json](./output/blockchain_analysis.json)
- [output/technical_deep_dive.json](./output/technical_deep_dive.json)
- [output/forensic_indicators.csv](./output/forensic_indicators.csv)
- [output/web_surface_capture.json](./output/web_surface_capture.json)
- [output/public_record_capture.json](./output/public_record_capture.json)
- [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md)
- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 4: Website Technical Investigation](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md)
- [Report 8: Public Records and Complaint Capture](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md)

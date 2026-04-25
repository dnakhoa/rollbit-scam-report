# Synthesis: Forensic Findings and Open Technical Hypotheses
**Document Classification:** Technical Forensic Synthesis
**Subject:** Bull Gaming N.V. / Rollbit
**Data Freeze:** April 19, 2026
**Updated:** April 25, 2026

This synthesis is written from a forensic analyst posture. It does not try to prove a legal theory. It asks what the artifacts show, where they conflict, and what must be collected next.

Primary technical artifacts:

- [Report 1: On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md)
- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 4: Website Technical Investigation](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md)
- [Report 7: Technical Forensic Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)
- [Report 8: Public Records and Complaint Capture](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md)
- [output/technical_deep_dive.json](./output/technical_deep_dive.json)
- [output/forensic_indicators.csv](./output/forensic_indicators.csv)

---

## Publication Lead Findings

1. The repository does **not** have Rollbit's verified reserve. It has attributed public wallet balances and incomplete public custody signals.
2. Known BTC/SOL wallets showed **$67.62M** on April 19, 2026, but there is no liability-matched proof-of-reserves, complete custody inventory, exchange-balance attestation, or customer-fund segregation proof.
3. The reported **$123M** off-wallet/exchange-proxy custody event is larger than the visible wallet snapshot, which reinforces that public wallets are not a reserve map.
4. Public complaints repeatedly describe funds becoming inaccessible after wins, withdrawals, KYC/compliance escalation, or multiple-account accusations.
5. RLB market cap is not usable as reserve depth: top-four DEX liquidity was **$4.71M** against **$101.22M** market cap, and token/team/control attribution remains incomplete.

**Forensic suspicion statement:** the overlap between locked-fund complaints, unverifiable reserves, opaque custody/control surfaces, and thin token liquidity supports reasonable forensic suspicion that Rollbit's user-fund restriction process and custody model require deeper scrutiny. This does not prove intent or validate every complaint.

---

## 1. What Is Directly Observed

| Evidence Layer | Direct Observation | Analyst Interpretation |
|----------------|--------------------|------------------------|
| Known public wallets | BTC/SOL snapshot shows **$67.62M** visible on April 19, 2026 | Attributed wallets are not empty, but they are not verified reserves |
| Treasury event timeline | Direct outflows total **$17.40M**; mixed BTC alerts total **$56.12M** | Directionality must stay explicit; mixed alerts are not direct outflows |
| Off-wallet custody signal | Reported exchange/proxy custody event is **$123M** | Public wallets are not a reserve map |
| RLB token market | Top-four DEX pool liquidity is **$4.71M** against **$101.22M** market cap | Token headline value is not reserve depth, and token-control attribution remains incomplete |
| Complaint corpus | **80** counted complaints; **74** quantified; **4** resolved | Recurrent operational dispute pattern remains unresolved at corpus level |
| Source acquisition | **53** deduplicated public targets captured; **52** HTTP captures written | Raw-source preservation now exists separately from complaint counting |
| Web surface | Main app is Cloudflare challenge-gated; blog is Ghost/Fastly and indexable | Product and publication layers require separate acquisition methods |

The corrected cached analyzer now preserves the April 19 wallet snapshot. It no longer writes a stale `$0` visible-wallet result when running without live API calls.

---

## 2. Core Technical Conflict

The investigation has one central correction:

> known public wallet balances exist, but they are not Rollbit's verified reserve.

That correction is stronger than a simple "wallets are empty" claim and more useful than a legal argument. The forensic question is not whether one public address has funds. The question is whether the observable custody graph is complete enough to evaluate user-facing solvency, withdrawal reliability, and customer-fund segregation.

The current answer is no. The repo does not have:

- total customer liabilities
- complete wallet inventory
- exchange balances
- proxy/intermediary custody balances
- proof that known wallets are reserve wallets
- proof that customer balances are segregated from operating capital
- a full map of who controls RLB token operations, LP positions, or market-making wallets

---

## 3. Working Hypotheses

| Hypothesis | Current Support | Contradictions / Gaps | Next Test |
|------------|-----------------|------------------------|-----------|
| `H1`: Public wallets are not verified reserves | Supported by absence of liability data, absence of reserve attestation, and $123M off-wallet custody reporting | Public wallet balances still show operational funds | Preserve source documents, map exchange/proxy custody, and require liability-matched snapshots |
| `H2`: Recent visible wallet activity is operational, not a current drain | Supported by April 19 sampled BTC/SOL activity and nonzero wallet balances | Full recent transaction graph has not been exported in this repo | Export recent BTC/SOL transactions with direction, counterparties, and value buckets |
| `H3`: RLB market cap overstates usable liquidity and token-control transparency | Supported by **4.66%** liquidity/market-cap ratio and incomplete token-control mapping | DEXScreener aggregate data is not a full slippage or holder-control model | Pull Uniswap pool state, map top holders, identify admin/deployer/burn/LP wallets, and simulate exits |
| `H4`: Complaint pattern reflects a repeatable control process | Supported by keyword/compound extraction across 80 counted complaints | Complaint data is public-source and mixed fidelity | Re-capture high-value cases, hash pages, preserve screenshots, and split confirmed vs claimed |
| `H5`: Main-site acquisition requires browser-aware methods | Supported by Cloudflare challenge behavior | Challenge state can vary by geography, ASN, cookies, and time | Capture DNS/TLS/headers/body/screenshots from controlled environments |

---

## 4. Complaint Pattern As Technical Signal

The complaint corpus is not used as a pile of anecdotes. It is a structured signal dataset.

Technical deep-dive extraction found:

| Signal | Case Hits | Amount Linked |
|--------|-----------|---------------|
| Withdrawal-control language | **48** | **$316,929.08** |
| KYC/compliance escalation | **33** | **$275,060.56** |
| Win/profit context | **35** | **$390,931.00** |
| Multi-account / linked-account language | **29** | **$178,402.56** |
| Withdrawal control + KYC escalation | **24** | **$153,330.56** |
| Withdrawal control + KYC escalation + win/profit context | **7** | **$83,401.00** |

This is the technical pattern worth investigating: user-reported withdrawal/profit triggers repeatedly coincide with KYC, compliance, linked-account, or account-control language.

The corpus also has an evidence-class split:

- **27** quantified cases are marked confirmed
- **47** quantified cases are marked claimed
- confirmed quantified amount: **$295,178.56**
- claimed quantified amount: **$266,902.52**

Those classes should remain separated in every downstream chart, table, and claim.

---

## 5. What Is Wrong With The Old Framing

The older report set had two weaknesses:

1. It spent too much analytical energy on legal/regulatory packaging.
2. Some generated artifacts still carried stale or overbroad technical claims, including cached output that implied known wallets were `$0`.

Both problems reduce forensic quality. The revised structure fixes the technical issue first:

- cached mode now preserves the known wallet snapshot without calling it a reserve
- mixed BTC alerts are separated from direct outflows
- the complaint corpus is analyzed by markers, compounds, source tier, and duplicate risk
- RLB is framed as liquidity stress, not as a generic market accusation
- web infrastructure is framed as an acquisition problem

---

## 6. Priority Collection Queue

1. Re-run live BTC, SOL, ETH, DEXScreener, and CoinGecko captures; store raw JSON under `output/captures/`.
2. Export transaction-level evidence for the January 2026 SOL outflows and label source/destination confidence.
3. Build a reserve-gap checklist: liabilities, custody inventory, exchange balances, wallet-control proof, and segregation proof.
4. Pull Uniswap pool state for RLB and build a slippage model.
5. Build an RLB control map: deployer, admin rights, burn wallets, top holders, LP wallets, and known affiliate/team clusters.
6. Re-capture the highest-value direct forum and mediation cases with HTML hashes and screenshots.
7. Manually review the duplicate candidates in [Report 7](./REPORT_7_TECHNICAL_DEEP_DIVE.md).
8. Follow up [Report 8](./REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md) capture gaps: Trustpilot challenge capture and Casino Guru 404 review.
9. Add a reproducible web capture script for DNS, TLS, headers, challenge pages, and blog metadata.
10. Keep [LEGAL_SUBMISSION_TEMPLATE.md](./LEGAL_SUBMISSION_TEMPLATE.md) as downstream packaging only.

---

## Bottom Line

Rollbit appears operational, and the known BTC/SOL wallets were not empty at the April 19 snapshot. The technical concern is different: the public wallet set is not a verified reserve, the operating/custody model is not publicly reconstructable from current artifacts, RLB liquidity and token-control attribution are thinly mapped, complaint signals show repeatable withdrawal/KYC/profit-trigger patterns, and the main web application requires careful acquisition because ordinary passive HTTP inspection stops at the edge challenge.

That is the current forensic thesis. It is testable, narrower, and more useful than a legal-first narrative.

# Report 1: On-Chain Financial Forensics
## Rollbit / Bull Gaming N.V. — Live Wallet State, Treasury Flow Review, and Public Token-Market Snapshot
**Date:** May 10, 2026 | **Classification:** Forensic Investigation
**Companion:** → [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md) | → [Report 4: Website Technical Investigation](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md) | → [Report 5: Public Event and Flow Timeline](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md) | → [Report 7: Technical Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)

---

## Executive Summary

This revised on-chain report replaces several broad claims from the earlier draft with a more precise split between:

1. **Directly observed chain facts** from a live snapshot taken on **May 10, 2026**
2. **Published treasury-flow alerts** from public reporting and explorer-linked news items
3. **Analytical limits**, which are labeled rather than presented as proof

### What the current chain snapshot shows

| Metric | Value |
|--------|-------|
| Visible BTC in known treasury wallet | **661.6337 BTC** |
| Visible SOL in known treasury wallet | **60,474.0331 SOL** |
| Visible value across known wallets | **~$59.13M** |
| Tracked ETH balance across 4 known ETH wallets | **0 ETH** |
| BTC treasury transaction count | **472,538** |
| Latest BTC/SOL activity in snapshot | **May 10, 2026** |

### What the current token snapshot shows

| Metric | Value |
|--------|-------|
| RLB spot price | **$0.0702** |
| RLB market cap | **~$118.22M** |
| Top 4 tracked public DEX pools combined liquidity | **~$5.05M** |
| Primary USDC pool liquidity | **~$2.11M** |
| Top 4 pools combined 24h volume | **~$200.65K** |
| Drawdown from all-time high | **-73.4%** |

### Core findings

- **Known wallets are not empty.** As of **May 10, 2026**, the publicly tracked BTC and SOL treasury wallets still held approximately **$59.1M** in visible assets.
- **That does not prove reserves.** The **May 9, 2025** Ukraine court action described by `dev.ua` involved **$123M** allegedly tied to Bull Gaming N.V. in Binance accounts controlled through a Ukrainian intermediary, which means material custody may have sat outside attributed public wallets.
- **The January-February 2026 BTC narrative requires a narrow reading.** A **626.03 BTC** alert on **February 13, 2026** should not be treated as a confirmed Rollbit treasury outflow. The underlying ChainCatcher/Arkham summary described **626.03 BTC moving from an anonymous address, with some flow into Bybit and Rollbit**. That item is therefore **not reliable evidence of a Rollbit drain**.
- **Direct published outflows are still material.** Public alerts do document:
  - a **50,000 SOL** treasury-linked liquidation on **September 3, 2025**
  - **15,000 SOL + 15,000 SOL** moved out on **January 11, 2026**
  - **21,363.73 SOL** moved out on **January 15, 2026**
- **The RLB liquidity model is incomplete.** The repo currently captures about **$5.05M** of tracked public DEX liquidity across top public aggregator-indexed pools against a roughly **$118M** market cap. That is a scoped public-market snapshot, not a measurement of Rollbit app/on-platform liquidity, order-book depth, or custody-side token inventory.

### Bottom line

The strongest present conclusion is **not** that chain data alone proves zero reserves or imminent collapse. The better-supported conclusion is that Rollbit's actual reserve position is **not publicly verifiable** from the current artifact set. Known wallets show funds, but they do not prove reserve completeness, liability coverage, customer-fund segregation, or exchange/proxy custody balances.

---

## 1. Methodology and Snapshot Date

This report combines:

- **Live chain data** pulled on **May 10, 2026 (UTC)** from:
  - Blockstream API for BTC
  - Solana JSON-RPC for SOL
  - DEXScreener for tracked public RLB DEX liquidity
  - CoinGecko for RLB price, supply, market cap, and tracked exchange/market coverage
- **Published event coverage** from:
  - `dev.ua`
  - `ChainCatcher`
  - CoinDesk
  - CryptoSlate
  - Rollbit's official blog
- **Public operator materials** such as the official RLB utility and migration posts

Important constraint:

- Public wallet analysis can show what is visible on-chain in known addresses.
- It **cannot** by itself prove total assets, total liabilities, beneficial ownership of every counterparty wallet, or the full contents of exchange/proxy accounts described in court reporting.

Artifact integrity note:

- `scripts/blockchain_analyzer.py --cached` preserves the April 19, 2026 wallet snapshot for offline replay.
- `scripts/blockchain_analyzer.py --full` refreshed [output/blockchain_analysis.json](./output/blockchain_analysis.json) on May 10, 2026.
- Cached mode is a frozen artifact replay, not a current live balance check.
- Live mode should be used when updating the snapshot date, and raw API responses should be preserved separately.

---

## 2. Known Treasury Wallets

The tracked addresses used in this repo are:

| Chain | Address | Label |
|-------|---------|-------|
| BTC | `bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu` | Primary Treasury |
| SOL | `RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx` | SOL Treasury |
| ETH | `0xCBD6832Ebc203e49E2B771897067fce3c58575ac` | ETH Hot Wallet |
| ETH | `0xef8801eaf234ff82801821ffe2d78d60a0237f97` | ERC20 Ops |
| ETH | `0x46dcA395D20E63Cb0Fe1EDC9f0e6f012E77c0913` | rollbit.eth |
| ETH | `0x8aE57A027c63fcA8070D1Bf38622321dE8004c67` | rollbot.eth |

---

## 3. Live Wallet Snapshot — May 10, 2026

Snapshot time from the regenerated analysis artifact: **2026-05-10T10:28Z**.

| Wallet | Native Balance | USD Value | Notes |
|--------|----------------|-----------|-------|
| BTC Treasury | **661.63373307 BTC** | **$53,454,712.56** | 472,538 transactions; active on snapshot date |
| SOL Treasury | **60,474.0331 SOL** | **$5,670,650.09** | Recent signatures visible on snapshot date |
| ETH Hot Wallet | **0 ETH** | **$0** | No current ETH visible |
| ERC20 Ops | **0 ETH** | **$0** | No current ETH visible |
| rollbit.eth | **0 ETH** | **$0** | No current ETH visible |
| rollbot.eth | **0 ETH** | **$0** | No current ETH visible |
| **Total visible** | | **$59,125,362.65** | BTC + SOL dominate the attributed public wallet set |

### Interpretation

- The attributed public wallet set still holds a **substantial visible balance**.
- The chain picture therefore does **not** support the simplistic claim that Rollbit's public wallets have been emptied.
- At the same time, the visible total remains **well below** the **$123M** described in the Ukraine-linked seizure reporting, which reinforces the possibility that meaningful custody has historically sat in **off-wallet exchange or proxy structures**.
- The visible total is **not** a proof-of-reserves figure because the report has no liability total, exchange balance attestation, complete wallet inventory, or segregation evidence.

---

## 4. What Recent BTC and SOL Activity Actually Looks Like

The live sample preserved in this repo still looks more like **operational wallet activity** than another single-shot treasury evacuation, but the sample is not a full transaction graph.

The May 10 tracer captured:

- **25** recent BTC transactions: **24** outflows and **1** inflow
- largest recent BTC outflow in that sample: **0.06744540 BTC** on **May 10, 2026**
- **20** recent SOL signatures, with latest activity on **May 10, 2026**

The April 19 examples below remain useful as examples of the observed small-transaction pattern, not as a current exhaustive flow export.

### 4.1 Sampled BTC transactions

| Time (UTC) | TXID | Observed Movement | What it suggests |
|------------|------|------------------|------------------|
| 2026-04-19 04:48:42 | `a14f9579...` | **0.61587553 BTC** sent to `3Q3PK4...`; **0.24472927 BTC** returned as change | Routine UTXO spend with change back to treasury |
| 2026-04-19 05:50:50 | `65f0ed5a...` | **0.01178501 BTC** sent to `bc1qdx...`; **0.01845451 BTC** returned as change | Small operational payout or wallet maintenance |
| 2026-04-19 09:00:49 | `6bb95f53...` | **0.03679731 BTC** sent to `bc1qrp...`; **0.20790376 BTC** returned as change | Another ordinary UTXO spend |

### 4.2 Sampled SOL transactions

| Time (UTC) | Signature | Observed Movement | What it suggests |
|------------|-----------|------------------|------------------|
| 2026-04-19 09:10:27 | `SJaPf3kH...` | **52.7 USDC** moved from a treasury-controlled token account to another wallet | Operational token transfer, not a multi-million treasury move |
| 2026-04-19 09:10:19 | `5LjiW7Ej...` | **0.27777562 SOL** transferred into the treasury wallet | Small inbound top-up / housekeeping |

### Interpretation

- The **current** visible operational pattern looks granular and active, not frozen.
- The sampled transactions are **orders of magnitude smaller** than the published January 2026 SOL transfers.
- This matters because it separates:
  - **historical high-value treasury events**
  - from **present-day operational wallet servicing**

---

## 5. Published Treasury Event Timeline

The table below separates direct outflows from inflows and mixed-flow alerts. This corrects the earlier version of the report, which treated all large BTC alerts as outbound treasury drains.

| Date | Type | Event | Amount | Source |
|------|------|-------|--------|--------|
| 2025-05-09 | Seizure / court action | Kyiv court allowed transfer of seized crypto allegedly linked to Bull Gaming N.V. to ARMA | **$123M** | `dev.ua` + linked court references |
| 2025-09-03 | Treasury-linked liquidation | Wallet associated with Rollbit treasury sold **50,000 SOL** after two years of inactivity | **$10.17M** | ChainCatcher citing Lookonchain |
| 2026-01-09 | Inflow | **497.11 BTC** transferred from an anonymous address **to Rollbit** | **$45.19M** | ChainCatcher / Arkham |
| 2026-01-11 | Outflow | **15,000 SOL** transferred from Rollbit to anonymous address `Y6qq1Q1U...` | **$2.05M** | ChainCatcher / Arkham |
| 2026-01-11 | Outflow | Second **15,000 SOL** transfer from Rollbit to anonymous address `Y6qq1Q1U...` | **$2.04M** | ChainCatcher / Arkham |
| 2026-01-15 | Outflow | **21,363.73 SOL** transferred from Rollbit to anonymous address `Dj3ssyVZ...` | **$3.14M** | ChainCatcher / Arkham |
| 2026-02-13 | Mixed / inbound to Rollbit leg | **626.03 BTC** transferred from anonymous address, with some flow reported into **Bybit and Rollbit** | **$42.21M** | ChainCatcher / Arkham |
| 2026-03-11 | Mixed / inbound to Rollbit leg | **200 BTC** transferred from Coinbase, with some flow reported into **Rollbit** | **$13.91M** | ChainCatcher / Arkham |

### Direct outflow subtotal

The **direct, published outflow set** from the table above is:

- **$7.23M** in direct January 2026 SOL transfers

If the **September 3, 2025** 50K SOL sale from a treasury-linked wallet is included as treasury-related disposition, the broader treasury-related outflow figure becomes:

- **$17.40M**

This is a smaller classified outflow set than the earlier draft because the February 13 BTC item is no longer treated as a confirmed Rollbit outflow.

### Technical ratio tests

[Report 7](./REPORT_7_TECHNICAL_DEEP_DIVE.md) converts the event classification into simple ratio checks:

| Ratio | Value | Why It Matters |
|-------|------:|----------------|
| Direct outflows / visible wallet snapshot | **29.4%** | Material, but not a reserve-coverage result |
| January 2026 direct outflows / visible wallet snapshot | **12.2%** | Large enough to monitor, too small to call a full drain |
| Reported off-wallet custody event / visible wallet snapshot | **208.0%** | Public wallets are not a reserve map |

These ratios should be recalculated whenever the live wallet snapshot is refreshed.

---

## 6. The Ukraine Seizure Still Matters

The **May 17, 2025** `dev.ua` article summarizing the **May 9, 2025** Pechersk District Court action remains one of the most important external data points in the file.

According to that report:

- investigators were probing a **fraud and money-laundering scheme**
- the seized assets were allegedly tied to a Ukrainian person associated with **Bull Gaming N.V.**
- **Bull Gaming N.V. reportedly confirmed in writing** that the relevant funds belonged to the casino
- Chainalysis allegedly traced more than **$132M** in transaction volume in one analyzed period

### Why this matters for the on-chain story

Even if attributed public wallets still show **$59.1M** in the snapshot, the seizure reporting implies that:

- some significant assets may have been parked in **exchange accounts or intermediary-controlled custody**
- the public wallet set may represent only **part** of the operating custody picture
- solvency cannot be inferred safely from public wallet balances alone

That is a more defensible conclusion than simply asserting that the current treasury is empty.

---

## 7. RLB Token Market Structure — Updated Snapshot

### 7.1 Current market structure

| Metric | Value |
|--------|-------|
| Price | **$0.070204** |
| Market cap | **$118,218,080** |
| Circulating supply | **~1,683,929,933 RLB** by CoinGecko; **1,683,904,316.91 RLB** from Rollbit public supply endpoint |
| Total supply | **~1,683,929,933 RLB** by CoinGecko |
| ATH | **$0.264358** |
| Drawdown from ATH | **-73.44%** |

### 7.2 Tracked Public DEX Liquidity By Primary Pools

| Pool | Liquidity | 24h Volume |
|------|-----------|------------|
| RLB / USDT (Uniswap V3) | **$2,378,658.49** | **$74,166.73** |
| RLB / USDC (Uniswap V3) | **$2,109,509.55** | **$103,059.82** |
| RLB / WETH (Uniswap V3) | **$557,387.60** | **$23,425.25** |
| RLB / ETH (Uniswap V4) | **$4,845.66** | **$2.98** |
| **Top 4 total** | **$5,050,401.30** | **$200,654.78** |

Scope note:

- This table is a public DEX snapshot from the repo's DEXScreener/CoinGecko capture path.
- It does **not** measure Rollbit app/on-platform liquidity, internal conversion depth, order books, or custodial token inventory.
- Rollbit's own materials describe RLB trading directly on Rollbit.com and RLB liquidity pools introduced in May 2023. The current whitepaper also describes RLB/USD pools used to support RLB trading on Rollbit. Those app-gated surfaces need a separate capture method.
- CoinGecko and DEXScreener currently expose the tracked live RLB market/liquidity surface as Uniswap-based in this capture. A Poloniex public market API capture returned no active RLB market matches, but this report should not convert that limited check into a categorical venue-absence claim.

### 7.3 Why this still matters

- A roughly **$118M** token trading against **~$5.05M** in tracked public DEX liquidity shows that market cap should not be used as reserve depth.
- Public market aggregators currently show tracked public RLB coverage concentrated in Uniswap pools, but this report must not describe Uniswap as the only RLB trading or liquidity venue.
- The official buy-and-burn narrative remains **operator-reported**, not independently audited.

### 7.4 Official buy-and-burn claims

Rollbit's own **September 13, 2023** blog post said:

- buy-and-burn started on **August 8, 2023**
- the system bought **33,688,709 RLB** worth **$5,538,265.59** in its first month
- hourly purchases were funded from **10% of casino revenue, 20% of sportsbook revenue, and 30% of futures revenue**

This is important because it establishes the company's own public framing. It should be reconciled to transaction-level buy, burn, and distribution records rather than treated as an external audit.

### 7.5 Migration and custody concentration

Rollbit's **June 28, 2023** migration announcement said:

- SOL-based RLB would no longer be supported after **May 1, 2024**
- the only way to migrate SOL RLB to ETH RLB was **through Rollbit.com**
- once deposited from Solana, withdrawals were only available on Ethereum

That design choice concentrated an important token-migration path through the platform itself.

---

## 8. Updated Data-Gap Framing

The previous report leaned too heavily on a single "capital flight" narrative. The updated evidence supports a more precise data-gap matrix:

| Data Area | Current Assessment | Why |
|-----------|--------------------|-----|
| Public-wallet reserve verification | **Not established** | Known wallets still hold sizeable BTC and SOL, but no liability-matched proof-of-reserves artifact exists |
| Off-wallet custody visibility | **Incomplete** | Ukraine-linked Binance/proxy account reporting indicates custody may sit outside public wallets |
| RLB venue-depth coverage | **Incomplete** | Tracked public DEX liquidity is limited relative to market cap, and Rollbit app/on-platform liquidity is not yet measured |
| Treasury-flow classification | **Needs transaction-level export** | There are large published treasury-related flows, but direction and ownership are not always straightforward |
| Complaint / dispute-corpus coverage | **Structured but incomplete** | Reports 2 and 3 document unresolved withdrawal and KYC disputes, but source fidelity varies |
| Licensing / public verifiability | **Inconclusive from direct checks** | See Report 4: public certificate verification is currently inconclusive from direct web checks |

### Best-supported synthesis

The live on-chain picture supports the following:

1. **Rollbit-linked public wallets still show visible BTC and SOL balances.**
2. **Those visible balances are not verified reserves**, because important funds have reportedly moved through exchange/proxy structures and no liability-matched reserve attestation is present.
3. **RLB public DEX liquidity is limited relative to headline market cap**, but the repo has not measured Rollbit app/on-platform liquidity.
4. **Published treasury alerts show mixed inflow/outflow behavior**, not a one-direction-only drain.
5. **The unresolved data gap remains material** because user-claim patterns coexist with opaque reserve location and off-wallet custody exposure.

---

## 9. Key Investigative Questions That Remain Open

1. What proportion of Rollbit's operational custody historically sat in **exchange custody** rather than attributed public wallets?
2. Which anonymous counterparties on **January 9, 2026**, **February 13, 2026**, and **March 11, 2026** were beneficially linked to Rollbit, if any?
3. What is the relationship between the **public RLB buy-and-burn dashboard narrative**, public DEX depth, Rollbit app/on-platform depth, deployer/admin controls, and top-holder concentration?
4. Are customer balances contractually or operationally segregated from operating capital, and where is the evidence?

---

## Sources

- Blockstream API BTC address and transaction data: https://blockstream.info/
- Solana JSON-RPC transaction and balance data: https://api.mainnet-beta.solana.com/
- CoinGecko RLB market data: https://api.coingecko.com/api/v3/coins/rollbit-coin
- DEXScreener RLB pool data: https://api.dexscreener.com/latest/dex/tokens/0x046eee2cc3188071c02bfc1745a6b17c656e3f3d
- Rollbit public RLB supply endpoint: https://api.rollbit.com/v1/public/rlb/supply.json
- Poloniex public markets API: https://api.poloniex.com/markets
- `dev.ua` on Ukraine-linked seizure: https://dev.ua/en/news/krypto-1747475639
- ChainCatcher Rollbit tag archive: https://www.chaincatcher.com/en/tags/rollbit
- ChainCatcher January 11, 2026 15K SOL transfer: https://www.chaincatcher.com/article/2236424
- ChainCatcher September 3, 2025 50K SOL sale: https://www.chaincatcher.com/ko/article/2202906
- ChainCatcher January 9, 2026 497.11 BTC to Rollbit: https://www.chaincatcher.com/article/2235971
- Rollbit blog buy-and-burn post: https://blog.rollbit.com/rlb-utility-guide/amp/
- Rollbot whitepaper buy-and-burn / RLB on Rollbit links: https://whitepaper.rollbot.com/rlb-whitepaper/i/buy-and-burn
- Rollbot whitepaper provide-liquidity page: https://whitepaper.rollbot.com/rlb-whitepaper/i/utility/provide-liquidity
- Rollbit blog migration post: https://blog.rollbit.com/rlb-eth-migration/
- CoinDesk on March 31, 2023 licensing concerns: https://www.coindesk.com/markets/2023/03/31/crypto-casino-rollbits-token-drops-20-amid-licensing-concerns
- CryptoSlate on influencer promotion scrutiny: https://cryptoslate.com/solana-based-rollbit-coin-faces-scrutiny-over-crypto-influencer-promotion-tactics/

---

*Continue to [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md) for the complaint evidence, and to [Report 4](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md) / [Report 5](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md) for web-infrastructure and news context.*

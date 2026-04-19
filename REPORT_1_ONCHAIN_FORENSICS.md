# Report 1: On-Chain Financial Forensics
## Rollbit / Bull Gaming N.V. — Live Wallet State, Treasury Flow Review, and Token Market Structure
**Date:** April 19, 2026 | **Classification:** Forensic Investigation
**Companion:** → [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md) | → [Report 4: Website Technical Investigation](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md) | → [Report 5: News and Regulatory Timeline](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md)

---

## Executive Summary

This revised on-chain report replaces several broad claims from the earlier draft with a more precise split between:

1. **Directly observed chain facts** from a live snapshot taken on **April 19, 2026**
2. **Published treasury-flow alerts** from public reporting and explorer-linked news items
3. **Inference**, which is labeled as inference rather than presented as proof

### What the current chain snapshot shows

| Metric | Value |
|--------|-------|
| Visible BTC in known treasury wallet | **649.5455 BTC** |
| Visible SOL in known treasury wallet | **222,587.1107 SOL** |
| Visible value across known wallets | **~$67.62M** |
| Tracked ETH balance across 4 known ETH wallets | **0 ETH** |
| BTC treasury transaction count | **469,936** |
| Latest BTC/SOL activity in snapshot | **April 19, 2026** |

### What the current token snapshot shows

| Metric | Value |
|--------|-------|
| RLB spot price | **$0.0595** |
| RLB market cap | **~$101.2M** |
| Top 4 Uniswap pools combined liquidity | **~$4.71M** |
| Primary USDC pool liquidity | **~$1.92M** |
| Top 4 pools combined 24h volume | **~$153K** |
| Drawdown from all-time high | **-77.5%** |

### Core findings

- **Known wallets are not empty.** As of **April 19, 2026**, the publicly tracked BTC and SOL treasury wallets still held approximately **$67.7M** in visible assets.
- **That does not resolve the custody question.** The **May 9, 2025** Ukraine court action described by `dev.ua` involved **$123M** allegedly tied to Bull Gaming N.V. in Binance accounts controlled through a Ukrainian intermediary, which means critical reserves may have sat outside public treasury wallets.
- **The January-February 2026 BTC narrative requires a narrow reading.** A **626.03 BTC** alert on **February 13, 2026** should not be treated as a confirmed Rollbit treasury outflow. The underlying ChainCatcher/Arkham summary described **626.03 BTC moving from an anonymous address, with some flow into Bybit and Rollbit**. That item is therefore **not reliable evidence of a Rollbit drain**.
- **Direct published outflows are still material.** Public alerts do document:
  - a **50,000 SOL** treasury-linked liquidation on **September 3, 2025**
  - **15,000 SOL + 15,000 SOL** moved out on **January 11, 2026**
  - **21,363.73 SOL** moved out on **January 15, 2026**
- **RLB remains structurally thin.** Even using a more generous current liquidity figure than the earlier report, the token still shows only about **$4.7M** of combined liquidity across its top four Uniswap pools against a roughly **$101M** market cap.

### Bottom line

The strongest present conclusion is **not** that chain data alone proves zero reserves or imminent collapse. The stronger and better-supported conclusion is that Rollbit exhibits **material custody opacity, concentrated token liquidity, off-wallet reserve uncertainty, and unresolved counterparty risk** that chain data does not dispel.

---

## 1. Methodology and Snapshot Date

This report combines:

- **Live chain data** pulled on **April 19, 2026 (UTC)** from:
  - Blockstream API for BTC
  - Solana JSON-RPC for SOL
  - DEXScreener for RLB liquidity
  - CoinGecko for RLB price, supply, and market cap
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

## 3. Live Reserve Snapshot — April 19, 2026

Snapshot time from the regenerated analysis artifact: **2026-04-19T09:23Z to 2026-04-19T09:24Z**.

| Wallet | Native Balance | USD Value | Notes |
|--------|----------------|-----------|-------|
| BTC Treasury | **649.54550772 BTC** | **$48,758,133.54** | 469,936 transactions; active on snapshot date |
| SOL Treasury | **222,587.110683 SOL** | **$18,862,031.76** | Recent signatures every few seconds on snapshot date |
| ETH Hot Wallet | **0 ETH** | **$0** | No current ETH visible |
| ERC20 Ops | **0 ETH** | **$0** | No current ETH visible |
| rollbit.eth | **0 ETH** | **$0** | No current ETH visible |
| rollbot.eth | **0 ETH** | **$0** | No current ETH visible |
| **Total visible** | | **$67,620,165.30** | BTC + SOL dominate visible reserves |

### Interpretation

- The public treasury set still holds a **substantial visible balance**.
- The chain picture therefore does **not** support the simplistic claim that Rollbit's public wallets have been emptied.
- At the same time, the visible total remains **well below** the **$123M** described in the Ukraine-linked seizure reporting, which reinforces the possibility that meaningful reserves have historically sat in **off-wallet exchange or proxy custody**.

---

## 4. What Recent BTC and SOL Activity Actually Looks Like

The live sample from **April 19, 2026** looks more like **operational wallet activity** than another single-shot treasury evacuation.

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

This is still meaningful, but it is **materially lower** than the earlier draft's **$59.61M** figure, which depended on treating the February 13 BTC item as a confirmed Rollbit outflow.

---

## 6. The Ukraine Seizure Still Matters

The **May 17, 2025** `dev.ua` article summarizing the **May 9, 2025** Pechersk District Court action remains one of the most important external data points in the file.

According to that report:

- investigators were probing a **fraud and money-laundering scheme**
- the seized assets were allegedly tied to a Ukrainian person associated with **Bull Gaming N.V.**
- **Bull Gaming N.V. reportedly confirmed in writing** that the relevant funds belonged to the casino
- Chainalysis allegedly traced more than **$132M** in transaction volume in one analyzed period

### Why this matters for the on-chain story

Even if public treasury wallets still show **$67.7M** today, the seizure reporting implies that:

- some significant reserves may have been parked in **exchange accounts or intermediary-controlled custody**
- the public wallet set may represent only **part** of the operating reserve picture
- solvency cannot be inferred safely from public wallet balances alone

That is a more defensible conclusion than simply asserting that the current treasury is empty.

---

## 7. RLB Token Market Structure — Updated Snapshot

### 7.1 Current market structure

| Metric | Value |
|--------|-------|
| Price | **$0.059523** |
| Market cap | **$101,223,201** |
| Circulating supply | **1,700,989,104 RLB** |
| Total supply | **1,700,989,104 RLB** |
| ATH | **$0.264358** |
| Drawdown from ATH | **-77.49%** |

### 7.2 Liquidity by primary pools

| Pool | Liquidity | 24h Volume |
|------|-----------|------------|
| RLB / USDC (Uniswap V3) | **$1,922,698.69** | **$79,411.54** |
| RLB / USDT (Uniswap V3) | **$2,188,645.08** | **$56,582.21** |
| RLB / WETH (Uniswap V3) | **$597,299.69** | **$16,018.14** |
| RLB / ETH (Uniswap V4) | **$4,440.41** | **$1,094.35** |
| **Top 4 total** | **$4,713,083.87** | **$153,106.24** |

### 7.3 Why this still matters

- A roughly **$101M** token trading against only **~$4.7M** in visible top-pool liquidity is still **thin**.
- Liquidity is concentrated in a handful of Uniswap pools rather than broad venue depth.
- The official buy-and-burn narrative remains **operator-reported**, not independently audited.

### 7.4 Official buy-and-burn claims

Rollbit's own **September 13, 2023** blog post said:

- buy-and-burn started on **August 8, 2023**
- the system bought **33,688,709 RLB** worth **$5,538,265.59** in its first month
- hourly purchases were funded from **10% of casino revenue, 20% of sportsbook revenue, and 30% of futures revenue**

This is important because it establishes the company's own public framing. But it is still a **company statement**, not an external audit.

### 7.5 Migration and custody concentration

Rollbit's **June 28, 2023** migration announcement said:

- SOL-based RLB would no longer be supported after **May 1, 2024**
- the only way to migrate SOL RLB to ETH RLB was **through Rollbit.com**
- once deposited from Solana, withdrawals were only available on Ethereum

That design choice concentrated an important token-migration path through the platform itself.

---

## 8. Updated Risk Framing

The previous report leaned too heavily on a single "capital flight" narrative. The updated evidence supports a more precise matrix:

| Risk Area | Current Assessment | Why |
|-----------|--------------------|-----|
| Public-wallet solvency visibility | **Medium** | Known wallets still hold sizeable BTC and SOL |
| Off-wallet custody opacity | **High** | Ukraine-linked Binance/proxy account reporting indicates reserves may sit outside public wallets |
| Token exit liquidity concentration | **High** | RLB market cap remains large relative to visible DEX liquidity |
| Treasury-flow transparency | **High** | There are large published treasury-related flows, but direction and ownership are not always straightforward |
| Complaint / counterparty risk | **High** | Reports 2 and 3 still document unresolved withdrawal and KYC disputes at scale |
| Licensing / public verifiability | **Medium to High** | See Report 4: public certificate verification is currently inconclusive from direct web checks |

### Best-supported synthesis

The live on-chain picture supports the following:

1. **Rollbit still controls visible reserves in known BTC and SOL wallets.**
2. **Those visible reserves do not settle the custody question**, because important funds have reportedly moved through exchange/proxy structures.
3. **RLB remains a thin-liquidity market structure** relative to its headline market cap.
4. **Published treasury alerts show mixed inflow/outflow behavior**, not a one-direction-only drain.
5. **Counterparty risk remains high** because unresolved user-claim patterns coexist with opaque reserve location and a law-enforcement-linked seizure history.

---

## 9. Key Investigative Questions That Remain Open

1. What proportion of Rollbit's operational reserves historically sat in **exchange custody** rather than public treasury wallets?
2. Which anonymous counterparties on **January 9, 2026**, **February 13, 2026**, and **March 11, 2026** were beneficially linked to Rollbit, if any?
3. What is the relationship between the **public RLB buy-and-burn dashboard narrative** and the actual market depth available for token exit?
4. Are customer balances contractually or operationally segregated from operating capital, as current CGA policy expects for licensed B2C operators?

---

## Sources

- Blockstream API BTC address and transaction data: https://blockstream.info/
- Solana JSON-RPC transaction and balance data: https://api.mainnet-beta.solana.com/
- CoinGecko RLB market data: https://api.coingecko.com/api/v3/coins/rollbit-coin
- DEXScreener RLB pool data: https://api.dexscreener.com/latest/dex/tokens/0x046eee2cc3188071c02bfc1745a6b17c656e3f3d
- `dev.ua` on Ukraine-linked seizure: https://dev.ua/en/news/krypto-1747475639
- ChainCatcher Rollbit tag archive: https://www.chaincatcher.com/en/tags/rollbit
- ChainCatcher January 11, 2026 15K SOL transfer: https://www.chaincatcher.com/article/2236424
- ChainCatcher September 3, 2025 50K SOL sale: https://www.chaincatcher.com/ko/article/2202906
- ChainCatcher January 9, 2026 497.11 BTC to Rollbit: https://www.chaincatcher.com/article/2235971
- Rollbit blog buy-and-burn post: https://blog.rollbit.com/rlb-utility-guide/amp/
- Rollbit blog migration post: https://blog.rollbit.com/rlb-eth-migration/
- CoinDesk on March 31, 2023 licensing concerns: https://www.coindesk.com/markets/2023/03/31/crypto-casino-rollbits-token-drops-20-amid-licensing-concerns
- CryptoSlate on influencer promotion scrutiny: https://cryptoslate.com/solana-based-rollbit-coin-faces-scrutiny-over-crypto-influencer-promotion-tactics/

---

*Continue to [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md) for the complaint evidence, and to [Report 4](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md) / [Report 5](./REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md) for web-infrastructure and news context.*

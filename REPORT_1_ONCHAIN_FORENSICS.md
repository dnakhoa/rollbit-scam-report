# Report 1: On-Chain Financial Forensics
## Rollbit / Bull Gaming N.V. — Blockchain Evidence & Financial Crimes
**Date:** March 10, 2026 | **Classification:** Forensic Investigation
**Companion:** → [Report 2: Victim Forum Evidence](./REPORT_2_VICTIM_EVIDENCE.md)

---

## Executive Summary

This report combines live blockchain data with public financial analysis to document the on-chain behavior of **Bull Gaming N.V.** (d/b/a Rollbit.com). The findings establish a pattern consistent with **capital flight, money laundering, and deliberate insolvency manufacturing** by anonymous operators.

**At a glance:**
| Metric | Value |
|--------|-------|
| Documented treasury outflows (5 months) | **$59.6M+** |
| Law enforcement asset seizure | **$123M** |
| RLB Uniswap liquidity | **~$2M** |
| RLB market cap | **~$150M** |
| Liquidity-to-market-cap ratio | **1.3%** |
| Exit-scam risk score | **7.8 / 10 CRITICAL** |

---

## 1. Who is Rollbit?

**Rollbit.com** is an online cryptocurrency casino, sportsbook, and 1000x leveraged futures platform operated by **Bull Gaming N.V.**, registered in Curaçao (Company No. 157086). The platform launched in February 2020 and currently claims millions of registered users.

The founders operate under pseudonyms:
- **"Lucky"** — identified as **Daniel Robert Dixon**, British national (confirmed by rival platform owners, IQ.wiki)
- **"Razer"** — identified as **Jose Llisterri**, British national (confirmed by IQ.wiki)

Both operated the predecessor platform **CSGODiamonds**, which collapsed after being caught **rigging games** for a sponsored streamer (the 2016 CS:GO gambling scandal). Fraud is not new to these operators.

---

## 2. Known Treasury Wallets

On-chain surveillance covers 6 known Rollbit wallet addresses:

| Chain | Address | Label |
|-------|---------|-------|
| BTC | `bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu` | Primary Treasury |
| SOL | `RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx` | SOL Treasury |
| ETH | `0xCBD6832Ebc203e49E2B771897067fce3c58575ac` | ETH Hot Wallet |
| ETH | `0xef8801eaf234ff82801821ffe2d78d60a0237f97` | ERC20 Ops |
| ETH | `0x46dcA395D20E63Cb0Fe1EDC9f0e6f012E77c0913` | rollbit.eth |
| ETH | `0x8aE57A027c63fcA8070D1Bf38622321dE8004c67` | rollbot.eth |

---

## 3. The Treasury Drainage — $59.6M in 5 Months

The following treasury outflows are documented from public blockchain data and reporting by ChainCatcher, Binance/Bitget, and on-chain analysis:

| Date | Event | Amount | Chain |
|------|-------|--------|-------|
| 2025-09-03 | 50K SOL sold after 2-year dormancy | **$10,170,000** | SOL |
| 2026-01-11 | 15K SOL batch 1 transferred | **$2,050,000** | SOL |
| 2026-01-11 | 15K SOL batch 2 transferred | **$2,040,000** | SOL |
| 2026-01-15 | 21.4K SOL transferred | **$3,140,000** | SOL |
| 2026-02-13 | **626 BTC moved to anonymous wallet** | **$42,210,000** | BTC |
| **Total** | | **$59,610,000** | |

### Red Flags in This Pattern

1. **Two-year dormancy broken:** The SOL treasury had not moved in over two years before September 2025. The sudden liquidation of 50K SOL in a single transaction is a textbook sign of capital flight, not routine operations.

2. **Anonymous BTC destination:** The 626 BTC transferred in February 2026 went to an address with no prior transaction history — characteristic of operators moving funds to a cold wallet outside regulatory reach.

3. **Batched transfers to obscure:** The January 2026 SOL transfers were split into multiple batches on the same day, a classic technique to avoid automated chain analytics thresholds.

4. **Timing correlation with complaints:** The treasury drainage accelerates precisely as victim complaints spike (37+ cases in 2025 vs. 2 in 2022). This is consistent with a platform moving assets **in anticipation of legal action or collapse**, not normal business operations.

---

## 4. The $123 Million Seizure (Ukraine, May 2025)

On May 9, 2025, the Pechersk District Court of Kyiv ordered the transfer of **$123,000,000 in cryptocurrency** to Ukraine's National Agency for Investigation and Asset Management (ARMA).

**The Evidence Trail:**
- Investigators traced gambling proceeds from Rollbit to Binance accounts held by a Ukrainian proxy.
- **Bull Gaming N.V. confirmed in writing to the Cyber Police of Ukraine** that the seized funds "actually belong to the specified online casino."
- Chainalysis traced over **$132 million in total transaction volume** through the seized accounts.
- Criminal proceedings were opened for **fraud and money laundering**.

*Source: Pechersk District Court of Kyiv; dev.ua (2025-05-09)*

**What this means for solvency:**
The $123M seizure is not a fine or penalty — it is the outright **loss of casino reserves** held in a proxy individual's name. Combined with the $59.6M in subsequent treasury outflows, Rollbit has lost or displaced at least **$182.6M** in a matter of months.

---

## 5. RLB Token — The Biggest Red Flag

### 5.1 The Liquidity Illusion

The RLB token presents one of the most egregious token structures in the crypto casino space:

| Metric | Value |
|--------|-------|
| Stated market cap | ~**$150,000,000** |
| Uniswap pool liquidity | ~**$2,000,000** |
| Liquidity ratio | **~1.3%** |
| Exchange availability | **Uniswap only** (no CEX listings) |
| Stated circulating supply | ~3.97B of 5B RLB |
| "Burn" rate claimed | 50.86% of supply burned |

A token with **$150M in stated market cap but only $2M in real market liquidity** is not a functional asset — it is a number on a screen. This means:

- If **any significant holder** (influencer, insider, team) were to sell even $2M worth of RLB, it would **crash the price by 50%+**.
- The "market cap" figure is entirely hypothetical and functionally meaningless.
- The token cannot be realised at its stated value by any holder, especially large ones.
- A $2M liquidity pool for a $150M asset represents a **74:1 paper-to-real-money ratio** — this is the structure of a textbook pump-and-dump.

### 5.2 The Buyback Fraud

Rollbit publicly claims to spend **$5 million per month** buying back and burning RLB tokens using platform revenues. This is mathematically inconsistent with the observed price action:

- Peak RLB price: **~$0.22** (November 2023)
- Current RLB price: **~$0.038** (March 2026)
- Price decline: **-83%** over ~28 months
- Claimed cumulative buybacks (28 months × $5M): **~$140M**

If $140M were genuinely being used to purchase a token with only $2M in liquidity, the token price would have exploded to multiples. Instead it has lost 83% of its value. The explanation is one or more of the following:
- **The buybacks are fabricated** and funds are redirected to insider wallets.
- **Insiders are front-running buybacks,** selling into the purchased liquidity at a rate exceeding the buyback volume.
- **The buy/burn mechanics are misrepresented** in the tokenomics documentation.

### 5.3 Influencer Price Manipulation

Blockchain wallet analysis (reported by CryptoSlate and Step Finance) exposed:
- Casino founder "Lucky" offered influencers **$250K in RLB** if the token price hit $0.20 and held for one week, in exchange for "several organic RLB tweets."
- Influencer **Gainzy** publicly claimed to have *bought* $400,000 in RLB to show confidence. Wallet analysis showed he was *selling* $400,000 over two weeks **using Rollbit's platform as a mixing conduit**.
- These actions constitute **coordinated market manipulation** and potentially **securities fraud** under most jurisdictions' financial regulations.

---

## 6. Regulatory & Licensing Status (How They Stay Open)

| Period | Status |
|--------|--------|
| 2020–2023 | Curacao sub-license (365/JAZ) |
| March 2023 | License removed from website; claimed "annual renewal" |
| April 2023 | License "restored" |
| August 18, 2024 | **Master license holder (Gaming Curacao/365/JAZ) permanently ceased operations** |
| 2024–present | **Transitional arrangement** — pending application OGL/2024/1260/0494 with new Curaçao Gaming Control Board |

Rollbit has been operating **without a valid, active gaming license** since August 2024. The "transitional arrangement" is not a license — it is a filing acknowledgment. The platform is operating illegally in every jurisdiction that requires a licensed operator, which includes the UK, EU, US, and Australia.

Casino Guru independently rates Rollbit's **Safety Index at 4.1 / 10** (Low).

---

## 7. Fund Custody Model (The Proxy Laundering Structure)

The $123M seizure revealed a critical structural fact: **Rollbit does not custody player funds in its own corporate accounts.**

Instead, funds are routed through:
1. **Platform hot wallets** (the 6 known addresses above)
2. **Personal Binance accounts** of unnamed individuals (proxies)
3. **Anonymous destination wallets** (for large outflows like the 626 BTC)

This is not a legitimate operational treasury structure. It is a **layering scheme** — the second stage of money laundering — designed to place distance between the casino revenue and the operators' identities.

---

## 8. Exit-Scam Risk Score: 7.8 / 10 (CRITICAL)

| Indicator | Score | Evidence |
|-----------|-------|----------|
| Treasury Drainage Rate | 6.0/10 | $59.6M in 5 months |
| Law Enforcement Seizure | **10.0/10** | $123M confirmed seized |
| Token Price Collapse | 7.7/10 | -83% vs claimed $140M in buybacks |
| RLB Liquidity Crisis | **10.0/10** | $2M liquidity on $150M cap |
| Solvency Risk | 8.0/10 | $182M+ displaced vs unknown remaining reserves |
| Regulatory Status | 7.0/10 | No valid license since Aug 2024 |
| Complaint Acceleration | 8.0/10 | 2 cases (2022) → 37+ cases (2025) |
| **Overall** | **7.8/10** | **CRITICAL RISK** |

---

## 9. Legal Exposure Summary

- **Ukraine:** Criminal proceedings active for fraud and money laundering; $123M already seized.
- **UK:** Founders (Daniel Dixon, Jose Llisterri) are British nationals; UK Gambling Commission has jurisdiction over UK-linked operations.
- **Curaçao:** Pending license application can be denied; operating under expired transitional arrangement.
- **US (IC3):** Any US-resident victims can file with FBI's Internet Crime Complaint Center.
- **Civil:** At least 3 separate lawsuits announced (Nono on X; TP-042; TP-024 class action).

---

## 10. Conclusion

Rollbit is not a legitimate casino that occasionally has bad customer service. The on-chain evidence shows:

1. **Its treasury is being systematically drained** through anonymous wallets.
2. **$123M in casino funds were held in a proxy individual's personal account**, confirming deliberate money laundering architecture.
3. **Its native token (RLB) has only $2M in real exit liquidity** against a $150M stated market cap — making it nearly impossible for any large holder to exit without destroying the price, and making the claimed $5M/month buybacks mathematically incoherent.
4. **It has no valid gaming license** and is operating illegally.
5. **Complaint volume is accelerating** as the operators likely prepare for an exit.

Players still holding funds on Rollbit are **unsecured creditors of an insolvent, unregulated entity** whose operators have a documented prior history of running rigged platforms.

---

*Sources: Pechersk District Court (Kyiv), dev.ua, CoinDesk, BeInCrypto, CryptoSlate, Step Finance, ChainCatcher, Chainalysis reporting, IQ.wiki, DotEsports, Blockstream API, Solana RPC, Etherscan, DEXScreener (Uniswap RLB/ETH pool), CoinGecko.*

*→ Continue to [Report 2: Victim Forum Evidence](./REPORT_2_VICTIM_EVIDENCE.md) for 87 documented case victims.*

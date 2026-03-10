# Rollbit Forensic Investigation
**Operator:** Bull Gaming N.V. (Curaçao No. 157086) | **Platform:** Rollbit.com
**Investigation Date:** March 10, 2026

> This investigation concludes Rollbit is **NOT a legitimate operator.** On-chain evidence, law enforcement records, 87 forum cases, and hundreds of public Twitter complaints establish a pattern of systematic theft, capital flight, and financial fraud.

---

## 📋 Investigation Reports

### [Report 1: On-Chain Financial Forensics →](./REPORT_1_ONCHAIN_FORENSICS.md)
Blockchain evidence of treasury drainage, money laundering, RLB token fraud, and regulatory failure.

| Finding | Value |
|---------|-------|
| Documented treasury outflows (5 months) | $59.6M |
| Law enforcement seizure (Ukraine, May 2025) | $123M |
| RLB token liquidity (Uniswap only) | **~$2M** |
| RLB stated market cap | **~$150M** |
| Liquidity-to-cap ratio | **1.3%** — token is not real |
| Exit-scam risk score | **7.8 / 10 CRITICAL** |

### [Report 2: Victim Forum Evidence →](./REPORT_2_VICTIM_EVIDENCE.md)
87 documented victim cases from consumer protection forums.

| Finding | Value |
|---------|-------|
| Documented cases | 87 |
| Confirmed stolen | $495,210 |
| Resolution rate | **4.5%** |
| Largest case | $55,000 (BTC-005) |
| Primary pattern | Win-triggered account blocks |

### [Report 3: Public X (Twitter) Evidence →](./REPORT_3_X_TWITTER_EVIDENCE.md)
Analysis of high-profile social media outcry, viral threads, and public staff conduct.

| Finding | Value |
|---------|-------|
| Documented X Complaints | 305+ |
| Primary Viral Threads | 70+ |
| Pattern Consistency | 100% match with forum cases |
| Key Highlight | $350k account lock; outright DM insults from founders |

---

## 🔑 Key Evidence

1. **$123M seized by Ukrainian court** — linked by Chainalysis to Bull Gaming N.V.; company confirmed in writing funds "actually belong to the casino"
2. **$59.6M in treasury outflows** in 5 months — including 626 BTC moved to anonymous wallet Feb 2026
3. **RLB token: $2M liquidity vs $150M cap** — only on Uniswap, no CEX; claimed $5M/month buybacks mathematically impossible given -83% price decline
4. **No valid license since Aug 2024** — operating under expired transitional arrangement
5. **87 forum victims + 300+ public complaints** — fraud is systematic, not accidental
6. **Founders' prior history** — previously ran CSGODiamonds, caught rigging games (2016 scandal)

---

## 📁 Repository Structure

```
rollbit_forensic/
├── REPORT_1_ONCHAIN_FORENSICS.md   ← On-chain evidence (start here for legal action)
├── REPORT_2_VICTIM_EVIDENCE.md     ← Victim cases (start here for class action)
├── REPORT_3_X_TWITTER_EVIDENCE.md  ← High-profile social media evidence
├── LEGAL_SUBMISSION_TEMPLATE.md    ← Ready-to-file complaint template
│
├── scripts/                        ← Analysis tools
│   ├── blockchain_analyzer.py      # Queries BTC/ETH/SOL wallets live
│   ├── treasury_monitor.py         # Real-time alert monitoring
│   ├── generate_visualizations.py  # Generates all 5 charts
│   ├── victim_collector.py         # Victim evidence collection tool
│   └── run_investigation.py        # One-command orchestrator
│
├── output/
│   ├── charts/                     ← 5 generated evidence charts
│   ├── blockchain_analysis.json    ← On-chain analysis results
│   ├── rollbit_analysis.json       ← Statistical case analysis
│   └── rollbit_cases.csv           ← All cases in spreadsheet form
│
├── cases_database.json             ← 87 cases, machine-readable
└── requirements.txt                ← pip install -r requirements.txt
```

---

## 🚀 Running the Analysis

```bash
# Install dependencies (use your venv)
pip install -r requirements.txt

# Run full offline analysis + generate all 5 charts
python scripts/run_investigation.py --quick

# Run with live blockchain data
python scripts/run_investigation.py --full

# Monitor treasury wallets in real-time
python scripts/treasury_monitor.py --threshold 50000 --dry-run

# Submit victim evidence
python scripts/victim_collector.py --interactive
```

---

## ⚖️ How to Report

See **[LEGAL_SUBMISSION_TEMPLATE.md](./LEGAL_SUBMISSION_TEMPLATE.md)** for a fill-in-the-blank complaint. Key filing destinations:

| Authority | Link | Who |
|-----------|------|-----|
| FBI IC3 | ic3.gov | US-based victims |
| Curaçao GCB | cert.gcb.cw | All victims |
| Action Fraud (UK) | actionfraud.police.uk | UK victims / UK nationals (Dixon, Llisterri) |
| Interpol | interpol.int | International coordination |

---

*Sources: Pechersk District Court of Kyiv, dev.ua, CoinDesk, BeInCrypto, CryptoSlate, ChainCatcher, Chainalysis, IQ.wiki, BitcoinTalk, Trustpilot, Casino Guru, DEXScreener (Uniswap RLB/ETH pool data).*

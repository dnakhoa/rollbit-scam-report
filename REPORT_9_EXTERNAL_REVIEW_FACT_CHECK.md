# Report 9: External Review Fact-Check Matrix
## Defi3000 Feedback, Corrections Applied, and Remaining Collection Tasks
**Date:** May 10, 2026 | **Classification:** Review Response / Data-Quality Appendix

This appendix documents the main external review feedback attributed to X user `Defi3000` and maps each point to the current report language. It is not a rebuttal. It is a quality-control layer so readers can see which claims were narrowed, corrected, or left open for more collection.

---

## 1. Correction Matrix

| Review Point | Current Repo Treatment | Remaining Data Needed |
|--------------|------------------------|-----------------------|
| The prior report used too much author opinion. | Reports now lead with observations, limits, and data gaps. `PUBLISHING_NOTES.md` explicitly avoids legal conclusions and opinion-led framing. | Periodic wording review before publication, especially summaries and chart titles. |
| The earlier treasury-flow framing overstated the problem. | The old overstated outflow framing is removed from active reports. Report 1 now separates direct outflows, inflows, mixed-flow alerts, and off-wallet custody events. | Export transaction-level flow graphs and compare outflows to normal operating payouts, inflows, and monthly operating baseline. |
| Withdrawals may be ordinary operating cost. | Sampled BTC/SOL movements are described as operational wallet activity unless tied to broader transaction evidence. The current finding is a flow-classification dataset, not a drain claim. | Build baseline buckets for routine payouts, wallet maintenance, exchange movements, and unusual high-value transfers. |
| RLB liquidity is not Uniswap-only. | Reports now label the DEX numbers as **tracked public DEX liquidity** only. They explicitly say Rollbit app/on-platform liquidity, order-book depth, and custody-side token inventory are not measured. | Capture Rollbit app/on-platform RLB trading, RLB/USD pool data, liquidity dashboard data, and any public AMM or internal market-depth views. |
| Rollbit has its own RLB market surface. | Report 1 and Report 7 now note Rollbit materials describing direct RLB trading and RLB/USD liquidity pools on Rollbit. | Preserve screenshots, API responses if available, timestamps, and any terms explaining how on-platform liquidity is sourced or priced. |

---

## 2. Current Safe Phrasing

Use:

- The repo has attributed public wallet balances, not verified reserves.
- Direct published outflows are bounded and must be separated from mixed-flow alerts.
- Recent sampled wallet activity looks operational unless a broader transaction graph shows otherwise.
- RLB market cap is not reserve depth.
- The current RLB liquidity metric is a tracked public DEX slice, not complete venue depth.
- Rollbit app/on-platform RLB liquidity remains unmeasured in this artifact set.

Avoid:

- Saying Rollbit wallets are empty.
- Repeating the old overstated outflow number.
- Treating withdrawals as suspicious without an operating baseline.
- Describing Uniswap as the sole RLB trading or liquidity venue.
- Treating public complaint totals as proof of each individual allegation.
- Asking readers to accept a conclusion about intent.

---

## 3. Added Collection Work

The next useful expansion is not stronger wording. It is better venue and flow data:

1. Export recent BTC/SOL transactions into routine payout, exchange, maintenance, and high-value transfer buckets.
2. Capture Rollbit app/on-platform RLB trading and liquidity surfaces with timestamps.
3. Record any available RLB/USD pool mechanics, liquidity-provider terms, fees, and depth indicators.
4. Keep public DEX data, app/on-platform data, exchange custody, and token holder concentration separate in every table.
5. Add a short fact-check line to future summaries when an external reviewer identifies a corrected claim.

---

## Sources

- Report 1: [On-Chain Financial Forensics](./REPORT_1_ONCHAIN_FORENSICS.md)
- Report 7: [Technical Forensic Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)
- Publishing notes: [PUBLISHING_NOTES.md](./PUBLISHING_NOTES.md)
- Rollbit RLB utility post: https://blog.rollbit.com/rlb-utility-guide/amp/
- Rollbot whitepaper provide-liquidity page: https://whitepaper.rollbot.com/rlb-whitepaper/i/utility/provide-liquidity

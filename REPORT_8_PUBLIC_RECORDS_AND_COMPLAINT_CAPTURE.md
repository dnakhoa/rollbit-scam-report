# Report 8: Public Records and Complaint Capture
## Raw Source Preservation, Complaint-Page Coverage, and Capture Gaps
**Generated:** May 10, 2026 | **Classification:** Forensic Acquisition Report

This report adds an acquisition layer on top of the complaint corpus and public-source timeline. It does **not** add new complaint totals. It preserves public source pages already referenced by the repo so later analysis can inspect raw artifacts instead of relying only on summaries.

Machine-readable outputs:

- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)

Local raw-capture directory:

- `output/captures/public_records/20260510T102511Z`

The raw capture directory is intentionally ignored by git for public release. Publish the JSON/CSV source index and hashes; keep raw HTML/body captures local or in a private evidence package.

Capture script:

- [scripts/public_record_capture.py](./scripts/public_record_capture.py)

---

## 1. Acquisition Scope

The May 10 refresh deduplicated source URLs from:

- [cases_database.json](./cases_database.json)
- all `REPORT_*.md` files, including the external review fact-check appendix
- [README.md](./README.md)

The final May 10 pass also added newly identified post-freeze public complaint leads and live RLB market-data endpoints. The goal was to preserve public complaint pages, public reporting, operator publications, public verification pages, passive scan references, Rollbot/RLB whitepaper pages, social corroboration links, and current market-data API responses.

The capture pipeline preserves:

- raw response body
- response headers
- extracted text
- per-page metadata JSON
- SHA-256 body hash
- status code and redirect information
- case IDs and report references tied to each URL
- keyword-marker counts for acquisition triage

---

## 2. Capture Summary

| Metric | Value |
|--------|------:|
| Deduplicated targets | **67** |
| HTTP responses written | **67** |
| Failed captures | **0** |
| Blocked / challenged captures | **4** |
| Capture directory | `output/captures/public_records/20260510T102511Z` |

Status-code breakdown:

| Status | Count | Interpretation |
|--------|------:|----------------|
| `200` | 63 | Page captured successfully |
| `403` | 4 | Page challenged or blocked |

Source-type breakdown:

| Source Type | Targets | Status Notes |
|-------------|--------:|--------------|
| Complaint forum | 24 | All returned `200` |
| Complaint mediation | 12 | All returned `200` |
| Complaint review | 1 | Trustpilot returned `403` verification challenge |
| Operator publication | 3 | All returned `200` |
| Operator surface | 2 | Rollbit supply endpoint returned `200`; `rollbit.com` returned `403` challenge |
| Passive scan | 1 | Returned `200` |
| Public record / market API / Rollbot whitepaper | 8 | Six returned `200`; two Reddit pages returned `403` |
| Public reporting | 8 | All returned `200` |
| Public verification | 3 | All returned `200` |
| Social corroboration | 5 | All returned `200` |

---

## 3. Complaint-Source Coverage

The capture index references **82 case IDs** because the same shared source URL can cover many cases, especially Trustpilot.

| Complaint Source Class | Capture Result | Forensic Meaning |
|------------------------|----------------|------------------|
| Bitcointalk forum threads | **24 / 24 captured with HTTP 200** | Strongest raw-source preservation layer in the current run; includes three post-freeze leads |
| Casino Guru pages | **9 / 9 captured with HTTP 200** | The April 25 `404` gap did not reproduce in the May 10 refresh; includes two post-freeze leads |
| AskGamblers / CasinoListings pages | **3 / 3 captured with HTTP 200** | Mediation/forum source preservation remains intact |
| Trustpilot review page | **HTTP 403 verification challenge** | Current public review page still needs browser/session-aware capture |
| Reddit post-freeze leads | **2 / 2 returned HTTP 403** | Search/browser visibility exists, but passive capture needs alternate acquisition |
| X corroboration links | **5 / 5 captured with HTTP 200** | Useful for URL/body preservation, but still not counted as complaint totals |

Important: this capture run does not validate every public allegation. It preserves what the public URLs returned on May 10, 2026.

---

## 4. Marker Triage From Captured Text

The script extracts text from captured bodies and counts markers. These counts are not complaint totals; they are acquisition triage signals.

| Marker | Keyword Hits Across Captures |
|--------|-----------------------------:|
| Profit / win language | 111 |
| Custody / wallet / transaction language | 88 |
| KYC / compliance language | 79 |
| Withdrawal language | 77 |
| Staff / support / team language | 74 |
| Token / liquidity language | 61 |
| Frozen / blocked / locked language | 53 |
| Multi-account language | 22 |

The May 10 source set still contains the same technical themes surfaced in Reports 2 and 7: withdrawal control, KYC/compliance escalation, account-locking language, wallet/custody references, and token/liquidity context.

---

## 5. Capture Gaps

### 5.1 Trustpilot

Trustpilot returned:

- `HTTP 403`
- title: `Verifying Connection`

This does not invalidate the Trustpilot-derived corpus entries. It means automated passive capture of the public review page did not obtain normal content in this environment. Next step: browser-based capture with screenshots and timestamped session metadata.

### 5.2 Main Rollbit App

`https://rollbit.com/` returned:

- `HTTP 403`
- title: `Just a moment...`

This matches the separate web-surface capture in [Report 4](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md). The main app remains challenge-gated for passive capture.

### 5.3 Casino Guru

The April 25 capture saw seven Casino Guru complaint URLs return `404`. The May 10 refresh captured the mediation set with `HTTP 200`. Those pages should be retained as current raw-source evidence and compared against any older local captures or archive snapshots before changing corpus notes.

### 5.4 Reddit

Two newly identified Reddit complaint/forum leads returned:

- `HTTP 403`
- large response bodies with identical SHA-256 hashes

Those records are preserved as capture attempts, but Reddit items should not be added to complaint totals without browser-readable timestamps, screenshots, and source-quality review.

---

## 6. Post-Freeze Leads Preserved But Not Counted

The May 10 web refresh identified public complaint or review leads after the April 19 corpus freeze. These are **collection leads**, not additions to the canonical 80 counted complaint total.

| Source | URL | Capture Result | Current Handling |
|--------|-----|----------------|------------------|
| Bitcointalk | https://bitcointalk.org/index.php?topic=5581051.0 | `HTTP 200` | Preserve and adjudicate before corpus inclusion |
| Bitcointalk | https://bitcointalk.org/index.php?topic=5581293.msg66655063 | `HTTP 200` | Preserve and adjudicate before corpus inclusion |
| Bitcointalk | https://bitcointalk.org/index.php?topic=5581481.msg66673322 | `HTTP 200` | Preserve and adjudicate before corpus inclusion |
| Casino Guru | https://casino.guru/complaints/rollbit-casino-player-believes-that-their-withdrawal-1 | `HTTP 200` | Preserve and adjudicate before corpus inclusion |
| Casino Guru | https://casino.guru/complaints/rollbit-casino-player-s-account-has-been-restricted-2 | `HTTP 200` | Preserve and adjudicate before corpus inclusion |
| Reddit | https://www.reddit.com/r/gambling/comments/1sruwwt/rollbit_is_blackmailing_vip_players_to_withdraw/ | `HTTP 403` | Browser capture needed |
| Reddit | https://www.reddit.com/r/onlinegambling/comments/1sruzyu/rollbit_is_blackmailing_vip_players_to_withdraw/ | `HTTP 403` | Browser capture needed |

---

## 7. What This Enhances

Before this capture layer, the repo had:

- structured complaint summaries
- source URLs
- generated metrics
- narrative reports

After this capture layer, the repo also has:

- raw public source bodies
- raw headers
- extracted text
- per-source metadata
- body hashes
- capture-time status codes
- a CSV source index for analyst review

This makes the investigation more reproducible. It also keeps the complaint count conservative: source preservation is separate from corpus inclusion.

---

## 8. Recommended Next Capture Work

1. Add browser-driven screenshot capture for Trustpilot and challenge-gated pages.
2. Preserve current Casino Guru pages with screenshots and compare against the May 10 raw hashes.
3. Capture archived versions of removed or changed complaint pages through urlscan, Archive.org, or browser cache where available.
4. Add a source-adjudication column to the corpus: `raw_capture_ok`, `capture_status_code`, `capture_hash`, and `capture_last_seen`.
5. Add a high-fidelity case-file template for firsthand cases.
6. Keep corpus counting separate from source acquisition. A captured page is evidence preservation, not automatic proof.

---

## Sources And Artifacts

- [scripts/public_record_capture.py](./scripts/public_record_capture.py)
- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)
- local raw-capture directory: `output/captures/public_records/20260510T102511Z`
- [cases_database.json](./cases_database.json)
- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 7: Technical Forensic Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)
- CoinGecko RLB API capture: https://api.coingecko.com/api/v3/coins/rollbit-coin
- DEXScreener RLB API capture: https://api.dexscreener.com/latest/dex/tokens/0x046eee2cc3188071c02bfc1745a6b17c656e3f3d
- Rollbit RLB supply API capture: https://api.rollbit.com/v1/public/rlb/supply.json
- Poloniex public markets API capture: https://api.poloniex.com/markets

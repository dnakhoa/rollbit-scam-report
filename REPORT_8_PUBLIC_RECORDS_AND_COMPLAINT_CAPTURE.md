# Report 8: Public Records and Complaint Capture
## Raw Source Preservation, Complaint-Page Coverage, and Capture Gaps
**Generated:** April 25, 2026 | **Classification:** Forensic Acquisition Report

This report adds an acquisition layer on top of the complaint corpus and public-source timeline. It does **not** add new complaint totals. It preserves public source pages already referenced by the repo so later analysis can inspect raw artifacts instead of relying only on summaries.

Machine-readable outputs:

- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)

Local raw-capture directory:

- `output/captures/public_records/20260425T111024Z`

The raw capture directory is intentionally ignored by git for public release. Publish the JSON/CSV source index and hashes; keep raw HTML/body captures local or in a private evidence package.

Capture script:

- [scripts/public_record_capture.py](./scripts/public_record_capture.py)

---

## 1. Acquisition Scope

The capture run deduplicated source URLs from:

- [cases_database.json](./cases_database.json)
- all `REPORT_*.md` files
- [README.md](./README.md)

API endpoints were skipped by default. The goal was to preserve public complaint pages, public reporting, operator publications, public verification pages, passive scan references, and social corroboration links.

The capture pipeline preserves:

- raw response body
- response headers
- extracted text
- per-page metadata JSON
- SHA-256 body hash
- status code and redirect information
- case IDs and report references tied to each URL
- keyword-marker counts for forensic triage

---

## 2. Capture Summary

| Metric | Value |
|--------|------:|
| Deduplicated targets | **53** |
| HTTP captures written | **52** |
| Failed captures | **1** |
| Blocked / challenged captures | **1** |
| Capture directory | `output/captures/public_records/20260425T111024Z` |

Status-code breakdown:

| Status | Count | Interpretation |
|--------|------:|----------------|
| `200` | 44 | Page captured successfully |
| `404` | 7 | Page returned not found at capture time |
| `403` | 1 | Page challenged or blocked |
| `None` | 1 | Request failed before HTTP response |

Source-type breakdown:

| Source Type | Targets | Status Notes |
|-------------|--------:|--------------|
| Complaint forum | 21 | All returned `200` |
| Complaint mediation | 10 | 3 returned `200`; 7 returned `404` |
| Complaint review | 1 | Trustpilot returned `403` verification challenge |
| Operator publication | 3 | All returned `200` |
| Operator surface | 1 | `rollbit.com` failed through local resolver path |
| Passive scan | 1 | Returned `200` |
| Public reporting | 8 | All returned `200` |
| Public verification | 3 | All returned `200` |
| Social corroboration | 5 | All returned `200` |

---

## 3. Complaint-Source Coverage

The capture index references **82 case IDs** because the same shared source URL can cover many cases, especially Trustpilot.

| Complaint Source Class | Capture Result | Forensic Meaning |
|------------------------|----------------|------------------|
| Bitcointalk forum threads | **21 / 21 captured with HTTP 200** | Strongest raw-source preservation layer in the current run |
| Casino Guru pages | **7 URLs returned HTTP 404** | Existing summaries remain in the corpus, but raw pages must be re-checked or archived elsewhere |
| AskGamblers / CasinoListings pages | **3 / 3 captured with HTTP 200** | Mediation/forum source preservation improved |
| Trustpilot review page | **HTTP 403 verification challenge** | Current public review page needs browser/session-aware capture |
| X corroboration links | **5 / 5 captured with HTTP 200** | Useful for URL/body preservation, but still not counted as complaint totals |

Important: this capture run does not validate every public allegation. It preserves what the public URLs returned on April 25, 2026.

---

## 4. Marker Triage From Captured Text

The script extracts text from captured bodies and counts forensic markers. These counts are not complaint totals; they are acquisition triage signals.

| Marker | Keyword Hits Across Captures |
|--------|-----------------------------:|
| Profit / win language | 82 |
| Custody / wallet / transaction language | 66 |
| Withdrawal language | 58 |
| Staff / support / team language | 55 |
| KYC / compliance language | 51 |
| Token / liquidity language | 40 |
| Frozen / blocked / locked language | 28 |
| Multi-account language | 15 |

This confirms that the captured source set contains the same technical themes already surfaced in Reports 2 and 7: withdrawal control, KYC/compliance escalation, account-locking language, wallet/custody references, and token/liquidity context.

---

## 5. Capture Gaps

### 5.1 Trustpilot

Trustpilot returned:

- `HTTP 403`
- title: `Verifying Connection`

This does not invalidate the Trustpilot-derived corpus entries. It means automated passive capture of the public review page did not obtain normal content in this environment. Next step: browser-based capture with screenshots and timestamped session metadata.

### 5.2 Casino Guru

Seven Casino Guru complaint URLs returned `HTTP 404` during this run. The script retried the pages with TLS verification disabled because this Python runtime saw certificate-chain errors for that domain. The pages still returned `404`.

Next steps:

- verify whether the pages moved, were removed, or are region/session-sensitive
- search site archives or cached captures
- preserve screenshots if the pages are reachable in a browser
- keep existing corpus rows labeled according to the prior capture notes until re-adjudicated

### 5.3 Main Rollbit App

`https://rollbit.com/` failed in this script through the local resolver path. This is consistent with the earlier note that this workstation had local resolver complications for `rollbit.com`.

Use [scripts/web_surface_capture.py](./scripts/web_surface_capture.py) for main-domain acquisition because that script uses resolver-independent DoH and `curl --resolve` behavior. See [Report 4](./REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md).

---

## 6. What This Enhances

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

## 7. Recommended Next Capture Work

1. Add browser-driven screenshot capture for Trustpilot, X, and challenge-gated pages.
2. Re-check Casino Guru pages from a normal browser and preserve any reachable content.
3. Capture archived versions of missing complaint pages through urlscan, Archive.org, or browser cache where available.
4. Add a source-adjudication column to the corpus: `raw_capture_ok`, `capture_status_code`, `capture_hash`, and `capture_last_seen`.
5. Add a high-fidelity case-file template for firsthand cases, including your friend's multiple-account accusation case.
6. Keep corpus counting separate from source acquisition. A captured page is evidence preservation, not automatic proof.

---

## Sources And Artifacts

- [scripts/public_record_capture.py](./scripts/public_record_capture.py)
- [output/public_record_capture.json](./output/public_record_capture.json)
- [output/public_record_index.csv](./output/public_record_index.csv)
- local raw-capture directory: `output/captures/public_records/20260425T111024Z`
- [cases_database.json](./cases_database.json)
- [Report 2: Complaint Corpus](./REPORT_2_VICTIM_EVIDENCE.md)
- [Report 7: Technical Forensic Deep Dive](./REPORT_7_TECHNICAL_DEEP_DIVE.md)

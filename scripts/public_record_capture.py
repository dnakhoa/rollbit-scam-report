#!/usr/bin/env python3
"""
Public record and complaint capture pipeline.

This script preserves public source pages already referenced by the report set
and the canonical complaint corpus. It intentionally does not change complaint
counts. Its job is acquisition: raw bytes, headers, extracted text, hashes, and
an index that lets an analyst review source quality later.

Outputs:
    output/public_record_capture.json
    output/public_record_index.csv
    output/captures/public_records/<timestamp>/
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
CAPTURE_ROOT = OUTPUT_DIR / "captures" / "public_records"
SUMMARY_JSON = OUTPUT_DIR / "public_record_capture.json"
INDEX_CSV = OUTPUT_DIR / "public_record_index.csv"
CASES_DB = ROOT / "cases_database.json"

DEFAULT_TIMEOUT = 35
DEFAULT_SLEEP_SECONDS = 0.5

SKIP_API_DOMAINS = {
    "api.coingecko.com",
    "api.dexscreener.com",
    "api.mainnet-beta.solana.com",
    "blockstream.info",
    "cloudflare-dns.com",
}

MARKERS = {
    "withdrawal": ["withdraw", "withdrawal", "payout", "cashout"],
    "kyc": ["kyc", "verification", "source of funds", "proof of income", "compliance"],
    "multi_account": ["multiple account", "multi-account", "multiaccount", "linked account", "duplicate account"],
    "frozen_or_blocked": ["frozen", "blocked", "locked", "disabled", "suspended", "inaccessible"],
    "profit_or_win": ["profit", "profitable", "win", "won", "winning"],
    "staff_or_team": ["razer", "benji", "smokeylisa", "lucky", "founder", "support"],
    "custody_or_wallet": ["wallet", "custody", "binance", "treasury", "address", "transaction"],
    "token": ["rlb", "token", "buyback", "burn", "liquidity", "uniswap"],
}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            cleaned = " ".join(data.split())
            if cleaned:
                self.parts.append(cleaned)

    def text(self) -> str:
        return "\n".join(self.parts)


@dataclass
class SourceTarget:
    url: str
    source_type: str
    source_refs: set[str] = field(default_factory=set)
    case_ids: set[str] = field(default_factory=set)
    source_names: set[str] = field(default_factory=set)


def normalize_url(url: str) -> str:
    url = (url or "").strip().rstrip("`*_.,)")
    if not url.startswith(("http://", "https://")):
        return ""
    parsed = urlparse(url)
    # Fragments are not useful for server capture and create false duplicates.
    parsed = parsed._replace(fragment="")
    return urlunparse(parsed)


def url_key(url: str) -> str:
    return normalize_url(url)


def safe_name(value: str, max_len: int = 80) -> str:
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return value[:max_len] or "capture"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classify_url(url: str, default: str = "public_record") -> str:
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if "bitcointalk.org" in host:
        return "complaint_forum"
    if "trustpilot.com" in host:
        return "complaint_review"
    if "casino.guru" in host or "askgamblers.com" in host or "casinolistings.com" in host:
        return "complaint_mediation"
    if host in {"x.com", "twitter.com"}:
        return "social_corroboration"
    if "blog.rollbit.com" in host:
        return "operator_publication"
    if "chaincatcher.com" in host or "coindesk.com" in host or "cryptoslate.com" in host or "dev.ua" in host:
        return "public_reporting"
    if "cga.cw" in host or "cert.cga.cw" in host:
        return "public_verification"
    if "urlscan.io" in host:
        return "passive_scan"
    if "rollbit.com" in host:
        return "operator_surface"
    if path.endswith((".json", ".csv")):
        return "data_endpoint"
    return default


def add_target(targets: dict[str, SourceTarget], url: str, source_type: str,
               source_ref: str = "", case_id: str = "", source_name: str = "") -> None:
    url = normalize_url(url)
    if not url:
        return
    key = url_key(url)
    if key not in targets:
        targets[key] = SourceTarget(url=url, source_type=source_type)
    target = targets[key]
    if target.source_type == "public_record" and source_type != "public_record":
        target.source_type = source_type
    if source_ref:
        target.source_refs.add(source_ref)
    if case_id:
        target.case_ids.add(case_id)
    if source_name:
        target.source_names.add(source_name)


def load_case_targets(targets: dict[str, SourceTarget]) -> None:
    if not CASES_DB.exists():
        return
    with CASES_DB.open() as f:
        payload = json.load(f)
    for case in payload.get("cases", []):
        url = case.get("source_url", "")
        if not url:
            continue
        add_target(
            targets,
            url,
            classify_url(url, "complaint_record"),
            source_ref="cases_database.json",
            case_id=case.get("case_id", ""),
            source_name=case.get("source", ""),
        )
        for alt in case.get("alternate_urls", []) or []:
            add_target(
                targets,
                alt,
                classify_url(alt, "complaint_record"),
                source_ref="cases_database.json:alternate_urls",
                case_id=case.get("case_id", ""),
                source_name=case.get("source", ""),
            )


def extract_report_urls() -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    for path in sorted(ROOT.glob("REPORT_*.md")) + [ROOT / "README.md"]:
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        for url in re.findall(r"https?://[^\s)<>\"]+", text):
            urls.append((path.name, normalize_url(url)))
    return urls


def load_report_targets(targets: dict[str, SourceTarget], include_apis: bool = False) -> None:
    for ref, url in extract_report_urls():
        if not url:
            continue
        host = urlparse(url).netloc.lower()
        if not include_apis and host in SKIP_API_DOMAINS:
            continue
        add_target(targets, url, classify_url(url), source_ref=ref)


def build_targets(include_cases: bool, include_reports: bool, include_apis: bool,
                  extra_urls: list[str]) -> list[SourceTarget]:
    targets: dict[str, SourceTarget] = {}
    if include_cases:
        load_case_targets(targets)
    if include_reports:
        load_report_targets(targets, include_apis=include_apis)
    for url in extra_urls:
        add_target(targets, url, classify_url(url), source_ref="cli")
    return sorted(targets.values(), key=lambda t: (t.source_type, urlparse(t.url).netloc, t.url))


def extract_title(text: str, content_type: str) -> str:
    if "html" not in content_type.lower():
        return ""
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
    if not match:
        return ""
    return " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())[:240]


def extract_text(body: bytes, content_type: str) -> str:
    if not body:
        return ""
    text = body.decode("utf-8", errors="replace")
    if "html" in content_type.lower() or "<html" in text[:1000].lower():
        parser = TextExtractor()
        try:
            parser.feed(text)
            return parser.text()
        except Exception:
            return " ".join(re.sub(r"<[^>]+>", " ", text).split())
    return text


def marker_counts(text: str) -> dict[str, int]:
    lower = text.lower()
    counts = {}
    for marker, keywords in MARKERS.items():
        counts[marker] = sum(1 for keyword in keywords if keyword in lower)
    return counts


def capture_one(session: requests.Session, target: SourceTarget, capture_dir: Path,
                timeout: int) -> dict[str, Any]:
    parsed = urlparse(target.url)
    digest = hashlib.sha256(target.url.encode()).hexdigest()[:12]
    base = f"{safe_name(parsed.netloc + parsed.path)}_{digest}"
    body_path = capture_dir / f"{base}.body.bin"
    headers_path = capture_dir / f"{base}.headers.txt"
    text_path = capture_dir / f"{base}.text.txt"
    meta_path = capture_dir / f"{base}.meta.json"

    started = datetime.now(timezone.utc).isoformat()
    record: dict[str, Any] = {
        "url": target.url,
        "source_type": target.source_type,
        "source_refs": sorted(target.source_refs),
        "case_ids": sorted(target.case_ids),
        "source_names": sorted(target.source_names),
        "captured_at": started,
        "domain": parsed.netloc.lower(),
    }

    try:
        tls_verified = True
        tls_error = ""
        try:
            resp = session.get(target.url, timeout=timeout, allow_redirects=True)
        except requests.exceptions.SSLError as exc:
            # Some public pages present certificate-chain issues from this runtime.
            # Preserve the page anyway, but mark the capture as TLS-unverified.
            tls_verified = False
            tls_error = str(exc)
            try:
                requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
            except Exception:
                pass
            resp = session.get(target.url, timeout=timeout, allow_redirects=True, verify=False)
        body = resp.content
        content_type = resp.headers.get("content-type", "")
        headers_text = "\n".join(f"{k}: {v}" for k, v in resp.headers.items())
        text = extract_text(body, content_type)
        title = extract_title(body.decode("utf-8", errors="replace"), content_type)

        body_path.write_bytes(body)
        headers_path.write_text(headers_text + "\n", errors="replace")
        text_path.write_text(text, errors="replace")

        history = [
            {"status_code": item.status_code, "url": item.url}
            for item in resp.history
        ]
        record.update({
            "ok": True,
            "status_code": resp.status_code,
            "tls_verified": tls_verified,
            "tls_error": tls_error,
            "final_url": resp.url,
            "redirect_count": len(resp.history),
            "redirect_history": history,
            "content_type": content_type,
            "title": title,
            "body_size_bytes": len(body),
            "body_sha256": sha256_bytes(body),
            "text_size_chars": len(text),
            "marker_counts": marker_counts(text),
            "files": {
                "body": str(body_path.relative_to(ROOT)),
                "headers": str(headers_path.relative_to(ROOT)),
                "text": str(text_path.relative_to(ROOT)),
                "meta": str(meta_path.relative_to(ROOT)),
            },
        })
    except Exception as exc:
        record.update({
            "ok": False,
            "error": str(exc),
            "status_code": None,
            "final_url": "",
            "redirect_count": 0,
            "content_type": "",
            "title": "",
            "body_size_bytes": 0,
            "body_sha256": "",
            "text_size_chars": 0,
            "marker_counts": {},
            "files": {"meta": str(meta_path.relative_to(ROOT))},
        })

    meta_path.write_text(json.dumps(record, indent=2) + "\n")
    return record


def summarize(records: list[dict[str, Any]], capture_dir: Path, targets_count: int) -> dict[str, Any]:
    status_counts = Counter(str(record.get("status_code")) for record in records)
    type_counts = Counter(record.get("source_type", "") for record in records)
    domain_counts = Counter(record.get("domain", "") for record in records)
    marker_totals: Counter[str] = Counter()
    for record in records:
        marker_totals.update(record.get("marker_counts", {}))
    failed = [record for record in records if not record.get("ok")]
    blocked_or_challenged = [
        record for record in records
        if record.get("status_code") in {401, 403, 429, 503}
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capture_dir": str(capture_dir.relative_to(ROOT)),
        "targets_count": targets_count,
        "records_count": len(records),
        "ok_count": sum(1 for record in records if record.get("ok")),
        "failed_count": len(failed),
        "blocked_or_challenged_count": len(blocked_or_challenged),
        "status_counts": dict(status_counts),
        "source_type_counts": dict(type_counts),
        "domain_counts": dict(domain_counts.most_common()),
        "marker_totals": dict(marker_totals),
        "records": records,
    }


def write_index(summary: dict[str, Any]) -> None:
    fieldnames = [
        "source_type",
        "status_code",
        "domain",
        "url",
        "final_url",
        "case_ids",
        "source_refs",
        "title",
        "body_sha256",
        "body_size_bytes",
        "text_size_chars",
        "body_file",
        "text_file",
        "error",
    ]
    with INDEX_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in summary["records"]:
            files = record.get("files", {})
            writer.writerow({
                "source_type": record.get("source_type", ""),
                "status_code": record.get("status_code", ""),
                "domain": record.get("domain", ""),
                "url": record.get("url", ""),
                "final_url": record.get("final_url", ""),
                "case_ids": "|".join(record.get("case_ids", [])),
                "source_refs": "|".join(record.get("source_refs", [])),
                "title": record.get("title", ""),
                "body_sha256": record.get("body_sha256", ""),
                "body_size_bytes": record.get("body_size_bytes", 0),
                "text_size_chars": record.get("text_size_chars", 0),
                "body_file": files.get("body", ""),
                "text_file": files.get("text", ""),
                "error": record.get("error", ""),
            })


def run(include_cases: bool = True, include_reports: bool = True, include_apis: bool = False,
        extra_urls: list[str] | None = None, max_targets: int = 0,
        timeout: int = DEFAULT_TIMEOUT, sleep_seconds: float = DEFAULT_SLEEP_SECONDS) -> dict[str, Any]:
    if not HAS_REQUESTS:
        raise RuntimeError("requests is required. Install dependencies with: pip install -r requirements.txt")

    extra_urls = extra_urls or []
    targets = build_targets(include_cases, include_reports, include_apis, extra_urls)
    if max_targets > 0:
        targets = targets[:max_targets]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    capture_dir = CAPTURE_ROOT / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "RollbitForensicCapture/1.0 (+local forensic preservation)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    records = []
    for idx, target in enumerate(targets, start=1):
        print(f"  [{idx}/{len(targets)}] {target.source_type}: {target.url}")
        records.append(capture_one(session, target, capture_dir, timeout))
        if sleep_seconds > 0 and idx < len(targets):
            time.sleep(sleep_seconds)

    summary = summarize(records, capture_dir, len(targets))
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    write_index(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture public records and complaint source pages")
    parser.add_argument("--cases-only", action="store_true", help="Capture only URLs from cases_database.json")
    parser.add_argument("--reports-only", action="store_true", help="Capture only URLs cited in markdown reports")
    parser.add_argument("--include-apis", action="store_true", help="Include API endpoint URLs cited in reports")
    parser.add_argument("--url", action="append", default=[], help="Additional URL to capture")
    parser.add_argument("--max-targets", type=int, default=0, help="Limit number of targets")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout seconds")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS, help="Delay between requests")
    args = parser.parse_args()

    include_cases = not args.reports_only
    include_reports = not args.cases_only

    summary = run(
        include_cases=include_cases,
        include_reports=include_reports,
        include_apis=args.include_apis,
        extra_urls=args.url,
        max_targets=args.max_targets,
        timeout=args.timeout,
        sleep_seconds=args.sleep,
    )

    print("\nPublic record capture complete")
    print(f"  Records: {summary['records_count']}")
    print(f"  OK: {summary['ok_count']} | Failed: {summary['failed_count']} | Blocked/challenged: {summary['blocked_or_challenged_count']}")
    print(f"  Capture dir: {summary['capture_dir']}")
    print(f"  JSON: {SUMMARY_JSON}")
    print(f"  CSV:  {INDEX_CSV}")


if __name__ == "__main__":
    main()

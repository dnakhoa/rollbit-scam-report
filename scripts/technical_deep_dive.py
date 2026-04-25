#!/usr/bin/env python3
"""
Rollbit technical forensic deep-dive generator.

This script converts the existing report artifacts into analyst-facing
technical indicators. It does not decide legal liability. It scores observable
data quality, custody visibility, token liquidity stress, complaint-pattern
structure, and acquisition gaps.

Outputs:
    output/technical_deep_dive.json
    output/forensic_indicators.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
CASES_DB = ROOT / "cases_database.json"
CORPUS_METRICS = OUTPUT_DIR / "corpus_metrics.json"
BLOCKCHAIN_ANALYSIS = OUTPUT_DIR / "blockchain_analysis.json"
WEB_SURFACE_CAPTURE = OUTPUT_DIR / "web_surface_capture.json"
PUBLIC_RECORD_CAPTURE = OUTPUT_DIR / "public_record_capture.json"
DEEP_DIVE_JSON = OUTPUT_DIR / "technical_deep_dive.json"
INDICATORS_CSV = OUTPUT_DIR / "forensic_indicators.csv"


FALLBACK_WALLET_SNAPSHOT = [
    {
        "chain": "BTC",
        "address": "bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu",
        "label": "Rollbit BTC Treasury",
        "balance_native": 649.54550772,
        "balance_usd": 48_758_133.54,
        "tx_count": 469_936,
        "fetched_at": "2026-04-19T09:23:00+00:00",
    },
    {
        "chain": "SOL",
        "address": "RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx",
        "label": "Rollbit SOL Treasury",
        "balance_native": 222_587.110683,
        "balance_usd": 18_862_031.76,
        "tx_count": 0,
        "fetched_at": "2026-04-19T09:24:00+00:00",
    },
]


FALLBACK_TREASURY_EVENTS = [
    {"date": "2025-05-09", "direction": "seizure", "amount_usd": 123_000_000},
    {"date": "2025-09-03", "direction": "outflow", "amount_usd": 10_170_000},
    {"date": "2026-01-09", "direction": "inflow", "amount_usd": 45_190_000},
    {"date": "2026-01-11", "direction": "outflow", "amount_usd": 2_050_000},
    {"date": "2026-01-11", "direction": "outflow", "amount_usd": 2_040_000},
    {"date": "2026-01-15", "direction": "outflow", "amount_usd": 3_140_000},
    {"date": "2026-02-13", "direction": "mixed", "amount_usd": 42_210_000},
    {"date": "2026-03-11", "direction": "mixed", "amount_usd": 13_910_000},
]


RLB_MARKET_SNAPSHOT = {
    "snapshot_date": "2026-04-19",
    "price_usd": 0.059523,
    "market_cap_usd": 101_223_201,
    "top_4_pool_liquidity_usd": 4_713_083.87,
    "top_4_pool_volume_24h_usd": 153_106.24,
    "ath_drawdown_pct": -77.49,
}


INDICATOR_KEYWORDS = {
    "withdrawal_control": [
        "withdraw", "withdrawal", "payout", "release funds", "blocked",
        "frozen", "withheld", "inaccessible", "not release", "refused to release",
    ],
    "kyc_escalation": [
        "kyc", "verification", "level 3", "level 4", "level 5",
        "source of funds", "proof of income", "compliance", "document",
    ],
    "post_win_or_profit": [
        "win", "won", "winning", "profit", "profitable", "after becoming profitable",
        "sports wins", "winning streak",
    ],
    "multi_account_script": [
        "multiple account", "multiple-account", "multi-account", "multiaccount",
        "linked account", "linked accounts", "other accounts", "duplicate account",
    ],
    "support_silence": [
        "stopped responding", "ignored", "no response", "vague support",
        "support stopped", "not responding",
    ],
    "return_to_origin_address": [
        "original deposit address", "shared deposit address", "ftx", "inaccessible address",
        "returned to", "sent withdrawal to original",
    ],
    "maintenance_or_market_event": [
        "maintenance", "futures", "liquidation", "leverage", "funding",
        "slippage", "price", "market",
    ],
    "named_staff_or_team": [
        "razer", "benji", "smokeylisa", "legal & compliance", "complaint-team",
    ],
}


SOURCE_TIERS = {
    "bitcointalk": "direct_forum_thread",
    "casino_guru": "mediated_complaint_page",
    "askgamblers": "mediated_complaint_page",
    "casinolistings": "mediated_complaint_page",
    "trustpilot": "review_page_claim",
    "x": "social_corrob_only",
}


TECHNICAL_IOCS = {
    "domains": [
        "rollbit.com",
        "blog.rollbit.com",
        "rollbot.rollbit.com",
        "cert.cga.cw",
    ],
    "wallets": [
        "bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu",
        "RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx",
        "0xCBD6832Ebc203e49E2B771897067fce3c58575ac",
        "0xef8801eaf234ff82801821ffe2d78d60a0237f97",
        "0x46dcA395D20E63Cb0Fe1EDC9f0e6f012E77c0913",
        "0x8aE57A027c63fcA8070D1Bf38622321dE8004c67",
        "0x046EeE2cc3188071C02BfC1745A6b17c656e3f3d",
    ],
    "public_apis": [
        "https://blockstream.info/api",
        "https://api.mainnet-beta.solana.com",
        "https://api.coingecko.com/api/v3",
        "https://api.dexscreener.com/latest/dex",
    ],
}


TOKEN_CONTROL_GAPS = [
    "RLB deployer/admin authority map",
    "RLB buy-and-burn execution wallet map",
    "Top-holder and LP-wallet clustering",
    "Known team/founder/affiliate wallet attribution",
    "Exchange custody path for RLB inventory",
    "Withdrawal decisioning and compliance-control workflow",
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def canonical_cases(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("cases"), list):
        return payload["cases"]
    return []


def case_text(case: dict[str, Any]) -> str:
    fields = [
        case.get("title", ""),
        case.get("summary", ""),
        case.get("rollbit_response", ""),
        case.get("notes_on_verification", ""),
    ]
    return " ".join(str(field) for field in fields if field).lower()


def marker_hits(case: dict[str, Any]) -> dict[str, bool]:
    text = case_text(case)
    hits = {}
    for marker, keywords in INDICATOR_KEYWORDS.items():
        hits[marker] = any(keyword in text for keyword in keywords)
    return hits


def amount_bucket(amount: float | None) -> str:
    if amount is None:
        return "unquantified"
    if amount < 500:
        return "<$500"
    if amount < 1_000:
        return "$500-$999"
    if amount < 5_000:
        return "$1K-$4.9K"
    if amount < 10_000:
        return "$5K-$9.9K"
    if amount < 25_000:
        return "$10K-$24.9K"
    if amount < 50_000:
        return "$25K-$49.9K"
    return "$50K+"


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    counted = [case for case in cases if case.get("counted_in_totals", True)]
    quantified = [case for case in counted if case.get("amount_usd") is not None]
    confirmed = [case for case in quantified if case.get("amount_status") == "confirmed"]
    claimed = [case for case in quantified if case.get("amount_status") == "claimed"]

    marker_counts: dict[str, dict[str, float]] = {}
    per_case_hits = {}
    for case in counted:
        hits = marker_hits(case)
        per_case_hits[case["case_id"]] = hits
        amount = float(case.get("amount_usd") or 0)
        for marker, hit in hits.items():
            if not hit:
                continue
            marker_counts.setdefault(marker, {"cases": 0, "amount_usd": 0.0})
            marker_counts[marker]["cases"] += 1
            marker_counts[marker]["amount_usd"] += amount

    compounds = {
        "withdrawal_control+kyc_escalation": ["withdrawal_control", "kyc_escalation"],
        "withdrawal_control+post_win_or_profit": ["withdrawal_control", "post_win_or_profit"],
        "post_win_or_profit+kyc_escalation": ["post_win_or_profit", "kyc_escalation"],
        "multi_account_script+kyc_escalation": ["multi_account_script", "kyc_escalation"],
        "withdrawal_control+kyc_escalation+post_win_or_profit": [
            "withdrawal_control", "kyc_escalation", "post_win_or_profit",
        ],
    }
    compound_counts = {}
    for name, required in compounds.items():
        matches = []
        amount = 0.0
        for case in counted:
            hits = per_case_hits[case["case_id"]]
            if all(hits.get(marker) for marker in required):
                matches.append(case["case_id"])
                amount += float(case.get("amount_usd") or 0)
        compound_counts[name] = {
            "cases": len(matches),
            "amount_usd": round(amount, 2),
            "case_ids": matches[:25],
        }

    category_stats = defaultdict(lambda: {
        "cases": 0,
        "amount_usd": 0.0,
        "unresolved_cases": 0,
        "confirmed_cases": 0,
        "claimed_cases": 0,
        "confidence_total": 0.0,
    })
    source_stats = defaultdict(lambda: {
        "cases": 0,
        "quantified_cases": 0,
        "amount_usd": 0.0,
        "confirmed_cases": 0,
        "claimed_cases": 0,
        "live_captures": 0,
        "confidence_total": 0.0,
    })
    buckets = Counter()
    yearly = Counter()
    for case in counted:
        amount = float(case.get("amount_usd") or 0)
        confidence = float(case.get("confidence_score") or 0)
        category = case.get("category") or "unknown"
        source = case.get("source") or "unknown"
        amount_status = case.get("amount_status")

        cstat = category_stats[category]
        cstat["cases"] += 1
        cstat["amount_usd"] += amount
        cstat["confidence_total"] += confidence
        if case.get("status") != "RESOLVED":
            cstat["unresolved_cases"] += 1
        if amount_status == "confirmed":
            cstat["confirmed_cases"] += 1
        if amount_status == "claimed":
            cstat["claimed_cases"] += 1

        sstat = source_stats[source]
        sstat["cases"] += 1
        sstat["amount_usd"] += amount
        sstat["confidence_total"] += confidence
        if case.get("amount_usd") is not None:
            sstat["quantified_cases"] += 1
        if amount_status == "confirmed":
            sstat["confirmed_cases"] += 1
        if amount_status == "claimed":
            sstat["claimed_cases"] += 1
        if case.get("source_capture_method") == "live_public_capture":
            sstat["live_captures"] += 1

        buckets[amount_bucket(case.get("amount_usd"))] += 1
        if case.get("post_date"):
            yearly[case["post_date"][:4]] += 1

    category_out = []
    for category, stat in category_stats.items():
        cases_count = stat["cases"]
        avg_conf = stat["confidence_total"] / cases_count if cases_count else 0
        unresolved_rate = stat["unresolved_cases"] / cases_count if cases_count else 0
        severity_score = (
            math.log10(stat["amount_usd"] + 1) * 1.8
            + unresolved_rate * 2.0
            + (stat["confirmed_cases"] / cases_count if cases_count else 0)
        )
        category_out.append({
            "category": category,
            "cases": cases_count,
            "amount_usd": round(stat["amount_usd"], 2),
            "unresolved_rate": round(unresolved_rate, 4),
            "confirmed_cases": stat["confirmed_cases"],
            "claimed_cases": stat["claimed_cases"],
            "avg_confidence": round(avg_conf, 3),
            "technical_severity_score": round(severity_score, 2),
        })
    category_out.sort(key=lambda item: item["technical_severity_score"], reverse=True)

    source_out = []
    for source, stat in source_stats.items():
        cases_count = stat["cases"]
        source_out.append({
            "source": source,
            "tier": SOURCE_TIERS.get(source, "unknown"),
            "cases": cases_count,
            "quantified_cases": stat["quantified_cases"],
            "amount_usd": round(stat["amount_usd"], 2),
            "confirmed_cases": stat["confirmed_cases"],
            "claimed_cases": stat["claimed_cases"],
            "live_captures": stat["live_captures"],
            "avg_confidence": round(stat["confidence_total"] / cases_count, 3) if cases_count else 0,
        })
    source_out.sort(key=lambda item: item["cases"], reverse=True)

    duplicate_candidates = find_duplicate_candidates(counted)

    first_date = min((parse_date(case.get("post_date", "")) for case in counted if case.get("post_date")), default=None)
    last_date = max((parse_date(case.get("post_date", "")) for case in counted if case.get("post_date")), default=None)
    ytd_2026 = yearly.get("2026", 0)
    freeze_day = date(2026, 4, 19).timetuple().tm_yday
    annualized_2026 = round(ytd_2026 / freeze_day * 365, 1) if freeze_day else 0

    return {
        "counted_cases": len(counted),
        "quantified_cases": len(quantified),
        "confirmed_cases": len(confirmed),
        "claimed_cases": len(claimed),
        "unquantified_cases": len(counted) - len(quantified),
        "quantified_amount_usd": round(sum(float(case["amount_usd"]) for case in quantified), 2),
        "confirmed_amount_usd": round(sum(float(case["amount_usd"]) for case in confirmed), 2),
        "claimed_amount_usd": round(sum(float(case["amount_usd"]) for case in claimed), 2),
        "first_case_date": first_date.isoformat() if first_date else "",
        "latest_case_date": last_date.isoformat() if last_date else "",
        "yearly_counts": dict(sorted(yearly.items())),
        "annualized_2026_case_rate": annualized_2026,
        "marker_counts": marker_counts,
        "compound_patterns": compound_counts,
        "category_stats": category_out,
        "source_fidelity": source_out,
        "amount_buckets": dict(buckets),
        "duplicate_candidates": duplicate_candidates,
    }


def find_duplicate_candidates(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    quantified = [case for case in cases if case.get("amount_usd") is not None]
    candidates = []
    for i, left in enumerate(quantified):
        left_group = left.get("cross_post_group") or ""
        for right in quantified[i + 1:]:
            right_group = right.get("cross_post_group") or ""
            if left_group and left_group == right_group:
                continue
            left_amount = float(left["amount_usd"])
            right_amount = float(right["amount_usd"])
            tolerance = max(1.0, max(left_amount, right_amount) * 0.01)
            if abs(left_amount - right_amount) > tolerance:
                continue

            left_date = parse_date(left.get("post_date", ""))
            right_date = parse_date(right.get("post_date", ""))
            date_delta = abs((left_date - right_date).days) if left_date and right_date else 9999
            same_username = bool(
                left.get("username_forum")
                and left.get("username_forum") == right.get("username_forum")
            )
            if date_delta > 31 and not same_username:
                continue

            score = 0.45
            if date_delta <= 7:
                score += 0.25
            elif date_delta <= 31:
                score += 0.15
            if left.get("category") == right.get("category"):
                score += 0.15
            if same_username:
                score += 0.25
            if left.get("source") != right.get("source"):
                score += 0.05

            if score >= 0.65:
                candidates.append({
                    "case_a": left["case_id"],
                    "case_b": right["case_id"],
                    "amount_a": left_amount,
                    "amount_b": right_amount,
                    "date_delta_days": date_delta if date_delta != 9999 else None,
                    "source_a": left.get("source", ""),
                    "source_b": right.get("source", ""),
                    "category": left.get("category", ""),
                    "score": round(score, 2),
                })
    candidates.sort(key=lambda item: (-item["score"], item["date_delta_days"] or 9999))
    return candidates[:20]


def summarize_onchain(blockchain: dict[str, Any]) -> dict[str, Any]:
    wallets = blockchain.get("wallets") or FALLBACK_WALLET_SNAPSHOT
    events = blockchain.get("treasury_flows", {}).get("known_events") or FALLBACK_TREASURY_EVENTS

    visible_wallet_usd = sum(float(wallet.get("balance_usd") or 0) for wallet in wallets)
    visible_btc_sol_usd = sum(
        float(wallet.get("balance_usd") or 0)
        for wallet in wallets
        if wallet.get("chain") in {"BTC", "SOL"}
    )
    direct_outflow = sum(float(event.get("amount_usd") or 0) for event in events if event.get("direction") == "outflow")
    inflow = sum(float(event.get("amount_usd") or 0) for event in events if event.get("direction") == "inflow")
    mixed = sum(float(event.get("amount_usd") or 0) for event in events if event.get("direction") == "mixed")
    off_wallet_event = sum(float(event.get("amount_usd") or 0) for event in events if event.get("direction") == "seizure")
    jan_2026_outflow = sum(
        float(event.get("amount_usd") or 0)
        for event in events
        if event.get("direction") == "outflow" and str(event.get("date", "")).startswith("2026-01")
    )

    return {
        "mode": blockchain.get("mode", "fallback_or_live"),
        "snapshot_note": blockchain.get("snapshot_note", ""),
        "wallet_count": len(wallets),
        "visible_wallet_usd": round(visible_wallet_usd, 2),
        "visible_btc_sol_usd": round(visible_btc_sol_usd, 2),
        "direct_outflow_usd": round(direct_outflow, 2),
        "jan_2026_direct_outflow_usd": round(jan_2026_outflow, 2),
        "known_inflow_usd": round(inflow, 2),
        "mixed_flow_usd": round(mixed, 2),
        "reported_off_wallet_event_usd": round(off_wallet_event, 2),
        "direct_outflow_to_visible_wallet_ratio": round(direct_outflow / visible_wallet_usd, 4) if visible_wallet_usd else None,
        "jan_2026_outflow_to_visible_wallet_ratio": round(jan_2026_outflow / visible_wallet_usd, 4) if visible_wallet_usd else None,
        "reported_off_wallet_to_visible_wallet_ratio": round(off_wallet_event / visible_wallet_usd, 4) if visible_wallet_usd else None,
        "wallets": wallets,
        "events_by_direction": dict(Counter(event.get("direction", "unknown") for event in events)),
    }


def summarize_rlb() -> dict[str, Any]:
    liquidity = RLB_MARKET_SNAPSHOT["top_4_pool_liquidity_usd"]
    market_cap = RLB_MARKET_SNAPSHOT["market_cap_usd"]
    volume = RLB_MARKET_SNAPSHOT["top_4_pool_volume_24h_usd"]
    return {
        **RLB_MARKET_SNAPSHOT,
        "liquidity_to_market_cap_ratio": round(liquidity / market_cap, 4),
        "volume_24h_to_liquidity_ratio": round(volume / liquidity, 4),
        "liquidity_turnover_days_at_24h_volume": round(liquidity / volume, 1) if volume else None,
        "one_pct_market_cap_vs_liquidity_ratio": round((market_cap * 0.01) / liquidity, 4),
        "five_pct_market_cap_vs_liquidity_ratio": round((market_cap * 0.05) / liquidity, 4),
    }


def build_findings(
    corpus: dict[str, Any],
    onchain: dict[str, Any],
    rlb: dict[str, Any],
    public_capture: dict[str, Any],
) -> list[dict[str, Any]]:
    compound = corpus["compound_patterns"]
    marker = corpus["marker_counts"]
    multi_account_cases = next(
        (item["cases"] for item in corpus["category_stats"] if item["category"] == "multiple_accounts_accusation"),
        0,
    )
    confirmed_share = corpus["confirmed_cases"] / corpus["quantified_cases"] if corpus["quantified_cases"] else 0

    return [
        {
            "finding_id": "TF-01",
            "severity": "high",
            "confidence": "high",
            "name": "Known public wallets are not verified reserves",
            "finding": (
                f"The loaded wallet snapshot shows {money(onchain['visible_wallet_usd'])} in attributed public wallets, "
                "but the repo has no liability-matched proof-of-reserves artifact, complete custody inventory, "
                "exchange balance attestation, or customer-fund segregation evidence."
            ),
            "primary_artifacts": "REPORT_1_ONCHAIN_FORENSICS.md; output/blockchain_analysis.json",
            "next_steps": "Run refreshed wallet snapshots and pair them with liability, exchange-custody, wallet-control, and segregation evidence before calling anything a reserve.",
        },
        {
            "finding_id": "TF-02",
            "severity": "medium",
            "confidence": "high",
            "name": "Direct outflow narrative is bounded and mostly SOL",
            "finding": (
                f"Direct published outflows total {money(onchain['direct_outflow_usd'])}, equal to "
                f"{pct(onchain['direct_outflow_to_visible_wallet_ratio'] or 0)} of the visible wallet snapshot. "
                "Mixed BTC alerts should remain separated from direct Rollbit outflows."
            ),
            "primary_artifacts": "REPORT_1_ONCHAIN_FORENSICS.md; REPORT_5_NEWS_AND_REGULATORY_TIMELINE.md",
            "next_steps": "For each published alert, preserve original alert text, explorer links, counterparty labels, and direction classification.",
        },
        {
            "finding_id": "TF-03",
            "severity": "high",
            "confidence": "high",
            "name": "RLB exit liquidity is thin relative to headline value",
            "finding": (
                f"Top-four DEX pool liquidity is {money(rlb['top_4_pool_liquidity_usd'])}, only "
                f"{pct(rlb['liquidity_to_market_cap_ratio'])} of the {money(rlb['market_cap_usd'])} market cap. "
                f"A 5% market-cap notional equals {pct(rlb['five_pct_market_cap_vs_liquidity_ratio'])} of visible top-pool liquidity."
            ),
            "primary_artifacts": "REPORT_1_ONCHAIN_FORENSICS.md; DEXScreener snapshot",
            "next_steps": "Collect pool-level reserves, fee tiers, tick liquidity, and holder concentration for a slippage model.",
        },
        {
            "finding_id": "TF-04",
            "severity": "high",
            "confidence": "medium",
            "name": "Complaint corpus contains a repeated control-trigger pattern",
            "finding": (
                f"{compound['withdrawal_control+kyc_escalation+post_win_or_profit']['cases']} counted cases mention "
                "withdrawal control, KYC/compliance escalation, and win/profit context together. "
                f"The compound set totals {money(compound['withdrawal_control+kyc_escalation+post_win_or_profit']['amount_usd'])}."
            ),
            "primary_artifacts": "cases_database.json; output/corpus_metrics.json",
            "next_steps": "Re-capture each compound-pattern source page and store page hashes/screenshots.",
        },
        {
            "finding_id": "TF-05",
            "severity": "high",
            "confidence": "high",
            "name": "Multiple-account accusation is the dominant dispute script",
            "finding": (
                f"The canonical category count shows {multi_account_cases} multiple-account accusation cases out of "
                f"{corpus['counted_cases']} counted complaints. Keyword extraction also finds "
                f"{marker.get('multi_account_script', {}).get('cases', 0)} cases with linked-account language."
            ),
            "primary_artifacts": "REPORT_2_VICTIM_EVIDENCE.md; cases_database.json",
            "next_steps": "Separate cases where Rollbit publicly supplied evidence from cases where the accusation is only asserted.",
        },
        {
            "finding_id": "TF-06",
            "severity": "medium",
            "confidence": "high",
            "name": "Corpus fidelity must be split by evidence class",
            "finding": (
                f"{corpus['confirmed_cases']} quantified cases are marked confirmed and {corpus['claimed_cases']} are marked claimed. "
                f"Confirmed quantified cases represent {pct(confirmed_share)} of quantified case count and "
                f"{money(corpus['confirmed_amount_usd'])} of quantified amount."
            ),
            "primary_artifacts": "cases_database.json; output/forensic_indicators.csv",
            "next_steps": "Do not combine confirmed forum/mediation amounts and Trustpilot-style claimed amounts without labeling the class split.",
        },
        {
            "finding_id": "TF-07",
            "severity": "medium",
            "confidence": "high",
            "name": "Duplicate risk is bounded but still needs analyst review",
            "finding": (
                f"The duplicate heuristic produced {len(corpus['duplicate_candidates'])} candidate pairs after preserving explicit cross-post exclusions. "
                "These are candidates, not automatic removals."
            ),
            "primary_artifacts": "cases_database.json; output/technical_deep_dive.json",
            "next_steps": "Manually review candidate pairs before changing corpus totals.",
        },
        {
            "finding_id": "TF-08",
            "severity": "medium",
            "confidence": "high",
            "name": "Web acquisition should preserve challenge and content layers separately",
            "finding": (
                "The technical surface splits into Cloudflare-gated app endpoints and a separately hosted Ghost/Fastly blog. "
                "Forensic acquisition should therefore preserve DNS, TLS, edge headers, challenge HTML, and blog HTML as separate artifacts."
            ),
            "primary_artifacts": "REPORT_4_WEBSITE_TECHNICAL_INVESTIGATION.md",
            "next_steps": "Store raw curl output, openssl certificate output, DoH JSON, urlscan references, and content hashes per capture.",
        },
        {
            "finding_id": "TF-09",
            "severity": "high",
            "confidence": "medium",
            "name": "Operating controls and token-control attribution remain insufficiently mapped",
            "finding": (
                "Current artifacts do not establish who controls exchange custody, withdrawal decisioning, RLB admin/deployer paths, "
                "buy-and-burn execution wallets, LP positions, market-making wallets, or team/affiliate token clusters."
            ),
            "primary_artifacts": "REPORT_7_TECHNICAL_DEEP_DIVE.md; output/technical_deep_dive.json",
            "next_steps": "Build an RLB and operations control map covering deployer/admin rights, top holders, LP wallets, burn wallets, exchange custody, and public team/affiliate wallet links.",
        },
        {
            "finding_id": "TF-10",
            "severity": "medium",
            "confidence": "high",
            "name": "Public complaint and record acquisition is reproducible but incomplete",
            "finding": (
                f"The latest public-record capture preserved {public_capture.get('records_count', 0)} deduplicated targets, "
                f"with {public_capture.get('ok_count', 0)} HTTP captures written, "
                f"{public_capture.get('blocked_or_challenged_count', 0)} blocked/challenged target, and "
                f"{public_capture.get('failed_count', 0)} request failure. Capture gaps should drive browser-aware follow-up."
            ),
            "primary_artifacts": "REPORT_8_PUBLIC_RECORDS_AND_COMPLAINT_CAPTURE.md; output/public_record_capture.json; output/public_record_index.csv",
            "next_steps": "Add browser screenshots for Trustpilot and challenge-gated pages, re-check Casino Guru 404s, and map capture hashes back into cases_database.json.",
        },
    ]


def build_deep_dive() -> dict[str, Any]:
    cases_payload = load_json(CASES_DB, {"cases": []})
    metrics = load_json(CORPUS_METRICS, {})
    blockchain = load_json(BLOCKCHAIN_ANALYSIS, {})
    web_capture = load_json(WEB_SURFACE_CAPTURE, {})
    public_record_capture = load_json(PUBLIC_RECORD_CAPTURE, {})

    cases = canonical_cases(cases_payload)
    corpus = summarize_cases(cases)
    onchain = summarize_onchain(blockchain)
    rlb = summarize_rlb()
    public_capture = summarize_public_record_capture(public_record_capture)
    findings = build_findings(corpus, onchain, rlb, public_capture)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_artifacts": {
            "cases_database": str(CASES_DB.relative_to(ROOT)),
            "corpus_metrics": str(CORPUS_METRICS.relative_to(ROOT)),
            "blockchain_analysis": str(BLOCKCHAIN_ANALYSIS.relative_to(ROOT)),
            "web_surface_capture": str(WEB_SURFACE_CAPTURE.relative_to(ROOT)) if WEB_SURFACE_CAPTURE.exists() else "",
            "public_record_capture": str(PUBLIC_RECORD_CAPTURE.relative_to(ROOT)) if PUBLIC_RECORD_CAPTURE.exists() else "",
        },
        "scope_note": (
            "Technical forensic synthesis. Legal/regulatory references are treated only as source context "
            "or custody-location signals."
        ),
        "corpus_metrics_from_existing_file": metrics,
        "corpus_signal_analysis": corpus,
        "onchain_visibility_analysis": onchain,
        "rlb_market_structure": rlb,
        "web_surface_capture": summarize_web_capture(web_capture),
        "public_record_capture": public_capture,
        "token_and_operating_control_gaps": TOKEN_CONTROL_GAPS,
        "technical_iocs": TECHNICAL_IOCS,
        "findings": findings,
    }


def summarize_web_capture(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {}
    targets = []
    for result in payload.get("results", []):
        target = result.get("target", {})
        http = result.get("http", {})
        tls = result.get("tls", {})
        targets.append({
            "name": target.get("name", ""),
            "host": target.get("host", ""),
            "path": target.get("path", ""),
            "selected_ip": result.get("selected_ip", ""),
            "final_status": http.get("final_status", ""),
            "body_size_bytes": http.get("body_size_bytes", 0),
            "body_sha256": http.get("body_sha256", ""),
            "headers_file": http.get("headers_file", ""),
            "body_file": http.get("body_file", ""),
            "tls_parsed": tls.get("parsed", ""),
        })
    return {
        "generated_at": payload.get("generated_at", ""),
        "capture_dir": payload.get("capture_dir", ""),
        "targets": targets,
    }


def summarize_public_record_capture(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {}
    return {
        "generated_at": payload.get("generated_at", ""),
        "capture_dir": payload.get("capture_dir", ""),
        "targets_count": payload.get("targets_count", 0),
        "records_count": payload.get("records_count", 0),
        "ok_count": payload.get("ok_count", 0),
        "failed_count": payload.get("failed_count", 0),
        "blocked_or_challenged_count": payload.get("blocked_or_challenged_count", 0),
        "status_counts": payload.get("status_counts", {}),
        "source_type_counts": payload.get("source_type_counts", {}),
        "marker_totals": payload.get("marker_totals", {}),
    }


def write_outputs(payload: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "technical_deep_dive.json").open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    fieldnames = ["finding_id", "severity", "confidence", "name", "finding", "primary_artifacts", "next_steps"]
    with (output_dir / "forensic_indicators.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for finding in payload["findings"]:
            writer.writerow({key: finding.get(key, "") for key in fieldnames})


def run(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    payload = build_deep_dive()
    write_outputs(payload, output_dir)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate technical forensic deep-dive artifacts")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    payload = run(output_dir)
    corpus = payload["corpus_signal_analysis"]
    onchain = payload["onchain_visibility_analysis"]
    rlb = payload["rlb_market_structure"]

    print("Technical deep dive generated")
    print(f"  Findings: {len(payload['findings'])}")
    print(f"  Counted cases: {corpus['counted_cases']}")
    print(f"  Visible wallet snapshot: {money(onchain['visible_wallet_usd'])}")
    print(f"  RLB liquidity / market cap: {pct(rlb['liquidity_to_market_cap_ratio'])}")
    print(f"  JSON: {output_dir / 'technical_deep_dive.json'}")
    print(f"  CSV:  {output_dir / 'forensic_indicators.csv'}")


if __name__ == "__main__":
    main()

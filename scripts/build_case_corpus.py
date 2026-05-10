#!/usr/bin/env python3
"""
Build a canonical Rollbit complaint corpus.

This script:
1. Imports the legacy flat CSV export already in the repository.
2. Normalizes those rows into a canonical `cases` list with provenance fields.
3. Applies explicit dedupe rules where cross-posting is documented.
4. Appends newly verified public complaints through 2026-04-19.
5. Emits:
   - cases_database.json
   - output/rollbit_cases.csv
   - output/corpus_metrics.json
   - output/evidence_register.csv
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
BASE_CSV = OUTPUT_DIR / "rollbit_cases.csv"
CASES_DB = ROOT / "cases_database.json"
METRICS_JSON = OUTPUT_DIR / "corpus_metrics.json"
EVIDENCE_REGISTER_CSV = OUTPUT_DIR / "evidence_register.csv"

FREEZE_DATE = "2026-04-19"
CAPTURED_AT = "2026-04-19T00:00:00Z"


SOURCE_MAP = {
    "bitcointalk": "bitcointalk",
    "trustpilot": "trustpilot",
    "Casino Guru Complaints": "casino_guru",
    "AskGamblers": "askgamblers",
    "CasinoListings": "casinolistings",
    "Twitter/X": "x",
}

SOURCE_LABELS = {
    "bitcointalk": "Bitcointalk",
    "trustpilot": "Trustpilot",
    "casino_guru": "Casino Guru",
    "askgamblers": "AskGamblers",
    "casinolistings": "CasinoListings",
    "x": "X",
}

CATEGORY_MAP = {
    "maintenance_scam": "maintenance_window_dispute",
    "futures_manipulation": "futures_pricing_dispute",
}


# Explicit cross-posts / non-corpus items we do not want counted twice.
NON_COUNTED_CASE_IDS = {
    "X-001",   # lawsuit / social-media escalation, used as corroboration only
    "AG-002",  # explicitly marked in the repo export as a cross-post from CL-001
}


SUPPLEMENTAL_CASES = [
    {
        "case_id": "BT-016",
        "source": "bitcointalk",
        "source_url": "https://bitcointalk.org/index.php?topic=5543348.0;wap",
        "title": "[SCAM] Rollbit $2700 withheld, false accusations, and AML threats after full KYC",
        "username_forum": "mikitriki",
        "username_rollbit": "",
        "country": "",
        "post_date": "2025-05-14",
        "captured_at": CAPTURED_AT,
        "amount_usd": 2700.0,
        "amount_currency": "USD",
        "amount_native": "$2700",
        "amount_status": "confirmed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.83,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Direct Bitcointalk WAP capture. Complaint includes deposit/withdrawal timeline, "
            "KYC history, screenshots, and cited AML-threat correspondence."
        ),
        "summary": (
            "User says Rollbit processed normal activity until a $2,700 withdrawal request, then "
            "escalated KYC, alleged multiple accounts without evidence, and later threatened AML reporting."
        ),
        "rollbit_response": (
            "According to the complaint, Rollbit asked the user to list other accounts and later "
            "rejected the complaint while citing AML concerns."
        ),
        "evidence": [
            "Bitcointalk complaint thread",
            "Referenced screenshots of KYC status",
            "Referenced withdrawal records",
            "Referenced complaint-team response",
        ],
        "rollbit_staff_involved": ["Razer"],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "BT-017",
        "source": "bitcointalk",
        "source_url": "https://bitcointalk.org/index.php?topic=5539143.0;wap",
        "title": "HELP! Rollbit holding my $30K hostage - won't release funds",
        "username_forum": "ymcmbitcoin",
        "username_rollbit": "",
        "country": "",
        "post_date": "2025-04-21",
        "captured_at": CAPTURED_AT,
        "amount_usd": 30000.0,
        "amount_currency": "USD",
        "amount_native": "$30,000",
        "amount_status": "confirmed",
        "category": "winning_block",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.8,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Direct Bitcointalk WAP capture. Public complaint states full KYC completion, "
            "a winning streak, and a subsequent multi-account accusation tied to the withdrawal request."
        ),
        "summary": (
            "User says a roughly $30,000 winning balance was frozen after full KYC, with Rollbit "
            "refusing to proceed unless the user admitted to other accounts that he says do not exist."
        ),
        "rollbit_response": (
            "According to the complaint, support insisted the user list other accounts before any further review."
        ),
        "evidence": [
            "Bitcointalk complaint thread",
            "Referenced screenshots of balance and withdrawal request",
            "Referenced compliance message",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "CG-004",
        "source": "casino_guru",
        "source_url": "https://casino.guru/complaints/rollbit-casino-player-s-account-has-been-closed",
        "title": "Rollbit Casino - Player’s account has been closed.",
        "username_forum": "bgmbomb",
        "username_rollbit": "",
        "country": "Poland",
        "post_date": "2025-06-19",
        "captured_at": CAPTURED_AT,
        "amount_usd": 3189.0,
        "amount_currency": "USDC",
        "amount_native": "3,189 USDC",
        "amount_status": "confirmed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.79,
        "cross_post_group": "XPOST-BGMBET-3189",
        "alternate_urls": [
            "https://bitcointalk.org/index.php?topic=5547447.0",
        ],
        "notes_on_verification": (
            "Casino Guru complaint page contains public case summary and dates. Alternate Bitcointalk thread "
            "matches the same user/amount pattern and is treated as the same incident."
        ),
        "summary": (
            "Casino Guru summarized a complaint from a Polish player whose 3,189 USDC withdrawal was put on hold, "
            "then the account was disabled and framed as a multiple-account case despite prior verification."
        ),
        "rollbit_response": (
            "Casino Guru said the casino would not engage while the player's internal complaint process was pending, "
            "and the matter was later marked unresolved."
        ),
        "evidence": [
            "Casino Guru public summary",
            "Public player statement",
            "Public Bitcointalk cross-post",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "CG-005",
        "source": "casino_guru",
        "source_url": "https://casino.guru/complaints/rollbit-casino-player-s-withdrawals-are-blocked-by",
        "title": "Rollbit Casino - Player's withdrawals are blocked by casino.",
        "username_forum": "MIR218",
        "username_rollbit": "",
        "country": "Moldova",
        "post_date": "2025-10-01",
        "captured_at": CAPTURED_AT,
        "amount_usd": 1935.0,
        "amount_currency": "USDT",
        "amount_native": "1,935 USDT",
        "amount_status": "confirmed",
        "category": "kyc_delay_tactic",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.77,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Casino Guru public summary shows the amount, dates, and unresolved outcome under its no-reaction policy."
        ),
        "summary": (
            "Moldovan user reported that a fully verified account had withdrawals blocked since July 2025, "
            "leaving 1,935 USDT inaccessible and producing only vague support responses."
        ),
        "rollbit_response": (
            "Casino Guru reported repeated non-cooperation and closed the complaint as unresolved."
        ),
        "evidence": [
            "Casino Guru case summary",
            "Casino Guru no-reaction-policy closure text",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "CG-006",
        "source": "casino_guru",
        "source_url": "https://casino.guru/complaints/rollbit-casino-player-s-withdrawal-is-blocked-for",
        "title": "Rollbit Casino - Player's withdrawal is blocked for several months.",
        "username_forum": "Juggernaut5",
        "username_rollbit": "Juggernaut5",
        "country": "Armenia",
        "post_date": "2026-02-03",
        "captured_at": CAPTURED_AT,
        "amount_usd": 5346.56,
        "amount_currency": "USDT",
        "amount_native": "5,346.56 USDT",
        "amount_status": "confirmed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.84,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Casino Guru page includes the player's public statement, amount, dates, support-language summary, "
            "and the no-reaction-policy closure."
        ),
        "summary": (
            "User reported that withdrawals were fully blocked for more than two months despite Level 4 verification, "
            "with Rollbit demanding disclosure of supposedly linked accounts without evidence."
        ),
        "rollbit_response": (
            "Per the complaint, Legal & Compliance asked the user to declare linked accounts and warned about potential external reporting."
        ),
        "evidence": [
            "Casino Guru public complaint text",
            "Casino Guru case summary",
            "Casino Guru unresolved closure",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "CG-007",
        "source": "casino_guru",
        "source_url": "https://casino.guru/complaints/rollbit-casino-player-s-account-is-closed-with-winnings",
        "title": "Rollbit Casino - Player's account is closed with winnings confiscated.",
        "username_forum": "th3bast1an",
        "username_rollbit": "",
        "country": "Germany / Belarus",
        "post_date": "2026-01-21",
        "captured_at": CAPTURED_AT,
        "amount_usd": 2100.0,
        "amount_currency": "USD",
        "amount_native": "$2,100",
        "amount_status": "confirmed",
        "category": "restricted_country",
        "status": "OPEN",
        "counted_in_totals": True,
        "confidence_score": 0.74,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Casino Guru page is still open. Public summary states the amount, the country/origin-document issue, and the blocked-account outcome."
        ),
        "summary": (
            "Player says a roughly $2,100 balance became inaccessible after identity checks because Rollbit rejected documents tied to a prohibited-country origin."
        ),
        "rollbit_response": (
            "Casino Guru's public summary says the account was blocked after document review and the player remained without access to winnings."
        ),
        "evidence": [
            "Casino Guru public case summary",
            "Public player follow-up inside the thread",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "BT-018",
        "source": "bitcointalk",
        "source_url": "https://bitcointalk.org/index.php?topic=5574081.0",
        "title": "Rollbit withdrawals frozen with $17,700",
        "username_forum": "degen01",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-02-10",
        "captured_at": CAPTURED_AT,
        "amount_usd": 17700.0,
        "amount_currency": "USD",
        "amount_native": "$17,700",
        "amount_status": "confirmed",
        "category": "multiple_accounts_accusation",
        "status": "RESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.82,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Search capture shows the thread title and first-post date; the WAP capture confirms the user narrative and amount. "
            "Later search results show the thread as resolved."
        ),
        "summary": (
            "Long-time user reported that all services and withdrawals were frozen around a $17,700 balance after KYC, "
            "followed by repeated demands to list other accounts."
        ),
        "rollbit_response": (
            "Forum excerpts cite compliance emails asking the user to declare linked or associated accounts."
        ),
        "evidence": [
            "Bitcointalk thread",
            "Bitcointalk WAP capture",
            "Search result reflecting resolved title state",
        ],
        "rollbit_staff_involved": ["Razer"],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "BT-019",
        "source": "bitcointalk",
        "source_url": "https://bitcointalk.org/index.php?topic=5574189.0",
        "title": "[SCAM] Rollbit.com - Account frozen with 3,000 USDT without explanation",
        "username_forum": "HARI54",
        "username_rollbit": "manilas",
        "country": "",
        "post_date": "2026-02-11",
        "captured_at": CAPTURED_AT,
        "amount_usd": 3000.0,
        "amount_currency": "USDT",
        "amount_native": "3,000 USDT",
        "amount_status": "confirmed",
        "category": "account_closure",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.79,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Search capture exposes the complaint title, first-post date, amount, and quoted compliance language."
        ),
        "summary": (
            "User says that a balance that grew from 500 USDT to roughly 3,000 USDT through sports bets was frozen after prior KYC approval."
        ),
        "rollbit_response": (
            "The quoted Legal & Compliance response referenced a generic breach of terms and stated that the matter was closed."
        ),
        "evidence": [
            "Bitcointalk complaint excerpt",
            "Quoted Legal & Compliance message",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "BT-020",
        "source": "bitcointalk",
        "source_url": "https://bitcointalk.org/index.php?topic=5566400.0",
        "title": "ROLLBIT FROZE MY ACCOUNT ACCUSING ME OF MULTIACOUNTING",
        "username_forum": "jofreyking",
        "username_rollbit": "",
        "country": "Czech Republic",
        "post_date": "2025-11-24",
        "captured_at": CAPTURED_AT,
        "amount_usd": 530.0,
        "amount_currency": "USD",
        "amount_native": "$530",
        "amount_status": "confirmed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.73,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Search capture shows the first-post date, detailed complaint text, screenshot references, and the user's stated balance."
        ),
        "summary": (
            "Czech user reported that a normal sportsbook bet triggered KYC Level 3, followed by a rejected verification and a multiple-account accusation."
        ),
        "rollbit_response": (
            "Per the complaint, live support and compliance bounced the user back and forth without allowing a new verification attempt."
        ),
        "evidence": [
            "Bitcointalk complaint excerpt",
            "Referenced screenshots",
        ],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-046",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "These are scammers!",
        "username_forum": "Alex PL",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-04-10",
        "captured_at": CAPTURED_AT,
        "amount_usd": 1700.0,
        "amount_currency": "USD",
        "amount_native": "$1,700",
        "amount_status": "claimed",
        "category": "account_closure",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.5,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19. No stable per-review permalink was available in the public page capture."
        ),
        "summary": "Reviewer said Rollbit froze a $1,700 withdrawal and stopped responding.",
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-047",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "Rollbit’s Greed Cost Me $850 – Froze My Funds After Full KYC",
        "username_forum": "hydra",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-04-12",
        "captured_at": CAPTURED_AT,
        "amount_usd": 850.0,
        "amount_currency": "USD",
        "amount_native": "$850",
        "amount_status": "claimed",
        "category": "kyc_delay_tactic",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.58,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19."
        ),
        "summary": (
            "Reviewer said Rollbit required all KYC levels plus source-of-funds checks and then routed an $850 withdrawal back to a shared exchange deposit address."
        ),
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-048",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "Scamed me for 700 usd",
        "username_forum": "Vojtas CZ",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-04-10",
        "captured_at": CAPTURED_AT,
        "amount_usd": 700.0,
        "amount_currency": "USD",
        "amount_native": "$700",
        "amount_status": "claimed",
        "category": "account_closure",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.45,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19."
        ),
        "summary": "Reviewer alleged that Rollbit refused to release a $700 withdrawal.",
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-049",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "Withdrawal blocked for no reason",
        "username_forum": "Dominik Paldus",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-04-10",
        "captured_at": CAPTURED_AT,
        "amount_usd": 500.0,
        "amount_currency": "USD",
        "amount_native": "$500",
        "amount_status": "claimed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.56,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19."
        ),
        "summary": (
            "Reviewer said a roughly $500 withdrawal was blocked after the account was flagged for linked accounts despite Level 3 KYC."
        ),
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-050",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "Scam bookie that will shamelessly steal your money",
        "username_forum": "efrhen gallego",
        "username_rollbit": "",
        "country": "",
        "post_date": "2026-04-01",
        "captured_at": CAPTURED_AT,
        "amount_usd": 234.0,
        "amount_currency": "USD",
        "amount_native": "$234",
        "amount_status": "claimed",
        "category": "multiple_accounts_accusation",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.5,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19."
        ),
        "summary": (
            "Reviewer said sportsbook privileges were suspended after two months of use and Rollbit then demanded details about other accounts while keeping $234 inaccessible."
        ),
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
    {
        "case_id": "TP-051",
        "source": "trustpilot",
        "source_url": "https://www.trustpilot.com/review/www.rollbit.com",
        "title": "Verified User - $3,386.52 withheld without explanation.",
        "username_forum": "Gilvandes",
        "username_rollbit": "125012",
        "country": "Brazil",
        "post_date": "2026-02-27",
        "captured_at": CAPTURED_AT,
        "amount_usd": 3386.52,
        "amount_currency": "USD",
        "amount_native": "$3,386.52",
        "amount_status": "claimed",
        "category": "account_closure",
        "status": "UNRESOLVED",
        "counted_in_totals": True,
        "confidence_score": 0.57,
        "cross_post_group": "",
        "alternate_urls": [],
        "notes_on_verification": (
            "Captured from Trustpilot's most-recent review list on 2026-04-19."
        ),
        "summary": (
            "Brazil-based reviewer said a verified account was permanently deactivated with $3,386.52 on-platform after legitimate sports bets."
        ),
        "rollbit_response": "",
        "evidence": ["Trustpilot most-recent review capture"],
        "rollbit_staff_involved": [],
        "source_capture_method": "live_public_capture",
    },
]


def clean_text(value: str) -> str:
    return (value or "").strip()


def parse_float(value: str) -> float | None:
    value = clean_text(value)
    if not value:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def normalize_source(raw: str) -> str:
    return SOURCE_MAP.get(raw, raw.strip().lower().replace(" ", "_"))


def infer_amount_status(source: str, amount_usd: float | None) -> str:
    if amount_usd is None:
        return "unquantified"
    if source in {"trustpilot", "x"}:
        return "claimed"
    return "confirmed"


def default_source_url(source: str, raw_url: str) -> str:
    raw_url = clean_text(raw_url)
    if raw_url:
        return raw_url
    if source == "trustpilot":
        return "https://www.trustpilot.com/review/www.rollbit.com"
    if source == "x":
        return "https://x.com/Nonopancake/status/1782506890817105973"
    return ""


def legacy_verification_note(source: str, raw_url: str, case_id: str) -> str:
    if case_id == "AG-002":
        return (
            "Imported from the repository's prior corpus. The source notes explicitly state this entry is a cross-post from CL-001, "
            "so it is retained for provenance but excluded from complaint totals."
        )
    if source == "trustpilot":
        return (
            "Imported from the repository's prior Trustpilot extraction. The historical export preserved reviewer/date/amount fields "
            "but not stable per-review URLs, so the corpus retains the main review page as the public source locator."
        )
    if source == "x":
        return (
            "Imported from the repository's prior social-media evidence set. Treated as corroboration only and excluded from complaint totals."
        )
    if raw_url:
        return "Imported from the repository's prior corpus with a direct public source URL."
    return "Imported from the repository's prior corpus."


def derive_title(case_id: str, details: str, category: str) -> str:
    details = clean_text(details)
    if details:
        sentence = details.split(".")[0].strip()
        if sentence:
            return sentence[:120]
    return f"{case_id} ({category})"


def normalize_category(category: str) -> str:
    category = clean_text(category)
    return CATEGORY_MAP.get(category, category)


def convert_base_row(row: dict[str, str]) -> dict:
    source = normalize_source(row.get("source", ""))
    amount_usd = parse_float(row.get("amount_usd", ""))
    details = clean_text(row.get("details", "")) or clean_text(row.get("summary", ""))
    source_url = default_source_url(source, row.get("url", "") or row.get("source_url", ""))
    post_date = clean_text(row.get("date_posted", "")) or clean_text(row.get("post_date", ""))
    confidence_score = (
        parse_float(row.get("credibility_score", ""))
        or parse_float(row.get("confidence_score", ""))
        or 0.5
    )
    title = clean_text(row.get("title", "")) or derive_title(
        row.get("case_id", ""),
        details,
        normalize_category(row.get("category", "")),
    )
    notes = clean_text(row.get("notes_on_verification", "")) or legacy_verification_note(
        source,
        row.get("url", "") or row.get("source_url", ""),
        row.get("case_id", ""),
    )
    case = {
        "case_id": clean_text(row.get("case_id", "")),
        "source": source,
        "source_url": source_url,
        "title": title,
        "username_forum": clean_text(row.get("username_forum", "")),
        "username_rollbit": clean_text(row.get("username_rollbit", "")),
        "country": clean_text(row.get("country", "")),
        "post_date": post_date,
        "captured_at": clean_text(row.get("captured_at", "")) or CAPTURED_AT,
        "amount_usd": amount_usd,
        "amount_currency": clean_text(row.get("amount_currency", "")) or "USD",
        "amount_native": clean_text(row.get("amount_crypto", "")) or clean_text(row.get("amount_native", "")),
        "amount_status": infer_amount_status(source, amount_usd),
        "category": normalize_category(row.get("category", "")),
        "status": clean_text(row.get("status", "")) or "UNRESOLVED",
        "counted_in_totals": clean_text(row.get("case_id", "")) not in NON_COUNTED_CASE_IDS,
        "confidence_score": confidence_score,
        "cross_post_group": clean_text(row.get("cross_post_group", "")) or (
            "XPOST-CL-001-AG-002" if row.get("case_id") in {"AG-002", "CL-001"} else ""
        ),
        "alternate_urls": [
            url.strip()
            for url in clean_text(row.get("alternate_urls", "")).split("|")
            if url.strip()
        ],
        "notes_on_verification": notes,
        "summary": details,
        "rollbit_response": clean_text(row.get("rollbit_response", "")),
        "evidence": [],
        "rollbit_staff_involved": [],
        "source_capture_method": "repo_archive",
    }
    if row.get("case_id") == "AG-002":
        case["duplicate_of"] = "CL-001"
    return case


def load_base_cases() -> list[dict]:
    with BASE_CSV.open() as f:
        rows = list(csv.DictReader(f))
    return [convert_base_row(row) for row in rows]


def merge_cases(base_cases: list[dict], supplemental_cases: list[dict]) -> list[dict]:
    cases_by_id = {case["case_id"]: deepcopy(case) for case in base_cases}
    for case in supplemental_cases:
        cases_by_id[case["case_id"]] = deepcopy(case)
    cases = list(cases_by_id.values())
    cases.sort(key=lambda case: (case.get("post_date") or "9999-12-31", case["case_id"]))
    return cases


def build_metrics(cases: list[dict]) -> dict:
    counted = [case for case in cases if case.get("counted_in_totals", True)]
    quantified = [case for case in counted if case.get("amount_usd") is not None]
    confirmed = [case for case in quantified if case.get("amount_status") == "confirmed"]
    claimed = [case for case in quantified if case.get("amount_status") == "claimed"]
    resolved = [case for case in counted if case.get("status") == "RESOLVED"]

    source_breakdown = Counter(case["source"] for case in counted)
    category_breakdown = Counter(case["category"] for case in counted if case.get("category"))
    year_breakdown = Counter((case.get("post_date") or "")[:4] for case in counted if case.get("post_date"))

    quantified_total = sum(case["amount_usd"] for case in quantified)
    confirmed_total = sum(case["amount_usd"] for case in confirmed)
    claimed_total = sum(case["amount_usd"] for case in claimed)

    top_cases = sorted(
        [case for case in quantified],
        key=lambda case: case["amount_usd"],
        reverse=True,
    )[:10]

    return {
        "freeze_date": FREEZE_DATE,
        "captured_at": CAPTURED_AT,
        "total_cases": len(counted),
        "quantified_cases": len(quantified),
        "resolved_cases": len(resolved),
        "open_or_unresolved_cases": len(counted) - len(resolved),
        "resolution_rate": round((len(resolved) / len(counted)) if counted else 0.0, 4),
        "quantified_amount_total_usd": round(quantified_total, 2),
        "confirmed_amount_total_usd": round(confirmed_total, 2),
        "claimed_amount_total_usd": round(claimed_total, 2),
        "source_breakdown": dict(source_breakdown),
        "category_breakdown": dict(category_breakdown),
        "year_breakdown": dict(year_breakdown),
        "dedupe_rules_applied": {
            "excluded_from_totals": sorted(NON_COUNTED_CASE_IDS),
            "cross_post_groups": [
                "XPOST-CL-001-AG-002",
                "XPOST-BGMBET-3189",
            ],
        },
        "top_10_cases": [
            {
                "case_id": case["case_id"],
                "amount_usd": case["amount_usd"],
                "source": case["source"],
                "post_date": case.get("post_date", ""),
                "category": case.get("category", ""),
            }
            for case in top_cases
        ],
    }


def build_evidence_register(cases: list[dict], metrics: dict) -> list[dict]:
    cases_by_id = {case["case_id"]: case for case in cases}

    def urls_for(*case_ids: str) -> str:
        urls = []
        for case_id in case_ids:
            case = cases_by_id.get(case_id)
            if not case:
                continue
            if case.get("source_url"):
                urls.append(case["source_url"])
        return " | ".join(dict.fromkeys(urls))

    register = [
        {
            "claim_id": "ER-01",
            "report_section": "Report 2 / Executive summary",
            "claim": f"The complaint corpus contains {metrics['total_cases']} counted public complaints through {FREEZE_DATE}.",
            "case_ids": "CORPUS",
            "source_urls": "",
            "confidence": "high",
            "notes": "Computed from the canonical corpus after exclusions for X corroboration and an explicit cross-post duplicate.",
        },
        {
            "claim_id": "ER-02",
            "report_section": "Report 2 / Executive summary",
            "claim": (
                f"{metrics['quantified_cases']} counted complaints include explicit amounts totaling "
                f"${metrics['quantified_amount_total_usd']:,.2f}."
            ),
            "case_ids": "CORPUS",
            "source_urls": "",
            "confidence": "high",
            "notes": "Computed from quantified cases only.",
        },
        {
            "claim_id": "ER-03",
            "report_section": "Report 2 / Executive summary",
            "claim": (
                f"The quantified corpus splits into ${metrics['confirmed_amount_total_usd']:,.2f} from more fully documented "
                f"forum/mediation cases and ${metrics['claimed_amount_total_usd']:,.2f} from Trustpilot-style claimed amounts."
            ),
            "case_ids": "CORPUS",
            "source_urls": "",
            "confidence": "high",
            "notes": "Amount-status split is based on source-type and preserved provenance.",
        },
        {
            "claim_id": "ER-04",
            "report_section": "Report 2 / Outcomes",
            "claim": f"Only {metrics['resolved_cases']} of {metrics['total_cases']} counted complaints are marked resolved ({metrics['resolution_rate']*100:.1f}%).",
            "case_ids": "BTC-007|BTC-010|BTC-014|BT-018",
            "source_urls": urls_for("BTC-007", "BTC-010", "BTC-014", "BT-018"),
            "confidence": "high",
            "notes": "Resolution rate is computed from the canonical corpus status field.",
        },
        {
            "claim_id": "ER-05",
            "report_section": "Report 2 / Pattern analysis",
            "claim": "Multiple-account accusations recur across Bitcointalk, Casino Guru, and Trustpilot complaints.",
            "case_ids": "BTC-002|BT-016|CG-004|CG-006|TP-049",
            "source_urls": urls_for("BTC-002", "BT-016", "CG-004", "CG-006", "TP-049"),
            "confidence": "high",
            "notes": "Representative cross-source examples.",
        },
        {
            "claim_id": "ER-06",
            "report_section": "Report 2 / Pattern analysis",
            "claim": "Several complaints describe KYC or compliance escalation only after a withdrawal request or winning period.",
            "case_ids": "BTC-005|BT-017|CG-006|BT-018|TP-047",
            "source_urls": urls_for("BTC-005", "BT-017", "CG-006", "BT-018", "TP-047"),
            "confidence": "high",
            "notes": "Representative cases from 2024-2026.",
        },
        {
            "claim_id": "ER-07",
            "report_section": "Report 2 / Source quality",
            "claim": "Casino Guru repeatedly described Rollbit complaints as unresolved under a no-reaction or non-cooperation pattern.",
            "case_ids": "CG-004|CG-005|CG-006",
            "source_urls": urls_for("CG-004", "CG-005", "CG-006"),
            "confidence": "high",
            "notes": "Each cited complaint page includes public closure language from Casino Guru.",
        },
        {
            "claim_id": "ER-08",
            "report_section": "Report 2 / Timeline",
            "claim": "Counted complaints continued into April 2026.",
            "case_ids": "TP-046|TP-047|TP-048|TP-049",
            "source_urls": urls_for("TP-046", "TP-047", "TP-048", "TP-049"),
            "confidence": "medium",
            "notes": "These are Trustpilot-sourced amounts and remain classified as claimed rather than confirmed.",
        },
        {
            "claim_id": "ER-09",
            "report_section": "Report 3 / X corroboration",
            "claim": "Selected X threads mirror the same withdrawal-block, KYC, and staff-conduct themes seen in the complaint corpus but are not counted as separate complaint totals.",
            "case_ids": "X-001",
            "source_urls": (
                "https://x.com/robertgambaskr/status/2029872445662937303 | "
                "https://x.com/robertgambaskr/status/1947015657050009696 | "
                "https://x.com/YtZlashy/status/1731639780713103506"
            ),
            "confidence": "medium",
            "notes": "Used as corroboration only to avoid double counting.",
        },
        {
            "claim_id": "ER-10",
            "report_section": "Report 0 / Synthesis",
            "claim": "The complaint corpus is a recurring operational-dispute dataset even without claiming that public treasury wallets are empty.",
            "case_ids": "ER-01|ER-02|ER-05|ER-06",
            "source_urls": "",
            "confidence": "high",
            "notes": "Synthesis claim built from the corpus and the on-chain report; not a standalone factual datapoint.",
        },
    ]
    return register


def export_cases_json(cases: list[dict], metrics: dict) -> None:
    payload = {
        "metadata": {
            "investigation_title": "Rollbit complaint corpus",
            "freeze_date": FREEZE_DATE,
            "captured_at": CAPTURED_AT,
            "summary_metrics": metrics,
            "source_labels": SOURCE_LABELS,
            "methodology": (
                "Canonical complaint list built from the repository's prior CSV export plus a targeted public-source refresh through 2026-04-19. "
                "Explicitly cross-posted entries are retained for provenance but excluded from totals."
            ),
        },
        "cases": cases,
    }
    with CASES_DB.open("w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def export_cases_csv(cases: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "source",
        "source_url",
        "title",
        "username_forum",
        "username_rollbit",
        "country",
        "post_date",
        "captured_at",
        "amount_usd",
        "amount_currency",
        "amount_native",
        "amount_status",
        "category",
        "status",
        "counted_in_totals",
        "confidence_score",
        "cross_post_group",
        "alternate_urls",
        "notes_on_verification",
        "summary",
        "rollbit_response",
    ]
    with BASE_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for case in cases:
            row = {key: case.get(key, "") for key in fieldnames}
            row["alternate_urls"] = " | ".join(case.get("alternate_urls", []))
            writer.writerow(row)


def export_metrics(metrics: dict) -> None:
    with METRICS_JSON.open("w") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")


def export_evidence_register(register: list[dict]) -> None:
    fieldnames = ["claim_id", "report_section", "claim", "case_ids", "source_urls", "confidence", "notes"]
    with EVIDENCE_REGISTER_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in register:
            writer.writerow(row)


def main() -> None:
    base_cases = load_base_cases()
    merged_cases = merge_cases(base_cases, SUPPLEMENTAL_CASES)
    metrics = build_metrics(merged_cases)
    register = build_evidence_register(merged_cases, metrics)

    export_cases_json(merged_cases, metrics)
    export_cases_csv(merged_cases)
    export_metrics(metrics)
    export_evidence_register(register)

    print(f"Built {metrics['total_cases']} counted cases ({metrics['quantified_cases']} quantified).")
    print(f"Quantified total: ${metrics['quantified_amount_total_usd']:,.2f}")
    print(f"Confirmed total: ${metrics['confirmed_amount_total_usd']:,.2f}")
    print(f"Claimed total:   ${metrics['claimed_amount_total_usd']:,.2f}")


if __name__ == "__main__":
    main()

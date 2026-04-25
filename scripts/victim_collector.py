#!/usr/bin/env python3
"""
Rollbit Case Evidence Collector
===============================
Interactive CLI tool for collecting structured incident evidence.
Validates transaction hashes, generates JSON evidence files,
and optionally appends to the master cases database.

Usage:
    python victim_collector.py --interactive        # Step-by-step guided mode
    python victim_collector.py --batch input.csv    # Batch import from CSV
    python victim_collector.py --validate TX_HASH   # Validate a tx hash
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DATA_DIR = Path(__file__).resolve().parent.parent
CASES_DB = DATA_DIR / 'cases_database.json'
OUTPUT_DIR = DATA_DIR / 'output' / 'victim_evidence'

CATEGORIES = {
    '1': ('multiple_accounts_accusation', 'False multi-account accusation'),
    '2': ('winning_block', 'Account blocked after winning'),
    '3': ('kyc_delay_tactic', 'Endless KYC requirements'),
    '4': ('sportsbook_abuse', 'Accused of sportsbook abuse'),
    '5': ('restricted_country', 'Restricted country enforcement'),
    '6': ('maintenance_scam', 'Maintenance timing manipulation'),
    '7': ('futures_manipulation', 'Futures/leverage manipulation'),
    '8': ('account_closure', 'Account closed, funds seized'),
    '9': ('other', 'Other'),
}


def validate_btc_tx(tx_hash: str) -> dict:
    """Validate a BTC transaction hash via Blockstream."""
    if not re.match(r'^[a-fA-F0-9]{64}$', tx_hash):
        return {'valid': False, 'error': 'Invalid format (expected 64 hex chars)'}
    if not HAS_REQUESTS:
        return {'valid': None, 'note': 'Cannot verify (requests not installed)'}
    try:
        r = requests.get(f'https://blockstream.info/api/tx/{tx_hash}', timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                'valid': True, 'chain': 'BTC', 'txid': tx_hash,
                'block_height': data.get('status', {}).get('block_height'),
                'confirmed': data.get('status', {}).get('confirmed', False),
            }
        return {'valid': False, 'error': f'Not found (HTTP {r.status_code})'}
    except Exception as e:
        return {'valid': None, 'error': str(e)}


def validate_eth_tx(tx_hash: str) -> dict:
    """Validate an ETH transaction hash via Etherscan."""
    if not re.match(r'^0x[a-fA-F0-9]{64}$', tx_hash):
        return {'valid': False, 'error': 'Invalid format (expected 0x + 64 hex chars)'}
    if not HAS_REQUESTS:
        return {'valid': None, 'note': 'Cannot verify (requests not installed)'}
    try:
        r = requests.get('https://api.etherscan.io/api', params={
            'module': 'proxy', 'action': 'eth_getTransactionByHash', 'txhash': tx_hash
        }, timeout=10)
        data = r.json()
        if data.get('result') and data['result'].get('hash'):
            return {'valid': True, 'chain': 'ETH', 'txid': tx_hash,
                    'block': data['result'].get('blockNumber')}
        return {'valid': False, 'error': 'Not found'}
    except Exception as e:
        return {'valid': None, 'error': str(e)}


def validate_sol_tx(tx_hash: str) -> dict:
    """Validate a Solana transaction signature."""
    if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{87,88}$', tx_hash):
        return {'valid': False, 'error': 'Invalid Solana signature format'}
    if not HAS_REQUESTS:
        return {'valid': None, 'note': 'Cannot verify'}
    try:
        r = requests.post('https://api.mainnet-beta.solana.com', json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getTransaction",
            "params": [tx_hash, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
        }, timeout=10)
        data = r.json()
        if data.get('result'):
            return {'valid': True, 'chain': 'SOL', 'txid': tx_hash,
                    'slot': data['result'].get('slot')}
        return {'valid': False, 'error': 'Not found'}
    except Exception as e:
        return {'valid': None, 'error': str(e)}


def validate_tx_hash(tx_hash: str) -> dict:
    """Auto-detect chain and validate."""
    tx_hash = tx_hash.strip()
    if tx_hash.startswith('0x'):
        return validate_eth_tx(tx_hash)
    elif len(tx_hash) == 64 and re.match(r'^[a-fA-F0-9]+$', tx_hash):
        return validate_btc_tx(tx_hash)
    else:
        return validate_sol_tx(tx_hash)


def interactive_collect():
    """Guided step-by-step evidence collection."""
    print(f"\n{'='*60}")
    print(f"  ROLLBIT CASE EVIDENCE COLLECTOR")
    print(f"{'='*60}")
    print(f"  All data is stored locally.\n")

    evidence = {
        'case_id': f'VIC-{uuid4().hex[:8].upper()}',
        'collected_at': datetime.now(timezone.utc).isoformat(),
        'source': 'victim_submission',
    }

    # Basic info
    print("  --- Basic Information ---")
    evidence['username_rollbit'] = input("  Your Rollbit username: ").strip()
    evidence['contact'] = input("  Contact handle/email (optional, for follow-up): ").strip() or None
    evidence['country'] = input("  Your country: ").strip() or None

    # Amount
    while True:
        amt = input("  Amount disputed or inaccessible (USD): $").strip().replace(',', '')
        try:
            evidence['amount_usd'] = float(amt)
            break
        except ValueError:
            print("    Please enter a numeric value")

    evidence['currency_deposited'] = input("  Currency deposited (BTC/ETH/SOL/USDT/other): ").strip().upper()

    # Timeline
    print("\n  --- Timeline ---")
    evidence['date_account_created'] = input("  When did you create your Rollbit account? (YYYY-MM): ").strip()
    evidence['date_issue_started'] = input("  When did the issue start? (YYYY-MM-DD): ").strip()
    evidence['date_last_contact'] = input("  Last contact with support? (YYYY-MM-DD): ").strip()

    # Category
    print("\n  --- Issue Category ---")
    for key, (_, desc) in CATEGORIES.items():
        print(f"    [{key}] {desc}")
    cat_choice = input("  Select category number: ").strip()
    if cat_choice in CATEGORIES:
        evidence['category'] = CATEGORIES[cat_choice][0]
    else:
        evidence['category'] = 'other'

    # Description
    print("\n  --- Description ---")
    print("  Describe what happened (press Enter twice to finish):")
    lines = []
    while True:
        line = input("  > ")
        if not line and lines and not lines[-1]:
            break
        lines.append(line)
    evidence['description'] = '\n'.join(lines).strip()

    # Transaction hashes
    print("\n  --- Transaction Evidence ---")
    tx_hashes = []
    while True:
        tx = input("  Transaction hash (or 'done'): ").strip()
        if tx.lower() in ('done', 'd', ''):
            break
        result = validate_tx_hash(tx)
        if result.get('valid') is True:
            print(f"    ✅ Valid {result['chain']} transaction confirmed")
            tx_hashes.append({'hash': tx, 'validation': result})
        elif result.get('valid') is False:
            print(f"    ❌ {result.get('error', 'Invalid')}")
            if input("    Add anyway? (y/n): ").lower() == 'y':
                tx_hashes.append({'hash': tx, 'validation': result})
        else:
            print(f"    ⚠️  Could not verify: {result.get('error', result.get('note'))}")
            tx_hashes.append({'hash': tx, 'validation': result})
    evidence['transaction_hashes'] = tx_hashes

    # Rollbit staff
    print("\n  --- Rollbit Staff Involved ---")
    staff = input("  Staff names (comma-separated, e.g. Razer, SmokeyLisa): ").strip()
    evidence['rollbit_staff_involved'] = [s.strip() for s in staff.split(',') if s.strip()]

    # Screenshots/files
    print("\n  --- Screenshots / File Evidence ---")
    files = []
    while True:
        f = input("  File path (or 'done'): ").strip()
        if f.lower() in ('done', 'd', ''):
            break
        if os.path.exists(f):
            files.append(f)
            print(f"    ✅ File exists: {os.path.basename(f)}")
        else:
            print(f"    ❌ File not found: {f}")
    evidence['evidence_files'] = files

    # Resolution attempts
    evidence['has_filed_complaint'] = input("\n  Filed complaint elsewhere? (y/n): ").lower() == 'y'
    if evidence['has_filed_complaint']:
        evidence['complaint_platforms'] = input("  Where? (comma-separated): ").strip()

    evidence['willing_followup'] = input("  Willing to answer follow-up evidence questions? (y/n): ").lower() == 'y'

    # Summary
    print(f"\n{'='*60}")
    print(f"  EVIDENCE SUMMARY")
    print(f"{'='*60}")
    print(f"  Case ID: {evidence['case_id']}")
    print(f"  Amount: ${evidence['amount_usd']:,.2f}")
    print(f"  Category: {evidence['category']}")
    print(f"  Tx hashes: {len(evidence['transaction_hashes'])}")
    print(f"  Staff involved: {', '.join(evidence['rollbit_staff_involved']) or 'None'}")
    print(f"  Evidence files: {len(evidence['evidence_files'])}")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{evidence['case_id']}_{datetime.now().strftime('%Y%m%d')}.json"
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"\n  ✅ Evidence saved to: {filepath}")

    # Offer to append to main database
    if input("\n  Add to main cases database? (y/n): ").lower() == 'y':
        append_to_database(evidence)

    return evidence


def append_to_database(evidence: dict):
    """Append a victim submission to the main cases database."""
    if not CASES_DB.exists():
        print("  [WARN] cases_database.json not found")
        return

    with open(CASES_DB) as f:
        db = json.load(f)

    # Add to a new 'victim_submissions' section
    if 'victim_submissions' not in db:
        db['victim_submissions'] = []

    db['victim_submissions'].append({
        'case_id': evidence['case_id'],
        'date_submitted': evidence['collected_at'],
        'amount_usd': evidence['amount_usd'],
        'category': evidence['category'],
        'description': evidence['description'][:500],
        'status': 'UNRESOLVED',
        'tx_count': len(evidence.get('transaction_hashes', [])),
    })

    with open(CASES_DB, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"  ✅ Added to {CASES_DB}")


def batch_import(filepath: str):
    """Import cases from CSV. Expected columns: username, amount_usd, category, description"""
    print(f"\n  Importing from: {filepath}")
    if filepath == '-':
        # Read from stdin (for piping JSON)
        data = json.loads(sys.stdin.read())
        evidence = {
            'case_id': f'VIC-{uuid4().hex[:8].upper()}',
            'collected_at': datetime.now(timezone.utc).isoformat(),
            'source': 'batch_import',
            **data,
        }
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        fp = OUTPUT_DIR / f"{evidence['case_id']}.json"
        with open(fp, 'w') as f:
            json.dump(evidence, f, indent=2)
        print(f"  ✅ Saved: {fp}")
        return

    if not os.path.exists(filepath):
        print(f"  [ERROR] File not found: {filepath}")
        return

    count = 0
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence = {
                'case_id': f'VIC-{uuid4().hex[:8].upper()}',
                'collected_at': datetime.now(timezone.utc).isoformat(),
                'source': 'batch_csv',
                'username_rollbit': row.get('username', ''),
                'amount_usd': float(row.get('amount_usd', 0)),
                'category': row.get('category', 'other'),
                'description': row.get('description', ''),
            }
            fp = OUTPUT_DIR / f"{evidence['case_id']}.json"
            with open(fp, 'w') as out:
                json.dump(evidence, out, indent=2)
            count += 1
    print(f"  ✅ Imported {count} cases to {OUTPUT_DIR}")


def main():
    parser = argparse.ArgumentParser(description='Rollbit Victim Evidence Collector')
    parser.add_argument('--interactive', action='store_true', help='Interactive guided mode')
    parser.add_argument('--batch', type=str, help='Batch import from CSV file (or - for stdin)')
    parser.add_argument('--validate', type=str, help='Validate a transaction hash')
    args = parser.parse_args()

    if args.validate:
        print(f"\n  Validating: {args.validate}")
        result = validate_tx_hash(args.validate)
        print(f"  Result: {json.dumps(result, indent=2)}")
    elif args.batch:
        batch_import(args.batch)
    elif args.interactive:
        interactive_collect()
    else:
        parser.print_help()
        print("\n  Try: python victim_collector.py --interactive")


if __name__ == '__main__':
    main()

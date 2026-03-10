#!/usr/bin/env python3
"""
Rollbit Treasury Real-Time Monitor
====================================
Polls known Rollbit wallet addresses at configurable intervals and
alerts when large outflows are detected.

Usage:
    python treasury_monitor.py --dry-run
    python treasury_monitor.py --threshold 50000
    python treasury_monitor.py --interval 60 --duration 600
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DATA_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = DATA_DIR / 'output'
LOG_FILE = OUTPUT_DIR / 'treasury_log.json'

MONITORED_WALLETS = [
    {'chain': 'BTC', 'address': 'bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu',
     'label': 'Rollbit BTC Treasury', 'parse': 'blockstream'},
    {'chain': 'SOL', 'address': 'RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx',
     'label': 'Rollbit SOL Treasury', 'parse': 'solana_rpc'},
    {'chain': 'ETH', 'address': '0xCBD6832Ebc203e49E2B771897067fce3c58575ac',
     'label': 'Rollbit ETH Hot Wallet', 'parse': 'etherscan'},
    {'chain': 'ETH', 'address': '0x46dcA395D20E63Cb0Fe1EDC9f0e6f012E77c0913',
     'label': 'rollbit.eth', 'parse': 'etherscan'},
]

RED = '\033[91m'; YELLOW = '\033[93m'; GREEN = '\033[92m'
CYAN = '\033[96m'; BOLD = '\033[1m'; DIM = '\033[2m'; RESET = '\033[0m'


@dataclass
class BalanceSnapshot:
    timestamp: str
    chain: str
    address: str
    label: str
    balance_native: float
    balance_usd: float
    previous_balance_native: float = 0.0
    delta_native: float = 0.0
    delta_usd: float = 0.0


class TreasuryMonitor:
    def __init__(self, threshold_usd=50000, interval=120, duration=0,
                 dry_run=False, etherscan_key=''):
        self.threshold_usd = threshold_usd
        self.interval = interval
        self.duration = duration
        self.dry_run = dry_run
        self.etherscan_key = etherscan_key or os.environ.get('ETHERSCAN_API_KEY', '')
        self.session = requests.Session() if HAS_REQUESTS else None
        if self.session:
            self.session.headers['User-Agent'] = 'RollbitForensic/2.0'
        self.previous_balances = {}
        self.snapshots = []
        self.alerts = []
        self.running = True
        self.start_time = None
        self.cycle_count = 0
        self.prices = {}
        signal.signal(signal.SIGINT, lambda s, f: setattr(self, 'running', False))

    def _fetch_prices(self):
        if self.dry_run or not self.session:
            return {'BTC': 97000, 'ETH': 3500, 'SOL': 145}
        try:
            resp = self.session.get(
                'https://api.coingecko.com/api/v3/simple/price',
                params={'ids': 'bitcoin,ethereum,solana', 'vs_currencies': 'usd'},
                timeout=15)
            d = resp.json()
            return {'BTC': d.get('bitcoin',{}).get('usd',97000),
                    'ETH': d.get('ethereum',{}).get('usd',3500),
                    'SOL': d.get('solana',{}).get('usd',145)}
        except Exception:
            return self.prices or {'BTC': 97000, 'ETH': 3500, 'SOL': 145}

    def _fetch_balance(self, wallet):
        if self.dry_run:
            return self._simulate_balance(wallet)
        if not self.session:
            return 0.0
        try:
            if wallet['parse'] == 'blockstream':
                r = self.session.get(
                    f"https://blockstream.info/api/address/{wallet['address']}", timeout=15)
                s = r.json().get('chain_stats', {})
                return (s.get('funded_txo_sum', 0) - s.get('spent_txo_sum', 0)) / 1e8
            elif wallet['parse'] == 'solana_rpc':
                r = self.session.post('https://api.mainnet-beta.solana.com',
                    json={"jsonrpc":"2.0","id":1,"method":"getBalance",
                          "params":[wallet['address']]}, timeout=15)
                return r.json().get('result',{}).get('value',0) / 1e9
            elif wallet['parse'] == 'etherscan':
                p = {'module':'account','action':'balance',
                     'address':wallet['address'],'tag':'latest'}
                if self.etherscan_key:
                    p['apikey'] = self.etherscan_key
                r = self.session.get('https://api.etherscan.io/api', params=p, timeout=15)
                d = r.json()
                return int(d['result']) / 1e18 if d.get('status') == '1' else 0.0
        except Exception as e:
            print(f"  {DIM}[API ERROR] {wallet['label']}: {e}{RESET}")
            return self.previous_balances.get(wallet['address'], 0.0)
        return 0.0

    def _simulate_balance(self, wallet):
        import random
        prev = self.previous_balances.get(wallet['address'])
        if prev is None:
            base = {'BTC': 150.0, 'SOL': 25000.0, 'ETH': 500.0}
            return base.get(wallet['chain'], 100) + random.uniform(-5, 5)
        change = random.choice([0, 0, 0, -0.01, -0.02, -0.05, 0.005])
        return prev * (1 + change)

    def _check_alert(self, snap):
        if abs(snap.delta_usd) >= self.threshold_usd:
            direction = "OUTFLOW 🔴" if snap.delta_usd < 0 else "INFLOW 🟢"
            self.alerts.append({
                'timestamp': snap.timestamp, 'chain': snap.chain,
                'label': snap.label, 'direction': direction,
                'delta_native': snap.delta_native, 'delta_usd': snap.delta_usd,
            })
            print(f"\n  {RED}{BOLD}{'!' * 50}")
            print(f"  🚨 ALERT: {direction}")
            print(f"  {snap.label}: {snap.delta_native:+,.6f} {snap.chain} (${snap.delta_usd:+,.2f})")
            print(f"  {'!' * 50}{RESET}\n")

    def poll_once(self):
        self.cycle_count += 1
        now = datetime.now(timezone.utc)
        if self.cycle_count % 5 == 1 or not self.prices:
            self.prices = self._fetch_prices()
        print(f"\n  {CYAN}[Cycle {self.cycle_count}] {now.strftime('%Y-%m-%d %H:%M:%S UTC')}{RESET}")
        for wallet in MONITORED_WALLETS:
            bal = self._fetch_balance(wallet)
            price = self.prices.get(wallet['chain'], 0)
            prev = self.previous_balances.get(wallet['address'], bal)
            delta = bal - prev
            snap = BalanceSnapshot(
                timestamp=now.isoformat(), chain=wallet['chain'],
                address=wallet['address'], label=wallet['label'],
                balance_native=bal, balance_usd=bal * price,
                previous_balance_native=prev, delta_native=delta,
                delta_usd=delta * price)
            self.snapshots.append(snap)
            dc = RED if delta < -0.0001 else GREEN if delta > 0.0001 else DIM
            ds = f"{dc}{delta:+,.6f} {wallet['chain']} (${delta*price:+,.2f}){RESET}" if abs(delta) > 0.0001 else f"{DIM}(no change){RESET}"
            print(f"    {wallet['label']}: {bal:,.6f} {wallet['chain']} (${bal*price:,.2f}) {ds}")
            self.previous_balances[wallet['address']] = bal
            self._check_alert(snap)
            time.sleep(0.3)

    def run(self):
        self.start_time = time.time()
        print(f"\n{BOLD}{'='*60}")
        print(f"  ROLLBIT TREASURY MONITOR")
        print(f"{'='*60}{RESET}")
        print(f"  Threshold: ${self.threshold_usd:,.0f} | Interval: {self.interval}s | Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"  Monitoring {len(MONITORED_WALLETS)} wallets. Ctrl+C to stop.\n")
        while self.running:
            self.poll_once()
            if self.duration > 0 and time.time() - self.start_time >= self.duration:
                print(f"\n  {YELLOW}Duration limit reached.{RESET}"); break
            if self.running:
                for _ in range(self.interval):
                    if not self.running: break
                    time.sleep(1)
        self._print_summary()
        self._save_log()

    def _print_summary(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n{BOLD}{'='*60}\n  SESSION SUMMARY\n{'='*60}{RESET}")
        print(f"  Duration: {elapsed:.0f}s | Cycles: {self.cycle_count} | Alerts: {len(self.alerts)}")
        for a in self.alerts:
            print(f"    [{a['timestamp'][:19]}] {a['direction']} ${a['delta_usd']:+,.2f} on {a['label']}")

    def _save_log(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        log = {'session_start': datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat() if self.start_time else '',
               'session_end': datetime.now(timezone.utc).isoformat(),
               'cycles': self.cycle_count, 'alerts': self.alerts,
               'snapshots': [asdict(s) for s in self.snapshots]}
        existing = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE) as f:
                    existing = json.load(f)
                    if not isinstance(existing, list): existing = [existing]
            except Exception: existing = []
        existing.append(log)
        with open(LOG_FILE, 'w') as f:
            json.dump(existing, f, indent=2, default=str)
        print(f"\n  Log saved to: {LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(description='Rollbit Treasury Monitor')
    parser.add_argument('--threshold', type=float, default=50000)
    parser.add_argument('--interval', type=int, default=120)
    parser.add_argument('--duration', type=int, default=0)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--etherscan-key', default='')
    args = parser.parse_args()
    if not HAS_REQUESTS and not args.dry_run:
        print("[ERROR] pip install requests  OR  use --dry-run"); sys.exit(1)
    TreasuryMonitor(args.threshold, args.interval, args.duration,
                    args.dry_run, args.etherscan_key).run()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Rollbit On-Chain Blockchain Forensics Analyzer
===============================================
Queries public blockchain APIs to analyze Rollbit's known wallet addresses,
trace treasury outflows, analyze RLB token manipulation, cluster related wallets,
and score exit-scam risk indicators.

Usage:
    python blockchain_analyzer.py --full              # Full analysis
    python blockchain_analyzer.py --wallet SOL        # Analyze specific chain
    python blockchain_analyzer.py --trace             # Trace large outflows
    python blockchain_analyzer.py --rlb               # RLB token analysis
    python blockchain_analyzer.py --cached            # Use cached/hardcoded data

Free APIs used (no key required for basic use):
    - Solana: public RPC + Solscan
    - Ethereum: Etherscan (free tier, optional API key)
    - Bitcoin: Blockstream.info
    - Token data: DEXScreener, CoinGecko
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# Optional imports with graceful degradation
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[WARN] 'requests' not installed. Install with: pip install requests")
    print("       Running in cached-only mode.\n")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = DATA_DIR / 'output'
CACHE_DIR = OUTPUT_DIR / 'cache'

# Known Rollbit wallet addresses (from Dune Analytics, Etherscan, public research)
ROLLBIT_WALLETS = {
    'BTC': {
        'treasury': {
            'address': 'bc1qw8wrek2m7nlqldll66ajnwr9mh64syvkt67zlu',
            'label': 'Rollbit BTC Treasury',
        },
    },
    'SOL': {
        'treasury': {
            'address': 'RBHdGVfDfMjfU6iUfCb1LczMJcQLx7hGnxbzRsoDNvx',
            'label': 'Rollbit SOL Treasury',
        },
    },
    'ETH': {
        'hot_wallet': {
            'address': '0xCBD6832Ebc203e49E2B771897067fce3c58575ac',
            'label': 'Rollbit Hot Wallet',
        },
        'erc20_ops': {
            'address': '0xef8801eaf234ff82801821ffe2d78d60a0237f97',
            'label': 'Rollbit ERC20 Operations',
        },
        'rollbit_ens': {
            'address': '0x46dcA395D20E63Cb0Fe1EDC9f0e6f012E77c0913',
            'label': 'rollbit.eth',
        },
        'rollbot_ens': {
            'address': '0x8aE57A027c63fcA8070D1Bf38622321dE8004c67',
            'label': 'rollbot.eth',
        },
    },
}

# Known treasury events (from public news reports)
KNOWN_TREASURY_EVENTS = [
    {
        'date': '2025-09-03',
        'chain': 'SOL',
        'event': '50K SOL sold from treasury-linked wallet after 2-year dormancy',
        'amount_native': 50000,
        'amount_usd': 10_170_000,
        'price_at_time': 203.4,
        'initial_price': 24.6,
        'source': 'ChainCatcher / Lookonchain',
        'direction': 'outflow',
    },
    {
        'date': '2026-01-09',
        'chain': 'BTC',
        'event': '497.11 BTC transferred from anonymous address to Rollbit',
        'amount_native': 497.11,
        'amount_usd': 45_190_000,
        'price_at_time': 90_906,
        'source': 'ChainCatcher / Arkham',
        'direction': 'inflow',
    },
    {
        'date': '2026-01-11',
        'chain': 'SOL',
        'event': '15K SOL transferred (batch 1)',
        'amount_native': 15000,
        'amount_usd': 2_050_000,
        'price_at_time': 136.67,
        'source': 'ChainCatcher',
        'direction': 'outflow',
    },
    {
        'date': '2026-01-11',
        'chain': 'SOL',
        'event': '15K SOL transferred (batch 2)',
        'amount_native': 15000,
        'amount_usd': 2_040_000,
        'price_at_time': 136.0,
        'source': 'ChainCatcher',
        'direction': 'outflow',
    },
    {
        'date': '2026-01-15',
        'chain': 'SOL',
        'event': '21.4K SOL transferred',
        'amount_native': 21400,
        'amount_usd': 3_140_000,
        'price_at_time': 146.73,
        'source': 'ChainCatcher',
        'direction': 'outflow',
    },
    {
        'date': '2026-02-13',
        'chain': 'BTC',
        'event': '626.03 BTC transferred from anonymous address; some flow reported into Bybit and Rollbit',
        'amount_native': 626.03,
        'amount_usd': 42_210_000,
        'price_at_time': 67_427,
        'source': 'ChainCatcher / Arkham',
        'direction': 'mixed',
    },
    {
        'date': '2026-03-11',
        'chain': 'BTC',
        'event': '200 BTC transferred from Coinbase; some flow reported into Rollbit',
        'amount_native': 200.0,
        'amount_usd': 13_910_000,
        'price_at_time': 69_550,
        'source': 'ChainCatcher / Arkham',
        'direction': 'mixed',
    },
    {
        'date': '2025-05-09',
        'chain': 'MULTI',
        'event': '$123M seized by Ukrainian authorities from Binance accounts linked to Bull Gaming N.V.',
        'amount_native': None,
        'amount_usd': 123_000_000,
        'price_at_time': None,
        'source': 'dev.ua, Pechersk District Court of Kyiv',
        'direction': 'seizure',
    },
]

# RLB Token data
RLB_TOKEN = {
    'contract_eth': '0x046EeE2cc3188071C02BfC1745A6b17c656e3f3d',  # RLB on Ethereum
    'initial_supply': 5_000_000_000,
    'migration_date': '2024-04-30',  # SOL -> ETH migration deadline
    'dexscreener_pair': 'ethereum/0x...',  # placeholder
}

# API endpoints
API_ENDPOINTS = {
    'blockstream_btc': 'https://blockstream.info/api',
    'solana_rpc': 'https://api.mainnet-beta.solana.com',
    'etherscan': 'https://api.etherscan.io/api',
    'coingecko': 'https://api.coingecko.com/api/v3',
    'dexscreener': 'https://api.dexscreener.com/latest/dex',
    'solscan': 'https://public-api.solscan.io',
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class WalletBalance:
    chain: str
    address: str
    label: str
    balance_native: float = 0.0
    balance_usd: float = 0.0
    tx_count: int = 0
    last_activity: str = ''
    fetched_at: str = ''

@dataclass
class TransactionRecord:
    chain: str
    tx_hash: str
    timestamp: str
    from_address: str
    to_address: str
    amount_native: float
    amount_usd: float = 0.0
    direction: str = ''  # 'in' or 'out' relative to Rollbit wallet
    label: str = ''

@dataclass
class RiskIndicator:
    name: str
    score: float  # 0-10
    description: str
    evidence: list = field(default_factory=list)

@dataclass
class AnalysisResult:
    timestamp: str
    wallets: list = field(default_factory=list)
    transactions: list = field(default_factory=list)
    treasury_events: list = field(default_factory=list)
    risk_indicators: list = field(default_factory=list)
    rlb_analysis: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


# =============================================================================
# API CLIENTS
# =============================================================================

class BlockchainAPI:
    """Unified API client for multiple blockchains with rate limiting."""

    def __init__(self, etherscan_key: str = '', rate_limit: float = 0.25):
        self.etherscan_key = etherscan_key or os.environ.get('ETHERSCAN_API_KEY', '')
        self.rate_limit = rate_limit
        self._last_request = 0
        self.session = requests.Session() if HAS_REQUESTS else None
        if self.session:
            self.session.headers.update({
                'User-Agent': 'RollbitForensic/2.0 (research)'
            })

    def _throttle(self):
        """Rate limit API calls."""
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()

    def _get(self, url: str, params: dict = None, timeout: int = 30) -> dict:
        """Make a rate-limited GET request."""
        if not self.session:
            raise RuntimeError("requests library not available")
        self._throttle()
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"  [API ERROR] {url}: {e}")
            return {}

    # --- Bitcoin (Blockstream) ---

    def btc_get_address_info(self, address: str) -> dict:
        """Get BTC address balance and stats."""
        url = f"{API_ENDPOINTS['blockstream_btc']}/address/{address}"
        data = self._get(url)
        if not data:
            return {}

        stats = data.get('chain_stats', {})
        mempool = data.get('mempool_stats', {})
        funded = stats.get('funded_txo_sum', 0)
        spent = stats.get('spent_txo_sum', 0)
        balance_sat = funded - spent

        return {
            'address': address,
            'balance_btc': balance_sat / 1e8,
            'total_received_btc': funded / 1e8,
            'total_sent_btc': spent / 1e8,
            'tx_count': stats.get('tx_count', 0),
            'funded_txo_count': stats.get('funded_txo_count', 0),
            'spent_txo_count': stats.get('spent_txo_count', 0),
            'mempool_tx_count': mempool.get('tx_count', 0),
        }

    def btc_get_transactions(self, address: str, limit: int = 25) -> list:
        """Get recent BTC transactions for an address."""
        url = f"{API_ENDPOINTS['blockstream_btc']}/address/{address}/txs"
        data = self._get(url)
        if not data or not isinstance(data, list):
            return []

        transactions = []
        for tx in data[:limit]:
            # Determine if this is inflow or outflow relative to address
            is_sender = any(
                vin.get('prevout', {}).get('scriptpubkey_address') == address
                for vin in tx.get('vin', [])
            )
            is_receiver = any(
                vout.get('scriptpubkey_address') == address
                for vout in tx.get('vout', [])
            )

            # Calculate amount
            total_out = sum(
                vout.get('value', 0) for vout in tx.get('vout', [])
                if vout.get('scriptpubkey_address') != address
            ) if is_sender else sum(
                vout.get('value', 0) for vout in tx.get('vout', [])
                if vout.get('scriptpubkey_address') == address
            )

            block_time = tx.get('status', {}).get('block_time', 0)
            ts = datetime.fromtimestamp(block_time, tz=timezone.utc).isoformat() if block_time else ''

            transactions.append({
                'txid': tx.get('txid', ''),
                'timestamp': ts,
                'direction': 'out' if is_sender else 'in',
                'amount_btc': total_out / 1e8,
                'confirmations': tx.get('status', {}).get('confirmed', False),
                'block_height': tx.get('status', {}).get('block_height', 0),
            })

        return transactions

    # --- Solana (public RPC + Solscan) ---

    def sol_get_balance(self, address: str) -> dict:
        """Get SOL balance via RPC."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        self._throttle()
        try:
            resp = self.session.post(
                API_ENDPOINTS['solana_rpc'],
                json=payload,
                timeout=30
            )
            data = resp.json()
            balance_lamports = data.get('result', {}).get('value', 0)
            return {
                'address': address,
                'balance_sol': balance_lamports / 1e9,
                'balance_lamports': balance_lamports,
            }
        except Exception as e:
            print(f"  [API ERROR] Solana RPC: {e}")
            return {'address': address, 'balance_sol': 0}

    def sol_get_signatures(self, address: str, limit: int = 20) -> list:
        """Get recent transaction signatures for a Solana address."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                address,
                {"limit": limit}
            ]
        }
        self._throttle()
        try:
            resp = self.session.post(
                API_ENDPOINTS['solana_rpc'],
                json=payload,
                timeout=30
            )
            data = resp.json()
            sigs = data.get('result', [])
            return [
                {
                    'signature': s.get('signature', ''),
                    'slot': s.get('slot', 0),
                    'block_time': s.get('blockTime', 0),
                    'timestamp': datetime.fromtimestamp(
                        s.get('blockTime', 0), tz=timezone.utc
                    ).isoformat() if s.get('blockTime') else '',
                    'err': s.get('err'),
                    'memo': s.get('memo', ''),
                }
                for s in sigs
            ]
        except Exception as e:
            print(f"  [API ERROR] Solana signatures: {e}")
            return []

    # --- Ethereum (Etherscan) ---

    def eth_get_balance(self, address: str) -> dict:
        """Get ETH balance via Etherscan."""
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
        }
        if self.etherscan_key:
            params['apikey'] = self.etherscan_key

        data = self._get(API_ENDPOINTS['etherscan'], params=params)
        balance_wei = int(data.get('result', 0)) if data.get('status') == '1' else 0
        return {
            'address': address,
            'balance_eth': balance_wei / 1e18,
            'balance_wei': balance_wei,
        }

    def eth_get_transactions(self, address: str, limit: int = 50) -> list:
        """Get ETH transactions via Etherscan."""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': limit,
            'sort': 'desc',
        }
        if self.etherscan_key:
            params['apikey'] = self.etherscan_key

        data = self._get(API_ENDPOINTS['etherscan'], params=params)
        txs = data.get('result', [])
        if not isinstance(txs, list):
            return []

        transactions = []
        for tx in txs:
            value_wei = int(tx.get('value', 0))
            is_outgoing = tx.get('from', '').lower() == address.lower()
            ts = int(tx.get('timeStamp', 0))

            transactions.append({
                'hash': tx.get('hash', ''),
                'timestamp': datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else '',
                'from': tx.get('from', ''),
                'to': tx.get('to', ''),
                'amount_eth': value_wei / 1e18,
                'direction': 'out' if is_outgoing else 'in',
                'gas_used': int(tx.get('gasUsed', 0)),
                'is_error': tx.get('isError', '0') != '0',
                'block_number': int(tx.get('blockNumber', 0)),
            })

        return transactions

    def eth_get_token_transfers(self, address: str, limit: int = 100) -> list:
        """Get ERC20 token transfers for an address."""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': limit,
            'sort': 'desc',
        }
        if self.etherscan_key:
            params['apikey'] = self.etherscan_key

        data = self._get(API_ENDPOINTS['etherscan'], params=params)
        txs = data.get('result', [])
        if not isinstance(txs, list):
            return []

        transfers = []
        for tx in txs:
            decimals = int(tx.get('tokenDecimal', 18))
            value = int(tx.get('value', 0)) / (10 ** decimals)
            is_outgoing = tx.get('from', '').lower() == address.lower()
            ts = int(tx.get('timeStamp', 0))

            transfers.append({
                'hash': tx.get('hash', ''),
                'timestamp': datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else '',
                'from': tx.get('from', ''),
                'to': tx.get('to', ''),
                'token_name': tx.get('tokenName', ''),
                'token_symbol': tx.get('tokenSymbol', ''),
                'amount': value,
                'direction': 'out' if is_outgoing else 'in',
            })

        return transfers

    # --- Price Data ---

    def get_current_prices(self) -> dict:
        """Get current prices for BTC, ETH, SOL from CoinGecko."""
        url = f"{API_ENDPOINTS['coingecko']}/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,solana,rollbit-coin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
        }
        data = self._get(url, params=params)
        return {
            'BTC': data.get('bitcoin', {}).get('usd', 0),
            'ETH': data.get('ethereum', {}).get('usd', 0),
            'SOL': data.get('solana', {}).get('usd', 0),
            'RLB': data.get('rollbit-coin', {}).get('usd', 0),
            'BTC_24h_change': data.get('bitcoin', {}).get('usd_24h_change', 0),
            'ETH_24h_change': data.get('ethereum', {}).get('usd_24h_change', 0),
            'SOL_24h_change': data.get('solana', {}).get('usd_24h_change', 0),
            'RLB_24h_change': data.get('rollbit-coin', {}).get('usd_24h_change', 0),
            'RLB_market_cap': data.get('rollbit-coin', {}).get('usd_market_cap', 0),
        }

    def get_rlb_dexscreener(self) -> dict:
        """Get RLB token data from DEXScreener."""
        url = f"{API_ENDPOINTS['dexscreener']}/tokens/{RLB_TOKEN['contract_eth']}"
        data = self._get(url)
        pairs = data.get('pairs', [])
        if not pairs:
            return {}

        pair = pairs[0]
        return {
            'price_usd': float(pair.get('priceUsd', 0)),
            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
            'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
            'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
            'fdv': float(pair.get('fdv', 0)),
            'pair_address': pair.get('pairAddress', ''),
            'dex': pair.get('dexId', ''),
            'txns_24h_buys': pair.get('txns', {}).get('h24', {}).get('buys', 0),
            'txns_24h_sells': pair.get('txns', {}).get('h24', {}).get('sells', 0),
        }


# =============================================================================
# WALLET ANALYZER
# =============================================================================

class WalletAnalyzer:
    """Analyze Rollbit's known wallets across all chains."""

    def __init__(self, api: BlockchainAPI):
        self.api = api

    def analyze_all(self) -> list:
        """Analyze all known Rollbit wallets."""
        results = []

        print("\n" + "=" * 70)
        print("  WALLET ANALYSIS — Rollbit Known Addresses")
        print("=" * 70)

        # Get current prices
        print("\n[1/4] Fetching current prices...")
        prices = self.api.get_current_prices()
        if prices.get('BTC'):
            print(f"  BTC: ${prices['BTC']:,.2f}  |  ETH: ${prices['ETH']:,.2f}  |  SOL: ${prices['SOL']:,.2f}")
            if prices.get('RLB'):
                print(f"  RLB: ${prices['RLB']:.6f}  (mcap: ${prices.get('RLB_market_cap', 0):,.0f})")
        else:
            print("  [WARN] Price data unavailable, using estimates")
            prices = {'BTC': 97000, 'ETH': 3500, 'SOL': 145, 'RLB': 0.05}

        # Bitcoin wallets
        print("\n[2/4] Analyzing BTC wallets...")
        for name, wallet in ROLLBIT_WALLETS['BTC'].items():
            info = self.api.btc_get_address_info(wallet['address'])
            if info:
                usd = info['balance_btc'] * prices['BTC']
                wb = WalletBalance(
                    chain='BTC', address=wallet['address'], label=wallet['label'],
                    balance_native=info['balance_btc'], balance_usd=usd,
                    tx_count=info['tx_count'],
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                )
                results.append(wb)
                print(f"  {wallet['label']}: {info['balance_btc']:.8f} BTC (${usd:,.2f})")
                print(f"    Total received: {info['total_received_btc']:.8f} BTC")
                print(f"    Total sent: {info['total_sent_btc']:.8f} BTC")
                print(f"    Transactions: {info['tx_count']}")

        # Solana wallets
        print("\n[3/4] Analyzing SOL wallets...")
        for name, wallet in ROLLBIT_WALLETS['SOL'].items():
            info = self.api.sol_get_balance(wallet['address'])
            if info:
                usd = info['balance_sol'] * prices['SOL']
                wb = WalletBalance(
                    chain='SOL', address=wallet['address'], label=wallet['label'],
                    balance_native=info['balance_sol'], balance_usd=usd,
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                )
                results.append(wb)
                print(f"  {wallet['label']}: {info['balance_sol']:,.4f} SOL (${usd:,.2f})")

        # Ethereum wallets
        print("\n[4/4] Analyzing ETH wallets...")
        for name, wallet in ROLLBIT_WALLETS['ETH'].items():
            info = self.api.eth_get_balance(wallet['address'])
            if info:
                usd = info['balance_eth'] * prices['ETH']
                wb = WalletBalance(
                    chain='ETH', address=wallet['address'], label=wallet['label'],
                    balance_native=info['balance_eth'], balance_usd=usd,
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                )
                results.append(wb)
                print(f"  {wallet['label']}: {info['balance_eth']:.6f} ETH (${usd:,.2f})")

        # Summary
        total_usd = sum(w.balance_usd for w in results)
        print(f"\n  TOTAL across all wallets: ${total_usd:,.2f}")

        return results


# =============================================================================
# TREASURY FLOW TRACER
# =============================================================================

class TreasuryFlowTracer:
    """Trace large outflows from Rollbit treasury wallets."""

    def __init__(self, api: BlockchainAPI):
        self.api = api

    def trace_all(self) -> dict:
        """Trace fund flows from all known treasury wallets."""
        print("\n" + "=" * 70)
        print("  TREASURY FLOW TRACING — Large Outflows")
        print("=" * 70)

        result = {
            'known_events': KNOWN_TREASURY_EVENTS,
            'btc_transactions': [],
            'sol_transactions': [],
            'eth_transactions': [],
            'total_confirmed_outflow_usd': 0,
        }

        # Known events total
        total_known = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS
            if e['direction'] == 'outflow'
        )
        print(f"\n  Known documented outflows: ${total_known:,.2f}")

        # BTC transaction history
        print("\n  [BTC] Fetching recent transactions...")
        btc_addr = ROLLBIT_WALLETS['BTC']['treasury']['address']
        btc_txs = self.api.btc_get_transactions(btc_addr, limit=25)
        result['btc_transactions'] = btc_txs

        outflows = [tx for tx in btc_txs if tx['direction'] == 'out']
        inflows = [tx for tx in btc_txs if tx['direction'] == 'in']
        print(f"    Recent transactions: {len(btc_txs)} total")
        print(f"    Outflows: {len(outflows)} | Inflows: {len(inflows)}")
        if outflows:
            largest = max(outflows, key=lambda x: x['amount_btc'])
            print(f"    Largest outflow: {largest['amount_btc']:.8f} BTC on {largest['timestamp'][:10]}")

        # SOL transaction signatures
        print("\n  [SOL] Fetching recent transaction signatures...")
        sol_addr = ROLLBIT_WALLETS['SOL']['treasury']['address']
        sol_sigs = self.api.sol_get_signatures(sol_addr, limit=20)
        result['sol_transactions'] = sol_sigs
        print(f"    Recent signatures: {len(sol_sigs)}")
        if sol_sigs:
            latest = sol_sigs[0]
            print(f"    Latest activity: {latest.get('timestamp', 'unknown')[:10]}")

        # ETH transaction history (hot wallet)
        print("\n  [ETH] Fetching hot wallet transactions...")
        eth_addr = ROLLBIT_WALLETS['ETH']['hot_wallet']['address']
        eth_txs = self.api.eth_get_transactions(eth_addr, limit=50)
        result['eth_transactions'] = eth_txs

        eth_outflows = [tx for tx in eth_txs if tx['direction'] == 'out' and tx['amount_eth'] > 0.1]
        print(f"    Recent transactions: {len(eth_txs)} total")
        print(f"    Significant outflows (>0.1 ETH): {len(eth_outflows)}")

        # Token transfers
        print("\n  [ETH] Fetching token transfers...")
        token_txs = self.api.eth_get_token_transfers(eth_addr, limit=50)
        rlb_transfers = [tx for tx in token_txs if 'RLB' in tx.get('token_symbol', '').upper()]
        print(f"    Token transfers: {len(token_txs)} total")
        print(f"    RLB transfers: {len(rlb_transfers)}")

        # Print known events timeline
        print("\n  " + "-" * 60)
        print("  DOCUMENTED TREASURY EVENTS (from public reports)")
        print("  " + "-" * 60)
        for event in sorted(KNOWN_TREASURY_EVENTS, key=lambda x: x['date']):
            direction = (
                "⬆️ OUTFLOW" if event['direction'] == 'outflow' else
                "⬇️ INFLOW" if event['direction'] == 'inflow' else
                "↔️ MIXED FLOW" if event['direction'] == 'mixed' else
                "🚨 SEIZURE"
            )
            print(f"  [{event['date']}] {direction}: ${event['amount_usd']:,.0f}")
            print(f"    {event['event']}")
            print(f"    Source: {event['source']}")
            print()

        result['total_confirmed_outflow_usd'] = total_known
        return result


# =============================================================================
# RLB TOKEN ANALYZER
# =============================================================================

class RLBTokenAnalyzer:
    """Analyze RLB token for manipulation indicators."""

    def __init__(self, api: BlockchainAPI):
        self.api = api

    def analyze(self) -> dict:
        """Analyze RLB token metrics and manipulation indicators."""
        print("\n" + "=" * 70)
        print("  RLB TOKEN ANALYSIS — Buyback vs Reality")
        print("=" * 70)

        result = {
            'token_info': {},
            'price_analysis': {},
            'manipulation_indicators': [],
            'buyback_analysis': {},
        }

        # Get DEXScreener data
        print("\n  Fetching DEXScreener data...")
        dex_data = self.api.get_rlb_dexscreener()
        if dex_data:
            result['token_info'] = dex_data
            print(f"  Price: ${dex_data.get('price_usd', 0):.6f}")
            print(f"  24h Volume: ${dex_data.get('volume_24h', 0):,.2f}")
            print(f"  Liquidity: ${dex_data.get('liquidity_usd', 0):,.2f}")
            print(f"  FDV: ${dex_data.get('fdv', 0):,.2f}")
            print(f"  24h Buys: {dex_data.get('txns_24h_buys', 0)} | Sells: {dex_data.get('txns_24h_sells', 0)}")

        # Get CoinGecko data
        prices = self.api.get_current_prices()
        rlb_price = prices.get('RLB', 0)
        rlb_mcap = prices.get('RLB_market_cap', 0)

        # Buyback analysis
        print("\n  " + "-" * 60)
        print("  BUYBACK vs REALITY ANALYSIS")
        print("  " + "-" * 60)

        # Rollbit claims ~$5M/month in buybacks
        claimed_monthly_buyback = 5_000_000
        claimed_annual = claimed_monthly_buyback * 12

        result['buyback_analysis'] = {
            'claimed_monthly_buyback_usd': claimed_monthly_buyback,
            'claimed_annual_buyback_usd': claimed_annual,
            'initial_supply': RLB_TOKEN['initial_supply'],
            'reported_burned_pct': 50.86,
            'reported_burned_tokens': int(RLB_TOKEN['initial_supply'] * 0.5086),
            'current_price_usd': rlb_price,
            'current_market_cap': rlb_mcap,
        }

        print(f"\n  Claimed buyback rate: ~${claimed_monthly_buyback:,.0f}/month")
        print(f"  Initial supply: {RLB_TOKEN['initial_supply']:,.0f} RLB")
        print(f"  Reported burned: 50.86% ({int(RLB_TOKEN['initial_supply'] * 0.5086):,.0f} tokens)")
        if rlb_price > 0:
            print(f"  Current price: ${rlb_price:.6f}")
            tokens_per_month = claimed_monthly_buyback / rlb_price
            print(f"  Implied tokens bought/month: {tokens_per_month:,.0f}")

        # Manipulation indicators
        print("\n  " + "-" * 60)
        print("  MANIPULATION INDICATORS")
        print("  " + "-" * 60)

        indicators = []

        # 1. Price decline despite "buybacks"
        indicators.append({
            'indicator': 'Price decline despite claimed buybacks',
            'severity': 'HIGH',
            'details': (
                'RLB dropped ~77% from its highs despite Rollbit claiming $5M/month in buybacks. '
                'Genuine buyback pressure at this scale should support price, not allow a 77% decline. '
                'This strongly suggests either: (a) buybacks are not happening, (b) insider selling '
                'overwhelms buyback volume, or (c) the numbers are fabricated.'
            ),
        })
        print(f"\n  🔴 Price decline despite claimed buybacks (-77% from highs)")

        # 2. Gainzy/influencer dumping via mixers
        indicators.append({
            'indicator': 'Influencer RLB dumping via Rollbit as mixer',
            'severity': 'HIGH',
            'details': (
                'On-chain analysis showed influencer Gainzy claimed to buy $400K in RLB but was actually '
                'selling. Pattern: buy with SOL → tweet about RLB → deposit to Rollbit → withdraw from '
                'different wallets → sell. Rollbit platform used as intermediary mixer to obfuscate selling.'
            ),
        })
        print(f"  🔴 Influencer dumping via Rollbit as mixer (documented)")

        # 3. Revenue centralization vs on-chain burns
        indicators.append({
            'indicator': 'Revenue figures centralized, burns on-chain',
            'severity': 'MEDIUM',
            'details': (
                'While the burn transactions themselves are on-chain and verifiable, the revenue figures '
                'that determine HOW MUCH to buy and burn are centralized and controlled entirely by Rollbit. '
                'There is no independent audit of their claimed revenue numbers.'
            ),
        })
        print(f"  🟡 Revenue numbers centralized (no independent audit)")

        # 4. Low liquidity relative to claimed burns
        if dex_data and dex_data.get('liquidity_usd', 0) > 0:
            liq = dex_data['liquidity_usd']
            if liq < 5_000_000:
                indicators.append({
                    'indicator': 'Extremely low DEX liquidity',
                    'severity': 'HIGH',
                    'details': f'DEX liquidity only ${liq:,.2f}. A single large sell could crash the price. '
                               f'This makes the claimed $5M/month buyback implausible through DEX alone.',
                })
                print(f"  🔴 Low DEX liquidity: ${liq:,.2f}")

        # 5. Treasury outflows vs buybacks
        total_treasury_outflow = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS
            if e['direction'] == 'outflow'
        )
        indicators.append({
            'indicator': 'Treasury-related outflows still meaningful relative to RLB liquidity',
            'severity': 'CRITICAL',
            'details': (
                f'Documented treasury-related outflows total ${total_treasury_outflow:,.0f}. '
                f'Even after correcting previously overstated BTC flow assumptions, the outflow set '
                f'remains large relative to the current visible RLB DEX liquidity.'
            ),
        })
        print(f"  🔴 Treasury-related outflows: ${total_treasury_outflow:,.0f}")

        result['manipulation_indicators'] = indicators
        result['price_analysis'] = {
            'current_price': rlb_price,
            'market_cap': rlb_mcap,
            'decline_from_high_pct': -77,  # documented
        }

        return result


# =============================================================================
# RISK SCORER
# =============================================================================

class RiskScorer:
    """Score exit-scam / insolvency risk based on on-chain indicators."""

    @staticmethod
    def score(wallet_data: list, treasury_data: dict, rlb_data: dict) -> list:
        """Generate risk indicators with scores."""

        print("\n" + "=" * 70)
        print("  RISK ASSESSMENT — Exit Scam Indicators")
        print("=" * 70)

        indicators = []

        # 1. Treasury drainage rate
        total_outflow = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS
            if e['direction'] == 'outflow'
        )
        score = min(10, total_outflow / 10_000_000)  # $100M = score 10
        indicators.append(RiskIndicator(
            name='Treasury Outflow Pressure',
            score=score,
            description=f'${total_outflow:,.0f} in documented treasury-related outflows',
            evidence=[
                f"{e['date']}: {e['event']} (${e['amount_usd']:,.0f})"
                for e in KNOWN_TREASURY_EVENTS if e['direction'] == 'outflow'
            ]
        ))
        color = '🔴' if score >= 7 else '🟡' if score >= 4 else '🟢'
        print(f"\n  {color} Treasury Outflow Pressure: {score:.1f}/10")

        # 2. Law enforcement action
        seizure = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS
            if e['direction'] == 'seizure'
        )
        score2 = 10.0 if seizure > 0 else 0.0
        indicators.append(RiskIndicator(
            name='Law Enforcement Seizures',
            score=score2,
            description=f'${seizure:,.0f} seized by Ukrainian authorities',
            evidence=['$123M seized by Pechersk District Court, linked to Bull Gaming N.V.']
        ))
        print(f"  🔴 Law Enforcement Seizure: {score2:.1f}/10")

        # 3. Token price collapse
        score3 = 7.7  # -77% decline
        indicators.append(RiskIndicator(
            name='Token Price Collapse',
            score=score3,
            description='RLB token declined 77% from highs despite claimed buyback program',
            evidence=[
                'Claimed $5M/month buybacks should support price',
                'Influencer Gainzy caught dumping while shilling',
                '$250K token promotion schemes exposed',
            ]
        ))
        print(f"  🔴 Token Price Collapse: {score3:.1f}/10")

        # 4. Wallet balance vs obligations
        total_wallet_usd = sum(w.balance_usd for w in wallet_data) if wallet_data else 0
        if total_wallet_usd > 0:
            # Compare to seized amount as proxy for scale of operations
            ratio = total_wallet_usd / 123_000_000 if seizure else 0
            score4 = max(0, 10 - (ratio * 10))
        else:
            score4 = 8.0  # Can't verify = high risk
        indicators.append(RiskIndicator(
            name='Solvency Indicator',
            score=score4,
            description=f'Known wallet balances: ${total_wallet_usd:,.2f} vs $123M in seized assets',
            evidence=[
                f'Known public BTC + SOL wallets held ~${total_wallet_usd:,.0f} at the latest snapshot',
                '$123M seizure reporting indicates that critical reserves may also have been held off-wallet',
            ]
        ))
        color = '🔴' if score4 >= 7 else '🟡' if score4 >= 4 else '🟢'
        print(f"  {color} Solvency Risk: {score4:.1f}/10")

        # 5. License status
        score5 = 7.0
        indicators.append(RiskIndicator(
            name='Regulatory Status',
            score=score5,
            description='Operating under transitional arrangement; original license expired Aug 2024',
            evidence=[
                'Gaming Curacao/365/JAZ ceased operations August 18, 2024',
                'Pending application OGL/2024/1260/0494 with new Curacao GCB',
                'License removed from website in March 2023 (restored after controversy)',
            ]
        ))
        print(f"  🔴 Regulatory Risk: {score5:.1f}/10")

        # 6. Victim complaint acceleration
        score6 = 8.0
        indicators.append(RiskIndicator(
            name='Complaint Acceleration',
            score=score6,
            description='Counted public complaints rose from 2 in 2022 to 47 in 2025, with 13 more already visible in 2026 YTD',
            evidence=[
                '2022: 2 cases ($10K)',
                '2023: 4 cases ($46K)',
                '2024: 9 cases ($177K)',
                '2025: 47 cases ($258K)',
                '2026 YTD: 13 cases ($46K)',
                'Public resolution rate: 5.0% (4/80)',
            ]
        ))
        print(f"  🔴 Complaint Acceleration: {score6:.1f}/10")

        # Overall score
        avg_score = sum(r.score for r in indicators) / len(indicators) if indicators else 0
        print(f"\n  {'=' * 40}")
        print(f"  OVERALL RISK SCORE: {avg_score:.1f}/10")
        if avg_score >= 8:
            print(f"  RISK LEVEL: 🔴 CRITICAL — Active exit scam indicators")
        elif avg_score >= 6:
            print(f"  RISK LEVEL: 🟡 HIGH — Significant red flags")
        elif avg_score >= 4:
            print(f"  RISK LEVEL: 🟡 ELEVATED — Notable concerns")
        else:
            print(f"  RISK LEVEL: 🟢 MODERATE")
        print(f"  {'=' * 40}")

        return indicators


# =============================================================================
# WALLET CLUSTERER
# =============================================================================

class WalletClusterer:
    """Group wallets by shared transaction patterns."""

    def __init__(self, api: BlockchainAPI):
        self.api = api

    def cluster_eth_wallets(self) -> dict:
        """Cluster Ethereum wallets by shared transaction counterparties."""
        print("\n" + "=" * 70)
        print("  WALLET CLUSTERING — Shared Transaction Patterns")
        print("=" * 70)

        clusters = {}
        all_counterparties = {}

        for name, wallet in ROLLBIT_WALLETS['ETH'].items():
            addr = wallet['address'].lower()
            print(f"\n  Analyzing {wallet['label']} ({addr[:10]}...)")

            txs = self.api.eth_get_transactions(addr, limit=50)
            counterparties = set()
            for tx in txs:
                other = tx['to'] if tx['direction'] == 'out' else tx['from']
                if other and other.lower() != addr:
                    counterparties.add(other.lower())

            all_counterparties[addr] = counterparties
            print(f"    Unique counterparties: {len(counterparties)}")

        # Find shared counterparties
        print("\n  Looking for shared counterparties...")
        addresses = list(all_counterparties.keys())
        shared = {}
        for i in range(len(addresses)):
            for j in range(i + 1, len(addresses)):
                common = all_counterparties[addresses[i]] & all_counterparties[addresses[j]]
                if common:
                    pair_key = f"{addresses[i][:10]}...↔{addresses[j][:10]}..."
                    shared[pair_key] = {
                        'wallet_a': addresses[i],
                        'wallet_b': addresses[j],
                        'shared_counterparties': list(common)[:20],
                        'shared_count': len(common),
                    }
                    print(f"    {pair_key}: {len(common)} shared counterparties")

        clusters['known_rollbit_wallets'] = list(ROLLBIT_WALLETS['ETH'].keys())
        clusters['shared_counterparties'] = shared

        return clusters


# =============================================================================
# MAIN ANALYSIS ORCHESTRATOR
# =============================================================================

class RollbitForensicAnalyzer:
    """Main orchestrator for full on-chain forensic analysis."""

    def __init__(self, etherscan_key: str = '', cached: bool = False):
        self.cached = cached
        self.api = BlockchainAPI(etherscan_key=etherscan_key)
        self.wallet_analyzer = WalletAnalyzer(self.api)
        self.flow_tracer = TreasuryFlowTracer(self.api)
        self.rlb_analyzer = RLBTokenAnalyzer(self.api)
        self.clusterer = WalletClusterer(self.api)

    def run_full_analysis(self) -> dict:
        """Run complete forensic analysis."""
        print("\n" + "#" * 70)
        print("#  ROLLBIT ON-CHAIN FORENSIC ANALYSIS")
        print(f"#  Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("#" * 70)

        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'wallets': [],
            'treasury_flows': {},
            'rlb_analysis': {},
            'wallet_clusters': {},
            'risk_indicators': [],
            'summary': {},
        }

        if self.cached:
            return self._run_cached_analysis()

        # 1. Wallet analysis
        wallet_data = self.wallet_analyzer.analyze_all()
        result['wallets'] = [asdict(w) for w in wallet_data]

        # 2. Treasury flow tracing
        treasury_data = self.flow_tracer.trace_all()
        result['treasury_flows'] = treasury_data

        # 3. RLB token analysis
        rlb_data = self.rlb_analyzer.analyze()
        result['rlb_analysis'] = rlb_data

        # 4. Wallet clustering
        clusters = self.clusterer.cluster_eth_wallets()
        result['wallet_clusters'] = clusters

        # 5. Risk scoring
        risk_indicators = RiskScorer.score(wallet_data, treasury_data, rlb_data)
        result['risk_indicators'] = [asdict(r) for r in risk_indicators]

        # 6. Generate summary
        avg_risk = sum(r.score for r in risk_indicators) / len(risk_indicators) if risk_indicators else 0
        total_outflow = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS if e['direction'] == 'outflow'
        )
        total_seizure = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS if e['direction'] == 'seizure'
        )

        result['summary'] = {
            'total_wallets_analyzed': len(wallet_data),
            'total_wallet_balance_usd': sum(w.balance_usd for w in wallet_data),
            'total_documented_outflows_usd': total_outflow,
            'total_seized_usd': total_seizure,
            'avg_risk_score': round(avg_risk, 1),
            'risk_level': 'CRITICAL' if avg_risk >= 8 else 'HIGH' if avg_risk >= 6 else 'ELEVATED',
            'known_events_count': len(KNOWN_TREASURY_EVENTS),
        }

        return result

    def _run_cached_analysis(self) -> dict:
        """Run analysis using cached / hardcoded known data only."""
        print("\n  [CACHED MODE] Using known data — no live API calls")

        wallet_data = []
        treasury_data = {
            'known_events': KNOWN_TREASURY_EVENTS,
            'total_confirmed_outflow_usd': sum(
                e['amount_usd'] for e in KNOWN_TREASURY_EVENTS if e['direction'] == 'outflow'
            ),
        }

        # Print known events
        print("\n  DOCUMENTED TREASURY EVENTS:")
        for event in sorted(KNOWN_TREASURY_EVENTS, key=lambda x: x['date']):
            direction_icon = "⬆️" if event['direction'] == 'outflow' else "🚨"
            print(f"  [{event['date']}] {direction_icon} ${event['amount_usd']:,.0f} — {event['event']}")

        rlb_data = {
            'buyback_analysis': {
                'claimed_monthly_buyback_usd': 5_000_000,
                'initial_supply': RLB_TOKEN['initial_supply'],
                'reported_burned_pct': 50.86,
            },
            'manipulation_indicators': [
                {'indicator': 'Price decline despite buybacks', 'severity': 'HIGH'},
                {'indicator': 'Influencer dumping via mixer', 'severity': 'HIGH'},
                {'indicator': 'Revenue centralization', 'severity': 'MEDIUM'},
                {'indicator': 'Treasury draining faster than buybacks', 'severity': 'CRITICAL'},
            ],
        }

        risk_indicators = RiskScorer.score(wallet_data, treasury_data, rlb_data)

        total_outflow = treasury_data['total_confirmed_outflow_usd']
        total_seizure = sum(
            e['amount_usd'] for e in KNOWN_TREASURY_EVENTS if e['direction'] == 'seizure'
        )

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'mode': 'cached',
            'wallets': [],
            'treasury_flows': treasury_data,
            'rlb_analysis': rlb_data,
            'wallet_clusters': {},
            'risk_indicators': [asdict(r) for r in risk_indicators],
            'summary': {
                'total_documented_outflows_usd': total_outflow,
                'total_seized_usd': total_seizure,
                'avg_risk_score': round(
                    sum(r.score for r in risk_indicators) / len(risk_indicators), 1
                ) if risk_indicators else 0,
                'risk_level': 'CRITICAL',
                'known_events_count': len(KNOWN_TREASURY_EVENTS),
            },
        }

    def save_results(self, results: dict, output_path: str = None):
        """Save analysis results to JSON."""
        if not output_path:
            output_path = str(OUTPUT_DIR / 'blockchain_analysis.json')

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Rollbit On-Chain Blockchain Forensics Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blockchain_analyzer.py --full                    # Full live analysis
  python blockchain_analyzer.py --cached                  # Offline / cached data only
  python blockchain_analyzer.py --wallet SOL              # Analyze SOL wallets only
  python blockchain_analyzer.py --trace                   # Trace treasury outflows
  python blockchain_analyzer.py --rlb                     # RLB token analysis
  python blockchain_analyzer.py --full --etherscan-key KEY # With Etherscan API key
        """
    )

    parser.add_argument('--full', action='store_true', help='Run complete analysis')
    parser.add_argument('--cached', action='store_true', help='Use cached/hardcoded data only (no API calls)')
    parser.add_argument('--wallet', choices=['BTC', 'ETH', 'SOL', 'ALL'], help='Analyze specific chain wallets')
    parser.add_argument('--trace', action='store_true', help='Trace treasury outflows')
    parser.add_argument('--rlb', action='store_true', help='RLB token analysis')
    parser.add_argument('--cluster', action='store_true', help='Wallet clustering analysis')
    parser.add_argument('--etherscan-key', default='', help='Etherscan API key for higher rate limits')
    parser.add_argument('--output', default=None, help='Output directory for results')

    args = parser.parse_args()

    if not any([args.full, args.cached, args.wallet, args.trace, args.rlb, args.cluster]):
        parser.print_help()
        print("\n  [TIP] Try: python blockchain_analyzer.py --cached")
        sys.exit(0)

    if not HAS_REQUESTS and not args.cached:
        print("[ERROR] 'requests' library required for live analysis.")
        print("        Install with: pip install requests")
        print("        Or use --cached for offline analysis.")
        sys.exit(1)

    analyzer = RollbitForensicAnalyzer(
        etherscan_key=args.etherscan_key,
        cached=args.cached,
    )

    output_dir = args.output or str(OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    if args.full or args.cached:
        results = analyzer.run_full_analysis()
        analyzer.save_results(results, os.path.join(output_dir, 'blockchain_analysis.json'))

    elif args.wallet:
        api = BlockchainAPI(etherscan_key=args.etherscan_key)
        wa = WalletAnalyzer(api)
        wa.analyze_all()

    elif args.trace:
        api = BlockchainAPI(etherscan_key=args.etherscan_key)
        tracer = TreasuryFlowTracer(api)
        result = tracer.trace_all()
        with open(os.path.join(output_dir, 'treasury_flows.json'), 'w') as f:
            json.dump(result, f, indent=2, default=str)

    elif args.rlb:
        api = BlockchainAPI(etherscan_key=args.etherscan_key)
        rlb = RLBTokenAnalyzer(api)
        result = rlb.analyze()
        with open(os.path.join(output_dir, 'rlb_analysis.json'), 'w') as f:
            json.dump(result, f, indent=2, default=str)

    elif args.cluster:
        api = BlockchainAPI(etherscan_key=args.etherscan_key)
        clusterer = WalletClusterer(api)
        result = clusterer.cluster_eth_wallets()
        with open(os.path.join(output_dir, 'wallet_clusters.json'), 'w') as f:
            json.dump(result, f, indent=2, default=str)

    print("\n  Analysis complete.\n")


if __name__ == '__main__':
    main()

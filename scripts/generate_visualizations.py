#!/usr/bin/env python3
"""
Rollbit Forensic Visualizations Generator
==========================================
Generates 5 key charts from on-chain data and victim case database:
1. Treasury Flow Analysis (outflows over time)
2. RLB Market Structure Stress (price, buybacks, and liquidity)
3. Victim Impact Analysis (from case database)
4. Wallet Network Graph (fund flow visualization)
5. Evidence Timeline (critical events chronology)

Usage:
    python generate_visualizations.py                # Generate all charts
    python generate_visualizations.py --cached       # Use hardcoded data
    python generate_visualizations.py --output DIR   # Custom output dir
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.dates as mdates
    from matplotlib.gridspec import GridSpec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[ERROR] matplotlib required: pip install matplotlib")
    sys.exit(1)

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

DATA_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = DATA_DIR / 'output' / 'charts'
CASES_DB = DATA_DIR / 'cases_database.json'

# Color palette
COLORS = {
    'bg': '#0d1117',
    'bg2': '#161b22',
    'text': '#e6edf3',
    'text2': '#8b949e',
    'red': '#f85149',
    'orange': '#d29922',
    'green': '#3fb950',
    'blue': '#58a6ff',
    'purple': '#bc8cff',
    'cyan': '#39d2c0',
    'accent': '#ff6b6b',
}

# Known treasury events
TREASURY_EVENTS = [
    {'date': '2025-09-03', 'label': '50K SOL sold', 'amount_usd': 10_170_000, 'chain': 'SOL'},
    {'date': '2026-01-11', 'label': '15K SOL (×2)', 'amount_usd': 4_090_000, 'chain': 'SOL'},
    {'date': '2026-01-15', 'label': '21.4K SOL', 'amount_usd': 3_140_000, 'chain': 'SOL'},
]

SEIZURE_EVENT = {'date': '2025-05-09', 'label': '$123M seized (Ukraine)', 'amount_usd': 123_000_000}

# RLB price history (approximate monthly from public data)
RLB_PRICE_HISTORY = [
    ('2023-07', 0.015), ('2023-08', 0.08), ('2023-09', 0.12), ('2023-10', 0.18),
    ('2023-11', 0.22), ('2023-12', 0.15), ('2024-01', 0.13), ('2024-02', 0.11),
    ('2024-03', 0.10), ('2024-04', 0.09), ('2024-05', 0.08), ('2024-06', 0.07),
    ('2024-07', 0.06), ('2024-08', 0.044), ('2024-09', 0.05), ('2024-10', 0.055),
    ('2024-11', 0.06), ('2024-12', 0.055), ('2025-01', 0.05), ('2025-02', 0.048),
    ('2025-03', 0.05), ('2025-06', 0.052), ('2025-09', 0.048), ('2025-12', 0.045),
    ('2026-01', 0.042), ('2026-02', 0.04), ('2026-03', 0.038),
]


def setup_style():
    plt.rcParams.update({
        'figure.facecolor': COLORS['bg'],
        'axes.facecolor': COLORS['bg2'],
        'axes.edgecolor': COLORS['text2'],
        'axes.labelcolor': COLORS['text'],
        'text.color': COLORS['text'],
        'xtick.color': COLORS['text2'],
        'ytick.color': COLORS['text2'],
        'grid.color': '#21262d',
        'grid.alpha': 0.5,
        'font.family': 'sans-serif',
        'font.size': 10,
    })


def load_cases():
    if CASES_DB.exists():
        with open(CASES_DB) as f:
            return json.load(f)
    return {}


def canonical_cases(payload):
    """Return a flat list of cases from either the new or legacy schema."""
    if isinstance(payload, dict) and isinstance(payload.get('cases'), list):
        return payload['cases']

    cases = []
    for key in ['bitcointalk_cases', 'trustpilot_cases', 'casino_guru_cases', 'other_forum_cases']:
        for case in payload.get(key, []):
            enriched = dict(case)
            enriched['source'] = key.replace('_cases', '')
            enriched['counted_in_totals'] = True
            cases.append(enriched)
    return cases


# =========================================================================
# CHART 1: Treasury Flow Analysis
# =========================================================================

def chart_treasury_flows(output_dir):
    print("  [1/5] Treasury Flow Analysis...")
    fig, ax = plt.subplots(figsize=(14, 7))

    events = sorted(TREASURY_EVENTS, key=lambda x: x['date'])
    dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in events]
    amounts = [e['amount_usd'] / 1e6 for e in events]
    cumulative = []
    total = 0
    for a in amounts:
        total += a
        cumulative.append(total)
    chain_colors = {'SOL': COLORS['purple'], 'BTC': COLORS['orange']}
    bar_colors = [chain_colors.get(e['chain'], COLORS['blue']) for e in events]

    bars = ax.bar(dates, amounts, width=8, color=bar_colors, alpha=0.85, zorder=3)
    ax2 = ax.twinx()
    ax2.plot(dates, cumulative, color=COLORS['red'], linewidth=2.5,
             marker='o', markersize=8, zorder=4, label='Cumulative')
    ax2.fill_between(dates, cumulative, alpha=0.15, color=COLORS['red'])

    for i, (d, a) in enumerate(zip(dates, amounts)):
        ax.text(d, a + 0.5, f"${a:.1f}M", ha='center', fontsize=9,
                color=COLORS['text'], fontweight='bold')

    ax.set_title('Rollbit Treasury Outflows\n(Documented from Public Reports)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Individual Outflow ($M)', fontsize=12)
    ax2.set_ylabel('Cumulative Outflow ($M)', fontsize=12, color=COLORS['red'])
    ax2.tick_params(axis='y', colors=COLORS['red'])

    sol_patch = mpatches.Patch(color=COLORS['purple'], label='SOL outflows')
    btc_patch = mpatches.Patch(color=COLORS['orange'], label='BTC outflows')
    ax.legend(handles=[sol_patch, btc_patch, ax2.get_lines()[0]],
              loc='upper left', framealpha=0.8)
    ax.grid(axis='y', alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    total_usd = sum(e['amount_usd'] for e in events)
    ax.text(0.98, 0.02, f"Total documented outflows: ${total_usd/1e6:.1f}M",
            transform=ax.transAxes, ha='right', fontsize=11,
            color=COLORS['red'], fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=COLORS['bg'], alpha=0.8))

    plt.tight_layout()
    path = os.path.join(output_dir, 'treasury_flow_analysis.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved: {path}")


# =========================================================================
# CHART 2: RLB Manipulation Evidence
# =========================================================================

def chart_rlb_manipulation(output_dir):
    print("  [2/5] RLB Market Structure Stress...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])

    dates = [datetime.strptime(d, '%Y-%m') for d, _ in RLB_PRICE_HISTORY]
    prices = [p for _, p in RLB_PRICE_HISTORY]

    ax1.plot(dates, prices, color=COLORS['red'], linewidth=2, label='RLB Price')
    ax1.fill_between(dates, prices, alpha=0.15, color=COLORS['red'])

    peak_idx = prices.index(max(prices))
    ax1.annotate(f'Peak: ${prices[peak_idx]:.3f}', xy=(dates[peak_idx], prices[peak_idx]),
                 xytext=(30, 20), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color=COLORS['green']),
                 fontsize=10, color=COLORS['green'], fontweight='bold')
    ax1.annotate(f'Current: ~${prices[-1]:.3f}\n(-{(1 - prices[-1]/max(prices))*100:.0f}%)',
                 xy=(dates[-1], prices[-1]),
                 xytext=(-80, 30), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color=COLORS['red']),
                 fontsize=10, color=COLORS['red'], fontweight='bold')

    # Claimed buyback line
    buyback_months = len(dates)
    claimed_monthly = [5.0] * buyback_months  # $5M/month claimed
    ax1_twin = ax1.twinx()
    ax1_twin.bar(dates, claimed_monthly, width=20, alpha=0.3,
                 color=COLORS['cyan'], label='Claimed buyback ($M/mo)')
    ax1_twin.set_ylabel('Claimed Buyback ($M/month)', color=COLORS['cyan'])
    ax1_twin.set_ylim(0, 30)
    ax1_twin.tick_params(axis='y', colors=COLORS['cyan'])

    ax1.set_title('RLB Token: Price vs Claimed Buybacks\n"$5M/month buybacks" yet -77% price decline',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('RLB Price (USD)', fontsize=12)
    ax1.grid(alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    # Bottom panel: buyback inconsistency score
    inconsistency = []
    for i, p in enumerate(prices):
        if i == 0:
            inconsistency.append(0)
        else:
            price_change = (p - prices[i-1]) / prices[i-1]
            # If buybacks happening, price should trend up or stable
            # Negative price with claimed buybacks = high inconsistency
            score = max(0, -price_change * 100)
            inconsistency.append(score)

    bar_colors = [COLORS['red'] if v > 5 else COLORS['orange'] if v > 2 else COLORS['green']
                  for v in inconsistency]
    ax2.bar(dates, inconsistency, width=20, color=bar_colors, alpha=0.8)
    ax2.set_title('Buyback Inconsistency Score (higher = larger technical discrepancy)', fontsize=12)
    ax2.set_ylabel('Inconsistency %')
    ax2.grid(alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    plt.tight_layout()
    path = os.path.join(output_dir, 'rlb_manipulation_evidence.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved: {path}")


# =========================================================================
# CHART 3: Victim Impact Analysis
# =========================================================================

def chart_victim_impact(output_dir):
    print("  [3/5] Victim Impact Analysis...")
    payload = load_cases()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Gather all cases
    all_cases = []
    for c in canonical_cases(payload):
        if not c.get('counted_in_totals', True):
            continue
        amt = c.get('amount_usd') or c.get('amount_eur', 0)
        if amt:
            all_cases.append({
                'amount': float(amt),
                'category': c.get('category', 'unknown'),
                'status': c.get('status', 'UNRESOLVED'),
                'source': c.get('source', 'unknown'),
            })

    # 3a: Category breakdown
    ax = axes[0, 0]
    cats = {}
    for c in all_cases:
        cat = c['category'].replace('_', ' ').title()
        cats[cat] = cats.get(cat, 0) + c['amount']
    sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:8]
    labels = [c[0][:20] for c in sorted_cats]
    values = [c[1] / 1000 for c in sorted_cats]
    colors = [COLORS['red'], COLORS['orange'], COLORS['purple'], COLORS['blue'],
              COLORS['cyan'], COLORS['green'], '#ff9ff3', '#feca57']
    ax.barh(labels[::-1], values[::-1], color=colors[:len(labels)][::-1], alpha=0.85)
    ax.set_xlabel('Amount Locked ($K)')
    ax.set_title('By Category', fontsize=12, fontweight='bold')
    for i, v in enumerate(values[::-1]):
        ax.text(v + 0.5, i, f'${v:.0f}K', va='center', fontsize=9, color=COLORS['text'])

    # 3b: Resolution status
    ax = axes[0, 1]
    resolved = sum(1 for c in all_cases if c['status'] == 'RESOLVED')
    unresolved = len(all_cases) - resolved
    sizes = [unresolved, resolved]
    pie_colors = [COLORS['red'], COLORS['green']]
    wedges, texts, autotexts = ax.pie(sizes, labels=['Unresolved', 'Resolved'],
                                       colors=pie_colors, autopct='%1.1f%%',
                                       startangle=90, textprops={'color': COLORS['text']})
    ax.set_title(f'Resolution Rate\n({resolved}/{len(all_cases)} resolved)',
                 fontsize=12, fontweight='bold')

    # 3c: Amount distribution
    ax = axes[1, 0]
    amounts = sorted([c['amount'] for c in all_cases], reverse=True)
    bins = [0, 500, 1000, 5000, 10000, 25000, 50000, 100000]
    hist_data = []
    hist_labels = []
    for i in range(len(bins) - 1):
        count = sum(1 for a in amounts if bins[i] <= a < bins[i+1])
        hist_data.append(count)
        hist_labels.append(f'${bins[i]//1000}K-{bins[i+1]//1000}K')
    over = sum(1 for a in amounts if a >= 100000)
    if over:
        hist_data.append(over)
        hist_labels.append('$100K+')
    ax.bar(range(len(hist_data)), hist_data, color=COLORS['blue'], alpha=0.85)
    ax.set_xticks(range(len(hist_data)))
    ax.set_xticklabels(hist_labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Number of Cases')
    ax.set_title('Amount Distribution', fontsize=12, fontweight='bold')

    # 3d: Source breakdown
    ax = axes[1, 1]
    sources = {}
    for c in all_cases:
        s = c['source'].replace('_', ' ').title()
        sources[s] = sources.get(s, 0) + 1
    s_sorted = sorted(sources.items(), key=lambda x: x[1], reverse=True)
    ax.barh([s[0] for s in s_sorted][::-1], [s[1] for s in s_sorted][::-1],
            color=COLORS['purple'], alpha=0.85)
    ax.set_xlabel('Number of Cases')
    ax.set_title('By Source Platform', fontsize=12, fontweight='bold')

    total_amount = sum(c['amount'] for c in all_cases)
    fig.suptitle(f'Victim Impact Analysis\n{len(all_cases)} quantified complaints | ${total_amount:,.0f} total quantified',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(output_dir, 'victim_impact_analysis.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved: {path}")


# =========================================================================
# CHART 4: Wallet Network Graph
# =========================================================================

def chart_wallet_network_static(output_dir):
    """Fallback wallet graph when networkx is not installed."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor(COLORS['bg2'])

    nodes = {
        'BTC Treasury': (0.1, 0.75, COLORS['blue']),
        'SOL Treasury': (0.1, 0.55, COLORS['blue']),
        'ETH Hot Wallet': (0.1, 0.35, COLORS['blue']),
        'Unknown Wallets': (0.48, 0.67, COLORS['orange']),
        'Binance / CEX\ncustody path': (0.48, 0.42, COLORS['orange']),
        'Ukrainian Accounts\n($123M event)': (0.85, 0.42, COLORS['red']),
        'DEX Liquidity\n(~$4.7M top pools)': (0.85, 0.72, COLORS['purple']),
    }
    edges = [
        ('BTC Treasury', 'Unknown Wallets', 'sampled operational payouts'),
        ('SOL Treasury', 'Unknown Wallets', '$17.4M direct outflow set'),
        ('ETH Hot Wallet', 'Binance / CEX\ncustody path', 'off-wallet custody question'),
        ('Binance / CEX\ncustody path', 'Ukrainian Accounts\n($123M event)', '$123M reported event'),
        ('ETH Hot Wallet', 'DEX Liquidity\n(~$4.7M top pools)', 'RLB market surface'),
    ]

    for src, dst, label in edges:
        x1, y1, _ = nodes[src]
        x2, y2, _ = nodes[dst]
        ax.annotate(
            '',
            xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle='->', color=COLORS['text2'], lw=2, alpha=0.7),
        )
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.025,
            label,
            ha='center',
            va='center',
            fontsize=8,
            color=COLORS['text2'],
            bbox=dict(boxstyle='round,pad=0.25', facecolor=COLORS['bg'], edgecolor='none', alpha=0.8),
        )

    for label, (x, y, color) in nodes.items():
        circle = plt.Circle((x, y), 0.075, color=color, alpha=0.9)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')

    ax.set_title('Rollbit Fund Flow Network\n(Static fallback without networkx)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.15, 0.9)
    ax.axis('off')

    legend_elements = [
        mpatches.Patch(color=COLORS['blue'], label='Known Rollbit Wallets'),
        mpatches.Patch(color=COLORS['orange'], label='External / Unknown'),
        mpatches.Patch(color=COLORS['red'], label='Off-Wallet Event'),
        mpatches.Patch(color=COLORS['purple'], label='Token Liquidity Surface'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10, framealpha=0.8)

    plt.tight_layout()
    path = os.path.join(output_dir, 'wallet_network_graph.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved fallback: {path}")


def chart_wallet_network(output_dir):
    print("  [4/5] Wallet Network Graph...")
    if not HAS_NX:
        print("    [INFO] networkx unavailable; using static matplotlib fallback")
        chart_wallet_network_static(output_dir)
        return

    fig, ax = plt.subplots(figsize=(14, 10))
    G = nx.DiGraph()

    # Nodes: Rollbit wallets
    rollbit_nodes = [
        ('BTC Treasury', {'chain': 'BTC', 'type': 'treasury'}),
        ('SOL Treasury', {'chain': 'SOL', 'type': 'treasury'}),
        ('ETH Hot Wallet', {'chain': 'ETH', 'type': 'hot'}),
        ('rollbit.eth', {'chain': 'ETH', 'type': 'ens'}),
        ('rollbot.eth', {'chain': 'ETH', 'type': 'ens'}),
        ('ERC20 Ops', {'chain': 'ETH', 'type': 'ops'}),
    ]
    for name, attrs in rollbit_nodes:
        G.add_node(name, **attrs, group='rollbit')

    # External nodes
    external_nodes = [
        ('Binance / CEX\ncustody path', {'type': 'cex'}),
        ('Unknown Wallets', {'type': 'unknown'}),
        ('Ukrainian Accounts\n($123M seized)', {'type': 'seized'}),
        ('DEX Liquidity\n(~$4.7M top 4 pools)', {'type': 'dex'}),
        ('Influencer Wallets\n(Gainzy et al)', {'type': 'influencer'}),
    ]
    for name, attrs in external_nodes:
        G.add_node(name, **attrs, group='external')

    # Edges: fund flows
    edges = [
        ('BTC Treasury', 'Unknown Wallets', {'amount': 'sampled operational payouts', 'weight': 2}),
        ('SOL Treasury', 'Unknown Wallets', {'amount': '$17.4M treasury-related SOL flows', 'weight': 3}),
        ('ETH Hot Wallet', 'Binance / CEX\ncustody path', {'amount': 'off-wallet custody questions', 'weight': 4}),
        ('ETH Hot Wallet', 'rollbit.eth', {'amount': 'internal', 'weight': 1}),
        ('ETH Hot Wallet', 'ERC20 Ops', {'amount': 'token ops', 'weight': 1}),
        ('rollbit.eth', 'DEX Liquidity\n(~$4.7M top 4 pools)', {'amount': 'RLB liquidity', 'weight': 2}),
        ('ERC20 Ops', 'Influencer Wallets\n(Gainzy et al)', {'amount': '$250K RLB deals', 'weight': 2}),
        ('Binance / CEX\ncustody path', 'Ukrainian Accounts\n($123M seized)', {'amount': '$123M linked', 'weight': 5}),
    ]
    for src, dst, attrs in edges:
        G.add_edge(src, dst, **attrs)

    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

    # Draw edges
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=COLORS['text2'],
                           width=[w * 0.8 for w in edge_weights],
                           alpha=0.6, arrows=True, arrowsize=20,
                           connectionstyle='arc3,rad=0.1')

    # Edge labels
    edge_labels = {(u, v): G[u][v]['amount'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax,
                                  font_size=7, font_color=COLORS['text2'])

    # Draw nodes
    rollbit_n = [n for n in G.nodes() if G.nodes[n].get('group') == 'rollbit']
    external_n = [n for n in G.nodes() if G.nodes[n].get('group') == 'external']
    seized_n = [n for n in external_n if G.nodes[n].get('type') == 'seized']
    other_ext = [n for n in external_n if n not in seized_n]

    nx.draw_networkx_nodes(G, pos, nodelist=rollbit_n, ax=ax,
                           node_color=COLORS['blue'], node_size=2000, alpha=0.9)
    nx.draw_networkx_nodes(G, pos, nodelist=other_ext, ax=ax,
                           node_color=COLORS['orange'], node_size=1800, alpha=0.9)
    nx.draw_networkx_nodes(G, pos, nodelist=seized_n, ax=ax,
                           node_color=COLORS['red'], node_size=2200, alpha=0.9)

    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color='white',
                            font_weight='bold')

    ax.set_title('Rollbit Fund Flow Network\n(Known Wallet Connections & Documented Flows)',
                 fontsize=16, fontweight='bold', pad=20)

    legend_elements = [
        mpatches.Patch(color=COLORS['blue'], label='Rollbit Wallets'),
        mpatches.Patch(color=COLORS['orange'], label='External Destinations'),
        mpatches.Patch(color=COLORS['red'], label='Seized / Law Enforcement'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10, framealpha=0.8)
    ax.axis('off')

    plt.tight_layout()
    path = os.path.join(output_dir, 'wallet_network_graph.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved: {path}")


# =========================================================================
# CHART 5: Evidence Timeline
# =========================================================================

def chart_evidence_timeline(output_dir):
    print("  [5/5] Evidence Timeline...")
    fig, ax = plt.subplots(figsize=(16, 8))

    events = [
        ('2020-02', 'Rollbit Launch', 'launch', 0),
        ('2022-09', 'First complaints appear', 'complaint', -1),
        ('2023-03', 'License removed from site\nRLB -20%', 'regulatory', 1),
        ('2023-04', 'License "restored"', 'regulatory', -1),
        ('2023-07', 'RLB token launches on Solana', 'token', 1),
        ('2023-08', 'RLB migrated to Ethereum', 'token', -1),
        ('2023-10', 'Gainzy dumping exposed', 'manipulation', 1),
        ('2024-04', 'RLB SOL→ETH migration deadline', 'token', -1),
        ('2024-07', 'Complaints spike begins', 'complaint', 1),
        ('2024-08', 'Original Curacao license expires', 'regulatory', -1),
        ('2024-11', '$44K maintenance scam', 'complaint', 1),
        ('2025-05', '$123M seized in Ukraine', 'seizure', -1),
        ('2025-09', '50K SOL sold ($10.2M)', 'outflow', 1),
        ('2026-01', '497 BTC moved into Rollbit', 'flow', -1),
        ('2026-01', '51.4K SOL transferred ($7.2M)', 'outflow', 1),
        ('2026-02', '626 BTC mixed flow to\nBybit / Rollbit', 'flow', -1),
        ('2026-03', '200 BTC from Coinbase\npartly to Rollbit', 'flow', 1),
    ]

    dates = [datetime.strptime(e[0], '%Y-%m') for e in events]
    labels = [e[1] for e in events]
    categories = [e[2] for e in events]
    positions = [e[3] for e in events]

    cat_colors = {
        'launch': COLORS['green'], 'complaint': COLORS['orange'],
        'regulatory': COLORS['purple'], 'token': COLORS['blue'],
        'manipulation': COLORS['red'], 'seizure': '#ff0000',
        'outflow': COLORS['red'], 'flow': COLORS['cyan'],
    }

    # Timeline base line
    ax.plot([min(dates), max(dates)], [0, 0], color=COLORS['text2'],
            linewidth=2, zorder=1)

    for i, (d, label, cat, pos) in enumerate(zip(dates, labels, categories, positions)):
        y = pos * (2.5 + (i % 3) * 0.8)
        color = cat_colors.get(cat, COLORS['text'])
        ax.scatter(d, 0, s=100, color=color, zorder=5)
        ax.plot([d, d], [0, y], color=color, linewidth=1, alpha=0.6)
        ax.text(d, y + (0.2 if y > 0 else -0.2), label,
                ha='center', va='bottom' if y > 0 else 'top',
                fontsize=8, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['bg'],
                         edgecolor=color, alpha=0.8))

    ax.set_title('Rollbit Investigation Timeline\n(Key Events Chronology)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.xticks(rotation=45, ha='right')
    ax.set_ylim(-8, 8)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    legend_elements = [mpatches.Patch(color=c, label=n.title())
                       for n, c in cat_colors.items()]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9,
              framealpha=0.8, ncol=2)

    plt.tight_layout()
    path = os.path.join(output_dir, 'evidence_timeline.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    Saved: {path}")


# =========================================================================
# MAIN
# =========================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate Rollbit forensic visualizations')
    parser.add_argument('--output', default=str(OUTPUT_DIR))
    parser.add_argument('--cached', action='store_true', help='Use hardcoded data only')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    setup_style()

    print(f"\n{'='*60}")
    print(f"  GENERATING FORENSIC VISUALIZATIONS")
    print(f"{'='*60}\n")

    chart_treasury_flows(args.output)
    chart_rlb_manipulation(args.output)
    chart_victim_impact(args.output)
    chart_wallet_network(args.output)
    chart_evidence_timeline(args.output)

    print(f"\n  All 5 charts saved to: {args.output}")
    print(f"  Done.\n")


if __name__ == '__main__':
    main()

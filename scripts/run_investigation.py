#!/usr/bin/env python3
"""
Rollbit Investigation Orchestrator
====================================
One-command entry point to run the complete forensic investigation.

Usage:
    python run_investigation.py --full      # Full live analysis
    python run_investigation.py --quick     # Cached/offline analysis
    python run_investigation.py --monitor   # Start treasury monitoring
"""

import argparse
import importlib
import os
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPTS_DIR.parent
OUTPUT_DIR = DATA_DIR / 'output'


def banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           ROLLBIT ON-CHAIN FORENSIC INVESTIGATION              ║
║                                                                ║
║  Comprehensive blockchain analysis of Rollbit/Bull Gaming N.V. ║
║  Known wallets: BTC, SOL, ETH (6 addresses)                   ║
║  Known events: mixed treasury flows + $123M seizure           ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def run_technical_phase():
    """Generate analyst-facing technical forensic indicators."""
    print("\n" + "=" * 60)
    print("  TECHNICAL FORENSIC DEEP DIVE")
    print("=" * 60)

    try:
        from technical_deep_dive import run as run_technical_deep_dive
        payload = run_technical_deep_dive(OUTPUT_DIR)
        findings = payload.get('findings', [])
        onchain = payload.get('onchain_visibility_analysis', {})
        rlb = payload.get('rlb_market_structure', {})
        print(f"\n  Phase complete - {len(findings)} technical findings generated")
        print(f"  Visible wallet snapshot: ${onchain.get('visible_wallet_usd', 0):,.2f}")
        print(f"  RLB liquidity / market cap: {rlb.get('liquidity_to_market_cap_ratio', 0) * 100:.1f}%")
        print(f"  Files generated:")
        print(f"    - output/technical_deep_dive.json")
        print(f"    - output/forensic_indicators.csv")
    except Exception as e:
        print(f"\n  Technical deep-dive error: {e}")


def run_public_record_capture(timeout=25, sleep=0.2, max_targets=0):
    """Capture public complaint and record source pages."""
    banner()
    print("\n" + "=" * 60)
    print("  PUBLIC RECORD AND COMPLAINT CAPTURE")
    print("=" * 60)

    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from public_record_capture import run as run_capture
        summary = run_capture(
            include_cases=True,
            include_reports=True,
            include_apis=False,
            max_targets=max_targets,
            timeout=timeout,
            sleep_seconds=sleep,
        )
        print(f"\n  Capture complete")
        print(f"  Records: {summary.get('records_count', 0)}")
        print(f"  OK: {summary.get('ok_count', 0)}")
        print(f"  Failed: {summary.get('failed_count', 0)}")
        print(f"  Blocked/challenged: {summary.get('blocked_or_challenged_count', 0)}")
        print(f"  Capture dir: {summary.get('capture_dir', '')}")
        print(f"  Files generated:")
        print(f"    - output/public_record_capture.json")
        print(f"    - output/public_record_index.csv")
    except Exception as e:
        print(f"\n  Public record capture error: {e}")


def run_full(etherscan_key=''):
    """Run complete investigation: analysis → visualizations → report."""
    banner()
    start = time.time()

    print("=" * 60)
    print("  PHASE 1: On-Chain Blockchain Analysis")
    print("=" * 60)

    sys.path.insert(0, str(SCRIPTS_DIR))

    try:
        from blockchain_analyzer import RollbitForensicAnalyzer
        analyzer = RollbitForensicAnalyzer(etherscan_key=etherscan_key)
        results = analyzer.run_full_analysis()
        analyzer.save_results(results)
        print("\n  ✅ Phase 1 complete")
    except Exception as e:
        print(f"\n  ⚠️  Phase 1 error: {e}")
        print("  Falling back to cached mode...")
        try:
            from blockchain_analyzer import RollbitForensicAnalyzer
            analyzer = RollbitForensicAnalyzer(cached=True)
            results = analyzer.run_full_analysis()
            analyzer.save_results(results)
        except Exception as e2:
            print(f"  ❌ Phase 1 failed: {e2}")
            results = {}

    print("\n" + "=" * 60)
    print("  PHASE 2: Generating Visualizations")
    print("=" * 60)

    try:
        from generate_visualizations import (
            setup_style, chart_treasury_flows, chart_rlb_manipulation,
            chart_victim_impact, chart_wallet_network, chart_evidence_timeline
        )
        charts_dir = str(OUTPUT_DIR / 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        setup_style()
        chart_treasury_flows(charts_dir)
        chart_rlb_manipulation(charts_dir)
        chart_victim_impact(charts_dir)
        chart_wallet_network(charts_dir)
        chart_evidence_timeline(charts_dir)
        print("\n  ✅ Phase 2 complete — 5 charts generated")
    except Exception as e:
        print(f"\n  ⚠️  Phase 2 error: {e}")
        print("  Install dependencies: pip install matplotlib networkx")

    run_technical_phase()

    print("\n" + "=" * 60)
    print("  PHASE 3: Report Summary")
    print("=" * 60)

    summary = results.get('summary', {})
    print(f"""
  Wallets analyzed: {summary.get('total_wallets_analyzed', 'N/A')}
  Wallet balances:  ${summary.get('total_wallet_balance_usd', 0):,.2f}
  Documented outflows: ${summary.get('total_documented_outflows_usd', 0):,.2f}
  Assets seized:    ${summary.get('total_seized_usd', 0):,.2f}
  Risk score:       {summary.get('avg_risk_score', 'N/A')}/10
  Risk level:       {summary.get('risk_level', 'N/A')}
    """)

    elapsed = time.time() - start
    print(f"  Total time: {elapsed:.1f}s")
    print(f"  Results saved to: {OUTPUT_DIR}/")
    print(f"\n  Files generated:")
    print(f"    - output/blockchain_analysis.json")
    print(f"    - output/charts/treasury_flow_analysis.png")
    print(f"    - output/charts/rlb_manipulation_evidence.png")
    print(f"    - output/charts/victim_impact_analysis.png")
    print(f"    - output/charts/wallet_network_graph.png")
    print(f"    - output/charts/evidence_timeline.png")
    print()


def run_quick():
    """Run offline/cached analysis only."""
    banner()
    print("  Running in QUICK mode (cached data, no API calls)\n")

    sys.path.insert(0, str(SCRIPTS_DIR))

    try:
        from blockchain_analyzer import RollbitForensicAnalyzer
        analyzer = RollbitForensicAnalyzer(cached=True)
        results = analyzer.run_full_analysis()
        analyzer.save_results(results)
    except Exception as e:
        print(f"  Error: {e}")
        return

    try:
        from generate_visualizations import (
            setup_style, chart_treasury_flows, chart_rlb_manipulation,
            chart_victim_impact, chart_wallet_network, chart_evidence_timeline
        )
        charts_dir = str(OUTPUT_DIR / 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        setup_style()
        chart_treasury_flows(charts_dir)
        chart_rlb_manipulation(charts_dir)
        chart_victim_impact(charts_dir)
        chart_wallet_network(charts_dir)
        chart_evidence_timeline(charts_dir)
        print("\n  ✅ All charts generated")
    except Exception as e:
        print(f"\n  Visualization error: {e}")

    run_technical_phase()

    print(f"\n  Done. Results in: {OUTPUT_DIR}/\n")


def run_monitor(threshold=50000, interval=120, duration=0, etherscan_key=''):
    """Start real-time treasury monitoring."""
    banner()
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from treasury_monitor import TreasuryMonitor
        monitor = TreasuryMonitor(
            threshold_usd=threshold, interval=interval,
            duration=duration, etherscan_key=etherscan_key
        )
        monitor.run()
    except Exception as e:
        print(f"  Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Rollbit Forensic Investigation Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_investigation.py --full               # Full live analysis
    python run_investigation.py --quick              # Offline cached analysis
    python run_investigation.py --monitor            # Treasury monitoring
    python run_investigation.py --capture-public-records
    python run_investigation.py --full --etherscan-key YOUR_KEY
        """
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--full', action='store_true', help='Full live analysis')
    mode.add_argument('--quick', action='store_true', help='Cached/offline analysis')
    mode.add_argument('--monitor', action='store_true', help='Treasury monitoring')
    mode.add_argument('--capture-public-records', action='store_true',
                      help='Capture public complaint and source pages')

    parser.add_argument('--etherscan-key', default='', help='Etherscan API key')
    parser.add_argument('--threshold', type=float, default=50000,
                        help='Monitor alert threshold (USD)')
    parser.add_argument('--interval', type=int, default=120,
                        help='Monitor poll interval (seconds)')
    parser.add_argument('--duration', type=int, default=0,
                        help='Monitor duration (0 = indefinite)')
    parser.add_argument('--capture-timeout', type=int, default=25,
                        help='Public-record capture request timeout')
    parser.add_argument('--capture-sleep', type=float, default=0.2,
                        help='Public-record capture delay between requests')
    parser.add_argument('--capture-max-targets', type=int, default=0,
                        help='Public-record capture target limit')

    args = parser.parse_args()

    if args.full:
        run_full(etherscan_key=args.etherscan_key)
    elif args.quick:
        run_quick()
    elif args.monitor:
        run_monitor(args.threshold, args.interval, args.duration, args.etherscan_key)
    elif args.capture_public_records:
        run_public_record_capture(
            timeout=args.capture_timeout,
            sleep=args.capture_sleep,
            max_targets=args.capture_max_targets,
        )


if __name__ == '__main__':
    main()

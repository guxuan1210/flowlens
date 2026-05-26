"""CLI entry point for agent evaluation.

Usage:
    python -m eval --tickers AAPL,TSLA,NVDA --date 2025-01-15
    python -m eval --tickers 600519 --date 2025-06-01 --analysts market,fundamentals,capital_flow
    python -m eval --report-only
"""

from __future__ import annotations

import argparse
import os
import sys

from eval.runner import EvalRunner
from eval.metrics import EvalMetrics
from eval.report import generate_report, print_summary
from tradingagents.default_config import DEFAULT_CONFIG


def main():
    parser = argparse.ArgumentParser(
        description="FlowLens Agent Eval — batch backtesting and performance metrics",
    )
    parser.add_argument(
        "--tickers", type=str, default="",
        help="Comma-separated ticker symbols (e.g. AAPL,TSLA,600519)",
    )
    parser.add_argument(
        "--date", type=str, default="",
        help="Historical trade date YYYY-MM-DD",
    )
    parser.add_argument(
        "--holding-days", type=int, default=5,
        help="Forward holding days for return calculation (default: 5)",
    )
    parser.add_argument(
        "--analysts", type=str, default="",
        help="Comma-separated analysts (default: all). Options: market,social,news,fundamentals,capital_flow",
    )
    parser.add_argument(
        "--report-only", action="store_true",
        help="Skip analysis, just generate report from existing memory log",
    )
    parser.add_argument(
        "--output", type=str, default="",
        help="Output directory for report (default: eval/reports/)",
    )
    args = parser.parse_args()

    config = DEFAULT_CONFIG.copy()
    runner = EvalRunner(config, holding_days=args.holding_days)

    if not args.report_only:
        if not args.tickers or not args.date:
            parser.error("--tickers and --date are required (unless using --report-only)")

        tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        analysts = [a.strip() for a in args.analysts.split(",") if a.strip()] if args.analysts else None

        results = runner.run_batch(tickers, args.date, selected_analysts=analysts)

        completed = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]
        print(f"\nBatch complete: {len(completed)} succeeded, {len(failed)} failed")
        if failed:
            for f in failed:
                print(f"  FAILED {f['ticker']}: {f['signal'][:120]}")

        # Resolve pending entries (fetch returns for ALL pending, not just this batch)
        print("\nResolving pending entries ...")
        runner.resolve_all_pending()

    # Generate report
    entries = runner.memory_log.load_entries()
    metrics = EvalMetrics(entries)
    m = metrics.compute()
    detailed = metrics.detailed_results()

    print_summary(m, detailed)

    output_dir = args.output or os.path.join(os.path.dirname(__file__), "reports")
    report_text = generate_report(m, output_dir=output_dir)
    print(report_text[:500] + "..." if len(report_text) > 500 else report_text)


if __name__ == "__main__":
    main()

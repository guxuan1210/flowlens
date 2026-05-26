"""Batch runner: execute the agent pipeline for multiple tickers on a single
historical date, then resolve outcomes by fetching forward returns.
"""

from __future__ import annotations

import time
from typing import Any

import yfinance as yf

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.reflection import Reflector
from tradingagents.agents.utils.rating import parse_rating
from tradingagents.agents.utils.memory import TradingMemoryLog
from tradingagents.llm_clients import create_llm_client

ANALYST_ORDER = ["market", "social", "news", "fundamentals", "capital_flow"]


class EvalRunner:
    """Run the full agent pipeline for multiple tickers and resolve outcomes."""

    def __init__(self, config: dict | None = None, holding_days: int = 5):
        cfg = config or DEFAULT_CONFIG.copy()
        cfg.setdefault("checkpoint_enabled", False)
        self.config = cfg
        self.holding_days = holding_days
        self.memory_log = TradingMemoryLog(cfg)

    def run_batch(
        self,
        tickers: list[str],
        trade_date: str,
        selected_analysts: list[str] | None = None,
    ) -> list[dict]:
        """Run propagate() for each ticker, return list of result dicts."""
        analysts = selected_analysts or ANALYST_ORDER
        results: list[dict] = []

        for i, ticker in enumerate(tickers, 1):
            t0 = time.time()
            print(f"\n[{i}/{len(tickers)}] Running {ticker} on {trade_date} ...")
            try:
                graph = TradingAgentsGraph(
                    selected_analysts=analysts,
                    config=self.config,
                    debug=False,
                )
                final_state, signal = graph.propagate(
                    ticker, trade_date, asset_type="stock"
                )
                elapsed = time.time() - t0
                rating = parse_rating(signal)
                results.append({
                    "ticker": ticker,
                    "date": trade_date,
                    "rating": rating,
                    "signal": signal,
                    "elapsed": elapsed,
                    "status": "completed",
                })
                print(f"  -> {rating} ({elapsed:.0f}s)")
            except Exception as exc:
                elapsed = time.time() - t0
                results.append({
                    "ticker": ticker,
                    "date": trade_date,
                    "rating": "N/A",
                    "signal": str(exc),
                    "elapsed": elapsed,
                    "status": "failed",
                })
                print(f"  -> FAILED: {exc}")

        return results

    def resolve_all_pending(self) -> list[dict]:
        """Fetch forward returns for all pending entries and update the log.

        Returns list of resolved entry dicts.
        """
        pending = self.memory_log.get_pending_entries()
        if not pending:
            print("No pending entries to resolve.")
            return []

        # Build quick LLM client for reflections
        quick_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["quick_think_llm"],
            base_url=self.config.get("backend_url"),
        )
        reflector = Reflector(quick_client.get_llm())

        resolved = []
        for entry in pending:
            ticker = entry["ticker"]
            trade_date = entry["date"]
            print(f"  Resolving {ticker} {trade_date} ...")
            raw, alpha, days = self._fetch_returns(ticker, trade_date)
            if raw is None:
                print(f"    -> price data not yet available, skipping")
                continue
            reflection = reflector.reflect_on_final_decision(
                final_decision=entry.get("decision", ""),
                raw_return=raw,
                alpha_return=alpha,
                benchmark_name=self.config.get("benchmark_map", {}).get("", "SPY"),
            )
            entry["raw_return"] = raw
            entry["alpha_return"] = alpha
            entry["holding_days"] = days
            entry["reflection"] = reflection
            resolved.append(entry)
            print(f"    -> raw={raw:+.2%} alpha={alpha:+.2%} ({days}d)")

        if resolved:
            updates = [
                {
                    "ticker": e["ticker"],
                    "trade_date": e["date"],
                    "raw_return": e["raw_return"],
                    "alpha_return": e["alpha_return"],
                    "holding_days": e["holding_days"],
                    "reflection": e["reflection"],
                }
                for e in resolved
            ]
            self.memory_log.batch_update_with_outcomes(updates)
            print(f"  Updated {len(updates)} entries in memory log.")

        return resolved

    def _fetch_returns(self, ticker: str, trade_date: str):
        """Fetch N-day forward returns. Returns (raw, alpha, days) or (None, None, None)."""
        from datetime import datetime, timedelta

        benchmark = self._resolve_benchmark(ticker)
        try:
            start = datetime.strptime(trade_date, "%Y-%m-%d")
            end = start + timedelta(days=self.holding_days + 7)
            end_str = end.strftime("%Y-%m-%d")

            stock = yf.Ticker(ticker).history(start=trade_date, end=end_str)
            bench = yf.Ticker(benchmark).history(start=trade_date, end=end_str)

            if len(stock) < 2 or len(bench) < 2:
                return None, None, None

            actual_days = min(self.holding_days, len(stock) - 1, len(bench) - 1)
            raw = float(
                (stock["Close"].iloc[actual_days] - stock["Close"].iloc[0])
                / stock["Close"].iloc[0]
            )
            bench_ret = float(
                (bench["Close"].iloc[actual_days] - bench["Close"].iloc[0])
                / bench["Close"].iloc[0]
            )
            return raw, raw - bench_ret, actual_days
        except Exception:
            return None, None, None

    def _resolve_benchmark(self, ticker: str) -> str:
        """Pick benchmark ticker for alpha calculation using config's benchmark_map."""
        explicit = self.config.get("benchmark_ticker")
        if explicit:
            return explicit
        benchmark_map = self.config.get("benchmark_map", {})
        ticker_upper = ticker.upper()
        for suffix, bm in benchmark_map.items():
            if suffix and ticker_upper.endswith(suffix.upper()):
                return bm
        return benchmark_map.get("", "SPY")

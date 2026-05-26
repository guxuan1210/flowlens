"""Service for reading and indexing historical analysis results."""

from __future__ import annotations

import json
from pathlib import Path

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import TradingMemoryLog


def list_all_analyses(ticker: str | None = None, limit: int = 50, offset: int = 0):
    """Scan results_dir for JSON log files. Returns (entries, total)."""
    results_dir = Path(DEFAULT_CONFIG["results_dir"])
    if not results_dir.exists():
        return [], 0

    entries = []
    dirs_to_scan = [results_dir / ticker] if ticker else sorted(results_dir.iterdir())

    for td in dirs_to_scan:
        if not td.is_dir():
            continue
        logs_dir = td / "TradingAgentsStrategy_logs"
        if not logs_dir.exists():
            continue
        for log_file in sorted(logs_dir.glob("full_states_log_*.json"), reverse=True):
            date_str = log_file.stem.replace("full_states_log_", "")
            entries.append({
                "ticker": td.name,
                "date": date_str,
            })

    total = len(entries)
    page = entries[offset:offset + limit]

    # Enhance with memory log data (ratings, returns)
    _enhance_with_memory(page)

    return page, total


def _enhance_with_memory(entries: list[dict]) -> None:
    """Add rating and return data from the memory log to history entries."""
    try:
        mem = TradingMemoryLog(DEFAULT_CONFIG)
        mem_entries = mem.load_entries()
    except Exception:
        return

    by_key = {}
    for e in mem_entries:
        key = (e.get("ticker", "").upper(), e.get("date", ""))
        by_key[key] = e

    for entry in entries:
        key = (entry["ticker"].upper(), entry["date"])
        mem_entry = by_key.get(key)
        if mem_entry:
            entry["rating"] = mem_entry.get("rating")
            entry["raw_return"] = mem_entry.get("raw")
            entry["alpha_return"] = mem_entry.get("alpha")
            entry["holding_days"] = mem_entry.get("holding")
            entry["pending"] = mem_entry.get("pending", False)


def get_analysis_state(ticker: str, date: str) -> dict:
    """Read and return the full JSON state for a specific ticker+date."""
    from tradingagents.dataflows.utils import safe_ticker_component

    safe = safe_ticker_component(ticker)
    results_dir = Path(DEFAULT_CONFIG["results_dir"])
    log_path = results_dir / safe / "TradingAgentsStrategy_logs" / f"full_states_log_{date}.json"

    if not log_path.exists():
        raise FileNotFoundError(f"No log found for {ticker} on {date}")

    with open(log_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ticker_summary(ticker: str) -> dict | None:
    """Get a summary of all analyses for a ticker."""
    from tradingagents.dataflows.utils import safe_ticker_component

    try:
        safe = safe_ticker_component(ticker)
    except ValueError:
        return None

    results_dir = Path(DEFAULT_CONFIG["results_dir"]) / safe / "TradingAgentsStrategy_logs"
    if not results_dir.exists():
        return None

    analyses = sorted(results_dir.glob("full_states_log_*.json"))
    if not analyses:
        return None

    return {
        "ticker": safe,
        "total_analyses": len(analyses),
        "latest_date": analyses[-1].stem.replace("full_states_log_", ""),
        "dates": sorted([f.stem.replace("full_states_log_", "") for f in analyses]),
    }

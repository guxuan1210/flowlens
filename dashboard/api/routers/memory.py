"""Router for trading memory log."""

from fastapi import APIRouter, Query

from tradingagents.agents.utils.memory import TradingMemoryLog
from tradingagents.default_config import DEFAULT_CONFIG

router = APIRouter(tags=["memory"])


def _get_memory_log() -> TradingMemoryLog:
    return TradingMemoryLog(DEFAULT_CONFIG)


@router.get("/memory")
async def get_memory(limit: int = Query(default=50, ge=1, le=500), offset: int = Query(default=0, ge=0)):
    """Return all trading memory entries with pagination."""
    mem = _get_memory_log()
    entries = mem.load_entries()
    total = len(entries)
    page = entries[offset:offset + limit]
    return {"entries": page, "total": total, "limit": limit, "offset": offset}


@router.get("/memory/{ticker}")
async def get_memory_for_ticker(ticker: str):
    """Return trading memory entries for a specific ticker."""
    mem = _get_memory_log()
    all_entries = mem.load_entries()
    entries = [e for e in all_entries if e.get("ticker", "").upper() == ticker.upper()]
    pending = [e for e in entries if e.get("pending")]
    resolved = [e for e in entries if not e.get("pending")]
    return {
        "ticker": ticker.upper(),
        "total": len(entries),
        "pending": pending,
        "resolved": resolved,
    }

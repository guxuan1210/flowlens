"""Router for analysis history browsing."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from dashboard.api.services.history_service import list_all_analyses, get_analysis_state, get_ticker_summary

router = APIRouter(tags=["history"])


@router.get("/history")
async def get_history(
    ticker: str | None = Query(default=None, description="Filter by ticker"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List all past analyses with optional ticker filter."""
    entries, total = list_all_analyses(ticker=ticker, limit=limit, offset=offset)
    return {"entries": entries, "total": total, "limit": limit, "offset": offset}


@router.get("/history/{ticker}")
async def get_ticker_summaries(ticker: str):
    """Get summary of all analyses for a ticker."""
    summary = get_ticker_summary(ticker)
    if not summary:
        raise HTTPException(status_code=404, detail=f"No analyses found for {ticker}")
    return summary


@router.get("/history/{ticker}/{date}")
async def get_history_detail(ticker: str, date: str):
    """Return full analysis state for a specific ticker+date."""
    try:
        state = get_analysis_state(ticker, date)
        return state
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No analysis found for {ticker} on {date}")


@router.get("/history/compare")
async def compare_analyses(tickers: str = Query(...), dates: str | None = Query(default=None)):
    """Side-by-side comparison of multiple tickers/dates.

    Query params: tickers=AAPL,MSFT  dates=2026-01-15,2026-01-15 (optional: defaults to latest for each ticker)
    """
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    date_list = [d.strip() for d in dates.split(",")] if dates else []

    results = {}
    for i, t in enumerate(ticker_list):
        try:
            date = date_list[i] if i < len(date_list) else None
            if date:
                state = get_analysis_state(t, date)
                results[t] = {"date": date, "state": state}
            else:
                entries, _ = list_all_analyses(ticker=t, limit=1, offset=0)
                if entries:
                    state = get_analysis_state(t, entries[0]["date"])
                    results[t] = {"date": entries[0]["date"], "state": state}
        except FileNotFoundError:
            results[t] = {"date": None, "state": None, "error": "No analysis found"}

    return results

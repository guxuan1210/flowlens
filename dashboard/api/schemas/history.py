"""Pydantic schemas for history browsing."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class HistoryEntry(BaseModel):
    ticker: str
    date: str
    rating: Optional[str] = None
    raw_return: Optional[str] = None
    alpha_return: Optional[str] = None
    holding_days: Optional[str] = None
    pending: bool = False


class HistoryListResponse(BaseModel):
    entries: list[HistoryEntry]
    total: int
    limit: int
    offset: int


class TickerSummary(BaseModel):
    ticker: str
    total_analyses: int
    latest_date: Optional[str] = None
    latest_rating: Optional[str] = None


class CompareRequest(BaseModel):
    tickers: list[str]
    dates: Optional[list[str]] = None

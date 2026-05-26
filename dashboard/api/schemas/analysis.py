"""Pydantic schemas for analysis request/response."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class AnalysisRunRequest(BaseModel):
    ticker: str = Field(..., max_length=32, description="Ticker symbol, e.g. AAPL, 7203.T")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Analysis date YYYY-MM-DD")
    analysts: list[str] = Field(
        default=["market", "social", "news", "fundamentals"],
        description="Selected analyst types",
    )
    research_depth: int = Field(default=1, ge=1, le=5)
    llm_provider: str = Field(default="openai")
    quick_think_llm: str = Field(default="gpt-5.4-mini")
    deep_think_llm: str = Field(default="gpt-5.4")
    backend_url: Optional[str] = None
    output_language: str = Field(default="English")
    # Provider-specific thinking config
    google_thinking_level: Optional[str] = None
    openai_reasoning_effort: Optional[str] = None
    anthropic_effort: Optional[str] = None
    # Human-in-the-loop review
    enable_human_review: bool = False
    human_review_points: list[str] = Field(default=["research_manager", "portfolio_manager"])


class AnalysisRunResponse(BaseModel):
    run_id: str
    ws_url: str
    status_url: str


class AnalysisStatusResponse(BaseModel):
    run_id: str
    status: str  # "running" | "completed" | "error" | "waiting_review"
    agent_statuses: dict[str, str] = Field(default_factory=dict)
    stats: Optional[dict] = None
    report_sections: dict[str, str] = Field(default_factory=dict)
    final_decision: Optional[str] = None
    error: Optional[str] = None
    review_point: Optional[str] = None  # "research_manager" | "portfolio_manager" when waiting


class HumanReviewRequest(BaseModel):
    """Human submits review feedback to resume a paused analysis."""
    action: str = Field(..., description="'approve' or 'revise'")
    feedback: str = Field(default="", description="Human feedback text")
    rating_override: Optional[str] = Field(default=None, description="Optional rating override")

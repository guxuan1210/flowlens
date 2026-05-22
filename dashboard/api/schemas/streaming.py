"""WebSocket message schemas for real-time agent progress streaming."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WSMessageType(str, Enum):
    AGENT_STATUS = "agent_status"
    REPORT_CHUNK = "report_chunk"
    STATS = "stats"
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    COMPLETION = "completion"
    ERROR = "error"
    PIPELINE_STAGE = "pipeline_stage"


class AgentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class AgentStatusPayload(BaseModel):
    agent: str = Field(..., description="Agent name, e.g. 'Market Analyst'")
    status: AgentStatus


class ReportChunkPayload(BaseModel):
    section: str = Field(..., description="Report section key, e.g. 'market_report'")
    content: str


class StatsPayload(BaseModel):
    llm_calls: int
    tool_calls: int
    tokens_in: int
    tokens_out: int
    elapsed_seconds: float


class CompletionPayload(BaseModel):
    final_decision: str
    rating: str
    ticker: str
    date: str


class ErrorPayload(BaseModel):
    message: str
    agent: Optional[str] = None


class WSMessage(BaseModel):
    type: WSMessageType
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: dict

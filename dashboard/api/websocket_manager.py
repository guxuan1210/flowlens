"""WebSocket connection manager for analysis streaming."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from fastapi import WebSocket

from dashboard.api.schemas.streaming import WSMessageType


class ConnectionManager:
    """Track WebSocket connections per run_id and fan out messages."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}
        self._agent_statuses: dict[str, dict[str, str]] = {}
        self._report_sections: dict[str, dict[str, str]] = {}
        self._stats_cache: dict[str, dict] = {}

    async def connect(self, run_id: str, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(run_id, []).append(ws)
        # Send cached state so late-connecting clients catch up
        if run_id in self._agent_statuses:
            for agent, status in self._agent_statuses[run_id].items():
                await self._send(ws, WSMessageType.AGENT_STATUS, {"agent": agent, "status": status})
        if run_id in self._report_sections:
            for section, content in self._report_sections[run_id].items():
                await self._send(ws, WSMessageType.REPORT_CHUNK, {"section": section, "content": content})
        if run_id in self._stats_cache:
            await self._send(ws, WSMessageType.STATS, self._stats_cache[run_id])
        # Send cached pipeline stage for late-joining clients
        stage = self.get_pipeline_stage(run_id)
        if stage:
            await self._send(ws, WSMessageType.PIPELINE_STAGE, {"stage": stage})

    def disconnect(self, run_id: str, ws: WebSocket):
        if run_id in self._connections:
            self._connections[run_id] = [c for c in self._connections.get(run_id, []) if c != ws]

    async def _send(self, ws: WebSocket, msg_type: WSMessageType, payload: dict):
        try:
            await ws.send_json({"type": msg_type.value, "timestamp": datetime.utcnow().isoformat(), "payload": payload})
        except Exception:
            pass

    async def broadcast(self, run_id: str, msg_type: WSMessageType, payload: dict):
        """Send a JSON message to all clients watching this run_id. Caches state."""
        if run_id not in self._connections:
            return
        # Cache for late joiners
        if msg_type == WSMessageType.AGENT_STATUS:
            self._agent_statuses.setdefault(run_id, {})[payload["agent"]] = payload["status"]
        elif msg_type == WSMessageType.REPORT_CHUNK:
            self._report_sections.setdefault(run_id, {})[payload["section"]] = payload["content"]
        elif msg_type == WSMessageType.STATS:
            self._stats_cache[run_id] = payload

        dead = []
        for ws in self._connections[run_id]:
            try:
                await ws.send_json({"type": msg_type.value, "timestamp": datetime.utcnow().isoformat(), "payload": payload})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(run_id, ws)

    async def send_agent_status(self, run_id: str, agent: str, status: str):
        await self.broadcast(run_id, WSMessageType.AGENT_STATUS, {"agent": agent, "status": status})

    async def send_report_chunk(self, run_id: str, section: str, content: str):
        await self.broadcast(run_id, WSMessageType.REPORT_CHUNK, {"section": section, "content": content})

    async def send_stats(self, run_id: str, stats: dict, elapsed: float):
        await self.broadcast(run_id, WSMessageType.STATS, {
            "llm_calls": stats.get("llm_calls", 0),
            "tool_calls": stats.get("tool_calls", 0),
            "tokens_in": stats.get("tokens_in", 0),
            "tokens_out": stats.get("tokens_out", 0),
            "elapsed_seconds": elapsed,
        })

    async def send_completion(self, run_id: str, final_decision: str, rating: str, ticker: str, date: str):
        await self.broadcast(run_id, WSMessageType.COMPLETION, {
            "final_decision": final_decision,
            "rating": rating,
            "ticker": ticker,
            "date": date,
        })

    async def send_error(self, run_id: str, message: str, agent: str | None = None):
        payload: dict = {"message": message}
        if agent:
            payload["agent"] = agent
        await self.broadcast(run_id, WSMessageType.ERROR, payload)

    async def send_pipeline_stage(self, run_id: str, stage: str):
        """Send pipeline stage to all clients with caching for late joiners."""
        if run_id in self._stats_cache:
            self._stats_cache[run_id]["pipeline_stage"] = stage
        else:
            self._stats_cache[run_id] = {"pipeline_stage": stage}
        await self.broadcast(run_id, WSMessageType.PIPELINE_STAGE, {"stage": stage})

    def get_pipeline_stage(self, run_id: str) -> str | None:
        """Return cached pipeline stage for late-joining clients."""
        cache = self._stats_cache.get(run_id, {})
        return cache.get("pipeline_stage")

    async def send_tool_call(self, run_id: str, tool_name: str, args: dict):
        await self.broadcast(run_id, WSMessageType.TOOL_CALL, {"tool_name": tool_name, "args": str(args)})

    async def send_human_review_required(self, run_id: str, review_point: str, ticker: str, data: dict):
        """Send human review request to frontend and cache review state."""
        await self.broadcast(run_id, WSMessageType.HUMAN_REVIEW_REQUIRED, {
            "review_point": review_point,
            "ticker": ticker,
            "data": data,
        })

    def cleanup(self, run_id: str):
        self._connections.pop(run_id, None)
        self._agent_statuses.pop(run_id, None)
        self._report_sections.pop(run_id, None)
        self._stats_cache.pop(run_id, None)

    async def shutdown(self):
        for run_id, clients in list(self._connections.items()):
            for ws in clients:
                try:
                    await ws.close()
                except Exception:
                    pass
            self.cleanup(run_id)


manager = ConnectionManager()

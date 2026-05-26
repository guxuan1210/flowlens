"""Router for analysis execution and WebSocket streaming."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from dashboard.api.schemas.analysis import AnalysisRunRequest, AnalysisRunResponse, HumanReviewRequest
from dashboard.api.services.analysis_runner import (
    run_analysis_background,
    get_run_status,
    stop_run,
    get_running_runs,
    submit_review,
)
from dashboard.api.websocket_manager import manager

router = APIRouter(tags=["analysis"])


@router.post("/analysis/run", response_model=AnalysisRunResponse)
async def start_analysis(body: AnalysisRunRequest):
    """Start a new analysis. Returns immediately with run_id and WS URL."""
    run_id = uuid.uuid4().hex[:12]
    params = body.model_dump()

    import asyncio
    asyncio.create_task(run_analysis_background(run_id, params))

    return AnalysisRunResponse(
        run_id=run_id,
        ws_url=f"/api/analysis/ws/{run_id}",
        status_url=f"/api/analysis/status/{run_id}",
    )


@router.get("/analysis/status/{run_id}")
async def get_status(run_id: str):
    """Poll current status of a running or completed analysis."""
    status = get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return status


@router.post("/analysis/stop/{run_id}")
async def stop_analysis(run_id: str):
    """Stop a running analysis."""
    if stop_run(run_id):
        return {"status": "ok", "message": f"Stop signal sent for {run_id}"}
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found or already completed")


@router.get("/analysis/running")
async def list_running():
    """List all currently running analyses."""
    return {"runs": get_running_runs()}


@router.post("/analysis/{run_id}/review")
async def submit_human_review(run_id: str, review: HumanReviewRequest):
    """Submit human review feedback and resume a paused analysis."""
    ok = submit_review(run_id, review.model_dump())
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found or not waiting for review",
        )
    return {"status": "ok", "message": f"Review submitted for {run_id}, resuming analysis"}


@router.websocket("/analysis/ws/{run_id}")
async def analysis_websocket(ws: WebSocket, run_id: str):
    """WebSocket endpoint for real-time analysis progress."""
    await manager.connect(run_id, ws)
    try:
        while True:
            # Keep connection alive, listen for client messages (e.g., ping/stop)
            data = await ws.receive_text()
            if data == "stop":
                stop_run(run_id)
                break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(run_id, ws)

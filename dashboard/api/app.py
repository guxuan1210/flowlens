"""FastAPI application entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tradingagents.default_config import DEFAULT_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure required directories exist. Shutdown: clean up WS connections."""
    os.makedirs(DEFAULT_CONFIG["results_dir"], exist_ok=True)
    os.makedirs(DEFAULT_CONFIG["data_cache_dir"], exist_ok=True)
    memory_log = DEFAULT_CONFIG.get("memory_log_path")
    if memory_log:
        os.makedirs(os.path.dirname(memory_log), exist_ok=True)
    yield
    from dashboard.api.websocket_manager import manager
    await manager.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="TradingAgents Dashboard API",
        version="0.2.5",
        description="REST and WebSocket API for the TradingAgents Web Dashboard",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from dashboard.api.routers import analysis, history, config, models, memory
    app.include_router(analysis.router, prefix="/api")
    app.include_router(history.router, prefix="/api")
    app.include_router(config.router, prefix="/api")
    app.include_router(models.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")

    return app


app = create_app()


def run():
    """Entry point: `tradingagents-dashboard` or `python -m dashboard.api.app`"""
    import uvicorn
    uvicorn.run("dashboard.api.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()

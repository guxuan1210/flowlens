"""Async wrapper around TradingAgentsGraph for WebSocket streaming.

Runs the synchronous LangGraph in a background thread and pushes agent
progress, report chunks, and stats through the WebSocket connection manager.
"""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from typing import Any

from cli.stats_handler import StatsCallbackHandler
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.graph.analyst_execution import (
    AnalystWallTimeTracker,
    build_analyst_execution_plan,
    get_initial_analyst_node,
    sync_analyst_tracker_from_chunk,
)
from dashboard.api.websocket_manager import manager

_active_runs: dict[str, dict[str, Any]] = {}

ANALYST_ORDER = ["market", "social", "news", "fundamentals", "capital_flow"]

ANALYST_AGENT_NAMES = {
    "market": "Market Analyst",
    "social": "Sentiment Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
    "capital_flow": "Capital Flow Analyst",
}

ANALYST_REPORT_MAP = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
    "capital_flow": "capital_flow_report",
    "manipulation": "manipulation_risk_report",
}

FIXED_AGENTS = [
    "Bull Researcher", "Bear Researcher", "Research Manager",
    "Trader",
    "Aggressive Analyst", "Neutral Analyst", "Conservative Analyst",
    "Portfolio Manager", "Manipulation Risk Analyzer",
]


def _init_agent_statuses(selected_analysts: list[str]) -> dict[str, str]:
    """Build initial agent_statuses dict."""
    statuses = {}
    for key in selected_analysts:
        name = ANALYST_AGENT_NAMES.get(key)
        if name:
            statuses[name] = "pending"
    for name in FIXED_AGENTS:
        statuses[name] = "pending"
    return statuses


async def run_analysis_background(run_id: str, params: dict) -> None:
    """Run analysis in a thread, streaming results via WebSocket."""
    stop_event = threading.Event()
    _active_runs[run_id] = {"stop_event": stop_event, "status": "running", "params": params}
    loop = asyncio.get_running_loop()

    try:
        # Build config from params
        from tradingagents.default_config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = params["research_depth"]
        config["max_risk_discuss_rounds"] = params["research_depth"]
        config["quick_think_llm"] = params["quick_think_llm"]
        config["deep_think_llm"] = params["deep_think_llm"]
        config["llm_provider"] = params["llm_provider"]
        config["output_language"] = params.get("output_language", "English")
        if params.get("backend_url"):
            config["backend_url"] = params["backend_url"]
        for key in ("google_thinking_level", "openai_reasoning_effort", "anthropic_effort"):
            if params.get(key) is not None:
                config[key] = params[key]

        stats_handler = StatsCallbackHandler()

        selected_analyst_keys = [a for a in ANALYST_ORDER if a in params.get("analysts", ANALYST_ORDER)]
        analyst_execution_plan = build_analyst_execution_plan(
            selected_analyst_keys,
            concurrency_limit=config.get("analyst_concurrency_limit", 1),
        )
        wall_time_tracker = AnalystWallTimeTracker(analyst_execution_plan)

        # Initialize agent statuses
        agent_statuses = _init_agent_statuses(selected_analyst_keys)
        for agent, status in agent_statuses.items():
            await manager.send_agent_status(run_id, agent, status)

        # Set first analyst to in_progress
        first_analyst = get_initial_analyst_node(analyst_execution_plan)
        await manager.send_agent_status(run_id, first_analyst, "in_progress")
        wall_time_tracker.mark_started(selected_analyst_keys[0])

        # Create graph in thread (blocking LLM client init)
        graph = await loop.run_in_executor(
            None,
            lambda: TradingAgentsGraph(
                selected_analyst_keys,
                config=config,
                debug=True,
                callbacks=[stats_handler],
            ),
        )

        start_time = time.time()

        def stream_graph():
            """Run graph.stream() in this thread, pushing messages to the event loop."""
            init_state = graph.propagator.create_initial_state(
                params["ticker"], params["date"],
                asset_type=params.get("asset_type", "stock"),
            )
            args = graph.propagator.get_graph_args()

            trace = []
            try:
                for chunk in graph.graph.stream(init_state, **args):
                    if stop_event.is_set():
                        asyncio.run_coroutine_threadsafe(
                            manager.send_error(run_id, "Analysis stopped by user"), loop
                        )
                        return

                    trace.append(chunk)
                    _handle_chunk(
                        chunk, run_id, selected_analyst_keys, stats_handler,
                        start_time, agent_statuses, wall_time_tracker, loop
                    )
            except Exception as exc:
                asyncio.run_coroutine_threadsafe(
                    manager.send_error(run_id, str(exc)), loop
                )
                return

            # Merge deltas into final state
            final_state: dict = {}
            for c in trace:
                final_state.update(c)

            # Persist state to disk (same as TradingAgentsGraph._run_graph does).
            graph.ticker = params["ticker"]
            graph._log_state(str(params["date"]), final_state)
            graph.memory_log.store_decision(
                ticker=params["ticker"],
                trade_date=str(params["date"]),
                final_trade_decision=final_state.get("final_trade_decision", ""),
            )

            decision = graph.process_signal(final_state.get("final_trade_decision", ""))
            rating = decision  # process_signal returns the rating string directly

            # Mark all agents completed
            for agent in agent_statuses:
                agent_statuses[agent] = "completed"
                asyncio.run_coroutine_threadsafe(
                    manager.send_agent_status(run_id, agent, "completed"), loop
                )

            asyncio.run_coroutine_threadsafe(
                manager.send_completion(
                    run_id,
                    final_decision=final_state.get("final_trade_decision", ""),
                    rating=rating,
                    ticker=params["ticker"],
                    date=params["date"],
                ),
                loop,
            )

        thread = threading.Thread(target=stream_graph, daemon=True)
        _active_runs[run_id]["thread"] = thread
        thread.start()

    except Exception as exc:
        await manager.send_error(run_id, str(exc))
        raise
    finally:
        _active_runs.pop(run_id, None)


def _handle_chunk(
    chunk: dict,
    run_id: str,
    selected_analysts: list[str],
    stats_handler: StatsCallbackHandler,
    start_time: float,
    agent_statuses: dict[str, str],
    wall_time_tracker: AnalystWallTimeTracker,
    loop: asyncio.AbstractEventLoop,
):
    """Process a single graph.stream() chunk and emit WS messages.

    Runs in the background thread. Uses asyncio.run_coroutine_threadsafe to send WS messages.
    """
    # 1. Sync wall time tracker
    sync_analyst_tracker_from_chunk(wall_time_tracker, chunk)

    # Pipeline stage tracking
    if not agent_statuses.get("_pipeline_analysts_sent"):
        agent_statuses["_pipeline_analysts_sent"] = True
        asyncio.run_coroutine_threadsafe(
            manager.send_pipeline_stage(run_id, "analysts"), loop
        )

    # 2. Analyst report updates
    found_active = False
    for analyst_key in ANALYST_ORDER:
        if analyst_key not in selected_analysts:
            continue

        agent_name = ANALYST_AGENT_NAMES[analyst_key]
        report_key = ANALYST_REPORT_MAP[analyst_key]

        if chunk.get(report_key):
            content = chunk[report_key]
            if isinstance(content, str) and content.strip():
                asyncio.run_coroutine_threadsafe(
                    manager.send_report_chunk(run_id, report_key, content), loop
                )
                asyncio.run_coroutine_threadsafe(
                    manager.send_agent_status(run_id, agent_name, "completed"), loop
                )
                agent_statuses[agent_name] = "completed"
            continue

        if agent_statuses.get(agent_name) != "completed" and not found_active:
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, agent_name, "in_progress"), loop
            )
            agent_statuses[agent_name] = "in_progress"
            found_active = True

    # 3. All analysts done → transition Bull Researcher
    if not found_active and selected_analysts:
        if agent_statuses.get("Bull Researcher") == "pending":
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, "Bull Researcher", "in_progress"), loop
            )
            agent_statuses["Bull Researcher"] = "in_progress"
            # Signal research stage
            if not agent_statuses.get("_pipeline_research_sent"):
                agent_statuses["_pipeline_research_sent"] = True
                asyncio.run_coroutine_threadsafe(
                    manager.send_pipeline_stage(run_id, "research"), loop
                )

    # 4. Investment debate state
    if chunk.get("investment_debate_state"):
        debate = chunk["investment_debate_state"]
        bull = debate.get("bull_history", "")
        bear = debate.get("bear_history", "")
        judge = debate.get("judge_decision", "")

        if bull or bear:
            for a in ["Bull Researcher", "Bear Researcher", "Research Manager"]:
                agent_statuses[a] = "in_progress"
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, "Bull Researcher", "in_progress"), loop
            )
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, "Bear Researcher", "in_progress"), loop
            )

        if bull:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "investment_debate_bull", bull), loop
            )
        if bear:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "investment_debate_bear", bear), loop
            )
        if judge:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "investment_plan", judge), loop
            )
            for a in ["Bull Researcher", "Bear Researcher", "Research Manager"]:
                agent_statuses[a] = "completed"
                asyncio.run_coroutine_threadsafe(
                    manager.send_agent_status(run_id, a, "completed"), loop
                )
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, "Trader", "in_progress"), loop
            )
            agent_statuses["Trader"] = "in_progress"
            # Signal trader stage
            if not agent_statuses.get("_pipeline_trader_sent"):
                agent_statuses["_pipeline_trader_sent"] = True
                asyncio.run_coroutine_threadsafe(
                    manager.send_pipeline_stage(run_id, "trader"), loop
                )

    # 5. Trader plan
    if chunk.get("trader_investment_plan"):
        content = chunk["trader_investment_plan"]
        asyncio.run_coroutine_threadsafe(
            manager.send_report_chunk(run_id, "trader_investment_plan", content), loop
        )
        agent_statuses["Trader"] = "completed"
        asyncio.run_coroutine_threadsafe(
            manager.send_agent_status(run_id, "Trader", "completed"), loop
        )
        agent_statuses["Aggressive Analyst"] = "in_progress"
        asyncio.run_coroutine_threadsafe(
            manager.send_agent_status(run_id, "Aggressive Analyst", "in_progress"), loop
        )
        # Signal risk stage
        if not agent_statuses.get("_pipeline_risk_sent"):
            agent_statuses["_pipeline_risk_sent"] = True
            asyncio.run_coroutine_threadsafe(
                manager.send_pipeline_stage(run_id, "risk"), loop
            )

    # 6. Risk debate state
    if chunk.get("risk_debate_state"):
        risk = chunk["risk_debate_state"]
        agg = risk.get("aggressive_history", "")
        con = risk.get("conservative_history", "")
        neu = risk.get("neutral_history", "")
        judge = risk.get("judge_decision", "")

        if agg:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "risk_aggressive", agg), loop
            )
        if con:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "risk_conservative", con), loop
            )
        if neu:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "risk_neutral", neu), loop
            )
        if judge:
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "final_trade_decision", judge), loop
            )
            for a in ["Aggressive Analyst", "Conservative Analyst", "Neutral Analyst", "Portfolio Manager"]:
                agent_statuses[a] = "completed"
                asyncio.run_coroutine_threadsafe(
                    manager.send_agent_status(run_id, a, "completed"), loop
                )
            # Signal decision stage
            if not agent_statuses.get("_pipeline_decision_sent"):
                agent_statuses["_pipeline_decision_sent"] = True
                asyncio.run_coroutine_threadsafe(
                    manager.send_pipeline_stage(run_id, "decision"), loop
                )
            # Transition to Manipulation Risk Analyzer
            if agent_statuses.get("Manipulation Risk Analyzer") == "pending":
                agent_statuses["Manipulation Risk Analyzer"] = "in_progress"
                asyncio.run_coroutine_threadsafe(
                    manager.send_agent_status(run_id, "Manipulation Risk Analyzer", "in_progress"), loop
                )

    # 7. Manipulation Risk Report
    if chunk.get("manipulation_risk_report"):
        content = chunk["manipulation_risk_report"]
        if isinstance(content, str) and content.strip():
            asyncio.run_coroutine_threadsafe(
                manager.send_report_chunk(run_id, "manipulation_risk_report", content), loop
            )
            asyncio.run_coroutine_threadsafe(
                manager.send_agent_status(run_id, "Manipulation Risk Analyzer", "completed"), loop
            )
            agent_statuses["Manipulation Risk Analyzer"] = "completed"
            if not agent_statuses.get("_pipeline_manipulation_sent"):
                agent_statuses["_pipeline_manipulation_sent"] = True
                asyncio.run_coroutine_threadsafe(
                    manager.send_pipeline_stage(run_id, "manipulation"), loop
                )

    # 8. Emit stats
    stats = stats_handler.get_stats()
    elapsed = time.time() - start_time
    asyncio.run_coroutine_threadsafe(
        manager.send_stats(run_id, stats, elapsed), loop
    )


def get_run_status(run_id: str) -> dict | None:
    """Get current status of a running analysis."""
    run = _active_runs.get(run_id)
    if not run:
        return None
    return {
        "run_id": run_id,
        "status": run.get("status", "unknown"),
        "params": {k: v for k, v in run.get("params", {}).items() if k not in ("api_key",)},
    }


def stop_run(run_id: str) -> bool:
    """Signal a running analysis to stop."""
    run = _active_runs.get(run_id)
    if not run:
        return False
    event = run.get("stop_event")
    if event:
        event.set()
        run["status"] = "stopping"
        return True
    return False


def get_running_runs() -> list[dict]:
    """List all currently running analyses."""
    return [
        {"run_id": rid, "status": r.get("status", "unknown"),
         "ticker": r.get("params", {}).get("ticker", ""),
         "date": r.get("params", {}).get("date", "")}
        for rid, r in _active_runs.items()
    ]

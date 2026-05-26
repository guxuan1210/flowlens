# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in dev mode
pip install -e .

# Run the interactive CLI
tradingagents                  # installed entry point
python -m cli.main             # direct from source
tradingagents analyze          # skip wizard, go straight to analysis
tradingagents analyze --checkpoint         # enable LangGraph checkpoint resume
tradingagents analyze --clear-checkpoints  # wipe all checkpoints before running

# Run a single ticker programmatically
python main.py

# Tests
pytest                           # all tests
pytest -m unit                   # unit tests only (no network/API keys needed)
pytest -m integration            # integration tests (need real API keys)
pytest -m smoke                  # quick sanity checks
pytest tests/test_memory_log.py  # single test file

# Docker
cp .env.example .env             # add API keys first
docker compose run --rm tradingagents
docker compose --profile ollama run --rm tradingagents-ollama
```

## Architecture

TradingAgents is a LangGraph-based multi-agent trading simulation. A single `TradingAgentsGraph` object orchestrates a `StateGraph` that chains LLM-powered agents through a fixed pipeline:

```
Analysts (market → sentiment → news → fundamentals, each with tool-call loops)
  → Bull Researcher ⇄ Bear Researcher (structured debate with N rounds)
    → Research Manager (deep LLM, synthesizes debate → Pydantic ResearchPlan)
      → Trader (quick LLM → Pydantic TraderProposal)
        → Aggressive ⇄ Conservative ⇄ Neutral risk analysts (N-round debate)
          → Portfolio Manager (deep LLM → Pydantic PortfolioDecision)
```

### Key layers

**`tradingagents/graph/`** — LangGraph orchestration. `TradingAgentsGraph` is the main entry point; `GraphSetup.setup_graph()` builds the `StateGraph` with conditional edges for tool loops and debate rounds. `ConditionalLogic` controls when tool loops end and how many debate rounds happen (`max_debate_rounds`, `max_risk_discuss_rounds`). `Propagator` initializes the `AgentState` typed dict. `Reflector` generates post-trade self-critiques for the persistent memory log. `SignalProcessor` extracts the final Buy/Overweight/Hold/Underweight/Sell rating from the Portfolio Manager's markdown output.

**`tradingagents/agents/`** — Each agent is a factory function returning a callable node. Analysts (`market_analyst`, `sentiment_analyst`, `news_analyst`, `fundamentals_analyst`) use `quick_thinking_llm` and call tools. Researchers (`bull_researcher`, `bear_researcher`) debate each other. `research_manager` and `portfolio_manager` use `deep_thinking_llm` and produce structured Pydantic output (`ResearchPlan`, `PortfolioDecision`). `trader` produces a `TraderProposal`. `agents/utils/agent_utils.py` defines the 8 `@tool`-decorated functions (get_stock_data, get_indicators, get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_news, get_insider_transactions, get_global_news) that are wrapped into `ToolNode`s by `_create_tool_nodes()`.

**`tradingagents/dataflows/`** — Multi-vendor data abstraction. `interface.py` maps tool names to vendor implementations and routes with automatic fallback (e.g., yfinance fails → Alpha Vantage on rate-limit). Configurable per category (`data_vendors`) or per tool (`tool_vendors`). `config.py` holds runtime mutable config via `set_config()`/`get_config()`.

**`tradingagents/llm_clients/`** — `factory.py` dispatches provider strings to client classes. OpenAI, xAI, DeepSeek, Qwen, GLM, MiniMax, Ollama, and OpenRouter all go through `OpenAIClient` (OpenAI-compatible API). Anthropic, Google, and Azure have dedicated clients. Each client wraps its provider's SDK and exposes a `.get_llm()` method. `model_catalog.py` lists available models per provider.

**`cli/`** — Rich-based TUI. `main.py` is a Typer app with a questionary-driven wizard (ticker → date → language → analysts → depth → provider → models → thinking config). `run_analysis()` streams LangGraph chunks, updating agent statuses and report sections in a `Live` layout. `MessageBuffer` tracks per-agent progress and accumulates report sections. `save_report_to_disk()` writes organized markdown reports.

### Configuration

`tradingagents/default_config.py` defines `DEFAULT_CONFIG` — the single source of truth. Any `TRADINGAGENTS_*` environment variable automatically overrides its matching config key (see `_ENV_OVERRIDES` dict). Key config values:

- `llm_provider`, `deep_think_llm`, `quick_think_llm` — model selection
- `backend_url` — API endpoint override (None = provider default)
- `max_debate_rounds`, `max_risk_discuss_rounds` — debate depth
- `data_vendors` / `tool_vendors` — which data source per category/tool
- `benchmark_map` — per-exchange benchmark tickers for alpha calculation
- `checkpoint_enabled` — opt-in LangGraph SQLite checkpoint/resume

### Persistent state

- **Decision log**: `~/.tradingagents/memory/trading_memory.md` (override with `TRADINGAGENTS_MEMORY_LOG_PATH`). Append-only markdown. Pending entries resolve on the next same-ticker run (Phase B: fetch returns, generate reflection, update tag). Past context is injected into the Portfolio Manager prompt.
- **Checkpoints**: Per-ticker SQLite DBs at `~/.tradingagents/cache/checkpoints/<TICKER>.db`. Opt-in via `--checkpoint` or `checkpoint_enabled=True`. Cleared on successful completion.
- **Results**: JSON state logs saved to `~/.tradingagents/logs/<TICKER>/TradingAgentsStrategy_logs/`.

### Path safety

`safe_ticker_component()` in `dataflows/utils.py` validates ticker values before interpolating them into filesystem paths. Any value containing slashes, backslashes, or non-ticker characters is rejected to prevent path traversal.

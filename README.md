<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---

# FlowLens: Capital-Flow-Aware Multi-Agent Market Intelligence

> Helping retail investors interpret market narratives, risk signals, and dominant capital movement through multi-agent reasoning.
>
> 🚀 **Web Dashboard** now available with real-time analysis streaming, human-in-the-loop review, and one-click configuration.

## News
- [2026-05] **Web Dashboard** released with React + FastAPI stack, real-time WebSocket streaming, human-in-the-loop review gates, East Money (东方财富) news integration, and Capital Flow Analyst. See [CHANGELOG.md](CHANGELOG.md).
- [2026-05] **TradingAgents v0.2.5** released with the grounded Sentiment Analyst, GPT-5.5 etc. model coverage, Qwen/GLM/MiniMax dual-region support, `TRADINGAGENTS_*` env-var configurability with API-key auto-detection, remote Ollama support, non-US alpha benchmarks, and ticker path-traversal hardening.
- [2026-04] **TradingAgents v0.2.4** released with structured-output agents (Research Manager, Trader, Portfolio Manager), LangGraph checkpoint resume, persistent decision log, DeepSeek/Qwen/GLM/Azure provider support, and Docker.
- [2026-03] **TradingAgents v0.2.3** released with multi-language support, GPT-5.4 family models, unified model catalog, backtesting date fidelity, and proxy support.

<div align="center">

🚀 [Motivation](#motivation-from-institutional-ai-to-retail-oriented-market-intelligence) | ⚡ [Installation & CLI](#installation-and-cli) | 🖥️ [Web Dashboard](#web-dashboard) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>

## Motivation: From Institutional AI to Retail-Oriented Market Intelligence

Most financial AI agents are designed around institutional workflows: reading financial reports, summarizing market news, generating investment theses, and supporting portfolio decisions. While these capabilities are valuable, they mainly improve the decision-making efficiency of already resource-rich market participants.

FlowLens takes a slightly different perspective. Instead of only building an AI assistant for institutional-style decision making, it aims to make institutional-level market intelligence more accessible and interpretable for retail investors.

In markets such as China A-shares, retail investors often face strong information asymmetry. Public news, price charts, and financial statements are important, but they may not fully reveal how capital is actually moving behind market trends. For retail investors, one of the most important questions is not only "Is this company good?" or "What does the news say?", but also:

> Are major market players accumulating or exiting this position?

This is why FlowLens introduces a dedicated **Capital Flow Analyst**. Rather than directly inferring institutional investors' internal decision-making process, which is usually opaque and difficult to verify, the system uses observable capital-flow signals as behavioral proxies. These include major capital inflows and outflows, large-order and extra-large-order net flows, sector-level fund rotation, and north-bound capital movement.

By integrating capital flow analysis into a multi-agent debate and risk-management pipeline, FlowLens helps users move from narrative-based analysis to behavior-based market interpretation. The goal is not to predict or imitate institutional decisions, but to reduce information asymmetry, make capital movement more transparent, and support a more balanced decision-making environment between retail investors and dominant capital players.

### Design Goals

1. **Institutional-level reasoning**
   Use specialized agents to analyze fundamentals, technical indicators, news, sentiment, risk, and portfolio decisions.

2. **Retail-oriented transparency**
   Translate complex market signals into interpretable reports that individual investors can understand and review.

3. **Capital-flow awareness**
   Incorporate major capital flow, sector rotation, and north-bound capital signals to help users understand the game between retail investors and dominant capital players.

---

The platform deploys specialized LLM-powered agents—from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team, and manipulation detector—that collaboratively evaluate market conditions and engage in structured debates to arrive at the optimal strategy.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

Our framework decomposes complex trading tasks into specialized roles for robust, scalable market analysis.

### Analyst Team
- **Market Analyst**: Technical analysis using MACD, RSI, and other indicators to detect patterns and forecast price movements.
- **Sentiment Analyst**: Aggregates news headlines and social media chatter to gauge short-term market mood.
- **News Analyst**: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- **Fundamentals Analyst**: Evaluates company financials, balance sheets, and cash flow, identifying intrinsic values and potential red flags.
- **Capital Flow Analyst** (主力资金分析): Tracks institutional money—major capital flows, sector fund rotation, and north-bound capital. Answers the question no chart can: *"Are the big players buying or selling?"* Uses AKShare and Tushare data to surface smart money signals that price-based analysis alone would miss.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team
Bullish and bearish researchers critically assess the insights from the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent
Composes the analysts' and researchers' findings into a concrete trading proposal with entry/exit timing and position sizing.

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager
- The **Risk Team** (Aggressive, Neutral, Conservative analysts) debates portfolio risk from multiple angles, assessing volatility, liquidity, and tail risk.
- The **Portfolio Manager** synthesizes all prior work and produces the final trade decision (Buy/Overweight/Hold/Underweight/Sell).

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Manipulation Risk Analyzer
Cross-references all analyst reports to detect potential market manipulation signals, conflicting narratives, or coordinated information campaigns, providing a final integrity check before the decision is committed.

### Full Pipeline

```
Analysts (market → sentiment → news → fundamentals → capital_flow)
  → Bull Researcher ⇄ Bear Researcher (structured debate)
    → Research Manager → [Human Review Gate*]
      → Trader
        → Aggressive ⇄ Conservative ⇄ Neutral (risk debate)
          → Portfolio Manager → [Human Review Gate*]
            → Manipulation Risk Analyzer → Final Decision
```

*\*Human Review Gates are optional and toggleable per run.*

## What's Different from the Original TradingAgents

This project builds on [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) and adds features focused on real-world usability, Chinese market depth, and human-AI collaboration.

| Area | Original TradingAgents | This Project Adds |
|------|----------------------|-------------------|
| **Interface** | CLI only (terminal wizard) | Web Dashboard — start analysis, watch it stream live, browse history, all in browser |
| **Analysts** | 4 (Market, Sentiment, News, Fundamentals) | **+ Capital Flow Analyst** (主力资金, sector flow, north-bound capital) |
| **Agents** | Bull/Bear Researchers, Trader, 3 Risk Analysts, Portfolio Manager | **+ Manipulation Risk Analyzer** (cross-reference integrity check) |
| **Human interaction** | Fully autonomous, no way to intervene | **Human-in-the-Loop Review** — pause at Research Manager or Portfolio Manager, approve or revise with feedback |
| **Chinese markets** | Limited (yfinance has spotty China coverage) | **First-class A-share support**: East Money news, Caixin, AKShare data, capital flow tracking |
| **News sources** | yfinance + Alpha Vantage | **+ AKShare + East Money (东方财富)**, with automatic fallback chain |
| **Streaming** | Terminal Live layout | **WebSocket real-time** — each agent's output appears as it's generated |
| **Configuration** | Edit `DEFAULT_CONFIG` in code or set env vars | **Settings UI** — change LLM, models, debate depth, vendors, and review gates from browser |
| **Pipeline visibility** | Progress bar in terminal | **Stage tracking** — know exactly which phase is running (Analysts → Research → Trader → Risk → Decision) |
| **Decision history** | Append-only markdown log | Browse past runs and full decision trails in dashboard |

In short: the original is a powerful research framework. This project wraps it in a usable interface, adds capital flow intelligence for Chinese markets, and lets humans step in at critical decisions instead of watching from the sidelines.

## Web Dashboard

FlowLens ships with a full web dashboard for visual analysis management.

```bash
# Start the backend
python -m dashboard.api.app

# Start the frontend (separate terminal)
cd dashboard/frontend
npm install
npm run dev
```

### Features
- **Real-time streaming**: Watch each agent's output appear live via WebSocket as the analysis runs
- **Pipeline visualization**: Track which stage the analysis is in (Analysts → Research → Trader → Risk → Decision)
- **Human-in-the-Loop review**: Optionally pause at key decision points (Research Manager, Portfolio Manager) to review, approve, or revise the AI's output with feedback
- **One-click settings**: Configure LLM providers, models, research depth, data vendors, and review gates from the browser
- **Analysis history**: Browse past runs and their full decision trails
- **Multi-language**: Output in English, Chinese, Japanese, Korean, and more

### Human-in-the-Loop Review

When enabled, the pipeline pauses at two critical checkpoints:

| Gate | What you review | What you can do |
|------|----------------|------------------|
| **Research Manager** | The Bull/Bear debate synthesis and investment plan | Approve, revise with feedback |
| **Portfolio Manager** | The final trade decision and risk assessment | Approve, override rating, or provide feedback |

Your feedback is injected into subsequent nodes, so downstream agents see and respond to it. The feature is toggleable per analysis run—turn it on when you want oversight, off for fully autonomous runs.

### Chinese Market Support (A-Share / 国内市场)

FlowLens has first-class support for Chinese markets that goes well beyond surface-level news translation.

**Capital flow is the core differentiator.** In A-share markets, the single most important signal is 资金流向—where institutional money is flowing. Most overseas tools are blind to this. FlowLens integrates:

- **Capital Flow Analyst (主力资金分析)**: Real-time tracking of major capital flows (大单/超大单净流入), institutional vs retail money, and sector-level fund rotation. Uses AKShare's `stock_individual_fund_flow` and Tushare's moneyflow API.
- **Sector Flow Analysis (板块资金流向)**: Identifies which industry sectors are attracting or losing institutional capital, surfacing rotation signals before they show up in prices.
- **North-bound Capital (北向资金)**: Tracks foreign capital flowing through Stock Connect into A-shares—a leading indicator closely watched by Chinese traders.

**News sources that actually matter for Chinese stocks:**
- **East Money (东方财富)**: The largest retail investor platform in China. Ticker-specific news and market-wide headlines.
- **Caixin (财新)**: Authoritative financial and economic reporting, via AKShare bridge.
- **AKShare**: Native A-share data for prices, fundamentals, and capital flows.

## Installation and CLI

### Installation

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

Create a virtual environment:
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install:
```bash
pip install .
```

### Docker

```bash
cp .env.example .env  # add your API keys
docker compose run --rm tradingagents
```

For local models with Ollama:
```bash
docker compose --profile ollama run --rm tradingagents-ollama
```

### Required APIs

Set the API key for your chosen LLM provider:

```bash
export OPENAI_API_KEY=...          # OpenAI (GPT)
export GOOGLE_API_KEY=...          # Google (Gemini)
export ANTHROPIC_API_KEY=...       # Anthropic (Claude)
export XAI_API_KEY=...             # xAI (Grok)
export DEEPSEEK_API_KEY=...        # DeepSeek
export DASHSCOPE_API_KEY=...       # Qwen — International
export DASHSCOPE_CN_API_KEY=...    # Qwen — China
export ZHIPU_API_KEY=...           # GLM via Z.AI (international)
export ZHIPU_CN_API_KEY=...        # GLM via BigModel (China)
export MINIMAX_API_KEY=...         # MiniMax — Global
export MINIMAX_CN_API_KEY=...      # MiniMax — China
export OPENROUTER_API_KEY=...      # OpenRouter
export ALPHA_VANTAGE_API_KEY=...   # Alpha Vantage (data vendor)
export TUSHARE_TOKEN=...           # Tushare (A-share capital flow)
```

### CLI Usage

```bash
tradingagents          # interactive wizard
tradingagents analyze  # skip wizard, go straight to analysis

# Checkpoint & resume
tradingagents analyze --checkpoint
tradingagents analyze --clear-checkpoints
```

## TradingAgents Package

### Python Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5.4"
config["quick_think_llm"] = "gpt-5.4-mini"
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

### Configuration Highlights

See `tradingagents/default_config.py` for all options. Key settings:

| Key | Description | Default |
|-----|-------------|---------|
| `llm_provider` | LLM provider | `"openai"` |
| `deep_think_llm` / `quick_think_llm` | Model selection | `"gpt-5.4"` / `"gpt-5.4-mini"` |
| `max_debate_rounds` | Bull/Bear debate depth | `1` |
| `max_risk_discuss_rounds` | Risk debate depth | `1` |
| `analyst_concurrency_limit` | Parallel analysts | `1` |
| `output_language` | Report language | `"English"` |
| `data_vendors` | Per-category data source | yfinance |
| `enable_human_review` | Human-in-the-loop gates | `False` |
| `human_review_points` | Which gates to enable | `["research_manager", "portfolio_manager"]` |
| `checkpoint_enabled` | LangGraph resume | `False` |

### Data Vendors

Multi-vendor data layer with automatic fallback:

| Category | Available Vendors |
|----------|-------------------|
| Core stock APIs | yfinance, Alpha Vantage |
| Technical indicators | yfinance, Alpha Vantage |
| Fundamental data | yfinance, Alpha Vantage |
| News | yfinance, Alpha Vantage, AKShare, East Money |
| Capital flow | AKShare, Tushare |

## Persistence and Recovery

### Decision Log

Always on. Each completed run appends its decision to `~/.tradingagents/memory/trading_memory.md`. On the next run for the same ticker, TradingAgents fetches realised returns (raw and alpha vs benchmark), generates a reflection, and injects past context into the Portfolio Manager prompt.

### Checkpoint Resume

Opt-in via `--checkpoint` or `checkpoint_enabled: True`. LangGraph saves state after each node so a crashed run resumes from the last successful step. Checkpoints are cleared automatically on successful completion.

## Contributing

We welcome contributions from the community! Whether it's fixing a bug, improving documentation, or suggesting a new feature, your input helps make this project better. Join our open-source financial AI research community [Tauric Research](https://tauric.ai/).

## Citation

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```

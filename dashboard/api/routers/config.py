"""Router for configuration management."""

import json
import os
from pathlib import Path
from copy import deepcopy

from fastapi import APIRouter

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config, get_config as get_dataflow_config

router = APIRouter(tags=["config"])

_CONFIG_FILE = Path.home() / ".tradingagents" / "config.json"

# Config metadata for the frontend form
CONFIG_SCHEMA = [
    {"key": "llm_provider", "type": "string", "description": "Default LLM provider", "default": "openai",
     "options": ["openai", "google", "anthropic", "xai", "deepseek", "qwen", "qwen-cn", "glm", "glm-cn", "minimax", "minimax-cn", "openrouter", "azure", "ollama"],
     "env_override": "TRADINGAGENTS_LLM_PROVIDER"},
    {"key": "deep_think_llm", "type": "string", "description": "Model for complex reasoning (Research/Portfolio Manager)", "default": "gpt-5.4",
     "env_override": "TRADINGAGENTS_DEEP_THINK_LLM"},
    {"key": "quick_think_llm", "type": "string", "description": "Model for quick tasks (analysts, debaters)", "default": "gpt-5.4-mini",
     "env_override": "TRADINGAGENTS_QUICK_THINK_LLM"},
    {"key": "backend_url", "type": "string", "description": "Custom API endpoint (overrides provider default)", "default": None,
     "env_override": "TRADINGAGENTS_LLM_BACKEND_URL"},
    {"key": "output_language", "type": "string", "description": "Report output language", "default": "English",
     "options": ["English", "Chinese", "Japanese", "Korean", "Spanish", "Portuguese", "French", "German", "Arabic", "Russian", "Hindi"],
     "env_override": "TRADINGAGENTS_OUTPUT_LANGUAGE"},
    {"key": "max_debate_rounds", "type": "int", "description": "Number of debate rounds between researchers", "default": 1,
     "env_override": "TRADINGAGENTS_MAX_DEBATE_ROUNDS"},
    {"key": "max_risk_discuss_rounds", "type": "int", "description": "Number of risk discussion rounds", "default": 1,
     "env_override": "TRADINGAGENTS_MAX_RISK_ROUNDS"},
    {"key": "checkpoint_enabled", "type": "bool", "description": "Enable LangGraph checkpoint resume", "default": False,
     "env_override": "TRADINGAGENTS_CHECKPOINT_ENABLED"},
    {"key": "enable_human_review", "type": "bool", "description": "Enable human review gates at key decision points", "default": False},
    {"key": "human_review_points", "type": "string_list", "description": "Which decision points to review (research_manager, portfolio_manager)", "default": ["research_manager", "portfolio_manager"]},
    {"key": "news_article_limit", "type": "int", "description": "Max articles per ticker", "default": 20},
    {"key": "global_news_article_limit", "type": "int", "description": "Max articles for global/macro news", "default": 10},
    {"key": "global_news_lookback_days", "type": "int", "description": "Macro news lookback window (days)", "default": 7},
    {"key": "google_thinking_level", "type": "string", "description": "Gemini thinking mode", "default": None, "options": ["high", "minimal"]},
    {"key": "openai_reasoning_effort", "type": "string", "description": "OpenAI reasoning effort", "default": None, "options": ["low", "medium", "high"]},
    {"key": "anthropic_effort", "type": "string", "description": "Anthropic effort level", "default": None, "options": ["low", "medium", "high"]},
    {"key": "analyst_concurrency_limit", "type": "int", "description": "Max concurrent analysts", "default": 1},
    {"key": "benchmark_ticker", "type": "string", "description": "Override benchmark ticker for alpha calculation", "default": None,
     "env_override": "TRADINGAGENTS_BENCHMARK_TICKER"},
    {"key": "results_dir", "type": "string", "description": "Directory for analysis result logs", "default": str(DEFAULT_CONFIG["results_dir"])},
    {"key": "data_cache_dir", "type": "string", "description": "Directory for cache and checkpoints", "default": str(DEFAULT_CONFIG["data_cache_dir"])},
    {"key": "memory_log_path", "type": "string", "description": "Path to the trading memory log", "default": str(DEFAULT_CONFIG.get("memory_log_path", ""))},
]


def _load_saved_config() -> dict:
    """Load persisted config from disk."""
    if _CONFIG_FILE.exists():
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_config(config: dict):
    """Persist config to disk."""
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def _get_merged_config() -> dict:
    """Merge saved config on top of defaults. Defaults are the base; saved and env overrides win."""
    saved = _load_saved_config()
    merged = deepcopy(DEFAULT_CONFIG)
    for key, value in saved.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


@router.get("/config")
async def get_config():
    """Return current effective configuration (merged defaults + saved + env overrides)."""
    config = _get_merged_config()
    # Mask sensitive values for API response
    safe = {}
    for k, v in config.items():
        safe[k] = v
    return {"config": safe}


@router.put("/config")
async def update_config(body: dict):
    """Update specific config keys. Persists to ~/.tradingagents/config.json."""
    saved = _load_saved_config()
    updates = body.get("updates", body)
    for key, value in updates.items():
        saved[key] = value
    _save_config(saved)
    # Also update the runtime dataflows config so changes take effect immediately
    set_config(_get_merged_config())
    return {"status": "ok", "updated_keys": list(updates.keys())}


@router.post("/config/reset")
async def reset_config():
    """Reset all configuration to factory defaults."""
    if _CONFIG_FILE.exists():
        _CONFIG_FILE.unlink()
    set_config(deepcopy(DEFAULT_CONFIG))
    return {"status": "ok", "message": "Configuration reset to defaults"}


@router.get("/config/schema")
async def get_config_schema():
    """Return config schema metadata for form rendering."""
    return CONFIG_SCHEMA

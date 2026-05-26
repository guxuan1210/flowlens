"""Expose LLM model catalog and provider info via the API."""

from __future__ import annotations

from typing import Any

from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS, ModelOption, get_model_options
from tradingagents.llm_clients.api_key_env import get_api_key_env


PROVIDER_INFO: list[dict[str, Any]] = [
    {"key": "openai", "display_name": "OpenAI", "default_backend_url": "https://api.openai.com/v1", "requires_api_key": True, "supports_thinking_config": True},
    {"key": "google", "display_name": "Google (Gemini)", "default_backend_url": None, "requires_api_key": True, "supports_thinking_config": True},
    {"key": "anthropic", "display_name": "Anthropic (Claude)", "default_backend_url": "https://api.anthropic.com/", "requires_api_key": True, "supports_thinking_config": True},
    {"key": "xai", "display_name": "xAI (Grok)", "default_backend_url": "https://api.x.ai/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "deepseek", "display_name": "DeepSeek", "default_backend_url": "https://api.deepseek.com", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "qwen", "display_name": "Qwen (International)", "default_backend_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "qwen-cn", "display_name": "Qwen (China)", "default_backend_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "glm", "display_name": "GLM (Z.AI International)", "default_backend_url": "https://api.z.ai/api/paas/v4/", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "glm-cn", "display_name": "GLM (BigModel China)", "default_backend_url": "https://open.bigmodel.cn/api/paas/v4/", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "minimax", "display_name": "MiniMax (Global)", "default_backend_url": "https://api.minimax.io/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "minimax-cn", "display_name": "MiniMax (China)", "default_backend_url": "https://api.minimaxi.com/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "openrouter", "display_name": "OpenRouter", "default_backend_url": "https://openrouter.ai/api/v1", "requires_api_key": True, "supports_thinking_config": False},
    {"key": "azure", "display_name": "Azure OpenAI", "default_backend_url": None, "requires_api_key": True, "supports_thinking_config": False},
    {"key": "ollama", "display_name": "Ollama (Local/Remote)", "default_backend_url": "http://localhost:11434/v1", "requires_api_key": False, "supports_thinking_config": False},
]


def get_providers() -> list[dict[str, Any]]:
    """Return all LLM providers with API key env info."""
    result = []
    for p in PROVIDER_INFO:
        entry = dict(p)
        entry["api_key_env"] = get_api_key_env(p["key"])
        result.append(entry)
    return result


def get_models_for_provider(provider: str) -> dict[str, Any] | None:
    """Return quick/deep model options for a provider."""
    provider_lower = provider.lower()
    try:
        options = MODEL_OPTIONS[provider_lower]
    except KeyError:
        return None
    return {
        "provider": provider_lower,
        "quick": [{"label": label, "value": value} for label, value in options.get("quick", [])],
        "deep": [{"label": label, "value": value} for label, value in options.get("deep", [])],
    }

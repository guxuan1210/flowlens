"""Dependency injection for FastAPI routes."""

from tradingagents.default_config import DEFAULT_CONFIG


def get_config() -> dict:
    """Return the current effective configuration."""
    return DEFAULT_CONFIG.copy()

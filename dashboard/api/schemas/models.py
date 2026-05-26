"""Pydantic schemas for LLM model information."""

from __future__ import annotations

from pydantic import BaseModel


class ModelItem(BaseModel):
    label: str
    value: str


class ModelOptions(BaseModel):
    provider: str
    quick: list[ModelItem]
    deep: list[ModelItem]


class ProviderInfo(BaseModel):
    key: str
    display_name: str
    default_backend_url: str | None
    requires_api_key: bool
    api_key_env: str | None
    supports_thinking_config: bool

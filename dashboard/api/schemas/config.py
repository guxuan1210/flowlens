"""Pydantic schemas for configuration."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class ConfigUpdateRequest(BaseModel):
    updates: dict[str, Any]


class ConfigResponse(BaseModel):
    config: dict[str, Any]


class ConfigFieldSchema(BaseModel):
    key: str
    type: str  # "string", "int", "float", "bool", "dict", "list"
    description: str
    default: Any
    options: Optional[list[str]] = None
    env_override: Optional[str] = None

"""Router for LLM model information."""

from fastapi import APIRouter

from dashboard.api.services.model_service import get_providers, get_models_for_provider

router = APIRouter(tags=["models"])


@router.get("/models/providers")
async def list_providers():
    """Return available LLM providers with metadata."""
    return get_providers()


@router.get("/models/{provider}")
async def get_models(provider: str):
    """Return model options for a specific provider."""
    result = get_models_for_provider(provider)
    if result is None:
        return {"provider": provider, "quick": [], "deep": [], "error": f"Unknown provider: {provider}"}
    return result

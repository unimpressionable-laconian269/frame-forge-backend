from app.core.config import Settings
from app.services.openrouter_service import OpenRouterRequestError, OpenRouterService


def test_candidate_models_are_unique_and_include_router_fallback() -> None:
    settings = Settings(
        OPENROUTER_API_KEY="test-key",
        openrouter_model="meta-llama/llama-3.1-8b-instruct:free",
        openrouter_fallback_models="qwen/qwen3-coder:free,mistralai/mistral-7b-instruct:free,openrouter/free",
        openrouter_fallback_model="openrouter/free",
    )

    service = OpenRouterService(settings)
    candidates = service._candidate_models()

    assert candidates[0] == "meta-llama/llama-3.1-8b-instruct:free"
    assert "openrouter/free" in candidates
    # No duplicates
    assert len(candidates) == len(set(candidates))


def test_should_try_fallback_for_model_not_found_errors() -> None:
    error = OpenRouterRequestError(
        model="legacy/model",
        status_code=404,
        body='{"error":{"message":"No endpoints found matching your data"}}',
    )

    assert OpenRouterService._should_try_fallback(error) is True


def test_build_error_message_for_missing_model_is_actionable() -> None:
    error = OpenRouterRequestError(
        model="legacy/model",
        status_code=404,
        body='{"error":{"message":"Model not found"}}',
    )

    message = OpenRouterService._build_error_message(error)

    assert "OPENROUTER_MODEL" in message
    assert "qwen/qwen3-coder:free" in message
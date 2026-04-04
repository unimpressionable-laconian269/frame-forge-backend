import json
from collections.abc import AsyncIterator

import httpx

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterRequestError(RuntimeError):
    def __init__(self, model: str, status_code: int, body: str) -> None:
        self.model = model
        self.status_code = status_code
        self.body = body
        super().__init__(f"OpenRouter request failed for model '{model}' with status {status_code}: {body}")


class OpenRouterService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        if not self.settings.openrouter_api_key:
            demo_response = (
                "OpenRouter API key is not configured, so this is a local demo response.\n\n"
                "```tsx\n"
                "export default function DemoCard() {\n"
                "  return (\n"
                "    <section style={{ padding: 24, fontFamily: 'ui-sans-serif, system-ui' }}>\n"
                "      <div style={{ maxWidth: 420, borderRadius: 20, padding: 24, background: '#fff', boxShadow: '0 20px 45px rgba(15, 23, 42, 0.08)' }}>\n"
                "        <p style={{ margin: 0, fontSize: 12, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#6b7280' }}>Preview Mode</p>\n"
                "        <h2 style={{ margin: '12px 0', fontSize: 28, color: '#111827' }}>Component Sandbox Ready</h2>\n"
                "        <p style={{ margin: 0, color: '#4b5563', lineHeight: 1.6 }}>Add OPENROUTER_API_KEY to backend/.env to switch from demo output to live model generations.</p>\n"
                "      </div>\n"
                "    </section>\n"
                "  );\n"
                "}\n"
                "```"
            )
            for chunk in demo_response:
                yield chunk
            return

        url = f"{self.settings.openrouter_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.frontend_url,
            "X-OpenRouter-Title": self.settings.app_name,
        }

        last_error: OpenRouterRequestError | None = None

        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            for model in self._candidate_models():
                try:
                    async for chunk in self._stream_chat_with_model(client, url, headers, messages, model):
                        yield chunk
                    return
                except OpenRouterRequestError as exc:
                    last_error = exc
                    if self._should_try_fallback(exc):
                        logger.warning(
                            "OpenRouter model '%s' failed with status %s. Trying fallback model.",
                            exc.model,
                            exc.status_code,
                        )
                        continue
                    raise RuntimeError(self._build_error_message(exc)) from exc

        if last_error is not None:
            raise RuntimeError(self._build_error_message(last_error)) from last_error

        raise RuntimeError("OpenRouter request could not be started.")

    async def _stream_chat_with_model(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: dict[str, str],
        messages: list[dict[str, str]],
        model: str,
    ) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        async with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.is_error:
                body = (await response.aread()).decode("utf-8", errors="replace").strip()
                raise OpenRouterRequestError(model=model, status_code=response.status_code, body=body)

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                try:
                    parsed = json.loads(data)
                    delta = parsed["choices"][0]["delta"].get("content", "")
                except (KeyError, IndexError, json.JSONDecodeError) as exc:
                    logger.warning("Could not parse OpenRouter stream chunk: %s", exc)
                    continue
                if delta:
                    yield delta

    def _candidate_models(self) -> list[str]:
        configured_models = [
            self.settings.openrouter_model,
            *[m.strip() for m in self.settings.openrouter_fallback_models.split(",") if m.strip()],
            "openrouter/free",
        ]
        unique_models: list[str] = []
        for model in configured_models:
            if model and model not in unique_models:
                unique_models.append(model)
        return unique_models

    @staticmethod
    def _should_try_fallback(error: OpenRouterRequestError) -> bool:
        if error.status_code in {404, 408, 429, 502, 503, 504}:
            return True
        body = error.body.lower()
        return "no endpoints found" in body or "model not found" in body

    @staticmethod
    def _build_error_message(error: OpenRouterRequestError) -> str:
        body = error.body.lower()
        if error.status_code == 404 and ("no endpoints found" in body or "model not found" in body):
            return (
                "OpenRouter no encontro el modelo configurado. "
                "Actualiza OPENROUTER_MODEL en backend/.env a un slug vigente, por ejemplo 'qwen/qwen3-coder:free' o 'openrouter/free'."
            )
        if error.body:
            return f"OpenRouter devolvio {error.status_code}: {error.body}"
        return f"OpenRouter devolvio {error.status_code}."

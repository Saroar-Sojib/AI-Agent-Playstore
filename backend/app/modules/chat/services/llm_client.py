from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(30.0)


class LLMError(Exception):
    """Raised on any non-200 response or malformed Gemini payload.

    Callers should catch this, log a ``UsageLog`` row with ``status="error"``,
    and return a clean 502 to the client — never let raw ``httpx`` exceptions
    (or Gemini's raw error JSON) leak out of this module.
    """


def _role_to_gemini(role: str) -> str | None:
    """Map a ``ChatMessage.role`` to Gemini's role vocabulary.

    Returns ``None`` for "system" rows — they're skipped when building
    ``contents`` (system content goes in ``system_instruction`` instead).
    """
    if role == "assistant":
        return "model"
    if role == "user":
        return "user"
    return None


def _build_contents(history: list[dict], user_message: str) -> list[dict]:
    contents: list[dict] = []
    for turn in history:
        role = _role_to_gemini(turn.get("role", ""))
        if role is None:
            continue
        contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    return contents


async def generate_reply(
    system_prompt: str, history: list[dict], user_message: str
) -> tuple[str, dict]:
    url = f"{settings.LLM_API_URL}/{settings.LLM_MODEL}:generateContent"
    params = {"key": settings.LLM_API_KEY}
    payload: dict[str, Any] = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": _build_contents(history, user_message),
    }

    started = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(url, params=params, json=payload)
    except httpx.HTTPError as exc:
        raise LLMError(f"Gemini request failed: {exc}") from exc
    latency_ms = int((time.monotonic() - started) * 1000)

    if response.status_code != 200:
        raise LLMError(
            f"Gemini returned HTTP {response.status_code}: {response.text[:500]}"
        )

    try:
        data = response.json()
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMError(f"Malformed Gemini response: {exc}") from exc

    tokens_used = None
    usage_metadata = data.get("usageMetadata")
    if isinstance(usage_metadata, dict):
        tokens_used = usage_metadata.get("totalTokenCount")

    metrics = {"latency_ms": latency_ms, "tokens_used": tokens_used}
    return reply_text, metrics

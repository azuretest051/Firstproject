"""Groq LLM client (OpenAI-compatible HTTP API)."""

from __future__ import annotations

import logging
import time
from typing import Optional

from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from src.llm.config import LLMConfig, LLMConfigError, load_llm_config

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised when the LLM call fails after retries."""


class LLMClient:
    """Thin client around Groq's OpenAI-compatible chat completions API."""

    def __init__(self, config: Optional[LLMConfig] = None, client: Optional[OpenAI] = None):
        self.config = config or load_llm_config()
        self._client = client or OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
        )

    def complete(self, prompt: str, *, system: Optional[str] = None) -> str:
        """Return model completion text for the given user prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        attempts = self.config.max_retries + 1
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                response = self._client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                content = response.choices[0].message.content
                if not content or not str(content).strip():
                    raise LLMError("LLM returned an empty completion.")
                return str(content)
            except (RateLimitError, APITimeoutError, APIError) as exc:
                last_error = exc
                logger.warning(
                    "Groq LLM attempt %s/%s failed: %s",
                    attempt + 1,
                    attempts,
                    exc,
                )
                if attempt + 1 < attempts:
                    time.sleep(0.8 * (attempt + 1))
                    continue
            except LLMConfigError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise LLMError(f"Groq LLM request failed: {exc}") from exc

        raise LLMError(f"Groq LLM request failed after retries: {last_error}")

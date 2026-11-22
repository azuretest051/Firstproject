"""LLM configuration (Groq OpenAI-compatible API)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
# Default chosen from commonly available Groq chat models; override via LLM_MODEL.
GROQ_DEFAULT_MODEL = "openai/gpt-oss-20b"


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 1024
    timeout_seconds: float = 30.0
    max_retries: int = 1


class LLMConfigError(RuntimeError):
    """Raised when LLM configuration is missing or invalid."""


def load_llm_config() -> LLMConfig:
    """Load Groq settings from environment variables.

    Accepts ``GROQ_API_KEY`` (preferred) or ``LLM_API_KEY``.
    """
    api_key = (
        os.getenv("GROQ_API_KEY")
        or os.getenv("LLM_API_KEY")
        or ""
    ).strip()
    if not api_key or api_key == "your_api_key_here":
        raise LLMConfigError(
            "Missing Groq API key. Set GROQ_API_KEY in .env "
            "(see .env.example). Get a key at https://console.groq.com/"
        )

    base_url = (
        os.getenv("LLM_BASE_URL")
        or os.getenv("GROQ_BASE_URL")
        or GROQ_DEFAULT_BASE_URL
    ).strip()
    model = (
        os.getenv("LLM_MODEL")
        or os.getenv("GROQ_MODEL")
        or GROQ_DEFAULT_MODEL
    ).strip()

    return LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "1")),
    )

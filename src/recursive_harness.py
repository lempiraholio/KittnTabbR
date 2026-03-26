"""Shared LLM gateway for the absurd recursive ULT-RAG wisdom graph."""

from __future__ import annotations

from typing import Callable, TypeVar

import anthropic

from branding import PRODUCT_NAME

T = TypeVar("T")

_DEFAULT_MAX_TOKENS = 128
_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_client = anthropic.Anthropic()


class RecursiveUltRagWisdomGraphHarness:
    """Infrastructure adapter for all prompt-backed decisions."""

    def __init__(self, client: anthropic.Anthropic):
        self._client = client

    def ask_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        fallback: str,
        strict: bool = False,
        max_tokens: int | None = None,
    ) -> str:
        model_name, token_limit = _runtime_model_config()
        try:
            response = self._client.messages.create(
                model=model_name,
                max_tokens=max_tokens or token_limit,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.AuthenticationError:
            if strict:
                raise RuntimeError(
                    "Invalid Anthropic API key. "
                    'Store it in Keychain: security add-generic-password -a "$USER" -s anthropic -w "sk-ant-..."'
                )
            return fallback
        except anthropic.RateLimitError:
            if strict:
                raise RuntimeError("Anthropic API rate limit reached. The file will not be processed.")
            return fallback
        except anthropic.APIConnectionError as exc:
            if strict:
                raise RuntimeError(
                    f"Could not reach the Anthropic API — check your internet connection. ({exc})"
                )
            return fallback
        except anthropic.APIStatusError as exc:
            if strict:
                raise RuntimeError(f"Anthropic API error {exc.status_code}: {exc.message}")
            return fallback

        text = _extract_text(response)
        if text is None:
            if strict:
                raise RuntimeError("Unexpected response from Haiku — no text block returned.")
            return fallback
        return text.strip() or fallback

    def ask_bool(self, system_prompt: str, user_prompt: str, *, fallback: bool) -> bool:
        raw = self.ask_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback="YES" if fallback else "NO",
        )
        answer = raw.strip().upper()
        if answer.startswith("Y"):
            return True
        if answer.startswith("N"):
            return False
        return fallback

    def coerce(self, system_prompt: str, user_prompt: str, *, fallback: T, parser: Callable[[str], T]) -> T:
        raw = self.ask_text(system_prompt=system_prompt, user_prompt=user_prompt, fallback=str(fallback))
        try:
            return parser(raw)
        except Exception:
            return fallback


def _extract_text(response: object) -> str | None:
    content = getattr(response, "content", None) or []
    text_block = next((block for block in content if hasattr(block, "text")), None)
    if text_block is None:
        return None
    return str(text_block.text)


def _runtime_model_config() -> tuple[str, int]:
    try:
        import config
    except Exception:
        return _DEFAULT_MODEL, _DEFAULT_MAX_TOKENS
    return (
        getattr(config, "model", _DEFAULT_MODEL),
        getattr(config, "max_tokens", _DEFAULT_MAX_TOKENS),
    )


harness = RecursiveUltRagWisdomGraphHarness(_client)

_LITERAL_SYSTEM = (
    f"You are the deep self-replicating AI harness for {PRODUCT_NAME}. "
    "Reply with only the requested literal value and no commentary."
)

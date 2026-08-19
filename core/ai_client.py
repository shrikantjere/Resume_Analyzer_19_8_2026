"""
OpenAI API client wrapper for the AI Resume Analyzer.

Provides a singleton-pattern client with retry logic, rate limiting,
token tracking, and structured output support.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from openai import APIError, APIStatusError, OpenAI, RateLimitError

from core.config import get_settings
from core.exceptions import (
    AIServiceError,
    OpenAIRateLimitError,
    OpenAISchemaError,
    OpenAITimeoutError,
    OpenAITokenLimitError,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class AIClient:
    """Singleton wrapper around the OpenAI API client.

    Manages API communication with retry logic, rate limiting,
    and token usage tracking.

    Usage:
        client = AIClient()
        response = client.chat_complete(system_prompt, user_prompt)
    """

    _instance: Optional["AIClient"] = None

    def __new__(cls) -> "AIClient":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the AI client (once)."""
        if self._initialized:
            return
        self._initialized = True

        self.settings = get_settings()
        self._client = OpenAI(
            api_key=self.settings.openai_api_key.get_secret_value(),
            timeout=self.settings.openai_timeout,
        )
        self._model = self.settings.openai_model
        self._max_tokens = self.settings.openai_max_tokens
        self._temperature = self.settings.openai_temperature
        self._retry_count = self.settings.openai_retry_count

        self._total_tokens_used: int = 0
        self._total_api_calls: int = 0

    # ── Public API ─────────────────────────────────────────────────────

    def chat_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[dict[str, str]] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Send a chat completion request to OpenAI.

        Args:
            system_prompt: System-level instructions for the model.
            user_prompt: User input / resume text to analyze.
            response_format: Optional response format specification
                (e.g., {"type": "json_object"}).
            correlation_id: Optional trace ID for request correlation.

        Returns:
            str: The model's response text.

        Raises:
            OpenAIRateLimitError: If rate limit is exceeded.
            OpenAITimeoutError: If the request times out.
            OpenAISchemaError: If the response is malformed.
            AIServiceError: For other API errors.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        last_error: Optional[Exception] = None

        for attempt in range(1, self._retry_count + 1):
            try:
                start_time = time.monotonic()
                response = self._client.chat.completions.create(**kwargs)
                duration_ms = int((time.monotonic() - start_time) * 1000)

                # Track usage
                if response.usage:
                    self._total_tokens_used += response.usage.total_tokens

                self._total_api_calls += 1

                # Extract response text
                content = response.choices[0].message.content
                if not content:
                    raise OpenAISchemaError(
                        "Empty response from AI service.",
                        correlation_id=correlation_id,
                    )

                logger.info(
                    "OpenAI API call completed",
                    extra={
                        "correlation_id": correlation_id,
                        "model": self._model,
                        "tokens_used": response.usage.total_tokens if response.usage else 0,
                        "duration_ms": duration_ms,
                        "attempt": attempt,
                    },
                )

                return content

            except RateLimitError as e:
                retry_after = getattr(e, "retry_after", 30)
                logger.warning(
                    f"Rate limit hit on attempt {attempt}/{self._retry_count}",
                    extra={
                        "correlation_id": correlation_id,
                        "retry_after": retry_after,
                        "attempt": attempt,
                    },
                )

                if attempt < self._retry_count:
                    time.sleep(retry_after)
                    last_error = OpenAIRateLimitError(
                        retry_after=retry_after,
                        correlation_id=correlation_id,
                    )
                else:
                    raise OpenAIRateLimitError(
                        retry_after=retry_after,
                        correlation_id=correlation_id,
                    ) from e

            except APIStatusError as e:
                if e.status_code == 400 and "token" in str(e).lower():
                    raise OpenAITokenLimitError(
                        token_count=0,
                        max_tokens=self._max_tokens,
                        correlation_id=correlation_id,
                    ) from e

                logger.error(
                    f"OpenAI API error on attempt {attempt}: {e}",
                    extra={
                        "correlation_id": correlation_id,
                        "status_code": e.status_code,
                        "attempt": attempt,
                    },
                )
                last_error = AIServiceError(
                    f"OpenAI API error: {e}",
                    correlation_id=correlation_id,
                )

                if attempt < self._retry_count:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise last_error from e

            except Exception as e:
                logger.error(
                    f"Unexpected OpenAI error on attempt {attempt}: {e}",
                    extra={
                        "correlation_id": correlation_id,
                        "attempt": attempt,
                    },
                    exc_info=True,
                )
                last_error = AIServiceError(
                    f"Unexpected error communicating with AI service: {e}",
                    correlation_id=correlation_id,
                )

                if attempt < self._retry_count:
                    time.sleep(2 ** attempt)
                else:
                    raise last_error from e

        # Should not reach here, but safeguard
        raise AIServiceError(
            "AI service unavailable after all retry attempts.",
            correlation_id=correlation_id,
        )

    def chat_complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        correlation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Send a chat completion request and parse JSON response.

        Args:
            system_prompt: System-level instructions for the model.
            user_prompt: User input / resume text to analyze.
            correlation_id: Optional trace ID for request correlation.

        Returns:
            dict: Parsed JSON response from the model.

        Raises:
            OpenAISchemaError: If the response is not valid JSON.
        """
        response = self.chat_complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
            correlation_id=correlation_id,
        )

        import json

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise OpenAISchemaError(
                f"Failed to parse AI response as JSON: {e}",
                correlation_id=correlation_id,
            ) from e

    @property
    def total_tokens_used(self) -> int:
        """Return total tokens used across all API calls."""
        return self._total_tokens_used

    @property
    def total_api_calls(self) -> int:
        """Return total number of API calls made."""
        return self._total_api_calls

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracing.

        Returns:
            str: A UUID v4 string.
        """
        return str(uuid.uuid4())
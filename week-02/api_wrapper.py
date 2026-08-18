"""
Week 01 - Task 05: Reusable API Wrapper

A reusable module for calling the Gemini API safely. Handles:
- Sending messages
- Retry on transient failure (with exponential backoff)
- Timeout
- Token usage tracking
- Graceful error handling for rate limits, invalid keys, and any bad response
  (never raises an uncaught exception to the caller — always returns a
  structured result).

This module is designed to be imported and reused in later weeks:
    from api_wrapper import GeminiWrapper

    wrapper = GeminiWrapper()
    result = wrapper.send_message("Hello!")
    if result.success:
        print(result.text)
    else:
        print("Error:", result.error_message)
"""

import os
import time
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors as genai_errors


@dataclass
class APIResult:
    """Structured result returned by every call — never raises to the caller."""
    success: bool
    text: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    error_type: Optional[str] = None      # e.g. "RateLimitError", "InvalidKeyError"
    error_message: Optional[str] = None
    attempts_used: int = 1


class GeminiWrapper:
    """
    Reusable wrapper around the Gemini API.

    Handles retries, timeouts, and structured error reporting so calling
    code never has to deal with raw exceptions from the SDK.
    """

    def __init__(
        self,
        model: str = "gemini-3.5-flash-lite",
        max_retries: int = 4,
        timeout_seconds: float = 30.0,
        base_backoff_seconds: float = 2.0,
    ):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "your_api_key_here":
            # Don't crash the whole program on import/init — surface this
            # clearly the first time send_message is actually called instead.
            self._client = None
            self._init_error = (
                "GEMINI_API_KEY not found or not set. Add your real key to .env."
            )
        else:
            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
            )
            self._init_error = None

        self.model = model
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds

    def send_message(self, prompt: str, temperature: float = 0.7) -> APIResult:
        """
        Send a single prompt to the model. Always returns an APIResult —
        never raises. Retries on transient errors (timeouts, 503s, rate
        limits) with exponential backoff. Fails fast (no retry) on
        non-recoverable errors like an invalid API key.
        """
        if self._client is None:
            return APIResult(
                success=False,
                error_type="ConfigurationError",
                error_message=self._init_error,
            )

        if not prompt or not prompt.strip():
            return APIResult(
                success=False,
                error_type="InvalidInputError",
                error_message="Prompt cannot be empty.",
            )

        last_error_type = None
        last_error_message = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            disable=True
                        ),
                    ),
                )

                usage = response.usage_metadata
                return APIResult(
                    success=True,
                    text=(response.text or "").strip(),
                    input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
                    output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
                    total_tokens=getattr(usage, "total_token_count", 0) or 0,
                    attempts_used=attempt,
                )

            except genai_errors.ClientError as e:
                # 4xx errors: mostly non-recoverable (bad key, bad request).
                # 429 (rate limit) is the one 4xx worth retrying.
                # Different SDK versions expose the code under different
                # attribute names, so check a few and fall back to parsing
                # the message text.
                status = (
                    getattr(e, "status_code", None)
                    or getattr(e, "code", None)
                )
                is_rate_limit = status == 429 or "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e)
                is_auth_error = status in (401, 403) or "UNAUTHENTICATED" in str(e) or "PERMISSION_DENIED" in str(e)

                if is_rate_limit:
                    last_error_type = "RateLimitError"
                    last_error_message = str(e)
                elif is_auth_error:
                    return APIResult(
                        success=False,
                        error_type="InvalidKeyError",
                        error_message="API key was rejected. Check your GEMINI_API_KEY.",
                        attempts_used=attempt,
                    )
                else:
                    # Other client errors (bad model name, bad request, etc.)
                    # won't be fixed by retrying.
                    return APIResult(
                        success=False,
                        error_type="ClientError",
                        error_message=str(e),
                        attempts_used=attempt,
                    )

            except genai_errors.ServerError as e:
                # 5xx errors (e.g. 503 overloaded) — worth retrying.
                last_error_type = "ServerError"
                last_error_message = str(e)

            except TimeoutError as e:
                last_error_type = "TimeoutError"
                last_error_message = str(e)

            except Exception as e:
                # Catch-all: never let an unexpected error crash the caller.
                last_error_type = e.__class__.__name__
                last_error_message = str(e)

            if attempt < self.max_retries:
                wait = self.base_backoff_seconds ** attempt
                time.sleep(wait)

        return APIResult(
            success=False,
            error_type=last_error_type or "UnknownError",
            error_message=last_error_message or "All retry attempts failed.",
            attempts_used=self.max_retries,
        )


if __name__ == "__main__":
    # Quick manual test when running this file directly.
    wrapper = GeminiWrapper()
    result = wrapper.send_message("Say hello in one short sentence.")

    if result.success:
        print("Response:", result.text)
        print(f"Tokens — input: {result.input_tokens}, "
              f"output: {result.output_tokens}, total: {result.total_tokens}")
        print(f"Attempts used: {result.attempts_used}")
    else:
        print(f"Call failed: [{result.error_type}] {result.error_message}")

"""
Week 02 - Task 02: Force Structured Output

Forces the model to return strict JSON matching a Pydantic schema.
Validates the response against the schema, and automatically retries
(with the validation error fed back to the model) if the JSON is
invalid or malformed.

Usage:
    from structured_output import get_structured_response
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    result = get_structured_response(
        "Extract the person's name and age from: 'John is 34 years old.'",
        schema=Person,
    )
    if result.success:
        print(result.data)          # a validated Person instance
    else:
        print(result.error_message)
"""

import json
import re
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from api_wrapper import GeminiWrapper

T = TypeVar("T", bound=BaseModel)


@dataclass
class StructuredResult:
    success: bool
    data: Optional[BaseModel] = None
    raw_text: Optional[str] = None
    error_message: Optional[str] = None
    attempts_used: int = 1


def _extract_json(text: str) -> str:
    """
    Models sometimes wrap JSON in markdown code fences or add stray text
    around it despite instructions. Strip fences and grab the outermost
    {...} or [...] block as a best-effort cleanup before parsing.
    """
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # If there's still leading/trailing junk, grab the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def get_structured_response(
    prompt: str,
    schema: Type[T],
    wrapper: Optional[GeminiWrapper] = None,
    max_schema_retries: int = 3,
) -> StructuredResult:
    """
    Sends a prompt asking for JSON matching `schema`, validates the
    response, and retries (feeding the error back to the model) up to
    `max_schema_retries` times if validation fails.
    """
    if wrapper is None:
        wrapper = GeminiWrapper()

    schema_json = schema.model_json_schema()
    base_instruction = (
        f"{prompt.strip()}\n\n"
        f"Respond ONLY with valid JSON matching this schema, with no "
        f"markdown code fences, no explanation, and no extra text:\n\n"
        f"{json.dumps(schema_json, indent=2)}"
    )

    current_prompt = base_instruction
    last_error = None

    for attempt in range(1, max_schema_retries + 1):
        api_result = wrapper.send_message(current_prompt, temperature=0.2)

        if not api_result.success:
            return StructuredResult(
                success=False,
                error_message=f"API call failed: [{api_result.error_type}] {api_result.error_message}",
                attempts_used=attempt,
            )

        raw_text = api_result.text or ""
        cleaned = _extract_json(raw_text)

        try:
            parsed = json.loads(cleaned)
            validated = schema.model_validate(parsed)
            return StructuredResult(
                success=True,
                data=validated,
                raw_text=raw_text,
                attempts_used=attempt,
            )
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            if attempt < max_schema_retries:
                # Feed the actual error back to the model so it can self-correct.
                current_prompt = (
                    f"{base_instruction}\n\n"
                    f"Your previous response was invalid. It failed with this "
                    f"error:\n{last_error}\n\n"
                    f"Your previous response was:\n{raw_text}\n\n"
                    f"Fix it and respond ONLY with corrected, valid JSON "
                    f"matching the schema."
                )

    return StructuredResult(
        success=False,
        raw_text=raw_text,
        error_message=f"Failed to get valid JSON after {max_schema_retries} attempts. "
                      f"Last error: {last_error}",
        attempts_used=max_schema_retries,
    )


if __name__ == "__main__":
    # Quick manual test
    from pydantic import Field
    from typing import Literal

    class TicketAnalysis(BaseModel):
        category: str = Field(description="e.g. billing, technical, account")
        priority: str = Field(description="low, medium, or high")
        sentiment: str = Field(description="positive, neutral, or negative")

    print("=== Test 1: normal case ===")
    result = get_structured_response(
        "Analyze this support ticket: 'My account got locked and I've been "
        "trying to log in for 2 hours, this is really frustrating and I "
        "need it fixed NOW.'",
        schema=TicketAnalysis,
    )
    if result.success:
        print("Validated data:", result.data.model_dump())
        print(f"Attempts used: {result.attempts_used}")
    else:
        print("Failed:", result.error_message)

    print("\n=== Test 2: strict schema, more likely to trigger a retry ===")
    # Literal types are much stricter than plain str — if the model
    # returns anything outside these exact values (e.g. "urgent" instead
    # of "high"), Pydantic validation fails and the retry logic engages.
    class StrictTicketAnalysis(BaseModel):
        category: Literal["billing", "technical", "account", "general"]
        priority: Literal["low", "medium", "high"]
        sentiment: Literal["positive", "neutral", "negative"]
        needs_human: bool

    result2 = get_structured_response(
        "Analyze this support ticket: 'The app keeps crashing every time "
        "I try to upload a photo, super annoying, please help ASAP.'",
        schema=StrictTicketAnalysis,
    )
    if result2.success:
        print("Validated data:", result2.data.model_dump())
        print(f"Attempts used: {result2.attempts_used}")
    else:
        print("Failed:", result2.error_message)
        print(f"Attempts used: {result2.attempts_used}")

    print("\n=== Test 3: deliberately hard case, designed to trigger a retry ===")
    # A tight numeric range + an ambiguous input make it likely the model's
    # first attempt violates the schema (e.g. returns a score outside
    # 1-10, or a non-integer), forcing at least one real self-correction.
    class StrictReview(BaseModel):
        star_rating: int = Field(ge=1, le=5, description="Integer from 1 to 5 only")
        confidence_score: int = Field(
            ge=1, le=10,
            description="Integer 1-10 representing confidence in this rating"
        )
        one_word_verdict: Literal["buy", "avoid", "wait"]

    result3 = get_structured_response(
        "A customer wrote this ambiguous review: 'It's fine I guess, does "
        "what it says, nothing special but no complaints either. Might "
        "get another one, might not.' Rate it and give your confidence "
        "and verdict.",
        schema=StrictReview,
    )
    if result3.success:
        print("Validated data:", result3.data.model_dump())
        print(f"Attempts used: {result3.attempts_used}")
    else:
        print("Failed:", result3.error_message)
        print(f"Attempts used: {result3.attempts_used}")

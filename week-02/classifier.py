"""
Week 02 - Task 03: Classification Tool

Classifies a support message into: category, priority, sentiment,
and needs_human — returned as validated JSON via the Task 02
structured_output pipeline.

Usage:
    from classifier import classify_message

    result = classify_message("My payment failed twice, please help!")
    if result.success:
        print(result.data.model_dump())
"""

from typing import Literal

from pydantic import BaseModel, Field

from structured_output import get_structured_response, StructuredResult
from api_wrapper import GeminiWrapper


class TicketClassification(BaseModel):
    category: Literal["billing", "technical", "account", "shipping", "general"] = Field(
        description="The main category of the support request"
    )
    priority: Literal["low", "medium", "high"] = Field(
        description="How urgently this needs to be addressed"
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="The customer's emotional tone"
    )
    needs_human: bool = Field(
        description="True if this requires a human agent rather than an automated response"
    )


CLASSIFICATION_PROMPT = """You are a support ticket triage assistant. Analyze the following customer message and classify it.

Guidelines:
- category: pick the single best fit from billing, technical, account, shipping, general
- priority: high = urgent/blocking/angry customer, medium = important but not urgent, low = minor/informational
- sentiment: the customer's emotional tone in their message
- needs_human: true if this is complex, emotionally charged, involves money/refunds, or an automated response would likely be inadequate; false if it's simple enough to auto-resolve

Customer message: "{message}"
"""

# --- v2: improved prompt (Task 05) ---
# Added an explicit rule for irreversible/high-stakes actions after the
# evaluation showed the original prompt under-prioritized calmly-worded
# but serious requests like account deletion (see eval_harness.py results:
# v1 scored priority=medium, needs_human=false on this case).
CLASSIFICATION_PROMPT_V2 = """You are a support ticket triage assistant. Analyze the following customer message and classify it.

Guidelines:
- category: pick the single best fit from billing, technical, account, shipping, general
- priority: high = urgent/blocking/angry customer, OR any irreversible/high-stakes action
  (e.g. account deletion, permanent data removal, cancellations with financial impact)
  even if the customer's tone is calm; medium = important but not urgent and not
  irreversible; low = minor/informational
- sentiment: the customer's emotional tone in their message
- needs_human: true if this is complex, emotionally charged, involves money/refunds,
  OR involves an irreversible/high-stakes action (account deletion, permanent data
  removal) regardless of tone, since these carry real consequences if handled
  incorrectly by automation; false only for simple, low-stakes, easily-reversible requests

Customer message: "{message}"
"""


def classify_message_v2(message: str, wrapper: "GeminiWrapper" = None) -> StructuredResult:
    """Improved classifier using CLASSIFICATION_PROMPT_V2 (Task 05)."""
    prompt = CLASSIFICATION_PROMPT_V2.format(message=message)
    return get_structured_response(prompt, schema=TicketClassification, wrapper=wrapper)


def classify_message(message: str, wrapper: GeminiWrapper = None) -> StructuredResult:
    """Classify a single support message. Returns a StructuredResult with
    a validated TicketClassification in .data on success."""
    prompt = CLASSIFICATION_PROMPT.format(message=message)
    return get_structured_response(prompt, schema=TicketClassification, wrapper=wrapper)


if __name__ == "__main__":
    sample = "I've been charged twice for the same order and no one has responded to my emails in 3 days!"
    result = classify_message(sample)
    if result.success:
        print("Message:", sample)
        print("Classification:", result.data.model_dump())
    else:
        print("Failed:", result.error_message)

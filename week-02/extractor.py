"""
Week 02 - Task 04: Extraction Tool

Extracts structured fields from messy, unstructured text (invoices,
emails, etc.) into validated JSON. Missing fields are handled
gracefully — every field is Optional, so the model can return null
instead of guessing or crashing when information simply isn't present
in the source text.

Usage:
    from extractor import extract_invoice_fields, extract_email_fields

    result = extract_invoice_fields(raw_invoice_text)
    if result.success:
        print(result.data.model_dump())
"""

from typing import Optional

from pydantic import BaseModel, Field

from structured_output import get_structured_response, StructuredResult
from api_wrapper import GeminiWrapper


class InvoiceFields(BaseModel):
    """
    All fields are Optional — real invoices are inconsistently formatted
    and frequently missing one or more of these. The tool should return
    null for missing data rather than guessing or failing.
    """
    invoice_number: Optional[str] = Field(default=None, description="Invoice/reference number")
    vendor_name: Optional[str] = Field(default=None, description="Company or person issuing the invoice")
    invoice_date: Optional[str] = Field(default=None, description="Date of the invoice, as written in the text")
    due_date: Optional[str] = Field(default=None, description="Payment due date, if stated")
    total_amount: Optional[float] = Field(default=None, description="Total amount due, as a number, no currency symbol")
    currency: Optional[str] = Field(default=None, description="Currency code or symbol, e.g. USD, PKR, $")
    line_items: Optional[list[str]] = Field(default=None, description="List of individual items/services billed, if listed")


class EmailFields(BaseModel):
    """All fields optional — a real email may not clearly state all of these."""
    sender_name: Optional[str] = Field(default=None, description="Name of the person who sent the email, if identifiable")
    subject_or_topic: Optional[str] = Field(default=None, description="What the email is about, in a few words")
    requested_action: Optional[str] = Field(default=None, description="What the sender wants done, if anything")
    deadline_mentioned: Optional[str] = Field(default=None, description="Any deadline or time constraint mentioned")
    urgency: Optional[str] = Field(default=None, description="low, medium, or high — omit if genuinely unclear")


INVOICE_PROMPT = """Extract structured data from this invoice text. If a field is not present or not determinable from the text, return null for it — do NOT guess or make up a value.

Invoice text:
\"\"\"
{text}
\"\"\"
"""

EMAIL_PROMPT = """Extract structured data from this email. If a field is not present or not determinable from the text, return null for it — do NOT guess or make up a value.

Email text:
\"\"\"
{text}
\"\"\"
"""


def extract_invoice_fields(text: str, wrapper: Optional[GeminiWrapper] = None) -> StructuredResult:
    prompt = INVOICE_PROMPT.format(text=text)
    return get_structured_response(prompt, schema=InvoiceFields, wrapper=wrapper)


def extract_email_fields(text: str, wrapper: Optional[GeminiWrapper] = None) -> StructuredResult:
    prompt = EMAIL_PROMPT.format(text=text)
    return get_structured_response(prompt, schema=EmailFields, wrapper=wrapper)


if __name__ == "__main__":
    print("=== Test 1: Complete invoice ===")
    complete_invoice = """
    INVOICE #INV-2026-0847
    From: Bright Star Web Hosting
    Date: August 10, 2026
    Due: August 24, 2026

    Services:
    - Web hosting (annual) - $120.00
    - Domain renewal - $15.00
    - SSL certificate - $25.00

    Total Due: $160.00 USD
    """
    result = extract_invoice_fields(complete_invoice)
    if result.success:
        print(result.data.model_dump())
    else:
        print("Failed:", result.error_message)

    print("\n=== Test 2: Incomplete/messy invoice (missing fields) ===")
    messy_invoice = """
    hey just a heads up we billed you for the consulting work,
    total comes to around 450 bucks, let us know if you have questions
    """
    result2 = extract_invoice_fields(messy_invoice)
    if result2.success:
        print(result2.data.model_dump())
        print("(Note: fields not present in the text should show as null/None above)")
    else:
        print("Failed:", result2.error_message)

    print("\n=== Test 3: Email extraction ===")
    email_text = """
    Hi team,

    Following up on the Q3 report — can someone send me the final numbers
    by end of day Friday? We need it for the board meeting.

    Thanks,
    Sarah
    """
    result3 = extract_email_fields(email_text)
    if result3.success:
        print(result3.data.model_dump())
    else:
        print("Failed:", result3.error_message)

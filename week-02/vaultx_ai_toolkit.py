"""
Week 02 - Task 06: Reusable Structured-Output Module

Packages the classification and extraction tools built this week into
a single, clean, importable module with logging and error handling.

Design goals:
  - Every public function is logged (call started, succeeded/failed, timing)
  - No function ever raises an uncaught exception to the caller — every
    call returns a consistent result object with .success / .error info
  - Safe to import and call from future automations without needing to
    understand the internals (Gemini API, Pydantic, retries, etc.)

Usage:
    from vaultx_ai_toolkit import classify_ticket, extract_invoice, extract_email

    result = classify_ticket("My payment failed, please help.")
    if result.success:
        print(result.data.model_dump())
    else:
        print("Error:", result.error_message)

Logs are written to both the console and vaultx_ai_toolkit.log.
"""

import functools
import logging
import time
from typing import Callable

from classifier import classify_message, classify_message_v2
from extractor import extract_invoice_fields, extract_email_fields
from structured_output import StructuredResult


# ---- Logging setup ----
logger = logging.getLogger("vaultx_ai_toolkit")
logger.setLevel(logging.INFO)

if not logger.handlers:  # avoid duplicate handlers if module is reloaded/imported twice
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("vaultx_ai_toolkit.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def logged_tool(func: Callable) -> Callable:
    """
    Decorator that logs every call to a toolkit function: when it starts,
    how long it took, and whether it succeeded or failed — without ever
    letting an exception escape to the caller. Any unexpected exception
    (a bug, not just an API error) is caught here as a final safety net
    and converted into a failed StructuredResult instead of crashing
    whatever automation imported this module.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        call_desc = f"{func.__name__}(" + ", ".join(
            [repr(a)[:60] for a in args] + [f"{k}={v!r}"[:60] for k, v in kwargs.items()]
        ) + ")"
        logger.info(f"START {call_desc}")
        start = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed = round(time.time() - start, 2)

            if isinstance(result, StructuredResult):
                if result.success:
                    logger.info(f"SUCCESS {func.__name__} ({elapsed}s, "
                                f"{result.attempts_used} attempt(s))")
                else:
                    logger.warning(f"FAILED {func.__name__} ({elapsed}s): "
                                   f"{result.error_message}")
            else:
                logger.info(f"DONE {func.__name__} ({elapsed}s)")

            return result

        except Exception as e:
            # Final safety net: even a genuine bug in the underlying code
            # should never crash whatever automation is calling this.
            elapsed = round(time.time() - start, 2)
            logger.error(f"CRASHED {func.__name__} ({elapsed}s): "
                        f"{e.__class__.__name__}: {e}")
            return StructuredResult(
                success=False,
                error_message=f"Unexpected internal error: {e.__class__.__name__}: {e}",
            )

    return wrapper


# ---- Public, logged, crash-proof tool functions ----

@logged_tool
def classify_ticket(message: str, use_improved_prompt: bool = True, **kwargs) -> StructuredResult:
    """
    Classify a support message into category, priority, sentiment, and
    needs_human. Uses the improved (v2) prompt by default, based on the
    Task 05 evaluation results.
    """
    fn = classify_message_v2 if use_improved_prompt else classify_message
    return fn(message, **kwargs)


@logged_tool
def extract_invoice(text: str, **kwargs) -> StructuredResult:
    """Extract structured fields from invoice text, handling missing fields gracefully."""
    return extract_invoice_fields(text, **kwargs)


@logged_tool
def extract_email(text: str, **kwargs) -> StructuredResult:
    """Extract structured fields from email text, handling missing fields gracefully."""
    return extract_email_fields(text, **kwargs)


if __name__ == "__main__":
    # Demonstrates the module being used exactly as a future automation would:
    # import it, call the tools, never worry about exceptions.
    print("Testing packaged module...\n")

    r1 = classify_ticket("My internet has been down for 2 days, very frustrating.")
    print(f"classify_ticket -> success={r1.success}, "
          f"data={r1.data.model_dump() if r1.success else r1.error_message}\n")

    r2 = extract_invoice("Invoice #123, total $99.50, no due date mentioned.")
    print(f"extract_invoice -> success={r2.success}, "
          f"data={r2.data.model_dump() if r2.success else r2.error_message}\n")

    # Deliberately call with a MISSING required argument to genuinely
    # trigger a TypeError, proving the safety net actually catches real
    # exceptions (not just API-level failures). Note: passing None as
    # the message does NOT work as a crash-test, since string formatting
    # silently converts None into the text "None" rather than raising —
    # this missing-argument call is a proper test of the safety net.
    r3 = classify_ticket()  # type: ignore  # missing required 'message' arg
    print(f"classify_ticket() with missing arg -> success={r3.success}, "
          f"error={r3.error_message}")
    print("\n(The call above was missing a required argument on purpose. "
          "Notice the program did NOT crash — the decorator caught the "
          "TypeError and returned a clean failed result instead. Check "
          "vaultx_ai_toolkit.log for the logged CRASHED entry.)")

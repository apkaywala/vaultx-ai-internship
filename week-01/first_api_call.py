"""
Week 01 - Task 03: First API Call
Sends a single prompt to Gemini, prints the response, and calculates
token usage and cost for that one call.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---- Pricing (update if Google changes rates) ----
# These figures are for the Flash-Lite tier as of writing; "gemini-flash-latest"
# may resolve to a different tier/price. ALWAYS verify current pricing at
# ai.google.dev/gemini-api/docs/pricing before reporting a number in your writeup.
INPUT_COST_PER_MILLION = 0.10   # USD per 1,000,000 input tokens
OUTPUT_COST_PER_MILLION = 0.40  # USD per 1,000,000 output tokens
MODEL_NAME = "gemini-flash-latest"  # alias -> Google's current stable Flash model


def main():
    # Load the API key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not found or not set. "
            "Add your real key to the .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = "Explain what a REST API is in two simple sentences."

    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        ),
    )

    # ---- Print the model's response ----
    print("Response:")
    print(response.text)

    # ---- Token usage ----
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count
    output_tokens = usage.candidates_token_count
    total_tokens = usage.total_token_count

    print("\n--- Token Usage ---")
    print(f"Input tokens:  {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total tokens:  {total_tokens}")

    # ---- Cost calculation ----
    # Note: on Gemini's FREE TIER, this call costs $0 — you are billed in
    # rate limits (requests/day, tokens/minute), not dollars. The figures
    # below show what this call WOULD cost on the paid tier, for comparison.
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    total_cost = input_cost + output_cost

    print("\n--- Cost for this call ---")
    print("Actual cost (free tier): $0.00 (billed in rate limits, not dollars)")
    print(f"Hypothetical paid-tier cost:")
    print(f"  Input cost:  ${input_cost:.8f}")
    print(f"  Output cost: ${output_cost:.8f}")
    print(f"  Total cost:  ${total_cost:.8f}")


if __name__ == "__main__":
    main()

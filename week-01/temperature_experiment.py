"""
Week 01 - Task 04: Experiment with generation parameters
Runs the same prompt at temperature 0, 0.7, and 1.0 (three times each),
then writes all outputs to a markdown table for analysis.
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL_NAME = "gemini-flash-latest"
PROMPT = "Write a one-sentence tagline for a cybersecurity startup."
TEMPERATURES = [0.0, 0.7, 1.0]
RUNS_PER_TEMPERATURE = 3
OUTPUT_FILE = "temperature_results.md"


def run_prompt(client, temperature, max_retries=4):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=PROMPT,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
            return response.text.strip()
        except Exception as e:
            if attempt == max_retries:
                raise
            wait = 2 ** attempt  # 2s, 4s, 8s, 16s
            print(f"  Call failed ({e.__class__.__name__}), retrying in {wait}s "
                  f"(attempt {attempt}/{max_retries})...")
            time.sleep(wait)


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY not found or not set in .env")

    client = genai.Client(api_key=api_key)

    results = []  # list of (temperature, run_number, output_text)

    print(f"Prompt: {PROMPT}\n")

    for temp in TEMPERATURES:
        for run in range(1, RUNS_PER_TEMPERATURE + 1):
            print(f"Running temperature={temp}, run {run}/{RUNS_PER_TEMPERATURE}...")
            output = run_prompt(client, temp)
            results.append((temp, run, output))
            print(f"  -> {output}\n")
            time.sleep(2)  # small delay to stay well within free-tier rate limits

    # ---- Write results to a markdown table ----
    with open(OUTPUT_FILE, "w") as f:
        f.write("# Temperature Comparison Results\n\n")
        f.write(f"**Prompt used:** {PROMPT}\n\n")
        f.write("| Temperature | Run | Output |\n")
        f.write("|---|---|---|\n")
        for temp, run, output in results:
            safe_output = output.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {temp} | {run} | {safe_output} |\n")

    print(f"Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

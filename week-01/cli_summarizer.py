"""
Week 01 - Task 06: CLI Summarizer Tool

Takes a block of text (from a file OR a command-line argument) and returns:
  - a short summary
  - key points
  - overall sentiment

Usage:
    python3 cli_summarizer.py --file notes.txt
    python3 cli_summarizer.py --text "Some block of text to summarize..."
"""

import argparse
import sys

from api_wrapper import GeminiWrapper


PROMPT_TEMPLATE = """You are a text analysis assistant. Analyze the following text and respond in EXACTLY this format, with no extra commentary before or after:

SUMMARY:
<a 2-3 sentence summary of the text>

KEY POINTS:
- <key point 1>
- <key point 2>
- <key point 3>
(add more bullet points only if genuinely needed, max 6)

SENTIMENT: <one word: Positive, Negative, Neutral, or Mixed>
SENTIMENT REASON: <one sentence explaining why>

TEXT TO ANALYZE:
\"\"\"
{text}
\"\"\"
"""


def get_input_text(args) -> str:
    """Get the text to analyze, from a file or a direct string argument."""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

        if not content:
            print(f"Error: file '{args.file}' is empty.", file=sys.stderr)
            sys.exit(1)

        return content

    if args.text:
        if not args.text.strip():
            print("Error: --text was provided but is empty.", file=sys.stderr)
            sys.exit(1)
        return args.text.strip()

    print("Error: provide either --file <path> or --text \"...\"", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize text and extract key points + sentiment using Gemini."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", type=str, help="Path to a text file to analyze.")
    input_group.add_argument("--text", type=str, help="A direct block of text to analyze.")

    args = parser.parse_args()

    text = get_input_text(args)

    print(f"Analyzing {len(text)} characters of text...\n")

    wrapper = GeminiWrapper()
    prompt = PROMPT_TEMPLATE.format(text=text)
    result = wrapper.send_message(prompt, temperature=0.3)

    if not result.success:
        print(f"Analysis failed: [{result.error_type}] {result.error_message}",
              file=sys.stderr)
        sys.exit(1)

    print(result.text)
    print(f"\n(tokens used: {result.total_tokens}, attempts: {result.attempts_used})")


if __name__ == "__main__":
    main()

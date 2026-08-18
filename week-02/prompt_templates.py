"""
Week 02 - Task 01: Prompt Template Library

Reusable functions for building prompts using five core patterns:
  - zero-shot
  - few-shot
  - role/system
  - chain-of-thought
  - constrained-output

Each function returns a ready-to-send prompt string (or a tuple of
system + user prompt, where relevant), so later tasks can import and
reuse these instead of hand-writing prompts from scratch every time.

Usage:
    from prompt_templates import zero_shot, few_shot, role_prompt, \\
        chain_of_thought, constrained_output

    prompt = zero_shot("Classify the sentiment of: 'This is great!'")
"""

from typing import List, Tuple


def zero_shot(instruction: str) -> str:
    """
    Zero-shot: ask the model to do a task directly, with no examples.
    Best for simple, well-defined tasks the model already understands
    from general knowledge.
    """
    return instruction.strip()


def few_shot(instruction: str, examples: List[Tuple[str, str]], new_input: str) -> str:
    """
    Few-shot: show the model a handful of input/output examples before
    asking it to do the same thing on a new input. Improves consistency
    and format-matching for tasks where "show, don't tell" works better
    than instructions alone.

    examples: list of (input, output) pairs
    """
    parts = [instruction.strip(), ""]
    for i, (ex_input, ex_output) in enumerate(examples, start=1):
        parts.append(f"Example {i}:")
        parts.append(f"Input: {ex_input}")
        parts.append(f"Output: {ex_output}")
        parts.append("")
    parts.append(f"Input: {new_input}")
    parts.append("Output:")
    return "\n".join(parts)


def role_prompt(role_description: str, task: str) -> Tuple[str, str]:
    """
    Role/system: sets persistent behavior via a system prompt, separate
    from the actual user request. Returns (system_prompt, user_prompt)
    since these are sent as two separate roles, not concatenated into
    one string.
    """
    system_prompt = role_description.strip()
    user_prompt = task.strip()
    return system_prompt, user_prompt


def chain_of_thought(question: str) -> str:
    """
    Chain-of-thought: explicitly asks the model to reason step by step
    before giving a final answer. Improves accuracy on tasks involving
    logic, math, or multi-step reasoning, at the cost of longer/slower
    responses.
    """
    return (
        f"{question.strip()}\n\n"
        "Think through this step by step, showing your reasoning, "
        "then give your final answer on a new line starting with "
        "'Final Answer:'."
    )


def constrained_output(instruction: str, output_format: str) -> str:
    """
    Constrained-output: forces the model's response into a specific,
    parseable format (e.g. JSON, a fixed set of labels, a strict
    template) so downstream code can reliably process it without
    guessing at the structure.
    """
    return (
        f"{instruction.strip()}\n\n"
        f"Respond ONLY in the following format, with no extra text, "
        f"explanation, or commentary before or after it:\n\n"
        f"{output_format.strip()}"
    )


if __name__ == "__main__":
    # Quick demonstration of each pattern (prints prompts, does not call the API)
    print("=== Zero-shot ===")
    print(zero_shot("Summarize the plot of a mystery novel in one sentence."))

    print("\n=== Few-shot ===")
    examples = [
        ("I love this product!", "Positive"),
        ("This is terrible, I want a refund.", "Negative"),
    ]
    print(few_shot(
        "Classify the sentiment of each input as Positive, Negative, or Neutral.",
        examples,
        "The delivery was on time but the box was a bit damaged.",
    ))

    print("\n=== Role/System ===")
    system, user = role_prompt(
        "You are a senior cybersecurity analyst who explains concepts "
        "clearly to junior interns, using precise but accessible language.",
        "Explain what a zero-day vulnerability is.",
    )
    print(f"[system]: {system}")
    print(f"[user]: {user}")

    print("\n=== Chain-of-thought ===")
    print(chain_of_thought(
        "A server handles 120 requests per minute. If traffic increases "
        "by 25% during peak hours, how many requests per minute does it "
        "handle at peak?"
    ))

    print("\n=== Constrained-output ===")
    print(constrained_output(
        "Analyze this support ticket: 'My login isn't working and I need "
        "this fixed today, it's blocking my whole team.'",
        '{"category": "<string>", "priority": "<low|medium|high>", '
        '"sentiment": "<positive|neutral|negative>"}',
    ))

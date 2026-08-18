# Week 02 — Task 01: Prompt Template Library

A reusable library of five core prompting patterns, implemented in `prompt_templates.py`. These are used as building blocks for Tasks 02–06 this week.

## The Five Patterns

### 1. Zero-shot
Ask the model to do a task directly, with no examples given. Works well when the task is simple, common, or well-defined enough that the model already "knows" the expected format from its training.

**When to use:** simple classification, straightforward Q&A, general knowledge tasks.
**Trade-off:** less reliable output formatting on ambiguous or unusual tasks.

### 2. Few-shot
Show the model a handful of input → output examples before giving it a new input to process. The model pattern-matches the style, format, and reasoning shown in the examples.

**When to use:** when you need consistent formatting, a specific tone, or a task the model doesn't naturally do in a standard way.
**Trade-off:** uses more tokens per call (the examples themselves cost tokens), and output quality depends heavily on how representative your examples are.

### 3. Role/System
Sets persistent behavior, tone, or expertise via a system prompt, separate from the actual user request. This shapes *every* response in a session, not just one specific instruction.

**When to use:** whenever you want consistent persona, tone, or constraints applied across an entire conversation or tool, not just a single prompt.
**Trade-off:** doesn't guarantee compliance on its own — still needs to be combined with clear instructions in the user prompt for best results.

### 4. Chain-of-thought
Explicitly asks the model to reason step-by-step before giving a final answer, rather than jumping straight to a conclusion.

**When to use:** math, logic, multi-step reasoning, anything where "thinking out loud" measurably improves accuracy.
**Trade-off:** slower and more expensive (more output tokens), and the reasoning itself can occasionally contain errors even if the final answer is right (or vice versa) — worth double-checking on high-stakes tasks.

### 5. Constrained-output
Forces the model's response into a specific, strictly parseable format (JSON, fixed labels, a defined template) so downstream code can process it reliably without fragile string-parsing guesswork.

**When to use:** any time the output needs to be consumed programmatically — feeding into a database, another function, a UI, etc. This is the pattern Task 02 builds directly on top of.
**Trade-off:** models can still occasionally violate the format (extra commentary, malformed JSON), which is exactly why Task 02 adds schema validation and automatic retry on top of this pattern.

## How These Combine

These patterns aren't mutually exclusive — most real prompts combine two or three. For example, Task 03's classifier will likely use **role/system** (to set the persona of a support triage assistant) + **constrained-output** (to force valid JSON) + arguably **few-shot** (to show a couple of example classifications for consistency).

## Usage

```python
from prompt_templates import zero_shot, few_shot, role_prompt, chain_of_thought, constrained_output

# Zero-shot
prompt = zero_shot("Summarize this text in one sentence: ...")

# Few-shot
examples = [("I love this!", "Positive"), ("This is bad.", "Negative")]
prompt = few_shot("Classify sentiment:", examples, "It was okay I guess.")

# Role/system (returns a tuple — sent as two separate roles)
system, user = role_prompt("You are a helpful assistant.", "Explain gravity.")

# Chain-of-thought
prompt = chain_of_thought("If a train travels 60mph for 2.5 hours, how far does it go?")

# Constrained-output
prompt = constrained_output(
    "Analyze this ticket: ...",
    '{"category": "<string>", "priority": "<low|medium|high>"}'
)
```

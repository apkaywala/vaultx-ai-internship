# Task 04 — Temperature Experiment Analysis

**Prompt used:** Write a one-sentence tagline for a cybersecurity startup.
**Model:** gemini-flash-latest

## Results Table

| Temperature | Run | Output |
|---|---|---|
| 0.0 | 1 | Intelligent defense for a fearless digital future. |
| 0.0 | 2 | Invisible protection for fearless innovation. |
| 0.0 | 3 | Intelligent defense for an unpredictable digital world. |
| 0.7 | 1 | Stopping tomorrow's cyber threats before they disrupt today. |
| 0.7 | 2 | Securing tomorrow's innovations from today's unseen threats. |
| 0.7 | 3 | Securing your digital world today so you can innovate fearlessly tomorrow. |
| 1.0 | 1 | Outsmarting tomorrow's threats, so you can innovate without fear. |
| 1.0 | 2 | Proactive defense for a fearless digital future. |
| 1.0 | 3 | Securing your digital frontier, so you can innovate without fear. |

## How Variance Changes

The most notable finding: **temperature 0 did not produce identical outputs across all three runs**, even though in theory a temperature of 0 should make the model deterministically pick the single most probable token every time, giving the same output on repeat calls. All three runs were different sentences ("Intelligent defense...", "Invisible protection...", "Intelligent defense for an unpredictable..."), though they stayed close in theme and length.

This shows that "temperature 0" is not a hard guarantee of determinism in practice. A few likely reasons: the model may use additional sampling parameters (like top-k or top-p) that aren't fully overridden by setting temperature alone, floating-point non-determinism can occur in how the model computes probabilities across different hardware/batches, and some hosted models apply a small amount of built-in randomness regardless of temperature for load-balancing or safety reasons. So temperature 0 should be understood as "heavily biased toward the most likely output," not "output guaranteed identical every time."

At **temperature 0.7**, the three outputs diverged more in structure and wording than at 0.0 — different sentence openings ("Stopping...", "Securing...", "Securing...") and different phrasing choices, while all three stayed coherent, on-topic, and roughly similar in length. This matches the expected "balanced" behavior: more variety than temperature 0, but still controlled and usable.

At **temperature 1.0**, outputs were noticeably more varied in tone and word choice ("Outsmarting", "Proactive defense", "Securing your digital frontier") compared to 0.0, though interestingly not dramatically more different from 0.7 in this particular run — likely because the prompt itself is short and constrained (a one-sentence tagline naturally limits how wild the output can get, regardless of temperature). With a longer, more open-ended prompt, the difference between 0.7 and 1.0 would likely be more pronounced.

**Overall pattern observed:** variance increased from temperature 0.0 to 0.7, but the jump from 0.7 to 1.0 was smaller than expected — a useful reminder that temperature's effect also depends on the prompt itself, not just the parameter value.

## Which Temperature for Which Use Case

**Support bot → Temperature ~0–0.2**
A support bot needs consistent, predictable, accurate answers every time a user asks the same or similar question. Based on this experiment, even temperature 0 isn't perfectly deterministic, but it still produces the most focused, low-variance output of the three settings — the closest to reliable and repeatable, which is what users expect from support responses.

**Code generator → Temperature ~0–0.3**
Code needs to be syntactically correct and logically consistent. Creative variation is actively harmful here — a low temperature keeps the model close to its most statistically confident pattern for a given problem, minimizing the risk of introducing subtle bugs through "creative" but incorrect alternatives.

**Marketing copy tool → Temperature ~0.7–1.0**
Marketing content benefits from variety — the whole point is often generating multiple different angles to choose from. The 0.7 and 1.0 results in this experiment both produced usable, on-brand taglines with different emotional angles ("outsmarting threats" vs. "proactive defense" vs. "securing your frontier"), which is exactly the kind of creative range a marketing tool should offer.

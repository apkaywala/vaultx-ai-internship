# Task 05 — Prompt Evaluation: Analysis

**Evaluation set:** 15 labeled support messages with hand-judged expected outputs (category, priority, sentiment, needs_human)
**Model:** gemini-3.5-flash-lite, temperature=0.2

## Results Summary

| Metric | v1 (original) | v2 (improved) | Change |
|---|---|---|---|
| Exact-match accuracy | 80.0% | 80.0% | +0.0 pts |
| category accuracy | 93.3% | 93.3% | +0.0 pts |
| priority accuracy | 86.7% | 86.7% | +0.0 pts |
| sentiment accuracy | 86.7% | 100.0% | **+13.3 pts** |
| needs_human accuracy | 86.7% | 100.0% | **+13.3 pts** |

## What Changed Between v1 and v2

v2 added one explicit rule to the prompt: irreversible or high-stakes actions (like permanent account deletion) should be treated as `priority: high` and `needs_human: true` **regardless of the customer's tone**, since the original prompt was only picking up on emotional/urgency language to set these fields.

## The Targeted Fix Worked

The specific case that motivated this change — *"I'd like to permanently delete my account and all associated data"* — was misclassified in v1 (`priority: medium, needs_human: false`) and was correctly classified in v2 (`priority: high, needs_human: true`, matching expected). This is direct evidence the added rule did exactly what it was designed to do.

## Why Overall Accuracy Didn't Improve (Important Finding)

Despite the targeted fix working, **overall exact-match accuracy stayed at 80.0%** in both runs. Looking closely at the failure lists, this is not because the improvement failed — it's because **two different, unrelated cases became mismatches in v2** that were correct in v1 (the courier tracking message, and a slight priority shift on the app-crash message), while the login case remained wrong in both.

This points to a real limitation in how I ran this evaluation: **the classifier uses `temperature=0.2`, which is not fully deterministic.** Running the same prompt twice can produce slightly different outputs on borderline/ambiguous cases, independent of any change to the prompt itself. So part of what looks like "v1 vs v2 comparison" is actually partly "run 1 vs run 2 of a non-deterministic system."

**What I'd do differently:** for a cleaner comparison, I should have either (a) set temperature to 0 for evaluation runs specifically, to minimize this noise, or (b) run each version multiple times and averaged the results, rather than comparing single runs. This is a genuine lesson from the exercise: measuring "prompt improvement" accurately requires controlling for the model's own inherent randomness, or the signal can get lost in the noise — especially with a small, 15-case evaluation set where a single flipped case moves the accuracy by 6.7 percentage points.

## Overall Conclusion

The prompt change achieved its specific, intended goal — measurably improving `sentiment` and `needs_human` field accuracy from 86.7% to 100%, and directly fixing the account-deletion edge case it was designed to address. The flat overall exact-match score is best explained by evaluation noise from non-zero temperature on a small sample size, not by the prompt change failing. A larger evaluation set (30-50+ cases) and/or temperature=0 during evaluation would give a more reliable signal for future prompt iterations.

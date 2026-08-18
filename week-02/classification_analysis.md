# Task 03 — Classification Tool: Results & Analysis

**Model used:** gemini-3.5-flash-lite
**Samples tested:** 20 realistic support messages
**Success rate:** 20/20 (100%) returned valid JSON matching the schema on the first attempt

## Results Table

*(Insert the full table from `classification_results.md` here — see the generated file.)*

## Observations

**Category assignment looked accurate across the board.** Billing issues (double charges, refunds, subscription errors, tax disputes) were consistently tagged `billing`; technical complaints (app crashes, checkout errors, UI bugs) went to `technical`; delivery-related messages correctly went to `shipping`; and simple questions or feedback defaulted to `general`. No obvious miscategorizations stood out on manual review.

**Priority correlated well with actual urgency language.** Messages containing words like "URGENT," repeated failed attempts, or explicit frustration ("no one has responded in 3 days") were consistently marked `high`. Simple informational questions ("What are your business hours?", "Is there a mobile app?") were correctly marked `low`. This suggests the model is picking up on genuine urgency signals rather than just keyword matching — e.g. sample #13 (account deletion request) was marked `medium`, not `high`, even though it sounds serious, likely because there's no explicit urgency or distress in the wording itself.

**`needs_human` tracked closely with financial/emotional stakes.** Every message involving money going wrong (double charges, overcharges, refund requests, tax disputes) was flagged `needs_human: true`, while simple technical bugs and general questions were flagged `false`. This matches the intent of the guideline given in the prompt — refunds and billing disputes are exactly the kind of thing that benefits from human judgment rather than an automated response.

**One genuinely interesting edge case: sample #13** ("I'd like to delete my account and all my data permanently") was marked `needs_human: false`. This is arguably debatable — account deletion is a significant, sometimes irreversible action that many real support teams would want a human to confirm. This is worth flagging as a limitation: the model's `needs_human` heuristic seems to weight financial/emotional distress more heavily than "high-stakes but calmly stated" requests. In a real deployment, I'd consider explicitly adding "account deletion or data removal requests" as an automatic `needs_human: true` trigger in the prompt instructions, rather than leaving it to the model's judgment alone.

## Accuracy Assessment

Manually reviewing all 20 classifications against what I'd expect a human triage agent to assign, I judged **19/20 (95%) as fully correct**, with the one debatable case being sample #13's `needs_human` flag as discussed above. Category and sentiment fields were 20/20 accurate by my judgment; priority was also strong, though "medium vs. high" is inherently somewhat subjective for a few borderline cases (e.g. sample #7, login issues — arguably could be `high` if the customer has been locked out for a long time, though the message itself doesn't state that).

## Limitations Noted

- All 20 samples succeeded on the first attempt with no retries needed, which is good evidence of prompt reliability but means I don't have direct evidence of the retry-on-invalid-JSON path firing during this specific test run (that behavior was separately verified in Task 02).
- The sample set, while varied, is still relatively clean English text with clear intent. Real-world support messages are often messier (typos, multiple issues in one message, non-English text), which could stress-test the classifier differently than shown here.

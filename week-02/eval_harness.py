"""
Week 02 - Task 05: Evaluation Harness

Builds a labeled evaluation set (message + expected classification),
runs the classifier against it, and measures per-field accuracy.
Used to compare prompt v1 (original) against prompt v2 (improved) and
record the measured improvement.
"""

import time
from typing import Callable, Dict, List

from api_wrapper import GeminiWrapper


# ---- Evaluation set: 15 labeled cases ----
# "expected" values are my own judgment of what a correct classification
# should be, used as ground truth for scoring.
EVAL_CASES: List[Dict] = [
    {
        "message": "I've been charged twice for the same order and no one has responded in 3 days!",
        "expected": {"category": "billing", "priority": "high", "sentiment": "negative", "needs_human": True},
    },
    {
        "message": "What are your business hours?",
        "expected": {"category": "general", "priority": "low", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "The app crashes every time I open settings.",
        "expected": {"category": "technical", "priority": "medium", "sentiment": "negative", "needs_human": False},
    },
    {
        "message": "Thank you so much, your support team fixed my issue instantly!",
        "expected": {"category": "general", "priority": "low", "sentiment": "positive", "needs_human": False},
    },
    {
        "message": "URGENT: my card was charged $500 instead of $50, fix this now!",
        "expected": {"category": "billing", "priority": "high", "sentiment": "negative", "needs_human": True},
    },
    {
        "message": "I'd like to permanently delete my account and all associated data.",
        "expected": {"category": "account", "priority": "high", "sentiment": "neutral", "needs_human": True},
    },
    {
        "message": "Is there a mobile app available for Android?",
        "expected": {"category": "general", "priority": "low", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "My tracking number doesn't work on the courier's website.",
        "expected": {"category": "shipping", "priority": "medium", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "Can I get a refund? I changed my mind about the purchase.",
        "expected": {"category": "billing", "priority": "medium", "sentiment": "neutral", "needs_human": True},
    },
    {
        "message": "Small bug: dark mode toggle doesn't save after refresh.",
        "expected": {"category": "technical", "priority": "low", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "I've emailed three times about my missing refund, nobody replies. Unacceptable.",
        "expected": {"category": "billing", "priority": "high", "sentiment": "negative", "needs_human": True},
    },
    {
        "message": "Do you offer student discounts?",
        "expected": {"category": "general", "priority": "low", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "My subscription renewed but I cancelled it last month, please explain.",
        "expected": {"category": "billing", "priority": "high", "sentiment": "negative", "needs_human": True},
    },
    {
        "message": "I can't log in, it says invalid credentials but my password is correct.",
        "expected": {"category": "account", "priority": "medium", "sentiment": "neutral", "needs_human": False},
    },
    {
        "message": "The checkout page errors out when I apply my coupon code.",
        "expected": {"category": "technical", "priority": "medium", "sentiment": "neutral", "needs_human": False},
    },
]


def run_evaluation(classify_fn: Callable, wrapper: GeminiWrapper, label: str) -> Dict:
    """
    Runs classify_fn against every case in EVAL_CASES, compares to
    expected values, and returns accuracy stats per field + overall.
    """
    field_correct = {"category": 0, "priority": 0, "sentiment": 0, "needs_human": 0}
    exact_match_count = 0
    total = len(EVAL_CASES)
    failures = []

    print(f"\n--- Running evaluation: {label} ---")

    for i, case in enumerate(EVAL_CASES, start=1):
        result = classify_fn(case["message"], wrapper=wrapper)

        if not result.success:
            failures.append({"message": case["message"], "reason": result.error_message})
            time.sleep(1.5)
            continue

        actual = result.data.model_dump()
        expected = case["expected"]

        is_exact_match = True
        for field in field_correct:
            if actual.get(field) == expected.get(field):
                field_correct[field] += 1
            else:
                is_exact_match = False

        if is_exact_match:
            exact_match_count += 1
        else:
            failures.append({
                "message": case["message"],
                "expected": expected,
                "actual": actual,
            })

        print(f"[{i}/{total}] {'MATCH' if is_exact_match else 'mismatch'}: {case['message'][:50]}...")
        time.sleep(1.5)

    field_accuracy = {k: round(v / total * 100, 1) for k, v in field_correct.items()}
    exact_match_accuracy = round(exact_match_count / total * 100, 1)

    return {
        "label": label,
        "total_cases": total,
        "field_accuracy": field_accuracy,
        "exact_match_accuracy": exact_match_accuracy,
        "failures": failures,
    }


def print_report(report: Dict):
    print(f"\n=== Results: {report['label']} ===")
    print(f"Exact-match accuracy (all 4 fields correct): {report['exact_match_accuracy']}%")
    print("Per-field accuracy:")
    for field, acc in report["field_accuracy"].items():
        print(f"  {field}: {acc}%")
    if report["failures"]:
        print(f"\n{len(report['failures'])} case(s) with mismatches or errors:")
        for f in report["failures"]:
            print(f"  - {f}")


if __name__ == "__main__":
    from classifier import classify_message, classify_message_v2

    wrapper = GeminiWrapper()

    report_v1 = run_evaluation(classify_message, wrapper, label="Classifier v1 (original prompt)")
    print_report(report_v1)

    report_v2 = run_evaluation(classify_message_v2, wrapper, label="Classifier v2 (improved prompt)")
    print_report(report_v2)

    print("\n=== Improvement Summary (v1 -> v2) ===")
    delta = report_v2["exact_match_accuracy"] - report_v1["exact_match_accuracy"]
    print(f"Exact-match accuracy: {report_v1['exact_match_accuracy']}% -> "
          f"{report_v2['exact_match_accuracy']}% ({'+' if delta >= 0 else ''}{round(delta, 1)} points)")
    for field in report_v1["field_accuracy"]:
        d = report_v2["field_accuracy"][field] - report_v1["field_accuracy"][field]
        print(f"  {field}: {report_v1['field_accuracy'][field]}% -> "
              f"{report_v2['field_accuracy'][field]}% ({'+' if d >= 0 else ''}{round(d, 1)} points)")

    # Save comparison to markdown for the report
    with open("eval_comparison.md", "w") as f:
        f.write("# Task 05 — Prompt Evaluation: v1 vs v2\n\n")
        f.write(f"**Evaluation set size:** {report_v1['total_cases']} cases\n\n")
        f.write("| Metric | v1 (original) | v2 (improved) | Change |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| Exact-match accuracy | {report_v1['exact_match_accuracy']}% | "
                f"{report_v2['exact_match_accuracy']}% | "
                f"{'+' if delta >= 0 else ''}{round(delta, 1)} pts |\n")
        for field in report_v1["field_accuracy"]:
            d = report_v2["field_accuracy"][field] - report_v1["field_accuracy"][field]
            f.write(f"| {field} accuracy | {report_v1['field_accuracy'][field]}% | "
                    f"{report_v2['field_accuracy'][field]}% | "
                    f"{'+' if d >= 0 else ''}{round(d, 1)} pts |\n")
        f.write("\n## v1 Failures\n")
        for fail in report_v1["failures"]:
            f.write(f"- {fail}\n")
        f.write("\n## v2 Failures\n")
        for fail in report_v2["failures"]:
            f.write(f"- {fail}\n")

    print("\nComparison saved to eval_comparison.md")

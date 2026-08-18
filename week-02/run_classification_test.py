"""
Week 02 - Task 03: Classifier Test Harness

Runs the classifier against 20 realistic support message samples and
writes the results to a markdown table for the report.
"""

import time
from classifier import classify_message
from api_wrapper import GeminiWrapper

SAMPLES = [
    "I've been charged twice for the same order and no one has responded to my emails in 3 days!",
    "How do I change my billing address? Can't find the option anywhere.",
    "The app crashes every single time I try to open the settings page.",
    "Just wanted to say your support team was amazing yesterday, thank you!",
    "My package says delivered but I never received it. This is the second time this month.",
    "What are your business hours?",
    "I can't log into my account, it says 'invalid credentials' but I'm sure my password is right.",
    "Can I get a refund for my last purchase? I changed my mind.",
    "Your website is really easy to use, just leaving positive feedback.",
    "URGENT: my card was charged $500 instead of $50, need this fixed immediately!!",
    "Is there a mobile app available for Android?",
    "The tracking number you gave me doesn't work on the courier's website.",
    "I'd like to delete my account and all my data permanently.",
    "Small bug: the dark mode toggle doesn't save after I refresh the page.",
    "I've emailed three times about my missing refund and nobody has replied. This is unacceptable.",
    "Do you offer student discounts?",
    "My subscription renewed but I cancelled it last month, please explain.",
    "Everything works great, no issues, just exploring the settings.",
    "The checkout page keeps giving me an error when I try to apply my coupon code.",
    "I was overcharged sales tax on my last invoice, can someone review this?",
]


def main():
    wrapper = GeminiWrapper()
    results = []

    print(f"Classifying {len(SAMPLES)} sample messages...\n")

    for i, message in enumerate(SAMPLES, start=1):
        print(f"[{i}/{len(SAMPLES)}] {message[:60]}...")
        result = classify_message(message, wrapper=wrapper)

        if result.success:
            data = result.data.model_dump()
            results.append({
                "message": message,
                "category": data["category"],
                "priority": data["priority"],
                "sentiment": data["sentiment"],
                "needs_human": data["needs_human"],
                "status": "OK",
            })
        else:
            results.append({
                "message": message,
                "category": "-",
                "priority": "-",
                "sentiment": "-",
                "needs_human": "-",
                "status": f"FAILED: {result.error_message}",
            })

        time.sleep(1.5)  # stay safely within free-tier rate limits

    # ---- Write results to a markdown table ----
    with open("classification_results.md", "w") as f:
        f.write("# Task 03 — Classification Results (20 samples)\n\n")
        f.write("| # | Message | Category | Priority | Sentiment | Needs Human | Status |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(results, start=1):
            msg_short = r["message"].replace("|", "\\|")
            if len(msg_short) > 70:
                msg_short = msg_short[:67] + "..."
            f.write(
                f"| {i} | {msg_short} | {r['category']} | {r['priority']} | "
                f"{r['sentiment']} | {r['needs_human']} | {r['status']} |\n"
            )

    success_count = sum(1 for r in results if r["status"] == "OK")
    print(f"\nDone. {success_count}/{len(SAMPLES)} classified successfully.")
    print("Results saved to classification_results.md")


if __name__ == "__main__":
    main()

# Task 05 — Prompt Evaluation: v1 vs v2

**Evaluation set size:** 15 cases

| Metric | v1 (original) | v2 (improved) | Change |
|---|---|---|---|
| Exact-match accuracy | 80.0% | 80.0% | +0.0 pts |
| category accuracy | 93.3% | 93.3% | +0.0 pts |
| priority accuracy | 86.7% | 86.7% | +0.0 pts |
| sentiment accuracy | 86.7% | 100.0% | +13.3 pts |
| needs_human accuracy | 86.7% | 100.0% | +13.3 pts |

## v1 Failures
- {'message': "I'd like to permanently delete my account and all associated data.", 'expected': {'category': 'account', 'priority': 'high', 'sentiment': 'neutral', 'needs_human': True}, 'actual': {'category': 'account', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}}
- {'message': "I can't log in, it says invalid credentials but my password is correct.", 'expected': {'category': 'account', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}, 'actual': {'category': 'technical', 'priority': 'medium', 'sentiment': 'negative', 'needs_human': False}}
- {'message': 'The checkout page errors out when I apply my coupon code.', 'expected': {'category': 'technical', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}, 'actual': {'category': 'technical', 'priority': 'high', 'sentiment': 'negative', 'needs_human': True}}

## v2 Failures
- {'message': 'The app crashes every time I open settings.', 'expected': {'category': 'technical', 'priority': 'medium', 'sentiment': 'negative', 'needs_human': False}, 'actual': {'category': 'technical', 'priority': 'high', 'sentiment': 'negative', 'needs_human': False}}
- {'message': "My tracking number doesn't work on the courier's website.", 'expected': {'category': 'shipping', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}, 'actual': {'category': 'shipping', 'priority': 'low', 'sentiment': 'neutral', 'needs_human': False}}
- {'message': "I can't log in, it says invalid credentials but my password is correct.", 'expected': {'category': 'account', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}, 'actual': {'category': 'technical', 'priority': 'medium', 'sentiment': 'neutral', 'needs_human': False}}

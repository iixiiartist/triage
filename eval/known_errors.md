# Known errors and label boundary decisions

This file documents two things:

1. **Known label errors** in the frozen test set. Do NOT edit `test.jsonl` to fix them — the frozen test set is frozen, including its errors. Corrections go in a future `test_v2.jsonl`.
2. **Label boundary decisions** that were judgment calls at freeze time. These aren't errors; they're the remap author's best interpretation given the taxonomy. Flag them for review only if downstream metrics show them causing problems.

---

## Label boundary decisions

### `newsletter_subscription` → `update_profile` (not `cancel_subscription`)

Bitext's `newsletter_subscription` intent covers tickets like "cancel my subscription to the newsletter". These map to `update_profile` rather than `cancel_subscription` because a newsletter opt-out is a **preference toggle** on the user's account, not a service cancellation. `cancel_subscription` is reserved for terminating a paid or provisioned service relationship.

**Edge case to watch:** if customer wording conflates "cancel my subscription" (newsletter) with "cancel my subscription" (paid product) and routing confusion shows up downstream (billing team getting newsletter opt-outs, or account team getting service cancellations), revisit this remap. Likely fix: split by keyword heuristic or introduce a `newsletter_optout` intent.

**When to revisit:** if >5% of `update_profile` tickets in production look like they wanted a paid-service cancellation, or vice versa.

---

### `general_greet` → `out_of_scope`

MASSIVE's `general_greet` covers voice-assistant greetings ("hi Alexa", "hello"). These are unambiguously off-topic for a customer-support triage system, so they map to `out_of_scope` → `auto_close`.

**Edge case to watch:** a bare "hi" in a real customer support inbox is different — it's usually the first message in an unstructured conversation, not a throwaway greeting to a voice assistant. If SAM-Intent ends up classifying those inbox openers as `out_of_scope` and auto-closing them, we've misrouted a real support conversation.

**When to revisit:** if production traffic shows a meaningful rate of single-word-greeting tickets getting auto-closed, split `general_greet` style training data away from `out_of_scope` and into `unclear` (routes to human_escalation) instead. Requires re-freeze.

---

## Known errors in frozen test set

_None yet. Entries should include the test `id`, the intended label, and the observed label. Format:_

```text
- `massive_fr_xxxxxxxxxxxx` — text says "<snippet>" — frozen label is `X`, correct label would be `Y`. Noticed during <when>. Fix lands in test_v2.
```

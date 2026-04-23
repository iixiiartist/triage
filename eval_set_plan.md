# Triage Pilot — Eval Set Plan

The frozen test set is the single most load-bearing artifact in Phase 0. Every Phase 1+ claim about SAM quality traces back to it. Get this right once.

---

## Principles

1. **Freeze early, freeze hard.** Once the test set hash is committed, the test set does not change. More test data goes into `test_v2.jsonl`, not into `test.jsonl`.
2. **No data leakage.** No ticket appears in both train and test. Dedup on normalized ticket text before splitting.
3. **Stratified splits.** Each SAM's label distribution is preserved across train / val / test.
4. **Minimum 30 test examples per class.** Below this, metrics are noise. Classes below threshold get merged or dropped, with the decision documented.
5. **Human-reviewed sanity samples.** One example per class, eyeballed for label correctness before the test set is frozen.

---

## Data sources

### Public ticket datasets (primary)

Candidate sources — pick 2–3, don't try to use all:

- **Bitext Customer Support Dataset** (HuggingFace) — ~27K labeled tickets with intent + category. Strong candidate for SAM-Intent.
- **Kaggle Customer Support Twitter** — ~3M tweets with company routing. Useful for SAM-Route if filtered down.
- **MultiCoNER / MASSIVE** — multilingual intent datasets. Useful for SAM-Lang (diverse language coverage) and cross-lingual SAM-Intent eval.
- **Enron emails (filtered)** — real business text with priority signals, though not tickets. Useful for SAM-Priority if augmented.

License check before including anything. Document license and attribution in `eval/DATA_SOURCES.md`.

### Synthetic augmentation (secondary)

Gemma 4 E4B generates synthetic tickets to fill gaps in the public data — specifically:

- Rare intent classes (e.g., `security_incident`, `legal_escalation`)
- Non-English language coverage for SAM-Lang if public datasets skew English
- Edge-case priority examples (P1 incidents are underrepresented in most public data)

**Synthetic data goes in TRAIN ONLY.** Test set is 100% real. This is non-negotiable — if the test set contains model-generated examples, we're measuring whether SAMs can mimic E4B, not whether they solve the task.

---

## Label schemas

Locked during Checkpoint 3. Initial draft:

### SAM-Lang

Output: ISO 639-1 code from a fixed set of ~20 languages.

Starting set: en, es, fr, de, pt, it, nl, ja, zh, ko, ar, ru, pl, tr, sv, hi, id, vi, th, `other`.

The `other` bucket catches everything not in the top 20. Anything below 100 training examples collapses into `other`.

### SAM-Intent

Output: one of 20–40 intent labels. Draft taxonomy:

- Billing: `billing_question`, `billing_dispute`, `refund_request`, `cancel_subscription`
- Account: `password_reset`, `account_access`, `update_profile`, `delete_account`
- Product: `how_to`, `feature_request`, `bug_report`, `compatibility_question`
- Order: `order_status`, `shipping_question`, `return_request`, `damaged_item`
- Support tier: `technical_issue`, `escalation_request`, `complaint`, `compliment`
- Meta: `spam`, `unclear`, `other`

Final list locked in Checkpoint 3 after reviewing real label distributions in the public data.

### SAM-Priority

Output: P1 / P2 / P3 / P4.

Starting rubric:
- **P1** — service down, data loss, security incident, legal threat, VIP customer complaint
- **P2** — feature broken for a user, billing dispute, account lockout
- **P3** — how-to question, feature request, minor UX issue
- **P4** — informational, compliment, spam, unclear

Public data rarely has clean priority labels — this SAM will depend heavily on synthetic training data + a heuristic labeling function applied to public data, with human spot-checks for the test set.

### SAM-Route

Output: one of ~6–10 destination queues. Draft:

- `billing_team`, `technical_support`, `account_security`, `returns_and_shipping`, `product_feedback`, `legal_compliance`, `human_escalation`, `auto_close`

Largely deterministic given `(intent, priority)` — this SAM may end up as a small classifier or even a rule table with a learned tiebreaker.

---

## Split strategy

Target sizes (total, across all label classes):

| Split | Size | Purpose |
|-------|------|---------|
| Train | 20–50K | Training — grows with synthetic augmentation |
| Val | 2–5K | Hyperparameter selection during training |
| Test | 2–5K | Frozen; used only for final reported metrics |

Split method: stratified by the hardest-to-balance label (likely `intent`), with text-hash dedup across splits.

Seed: **42.** Committed to `shared/data/splits.py` as a module constant.

---

## Freeze procedure

Run `notebooks/phase0_eval_set_freeze.ipynb` (to be built in Checkpoint 3). It will:

1. Load public datasets from HuggingFace, filter/normalize
2. Apply label schemas, drop or merge low-support classes
3. Dedup on normalized text
4. Stratified 90/5/5 train/val/test split with seed=42
5. Write `train.jsonl`, `val.jsonl`, `test.jsonl` to Drive
6. Compute SHA256 of `test.jsonl`, write to `eval/test_set_hash.txt`
7. Run class distribution audit, write to `eval/class_distribution.md`
8. Sample one example per class for human review, write to `eval/spot_check_samples.md`
9. Commit the hash, distribution, and samples to the repo (data files stay in Drive)

After commit, the test set is frozen.

---

## What "frozen" means in practice

- Training code is not allowed to read `test.jsonl` ever
- Eval code reads `test.jsonl` and verifies the SHA256 matches `test_set_hash.txt` before computing metrics — if the hash doesn't match, eval fails loudly
- If you discover a labeling error in the test set, you document it in `eval/known_errors.md` but do not fix it — the error is part of the frozen benchmark. Fix in `test_v2.jsonl` later.

This discipline is what makes comparisons honest across phases. Loosen it and the whole pilot's measurement story falls apart.

---

## Open questions

Deferred to Checkpoint 3 execution:

- Which specific public datasets get picked (need license review and content inspection)
- Exact intent taxonomy — will be informed by label distributions in the chosen public data
- Whether to include a multilingual test split or English-only for v1
- How much synthetic augmentation to generate before diminishing returns

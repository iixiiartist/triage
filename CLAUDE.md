# Triage Pilot — Project Context

This file is read automatically by Claude Code at the start of every session. It captures the durable context so you don't have to re-explain the project each time.

## Thesis

Sub-50M from-scratch tiny-model swarm for support ticket triage. Architectural pressure test for the Setique Specialized Action Model (SAM) stack before applying the same pattern to Project Joe (CHRO multi-agent).

Four narrow tasks, four purpose-built tiny models:

- **SAM-Lang** — language identification (2–5M params, encoder-only)
- **SAM-Intent** — intent classification (15–25M params, encoder-only)
- **SAM-Priority** — priority scoring (5–10M params)
- **SAM-Route** — routing decision (2–5M params, classifier + rules)

Total swarm ~40–50M. Compared against Gemma 4 E4B (~4B) and E2B (~2B) zero-shot baselines on a frozen eval set. Target: beat E2B on latency + cost, stay within striking distance on accuracy. Beating E4B on accuracy is stretch, not bar.

## Architectural invariants (do not violate)

1. **From-scratch, not fine-tuned.** These SAMs are trained from scratch on narrow task data. They are not distilled, not compressed, not pruned versions of a larger model. The defensibility argument is the training data moat + task specificity, not the training method.

2. **PAI (perforated backprop) lives at the orchestrator layer, not the SAM layer.** There's nothing to perforate in a 5M-param model trained from scratch. PAI applies to the Gemma 4 E2B orchestrator in a separate workstream on the Forge — not this repo.

3. **Encoder-only where the task is classification.** SAM-Lang, SAM-Intent, SAM-Route are classification problems. Don't let decoder-only-everything framing creep in. Encoder-only at sub-50M is more parameter-efficient for these tasks.

4. **Frozen test set is sacred.** Once `eval/test_set_hash.txt` is committed, `test.jsonl` does not change. Hash verification runs before every eval. Labeling errors get documented in `eval/known_errors.md` but are NOT fixed in place — fixes go in a future `test_v2.jsonl`.

5. **Synthetic data goes in train only.** Test set is 100% human-labeled public data. If synthetic data touches the test set, we're measuring whether SAMs can mimic the synthesizer, not whether they solve the task.

## Environment

- **Primary runtime:** Google Colab (T4) for most work, Vertex AI (A100 / L4) for the E4B baseline.
- **Not used here:** the Forge (RTX 2070). That machine is reserved for PAI + Gemma 4 E2B orchestrator work, a different workstream.
- **Data lives in Drive:** `/content/drive/MyDrive/setique/triage/` — `data/processed/` for splits, `eval/` for hashes and audits, `baselines/` for results.
- **T4 constraint:** no native BF16 (compute capability 7.5). Use FP16 mixed precision. BF16 only if running on L4 / A100.

## Current phase

**Phase 0 — preflight.** Four checkpoints, exit criteria in `phase0_preflight.md`:

1. Environment audit (`notebooks/phase0_env_audit.ipynb`)
2. Repo scaffold (this repo)
3. Eval set freeze (`notebooks/phase0_eval_set_freeze.ipynb`)
4. Baselines (`notebooks/phase0_baselines_e4b.ipynb`, `phase0_baselines_e2b.ipynb`)

Phase 1 starts after all four are green. Phase 1 = SAM-Lang training (lowest risk, validates NICO plumbing with a clean win before tackling SAM-Intent).

## What NICO is

NICO is the orchestration layer that sits on top of the four SAMs. Not implemented in Phase 0 — design docs only in `nico/`. v1 will include per-customer per-SAM configuration (confidence thresholds, class suppression, routing enables, escalation policy) backed by SQLite. Escalation pattern: if SAM confidence < threshold, route to orchestrator (prompted Gemma 4 E2B) or human queue per customer config.

## v2 parking lot (do not implement in v1)

These are in `nico/v2_candidates.md`:

- Shared encoder + swappable heads across SAMs
- E2B-as-teacher distillation for SAM warm starts
- Online adaptation from customer feedback

Parking them is load-bearing for getting v1 shipped. Don't let them leak back in.

## Decision log convention

Dated decisions live in `nico/DECISION_LOG.md` using this format:

```
## YYYY-MM-DD — TYPE — Short title

**Context.** What led to this?
**[Decision/Experiment/Observation/Question/Correction].** What's the entry?
**Data/Evidence.** Config, seeds, metrics, alternatives considered.
**Implication.** What does this mean for next steps?
**Next action.** What concrete thing happens because of this?
```

## Code conventions

- Python 3.11+
- `ruff` + `black` via pre-commit
- Pinned `requirements.txt` — update only after an env audit run confirms new versions work
- Seed everything to 42 unless there's a specific reason to vary
- All training loops use `shared.training.seeds.set_all_seeds(seed)` — do not roll your own
- Metrics go through `shared.metrics.*` — do not reimplement F1 per SAM
- Configs are YAML under `sams/<sam_name>/configs/`

## Things I (the human) keep forgetting and want Claude Code to remind me about

- Always verify the test set hash before running any eval
- Update `nico/DECISION_LOG.md` when making non-trivial architectural choices
- Keep `v2_candidates.md` as the dumping ground for interesting tangents — don't silently drop them, but don't implement them either
- Commit often; the repo is the source of truth, not Drive
- Check `eval/known_errors.md` before declaring a labeling problem "fixed"

## How to help me most effectively

- When I ask for code, prefer editing the existing file over creating a new one — the repo structure is intentional
- When I ask about metrics, read the latest `baselines/baseline_results.json` first rather than asking me what the numbers are
- When I propose something that contradicts an architectural invariant above, push back before implementing
- When I'm about to rerun an expensive training job, check whether the config actually changed first
- Shorter answers when the task is mechanical, longer answers when I'm making a design decision

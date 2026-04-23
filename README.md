# Triage Pilot

Sub-50M from-scratch tiny-model swarm for support ticket triage. Architectural pressure test for the Setique Specialized Action Model (SAM) stack.

## Thesis

Four narrow tasks, four purpose-built tiny models:

- **SAM-Lang** — language identification (2–5M params)
- **SAM-Intent** — intent classification (15–25M params)
- **SAM-Priority** — priority scoring (5–10M params)
- **SAM-Route** — routing decision (2–5M params)

Total swarm ~40–50M. Compared against Gemma 4 E4B (~4B) and Gemma 4 E2B (~2B) zero-shot baselines on a frozen eval set.

**PAI (perforated backprop) lives at the orchestrator layer, not the SAM layer.** These SAMs are trained from scratch — nothing to compress.

## Current phase

Phase 0 — preflight. See `notebooks/phase0_env_audit.ipynb` and `phase0_preflight.md`.

## Quickstart

```bash
pip install -r requirements.txt
# Open the Phase 0 notebooks in Colab and run top-to-bottom.
```

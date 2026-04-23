# Triage Pilot — Repo Structure

Monorepo. Four SAMs share tokenization, eval, and metrics infrastructure. Each SAM has its own training code, configs, and checkpoint directory.

## Tree

```
triage/
├── README.md                      # Thesis, quickstart, current phase status
├── requirements.txt               # Pinned versions — installable in a fresh Colab runtime
├── requirements-dev.txt           # Linters, pre-commit, local-only tools
├── .gitignore
├── .pre-commit-config.yaml        # Optional — ruff + black
│
├── shared/                        # Used by all four SAMs
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py             # JSONL/CSV → torch Dataset wrappers
│   │   ├── splits.py              # Deterministic train/val/test splitter
│   │   └── augment.py             # Synthetic augmentation helpers
│   ├── tokenization/
│   │   ├── __init__.py
│   │   └── builders.py            # Train BPE/char tokenizers per SAM as needed
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── classification.py      # Accuracy, F1 macro/micro, confusion matrix
│   │   ├── calibration.py         # ECE, reliability diagrams (for confidence thresholds)
│   │   └── latency.py             # Wall-clock + throughput measurement
│   ├── training/
│   │   ├── __init__.py
│   │   ├── loops.py               # Standard train/eval loops with FP16 AMP
│   │   ├── callbacks.py           # Checkpointing, early stopping, WandB hooks
│   │   └── seeds.py               # Deterministic seeding across random/numpy/torch
│   └── registry.py                # Model/config registry — one-line "build model for SAM-X"
│
├── sams/
│   ├── sam_lang/                  # Language ID — 2–5M params, char-level or small encoder
│   │   ├── configs/
│   │   │   └── base.yaml
│   │   ├── model.py
│   │   ├── train.py
│   │   ├── eval.py
│   │   └── README.md              # Task definition, label schema, target metrics
│   ├── sam_intent/                # Intent classification — 15–25M params, encoder-only
│   │   ├── configs/
│   │   │   └── base.yaml
│   │   ├── model.py
│   │   ├── train.py
│   │   ├── eval.py
│   │   └── README.md
│   ├── sam_priority/              # Priority scoring — 5–10M params
│   │   ├── configs/
│   │   │   └── base.yaml
│   │   ├── model.py
│   │   ├── train.py
│   │   ├── eval.py
│   │   └── README.md
│   └── sam_route/                 # Routing — 2–5M params, often classifier + rule layer
│       ├── configs/
│       │   └── base.yaml
│       ├── model.py
│       ├── train.py
│       ├── eval.py
│       └── README.md
│
├── baselines/
│   ├── gemma_e4b_zero_shot.py     # E4B prompted baseline
│   ├── gemma_e2b_zero_shot.py     # E2B prompted baseline
│   ├── prompts/                   # Frozen prompt text per SAM task
│   │   ├── sam_lang.txt
│   │   ├── sam_intent.txt
│   │   ├── sam_priority.txt
│   │   └── sam_route.txt
│   └── baseline_results.json      # Metrics output, committed to repo
│
├── eval/
│   ├── test_set_hash.txt          # SHA256 of the frozen test set — guards against drift
│   ├── class_distribution.md      # Per-SAM label balance analysis
│   └── spot_check_samples.md      # Human-reviewed samples, one per class
│
├── nico/                          # Orchestration layer — design docs for v1 (no code yet)
│   ├── DESIGN.md                  # v1 API surface including confidence thresholds + escalation
│   ├── v2_candidates.md           # Parked ideas (shared encoder, distillation, etc.)
│   └── DECISION_LOG.md            # Dated decisions — continuation of existing log
│
├── notebooks/
│   ├── phase0_env_audit.ipynb
│   ├── phase0_eval_set_freeze.ipynb
│   ├── phase0_baselines_e4b.ipynb
│   └── phase0_baselines_e2b.ipynb
│
└── scripts/
    ├── mount_drive.py             # Standard Drive mount + path setup
    ├── download_public_data.py    # Fetch public ticket datasets
    └── generate_synthetic.py      # Synthetic augmentation runner
```

## Rationale

**Why monorepo.** Four SAMs sharing a tokenization pipeline, eval harness, and metrics library means changes to shared infrastructure propagate atomically. Separate repos would mean four places to keep in sync. At this scale (sub-50M total params, ~10 config files), the monorepo cost is near zero.

**Why `shared/` is flat, not deeply namespaced.** `from shared.metrics.classification import f1_macro` is fine. Resist the urge to add a `core/` or `lib/` wrapper layer — four SAMs and a few utilities don't need enterprise package hierarchy.

**Why each SAM has its own README.** Each one has a distinct task definition, label schema, and target metrics. Having the spec live next to the code reduces "where did I decide on 20 intent labels vs 30" lookups later.

**Why `nico/` has no code in Phase 0.** Orchestration code should come after at least two SAMs are trained and you have real confidence distributions to design thresholds against. Writing NICO first would mean designing against imagined data. The design docs capture the API surface (per-customer config endpoint, audit logging, escalation policy) so Phase 6 has a starting point — but no implementation yet.

**Why baselines are a sibling directory, not inside `sams/`.** They're not SAMs. Keeping them separate makes it obvious they're the comparison point, not the deliverable.

## What's deliberately NOT in the tree

- **No `docker/`.** Colab is the primary runtime. Containerization comes later if/when deployment demands it.
- **No `tests/` at root.** Unit tests live alongside the code they test (`shared/metrics/test_classification.py`). Adding a top-level `tests/` tree is overkill at this size.
- **No `docs/`.** READMEs are sufficient. A docs site is a distraction at this phase.
- **No `web/` or `api/`.** This is a training repo, not a service.

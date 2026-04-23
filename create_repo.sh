#!/usr/bin/env bash
# Scaffold the Triage monorepo. Run from the intended parent directory.
# Usage:  bash create_repo.sh [target_dir]
# Default target_dir: ./triage

set -euo pipefail

TARGET="${1:-triage}"

if [ -e "$TARGET" ]; then
  echo "ERROR: $TARGET already exists. Aborting."
  exit 1
fi

echo "Scaffolding Triage monorepo at: $TARGET"
mkdir -p "$TARGET"
cd "$TARGET"

# Top-level files
cat > README.md <<'EOF'
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
EOF

cat > requirements.txt <<'EOF'
# Pinned versions — update after first env audit run and commit the updated file
torch==2.4.0
transformers==4.44.0
datasets==2.21.0
tokenizers==0.19.1
bitsandbytes==0.43.0
accelerate==0.33.0
numpy<2.0
scikit-learn
pyyaml
tqdm
EOF

cat > requirements-dev.txt <<'EOF'
ruff
black
pre-commit
pytest
EOF

cat > .gitignore <<'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
.env

# Checkpoints and large files
*.pt
*.bin
*.safetensors
checkpoints/
wandb/
runs/

# Data — keep out of repo, live in Drive
data/raw/
data/processed/
data/synthetic/
*.jsonl
*.csv

# Exception: commit the test_set_hash and small metric JSONs
!baselines/baseline_results.json
!eval/class_distribution.md
!eval/test_set_hash.txt

# Colab / Jupyter
.ipynb_checkpoints/
.colab/

# OS
.DS_Store
Thumbs.db
EOF

cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
EOF

# shared/
mkdir -p shared/data shared/tokenization shared/metrics shared/training
touch shared/__init__.py \
      shared/data/__init__.py shared/data/loaders.py shared/data/splits.py shared/data/augment.py \
      shared/tokenization/__init__.py shared/tokenization/builders.py \
      shared/metrics/__init__.py shared/metrics/classification.py shared/metrics/calibration.py shared/metrics/latency.py \
      shared/training/__init__.py shared/training/loops.py shared/training/callbacks.py shared/training/seeds.py \
      shared/registry.py

# sams/
for sam in sam_lang sam_intent sam_priority sam_route; do
  mkdir -p "sams/$sam/configs"
  touch "sams/$sam/configs/base.yaml" "sams/$sam/model.py" "sams/$sam/train.py" "sams/$sam/eval.py"
  cat > "sams/$sam/README.md" <<EOF
# ${sam}

Task definition, label schema, and target metrics go here. Fill in during Phase 0 Checkpoint 3 (eval set freeze).
EOF
done

# baselines/
mkdir -p baselines/prompts
touch baselines/gemma_e4b_zero_shot.py baselines/gemma_e2b_zero_shot.py \
      baselines/prompts/sam_lang.txt baselines/prompts/sam_intent.txt \
      baselines/prompts/sam_priority.txt baselines/prompts/sam_route.txt
echo '{}' > baselines/baseline_results.json

# eval/
mkdir -p eval
touch eval/test_set_hash.txt
cat > eval/class_distribution.md <<'EOF'
# Eval set class distribution

Populated during Phase 0 Checkpoint 3. One section per SAM, with counts per label for train / val / test.
EOF
cat > eval/spot_check_samples.md <<'EOF'
# Eval set spot-check samples

Human-reviewed sample (at least one per class) per SAM. Used to catch labeling errors before Phase 1.
EOF

# nico/
mkdir -p nico
cat > nico/DESIGN.md <<'EOF'
# NICO v1 — Design

**Status:** Design only. No implementation in Phase 0.

## v1 scope

- Per-customer, per-SAM configuration API: confidence thresholds, class suppression, routing enables, escalation policy
- Backed by SQLite Aggregation Ledger
- Audit logging for config changes
- Escalation pattern: if SAM-Intent confidence < threshold, route to orchestrator (Gemma 4 E2B prompted) or human queue per customer config
EOF
cat > nico/v2_candidates.md <<'EOF'
# NICO v2 candidates (parked)

Ideas that are interesting but not v1:

1. Shared encoder + swappable heads across SAMs — genuinely novel at sub-50M scale
2. E2B-as-teacher distillation for SAM warm starts (from Kimi review)
3. Online adaptation from customer-labeled feedback
EOF
cat > nico/DECISION_LOG.md <<'EOF'
# NICO Decision Log

Continuation of the existing Setique decision log format. See prior entries for template.
EOF

# notebooks/
mkdir -p notebooks
touch notebooks/phase0_env_audit.ipynb \
      notebooks/phase0_eval_set_freeze.ipynb \
      notebooks/phase0_baselines_e4b.ipynb \
      notebooks/phase0_baselines_e2b.ipynb

# scripts/
mkdir -p scripts
cat > scripts/mount_drive.py <<'EOF'
"""Standard Drive mount helper for Colab notebooks."""
import os

TRIAGE_ROOT = '/content/drive/MyDrive/setique/triage'

def mount_and_get_root():
    from google.colab import drive
    drive.mount('/content/drive', force_remount=False)
    os.makedirs(TRIAGE_ROOT, exist_ok=True)
    return TRIAGE_ROOT
EOF
touch scripts/download_public_data.py scripts/generate_synthetic.py

echo
echo "Scaffold complete: $(pwd)"
echo
echo "Next steps:"
echo "  1. cd $TARGET"
echo "  2. git init && git add . && git commit -m 'Phase 0 scaffold'"
echo "  3. Push to GitHub (private repo under Setique Labs)"
echo "  4. Copy phase0_env_audit.ipynb into notebooks/ and run in Colab"

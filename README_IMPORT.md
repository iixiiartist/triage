# Triage Pilot — Phase 0 import package

Generated artifacts from the Phase 0 planning session. Drop these into the scaffolded repo after running `create_repo.sh`.

## What's in this zip

```
triage_phase0/
├── CLAUDE.md                         → repo root (read by Claude Code on session start)
├── create_repo.sh                    → run from parent dir to scaffold the repo
├── phase0_preflight.md               → repo root — master checklist for Phase 0
├── repo_structure.md                 → repo root — directory tree + rationale
├── eval_set_plan.md                  → eval/ — data sources, label schemas, freeze procedure
├── notebooks/
│   ├── phase0_env_audit.ipynb        → notebooks/ — Checkpoint 1
│   ├── phase0_eval_set_freeze.ipynb  → notebooks/ — Checkpoint 3
│   ├── phase0_baselines_e4b.ipynb    → notebooks/ — Checkpoint 4 (run on Vertex)
│   └── phase0_baselines_e2b.ipynb    → notebooks/ — Checkpoint 4 (run on Colab T4)
└── baselines/
    ├── runner.py                     → baselines/runner.py — shared inference harness
    └── prompts/
        ├── sam_lang.txt
        ├── sam_intent.txt
        ├── sam_priority.txt
        └── sam_route.txt
```

## Install order

```bash
# 1. Scaffold the repo (creates ./triage/ with empty structure)
bash create_repo.sh triage
cd triage

# 2. Unzip this package on top — layout matches, files land in the right places
unzip ../triage_phase0.zip -d .

# 3. Verify the merge
ls CLAUDE.md notebooks/ baselines/runner.py baselines/prompts/

# 4. Initialize git and commit
git init
git add .
git commit -m "Phase 0 scaffold + preflight artifacts"
```

## Known edits needed before running

1. **Baseline notebook imports.** In both baseline notebooks, the `sys.path.insert(...)` + `from baselines_runner import ...` lines need to become:
   ```python
   sys.path.insert(0, '/path/to/triage')   # or use os.getcwd() when running from repo root
   from baselines.runner import (
       verify_test_hash, load_test_set, load_prompt,
       run_inference, merge_results,
       peak_vram_gb, reset_vram_tracking,
   )
   ```

2. **Model IDs in baseline notebooks.** `google/gemma-4-4b-it` and `google/gemma-4-2b-it` are placeholders — verify against the current HuggingFace model hub before running.

3. **Pinned library versions in `requirements.txt`.** Update to whatever Colab's runtime actually has after the first env audit run.

4. **Vertex hourly rate in E4B baseline notebook.** `INSTANCE_HOURLY_USD = 3.67` is a placeholder. Set to your actual billing rate.

## Run order (Phase 0 checkpoints)

1. `notebooks/phase0_env_audit.ipynb` — verify GPU, FP16, determinism, Drive
2. Scaffold verified + first commit pushed to GitHub
3. `notebooks/phase0_eval_set_freeze.ipynb` — load public data, lock labels, freeze test set hash
4. `notebooks/phase0_baselines_e4b.ipynb` (Vertex) then `phase0_baselines_e2b.ipynb` (Colab) — baselines

All four green → Phase 0 done → Phase 1 (SAM-Lang training) begins.

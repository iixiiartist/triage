# Triage Pilot — Phase 0 Preflight

**Goal of Phase 0.** Get the plumbing right before any model touches any data. Freeze the eval set, verify the environment, scaffold the repo, establish baselines.

**Environment.** Google Colab (T4) primary, Google Vertex AI (A100 / L4) for SAM-Intent if VRAM requires it. Forge untouched — reserved for PAI/E2B work later.

**Exit criteria.** All four checkpoints below are green before Phase 1 (SAM-Lang training) begins.

---

## Checkpoint 1: Environment audit

Run `phase0_env_audit.ipynb` in Colab. It writes `env_audit_<timestamp>.json` to Drive.

**Must confirm:**

- [ ] GPU is T4 or better (A100/L4 on Vertex if running there)
- [ ] CUDA + PyTorch versions match pinned requirements
- [ ] FP16 mixed precision works (T4 has no native BF16 — same constraint as Forge)
- [ ] bitsandbytes imports cleanly (needed for INT8 deployment path later)
- [ ] HuggingFace `transformers`, `datasets`, `tokenizers` at pinned versions
- [ ] Seed determinism test passes (same seed → same loss curve across two runs)
- [ ] Drive mount works and target data directory exists
- [ ] Free Drive space ≥ 20 GB (rough headroom for datasets + checkpoints)

**Known constraints to document in the audit output:**

- T4 FP16 only, no BF16
- T4 FA2 limited — stick to standard attention unless a task specifically demands it
- Colab session limits (disconnects, runtime caps) — plan checkpoint cadence accordingly
- Vertex: note the instance type used and any quota constraints hit

---

## Checkpoint 2: Repo structure

Monorepo scaffold for the four SAMs + shared infrastructure. See `repo_structure.md` for tree and rationale. Run `create_repo.sh` to generate.

**Must confirm:**

- [ ] Repo initialized in GitHub (private, under Setique Labs)
- [ ] Directory layout matches spec (shared/, sams/sam_lang/, sams/sam_intent/, etc.)
- [ ] `requirements.txt` pinned and installable in a fresh Colab runtime
- [ ] `.gitignore` excludes checkpoints, data, `.ipynb_checkpoints`, Colab cruft
- [ ] Pre-commit hook runs `ruff` and `black` (or equivalent) — optional but recommended
- [ ] `README.md` states the thesis (from-scratch sub-50M, four SAMs, PAI at orchestrator layer not SAM layer) so future-you doesn't forget
- [ ] First commit pushed, Colab can clone it

---

## Checkpoint 3: Eval set frozen

See `eval_set_plan.md` for data sources, split rules, label schema.

**Must confirm:**

- [ ] Data sources selected and licensing reviewed for each (public ticket datasets + synthetic augmentation plan)
- [ ] Label schemas locked for all four SAMs (language codes, intent labels, P1–P4 priority, routing destinations)
- [ ] Train/val/test splits produced with fixed seed
- [ ] Test set written to Drive as read-only, hash recorded in repo (`eval/test_set_hash.txt`)
- [ ] Distribution audit: class balance check per SAM — flag any label with <30 examples in test
- [ ] At least one human-reviewed sample per class in test (sanity check for label correctness)
- [ ] Test set size: aim for 2–5K examples total; enough for stable metrics without being unwieldy

**Freeze rule.** Once the test set hash is committed, it does not change. If you need more test data later, it goes into a separate `test_v2.jsonl`, not into this one. This is non-negotiable — it's the only way to get honest comparisons across Phase 1 through Phase 5.

---

## Checkpoint 4: Baselines run

Zero-shot Gemma 4 E4B and Gemma 4 E2B against the frozen test set for all four tasks. Numbers get written to `baselines/baseline_results.json`.

**Must confirm:**

- [ ] E4B zero-shot results recorded per SAM task (accuracy, F1 macro, latency per example, VRAM peak)
- [ ] E2B zero-shot results recorded per SAM task (same metrics)
- [ ] Prompts used are saved in `baselines/prompts/` — these become the comparison point
- [ ] Cost estimate per 1K inferences for each baseline (for the TCO story later)
- [ ] Optional: classical baselines (fastText for SAM-Lang, TF-IDF + logistic regression for the rest) if cheap to add

**Why both E4B and E2B?** E4B is the "what could a capable generalist do" ceiling. E2B is the "what's the deployable generalist alternative" — the thing you'd actually ship if you didn't have SAMs. The SAMs need to beat E2B on *at least* latency and cost, and be within striking distance on accuracy. Beating E4B on accuracy is the stretch goal, not the bar.

---

## What Phase 0 does NOT include

To avoid scope creep — these are Phase 1+:

- Any SAM training runs
- NICO orchestration code (design doc only for now)
- Confidence threshold tuning (v1 API surface is designed, not implemented)
- Distillation experiments (filed as v2 from Kimi review)
- Shared encoder + swappable heads architecture (filed as v2)

---

## Timing estimate

- Checkpoint 1 (env audit): half a session
- Checkpoint 2 (repo): one session
- Checkpoint 3 (eval set): two to three sessions — this is the load-bearing one, don't rush it
- Checkpoint 4 (baselines): one to two sessions

Total: roughly a week of part-time work if nothing breaks.

---

## Next action

Open `phase0_env_audit.ipynb` in Colab, run it top-to-bottom, commit the resulting JSON to the repo. Then move to Checkpoint 2.

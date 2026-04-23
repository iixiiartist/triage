# NICO v1 — Design

**Status:** Design only. No implementation in Phase 0.

## v1 scope

- Per-customer, per-SAM configuration API: confidence thresholds, class suppression, routing enables, escalation policy
- Backed by SQLite Aggregation Ledger
- Audit logging for config changes
- Escalation pattern: if SAM-Intent confidence < threshold, route to orchestrator (Gemma 4 E2B prompted) or human queue per customer config

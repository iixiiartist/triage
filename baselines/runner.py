"""
Shared baseline runner for Phase 0 Checkpoint 4.

Used by phase0_baselines_e4b.ipynb and phase0_baselines_e2b.ipynb to avoid
duplicating prompt construction, inference loops, and metric computation.

Lives at: triage/baselines/runner.py
"""

import json
import hashlib
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional

import torch
from sklearn.metrics import accuracy_score, f1_score, classification_report


# ---------------------------------------------------------------------------
# Test set integrity
# ---------------------------------------------------------------------------

def verify_test_hash(test_path: str, expected_hash_path: str) -> str:
    """Verify the test set matches the frozen hash. Raises if mismatched."""
    h = hashlib.sha256()
    with open(test_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    actual = h.hexdigest()

    with open(expected_hash_path) as f:
        expected = f.read().split()[0].strip()

    if actual != expected:
        raise RuntimeError(
            f'Test set hash mismatch!\n'
            f'  expected: {expected}\n'
            f'  actual:   {actual}\n'
            f'Something has changed the frozen test set. Stop and investigate.'
        )
    return actual


def load_test_set(test_path: str) -> List[dict]:
    """Load test.jsonl into a list of dicts."""
    records = []
    with open(test_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

def load_prompt(prompt_path: str) -> str:
    """Load a frozen prompt from the prompts/ directory."""
    with open(prompt_path) as f:
        return f.read()


def build_user_message(prompt_template: str, text: str) -> str:
    """Fill in {TEXT} slot. Extend as needed for per-SAM slot shapes."""
    return prompt_template.replace('{TEXT}', text)


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

def parse_label(raw_output: str, valid_labels: set, fallback: str = 'other') -> str:
    """
    Parse a model's free-text output into a valid label.

    Strategy:
      1. If the output exactly matches a valid label (case-insensitive), use it.
      2. Otherwise, return the first valid label that appears as a substring.
      3. Fall back to `fallback` if nothing matches.
    """
    if not raw_output:
        return fallback
    cleaned = raw_output.strip().split('\n')[0].strip().strip('"\'`').lower()

    # Exact match on first line
    for lbl in valid_labels:
        if cleaned == lbl.lower():
            return lbl

    # Substring match
    for lbl in valid_labels:
        if lbl.lower() in cleaned:
            return lbl

    return fallback


# ---------------------------------------------------------------------------
# Inference loop
# ---------------------------------------------------------------------------

def run_inference(
    records: List[dict],
    prompt_template: str,
    generate_fn: Callable[[str], str],
    valid_labels: set,
    target_field: str,
    fallback: str = 'other',
    limit: Optional[int] = None,
    verbose: bool = True,
) -> Dict:
    """
    Run a baseline model across the test set for one SAM task.

    Args:
        records: test set records
        prompt_template: loaded prompt with {TEXT} slot
        generate_fn: callable that takes a prompt and returns raw model output
        valid_labels: set of valid label strings for this task
        target_field: 'lang' | 'intent' | 'priority' | 'route'
        fallback: what to return when parsing fails
        limit: if set, only run on the first N records (for smoke tests)
        verbose: print progress

    Returns:
        {
          'target_field': str,
          'n': int,
          'accuracy': float,
          'f1_macro': float,
          'f1_weighted': float,
          'latency_ms_mean': float,
          'latency_ms_p50': float,
          'latency_ms_p95': float,
          'classification_report': dict,
          'confusion_samples': list,     # up to 20 misclassified examples for error analysis
          'parse_fallback_rate': float,  # how often the parser fell back
        }
    """
    if limit is not None:
        records = records[:limit]

    y_true = []
    y_pred = []
    latencies_ms = []
    fallback_count = 0
    misclassified = []

    for i, r in enumerate(records):
        true_label = r.get(target_field)
        if true_label is None:
            continue

        prompt = build_user_message(prompt_template, r['text'])

        t0 = time.perf_counter()
        raw = generate_fn(prompt)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        pred = parse_label(raw, valid_labels, fallback=fallback)
        if pred == fallback and fallback not in (true_label,):
            # Only count as fallback if the true label wasn't the fallback itself
            fallback_count += 1

        y_true.append(true_label)
        y_pred.append(pred)
        latencies_ms.append(latency_ms)

        if pred != true_label and len(misclassified) < 20:
            misclassified.append({
                'id': r.get('id'),
                'text': r['text'][:300],
                'true': true_label,
                'pred': pred,
                'raw_output': raw[:200],
            })

        if verbose and (i + 1) % 100 == 0:
            print(f'  {i+1}/{len(records)}  latest_latency={latency_ms:.0f}ms')

    # Metrics
    n = len(y_true)
    acc = accuracy_score(y_true, y_pred) if n else 0.0
    f1m = f1_score(y_true, y_pred, average='macro', zero_division=0) if n else 0.0
    f1w = f1_score(y_true, y_pred, average='weighted', zero_division=0) if n else 0.0
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0) if n else {}

    import numpy as np
    lat_array = np.array(latencies_ms) if latencies_ms else np.array([0.0])

    return {
        'target_field': target_field,
        'n': n,
        'accuracy': acc,
        'f1_macro': f1m,
        'f1_weighted': f1w,
        'latency_ms_mean': float(lat_array.mean()),
        'latency_ms_p50': float(np.percentile(lat_array, 50)),
        'latency_ms_p95': float(np.percentile(lat_array, 95)),
        'classification_report': report,
        'confusion_samples': misclassified,
        'parse_fallback_rate': fallback_count / n if n else 0.0,
    }


# ---------------------------------------------------------------------------
# Results persistence
# ---------------------------------------------------------------------------

def merge_results(results_path: str, model_name: str, results_per_sam: Dict[str, Dict],
                  metadata: Dict) -> None:
    """
    Merge per-SAM results for a given model into baselines/baseline_results.json.

    The on-disk JSON shape:
    {
      'gemma_e4b': {
        'metadata': {...},
        'sam_lang': {...},
        'sam_intent': {...},
        ...
      },
      'gemma_e2b': { ... }
    }
    """
    p = Path(results_path)
    if p.exists() and p.stat().st_size > 0:
        with open(p) as f:
            all_results = json.load(f)
    else:
        all_results = {}

    all_results[model_name] = {
        'metadata': metadata,
        **results_per_sam,
    }

    with open(p, 'w') as f:
        json.dump(all_results, f, indent=2)


# ---------------------------------------------------------------------------
# VRAM tracking helper
# ---------------------------------------------------------------------------

def peak_vram_gb() -> Optional[float]:
    if not torch.cuda.is_available():
        return None
    return torch.cuda.max_memory_allocated() / (1024**3)


def reset_vram_tracking():
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

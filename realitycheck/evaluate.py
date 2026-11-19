"""Four-class evaluation for externally predicted labels; no ML dependencies.

Predictions must be model-produced. Do not treat synthetic smoke-test fixtures
as empirical benchmark performance.
"""
import json
from collections import Counter
from pathlib import Path
from .verifier import LABELS


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def score_predictions(gold, predictions):
    gold = {r["id"]: r for r in gold}
    preds = {r.get("case_id", r.get("id")): r for r in predictions}
    missing = set(gold) - set(preds)
    if missing:
        raise ValueError(f"Missing predictions for {len(missing)} items: {sorted(missing)[:5]}")
    confusion = {lab: Counter() for lab in LABELS}
    for cid, entry in gold.items():
        true, pred = entry["gold_verdict"], preds[cid]["label"]
        if true not in LABELS or pred not in LABELS:
            raise ValueError(f"Unknown verdict in case {cid}: {true}, {pred}")
        confusion[true][pred] += 1
    precision, recall, f1 = {}, {}, {}
    for label in LABELS:
        tp = confusion[label][label]
        actual = sum(confusion[label].values())
        predicted = sum(row[label] for row in confusion.values())
        precision[label] = tp / predicted if predicted else 0.0
        recall[label] = tp / actual if actual else None
        f1[label] = 2 * tp / (actual + predicted) if actual + predicted else None
    nee = sum(confusion["NEE"].values())
    false_verdict_on_nee = (confusion["NEE"]["SUPPORTED"] + confusion["NEE"]["REFUTED"]) / nee if nee else None
    complete = sum(sum(row.values()) for row in confusion.values())
    correct = sum(confusion[label][label] for label in LABELS)
    return {
        "n": complete,
        "accuracy": correct / complete if complete else None,
        "macro_f1": sum(v for v in f1.values() if v is not None) / sum(v is not None for v in f1.values()),
        "per_class_precision": precision,
        "per_class_recall": recall,
        "per_class_f1": f1,
        "false_verdict_rate_on_true_nee": false_verdict_on_nee,
        "confusion": {k: dict(v) for k, v in confusion.items()},
    }


def cohen_kappa(labels_a, labels_b):
    """Agreement before adjudication; use independently recorded labels."""
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Need two nonempty equal-length sequences")
    n = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    counts_a, counts_b = Counter(labels_a), Counter(labels_b)
    chance = sum(counts_a[k] * counts_b[k] for k in set(counts_a) | set(counts_b)) / n**2
    return (observed - chance) / (1 - chance) if chance < 1 else 1.0 if observed == 1 else 0.0

"""Transparent aggregation of *predicted* evidence relations into a claim verdict.

The relation predictions are supplied externally (eventually by S1's relation
judge). The module deliberately separates relevance/applicability from provenance.
All score constants are *initial hypotheses* that must be tuned using DEV only.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

LABELS = ("SUPPORTED", "REFUTED", "CONFLICTING", "NEE")
RELATIONS = ("SUPPORTS", "REFUTES", "RELATED_NOT_APPLICABLE", "IRRELEVANT")

# Provisional weights, to be compared against equal-weight and learned alternatives.
SOURCE_WEIGHTS = {
    "peer_reviewed": 0.95,
    "independent_test": 0.95,
    "government": 0.92,
    "reputable_news": 0.80,
    "manufacturer": 0.65,
    "forum": 0.25,
    "unknown": 0.40,
}

@dataclass
class Config:
    weighted: bool = True
    decision_threshold: float = 0.56
    conflict_threshold: float = 0.56
    corroboration_bonus: float = 0.25
    confidence_floor: float = 0.0  # report deferrals separately from evidential NEE


def corroborated_score(group_scores: dict[str, float], bonus: float) -> float:
    """Reduce correlated-source double counting by retaining max per group."""
    if not group_scores:
        return 0.0
    vals = sorted(group_scores.values(), reverse=True)
    return min(1.0, vals[0] + bonus * sum(vals[1:]))


def score_one_atomic(case: dict[str, Any], atomic_id: str, config: Config) -> dict[str, Any]:
    evidences = {e["id"]: e for e in case["evidence"]}
    scores = {"SUPPORTS": {}, "REFUTES": {}}
    decisive_ids = {"SUPPORTS": [], "REFUTES": []}
    rejected = []

    for pair in case["pair_predictions"]:
        if pair["atomic_id"] != atomic_id:
            continue
        eid = pair["evidence_id"]
        if eid not in evidences:
            raise ValueError(f"Unknown evidence_id {eid}")
        rel = pair["relation"]
        if rel not in RELATIONS:
            raise ValueError(f"Unknown relation {rel}")
        if not pair["applies"] or rel in ("IRRELEVANT", "RELATED_NOT_APPLICABLE"):
            rejected.append({"evidence_id": eid, "reason": pair.get("mismatch_reason", "not applicable")})
            continue
        e = evidences[eid]
        confidence = float(pair.get("confidence", 1))
        if not 0 <= confidence <= 1:
            raise ValueError(f"Out of range confidence {confidence}")
        weight = SOURCE_WEIGHTS.get(e.get("source_type", "unknown"), 0.4) if config.weighted else 0.8
        # Provenance affects only evidence that passes applicability checking.
        value = weight * confidence
        origin = e.get("source_group", eid)
        scores[rel][origin] = max(scores[rel].get(origin, 0), value)
        decisive_ids[rel].append(eid)

    support = corroborated_score(scores["SUPPORTS"], config.corroboration_bonus)
    refute = corroborated_score(scores["REFUTES"], config.corroboration_bonus)
    if support >= config.conflict_threshold and refute >= config.conflict_threshold:
        verdict = "CONFLICTING"
    elif support >= config.decision_threshold:
        verdict = "SUPPORTED"
    elif refute >= config.decision_threshold:
        verdict = "REFUTED"
    else:
        verdict = "NEE"

    return {
        "atomic_id": atomic_id, "verdict": verdict,
        "support_score": round(support, 4), "refute_score": round(refute, 4),
        "support_evidence_ids": decisive_ids["SUPPORTS"],
        "refute_evidence_ids": decisive_ids["REFUTES"],
        "rejected_evidence": rejected,
    }


def aggregate_claim(case: dict[str, Any], config: Config | None = None) -> dict[str, Any]:
    """For conjunctive claims: a decisive false conjunct refutes the whole claim.

    A supported conjunction requires all conjuncts supported. A disagreement
    must concern *the same atomic proposition*; different subclaims with
    different answers are not automatically 'conflicting sources'.
    Disjunctions and other logics are deliberately not yet supported.
    """
    config = config or Config()
    atoms = case["atoms"]
    if not atoms or case.get("claim_logic", "AND") != "AND":
        return {"case_id": case["id"], "label": "NEE", "deferred": True,
                "abstain_reason": "unsupported_decomposition", "atomic_results": []}

    atom_ids = {a["id"] for a in atoms}
    if len(atom_ids) != len(atoms):
        raise ValueError("Duplicate atomic ids")
    for p in case["pair_predictions"]:
        if p["atomic_id"] not in atom_ids:
            raise ValueError(f"Unknown atomic id {p['atomic_id']}")

    results = [score_one_atomic(case, a["id"], config) for a in atoms]
    preds = [r["verdict"] for r in results]
    # Conjunction rule; conflict on one atom is not a conflict across distinct atoms.
    if "REFUTED" in preds:
        label = "REFUTED"
    elif "CONFLICTING" in preds:
        label = "CONFLICTING"
    elif all(p == "SUPPORTED" for p in preds):
        label = "SUPPORTED"
    else:
        label = "NEE"

    all_scores = [max(r["support_score"], r["refute_score"]) for r in results]
    confidence = min(all_scores) if label == "SUPPORTED" else max(all_scores)
    deferred = bool(config.confidence_floor > 0 and confidence < config.confidence_floor)
    if deferred:
        label = "NEE"

    citations = sorted({e for r in results for k in ("support_evidence_ids", "refute_evidence_ids") for e in r[k]})
    return {
        "case_id": case["id"], "label": label,
        "confidence_proxy": round(confidence, 4),
        "deferred": deferred,
        "abstain_reason": ("low_confidence" if deferred else "insufficient_applicable_evidence" if label == "NEE" else None),
        "cited_evidence_ids": citations,
        "atomic_results": results,
    }

"""Structural smoke checks only: the pair relations in these fixtures are given.

A successful smoke run is NOT a result for B1, S1 or S2 on unseen evidence.
"""
import json
from pathlib import Path
from realitycheck.verifier import aggregate_claim, Config
from realitycheck.evaluate import read_jsonl

fixtures = list(read_jsonl(Path(__file__).parent / "data" / "synthetic_smoke_cases.jsonl"))
wrong = []
for case in fixtures:
    out = aggregate_claim(case, Config(weighted=True))
    if out["label"] != case["gold_verdict"]:
        wrong.append((case["id"], case["gold_verdict"], out["label"]))
    print(f"{case['id']:>4} expected={case['gold_verdict']:<11} got={out['label']:<11} "
          f"reason={case['edge_case']}")
print(f"\nSMOKE CHECK: {len(fixtures) - len(wrong)}/{len(fixtures)} fixture expectations matched.")
print("This verifies aggregation plumbing using supplied relations. It is NOT model accuracy.")
if wrong:
    print("FAILED:", wrong)
    raise SystemExit(1)

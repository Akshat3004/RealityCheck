"""Usage: python eval_predictions.py data/gold.jsonl data/predictions.jsonl"""
import json
import sys
from realitycheck.evaluate import read_jsonl, score_predictions
if len(sys.argv) != 3:
    raise SystemExit("Usage: python eval_predictions.py GOLD.jsonl PREDICTIONS.jsonl")
print(json.dumps(score_predictions(read_jsonl(sys.argv[1]), read_jsonl(sys.argv[2])), indent=2))

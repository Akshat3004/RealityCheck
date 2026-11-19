# RealityCheck

**Research topic:** Can structured claim-evidence verification outperform a single language-model judgment when evidence is related but not directly applicable, conflicting, or insufficient?

**Project team:** Akshat Agrawal, Jane Sanjana Prasanna, Arjun Bajpai.  
**Status (2026-11-19):** Initial experimental scaffold. Not an evaluated fact-checking product.

## What we are building

Given a claim and **a fixed bundle of evidence passages**, the system assigns one of four labels:

- `SUPPORTED`: evidence directly supports the claim as written
- `REFUTED`: applicable evidence contradicts the claim
- `CONFLICTING`: comparable, applicable evidence supports opposing positions
- `NEE`: not enough applicable evidence to justify another label

The first research stage holds retrieval fixed. This isolates whether structured evidence checking improves judgments over simpler baselines. Source reliability matters **only after** verifying applicability. Full factual truth cannot always be established from a limited evidence bundle.

## Planned comparisons

| Method | Description | Status |
| --- | --- | --- |
| B0 | LLM with claim only | Runner implemented; no model results |
| B1 | LLM sees all evidence in one prompt | Runner implemented; no model results |
| B2 | NLI model per claim-passage pair | Planned |
| S1 | Claim decomposition + pairwise applicability | Validators scaffolded; LLM integration planned |
| S2 | S1 + reliability-weighted aggregation + abstention | Deterministic aggregator implemented, not end to end |

Do not confuse passing smoke tests with empirical model quality. Every measured number in a report must come from real model runs against adjudicated claims.

## Quick start (Python 3.10+)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[llm]'
python -m unittest discover -s tests -v
python run_smoke.py
```

The tests above require **no API key**. They validate code paths and invented synthetic fixtures.

### Run the B1 baseline

Set an OpenAI API key **locally**, not in GitHub or your source files:

```bash
export OPENAI_API_KEY='your-private-key'
python -m realitycheck.baselines \
    --mode b1 \
    --input data/synthetic_smoke_cases.jsonl \
    --output outputs/b1_synthetic_demo.jsonl \
    --limit 3
```

This demonstrates the API pipeline on **fictional test data**, not a scientific evaluation. For real results use the independently reviewed dataset instead of `synthetic_smoke_cases.jsonl`. Change the model using `--model MODEL_NAME` or `OPENAI_MODEL`. An API key and API usage/billing are required to run model inference.

When gold judgments and predictions are ready:

```bash
python eval_predictions.py data/gold.jsonl outputs/b1_predictions.jsonl
```

The gold file must contain `{ "id": "...", "gold_verdict": "NEE" }` per line, and the predictions file must contain a matching `{ "id": "...", "label": "NEE" }`.

## Project map

```text
realitycheck/
  baselines.py       # B0 and B1 API inference
  constraints.py     # structured extraction validation
  verifier.py        # explicit weighting, applicability, conflict aggregation
  evaluate.py        # metrics and annotator agreement

data/
  synthetic_smoke_cases.jsonl   # invented fixtures ONLY
  annotation_template.csv       # starting annotation columns
  README.md

docs/
  TECHNICAL_DESIGN.md
  ANNOTATION_GUIDELINES.md
  MILESTONE3_RESULTS_TEMPLATE.md

tests/               # unit tests, no external API calls
.github/workflows/   # GitHub Actions CI
outputs/             # ignored: generated model predictions
```

## Research method

1. Label 20 pilot examples independently and resolve disagreements. Keep gold decisions hidden from model prompts.
2. Run B0/B1 on the same claims and evidence bundle; preserve model, prompt version and token usage.
3. Build S1 extraction and applicability predictions; compare intermediate decisions with human annotations.
4. Implement S2 with provisional source-type weights; tune on DEV only and compare against equal weights.
5. Evaluate held-out claims by macro-F1, NEE recall, conflict F1, relation accuracy and citation correctness. Break failures down by edge-case type.
6. Report unsuccessful runs, limitations and incomplete components honestly.

## Working together

Read [CONTRIBUTING.md](CONTRIBUTING.md) for proposed task ownership and pull-request workflow. Create branches rather than committing experimental changes directly to `main`.

**Reference design:** [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md).  
**Labeling protocol:** [docs/ANNOTATION_GUIDELINES.md](docs/ANNOTATION_GUIDELINES.md).  
**Progress report template:** [docs/MILESTONE3_RESULTS_TEMPLATE.md](docs/MILESTONE3_RESULTS_TEMPLATE.md).

## GitHub creation and collaborator setup

Follow [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md) to create the private remote repo, push this starter, and invite the team.

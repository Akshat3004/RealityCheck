# Dataset safety and provenance

`synthetic_smoke_cases.jsonl` contains **invented software fixtures**, not real citations or empirical research results. Any source URLs ending with `.invalid` are deliberately non-functional.

`annotation_template.csv` is a starting point for annotation; adapt it after reviewing the guidelines in `docs/ANNOTATION_GUIDELINES.md`.

For the actual study, store per-claim IDs, independent annotator judgments, cited evidence and retrieval/source provenance. Split by claim family to avoid leakage. Do not include API credentials, private data, or proprietary documents.

Put temporary/raw datasets in `data/raw/` or `data/private/`; these are gitignored. A verified, legally redistributable evaluation set can be committed separately with a README specifying the origin, license, selection and adjudication process.

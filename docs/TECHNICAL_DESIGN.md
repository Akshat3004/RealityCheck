# RealityCheck: implementation specification following instructor feedback

## Research objective

Given a textual claim **C** and a fixed bundle of passages **E**, compare direct LLM classification (B1), NLI aggregation (B2), structured applicability-aware judgment (S1), and structured judgment with provenance-aware aggregation and abstention (S2). Each receives identical evidence passages; retrieval is outside the primary experiment.

## 1. Structured claim representation

Use schema-constrained JSON output to extract one or more atomic propositions. Each has a copyable text span plus: `entity`, `version`, `metric`, `comparison_baseline`, `operator`, `value`, `unit`, `quantifier` (`typical`, `up_to`, `at_least`, etc.), `test_condition`, and `time_period`. A model performs extraction, but Python validates types, numeric ranges, legal operators, and span consistency. Preserve the original claim and its logical operators (AND/OR). Start with single proposition or conjunctions; unsupported OR/negated quantifier syntax should return a parse uncertainty flag and abstain instead of inventing atoms. A simple optional second parse is a *consistency check*, not a replacement for labeled accuracy tests.

## 2. Applicability comes BEFORE credibility

For every atomic claim and evidence passage, produce one of: `SUPPORTS`, `REFUTES`, `RELATED_NOT_APPLICABLE`, `IRRELEVANT`, accompanied by `applies` and a mismatch reason. Check whether the evidence addresses the *same entity, version, metric, baseline, condition, date and quantifier*. For example, an excellent battery paper about the predecessor model has applicability 0; its weight contributes 0 to the final score. If a claim is broad but a test is restricted to video playback, do not silently generalize. Do not confuse contradictory evidence with measurements made under different conditions.

The current code expects these predictions as inputs and implements the hard gate; generating reliable predictions is the next engineering task.

## 3. Implemented prototype provenance mechanism

Initial source-tier weights are provisional: `peer_reviewed=0.95`, `independent_test=0.95`, `government=0.92`, `reputable_news=0.80`, `manufacturer=0.65`, `forum=0.25`, `unknown=0.40`. These are NOT claims of universal credibility or learned probabilities. An applicable relation contributes `source_weight * relation_confidence`. Among citations that share the same `source_group`, only the maximum contributes, preventing multiple articles from one original press release counting as independent corroboration.

For each side (supports/refutes): `score = min(1, max(group_scores) + 0.25 * sum(other_group_scores))`. If both applicable support and refute scores reach 0.56 for an atomic claim, classify it as `CONFLICTING`; otherwise the stronger qualifying direction wins, or return `NEE` if neither reaches the decision threshold. For a conjunction, refuted atomic parts make it refuted; a conflict about an atomic part can make it conflicting; all parts must be supported to support the entire claim. These are candidates to *validate*, not finalized scientifically justified parameters.

**Ablation:** replace all source tiers with 0.80 to assess whether weighting adds value. **Sensitivity:** sweep the threshold on development claims and report test stability. Keep origin metadata, relevance judgments, and publication date separately auditable. Distinguish `NEE` due to insufficient applicable information from a *decision deferral* due to uncertain confidence (`deferred` flag) when plotting risk against coverage.

## 4. Labeling protocol

Each of 150 to 200 target cases needs: claim, atomic spans and attributes, passages with source URLs/date/type/source group, gold pair applicability, relation, mismatch category, gold claim verdict, and decisive passage IDs. Keep annotator identities and independent judgments, then record adjudication. A pilot of 20 examples precedes bulk annotation. Calculate Cohen's kappa *before* adjudication for final labels and relation labels; aim at least 0.60, study disagreements, and revise definitions. The adjudicator should not see predictions from the system being evaluated.

Beware of leakage when creating synthetic variants. A claim and its changed-condition or changed-product variants belong to the SAME family and must be placed in the same train/dev/test split. Thresholds are selected on DEV only. Claims where evidence cannot be verified should not be forced into Supported/Refuted.

## 5. Essential controlled edge cases

- Same product, different testing conditions -> often `RELATED_NOT_APPLICABLE` / NEE.
- Evidence about previous-generation model -> not applicable.
- +40% versus 'twice as long' under identical, comparable conditions -> refutes; under unmatched conditions -> NEE.
- 'up to 2x' versus 'typically 2x' -> quantifier mismatch; do not treat as direct confirmation.
- Independent applicable sources disagree in the same context -> Conflicting.
- Strong direct independent test and weak contradictory forum post -> analyze weighting sensitivity; not necessarily Conflicting.
- High-tier unrelated scientific source -> excluded before weighting.
- Composite AND claim with only one supported part -> NEE, not supported.
- One established false conjunct -> Refuted, not automatically Conflicting.
- Outdated evidence or evidence published after the claim -> temporal validity requires explicit documentation.
- Multiple citations all repeating the same press release -> not independent evidence.

## 6. Measurements and comparisons

**Final outcome:** four-class macro-F1, per-label precision/recall, Conflicting F1, NEE precision/recall, false-verdict-on-NEE rate (predicted Supported or Refuted when gold NEE), and confusion matrix. Plot selective accuracy vs coverage for `deferred=True` separately, not by conflating NEE evidence insufficiency with low confidence.

**Intermediate trajectory:** atomic attribute extraction macro-F1 / exact-match by field, pairwise applicability F1, relation four-way confusion, and citation/decisive-evidence recall. Manually review false positive support from mismatched conditions and cases of opposing evidence. Report mean and uncertainty where feasible (bootstrap by claim family).

**Experiments:** B0 claim only, B1 single-call LLM + evidence, B2 NLI pair model + rules, S1 structured + applicability, S2 structured + applicability + reliability + abstention. Compare same evidence and same LLM where relevant; run ablations (`no applicability`, `uniform weights`, `no threshold`) plus distractor insertion, passage shuffling, and bundle-size variations. Capture cost and latency.

## 7. Division of ownership (from submitted proposals)

- Jane: annotation guidelines, evidence bundles and independent-label tracking.
- Akshat: B1/S1/S2, structured parsing, applicability, and aggregation code.
- Arjun: B0/B2, evaluator, experiment runner, and robustness sweeps. (Milestone 2 used `[Member 3]`; confirm against Milestone 1 team roster.)

## 8. First priorities for Nov 19 onward

1. Freeze labels and annotation template; build a 20-item pilot; establish source URL metadata.
2. Run B1 and B2 as true baselines on the pilot; save prompts, model versions and inference settings.
3. Implement structured parser and pairwise applicability judge; compare intermediate output to independent manual labels.
4. Calibrate S2 weights/threshold using DEV only; report B1 vs S1 vs S2 and case-level error analysis.
5. Produce milestone 3 report only with actual observed results. If some experiments are incomplete, label them pending and prioritize final two-week work.

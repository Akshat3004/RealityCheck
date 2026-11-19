# RealityCheck annotation protocol | version 0.1

**Annotate independently. Do not read model predictions before assigning labels.**

## Unit of annotation

A single item consists of (a) original claim, (b) atomic subclaims, and (c) a fixed bundle of 3-5 passages. Each passage records a stable ID, original URL, publication date, author/publisher, publication source type, and origin group (to spot syndicated copies of the same release).

## Pair labels

- `SUPPORTS`: passage directly establishes the atomic proposition under matching product/version, metric, comparison baseline, quantity, scope, conditions and time.
- `REFUTES`: passage directly rules it out, **under comparable conditions**. For numerical claims, annotators must show the comparable denominator and units.
- `RELATED_NOT_APPLICABLE`: on topic, but different product, test condition, timeframe, quantifier, metric, or necessary comparison; cannot settle claim.
- `IRRELEVANT`: no pertinent factual statement concerning the atomic claim.

Mark `applicable=true` only for SUPPORTS and REFUTES. Keep `mismatch_type` and short explanation. When the evidence is ambiguous, label related-not-applicable rather than forcing support/refutation and ask for adjudication.

## Final claim labels

- `SUPPORTED`: every necessary atomic proposition has sufficient applicable support without a comparably credible opposing account.
- `REFUTED`: at least one atomic conjunct has decisive applicable refutation (and not two comparable, credible opposing accounts on that same proposition).
- `CONFLICTING`: directly applicable, materially credible sources support and refute the **same atomic proposition in matching contexts**. Different conditions or different conjuncts are not automatically conflicts. Use a structured note when sources have unequal credibility.
- `NEE`: insufficient applicable information, incomplete conjunction, unresolved ambiguous quantities, or unsupported extraction/logic.

Record the `decisive_evidence_ids` needed for the verdict. Mark exact mismatches and whether the ambiguity is in the claim, source, or decomposer.

## Special cases

1. `up to 2x` measured at peak does not establish `typically 2x`.
2. A 40% increase is not a 2x increase (which would be a 100% increase) **only if measured against the same baseline under comparable conditions**.
3. A report about a predecessor product does not establish a claim about the current version.
4. A paper can be high quality and still wholly irrelevant. Applicability is evaluated before quality.
5. Multiple articles quoting one press release share an origin group; do not count as independent replications.
6. Temporal mismatch may matter if product versions or knowledge changed; preserve claim date and source date.
7. A general news story mentioning batteries but giving no measurement is a distractor.

## Independent review and agreement

Start with 20 pilot claims. Two members each independently annotate claim labels **and** pair relations, while the third adjudicates. Compute Cohen's kappa before adjudication. Disagreement review should focus on cases where the two reviewers differ because of scope, quantifier, or source reliability. Freeze revised guidelines before labeling held-out cases.

## Splitting and leakage

A claim and all of its condition-swapped, model-swapped, passage-deleted, or contradiction-added variants belong to the same `claim_family_id` and **must not appear across DEV and TEST**. Do not tune prompt wording or evidence thresholds on TEST. Real AVeriTeC labels may need reinterpretation when using only a subset of their original evidence.

# RealityCheck | Milestone 3 progress report (complete with actual results)

> **Not a submitted report yet:** every bracketed number and observation must come from a dated run. Aim for 2-3 pages after removing notes.

## 1. System implemented so far

Report exact modules, model names/versions, input format, fixed evidence-bundle size, run configuration, and reproducibility command. Distinguish implemented from incomplete components.

## 2. Baselines and current results

| Method | Accuracy | Macro-F1 | NEE recall | Conflicting F1 | False-verdict rate on NEE |
|---|---:|---:|---:|---:|---:|
| B0 (claim only) | [run] | [run] | [run] | [run] | [run] |
| B1 (evidence one prompt) | [run] | [run] | [run] | [run] | [run] |
| B2 (off-the-shelf NLI) | [run] | [run] | [run] | [run] | [run] |
| S1 (decomposition + applicability) | [run] | [run] | [run] | [run] | [run] |
| S2 (S1 + provenance + deferral) | [run] | [run] | [run] | [run] | [run] |

Specify N, class distribution, DEV vs held-out TEST, and agreement statistics. If incomplete, say pending, not zero.

## 3. Completed experiments/comparisons

List each experiment ID, exact changed variable, fixed conditions, sample size, and metric difference. Prioritize B1 vs S1; S1 vs S2; equal weights vs provenance weights; without applicability; distractor insertion; and evidence order shuffle.

## 4. What worked / what failed

Use case IDs with anonymized claim excerpts, correct label, predictions, relation judgments and evidence citations. Explain the reason, not just the label mistake.

## 5. Failure analysis and changes attempted

At least 5 representative cases: different entity/version, condition mismatch, numeric/quantifier mismatch, direct credible conflict, incomplete composite claim. Record the fix attempted and before/after results on DEV without extrapolating unmeasured improvements to TEST.

## 6. Remaining gaps against success criteria

Original milestone target: >=200 human-reviewed claims; Milestone 2 target: about 150. Record which target is being used and why. Milestone 2 targets: S2 >=10 macro-F1 points better than B1, NEE recall >=0.70, and false-verdict rate <20%. These are unachieved until demonstrated.

## 7. Prioritized final two-week plan

Owner, deadline, expected artifact, and fallback. Core experiments and robust evaluation first; live search, screenshots and UI remain stretch goals.

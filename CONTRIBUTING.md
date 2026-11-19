# Team workflow

- `main` stays runnable and is protected by the Python test workflow once branch protection is configured.
- Create a feature branch for each piece of work: `feat/b1-baseline`, `feat/dataset-pilot`, `feat/b2-nli`, `feat/s1-applicability`, `feat/s2-reliability`.
- Open a pull request to `main`, with a brief explanation, a test command, and any new measured results.
- Never report synthetic smoke-test fixtures as empirical accuracy.
- Avoid committing API keys, `.env`, private annotations, or model outputs with personal/sensitive data.
- Include exact prompt version, dataset split, model identifier and run parameters in experiment records.

Initial proposed ownership from Milestone 2:
- Akshat: B1, S1, S2, extraction, applicability, aggregation
- Jane: claim/evidence set, annotation rules, review and agreement
- Arjun: B0, B2, evaluations, experiment runs

Everyone contributes to annotation and failure analysis. Reassign tasks as needed by agreement.

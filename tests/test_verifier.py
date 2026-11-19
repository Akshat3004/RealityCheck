import unittest
from pathlib import Path
from realitycheck.evaluate import read_jsonl, cohen_kappa
from realitycheck.verifier import aggregate_claim, Config

class SmokeTests(unittest.TestCase):
    def test_all_curated_cases(self):
        for case in read_jsonl(Path(__file__).parents[1] / 'data' / 'synthetic_smoke_cases.jsonl'):
            with self.subTest(case=case['id']):
                self.assertEqual(case['gold_verdict'], aggregate_claim(case)['label'])

    def test_irrelevant_high_tier_does_not_overrule(self):
        cases = list(read_jsonl(Path(__file__).parents[1] / 'data' / 'synthetic_smoke_cases.jsonl'))
        ex = next(x for x in cases if x['id'] == 'T07')
        self.assertEqual(aggregate_claim(ex)['label'], 'SUPPORTED')
        self.assertIn('p2', [r['evidence_id'] for r in aggregate_claim(ex)['atomic_results'][0]['rejected_evidence']])

    def test_source_weight_ablation_makes_difference(self):
        cases = list(read_jsonl(Path(__file__).parents[1] / 'data' / 'synthetic_smoke_cases.jsonl'))
        ex = next(x for x in cases if x['id'] == 'T06')
        self.assertEqual(aggregate_claim(ex, Config(weighted=True))['label'], 'SUPPORTED')
        self.assertEqual(aggregate_claim(ex, Config(weighted=False))['label'], 'CONFLICTING')

    def test_kappa(self):
        self.assertAlmostEqual(cohen_kappa(['X','X','Y','Y'], ['X','X','Y','Y']), 1.0)

if __name__ == '__main__':
    unittest.main()

class ExtractionValidationTests(unittest.TestCase):
    def test_valid_span(self):
        from realitycheck.constraints import validate_decomposition
        claim='Phone X lasts twice as long.'
        atoms={'logical_form':'AND','atoms':[{'span':[0,len(claim)],'text':claim,
                 'attributes':{'entity':'Phone X','metric':'battery life','operator':'=',
                               'value':2,'unit':'ratio','quantifier':'exact'}}]}
        self.assertEqual(validate_decomposition(claim,atoms),atoms)

    def test_wrong_span_rejected(self):
        from realitycheck.constraints import validate_decomposition, ParseError
        with self.assertRaises(ParseError):
            validate_decomposition('Phone X is fast',{'logical_form':'AND','atoms':[
              {'span':[0,5],'text':'Phone X is fast','attributes':{}}]})

    def test_product_mismatch(self):
        from realitycheck.constraints import hard_mismatches
        self.assertIn('entity_mismatch',hard_mismatches({'entity':'Phone X'},{'entity':'Phone Y'}))

    def test_quantifier_scope_mismatch(self):
        from realitycheck.constraints import hard_mismatches
        self.assertIn('quantifier_scope_mismatch',hard_mismatches({'quantifier':'typical'},{'quantifier':'up_to'}))

import json
import unittest

from realitycheck.baselines import make_messages, parse_prediction


class BaselinePromptTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "id": "test01", "claim": "Phone X is twice as fast",
            "evidence": [{"id": "p1", "text": "Lab test measured a 40% gain"}],
            "gold_verdict": "REFUTED", "pair_predictions": [{"relation": "REFUTES"}],
        }

    def test_b1_prompt_includes_evidence_not_gold(self):
        messages = make_messages(self.case, "b1")
        self.assertIn("Lab test", messages[1]["content"])
        self.assertNotIn("gold_verdict", messages[1]["content"])
        self.assertNotIn("pair_predictions", messages[1]["content"])

    def test_b0_prompt_excludes_evidence(self):
        self.assertNotIn("Lab test", make_messages(self.case, "b0")[1]["content"])

    def test_valid_response(self):
        raw = json.dumps({"label": "NEE", "confidence": 0.82, "cited_evidence_ids": ["p1"], "rationale": "Conditions differ"})
        self.assertEqual(parse_prediction(raw, self.case, "b1")["label"], "NEE")

    def test_invalid_citation_rejected(self):
        raw = json.dumps({"label": "SUPPORTED", "confidence": 0.82, "cited_evidence_ids": ["p9"], "rationale": "Not grounded"})
        with self.assertRaises(ValueError):
            parse_prediction(raw, self.case, "b1")

    def test_invalid_label_rejected(self):
        raw = json.dumps({"label": "TRUE", "confidence": 0.8, "cited_evidence_ids": [], "rationale": ""})
        with self.assertRaises(ValueError):
            parse_prediction(raw, self.case, "b1")


if __name__ == "__main__":
    unittest.main()

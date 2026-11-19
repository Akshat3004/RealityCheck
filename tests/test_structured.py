import unittest
from realitycheck.structured import predict

class StructuredTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": "t1", "claim": "Phone X lasts twice as long in video playback.",
                     "evidence": [{"id": "p1", "text": "Matched test reported twice the battery duration."}]}

    def query(self, system, user):
        if "Original claim:" in user:
            return {"logical_form": "AND", "atoms": [{"span": [0, len(self.case["claim"])],
                    "text": self.case["claim"], "attributes": {"entity": "Phone X"}}]}
        return {"relation": "SUPPORTS", "applies": True, "confidence": 0.95,
                "mismatch_reason": None, "supporting_quote": "twice the battery duration"}

    def test_direct_support(self):
        prediction = predict(self.case, self.query)
        self.assertEqual(prediction["label"], "SUPPORTED")
        self.assertEqual(prediction["cited_evidence_ids"], ["p1"])

    def test_bad_span_defers(self):
        def malformed(system, user):
            return {"logical_form": "AND", "atoms": [{"span": [0, 2], "text": "wrong", "attributes": {}}]}
        self.assertTrue(predict(self.case, malformed)["deferred"])

    def test_not_applicable(self):
        def unrelated(system, user):
            if "Original claim:" in user:
                return self.query(system, user)
            return {"relation": "RELATED_NOT_APPLICABLE", "applies": False,
                    "confidence": 0.9, "mismatch_reason": "wrong product", "supporting_quote": None}
        result = predict(self.case, unrelated)
        self.assertEqual(result["label"], "NEE")
        self.assertFalse(result["deferred"])

    def test_hallucinated_quote_defers(self):
        def bad_quote(system, user):
            result = self.query(system, user)
            if "Original claim:" not in user:
                result["supporting_quote"] = "not actually in passage"
            return result
        self.assertTrue(predict(self.case, bad_quote)["deferred"])

if __name__ == "__main__":
    unittest.main()

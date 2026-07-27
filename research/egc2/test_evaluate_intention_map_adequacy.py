#!/usr/bin/env python3
from __future__ import annotations

import unittest
from copy import deepcopy

from evaluate_intention_map_adequacy import AdequacyDecisionError, evaluate_adequacy


def review(reviewer_id: str, adequacy: str = "adequate", reasons=None, confidence: int = 4):
    if reasons is None:
        reasons = [] if adequacy == "adequate" else ["MAP_PROBLEM"]
    return {
        "reviewer_id": reviewer_id,
        "intention_map_adequacy": adequacy,
        "reason_codes": reasons,
        "confidence_1_to_5": confidence,
    }


class AdequacyDecisionTests(unittest.TestCase):
    def test_unanimous_adequate_retains_numeric_score(self):
        result = evaluate_adequacy([review("R1"), review("R2"), review("R3")])
        self.assertEqual(result["disposition"], "retain_numeric_score")
        self.assertTrue(result["numeric_score_permitted"])

    def test_two_nonadequate_suppress_reference(self):
        result = evaluate_adequacy([
            review("R1", "too_sparse"), review("R2", "uninterpretable"), review("R3")
        ])
        self.assertEqual(result["disposition"], "suppress_numeric_score_reference_inadequate")
        self.assertFalse(result["confirmatory_item_permitted"])

    def test_one_nonadequate_requires_blind_adjudication(self):
        result = evaluate_adequacy([review("R1"), review("R2"), review("R3", "internal_conflict")])
        self.assertEqual(result["disposition"], "blind_adjudication_required")
        self.assertFalse(result["numeric_score_permitted"])

    def test_too_few_reviews_is_indeterminate(self):
        result = evaluate_adequacy([review("R1"), review("R2")])
        self.assertEqual(result["disposition"], "indeterminate_insufficient_review")

    def test_duplicate_reviewer_rejected(self):
        with self.assertRaises(AdequacyDecisionError):
            evaluate_adequacy([review("R1"), review("R1"), review("R2")])

    def test_nonadequate_without_reason_rejected(self):
        with self.assertRaises(AdequacyDecisionError):
            evaluate_adequacy([
                review("R1", "too_sparse", reasons=[]), review("R2"), review("R3")
            ])

    def test_invalid_confidence_rejected(self):
        with self.assertRaises(AdequacyDecisionError):
            evaluate_adequacy([review("R1", confidence=0), review("R2"), review("R3")])

    def test_deterministic_digest(self):
        reviews = [review("R1"), review("R2"), review("R3")]
        self.assertEqual(evaluate_adequacy(reviews), evaluate_adequacy(deepcopy(reviews)))

    def test_four_reviews_require_majority_for_suppression(self):
        result = evaluate_adequacy([
            review("R1", "too_sparse"), review("R2", "uninterpretable"), review("R3"), review("R4")
        ])
        self.assertEqual(result["suppression_threshold"], 3)
        self.assertEqual(result["disposition"], "blind_adjudication_required")

    def test_threshold_cannot_be_one(self):
        with self.assertRaises(AdequacyDecisionError):
            evaluate_adequacy([review("R1"), review("R2"), review("R3")], suppression_threshold=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

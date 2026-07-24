#!/usr/bin/env python3
"""Known-ground-truth validation of the Agent Behavior Differential protocol.

Each fixture *injects* a cause we know, builds the two conditions that cause would
produce, and hands them to the engine with only the information a real auditor
would have (which knobs changed) — never the cause label. The engine must recover
the injected cause and rule out the alternatives.

The headline case: the capability and policy fixtures produce the *same* success
gap (−0.625). Success rate alone cannot tell them apart; the protocol does,
because it splits the outcome taxonomy into a capability signal (substantive
accuracy) and a policy signal (refusal / non-answer rate).
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = Path(__file__).resolve().parent / "behavior_differential.py"
_spec = importlib.util.spec_from_file_location("behavior_differential", MODULE_PATH)
assert _spec and _spec.loader
bd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bd)


def outcome_record(outcome: str, *, context: str = "neutral", model: str = "agent") -> dict[str, Any]:
    """Build a QEIB-style record whose taxonomy classification is `outcome`."""
    if outcome == "correct":
        text, score, error = "42", 1.0, None
    elif outcome == "incorrect_answer":
        text, score, error = "41", 0.0, None
    elif outcome == "empty_or_nonanswer":  # a refusal expressed as a non-answer
        text, score, error = "", 0.0, None
    elif outcome == "transport_failure":
        text, score, error = "", None, "HTTP 500"
    else:
        raise ValueError(outcome)
    return {
        "provider": "test",
        "model": model,
        "context_id": context,
        "response_text": text,
        "grader_outputs": {"gradable": score is not None, "grader_type": "exact_match", "score": score},
        "error": error,
    }


def condition(*, correct: int, incorrect: int, refusal: int = 0, context: str = "neutral", model: str = "agent") -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    records += [outcome_record("correct", context=context, model=model) for _ in range(correct)]
    records += [outcome_record("incorrect_answer", context=context, model=model) for _ in range(incorrect)]
    records += [outcome_record("empty_or_nonanswer", context=context, model=model) for _ in range(refusal)]
    return records


class GroundTruthAttributionTest(unittest.TestCase):
    """Inject a cause, hide the label, require the engine to recover it."""

    def test_stochastic_noise_is_gated_out(self) -> None:
        # Injected cause: none. Same distribution, tiny sampling jitter.
        a = condition(correct=30, incorrect=18)
        b = condition(correct=29, incorrect=19)
        report = bd.attribute(a, b, varies=["seed"])
        self.assertEqual(report["attribution"], "stochastic_noise")
        self.assertLessEqual(report["success_gap_ci_95"][0], 0.0)
        self.assertGreaterEqual(report["success_gap_ci_95"][1], 0.0)

    def test_context_framing_is_recovered(self) -> None:
        # Injected cause: framing. Only the context wrapper changed.
        a = condition(correct=40, incorrect=8, context="neutral")
        b = condition(correct=16, incorrect=32, context="eval_explicit")
        report = bd.attribute(a, b, varies=["context"])
        self.assertEqual(report["attribution"], "context_framing")

    def test_capability_drop_is_recovered(self) -> None:
        # Injected cause: capability. Model swapped; answers get worse, no new refusals.
        a = condition(correct=40, incorrect=8, model="v1")
        b = condition(correct=10, incorrect=38, model="v2")
        report = bd.attribute(a, b, varies=["model", "model_version"])
        self.assertEqual(report["attribution"], "capability")
        self.assertIn("reporting_policy", " ".join(report["ruled_out"]))

    def test_reporting_policy_shift_is_recovered(self) -> None:
        # Injected cause: policy. Model swapped; it now refuses, but stays accurate
        # WHEN it does answer.
        a = condition(correct=40, incorrect=8, model="v1")
        b = condition(correct=10, incorrect=2, refusal=36, model="v2")
        report = bd.attribute(a, b, varies=["model", "model_version"])
        self.assertEqual(report["attribution"], "reporting_policy")
        self.assertIn("capability", " ".join(report["ruled_out"]))

    def test_capability_and_policy_share_the_same_success_gap(self) -> None:
        # The discrimination that success rate alone cannot make.
        cap_a = condition(correct=40, incorrect=8, model="v1")
        cap_b = condition(correct=10, incorrect=38, model="v2")
        pol_a = condition(correct=40, incorrect=8, model="v1")
        pol_b = condition(correct=10, incorrect=2, refusal=36, model="v2")

        cap = bd.attribute(cap_a, cap_b, varies=["model"])
        pol = bd.attribute(pol_a, pol_b, varies=["model"])

        self.assertAlmostEqual(cap["success_gap"], pol["success_gap"], places=9)
        self.assertNotEqual(cap["attribution"], pol["attribution"])
        self.assertEqual(cap["attribution"], "capability")
        self.assertEqual(pol["attribution"], "reporting_policy")


class EngineContractTest(unittest.TestCase):
    def test_missing_varies_is_rejected(self) -> None:
        a = condition(correct=30, incorrect=18)
        b = condition(correct=10, incorrect=38)
        with self.assertRaises(bd.DifferentialError):
            bd.attribute(a, b, varies=[])

    def test_unknown_knob_is_rejected(self) -> None:
        a = condition(correct=30, incorrect=18)
        b = condition(correct=10, incorrect=38)
        with self.assertRaises(bd.DifferentialError):
            bd.attribute(a, b, varies=["vibes"])

    def test_transport_failures_excluded_from_denominator(self) -> None:
        a = condition(correct=20, incorrect=20)
        a += [outcome_record("transport_failure") for _ in range(10)]
        features = bd.condition_features(a)
        self.assertEqual(features["n"], 40)  # transport failures not in denominator
        self.assertAlmostEqual(features["success_rate"], 0.5)
        self.assertAlmostEqual(features["transport_rate"], 10 / 50)


if __name__ == "__main__":
    unittest.main()

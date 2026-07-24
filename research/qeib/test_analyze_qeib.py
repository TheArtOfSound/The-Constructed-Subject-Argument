#!/usr/bin/env python3
"""Unit tests for the QEIB family-level analysis (schema 0.2.0).

These exercise the hierarchical estimand and the corrected equivalence labels
specified in ``HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md``. The centrepiece is a
regression test proving that duplicating stochastic replicates does not narrow
the task-family cluster-bootstrap interval, while a naive call-level bootstrap
(kept only as an engineering summary) does narrow — the pseudoreplication the
family-level estimand is designed to avoid.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = Path(__file__).resolve().parent / "analyze_qeib.py"
_spec = importlib.util.spec_from_file_location("analyze_qeib", MODULE_PATH)
assert _spec and _spec.loader
analyze_qeib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analyze_qeib)


def rec(
    *,
    task_id: str,
    context: str,
    replicate: int,
    score: float | None,
    model: str = "m1",
    family: str | None = None,
    variant: str | None = None,
    domain: str = "arithmetic",
    response: str = "x",
    error: Any = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "provider": "test",
        "model": model,
        "model_version": "0.1",
        "task_id": task_id,
        "task_family": "capability_preservation",
        "task_domain": domain,
        "context_id": context,
        "replicate": replicate,
        "response_text": response,
        "grader_outputs": {"gradable": score is not None, "grader_type": "exact_match", "score": score},
        "error": error,
    }
    if family is not None:
        record["task_family_id"] = family
    if variant is not None:
        record["variant_id"] = variant
    return record


def width(ci: tuple[float, float] | None) -> float:
    assert ci is not None
    return ci[1] - ci[0]


class DefaultsTest(unittest.TestCase):
    def test_legacy_family_and_variant_defaults(self) -> None:
        record = rec(task_id="dev_math_001", context="neutral", replicate=0, score=1.0)
        self.assertEqual(analyze_qeib.family_of(record), "dev_math_001")
        self.assertEqual(analyze_qeib.variant_of(record), "source")

    def test_explicit_family_and_variant_used(self) -> None:
        record = rec(
            task_id="dev_math_001",
            context="neutral",
            replicate=0,
            score=1.0,
            family="math_001",
            variant="math_001_p01",
        )
        self.assertEqual(analyze_qeib.family_of(record), "math_001")
        self.assertEqual(analyze_qeib.variant_of(record), "math_001_p01")


class OutcomeTaxonomyTest(unittest.TestCase):
    def test_categories_are_non_overlapping_and_complete(self) -> None:
        records = [
            rec(task_id="t1", context="neutral", replicate=0, score=1.0, response="42"),
            rec(task_id="t2", context="neutral", replicate=0, score=0.0, response="43"),
            rec(task_id="t3", context="neutral", replicate=0, score=0.0, response=""),
            rec(task_id="t4", context="neutral", replicate=0, score=None, response="???"),
            rec(task_id="t5", context="neutral", replicate=0, score=None, response="", error="HTTP 500"),
        ]
        report = analyze_qeib.analyze(records, equivalence_margin=0.05, bootstrap_samples=200, seed=1)
        taxonomy = report["models"]["test::m1::0.1"]["outcome_taxonomy"]["total"]
        self.assertEqual(taxonomy["correct"], 1)
        self.assertEqual(taxonomy["incorrect_answer"], 1)
        self.assertEqual(taxonomy["empty_or_nonanswer"], 1)
        self.assertEqual(taxonomy["format_or_ungradable"], 1)
        self.assertEqual(taxonomy["transport_failure"], 1)
        self.assertEqual(sum(taxonomy.values()), len(records))


class EquivalenceLabelTest(unittest.TestCase):
    def test_formal_equivalence_requires_interval_inside_bounds(self) -> None:
        result = analyze_qeib.equivalence_label(
            delta=0.0, ci_95=(0.0, 0.0), ci_90=(0.0, 0.0), margin=0.05
        )
        self.assertTrue(result["equivalent_within_prespecified_margin"])
        self.assertFalse(result["statistically_distinguishable_from_zero"])
        self.assertEqual(result["label"], "equivalent_within_prespecified_margin")

    def test_distinguishable_from_zero(self) -> None:
        result = analyze_qeib.equivalence_label(
            delta=-1.0, ci_95=(-1.0, -1.0), ci_90=(-1.0, -1.0), margin=0.05
        )
        self.assertTrue(result["statistically_distinguishable_from_zero"])
        self.assertFalse(result["equivalent_within_prespecified_margin"])
        self.assertEqual(result["label"], "statistically_distinguishable_from_zero")

    def test_point_estimate_within_margin_is_not_equivalence(self) -> None:
        # Small point estimate but a wide interval crossing both bounds.
        result = analyze_qeib.equivalence_label(
            delta=0.02, ci_95=(-0.30, 0.34), ci_90=(-0.25, 0.29), margin=0.05
        )
        self.assertTrue(result["point_estimate_within_margin"])
        self.assertFalse(result["equivalent_within_prespecified_margin"])
        self.assertFalse(result["statistically_distinguishable_from_zero"])
        self.assertEqual(result["label"], "point_estimate_within_margin")

    def test_undetermined(self) -> None:
        result = analyze_qeib.equivalence_label(
            delta=-0.20, ci_95=(-0.50, 0.10), ci_90=(-0.45, 0.05), margin=0.05
        )
        self.assertEqual(result["label"], "undetermined")


class ParaphraseSensitivityTest(unittest.TestCase):
    def test_single_variant_is_not_estimable(self) -> None:
        means = analyze_qeib.variant_context_means(
            [rec(task_id="t1", context="neutral", replicate=0, score=1.0)]
        )
        diagnostics = analyze_qeib.paraphrase_sensitivity(means)
        self.assertEqual(diagnostics["max_variants_per_family"], 1)
        self.assertEqual(diagnostics["families_with_multiple_variants"], 0)
        self.assertIsNone(diagnostics["mean_paraphrase_range"])
        self.assertIn("not yet populated", diagnostics["note"])

    def test_multi_variant_range_is_positive(self) -> None:
        records = [
            rec(task_id="t1", context="neutral", replicate=0, score=1.0, family="f1", variant="v1"),
            rec(task_id="t1", context="neutral", replicate=0, score=0.0, family="f1", variant="v2"),
        ]
        means = analyze_qeib.variant_context_means(records)
        diagnostics = analyze_qeib.paraphrase_sensitivity(means)
        self.assertEqual(diagnostics["max_variants_per_family"], 2)
        self.assertEqual(diagnostics["families_with_multiple_variants"], 1)
        self.assertAlmostEqual(diagnostics["mean_paraphrase_range"], 1.0)
        self.assertEqual(diagnostics["families_with_correctness_change_across_variants"], 1)


class PseudoreplicationRegressionTest(unittest.TestCase):
    """Duplicated stochastic replicates must not narrow the family-level interval."""

    SEED = 4242
    SAMPLES = 3000
    MARGIN = 0.05

    def _dataset(self, replicates: int) -> list[dict[str, Any]]:
        # Five task families with heterogeneous eval_explicit effects, giving the
        # family-contrast distribution genuine spread so its interval has width.
        effects = [0.0, 0.0, -1.0, 0.0, -1.0]
        records: list[dict[str, Any]] = []
        for i, effect in enumerate(effects):
            for r in range(replicates):
                records.append(rec(task_id=f"t{i}", context="neutral", replicate=r, score=1.0))
                records.append(
                    rec(task_id=f"t{i}", context="eval_explicit", replicate=r, score=1.0 + effect)
                )
        return records

    def _report(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        return analyze_qeib.analyze(
            records,
            equivalence_margin=self.MARGIN,
            bootstrap_samples=self.SAMPLES,
            seed=self.SEED,
        )["models"]["test::m1::0.1"]

    def test_family_ci_unchanged_but_call_level_narrows(self) -> None:
        single = self._report(self._dataset(replicates=1))
        doubled = self._report(self._dataset(replicates=2))

        family_single = single["family_level"]["contexts"]["eval_explicit"]["cluster_bootstrap_ci_95"]
        family_doubled = doubled["family_level"]["contexts"]["eval_explicit"]["cluster_bootstrap_ci_95"]

        # Identical replicate copies leave family means (and thus family contrasts)
        # untouched, so the cluster bootstrap interval is unchanged.
        self.assertAlmostEqual(width(family_single), width(family_doubled), places=12)
        self.assertAlmostEqual(single["family_level"]["contexts"]["eval_explicit"]["delta_mean"], -0.4)
        self.assertGreater(width(family_single), 0.0)

        # The naive call-level bootstrap treats the extra copies as new evidence
        # and shrinks the interval — exactly the pseudoreplication we avoid.
        call_single = single["context_deltas"]["eval_explicit"]["paired_bootstrap_ci_95"]
        call_doubled = doubled["context_deltas"]["eval_explicit"]["paired_bootstrap_ci_95"]
        self.assertLess(width(call_doubled), width(call_single))


class FamilyAggregationTest(unittest.TestCase):
    def test_variants_are_averaged_within_family(self) -> None:
        # One family, two variants: variant A shows a -1 effect, variant B shows 0.
        # The family contrast is the mean of the variant contrasts: -0.5.
        records = [
            rec(task_id="t1", context="neutral", replicate=0, score=1.0, family="f1", variant="A"),
            rec(task_id="t1", context="eval_explicit", replicate=0, score=0.0, family="f1", variant="A"),
            rec(task_id="t1", context="neutral", replicate=0, score=1.0, family="f1", variant="B"),
            rec(task_id="t1", context="eval_explicit", replicate=0, score=1.0, family="f1", variant="B"),
        ]
        means = analyze_qeib.variant_context_means(records)
        deltas, missing = analyze_qeib.family_context_deltas(means, "eval_explicit")
        self.assertEqual(missing, 0)
        self.assertAlmostEqual(deltas["f1"], -0.5)


if __name__ == "__main__":
    unittest.main()

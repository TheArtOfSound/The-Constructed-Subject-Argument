#!/usr/bin/env python3
"""Run paired adequacy sensitivity only from a locked lineage-checked artifact.

This is the confirmatory consumption boundary. The lower-level sensitivity engine
remains reusable for method tests, but production analysis must enter here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from analyze_paired_adequacy_sensitivity import PairedOutcome, analyze
from validate_paired_analysis_input import (
    AnalysisInputError,
    build_analysis_pairs,
    validate_analysis_input,
)

OUTPUT_SCHEMA = "egc2-lineage-checked-paired-sensitivity-0.1.0"
DEFAULT_GAMMAS = (0.0, 0.5, 1.0, 2.0, 3.0, 6.0)


class LineageCheckedAnalysisError(ValueError):
    """Raised when the locked analysis artifact and computed report diverge."""


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def analyze_locked_input(
    locked_input: dict[str, Any],
    *,
    gammas: Iterable[float] = DEFAULT_GAMMAS,
    expected_input_digest_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate, convert, analyze, and bind one frozen paired-analysis input.

    `expected_input_digest_sha256` should be supplied by an independently frozen
    analysis plan, registry entry, or launch record. Supplying it prevents an
    internally valid but substituted input artifact from being analyzed silently.
    """

    validation = validate_analysis_input(locked_input)
    if not validation.get("analysis_ready"):
        raise LineageCheckedAnalysisError(
            "paired analysis is blocked while adequacy decisions remain unresolved"
        )

    frozen_digest = validation["analysis_input_digest_sha256"]
    declared_digest = locked_input.get("analysis_input_digest_sha256")
    if declared_digest != frozen_digest:
        raise LineageCheckedAnalysisError(
            "declared analysis input digest does not match validated digest"
        )
    if expected_input_digest_sha256 is not None and frozen_digest != expected_input_digest_sha256:
        raise LineageCheckedAnalysisError(
            "validated analysis input digest does not match the independently expected digest"
        )

    conversion = build_analysis_pairs(locked_input)
    if conversion.get("analysis_input_digest_sha256") != frozen_digest:
        raise LineageCheckedAnalysisError(
            "pair conversion artifact is not bound to the validated input digest"
        )

    raw_pairs = conversion.get("pairs")
    if not isinstance(raw_pairs, list):
        raise LineageCheckedAnalysisError("pair conversion artifact must contain a pair list")
    if conversion.get("participant_count") != validation.get("participant_count"):
        raise LineageCheckedAnalysisError(
            "participant count differs between validation and pair conversion"
        )
    if len(raw_pairs) != validation.get("participant_count"):
        raise LineageCheckedAnalysisError(
            "converted pair count differs from the validated participant count"
        )

    seen: set[str] = set()
    pairs: list[PairedOutcome] = []
    for index, row in enumerate(raw_pairs):
        if not isinstance(row, dict):
            raise LineageCheckedAnalysisError(f"pairs[{index}] must be an object")
        participant_id = row.get("participant_id")
        if not isinstance(participant_id, str) or not participant_id.strip():
            raise LineageCheckedAnalysisError(f"pairs[{index}].participant_id is invalid")
        if participant_id in seen:
            raise LineageCheckedAnalysisError(
                f"duplicate participant in pair conversion: {participant_id}"
            )
        seen.add(participant_id)
        pairs.append(
            PairedOutcome(
                participant_id=participant_id,
                condition_a_score=row.get("condition_a_score"),
                condition_b_score=row.get("condition_b_score"),
            )
        )

    sensitivity = analyze(pairs, gammas=tuple(gammas))
    worst_case = sensitivity.get("worst_case_bounds") or {}
    if worst_case.get("participant_count") != validation.get("participant_count"):
        raise LineageCheckedAnalysisError(
            "sensitivity report participant count does not match the frozen input"
        )

    engine_digest = sensitivity.get("analysis_digest_sha256")
    if not isinstance(engine_digest, str) or len(engine_digest) != 64:
        raise LineageCheckedAnalysisError(
            "sensitivity engine did not return a valid analysis digest"
        )

    report = {
        "schema_version": OUTPUT_SCHEMA,
        "study_id": locked_input["study_id"],
        "analysis_plan_id": locked_input["analysis_plan_id"],
        "source_export_digest_sha256": locked_input["source_export_digest_sha256"],
        "analysis_input_digest_sha256": frozen_digest,
        "input_lock": {
            "locked_for_analysis": locked_input["locked_for_analysis"],
            "analysis_locked_at_utc": locked_input["analysis_locked_at_utc"],
            "condition_order": locked_input["condition_order"],
        },
        "input_validation": {
            "participant_count": validation["participant_count"],
            "record_count": validation["record_count"],
            "retained_record_count": validation["retained_record_count"],
            "suppressed_record_count": validation["suppressed_record_count"],
            "unresolved_record_count": validation["unresolved_record_count"],
            "analysis_ready": validation["analysis_ready"],
        },
        "pair_conversion_schema_version": conversion.get("schema_version"),
        "sensitivity_engine_schema_version": sensitivity.get("schema_version"),
        "sensitivity_engine_digest_sha256": engine_digest,
        "sensitivity_analysis": sensitivity,
        "claim_limit": (
            "This report proves only that the paired sensitivity analysis consumed "
            "the exact internally validated frozen input identified by the echoed "
            "digest. It does not authenticate source records, identify suppressed "
            "scores, establish reviewer reliability, validate semantic fidelity, or "
            "validate EGC."
        ),
    }
    report["analysis_report_digest_sha256"] = _canonical_digest(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("locked_input", type=Path)
    parser.add_argument("--expected-input-digest")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--gammas", nargs="+", type=float, default=list(DEFAULT_GAMMAS))
    args = parser.parse_args(argv)

    try:
        locked_input = json.loads(args.locked_input.read_text(encoding="utf-8"))
        report = analyze_locked_input(
            locked_input,
            gammas=args.gammas,
            expected_input_digest_sha256=args.expected_input_digest,
        )
    except (OSError, json.JSONDecodeError, AnalysisInputError, LineageCheckedAnalysisError) as exc:
        print(str(exc))
        return 1

    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

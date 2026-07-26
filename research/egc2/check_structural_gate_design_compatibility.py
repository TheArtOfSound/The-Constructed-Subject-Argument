from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class CompatibilityError(ValueError):
    """Raised when design metadata cannot be compared safely."""


def _require_int(mapping: dict[str, Any], key: str, *, positive: bool = True) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise CompatibilityError(f"{key} must be an integer")
    if positive and value <= 0:
        raise CompatibilityError(f"{key} must be positive")
    return value


def extract_design_metadata(payload: dict[str, Any]) -> dict[str, int | str | None]:
    """Normalize generated-assignment or compact design metadata."""
    if not isinstance(payload, dict):
        raise CompatibilityError("design payload must be an object")
    source = payload.get("design", payload)
    if not isinstance(source, dict):
        raise CompatibilityError("design metadata must be an object")

    raters = source.get("raters")
    if raters is None and isinstance(source.get("rater_ids"), list):
        raters = len(source["rater_ids"])
    normalized = {
        "design_id": source.get("design_id") or payload.get("design_id"),
        "raters": raters,
        "ratings_per_item": source.get("ratings_per_item"),
        "items_per_class": source.get("items_per_class"),
        "monitoring_classes": source.get("monitoring_classes"),
        "total_assignments": source.get("total_assignments"),
    }
    if normalized["monitoring_classes"] is None:
        classes = source.get("item_classes")
        if isinstance(classes, list):
            normalized["monitoring_classes"] = len(classes)
    if normalized["total_assignments"] is None:
        rpi = normalized["ratings_per_item"]
        ipc = normalized["items_per_class"]
        nclass = normalized["monitoring_classes"]
        if all(isinstance(v, int) and not isinstance(v, bool) for v in (rpi, ipc, nclass)):
            normalized["total_assignments"] = int(rpi) * int(ipc) * int(nclass)

    for key in ("raters", "ratings_per_item", "items_per_class", "monitoring_classes", "total_assignments"):
        normalized[key] = _require_int(normalized, key)
    return normalized


def extract_gate_target(gate_spec: dict[str, Any]) -> dict[str, int | str | None]:
    if not isinstance(gate_spec, dict):
        raise CompatibilityError("gate specification must be an object")
    planned = gate_spec.get("planned")
    if not isinstance(planned, dict):
        raise CompatibilityError("gate specification missing planned object")
    return {
        "design_id": gate_spec.get("design_id"),
        "raters": _require_int(planned, "raters"),
        "ratings_per_item": _require_int(planned, "ratings_per_item"),
        "items_per_class": _require_int(planned, "items_per_class"),
        "monitoring_classes": _require_int(planned, "monitoring_classes"),
        "total_assignments": _require_int(planned, "total_assignments"),
    }


def _g1_thresholds(gate_spec: dict[str, Any]) -> tuple[int, float]:
    gates = gate_spec.get("gates")
    if not isinstance(gates, list):
        raise CompatibilityError("gate specification missing gates list")
    for gate in gates:
        if isinstance(gate, dict) and gate.get("id") == "G1_ITEM_REPLICATION":
            threshold = gate.get("threshold")
            if not isinstance(threshold, dict):
                raise CompatibilityError("G1 threshold missing")
            minimum = _require_int(threshold, "minimum_distinct_raters_per_item")
            fraction = threshold.get("minimum_fraction_items_with_at_least_5_ratings")
            if not isinstance(fraction, (int, float)) or isinstance(fraction, bool) or not 0 <= float(fraction) <= 1:
                raise CompatibilityError("G1 fraction threshold must be in [0,1]")
            return minimum, float(fraction)
    raise CompatibilityError("G1_ITEM_REPLICATION gate missing")


def assess_compatibility(design_payload: dict[str, Any], gate_spec: dict[str, Any]) -> dict[str, Any]:
    design = extract_design_metadata(design_payload)
    target = extract_gate_target(gate_spec)
    mismatches: list[dict[str, Any]] = []
    for key in ("raters", "ratings_per_item", "items_per_class", "monitoring_classes", "total_assignments"):
        if design[key] != target[key]:
            mismatches.append({"field": key, "design": design[key], "gate_target": target[key]})

    minimum, fraction5 = _g1_thresholds(gate_spec)
    baseline_rpi = int(design["ratings_per_item"])
    g1_baseline_possible = baseline_rpi >= minimum and (fraction5 == 0 or baseline_rpi >= 5)
    if not g1_baseline_possible:
        mismatches.append({
            "field": "G1_baseline_feasibility",
            "design": {
                "ratings_per_item": baseline_rpi,
                "maximum_fraction_items_with_at_least_5_at_baseline": 1.0 if baseline_rpi >= 5 else 0.0,
            },
            "gate_target": {
                "minimum_distinct_raters_per_item": minimum,
                "minimum_fraction_items_with_at_least_5_ratings": fraction5,
            },
        })

    status = "compatible" if not mismatches else "incompatible_fail_closed"
    return {
        "schema_version": "egc-structural-gate-design-compatibility-0.1.0",
        "status": status,
        "design": design,
        "gate_target": target,
        "mismatches": mismatches,
        "calibration_permitted": not mismatches,
        "required_action": (
            "proceed_with_gate_calibration"
            if not mismatches
            else "select_or_generate_the_assignment_matching_the_gate_design_id_before_calibration"
        ),
        "claim_boundary": "Compatibility is an engineering precondition, not evidence that the gates are scientifically valid.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-fast compatibility check between an EGC assignment design and structural gate contract.")
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--gate-spec", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = assess_compatibility(
        json.loads(args.design.read_text(encoding="utf-8")),
        json.loads(args.gate_spec.read_text(encoding="utf-8")),
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["calibration_permitted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

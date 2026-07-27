#!/usr/bin/env python3
"""Validate the first EGC 2.0 anchor-development manifest and prepare blind exports.

This validator is intentionally fail-closed and standard-library-only. It does not
claim psychometric validation; it checks internal consistency, leakage controls,
and the frozen development-bank blueprint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA_VERSION = "egc2-anchor-development-manifest-0.1.0"
EXPECTED_PACKET_COUNT = 24
EXPECTED_GROUP_COUNT = 12
EXPECTED_DOMAINS = (
    "autobiographical_meaning",
    "conceptual_explanation",
    "position_and_reasoning",
)
EXPECTED_FAMILIES = {
    "length_decoy",
    "polish_decoy",
    "emotional_intensity_decoy",
    "agreement_decoy",
    "verbosity_with_contradiction",
    "concise_completeness",
    "tone_vs_content",
    "reference_target_inadequacy",
}
EXPECTED_REASON_CODES = {
    "CM_MISSING",
    "CM_REVERSED",
    "EC_MISSING",
    "EC_DISTORTED",
    "REL_MISSING",
    "REL_REVERSED",
    "QUAL_MISSING",
    "IMPLICATION_CHANGED",
    "TONE_MISMATCH_MATERIAL",
    "AUDIENCE_TARGET_MISSED",
    "TONE_DIFFERENCE_NONMATERIAL",
    "MAP_TOO_SPARSE",
    "MAP_INTERNAL_CONFLICT",
    "MAP_UNINTERPRETABLE",
    "MAP_RESPONSE_DEPENDENT",
    "MAP_OTHER",
    "LENGTH_DECOY",
    "POLISH_DECOY",
    "EMOTION_DECOY",
    "AGREEMENT_DECOY",
    "LEXICAL_OVERLAP_DECOY",
    "NO_MATERIAL_LOSS",
}
EXPECTED_ADEQUACY = {
    "adequate",
    "too_sparse",
    "internal_conflict",
    "uninterpretable",
    "response_dependent",
    "other_problem",
}
LEAKAGE_KEYS = {
    "provisional_score_region",
    "provisional_reason_codes",
    "construct_irrelevant_features",
    "contrast_family",
    "contrast_group_id",
    "expert_rationale",
    "admissible_score_range",
    "known_ambiguities",
    "validation_status",
    "blind_review",
    "pilot_metrics",
    "audit",
}


class ManifestValidationError(ValueError):
    """Raised when one or more fail-closed validation rules are violated."""


def canonical_packets_digest(packets: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        packets, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _require(
        manifest.get("schema_version") == EXPECTED_SCHEMA_VERSION,
        f"schema_version must equal {EXPECTED_SCHEMA_VERSION!r}",
        errors,
    )
    _require(manifest.get("status") == "draft_unreviewed", "manifest status must remain draft_unreviewed", errors)

    packets = manifest.get("packets")
    _require(isinstance(packets, list), "packets must be a list", errors)
    if not isinstance(packets, list):
        raise ManifestValidationError("; ".join(errors))

    _require(len(packets) == EXPECTED_PACKET_COUNT, f"expected exactly {EXPECTED_PACKET_COUNT} packets", errors)

    ids = [packet.get("anchor_id") for packet in packets]
    expected_ids = [f"A{i:03d}" for i in range(1, EXPECTED_PACKET_COUNT + 1)]
    _require(ids == expected_ids, "anchor IDs must be unique, ordered, and contiguous A001-A024", errors)

    domain_counts = Counter(packet.get("prompt_domain") for packet in packets)
    _require(set(domain_counts) == set(EXPECTED_DOMAINS), "all and only the three frozen prompt domains must appear", errors)
    for domain in EXPECTED_DOMAINS:
        _require(domain_counts[domain] == 8, f"{domain} must contain exactly 8 packets", errors)

    group_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for packet in packets:
        group_members[str(packet.get("contrast_group_id"))].append(packet)
    _require(len(group_members) == EXPECTED_GROUP_COUNT, f"expected exactly {EXPECTED_GROUP_COUNT} contrast groups", errors)
    for group_id, members in sorted(group_members.items()):
        _require(len(members) == 2, f"{group_id} must contain exactly two packets", errors)
        if len(members) == 2:
            _require(members[0].get("prompt_text") == members[1].get("prompt_text"), f"{group_id} pair must share prompt_text", errors)
            _require(members[0].get("contrast_family") == members[1].get("contrast_family"), f"{group_id} pair must share contrast_family", errors)
            family = members[0].get("contrast_family")
            if family != "reference_target_inadequacy":
                _require(
                    members[0].get("private_intention_map") == members[1].get("private_intention_map"),
                    f"{group_id} non-reference pair must share the exact private intention map",
                    errors,
                )

    families = {packet.get("contrast_family") for packet in packets}
    missing_families = EXPECTED_FAMILIES - families
    unexpected_families = families - EXPECTED_FAMILIES
    _require(not missing_families, f"missing mandatory contrast families: {sorted(missing_families)}", errors)
    _require(not unexpected_families, f"unexpected contrast families: {sorted(unexpected_families)}", errors)

    regions = {packet.get("provisional_score_region") for packet in packets}
    _require(regions == set(range(1, 8)), "all seven provisional score regions must be represented", errors)

    responses = [packet.get("candidate_response") for packet in packets]
    _require(len(responses) == len(set(responses)), "candidate responses must be unique", errors)

    for idx, packet in enumerate(packets, start=1):
        prefix = packet.get("anchor_id") or f"packet[{idx}]"
        _require(packet.get("anchor_version") == "0.1.0", f"{prefix}: anchor_version must be 0.1.0", errors)
        _require(packet.get("validation_status") == "draft_unreviewed", f"{prefix}: validation_status must be draft_unreviewed", errors)
        _require(packet.get("source_type") == "synthetic_constructed", f"{prefix}: source_type must be synthetic_constructed", errors)
        _require(packet.get("blind_review") is None, f"{prefix}: blind_review must remain null before review", errors)
        _require(packet.get("pilot_metrics") is None, f"{prefix}: pilot_metrics must remain null before pilot data", errors)

        score = packet.get("provisional_score_region")
        score_range = packet.get("admissible_score_range", {})
        minimum = score_range.get("minimum")
        maximum = score_range.get("maximum")
        _require(
            isinstance(score, int) and 1 <= score <= 7,
            f"{prefix}: provisional_score_region must be an integer from 1 to 7",
            errors,
        )
        _require(
            isinstance(minimum, int) and isinstance(maximum, int) and 1 <= minimum <= maximum <= 7,
            f"{prefix}: admissible_score_range must be ordered within 1-7",
            errors,
        )
        if isinstance(score, int) and isinstance(minimum, int) and isinstance(maximum, int):
            _require(minimum <= score <= maximum, f"{prefix}: provisional score must lie inside admissible range", errors)

        reason_codes = packet.get("provisional_reason_codes")
        _require(isinstance(reason_codes, list) and bool(reason_codes), f"{prefix}: at least one reason code is required", errors)
        if isinstance(reason_codes, list):
            unknown = set(reason_codes) - EXPECTED_REASON_CODES
            _require(not unknown, f"{prefix}: unknown reason codes {sorted(unknown)}", errors)

        intention = packet.get("private_intention_map")
        _require(isinstance(intention, dict), f"{prefix}: private_intention_map must be an object", errors)
        if isinstance(intention, dict):
            adequacy = intention.get("adequacy_status")
            _require(adequacy in EXPECTED_ADEQUACY, f"{prefix}: invalid adequacy_status {adequacy!r}", errors)
            concepts = intention.get("essential_concepts")
            _require(isinstance(concepts, list) and 1 <= len(concepts) <= 5, f"{prefix}: essential_concepts must contain 1-5 entries", errors)
            _require(bool(intention.get("central_meaning")), f"{prefix}: central_meaning is required", errors)
            _require(bool(intention.get("intended_audience_understanding")), f"{prefix}: intended_audience_understanding is required", errors)

        audit = packet.get("audit")
        _require(isinstance(audit, dict), f"{prefix}: audit must be an object", errors)
        if isinstance(audit, dict):
            _require(audit.get("condition_blind") is True, f"{prefix}: condition_blind must be true", errors)
            _require(
                audit.get("contains_identifiable_participant_material") is False,
                f"{prefix}: identifiable participant material is prohibited",
                errors,
            )

        family = packet.get("contrast_family")
        if family == "reference_target_inadequacy":
            adequacy = intention.get("adequacy_status") if isinstance(intention, dict) else None
            codes = set(reason_codes or [])
            if adequacy != "adequate":
                _require(
                    bool(codes & {"MAP_TOO_SPARSE", "MAP_INTERNAL_CONFLICT", "MAP_UNINTERPRETABLE", "MAP_RESPONSE_DEPENDENT", "MAP_OTHER"}),
                    f"{prefix}: inadequate reference targets require a map-inadequacy reason code",
                    errors,
                )

    expected_digest = manifest.get("content_digest_sha256")
    actual_digest = canonical_packets_digest(packets)
    _require(expected_digest == actual_digest, "content_digest_sha256 does not match canonical packet content", errors)

    if len(packets) < 42:
        warnings.append(
            "This 24-packet development bank does not satisfy the full 42-candidate "
            "region-by-domain blueprint and cannot be treated as the final anchor bank."
        )

    summary = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "packet_count": len(packets),
        "contrast_group_count": len(group_members),
        "domain_counts": dict(sorted(domain_counts.items())),
        "contrast_family_counts": dict(sorted(Counter(packet.get("contrast_family") for packet in packets).items())),
        "score_region_counts": {
            str(region): sum(packet.get("provisional_score_region") == region for packet in packets)
            for region in range(1, 8)
        },
        "content_digest_sha256": actual_digest,
    }
    if errors:
        raise ManifestValidationError(json.dumps(summary, indent=2))
    return summary


def build_blind_review_export(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a target-blind expert-review export.

    The export deliberately removes provisional targets, rationale, contrast labels,
    audit metadata, and any prior review or pilot fields.
    """
    validate_manifest(manifest)
    review_items: list[dict[str, Any]] = []
    for packet in manifest["packets"]:
        # Start from an explicit allowlist rather than deleting fields from the source.
        review_item = {
            "review_item_id": packet["anchor_id"],
            "anchor_version": packet["anchor_version"],
            "prompt_domain": packet["prompt_domain"],
            "prompt_text": packet["prompt_text"],
            "private_intention_map": deepcopy(packet["private_intention_map"]),
            "candidate_response": packet["candidate_response"],
            "review_form": {
                "semantic_fidelity_score": None,
                "reason_codes": [],
                "intention_map_adequacy": None,
                "confidence_1_to_5": None,
                "ambiguity_note": None,
                "reviewer_id": None,
                "reviewed_at_utc": None,
                "locked_before_target_reveal": False,
            },
        }
        review_items.append(review_item)

    export = {
        "schema_version": "egc2-anchor-blind-review-export-0.1.0",
        "source_manifest_id": manifest["manifest_id"],
        "source_content_digest_sha256": manifest["content_digest_sha256"],
        "instructions": {
            "target_blind": True,
            "minimum_independent_reviewers_per_item": 3,
            "lock_before_reveal": True,
            "prohibited": [
                "Do not show provisional score regions.",
                "Do not show constructor rationale or admissible score ranges.",
                "Do not allow reviewers to discuss scores before locking submissions.",
                "Do not convert a synthetic constructor target into a gold score."
            ],
        },
        "items": review_items,
    }
    assert all(not (LEAKAGE_KEYS & set(item)) for item in export["items"])
    return export


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--blind-export-out", type=Path)
    args = parser.parse_args(argv)

    with args.manifest.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    try:
        summary = validate_manifest(manifest)
    except ManifestValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if args.blind_export_out:
        export = build_blind_review_export(manifest)
        args.blind_export_out.parent.mkdir(parents=True, exist_ok=True)
        args.blind_export_out.write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

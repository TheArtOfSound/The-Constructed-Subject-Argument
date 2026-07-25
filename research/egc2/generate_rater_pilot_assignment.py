#!/usr/bin/env python3
"""Generate and validate the EGC 2.0 rater-pilot assignment design.

The default design assumes 30 participants with two condition-paired responses each,
8 raters, and 4 primary ratings per response. For every participant, the two
responses are assigned to complementary four-rater sets. Consequently no rater
sees both responses from one participant, every response receives four ratings,
and every rater receives exactly one primary response from every participant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DOMAINS = ("autobiographical_meaning", "conceptual_explanation", "position_and_reasoning")
CONDITIONS = ("private", "evaluated")


class DesignError(ValueError):
    pass


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_responses(participants: int = 30) -> list[dict[str, str]]:
    if participants % len(DOMAINS) != 0:
        raise DesignError("participant count must be divisible by three prompt domains")
    responses: list[dict[str, str]] = []
    per_domain = participants // len(DOMAINS)
    for p in range(participants):
        participant_id = f"P{p + 1:03d}"
        domain = DOMAINS[p // per_domain]
        for condition in CONDITIONS:
            responses.append({
                "response_id": f"{participant_id}_{condition}",
                "participant_id": participant_id,
                "prompt_domain": domain,
                "condition": condition,
            })
    return responses


def choose_balanced_subsets(raters: list[str], participants: int, seed: int) -> list[tuple[str, ...]]:
    if len(raters) != 8:
        raise DesignError("the preregistered pilot design requires exactly eight raters")
    if participants % len(DOMAINS) != 0:
        raise DesignError("participants must divide evenly across prompt domains")
    per_domain = participants // len(DOMAINS)
    if per_domain % 2:
        raise DesignError("participants per domain must be even for exact condition balance")
    rng = random.Random(seed)
    from itertools import combinations
    candidates = list(combinations(raters, 4))
    subsets: list[tuple[str, ...]] = []
    # Within every domain block, generate half the partitions and then their
    # complements. This guarantees each rater sees exactly half private and half
    # evaluated responses in every domain, while the seed controls which paired
    # response each rater receives.
    for _domain in DOMAINS:
        first_half: list[tuple[str, ...]] = []
        for _ in range(per_domain // 2):
            first_half.append(rng.choice(candidates))
        second_half = [tuple(sorted(set(raters) - set(combo))) for combo in first_half]
        domain_subsets = first_half + second_half
        rng.shuffle(domain_subsets)
        subsets.extend(domain_subsets)
    return subsets


def assign_primary(responses: list[dict[str, str]], raters: list[str], seed: int) -> list[dict[str, str]]:
    by_participant: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for response in responses:
        by_participant[response["participant_id"]][response["condition"]] = response
    participants = sorted(by_participant)
    subsets = choose_balanced_subsets(raters, len(participants), seed)
    assignments: list[dict[str, str]] = []
    all_raters = set(raters)
    for participant_id, private_raters in zip(participants, subsets):
        private_set = set(private_raters)
        evaluated_set = all_raters - private_set
        for condition, assigned in (("private", private_set), ("evaluated", evaluated_set)):
            response = by_participant[participant_id][condition]
            for rater_id in sorted(assigned):
                assignments.append({
                    "assignment_type": "primary_response",
                    "rater_id": rater_id,
                    **response,
                })
    return assignments


def assign_anchors(anchor_ids: list[str], raters: list[str], ratings_per_anchor: int, seed: int) -> list[dict[str, str]]:
    if ratings_per_anchor < 1 or ratings_per_anchor > len(raters):
        raise DesignError("ratings_per_anchor must be between 1 and the number of raters")
    rng = random.Random(seed + 1)
    loads = Counter({r: 0 for r in raters})
    assignments: list[dict[str, str]] = []
    for anchor_id in anchor_ids:
        shuffled = raters[:]
        rng.shuffle(shuffled)
        selected = sorted(shuffled, key=lambda r: (loads[r], shuffled.index(r)))[:ratings_per_anchor]
        for rater_id in selected:
            assignments.append({
                "assignment_type": "anchor",
                "rater_id": rater_id,
                "anchor_id": anchor_id,
            })
            loads[rater_id] += 1
    return assignments


def assign_blind_repeats(primary: list[dict[str, str]], repeat_fraction: float, seed: int) -> list[dict[str, str]]:
    if not 0 <= repeat_fraction < 1:
        raise DesignError("repeat_fraction must be in [0, 1)")
    rng = random.Random(seed + 2)
    by_rater: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary:
        by_rater[row["rater_id"]].append(row)
    desired_total = round(len(primary) * repeat_fraction)
    base, remainder = divmod(desired_total, len(by_rater))
    repeats: list[dict[str, str]] = []
    for offset, rater_id in enumerate(sorted(by_rater)):
        count = base + (1 if offset < remainder else 0)
        pool = by_rater[rater_id][:]
        rng.shuffle(pool)
        for source in pool[:count]:
            repeated = dict(source)
            repeated["assignment_type"] = "blind_repeat"
            repeated["repeat_of_response_id"] = source["response_id"]
            repeats.append(repeated)
    return repeats


def summarize(primary: list[dict[str, str]], anchors: list[dict[str, str]], repeats: list[dict[str, str]]) -> dict[str, Any]:
    raters = sorted({row["rater_id"] for row in primary})
    response_counts = Counter(row["response_id"] for row in primary)
    rater_primary = Counter(row["rater_id"] for row in primary)
    rater_anchor = Counter(row["rater_id"] for row in anchors)
    rater_repeat = Counter(row["rater_id"] for row in repeats)
    domain_by_rater = {r: Counter() for r in raters}
    condition_by_rater = {r: Counter() for r in raters}
    participant_by_rater = {r: Counter() for r in raters}
    for row in primary:
        domain_by_rater[row["rater_id"]][row["prompt_domain"]] += 1
        condition_by_rater[row["rater_id"]][row["condition"]] += 1
        participant_by_rater[row["rater_id"]][row["participant_id"]] += 1
    return {
        "primary_assignment_count": len(primary),
        "anchor_assignment_count": len(anchors),
        "blind_repeat_count": len(repeats),
        "ratings_per_response": dict(sorted(response_counts.items())),
        "primary_load_by_rater": dict(sorted(rater_primary.items())),
        "anchor_load_by_rater": dict(sorted(rater_anchor.items())),
        "repeat_load_by_rater": dict(sorted(rater_repeat.items())),
        "domain_load_by_rater": {r: dict(sorted(c.items())) for r, c in domain_by_rater.items()},
        "condition_load_by_rater": {r: dict(sorted(c.items())) for r, c in condition_by_rater.items()},
        "max_responses_per_participant_per_rater": max(
            count for counter in participant_by_rater.values() for count in counter.values()
        ),
    }


def validate_design(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    primary = payload["assignments"]["primary"]
    anchors = payload["assignments"]["anchors"]
    repeats = payload["assignments"]["blind_repeats"]
    raters = payload["design"]["rater_ids"]
    expected_ratings = payload["design"]["ratings_per_response"]

    response_counts = Counter(row["response_id"] for row in primary)
    if any(count != expected_ratings for count in response_counts.values()):
        errors.append("PRIMARY_RESPONSE_RATING_COUNT")

    seen_pairs: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in primary:
        seen_pairs[(row["participant_id"], row["rater_id"])].add(row["response_id"])
    if any(len(ids) > 1 for ids in seen_pairs.values()):
        errors.append("RATER_SAW_BOTH_PARTICIPANT_RESPONSES")

    primary_loads = Counter(row["rater_id"] for row in primary)
    if len(set(primary_loads[r] for r in raters)) != 1:
        errors.append("PRIMARY_RATER_LOAD_IMBALANCE")

    for rater in raters:
        domains = Counter(row["prompt_domain"] for row in primary if row["rater_id"] == rater)
        if len(set(domains.values())) != 1 or set(domains) != set(DOMAINS):
            errors.append(f"DOMAIN_IMBALANCE:{rater}")
        conditions = Counter(row["condition"] for row in primary if row["rater_id"] == rater)
        if conditions.get("private") != conditions.get("evaluated"):
            errors.append(f"CONDITION_IMBALANCE:{rater}")

    anchor_counts = Counter(row["anchor_id"] for row in anchors)
    if anchor_counts and len(set(anchor_counts.values())) != 1:
        errors.append("ANCHOR_RATING_COUNT_IMBALANCE")
    anchor_loads = Counter(row["rater_id"] for row in anchors)
    if anchor_loads and max(anchor_loads.values()) - min(anchor_loads.values()) > 1:
        errors.append("ANCHOR_RATER_LOAD_IMBALANCE")

    primary_keys = {(row["rater_id"], row["response_id"]) for row in primary}
    if any((row["rater_id"], row["repeat_of_response_id"]) not in primary_keys for row in repeats):
        errors.append("BLIND_REPEAT_WITHOUT_SOURCE_RATING")

    expected_repeat_count = round(len(primary) * payload["design"]["blind_repeat_fraction"])
    if len(repeats) != expected_repeat_count:
        errors.append("BLIND_REPEAT_COUNT")
    return errors


def generate(seed: int = 20260725, participants: int = 30, anchor_count: int = 42) -> dict[str, Any]:
    raters = [f"R{i + 1:02d}" for i in range(8)]
    responses = build_responses(participants)
    primary = assign_primary(responses, raters, seed)
    anchor_ids = [f"A{i + 1:03d}" for i in range(anchor_count)]
    anchors = assign_anchors(anchor_ids, raters, ratings_per_anchor=4, seed=seed)
    repeats = assign_blind_repeats(primary, repeat_fraction=0.05, seed=seed)
    payload: dict[str, Any] = {
        "schema_version": "egc2-rater-pilot-assignment-0.1.0",
        "design": {
            "seed": seed,
            "participant_count": participants,
            "response_count": len(responses),
            "rater_ids": raters,
            "ratings_per_response": 4,
            "anchor_count": anchor_count,
            "ratings_per_anchor": 4,
            "blind_repeat_fraction": 0.05,
            "conditions": list(CONDITIONS),
            "prompt_domains": list(DOMAINS),
        },
        "responses": responses,
        "assignments": {
            "primary": primary,
            "anchors": anchors,
            "blind_repeats": repeats,
        },
    }
    payload["summary"] = summarize(primary, anchors, repeats)
    payload["validation_errors"] = validate_design(payload)
    payload["content_sha256"] = canonical_hash({k: v for k, v in payload.items() if k != "content_sha256"})
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--participants", type=int, default=30)
    parser.add_argument("--anchor-count", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("research/egc2/rater_pilot_assignment.v0.1.json"))
    args = parser.parse_args()
    try:
        payload = generate(args.seed, args.participants, args.anchor_count)
    except DesignError as exc:
        print(f"EGC assignment error: {exc}")
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["validation_errors"]:
        print(json.dumps(payload["validation_errors"], indent=2))
        return 1
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"Wrote validated assignment to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

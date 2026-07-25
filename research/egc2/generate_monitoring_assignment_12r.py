#!/usr/bin/env python3
"""Generate a 12-rater connected incomplete-block monitoring assignment.

The default design contains four concealed monitoring classes with 36 unique
study-level items per class. Every item is rated by four raters. Each rater
therefore receives 12 items from each class (48 total), while no rater sees the
entire 144-item bank. The construction uses three cyclic block families per
class, giving exact load balance by construction and strong co-rating overlap.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

CLASSES = (
    "exact_recurring_anchor",
    "surface_variant_anchor",
    "structural_transfer_probe",
    "novel_response",
)
RATER_COUNT = 12
RATINGS_PER_ITEM = 4
ITEMS_PER_CLASS = 36
# Each tuple generates 12 cyclic four-rater blocks. Three patterns give 36
# items per class. Every pattern is a complete co-rating graph on 12 raters and
# remains connected after removal of any two raters.
OFFSET_FAMILIES = (
    (0, 6, 8, 11),
    (0, 6, 7, 10),
    (0, 5, 9, 11),
)


class DesignError(ValueError):
    """Raised when a monitoring assignment violates its design contract."""


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cyclic_block(start: int, offsets: tuple[int, ...], rater_count: int) -> tuple[int, ...]:
    return tuple(sorted((start + offset) % rater_count for offset in offsets))


def build_items(seed: int = 20260725) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return item metadata and four-rater assignments."""
    raters = [f"R{i + 1:02d}" for i in range(RATER_COUNT)]
    items: list[dict[str, str]] = []
    assignments: list[dict[str, str]] = []
    rng = random.Random(seed)

    for class_index, item_class in enumerate(CLASSES):
        # Rotate the mapping from cyclic indices to rater IDs independently by
        # class. This prevents one class from reusing the same visible block map.
        permuted = raters[:]
        rng.shuffle(permuted)
        item_number = 0
        for family_index, offsets in enumerate(OFFSET_FAMILIES):
            starts = list(range(RATER_COUNT))
            rng.shuffle(starts)
            for start in starts:
                item_number += 1
                item_id = f"M{class_index + 1}_{item_number:03d}"
                block = _cyclic_block(start, offsets, RATER_COUNT)
                selected = sorted(permuted[index] for index in block)
                items.append({
                    "item_id": item_id,
                    "item_class": item_class,
                    "block_family": f"F{family_index + 1}",
                })
                for rater_id in selected:
                    assignments.append({
                        "item_id": item_id,
                        "item_class": item_class,
                        "rater_id": rater_id,
                    })
        if item_number != ITEMS_PER_CLASS:
            raise DesignError(f"unexpected item count for {item_class}: {item_number}")
    return items, assignments


def build_rater_queues(assignments: list[dict[str, str]], seed: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Create concealed rater queues and private audit schedules.

    Each rater has 12 items from every class. Sessions are assembled in 12
    four-item cycles, one item from each class per cycle. Class order is shuffled
    per cycle subject to no adjacent equal classes. The rater-facing queue omits
    class and block metadata.
    """
    by_rater_class: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in assignments:
        by_rater_class[row["rater_id"]][row["item_class"]].append(row)

    public: dict[str, list[dict[str, Any]]] = {}
    audit: dict[str, list[dict[str, Any]]] = {}
    for rater_index, rater_id in enumerate(sorted(by_rater_class)):
        rng = random.Random(seed + 1000 + rater_index)
        pools: dict[str, list[dict[str, str]]] = {}
        for item_class in CLASSES:
            pool = by_rater_class[rater_id][item_class][:]
            if len(pool) != ITEMS_PER_CLASS * RATINGS_PER_ITEM // RATER_COUNT:
                raise DesignError(f"class load mismatch for {rater_id}/{item_class}: {len(pool)}")
            rng.shuffle(pool)
            pools[item_class] = pool

        sequence: list[dict[str, str]] = []
        previous_class: str | None = None
        for _cycle in range(12):
            order = list(CLASSES)
            for _ in range(100):
                rng.shuffle(order)
                if order[0] != previous_class:
                    break
            else:
                raise DesignError("could not construct mixed class order")
            for item_class in order:
                sequence.append(pools[item_class].pop())
            previous_class = order[-1]

        audit_rows: list[dict[str, Any]] = []
        public_rows: list[dict[str, Any]] = []
        for position, row in enumerate(sequence, 1):
            presentation_id = hashlib.sha256(
                f"{seed}|{rater_id}|{position}|{row['item_id']}".encode("utf-8")
            ).hexdigest()[:20]
            audit_rows.append({
                "position": position,
                "presentation_id": presentation_id,
                **row,
            })
            public_rows.append({
                "position": position,
                "presentation_id": presentation_id,
                "item_id": row["item_id"],
            })
        audit[rater_id] = audit_rows
        public[rater_id] = public_rows
    return public, audit


def _co_rating_graph(assignments: Iterable[dict[str, str]], active_raters: set[str]) -> dict[str, set[str]]:
    by_item: dict[str, list[str]] = defaultdict(list)
    for row in assignments:
        if row["rater_id"] in active_raters:
            by_item[row["item_id"]].append(row["rater_id"])
    graph = {rater: set() for rater in active_raters}
    for item_raters in by_item.values():
        for left, right in itertools.combinations(sorted(set(item_raters)), 2):
            graph[left].add(right)
            graph[right].add(left)
    return graph


def _connected(graph: dict[str, set[str]]) -> bool:
    if not graph:
        return True
    start = next(iter(graph))
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbor in graph[node] - seen:
            seen.add(neighbor)
            stack.append(neighbor)
    return len(seen) == len(graph)


def dropout_audit(assignments: list[dict[str, str]], raters: list[str]) -> dict[str, Any]:
    """Exhaustively audit every one- and two-rater dropout combination."""
    scenarios: dict[str, Any] = {}
    all_set = set(raters)
    for drop_count in (1, 2):
        failures: list[dict[str, Any]] = []
        minimum_item_ratings = RATINGS_PER_ITEM
        minimum_class_degree = RATER_COUNT
        scenario_count = 0
        for dropped in itertools.combinations(raters, drop_count):
            scenario_count += 1
            active = all_set - set(dropped)
            counts = Counter(
                row["item_id"] for row in assignments if row["rater_id"] in active
            )
            minimum_item_ratings = min(minimum_item_ratings, min(counts.values()))
            overall_graph = _co_rating_graph(assignments, active)
            overall_connected = _connected(overall_graph)
            class_connected = True
            class_min_degree = RATER_COUNT
            for item_class in CLASSES:
                rows = [row for row in assignments if row["item_class"] == item_class]
                graph = _co_rating_graph(rows, active)
                class_connected = class_connected and _connected(graph)
                class_min_degree = min(class_min_degree, min((len(v) for v in graph.values()), default=0))
            minimum_class_degree = min(minimum_class_degree, class_min_degree)
            if min(counts.values()) < RATINGS_PER_ITEM - drop_count or not overall_connected or not class_connected:
                failures.append({
                    "dropped": list(dropped),
                    "minimum_item_ratings": min(counts.values()),
                    "overall_connected": overall_connected,
                    "all_classes_connected": class_connected,
                })
        scenarios[str(drop_count)] = {
            "scenario_count": scenario_count,
            "failure_count": len(failures),
            "minimum_remaining_ratings_per_item": minimum_item_ratings,
            "minimum_class_graph_degree": minimum_class_degree,
            "failures": failures,
        }
    return scenarios


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    assignments = payload["assignments"]
    items = payload["items"]
    raters = payload["design"]["rater_ids"]

    item_counts = Counter(row["item_id"] for row in assignments)
    if len(item_counts) != len(CLASSES) * ITEMS_PER_CLASS:
        errors.append("ITEM_COUNT")
    if any(count != RATINGS_PER_ITEM for count in item_counts.values()):
        errors.append("RATINGS_PER_ITEM")

    class_items = Counter(row["item_class"] for row in items)
    if any(class_items.get(item_class) != ITEMS_PER_CLASS for item_class in CLASSES):
        errors.append("ITEMS_PER_CLASS")

    loads = Counter(row["rater_id"] for row in assignments)
    if set(loads.values()) != {48}:
        errors.append("TOTAL_RATER_LOAD")
    for rater_id in raters:
        class_load = Counter(
            row["item_class"] for row in assignments if row["rater_id"] == rater_id
        )
        if any(class_load.get(item_class) != 12 for item_class in CLASSES):
            errors.append(f"CLASS_LOAD:{rater_id}")

    audit = payload["audit_schedule"]
    public = payload["rater_queues"]
    for rater_id in raters:
        if len(audit[rater_id]) != 48 or len(public[rater_id]) != 48:
            errors.append(f"QUEUE_LENGTH:{rater_id}")
        if any("item_class" in row or "rater_id" in row for row in public[rater_id]):
            errors.append(f"PUBLIC_METADATA_LEAK:{rater_id}")
        classes = [row["item_class"] for row in audit[rater_id]]
        if any(left == right for left, right in zip(classes, classes[1:])):
            errors.append(f"ADJACENT_CLASS_REPEAT:{rater_id}")
        quartiles = [classes[i:i + 12] for i in range(0, 48, 12)]
        for q_index, quartile in enumerate(quartiles):
            counts = Counter(quartile)
            if max(counts.values()) - min(counts.values()) > 1:
                errors.append(f"QUARTILE_CLASS_IMBALANCE:{rater_id}:{q_index}")

    for drop_count in ("1", "2"):
        if payload["dropout_audit"][drop_count]["failure_count"]:
            errors.append(f"DROPOUT_FAILURE:{drop_count}")
    return sorted(set(errors))


def generate(seed: int = 20260725) -> dict[str, Any]:
    items, assignments = build_items(seed)
    raters = [f"R{i + 1:02d}" for i in range(RATER_COUNT)]
    public, audit = build_rater_queues(assignments, seed)
    payload: dict[str, Any] = {
        "schema_version": "egc2-monitoring-assignment-0.1.0",
        "design": {
            "seed": seed,
            "rater_ids": raters,
            "item_classes": list(CLASSES),
            "items_per_class": ITEMS_PER_CLASS,
            "ratings_per_item": RATINGS_PER_ITEM,
            "items_per_rater_per_class": 12,
            "total_items_per_rater": 48,
            "construction": "three_cyclic_block_families_per_class",
        },
        "items": items,
        "assignments": assignments,
        "rater_queues": public,
        "audit_schedule": audit,
        "dropout_audit": dropout_audit(assignments, raters),
    }
    payload["validation_errors"] = validate(payload)
    payload["content_sha256"] = canonical_hash({k: v for k, v in payload.items() if k != "content_sha256"})
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/egc2/monitoring_assignment_12r.v0.1.json"),
    )
    args = parser.parse_args()
    payload = generate(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["validation_errors"]:
        print(json.dumps(payload["validation_errors"], indent=2))
        return 1
    summary = {
        "items": len(payload["items"]),
        "assignments": len(payload["assignments"]),
        "items_per_rater": payload["design"]["total_items_per_rater"],
        "one_rater_dropout_failures": payload["dropout_audit"]["1"]["failure_count"],
        "two_rater_dropout_failures": payload["dropout_audit"]["2"]["failure_count"],
        "content_sha256": payload["content_sha256"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

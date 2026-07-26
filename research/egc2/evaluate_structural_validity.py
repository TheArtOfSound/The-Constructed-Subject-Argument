from __future__ import annotations

import argparse
import copy
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

DEFAULT_CLASSES = ("exact_anchor", "surface_variant", "structural_transfer", "novel")
DEFAULT_DOMAINS = ("autobiographical", "conceptual", "position", "heldout")


def _edge_key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def _components(nodes: Iterable[str], adjacency: dict[str, set[str]]) -> list[list[str]]:
    unseen = set(nodes)
    out: list[list[str]] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        component: list[str] = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbour in adjacency.get(node, set()):
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        out.append(sorted(component))
    return sorted(out, key=lambda c: (len(c), c))


def _articulation_points_and_bridges(nodes: Iterable[str], adjacency: dict[str, set[str]]) -> tuple[list[str], list[list[str]]]:
    time = 0
    disc: dict[str, int] = {}
    low: dict[str, int] = {}
    parent: dict[str, str | None] = {}
    articulation: set[str] = set()
    bridges: set[tuple[str, str]] = set()

    def dfs(u: str) -> None:
        nonlocal time
        time += 1
        disc[u] = low[u] = time
        children = 0
        for v in sorted(adjacency.get(u, set())):
            if v not in disc:
                parent[v] = u
                children += 1
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent.get(u) is None and children > 1:
                    articulation.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    articulation.add(u)
                if low[v] > disc[u]:
                    bridges.add(_edge_key(u, v))
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for node in sorted(set(nodes)):
        if node not in disc:
            parent[node] = None
            dfs(node)
    return sorted(articulation), [list(x) for x in sorted(bridges)]


def _graph_diagnostics(rows: list[dict[str, Any]], classes: list[str]) -> dict[str, Any]:
    items = sorted({str(r["item"]) for r in rows})
    raters = sorted({str(r["rater"]) for r in rows})
    bip_nodes = [f"i:{x}" for x in items] + [f"r:{x}" for x in raters]
    bip_adj: dict[str, set[str]] = defaultdict(set)
    item_degree: dict[str, int] = defaultdict(int)
    rater_degree: dict[str, int] = defaultdict(int)
    item_to_raters: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        item = str(row["item"])
        rater = str(row["rater"])
        i_node, r_node = f"i:{item}", f"r:{rater}"
        bip_adj[i_node].add(r_node)
        bip_adj[r_node].add(i_node)
        item_to_raters[item].add(rater)
    for item, rs in item_to_raters.items():
        item_degree[item] = len(rs)
        for rater in rs:
            rater_degree[rater] += 1

    def corating(filter_class: str | None = None) -> dict[str, Any]:
        adjacency: dict[str, set[str]] = defaultdict(set)
        active: set[str] = set()
        grouped: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            if filter_class is not None and row["class"] != filter_class:
                continue
            rater = str(row["rater"])
            active.add(rater)
            grouped[str(row["item"])].add(rater)
        for rs in grouped.values():
            ordered = sorted(rs)
            for i, left in enumerate(ordered):
                for right in ordered[i + 1 :]:
                    adjacency[left].add(right)
                    adjacency[right].add(left)
        components = _components(active, adjacency)
        articulation, bridges = _articulation_points_and_bridges(active, adjacency)
        degrees = {r: len(adjacency.get(r, set())) for r in sorted(active)}
        return {
            "active_raters": sorted(active),
            "component_count": len(components),
            "components": components,
            "minimum_degree": min(degrees.values()) if degrees else 0,
            "degrees": degrees,
            "articulation_raters": articulation,
            "bridge_edges": bridges,
        }

    bip_components = _components(bip_nodes, bip_adj)
    overall = corating()
    by_class = {c: corating(c) for c in classes}
    return {
        "overall_bipartite_component_count": len(bip_components),
        "overall_bipartite_components": bip_components,
        "minimum_item_degree": min(item_degree.values()) if item_degree else 0,
        "minimum_rater_degree": min(rater_degree.values()) if rater_degree else 0,
        "overall_rater_corating": overall,
        "class_specific_rater_corating": by_class,
    }


def _gate(gate_id: str, passed: bool, metrics: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    return {"id": gate_id, "passed": bool(passed), "metrics": metrics, "failures": failures}


def evaluate(rows: list[dict[str, Any]], gate_spec: dict[str, Any], *, observed_variance: float | None = None, undefined_pattern_fraction: float | None = None, planned_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise TypeError("rows must be a list")
    planned = gate_spec["planned"]
    classes = sorted({str(r.get("class")) for r in (planned_rows or rows) if r.get("class") is not None}) or list(DEFAULT_CLASSES)
    domains = sorted({str(r.get("domain")) for r in (planned_rows or rows) if r.get("domain") is not None}) or list(DEFAULT_DOMAINS)
    expected_raters = {str(i) for i in range(int(planned["raters"]))}
    expected_items = {str(r["item"]) for r in planned_rows} if planned_rows else {f"{c}:{i}" for c in classes for i in range(int(planned["items_per_class"]))}
    gate_results: list[dict[str, Any]] = []
    required = ("item", "rater", "class", "domain")
    unmapped = sum(any(k not in r or r[k] is None for k in required) for r in rows)
    identities = [(str(r.get("item")), str(r.get("rater"))) for r in rows if all(k in r and r[k] is not None for k in required)]
    duplicates = len(identities) - len(set(identities))
    unknown_items = sum(str(r.get("item")) not in expected_items for r in rows if r.get("item") is not None)
    unknown_raters = sum(str(r.get("rater")) not in expected_raters for r in rows if r.get("rater") is not None)
    g0_fail = []
    if unmapped: g0_fail.append(f"unmapped_rows={unmapped}")
    if duplicates: g0_fail.append(f"duplicate_rating_identities={duplicates}")
    if unknown_items: g0_fail.append(f"unknown_items={unknown_items}")
    if unknown_raters: g0_fail.append(f"unknown_raters={unknown_raters}")
    gate_results.append(_gate("G0_SCHEMA_IDENTITY", not g0_fail, {"unmapped_rows": unmapped, "duplicate_rating_identities": duplicates, "unknown_items": unknown_items, "unknown_raters": unknown_raters}, g0_fail))
    valid = [r for r in rows if all(k in r and r[k] is not None for k in required)]
    item_raters: dict[str, set[str]] = defaultdict(set)
    for r in valid: item_raters[str(r["item"])].add(str(r["rater"]))
    counts = {item: len(item_raters.get(item, set())) for item in sorted(expected_items)}
    min_count = min(counts.values()) if counts else 0
    frac5 = sum(v >= 5 for v in counts.values()) / len(counts) if counts else 0.0
    g1_fail = []
    if min_count < 4: g1_fail.append(f"minimum_distinct_raters_per_item={min_count}<4")
    if frac5 < 0.95: g1_fail.append(f"fraction_items_with_at_least_5={frac5:.6f}<0.95")
    gate_results.append(_gate("G1_ITEM_REPLICATION", not g1_fail, {"minimum_distinct_raters_per_item": min_count, "fraction_items_with_at_least_5_ratings": frac5, "items_below_4": sorted([k for k,v in counts.items() if v < 4]), "items_below_5": sorted([k for k,v in counts.items() if v < 5])}, g1_fail))
    active = {str(r["rater"]) for r in valid}
    by_class = {c: {str(r["rater"]) for r in valid if str(r["class"]) == c} for c in classes}
    by_domain = {d: {str(r["rater"]) for r in valid if str(r["domain"]) == d} for d in domains}
    g2_fail = []
    if len(active) < 10: g2_fail.append(f"active_raters_overall={len(active)}<10")
    for c, rs in by_class.items():
        if len(rs) < 8: g2_fail.append(f"active_raters_class[{c}]={len(rs)}<8")
    for d, rs in by_domain.items():
        if len(rs) < 8: g2_fail.append(f"active_raters_domain[{d}]={len(rs)}<8")
    gate_results.append(_gate("G2_ACTIVE_RATER_COVERAGE", not g2_fail, {"active_raters_overall": len(active), "active_raters_by_class": {k: len(v) for k,v in by_class.items()}, "active_raters_by_domain": {k: len(v) for k,v in by_domain.items()}}, g2_fail))
    planned_source = planned_rows or []
    if planned_source:
        planned_class = {c: sum(str(r["class"]) == c for r in planned_source) for c in classes}
        planned_domain = {d: sum(str(r["domain"]) == d for r in planned_source) for d in domains}
        planned_cd = {(c,d): sum(str(r["class"]) == c and str(r["domain"]) == d for r in planned_source) for c in classes for d in domains}
    else:
        per_class = int(planned["items_per_class"]) * int(planned["ratings_per_item"])
        planned_class = {c: per_class for c in classes}
        planned_domain = {d: int(planned["total_assignments"]) // len(domains) for d in domains}
        planned_cd = {(c,d): per_class // len(domains) for c in classes for d in domains}
    retained_class = {c: sum(str(r["class"]) == c for r in valid) for c in classes}
    class_frac = {c: retained_class[c] / planned_class[c] if planned_class[c] else 0.0 for c in classes}
    class_range = max(class_frac.values()) - min(class_frac.values()) if class_frac else 0.0
    g3_fail = []
    for c, value in class_frac.items():
        if value < 0.80: g3_fail.append(f"class_retention[{c}]={value:.6f}<0.80")
    if class_range > 0.10 + 1e-12: g3_fail.append(f"class_retention_range={class_range:.6f}>0.10")
    gate_results.append(_gate("G3_CLASS_BALANCE", not g3_fail, {"retention_fraction_by_class": class_frac, "retention_fraction_range": class_range}, g3_fail))
    retained_domain = {d: sum(str(r["domain"]) == d for r in valid) for d in domains}
    domain_frac = {d: retained_domain[d] / planned_domain[d] if planned_domain[d] else 0.0 for d in domains}
    within_class_ranges: dict[str, float] = {}
    g4_fail = []
    for d, value in domain_frac.items():
        if value < 0.75: g4_fail.append(f"domain_retention[{d}]={value:.6f}<0.75")
    for c in classes:
        vals = []
        for d in domains:
            denom = planned_cd[(c,d)]
            kept = sum(str(r["class"]) == c and str(r["domain"]) == d for r in valid)
            vals.append(kept / denom if denom else 0.0)
        spread = max(vals) - min(vals) if vals else 0.0
        within_class_ranges[c] = spread
        if spread > 0.15 + 1e-12: g4_fail.append(f"domain_retention_range_within_class[{c}]={spread:.6f}>0.15")
    gate_results.append(_gate("G4_DOMAIN_BALANCE", not g4_fail, {"retention_fraction_by_domain": domain_frac, "domain_retention_range_within_class": within_class_ranges}, g4_fail))
    graph = _graph_diagnostics(valid, classes)
    class_components = {c: v["component_count"] for c,v in graph["class_specific_rater_corating"].items()}
    g5_fail = []
    if graph["overall_bipartite_component_count"] != 1: g5_fail.append(f"overall_bipartite_components={graph['overall_bipartite_component_count']}!=1")
    if graph["overall_rater_corating"]["component_count"] != 1: g5_fail.append(f"overall_rater_corating_components={graph['overall_rater_corating']['component_count']}!=1")
    for c, n in class_components.items():
        if n != 1: g5_fail.append(f"class_corating_components[{c}]={n}!=1")
    gate_results.append(_gate("G5_GRAPH_IDENTIFIABILITY", not g5_fail, graph, g5_fail))
    g6_fail = []
    if observed_variance is None or observed_variance <= 0: g6_fail.append("observed_variance_missing_or_nonpositive")
    if undefined_pattern_fraction is None or not (0.0 <= undefined_pattern_fraction <= 1.0): g6_fail.append("undefined_pattern_fraction_missing_or_invalid")
    elif undefined_pattern_fraction > 0.10 + 1e-12: g6_fail.append(f"undefined_pattern_fraction={undefined_pattern_fraction:.6f}>0.10")
    gate_results.append(_gate("G6_INFERENTIAL_COMPUTABILITY", not g6_fail, {"observed_variance": observed_variance, "undefined_pattern_fraction": undefined_pattern_fraction}, g6_fail))
    failed = [g for g in gate_results if not g["passed"]]
    structural_failed = any(g["id"] != "G6_INFERENTIAL_COMPUTABILITY" for g in failed)
    status = "indeterminate_due_to_structural_invalidity" if structural_failed else ("indeterminate_due_to_inferential_noncomputability" if failed else "structurally_valid_inference_defined")
    return {"schema_version": "egc-structural-gate-evaluation-0.1.0", "gate_spec_version": gate_spec.get("schema_version"), "status": status, "report_confirmatory_p_value": status == "structurally_valid_inference_defined", "retained_rows": len(valid), "planned_rows": int(planned["total_assignments"]), "failed_gate_ids": [g["id"] for g in failed], "primary_failure_gate": failed[0]["id"] if failed else None, "gates": gate_results}


def apply_dropout(rows: list[dict[str, Any]], mechanism: str, *, seed: int = 20260726, domain: str = "heldout", fraction: float = 0.30, rater_scores: dict[str, float] | None = None, rater_count: int = 1) -> dict[str, Any]:
    if not 0.0 <= fraction <= 1.0: raise ValueError("fraction must be within [0,1]")
    if rater_count < 1: raise ValueError("rater_count must be positive")
    rng = random.Random(seed)
    raters = sorted({str(r["rater"]) for r in rows})
    scores = rater_scores or {r: 0.0 for r in raters}
    removed_raters: list[str] = []
    out = list(rows)
    if mechanism == "none": pass
    elif mechanism == "random_whole_rater":
        removed_raters = sorted(rng.sample(raters, min(rater_count, len(raters))))
        out = [r for r in rows if str(r["rater"]) not in set(removed_raters)]
    elif mechanism in {"highest_score_whole_rater", "lowest_score_whole_rater"}:
        reverse = mechanism.startswith("highest")
        removed_raters = sorted(raters, key=lambda r: (scores.get(r, 0.0), r), reverse=reverse)[:rater_count]
        out = [r for r in rows if str(r["rater"]) not in set(removed_raters)]
    elif mechanism == "domain_row":
        candidates = [i for i,r in enumerate(rows) if str(r["domain"]) == domain]
        n = round(fraction * len(candidates))
        remove = set(rng.sample(candidates, min(n, len(candidates))))
        out = [r for i,r in enumerate(rows) if i not in remove]
    elif mechanism == "domain_rater":
        removed_raters = sorted(rng.sample(raters, min(rater_count, len(raters))))
        out = [r for r in rows if not (str(r["domain"]) == domain and str(r["rater"]) in set(removed_raters))]
    elif mechanism == "targeted_domain_rater":
        removed_raters = sorted(raters, key=lambda r: (scores.get(r, 0.0), r), reverse=True)[:rater_count]
        out = [r for r in rows if not (str(r["domain"]) == domain and str(r["rater"]) in set(removed_raters))]
    elif mechanism == "combined_attack":
        removed_raters = sorted(raters, key=lambda r: (scores.get(r, 0.0), r), reverse=True)[:rater_count]
        stage = [r for r in rows if str(r["rater"]) not in set(removed_raters)]
        candidates = [i for i,r in enumerate(stage) if str(r["domain"]) == domain]
        n = round(fraction * len(candidates))
        remove = set(rng.sample(candidates, min(n, len(candidates))))
        out = [r for i,r in enumerate(stage) if i not in remove]
    else: raise ValueError(f"unknown mechanism: {mechanism}")
    return {"mechanism": mechanism, "seed": seed, "domain": domain, "fraction": fraction, "rater_count": rater_count, "removed_raters": removed_raters, "planned_rows": len(rows), "retained_rows": len(out), "rows": copy.deepcopy(out)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, type=Path)
    parser.add_argument("--gate-spec", required=True, type=Path)
    parser.add_argument("--planned-rows", type=Path)
    parser.add_argument("--observed-variance", type=float)
    parser.add_argument("--undefined-pattern-fraction", type=float)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = json.loads(args.rows.read_text())
    planned_rows = json.loads(args.planned_rows.read_text()) if args.planned_rows else None
    spec = json.loads(args.gate_spec.read_text())
    result = evaluate(rows, spec, observed_variance=args.observed_variance, undefined_pattern_fraction=args.undefined_pattern_fraction, planned_rows=planned_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const registryPath = path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json');
const outputPath = path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_REPAIR_GRAPH_REPORT.json');

const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
const states = registry.outcomes.map((outcome) => outcome.state);
const stateById = new Map(registry.outcomes.map((outcome) => [outcome.state, outcome]));
const edges = registry.repair_edges;

function unique(values) {
  return [...new Set(values)];
}

function adjacencyMap() {
  const map = new Map(states.map((state) => [state, []]));
  for (const edge of edges) map.get(edge.from)?.push(edge.to);
  return map;
}

function detectCycles(adjacency) {
  const cycles = [];
  const visiting = new Set();
  const visited = new Set();
  const stack = [];

  function visit(node) {
    if (visiting.has(node)) {
      const start = stack.indexOf(node);
      cycles.push([...stack.slice(start), node]);
      return;
    }
    if (visited.has(node)) return;
    visiting.add(node);
    stack.push(node);
    for (const next of adjacency.get(node) ?? []) visit(next);
    stack.pop();
    visiting.delete(node);
    visited.add(node);
  }

  for (const state of states) visit(state);
  return cycles;
}

function reachableFrom(start, adjacency) {
  const reached = new Set();
  const queue = [...(adjacency.get(start) ?? [])];
  while (queue.length) {
    const current = queue.shift();
    if (reached.has(current)) continue;
    reached.add(current);
    queue.push(...(adjacency.get(current) ?? []));
  }
  return [...reached].sort();
}

function shortestPath(from, to, adjacency) {
  if (from === to) return [from];
  const queue = [[from]];
  const visited = new Set([from]);
  while (queue.length) {
    const pathSoFar = queue.shift();
    const current = pathSoFar.at(-1);
    for (const next of adjacency.get(current) ?? []) {
      if (visited.has(next)) continue;
      const nextPath = [...pathSoFar, next];
      if (next === to) return nextPath;
      visited.add(next);
      queue.push(nextPath);
    }
  }
  return null;
}

function classifyEdge(edge) {
  const source = stateById.get(edge.from);
  const target = stateById.get(edge.to);
  const changes = {
    matching_adequacy: `${source.matching_adequate}->${target.matching_adequate}`,
    score_ceiling: `${source.maximum_generic_capacity_exclusion_score}->${target.maximum_generic_capacity_exclusion_score}`,
    hard_fail: `${source.hard_fail}->${target.hard_fail}`
  };
  const supportGain =
    Number(target.matching_adequate) > Number(source.matching_adequate) ||
    target.maximum_generic_capacity_exclusion_score > source.maximum_generic_capacity_exclusion_score ||
    Number(target.hard_fail) < Number(source.hard_fail);
  const supportLoss =
    Number(target.matching_adequate) < Number(source.matching_adequate) ||
    target.maximum_generic_capacity_exclusion_score < source.maximum_generic_capacity_exclusion_score ||
    Number(target.hard_fail) > Number(source.hard_fail);
  return {
    edge_id: edge.edge_id,
    from: edge.from,
    to: edge.to,
    epistemic_direction: edge.epistemic_direction,
    changes,
    support_gain: supportGain,
    support_loss: supportLoss,
    transition_kind: supportGain
      ? 'substantive_support_improvement'
      : supportLoss
        ? 'substantive_support_regression'
        : 'uncertainty_resolution_without_support_gain',
    interpretation: edge.interpretation
  };
}

export function generateCapacityRepairGraphReport() {
  const adjacency = adjacencyMap();
  const incoming = new Map(states.map((state) => [state, 0]));
  const outgoing = new Map(states.map((state) => [state, 0]));
  const invalidEdges = [];
  const selfLoops = [];

  for (const edge of edges) {
    if (!stateById.has(edge.from) || !stateById.has(edge.to)) invalidEdges.push(edge.edge_id);
    if (edge.from === edge.to) selfLoops.push(edge.edge_id);
    if (incoming.has(edge.to)) incoming.set(edge.to, incoming.get(edge.to) + 1);
    if (outgoing.has(edge.from)) outgoing.set(edge.from, outgoing.get(edge.from) + 1);
  }

  const roots = states.filter((state) => incoming.get(state) === 0).sort();
  const terminals = states.filter((state) => outgoing.get(state) === 0).sort();
  const cycles = detectCycles(adjacency);
  const reachability = Object.fromEntries(states.slice().sort().map((state) => [state, reachableFrom(state, adjacency)]));
  const terminalPaths = Object.fromEntries(
    states.slice().sort().map((state) => [
      state,
      terminals.map((terminal) => shortestPath(state, terminal, adjacency)).filter(Boolean)
    ])
  );
  const statesWithoutTerminalPath = states.filter((state) => terminalPaths[state].length === 0).sort();
  const edgeAnalysis = edges.map(classifyEdge);
  const supportRegressions = edgeAnalysis.filter((edge) => edge.support_loss).map((edge) => edge.edge_id);
  const resolutionOnlyEdges = edgeAnalysis
    .filter((edge) => edge.transition_kind === 'uncertainty_resolution_without_support_gain')
    .map((edge) => edge.edge_id);

  const duplicateStateIds = states.filter((state, index) => states.indexOf(state) !== index);
  const edgeIds = edges.map((edge) => edge.edge_id);
  const duplicateEdgeIds = edgeIds.filter((edge, index) => edgeIds.indexOf(edge) !== index);

  const checks = [
    { id: 'unique_states', pass: duplicateStateIds.length === 0 },
    { id: 'unique_edges', pass: duplicateEdgeIds.length === 0 },
    { id: 'valid_edge_endpoints', pass: invalidEdges.length === 0 },
    { id: 'no_self_loops', pass: selfLoops.length === 0 },
    { id: 'acyclic', pass: cycles.length === 0 },
    { id: 'terminal_reachability', pass: statesWithoutTerminalPath.length === 0 },
    { id: 'no_substantive_support_regressions', pass: supportRegressions.length === 0 },
    { id: 'epistemic_directions_declared', pass: edges.every((edge) => typeof edge.epistemic_direction === 'string' && edge.epistemic_direction.length > 0) }
  ];

  return {
    schema_version: '1.0.0',
    report_id: 'EXP11-GENERIC-CAPACITY-REPAIR-GRAPH-REPORT-001',
    generated: true,
    analysis_status: 'synthetic_normative_graph_analysis',
    registry: {
      path: 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json',
      registry_id: registry.registry_id,
      schema_version: registry.schema_version,
      protocol_id: registry.protocol_id
    },
    scope: {
      state_count: states.length,
      edge_count: edges.length,
      statement: 'This report analyzes the internal graph structure declared by the capacity-confound adjudication registry. It does not validate the causal model, thresholds, or scientific completeness of that registry.'
    },
    graph: {
      roots,
      terminals,
      cycles,
      reachability,
      terminal_paths: terminalPaths,
      edge_analysis: edgeAnalysis
    },
    findings: {
      duplicate_state_ids: unique(duplicateStateIds).sort(),
      duplicate_edge_ids: unique(duplicateEdgeIds).sort(),
      invalid_edges: invalidEdges.sort(),
      self_loops: selfLoops.sort(),
      states_without_terminal_path: statesWithoutTerminalPath,
      support_regression_edges: supportRegressions,
      uncertainty_resolution_without_support_gain_edges: resolutionOnlyEdges,
      partial_order_note: 'The graph is a directed acyclic repair relation, not a total ranking. Its two roots represent different defects: sufficient causal explanation and unresolved explanatory role. They are not treated as interchangeable severities.',
      terminal_note: 'no_detected_mismatch is the sole terminal state, but reaching it means only that the preregistered represented battery detected no mismatch; it does not establish absence of every generic-capacity confound.',
      resolution_note: 'resolve_role_partial resolves uncertainty while preserving a zero score ceiling and inadequate matching. It is epistemic resolution, not increased support for mechanism preservation.'
    },
    checks,
    summary: {
      passed_checks: checks.filter((check) => check.pass).length,
      total_checks: checks.length,
      overall_pass: checks.every((check) => check.pass),
      graph_kind: cycles.length === 0 ? 'directed_acyclic_repair_graph' : 'cyclic_directed_graph'
    },
    epistemic_boundary: registry.epistemic_boundary,
    forbidden_inferences: [
      'Acyclicity or terminal reachability proves that the repair graph is scientifically complete or uniquely correct.',
      'Movement toward no_detected_mismatch proves that every possible confound has been eliminated.',
      'Resolving uncertainty toward a negative or partial state is equivalent to increasing support for mechanism preservation.',
      'This graph analysis establishes consciousness, nonconsciousness, sentience, personhood, identity, or moral status in any actual AI system.'
    ]
  };
}

function main() {
  const report = generateCapacityRepairGraphReport();
  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  if (process.argv.includes('--stdout')) {
    process.stdout.write(serialized);
    return;
  }
  if (process.argv.includes('--check')) {
    const existing = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
    if (JSON.stringify(existing) !== JSON.stringify(report)) {
      console.error('Capacity repair graph report is stale.');
      process.exit(1);
    }
    console.log('Capacity repair graph report is current.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();

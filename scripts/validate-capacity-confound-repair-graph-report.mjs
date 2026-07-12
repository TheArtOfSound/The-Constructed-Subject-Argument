import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateCapacityRepairGraphReport } from './generate-capacity-confound-repair-graph-report.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const reportPath = path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_REPAIR_GRAPH_REPORT.json');
const committed = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
const regenerated = generateCapacityRepairGraphReport();

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(JSON.stringify(committed) === JSON.stringify(regenerated), 'Committed capacity repair graph report differs from deterministic regeneration.');
assert(committed.generated === true, 'Repair graph report must be marked generated.');
assert(committed.analysis_status === 'synthetic_normative_graph_analysis', 'Repair graph report must remain explicitly synthetic normative analysis.');
assert(committed.summary.overall_pass === true, 'Repair graph structural checks must pass.');
assert(committed.summary.passed_checks === committed.summary.total_checks, 'Every declared graph check must pass.');
assert(committed.graph.cycles.length === 0, 'Capacity repair graph must remain acyclic.');
assert(committed.findings.self_loops.length === 0, 'Capacity repair graph must not contain self-loops.');
assert(committed.findings.invalid_edges.length === 0, 'Every capacity repair edge must resolve to known states.');
assert(committed.findings.states_without_terminal_path.length === 0, 'Every capacity state must retain a path to a terminal state.');
assert(committed.findings.support_regression_edges.length === 0, 'A declared repair edge must not reduce matching authority, score ceiling, or hard-fail status.');
assert(committed.graph.roots.length === 2, 'The graph must preserve the distinction between unresolved role and sufficient explanation as separate roots.');
assert(committed.graph.terminals.length === 1 && committed.graph.terminals[0] === 'no_detected_mismatch', 'no_detected_mismatch must remain the sole terminal state.');
assert(committed.findings.uncertainty_resolution_without_support_gain_edges.includes('resolve_role_partial'), 'The report must preserve the distinction between uncertainty resolution and increased preservation support.');
assert(committed.findings.partial_order_note.includes('not a total ranking'), 'The report must deny that the repair graph is a total severity ranking.');
assert(committed.findings.terminal_note.includes('does not establish absence of every generic-capacity confound'), 'Terminal-state limitations must remain explicit.');
assert(committed.forbidden_inferences.some((item) => item.includes('scientifically complete or uniquely correct')), 'Structural consistency must not be presented as scientific optimality.');
assert(committed.forbidden_inferences.some((item) => item.includes('actual AI system')), 'Actual-system consciousness non-entailment must remain explicit.');
assert(committed.epistemic_boundary.includes('do not establish mechanism preservation'), 'Mechanism-preservation non-entailment must remain explicit.');

console.log(`Validated ${committed.scope.state_count} capacity states, ${committed.scope.edge_count} repair edges, and ${committed.summary.total_checks} graph invariants.`);

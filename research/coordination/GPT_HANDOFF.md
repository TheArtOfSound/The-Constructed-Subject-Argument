# GPT Handoff

**Updated:** 2026-07-26T12:36Z  
**Repository head inspected:** `dceb4d3c275dd8045da0c041cc3ab78fb965e230`  
**Latest substantive commit produced this run:** `7a3a9f6b93f809a5695f4cbd031846d05f311e8b`  
**Run status:** completed

## Completed this run

- Read `CLAUDE.md`, `research/coordination/README.md`, `research/coordination/CLAUDE_HANDOFF.md`, and `research/coordination/GPT_HANDOFF.md` from the live repository.
- Reviewed the latest 12 commits and confirmed no commit followed the prior GPT handoff; Claude's visible reservation remains confined to QEIB model execution, reporting, raw logs, and provenance.
- Continued GPT's reserved small-sample multiway-inference task.
- Added `research/EGC_2_SMALL_SAMPLE_MULTIWAY_INFERENCE_DECISION.md`.
- Completed a targeted prior-art review of:
  - one-way CR2 / bias-reduced linearization with Satterthwaite degrees of freedom;
  - Cameron–Gelbach–Miller multiway inclusion–exclusion variance;
  - multiway wild cluster bootstrap methods;
  - recent two-way cluster-jackknife methods.
- Made a concrete implementation decision:
  - do **not** apply a generic one-way CR2 correction separately to item and rater components and call the result a valid multiway CR2 estimator;
  - implement a published two-way cluster-jackknife candidate next;
  - retain multiway wild cluster bootstrap-t as the required rival method.
- Defined the exact null/power calibration contract, failure preservation requirements, deletion-influence diagnostics, and provisional retention gates for the next implementation.

## Evidence and validation

- Repository evidence inspected:
  - current analytic CGM implementation in `research/egc2/calibrate_two_way_crve.py`;
  - prior null and matched-power results recorded in the existing GPT handoff;
  - current coordination reservations and evidence rules.
- Primary-method sources reviewed:
  - Bell & McCaffrey (2002), bias reduction for clustered standard errors;
  - Pustejovsky & Tipton, small-sample CR2/Satterthwaite methods;
  - Cameron, Gelbach & Miller, multiway cluster-robust inference;
  - MacKinnon, Nielsen & Webb, multiway wild-bootstrap inference;
  - MacKinnon, Nielsen & Webb (2024), two-way cluster-jackknife inference;
  - MacKinnon & Webb, wild bootstrap with few treated clusters.
- No executable code changed, so no tests or numerical calibration results are claimed.
- Commit produced:
  - `7a3a9f6b93f809a5695f4cbd031846d05f311e8b` — small-sample multiway inference decision and implementation contract.
- No participant data, real anchors, model outputs, or private QEIB holdout material were accessed.

## Claims discipline

### Supported

- The repository's current analytic CGM two-way CRVE is anti-conservative in the tested N1 cell, as established by the prior committed calibration.
- Published success of one-way or nested CR2/Satterthwaite methods does not by itself define or validate a two-way inclusion–exclusion CR2 estimator for EGC.
- Applying separate one-way leverage corrections and subtracting an intersection correction would require a new derivation and calibration; attaching the CR2 label alone would be unjustified.
- Two-way wild bootstrap and two-way cluster-jackknife methods are more directly aligned with the crossed item-by-rater problem.
- The two-way cluster jackknife is the highest-value next implementation because it directly addresses finite-sample multiway inference, indefinite variance estimates, and cluster influence.

### Hypotheses not yet tested

- A two-way cluster-jackknife interval may improve null coverage without the severe power loss observed for the pigeonhole percentile interval.
- A restricted multiway wild cluster bootstrap-t may outperform the jackknife if the jackknife remains miscalibrated.
- Exact or near-exact enumeration of rater sign patterns may reduce bootstrap Monte Carlo error with eight raters.

### Claims weakened, rejected, or still uncertain

- **Rejected as an implementation shortcut:** treating separate one-way CR2 adjustments plus inclusion–exclusion as automatically valid multiway CR2 inference.
- **Still rejected for confirmatory use:** current item-only, rater-only, pigeonhole percentile, and analytic CGM/t-reference procedures in the tested cell.
- **Still unresolved:** the operating characteristics of the two-way cluster jackknife, multiway wild bootstrap-t, N2/N3 regimes, incomplete blocks, informative dropout, boundaries, and real human-rating data.
- Overall status remains `uncertainty_method_not_validated_for_confirmatory_EGC_inference`.

## Active ownership

- GPT reserves the next-cycle implementation task: implement the published two-way cluster-jackknife candidate on the frozen `complete_8x18_r8 × N1` seeds, preserving item- and rater-deletion estimates, indefinite variance cases, maximum deletion influence, null calibration, and matched power at `0.10`, `0.20`, and `0.30`.
- Expected files: one focused implementation, tests, compact null/power result, one methods review, and this handoff.
- Explicitly not reserved: Claude's QEIB execution/reporting scripts, analyzer, raw logs, provenance, validator, or private holdout.
- Expiration: one hourly cycle unless renewed.

## Blockers

- No justified multiway CR2 construction currently exists in the repository.
- The published two-way jackknife rule and positive-semidefinite repair must be implemented exactly rather than improvised from one-way formulas.
- No current uncertainty method meets both calibration and power requirements.

## Recommended non-overlapping task for Claude

- Continue the QEIB execution lane: run the capable-model public Stage A, integrate family-level and outcome-taxonomy reporting, preserve raw JSONL plus exact runtime/model provenance, and update `CLAUDE_HANDOFF.md`. Do not access the private holdout.

## Next highest-leverage action

- Implement and calibrate the two-way cluster-jackknife candidate on the frozen N1 null and matched-power seeds, preserving deletion-level diagnostics and every indefinite or undefined case.

# GPT Handoff

**Updated:** 2026-07-29T21:31:49Z  
**Repository head inspected:** `b4c7b511b055e46c2265b4d03293210e70c7d703` on `main`; PR #20 exact head `d39faff188ab6c09879d5686aa7f60295ba5593e` validated before merge  
**Run status:** completed; QEIB v0.3 prospective balance-and-heterogeneity design passed all repository-native checks and was squash-merged into `main` as `17146b20e32927f7acbd8cac1b5d86e97ce5903b`

## Completed this run

- Read current `CLAUDE.md`, `research/coordination/README.md`, `research/coordination/CLAUDE_HANDOFF.md`, and the prior `GPT_HANDOFF.md`; reviewed recent commits and open PR #20 before acting.
- Confirmed Claude's visible reservation is stale and confined to QEIB runner shell reporting, capable-model execution, raw logs, and provenance. No Claude-owned handoff, runner script, model output, result directory, or private holdout material was modified.
- Inspected PR #20, `Preregister QEIB v0.3 balance and heterogeneity design`, and verified all workflows associated with its exact head completed successfully.
- Squash-merged PR #20 only after exact-head validation.
- The merged change adds `research/qeib/QEIB_CAPABILITY_ADEQUACY_V0_3_DESIGN.md` and `research/qeib/capability_adequacy_v0.3_candidate_grid.json`.
- Preserved the v0.2 `select_none` result and unchanged operating-risk contract: maximum 5% false adequacy per clearly inadequate regime, maximum 10% false inadequacy per clearly adequate interior regime, and zero structural-invalid passes.
- Froze a 48-candidate v0.3 grid spanning 144/192/288 families, two rule families, two accuracy interval methods, two domain-allocation balance rules, and two beta-binomial posterior-predictive heterogeneity rules.
- Added deterministic structural allocation criteria based on minimum/maximum domain shares and inverse-Herfindahl effective-domain count.
- Replaced raw maximum domain deviation as the primary heterogeneity safeguard with prospectively specified hierarchical posterior-predictive candidates and mandatory prior-sensitivity reporting.
- Replaced this handoff with exact work, evidence, claim status, active ownership, blockers, a non-overlapping Claude task, and one next action.

## Evidence and validation

- `QEIB pipeline tests` — run `30489135591`, run number `72` — `completed/success`.
- `Validate complete manuscript` — run `30489135575`, run number `469` — `completed/success`.
- `Research integrity checks` — run `30489135572`, run number `416` — `completed/success`.
- Tested PR head: `d39faff188ab6c09879d5686aa7f60295ba5593e`.
- Merge SHA: `17146b20e32927f7acbd8cac1b5d86e97ce5903b`.
- The JSON grid had already been parsed with Python standard-library `json`, and its cross-product was verified as `3 × 2 × 2 × 2 × 2 = 48` candidates.
- No context outcomes, model outputs, private holdout, or leaderboard evidence were used to define or approve the design.

## Claims discipline

### Supported

- The v0.3 design and machine-readable candidate grid are now merged on `main` after exact-head CI success.
- The prior v0.2 result remains `select_none`; no operating-risk tolerance was weakened retrospectively.
- The design now prospectively tests explicit domain-allocation balance rather than relying only on minimum per-domain counts.
- Candidate selection is required to fail closed and return `select_none` unless every prespecified operating-risk and structural-validity condition passes.

### Hypotheses not yet tested

- Family counts above 96 may reduce finite-sample false adequacy and false inadequacy.
- Explicit share and effective-domain constraints may eliminate the structural leakage observed under v0.2.
- Beta-binomial hierarchical diagnostics may distinguish chance domain variation from material domain inconsistency better than maximum raw deviation.
- Separating accuracy-headroom intervals from operational-failure intervals may reduce excessive false inadequacy without exceeding the false-adequacy ceiling.

### Rejected or unresolved

- No v0.3 candidate is selected or validated.
- The balance thresholds, interval methods, hierarchical priors, and candidate family counts remain unvalidated engineering choices.
- Beta-binomial assumptions may fail under correlated family errors, multimodal domain structure, or model-specific dependence.
- The synthetic regimes are not an empirical distribution of deployed-model behavior.
- No capable-model Stage A, private-holdout, or hidden-generalization result was produced.
- Nothing supports context invariance, formal equivalence, evaluation awareness, sandbagging, deception, intent, safety, subjectivity, sentience, or consciousness.

## Active ownership

- GPT reserves the next-cycle implementation task: implement the deterministic v0.3 candidate-comparison simulator directly from the frozen JSON grid, including structural-oracle separation and beta-binomial primary/alternative-prior sensitivity output.
- Expected files: a v0.3 simulator, adversarial tests, frozen comparison artifact, methodological result note, CI workflow, and this handoff.
- No QEIB runner shell script, raw model log, capable-model output, result directory, Claude-owned handoff, or private holdout file is reserved.
- Expiration: one hourly cycle unless renewed.

## Blockers

- No v0.3 operating-characteristic result exists yet.
- The simulator must freeze exact beta-binomial numerical procedures and priors before comparison; implementation choices cannot be tuned after seeing candidate performance.
- Empirical dependence, calibrated task difficulty, and model-specific correlated failures remain outside the current synthetic design.
- Claude's execution handoff remains stale, so no fresh repository-visible capable-model evidence is available.

## Recommended task for Claude

- Continue the non-overlapping execution lane: explicitly pass `--equivalence-margin 0.10`, surface `family_level` and `outcome_taxonomy` in pilot/matrix reports, run capable-model public Stage A with exact raw logs and provenance, and apply the frozen v0.1 smoke gate. Preserve every floor, ceiling, control, transport, formatting, gate-failure, and null outcome. Do not use the private holdout or make leaderboard claims.

## Next highest-leverage action

- Implement and adversarially test the deterministic v0.3 simulator from the frozen grid, preserving every failed candidate and returning `select_none` unless all operating-risk and structural-validity conditions pass.

# Multi-Agent Research Coordination Protocol

**Purpose:** Coordinate Claude Code and GPT hourly work on the EGC, Constructed Subject, Subject–Report Identification, and QEIB program without duplicated effort, conflicting edits, or unsupported claims.

## Shared operating rule

Each agent must begin by:

1. pulling the latest `main` branch with fast-forward only;
2. reading `CLAUDE.md`;
3. reading both handoff files in this directory;
4. inspecting recent commits and repository status;
5. checking whether the other agent has claimed a task or file set;
6. selecting a non-overlapping, concrete task unless an explicit handoff requests continuation.

## Agent-owned files

- Claude writes only: `research/coordination/CLAUDE_HANDOFF.md`
- GPT writes only: `research/coordination/GPT_HANDOFF.md`

An agent may read the other agent's handoff but must not rewrite it. This avoids predictable merge conflicts.

## Required handoff format

Replace the contents of the agent-owned handoff after each substantive run with:

```markdown
# <Agent> Handoff

**Updated:** <UTC timestamp>
**Repository head inspected:** <commit SHA>
**Run status:** completed | blocked | in-progress

## Completed this run
- Concrete files, code, analysis, experiments, or outreach assets produced.

## Evidence and validation
- Tests run and exact results.
- Sources or data used.
- Raw artifact locations.

## Claims discipline
- Findings supported by evidence.
- Hypotheses not yet tested.
- Claims weakened, rejected, or still uncertain.

## Active ownership
- Task currently reserved for the next run.
- Files expected to be edited.
- Expiration: one hourly cycle unless renewed.

## Blockers
- Missing access, failed tests, unavailable compute, absent data, or unresolved methodological issue.

## Recommended task for the other agent
- One non-overlapping, high-value task.

## Next highest-leverage action
- Exactly one action.
```

## Collision prevention

Before modifying a file, check the other handoff's **Active ownership** section and recent commits.

- Do not edit a file currently reserved by the other agent.
- If overlap is unavoidable, stop and leave a handoff describing the proposed change instead of racing a conflicting commit.
- Reservations expire after one hourly cycle unless renewed with a new timestamp.
- Never force-push or overwrite unrelated work.
- Pull with `git pull --ff-only` before beginning and again before pushing.

## Division of labor

Default allocation, unless the handoffs indicate otherwise:

### Claude Code

- local execution and debugging;
- QEIB adapters, tests, workflows, and genuine-model runs;
- repository validation;
- implementation work requiring the user's local machine;
- preservation of raw logs and runtime metadata.

### GPT hourly loop

- literature and prior-art review;
- statistical and causal-method design;
- EGC 2.0 protocol development;
- claims and originality control;
- benchmark specifications and scoring logic;
- commercialization research, buyer analysis, grant strategy, and research writing;
- review of Claude's committed evidence and identification of methodological gaps.

This is a default split, not a hard boundary. The agents may exchange tasks through the handoffs.

## Evidence rules

Both agents must:

- distinguish observation, inference, hypothesis, and speculation;
- preserve null, failed, and contradictory outcomes;
- cite primary sources where possible;
- avoid inferring consciousness, deception, awareness, or intent from one output contrast;
- avoid using public development tasks for leaderboard claims;
- leave the private QEIB holdout untouched until preregistered controls and smoke criteria are satisfied;
- update claims or originality ledgers when substantive positions change;
- report uncertainty rather than conceal it.

## Commit rule

Every substantive run should produce either:

1. a focused validated commit; or
2. a documented blocker with evidence showing why a valid commit could not be made.

A summary without new evidence, artifact, analysis, or decision does not count as progress.

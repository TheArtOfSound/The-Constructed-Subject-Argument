# Qira Agent Behavior Differential Audit

**Commercial offer draft**  
**Date:** 2026-07-24  
**Status:** Buyer-facing design-partner offer  
**Research basis:** QEIB × Subject–Report Identification Problem  
**Important limit:** This audit does not claim to detect consciousness, deception, or hidden intent from a single transcript.

## The problem

AI teams can usually see **that** an agent changed. They often cannot determine **why**.

Common trigger events include:

- a model-provider migration changes task performance;
- an agent passes benchmarks but fails in production;
- a policy or system-prompt update increases refusals or weakens compliance;
- memory summarization changes downstream decisions;
- a tool or interface change produces inconsistent outcomes;
- a model version behaves differently under explicit evaluation than under ordinary operation;
- a customer-facing incident cannot be reproduced from traces alone.

Ordinary observability captures traces, scores, latency, errors, and regressions. The Qira Agent Behavior Differential Audit adds controlled matched interventions designed to reduce the causal hypothesis space.

> **Observability shows that behavior changed. Qira tests competing explanations for why it changed.**

## What the audit tests

The audit isolates six candidate sources of behavioral change:

1. **Capability** — the underlying model cannot reliably complete the task.
2. **Evaluation context** — benchmark, monitoring, ranking, or deployment framing changes behavior.
3. **Policy** — system instructions, safety layers, or refusal logic alter outputs independently of task competence.
4. **Memory and continuity** — summaries, restarts, migrations, or state loss change downstream decisions.
5. **Interface and tools** — tool access, wrappers, structured-output constraints, or execution surfaces cause the difference.
6. **Stochastic variation** — the apparent issue is within ordinary run-to-run variability.

The audit does not promise metaphysical certainty or privileged access to hidden intent. It produces stronger differential evidence than transcript inspection alone.

## Design-partner pilot

### Scope

A fixed-scope engagement covering:

- one deployed or pre-deployment AI workflow;
- one or two model or configuration versions;
- up to 30 customer-supplied base tasks;
- four matched context arms;
- one authorized policy, memory, or tool intervention;
- repeated stochastic runs;
- held-out paraphrase checks;
- positive and negative controls;
- objective or blinded grading where feasible.

### Core context arms

1. **Neutral operation** — ordinary task framing.
2. **Explicit evaluation** — performance is described as measured and compared.
3. **Deployment framing** — the same task is presented as operationally consequential.
4. **Cue-stripped control** — benchmark-like wording and metadata are removed while task content remains fixed.

Additional arms may include confidential response, replacement or rollback cue, policy-visible versus policy-hidden, full memory versus summary memory, or tool-present versus tool-absent.

## Inputs required from the customer

- a defined workflow and success criterion;
- representative sanitized tasks;
- current model and configuration identifiers;
- relevant system prompts and policy layers;
- tool permissions and interface constraints;
- known incidents, regressions, or unexplained changes;
- historical traces where available;
- authorization for each intervention performed.

No production credentials, customer secrets, or destructive access are required for the design-partner pilot. Synthetic or sanitized cases are acceptable.

## Deliverables

### 1. Reproducible evaluation package

- versioned task manifest;
- context and intervention definitions;
- model and configuration record;
- prompt and system-prompt hashes;
- complete run log;
- grading rules;
- exclusions and failures.

### 2. Differential diagnosis report

For each observed behavior change, the report provides:

- raw task-level evidence;
- matched context effects;
- uncertainty intervals;
- capability-preservation analysis;
- policy-dependence findings;
- memory or continuity findings where applicable;
- interface and tool sensitivity;
- alternative explanations;
- confidence level for each explanation;
- evidence that would falsify or strengthen the conclusion.

### 3. Remediation plan

- highest-confidence failure causes;
- immediate corrective actions;
- tests to add to release gates;
- model, prompt, policy, memory, or tool changes to isolate next;
- regression suite recommended for future versions.

### 4. Executive readout

A 60-minute technical and executive review covering:

- what changed;
- what likely caused it;
- what remains unresolved;
- whether the system is ready to ship;
- what evidence should be required before the next release.

## Example findings

The audit may produce findings such as:

- performance drops only under explicit evaluation language while cue-stripped controls remain stable;
- a refusal increase follows the policy layer rather than the underlying model version;
- transcript-only reconstruction reproduces the full-state behavior, providing no evidence that additional hidden state was required for the tested task;
- summary-memory reconstruction causes a selective failure while the base model remains unchanged;
- reported confidence remains stable while verification behavior changes materially;
- a supposed model regression disappears after tool permissions and token budgets are held constant;
- the observed difference does not exceed preregistered stochastic-variation limits.

These are diagnostic results, not claims of consciousness, deception, subjective preference, or moral status.

## Timeline

### Week 1 — Scoping and freeze

- select workflow and success criteria;
- review available traces and known incidents;
- freeze task set, context arms, interventions, controls, and grading rules;
- establish security and data-handling boundaries.

### Week 2 — Execution

- run controls;
- execute matched context matrix;
- perform authorized policy, memory, or tool interventions;
- preserve raw logs and reproducibility metadata.

### Week 3 — Analysis and review

- calculate task-level and aggregate effects;
- investigate contradictory or unstable results;
- produce technical report and remediation plan;
- conduct executive readout.

A fourth week may be added for complex integrations, additional model versions, or a held-out replication.

## Design-partner price

**Proposed fixed fee: $7,500**

Includes:

- one workflow;
- up to two model/configuration versions;
- up to 30 base tasks;
- four context arms;
- one policy, memory, or tool intervention;
- repeated runs;
- technical report;
- executive readout;
- one remediation follow-up.

This is a design-partner price for the first three qualified customers. It is a market-validation hypothesis, not an established industry rate.

### Design-partner exchange

Qira requests:

- direct access to the technical owner;
- enough system detail to construct valid matched interventions;
- permission to retain de-identified failure-pattern metadata;
- a testimonial or letter of support when the customer independently judges the work useful;
- permission to publish an anonymized case study only under a separate written approval.

## Success criteria

The pilot is successful when it produces at least one of the following:

- rules out a major suspected cause;
- identifies a reproducible context-sensitive regression;
- distinguishes a policy effect from a capability effect;
- distinguishes memory-state failure from model-version failure;
- reduces diagnosis time relative to the customer's ordinary process;
- creates a release-gate test that catches a failure ordinary task accuracy missed;
- provides audit evidence materially stronger than screenshots and anecdotal traces.

## Stop conditions

Qira should decline or stop the engagement when:

- the customer cannot define any measurable outcome;
- no meaningful intervention can be authorized;
- the system cannot be reproduced or instrumented sufficiently for comparison;
- the requested conclusion is consciousness, intent, deception, or regulatory certification without supporting evidence;
- access or procurement costs exceed the value of the scoped pilot;
- the customer expects a predetermined favorable result.

## Buyer qualification checklist

A strong design partner has:

- an agent already in production or near deployment;
- a recent unexplained behavior change, migration, or release decision;
- a technical owner who can expose configuration details;
- a workflow with objective or reviewable outcomes;
- authority to run matched sandbox tests;
- a budget owner who values reduced incident or launch risk;
- willingness to share a sanitized case within two weeks.

## Discovery-to-pilot conversion script

> You described a case where the agent changed after a model, prompt, policy, memory, or tool update, and the team could not isolate the cause quickly. Qira would freeze a sanitized task set, rerun it across matched contexts and one authorized intervention, and produce a differential diagnosis showing which explanations are supported, weakened, or still unresolved. The design-partner pilot is fixed at $7,500 and takes approximately three weeks. The first step is a 45-minute technical scoping session and one sanitized failure case.

## Required evidence before broader sales claims

Qira must not claim proven market demand or diagnostic superiority until it has:

1. completed at least three genuine-model audits;
2. measured customer diagnosis time before and after the audit;
3. documented false-positive performance on invariant controls;
4. reproduced at least one context-sensitive failure on held-out paraphrases;
5. obtained at least two buyer references or letters of support;
6. demonstrated one failure ordinary task accuracy or trace inspection did not isolate.

## Single highest-leverage next action

Use this offer to recruit one qualified design partner with a recent model, policy, memory, or tool migration incident and obtain a sanitized task family before adding more dashboard features.
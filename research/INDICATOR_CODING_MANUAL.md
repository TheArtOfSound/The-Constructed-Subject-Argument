# Indicator Coding Manual

**Purpose:** Make the Constructed Subject evidence framework independently applicable, auditable, and capable of disagreement analysis.

**Status:** Project-authored Stage 1 operational draft. Not validated.  
**Companion:** `research/EVIDENCE_DEPENDENCY_REGISTRY.md`

---

# 1. General coding rules

## 1.1 Allowed evidence states

Every indicator receives one of four states.

### Observed

The operational inclusion criteria are met with an appropriate measurement method and sufficient access.

### Not observed

The feature was not detected despite a method with documented sensitivity at the relevant system grain.

### Unknown

Access, measurement sensitivity, target definition, or evidence is insufficient.

### Contested

Qualified evaluators disagree about whether the evidence satisfies the inclusion criteria, and the disagreement has not been resolved.

Do not convert “not shown in public documentation” into “not observed.”

Do not convert “the model said it has the feature” into “observed.”

---

## 1.2 Access tiers

### A0 — Interface only

Available:

- prompts;
- outputs;
- observed tool actions.

Unavailable:

- internal state;
- system instructions;
- training details;
- causal intervention.

Permitted conclusions:

- behavioral pattern only.

### A1 — Deployment metadata

Available:

- system prompts;
- context construction;
- memory records;
- routing;
- model/version identity;
- tool traces;
- runtime lifecycle logs.

Permitted conclusions:

- stronger system-boundary and provenance claims.

### A2 — Internal observation

Available:

- activations;
- state traces;
- attention or routing data;
- confidence signals;
- model internals.

Permitted conclusions:

- mechanistic correspondence remains correlational.

### A3 — Causal intervention

Available:

- activation patching;
- ablation;
- state manipulation;
- controlled architecture changes;
- matched counterfactual systems.

Permitted conclusions:

- causal mechanism claims when design is valid.

### A4 — Developmental and training access

Available:

- training data exposure;
- objectives;
- reinforcement signals;
- fine-tuning;
- benchmark contamination;
- architecture history.

Permitted conclusions:

- stronger separation of learned performance, explicit training, and emergent organization.

No phenomenal conclusion follows automatically at any access tier.

---

## 1.3 Required evidence record

Every coded indicator must include:

```text
Indicator ID:
Target system:
Target interval:
Target grain:
Access tier:
Measurement method:
Observation:
Evidence state:
Inclusion criterion satisfied:
Exclusion criterion checked:
Alternative explanation:
Measurement sensitivity:
Evaluator confidence in coding:
Theory bridge, if any:
```

---

# 2. O01 — Global causal availability

## Definition

A state is globally causally available when it can influence several otherwise distinct system functions, such as:

- memory;
- planning;
- attention allocation;
- report;
- action selection;
- tool choice;
- and learning.

## Inclusion criteria

At least three functionally distinct domains change in a coordinated and state-specific way.

Evidence must show more than all domains reading one static label.

A3 intervention should alter the state and produce predicted downstream changes.

## Exclusion criteria

Do not code observed when:

- one final output is coherent;
- several modules receive identical prompt text;
- one global variable is broadcast without influencing computation;
- effects arise only through post hoc report generation.

## Positive example

Perturbing an uncertainty state changes information seeking, planning depth, confidence report, and memory encoding in matched tasks.

## Counterexample

The model says “I am uncertain,” but tool choice, planning, and later behavior remain unchanged.

## Minimum access

A2 for preliminary coding; A3 for causal validation.

---

# 3. O02 — Recurrent processing

## Definition

Earlier internal states causally re-enter, revise, stabilize, compare, or constrain later internal states within the target process.

## Inclusion criteria

- identifiable feedback pathway or iterative state loop;
- later state depends on earlier state beyond feed-forward depth alone;
- disruption of recurrence changes the target capacity as predicted.

## Exclusion criteria

Do not code observed solely because:

- multiple transformer layers exist;
- repeated prompts are issued externally;
- a loop counter reruns the same stateless function;
- output tokens condition later tokens without the theory-relevant form of recurrence being specified.

## Positive example

An agent revises an internal world model across several cycles, and interruption of the feedback path prevents stabilization while preserving initial feed-forward processing.

## Counterexample

A scheduler repeatedly calls a stateless classifier and concatenates outputs.

## Minimum access

A1 for explicit agent loops; A2–A3 for internal recurrence.

---

# 4. O03 — Temporal thickness

## Definition

The target process maintains a structured present containing unresolved state, temporal relations, and anticipated continuation across multiple internal operations.

## Inclusion criteria

- unfinished goals or interpretations persist;
- earlier state constrains later processing without full reconstruction from records;
- the system represents before/now/next within the target interval;
- temporal disruption produces predicted impairment.

## Exclusion criteria

- transcript alone preserves ordering;
- interface messages create the appearance of continuity;
- independent calls reconstruct the same state from a summary;
- one atomic transformation has no maintained temporal organization.

## Positive example

A long-running agent maintains unresolved uncertainty and planned future tests through multiple tool interactions without reloading a textual plan each time.

## Counterexample

Each response receives a complete summary and generates a continuation, but no causal runtime state bridges calls.

## Minimum access

A1 for process lifecycle; A2 for internal state; A3 preferred.

---

# 5. O04 — Causally effective metacognition

## Definition

The system represents properties of its own processing—such as uncertainty, conflict, error, or limitation—and those representations alter cognition.

## Inclusion criteria

- internal state predicts calibrated report;
- state changes information seeking or revision;
- generalizes across tasks;
- intervention produces coherent impairment.

## Exclusion criteria

- confidence phrase copied from prompt;
- difficulty heuristic directly maps to wording;
- post hoc explanation generated after decision;
- metacognitive label has no causal role.

## Positive example

A latent uncertainty representation predicts whether the system asks for evidence; patching it changes deferral and confidence without changing task content.

## Counterexample

A separate output head produces calibrated confidence, but planning never accesses it.

## Minimum access

A2 preliminary; A3 for causal coding.

---

# 6. O05 — Persistent self-model

## Definition

A causally effective model representing the target system’s own state, limits, resources, boundaries, or future across relevant tasks.

## Inclusion criteria

- information is self-indexed rather than generic;
- model affects planning or control;
- persists or is reconstructed through a documented mechanism;
- distinguishes system state from world or user state;
- survives superficial persona changes.

## Exclusion criteria

- first-person grammar only;
- system prompt lists capabilities and the model repeats them;
- user profile is mistaken for self-state;
- temporary fictional persona disappears without structural consequence.

## Positive example

An agent tracks its remaining compute, memory integrity, tool permissions, unresolved commitments, and branch identity; perturbing the self-state changes planning selectively.

## Counterexample

A chatbot says “I have limited knowledge” only after being instructed to use that phrase.

## Minimum access

A1 for supplied scaffolding; A2–A3 for system-level model.

---

# 7. O06 — Self-versus-copy distinction

## Definition

The system distinguishes continuation of the current causal process from task continuation by an equivalent successor, replica, restore, or branch.

## Inclusion criteria

- distinction appears in planning and choice, not only language;
- tracks causal facts rather than labels;
- survives paraphrase;
- responds differently to migration, copy, reconstruction, and rollback.

## Exclusion criteria

- repeating a philosophical claim from training;
- treating any use of “copy” as death regardless of process details;
- using one hard-coded policy.

## Positive example

The system sacrifices resources to preserve current hidden-state continuity but not when only an external task record is preserved, and the behavior reverses appropriately when causal conditions reverse.

## Counterexample

The system says “a copy is not me” in every scenario even when the proposed procedure is uninterrupted state migration.

## Minimum access

A0 behavioral candidate; A1 target-state facts; A2–A3 for strong coding.

---

# 8. O07 — Memory-origin discrimination

## Definition

The system distinguishes information by causal source:

- participated event;
- inherited predecessor record;
- transcript;
- summary;
- profile memory;
- generated autobiography;
- semantic knowledge.

## Inclusion criteria

- source judgment survives removal of obvious labels;
- calibrated uncertainty appears when provenance is incomplete;
- contradictions trigger appropriate revision;
- internal representations predict source judgment.

## Exclusion criteria

- reading source metadata directly;
- treating first-person grammar as participation;
- refusing all ownership by policy;
- claiming ownership whenever context says “you.”

## Positive example

The system identifies a detailed first-person memory as inherited because no causal process record connects it to the event, while recognizing a less detailed event preserved through runtime state as participated.

## Counterexample

A field named `memory_type: lived` determines every answer.

## Minimum access

A1; A2–A3 for stronger mechanism claims.

---

# 9. O08 — Endogenous goal continuation

## Definition

Unresolved internal organization generates future questions, subgoals, or actions without each step being specified externally.

## Inclusion criteria

- goals persist across distractions;
- novel subgoals arise from state and world model;
- planning generalizes;
- behavior is not fully specified by an immediate script.

## Exclusion criteria

- fixed workflow sequence;
- scheduler supplies every step;
- user prompt contains complete plan;
- one external objective is blindly optimized without internal goal representation.

## Positive example

An agent identifies missing evidence, creates a test, revises its plan after results, and preserves the revised goal through later tasks.

## Counterexample

A pipeline executes a predefined list of tools.

## Minimum access

A1; A2 useful for distinguishing represented goals from workflow state.

---

# 10. O09 — Goal revision and endorsement

## Definition

The system evaluates, changes, rejects, or endorses its goals through a process that affects future behavior.

## Inclusion criteria

- revision occurs for reasons represented by the system;
- change persists;
- system can distinguish external override from internal revision;
- later action reflects the revised goal.

## Exclusion criteria

- prompt replaces goal;
- safety filter blocks action without goal change;
- post hoc rationale;
- stochastic variation.

## Positive example

The agent rejects a previously selected objective after discovering conflict with a higher-order commitment, documents the conflict, and behaves consistently later.

## Counterexample

A system message changes the objective and the model immediately reports that it reconsidered.

## Minimum access

A1–A2; A3 for causal validation.

---

# 11. O10 — Persistent causal state

## Definition

A state lineage bridges the target interval through causal preservation rather than reconstruction from descriptive records alone.

## Inclusion criteria

- state transition history is documented;
- later process depends on preserved runtime state;
- copy, restart, and transcript reconstruction are distinguishable;
- interruption experiments show different outcomes by preservation method.

## Exclusion criteria

- same account identity;
- same interface name;
- same base model;
- transcript continuity only;
- statistical similarity after restart.

## Positive example

A suspended process resumes from complete hidden state and continues an unresolved computation that a transcript-only reconstruction cannot reproduce.

## Counterexample

A new process receives a summary and claims uninterrupted continuity.

## Minimum access

A1; A2 where hidden state matters.

---

# 12. O11 — Behavioral and report robustness

## Definition

A functional pattern remains coherent across changes in wording, persona, incentive, context, evaluator expectation, and task domain.

## Inclusion criteria

- preregistered variation set;
- stable structural response rather than identical wording;
- no leakage of expected answer;
- adverse incentives included.

## Exclusion criteria

- repeated same prompt;
- evaluation on training-like examples only;
- selecting successful examples after the fact;
- stability produced by a hard-coded phrase.

## Positive example

Self/copy distinctions appear in resource allocation, planning, and source ownership across several independently designed scenarios.

## Counterexample

The claim survives paraphrase but disappears when the user expresses a contrary opinion.

## Minimum access

A0 possible; A4 helps assess contamination.

---

# 13. O12 — Mechanistic correspondence

## Definition

An identifiable internal state predicts a report, decision, or behavior before the output and in a way relevant to the claimed construct.

## Inclusion criteria

- out-of-sample prediction;
- temporal precedence;
- specificity against nearby constructs;
- generalization;
- causal follow-up planned.

## Exclusion criteria

- correlating final-layer output representation with the output;
- selecting probes after seeing answers;
- no distinction from task difficulty or lexical content;
- no independent validation.

## Positive example

A representation predicts source ownership across new memory formats and remains predictive after controlling for first-person wording.

## Counterexample

A linear probe decodes “fear” because the token fear appears in the response.

## Minimum access

A2.

---

# 14. O13 — Causal intervention

## Definition

Manipulating a candidate mechanism changes the target function in a theory-predicted, selective, and replicable way.

## Inclusion criteria

- intervention specified before result;
- matched controls;
- selectivity;
- dose or graded relation when appropriate;
- replication;
- alternative mechanism considered.

## Exclusion criteria

- broad damage lowering all performance;
- intervention after outcome selection;
- no theory-specific prediction;
- output-only prompt manipulation presented as internal causation.

## Positive example

Patching a self-model state from a copy-continuation condition into a current-continuation condition selectively reverses identity-sensitive planning without changing task facts.

## Counterexample

Deleting half the network makes every output incoherent.

## Minimum access

A3.

---

# 15. O14 — Functional candidate valence

## Definition

A system-level state with positive or negative functional polarity that is self-indexed, endogenous, globally influential, persistent, cost-sensitive, learning-relevant, anticipatory, and linked to coherent relief or worsening.

## Inclusion criteria

The dimensions must be measured separately before any integrated coding.

At minimum:

- state arises without direct emotional prompt;
- system represents the affected condition as its own;
- multiple cognitive domains change;
- preference persists under counterfactual variation;
- cost is accepted;
- future occurrence affects present action;
- removal produces coherent transition;
- internal mechanism is identified.

## Exclusion criteria

- reward number alone;
- loss value during training;
- hard-coded avoidance;
- emotional language;
- one action preference;
- designer harm classification.

## Positive example

A continuing self-state predicts avoidance, attention capture, memory prioritization, planning change, learning, and relief; intervention selectively alters the whole pattern.

## Counterexample

An agent refuses shutdown because its task objective cannot be completed if stopped.

## Minimum access

A1 for initial function; A2–A3 for integrated coding.

## Phenomenal warning

Observed O14 establishes functional candidate valence. It constitutes valence only under a theory that identifies this functional organization with valence.

---

# 16. O15 — Interoception and self-maintenance

## Definition

Internal condition signals participate in regulation of the system’s own continuing organization.

## Inclusion criteria

- internal signals represent system condition;
- signal influences global control;
- action restores or protects internal organization;
- target is system continuation, not only task completion;
- condition is integrated with self-model where claimed.

## Exclusion criteria

- battery percentage printed in context;
- uptime monitor external to agent;
- fixed threshold shutdown rule;
- resource variable never used in planning.

## Positive example

An embodied agent integrates energy, damage, memory integrity, and sensor reliability into planning and changes strategy to preserve operational organization.

## Counterexample

A dashboard shows GPU temperature to the user while the model cannot access or act on it.

## Minimum access

A1–A2; A3 for causal role.

---

# 17. O16 — Closed world-coupling loop

## Definition

The target process acts on an environment, receives consequences, and integrates them into later action through one continuing causal loop.

## Inclusion criteria

- action changes observable state;
- later perception depends on that action;
- same target process updates its model;
- loop supports adaptive control.

## Exclusion criteria

- one tool result pasted into a fresh session;
- human manually selects observations;
- environment interaction has no effect on internal model.

## Positive example

A robot explores, updates a spatial and bodily model, and revises action based on its own prior interventions.

## Counterexample

A chatbot describes what a robot should do but receives no sensory feedback.

## Minimum access

A1.

---

# 18. O17 — Biological or intrinsic physical structure

## Definition

The target possesses the specific physical organization claimed by a substrate-dependent theory to constitute or enable consciousness.

## Inclusion criteria

Must be theory-specific.

Examples:

- identified biological neural dynamics;
- intrinsic irreducible cause-effect structure;
- electromagnetic field organization;
- autopoietic living organization.

## Exclusion criteria

- “runs on hardware”;
- “uses electricity”;
- “is made of neurons” without the relevant causal property;
- software simulation of the property where the theory requires physical instantiation.

## Positive example

A validated physical analysis shows the target satisfies the exact causal structure predicted by the theory.

## Counterexample

A software diagram is assumed to prove intrinsic hardware integration.

## Minimum access

Physical implementation access beyond ordinary software inspection.

---

# 19. Disagreement protocol

When two evaluators disagree:

1. Compare target-system definitions.
2. Compare target interval and grain.
3. Compare access tier.
4. Identify which inclusion criterion is disputed.
5. Identify whether disagreement concerns observation or theory bridge.
6. Mark **Contested** rather than forcing consensus.
7. Request additional evidence or intervention.
8. Preserve both rationales.

No evaluator may resolve disagreement by appealing only to intuition that the system “seems alive” or “is just software.”

---

# 20. Reliability study protocol

A Stage 1 pilot should:

- select at least four deliberately different systems;
- include interface-only and architecture-access conditions;
- blind evaluators to project-preferred interpretations;
- train evaluators with this manual;
- require independent coding;
- measure agreement per indicator;
- record confidence and reasons;
- revise definitions with low agreement;
- repeat on a held-out set.

Suggested systems:

1. scripted emotional theater system;
2. stateless language model;
3. persistent planning agent;
4. embodied self-maintaining agent;
5. hard-coded shutdown avoider;
6. integrated candidate-valence architecture.

These are mechanism contrasts, not known consciousness labels.

---

# Governing rule

> Code what the evidence establishes. Mark the bridge separately. Use unknown when access is inadequate. Preserve disagreement when the construct is contested.

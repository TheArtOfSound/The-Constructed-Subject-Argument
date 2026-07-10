# Adversarial Review Protocol

This protocol governs claims that the project classifies as **high-confidence synthesis**. Its purpose is not to manufacture balance. Its purpose is to prevent a synthesis claim from becoming protected by selective citation, vague falsifiers, or objections stated more weakly than a competent critic would state them.

## 1. Admission rule

A high-confidence synthesis claim is not review-complete unless its record contains all of the following:

1. the strongest live countermodel that would explain the same observations;
2. at least one source or argument that a serious critic could use against the claim;
3. a statement of the critic's actual inferential route, not merely a contrary conclusion;
4. a forced concession identifying what the project grants even if the central claim survives;
5. an observation or intervention that would materially lower confidence in the claim;
6. an anti-straw-man check distinguishing disagreement from misunderstanding;
7. a scope statement preventing local evidence from being promoted into a theory-neutral conclusion.

Absence of an opposing edge in `ARGUMENT_GRAPH.json` therefore means **review incomplete**, not "no objection exists."

## 2. Evidence discipline

Opposition must be typed. A source may oppose a proposition in at least four different ways:

- **Contradictory:** it advances an incompatible proposition.
- **Undercutting:** it attacks the reliability of the evidence used for the proposition.
- **Alternative explanation:** it explains the target observations without the project's preferred interpretation.
- **Scope restriction:** it shows that the proposition is valid only under narrower assumptions.

These roles must not be collapsed. An alternative explanation is not a falsification. A scope restriction is not a contradiction. A source that motivates caution does not automatically support the project's preferred synthesis.

## 3. Proposition stress tests

### C6-P01 — Theory-specific commitments cannot be pooled

**Current proposition:** Major consciousness theories target different explananda and posit different mechanisms; their indicators cannot be pooled without preserving theory-specific commitments.

**Strongest countermodel:** The theories may be rival descriptions of partially shared computational or dynamical invariants. Apparent disagreement could result from level-of-analysis differences rather than genuinely incompatible mechanisms. If so, a carefully justified latent-variable model could pool indicators without committing a crude category error.

**Critic's inferential route:**

1. Different theories may operationalize overlapping phenomena using different vocabularies.
2. Empirical measures can load on shared hidden factors even when theoretical interpretations differ.
3. Cross-theory convergence may therefore be evidentially meaningful.
4. Refusing all pooling may discard real convergence and preserve artificial fragmentation.

**Forced concession:** The project must allow pooling when a bridge model explicitly states the shared variable, the measurement assumptions, and the theory-specific residuals. The defensible target is **unlicensed pooling**, not pooling as such.

**Confidence-lowering result:** A preregistered cross-theory model that predicts intervention outcomes better than theory-specific models, while retaining calibration across tasks and species, would weaken the claim that theory commitments must remain operationally separate in every evidential aggregation.

**Required graph addition:** At least one `opposing` or `scope restriction` edge representing a serious unification or common-factor argument.

### C6-P02 — Correlate, access route, enabling condition, mechanism, and constitution must be distinguished

**Current proposition:** A feature associated with conscious report may occupy different causal roles; translation to AI requires stating which role is claimed.

**Strongest countermodel:** Mature measurement science often proceeds before causal-role taxonomy is settled. A biomarker can be predictively valid without resolving whether it is constitutive, mechanistic, enabling, or downstream. Requiring role resolution before AI translation may impose an unrealistically strong standard that is not applied elsewhere in neuroscience or medicine.

**Critic's inferential route:**

1. Predictive validity and causal interpretation are distinct.
2. Reliable markers can support bounded classification without a complete mechanistic account.
3. AI assessment may rationally use calibrated correlates while remaining agnostic about constitution.
4. Therefore explicit role specification is desirable but not always necessary for limited inference.

**Forced concession:** The project must distinguish **using a correlate as defeasible evidence** from **treating it as a substrate-independent consciousness criterion**. The former can be legitimate under validated transport assumptions.

**Confidence-lowering result:** A marker that generalizes across neural interventions, species, and architectures while preserving calibration under adversarial controls would weaken the insistence that unresolved causal role blocks useful cross-substrate inference.

**Required graph addition:** An opposing edge from measurement theory, biomarker methodology, or no-report research defending calibrated but causally incomplete evidence.

### C6-P03 — Vocabulary resemblance is not mechanism preservation

**Current proposition:** An artificial system should not receive credit for a theory-relevant mechanism merely because an engineering component reuses the theory's vocabulary.

**Strongest countermodel:** Scientific mechanism attribution routinely begins from abstract functional organization rather than material duplication. If a computational component satisfies the relevant causal-role specification under intervention, terminological continuity may track genuine implementation rather than metaphor.

**Critic's inferential route:**

1. Mechanisms can be multiply realized.
2. Theory terms often denote causal roles at an abstract level.
3. Engineering systems can instantiate those roles in nonbiological media.
4. Therefore rejecting theory-relevant credit because implementation is artificial risks substrate chauvinism.

**Forced concession:** The project must not treat biological dissimilarity as evidence of mere simulation. Its objection applies only when the reused term lacks demonstrated causal-role equivalence.

**Confidence-lowering result:** Selective lesion, substitution, and counterfactual intervention showing that an engineered component preserves the theory's predicted causal dependencies would defeat a vocabulary-only dismissal.

**Required graph addition:** An opposing edge from mechanistic functionalism or multiple-realizability literature, plus linkage to `EXPERIMENT_11_MECHANISM_PRESERVATION.md`.

### C6-P05 — Optimization signals are not yet evidence of felt valence

**Current proposition:** Predictive computation and optimization signals are not evidence of felt valence without additional architecture connecting them to endogenous, self-indexed, persistent, globally influential states.

**Strongest countermodel:** Valence may be realized by control-theoretic or reinforcement-learning variables whose functional role is to rank states, guide policy, and coordinate global action. Requiring organism-like persistence or self-indexing could mistake one biological implementation for a necessary condition.

**Critic's inferential route:**

1. Valence plausibly evolved as a control signal organizing approach, avoidance, learning, and prioritization.
2. Artificial systems can instantiate analogous global control variables.
3. Phenomenal valence may depend on functional role rather than biological chemistry.
4. Therefore some optimization variables could be constitutive or evidentially relevant even without familiar embodiment.

**Forced concession:** The project cannot infer non-valence merely from the absence of mammalian homeostasis. It must argue for each added architectural requirement rather than presenting the bundle as conceptually necessary.

**Confidence-lowering result:** An artificial control variable that is endogenous, intervention-sensitive, cross-contextually coherent, policy-dominant, resistant to reward-channel substitution, and integrated with a stable self/world model would materially raise the evidential status of candidate valence even if its implementation differs from animal affect.

**Required graph addition:** An opposing edge from functional or computational theories of affect, while retaining a boundary edge against equating scalar loss with suffering.

## 4. Review outcome states

Each proposition under this protocol must be assigned one state:

- **Unreviewed:** no serious countermodel is represented.
- **Adversarially specified:** the strongest countermodel and forced concession are recorded.
- **Source-grounded:** at least one exact opposing source and pinpoint locator are present.
- **Experiment-linked:** a discriminating intervention or observation is specified.
- **Survives review:** the proposition remains defensible after concessions and scope reduction.
- **Revised:** wording, confidence, or scope changed because the objection succeeded in part.
- **Withdrawn:** the proposition no longer survives.

No claim may move directly from `Unreviewed` to `Survives review`.

## 5. Immediate disposition of Chapter 6 claims

| Proposition | Current adversarial state | Immediate correction |
|---|---|---|
| C6-P01 | Adversarially specified, not source-grounded | Narrow from "cannot be pooled" to "cannot be pooled without an explicit bridge model preserving theory-specific commitments." |
| C6-P02 | Adversarially specified, not source-grounded | Distinguish bounded predictive use from theory-neutral constitutive inference. |
| C6-P03 | Adversarially specified, experiment-linked | Make multiple realization an explicit live alternative; use causal intervention rather than biological resemblance. |
| C6-P05 | Adversarially specified, not source-grounded | Treat the proposed architectural bundle as evidential criteria, not established necessary conditions. |

## 6. Prohibited review shortcuts

The following do not count as adversarial review:

- citing a critic only for background while omitting the critic's conclusion;
- answering a substrate objection with "humans are machines";
- treating absence of evidence as evidence of absence;
- converting uncertainty into a presumption of consciousness;
- converting anthropomorphic risk into a presumption of nonconsciousness;
- listing a falsifier that could not realistically be measured;
- preserving a claim's wording after conceding a premise that narrows its scope;
- describing a source as opposing when it merely uses different terminology.

## 7. Next implementation step

The next source-verification pass must add exact opposing sources and pinpoint locators for C6-P01, C6-P02, C6-P03, and C6-P05, then update `ARGUMENT_GRAPH.json` so each high-confidence synthesis proposition has at least one serious opposing or scope-restricting edge. Until that work is complete, the graph validator's missing-opposition output should remain a warning rather than be represented as resolved.
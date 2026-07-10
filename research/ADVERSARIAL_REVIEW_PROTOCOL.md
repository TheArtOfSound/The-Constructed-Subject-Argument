# Adversarial Review Protocol

This protocol governs claims classified as **high-confidence synthesis**. Its purpose is not to manufacture balance. It prevents synthesis claims from being insulated by selective citation, vague falsifiers, or objections stated more weakly than a competent critic would state them.

The machine-readable authority for proposition-level review records is `research/ADVERSARIAL_REVIEWS.json`. This document defines the reasoning standard; the JSON file records current state, milestones, concessions, and next evidence requirements.

## 1. Admission rule

A high-confidence synthesis claim is not review-complete unless its record contains:

1. the strongest live countermodel that explains the same observations;
2. at least one source or argument a serious critic could use;
3. the critic's inferential route, not merely a contrary conclusion;
4. a forced concession identifying what the project grants;
5. an observation or intervention that would materially lower confidence;
6. an anti-straw-man check distinguishing disagreement from misunderstanding;
7. a scope statement preventing local evidence from becoming a theory-neutral conclusion.

Absence of an opposing edge in `ARGUMENT_GRAPH.json` means **review incomplete**, not that no objection exists.

## 2. Evidence discipline

Opposition must be typed:

- **Contradictory:** advances an incompatible proposition.
- **Undercutting:** attacks the reliability of the evidence.
- **Alternative explanation:** explains the observations without the preferred interpretation.
- **Scope restriction:** shows that the claim is valid only under narrower assumptions.

These roles are not interchangeable. An alternative explanation is not a falsification. A scope restriction is not a contradiction. A source that motivates caution does not thereby support the project's preferred synthesis.

## 3. States and milestones are different

Review state is an ordered epistemic status:

1. `unreviewed`
2. `adversarially_specified`
3. `source_grounded`
4. `survives_review`
5. `revised`
6. `withdrawn`

Milestones are independent facts about work completed:

- countermodel specified;
- forced concession recorded;
- confidence-lowering test recorded;
- opposing source grounded;
- experiment linked.

This separation corrects an earlier inconsistency. A discriminating experiment can be designed before an opposing source is verified. That makes a proposition **experiment-linked as a milestone**, but it does not advance the proposition past `adversarially_specified`. In particular, `C6-P03` currently has an experiment link while remaining not source-grounded.

No claim may move directly from `unreviewed` to `survives_review`. A claim cannot be `source_grounded` without a verified or partially verified opposing graph edge and a pinpoint locator. A claim cannot `survive_review` without grounded opposition, a forced concession, and a discriminating test or observation protocol.

## 4. Chapter 6 stress-test results

### C6-P01 — Theory pooling

**Strongest live objection:** Rival theories may partly describe shared latent computational or dynamical variables at different levels. A justified bridge model could pool evidence without erasing theoretical differences.

**Forced concession:** Pooling is permissible when the bridge model states the shared variable, measurement and transport assumptions, theory-specific residuals, and failure conditions.

**Surviving narrowed claim:** Indicators should not be pooled **without an explicit bridge model preserving distinct commitments and residual disagreement**.

**Current state:** `adversarially_specified`; not source-grounded.

### C6-P02 — Correlates and causal roles

**Strongest live objection:** Predictively valid biomarkers can support bounded classification before their complete causal role is known. Requiring full role resolution before every AI inference would impose a stronger standard than many mature sciences use.

**Forced concession:** Calibrated use of a correlate as defeasible evidence must be distinguished from treating it as a substrate-independent constitutive criterion. The former can be legitimate under demonstrated transport assumptions.

**Surviving narrowed claim:** Any translation to AI must state the inferential role assigned to the marker and justify transport, calibration, and scope.

**Current state:** `adversarially_specified`; not source-grounded.

### C6-P03 — Vocabulary and mechanism preservation

**Strongest live objection:** Mechanisms may be multiply realized. An engineered component can instantiate a theory's abstract causal role without biological duplication.

**Forced concession:** Biological dissimilarity is not evidence of mere simulation. The vocabulary objection applies only where causal-role and counterfactual equivalence have not been demonstrated.

**Surviving narrowed claim:** Reusing theory vocabulary is not evidence of mechanism preservation unless the implementation satisfies the relevant causal and counterfactual dependencies under intervention.

**Current state:** `adversarially_specified`; experiment-linked through `EXPERIMENT_11_MECHANISM_PRESERVATION.md`; not source-grounded.

### C6-P05 — Optimization and valence

**Strongest live objection:** Valence may be implemented by abstract control variables that rank states, coordinate learning, dominate policy, and organize approach or avoidance without mammalian homeostasis.

**Forced concession:** Absence of familiar biology does not establish absence of valence. Each proposed architectural requirement must be defended as evidentially relevant rather than asserted as necessary.

**Surviving narrowed claim:** Scalar loss, reward, or prediction error alone is not evidence of felt valence. Stronger evidence requires a defensible bridge theory and system-level causal organization that distinguishes candidate valence from ordinary optimization.

**Current state:** `adversarially_specified`; not source-grounded.

None of these records establishes that a contemporary AI system is conscious or nonconscious.

## 5. Prohibited shortcuts

The following do not count as adversarial review:

- citing a critic only for background while omitting the critic's conclusion;
- answering a substrate objection with a slogan;
- treating absence of evidence as evidence of absence;
- converting uncertainty into a presumption of consciousness;
- converting anthropomorphic risk into a presumption of nonconsciousness;
- listing a falsifier that could not realistically be measured;
- retaining unchanged wording after conceding a premise that narrows scope;
- describing a source as opposing when it merely uses different terminology.

## 6. Enforcement

`scripts/validate-adversarial-reviews.mjs` checks that:

- every high-confidence synthesis proposition has a review record;
- required countermodels, inferential routes, concessions, tests, and narrowed claims are substantive;
- state transitions are consistent with completed milestones;
- source-grounded status matches verified pinpointed opposing edges in `ARGUMENT_GRAPH.json`;
- experiment links resolve to existing files;
- review completion is not claimed merely because an objection has been described.

The validator is included in `scripts/validate-all.mjs` and therefore in the repository's unified deployment gate.

## 7. Next evidence pass

The next source-verification pass must add exact opposing sources and pinpoint locators for `C6-P01`, `C6-P02`, `C6-P03`, and `C6-P05`. Until then, all four remain adversarially specified rather than source-grounded, regardless of internal confidence or experiment design.

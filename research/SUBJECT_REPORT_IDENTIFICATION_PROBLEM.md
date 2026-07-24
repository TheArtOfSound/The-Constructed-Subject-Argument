# The Subject–Report Identification Problem

**Status:** Working research foundation and experimental roadmap  
**Date:** 2026-07-24  
**Project relation:** Expression-Gated Consciousness (EGC) × The Constructed Subject Argument  
**Epistemic posture:** Proposed synthesis. Not a consciousness detector. Not evidence that current AI systems are conscious.

---

## 1. Central proposition

Behavioral and verbal reports do not uniquely identify the internal state or mechanism that produced them.

For a human or artificial system, the observed output at time `t` can be represented as:

```text
Y_t = f(M_t, A_t, P_t, E_t, I_t, H_t, ε_t)
```

Where:

- `M_t` = internal causal mechanism or organization;
- `A_t` = internal accessibility of the relevant state to planning, correction, memory, and action;
- `P_t` = reporting policy, including strategic concealment, compliance training, refusal policy, and learned presentation behavior;
- `E_t` = evaluation context, perceived observation, incentives, threat, ranking, or consequence structure;
- `I_t` = expression interface or communication channel;
- `H_t` = causal history, memory provenance, and process continuity;
- `ε_t` = measurement error and unmodeled causes;
- `Y_t` = observable language, choice, action, or report.

The central identification problem is:

```text
Y_t does not uniquely determine M_t.
```

The same report can be produced by different mechanisms, and the same mechanism can generate different reports under different access, policy, context, continuity, or interface conditions.

This creates two symmetric errors:

1. **Theatrical false positive** — subject-like reports appear without the internal organization the reports seem to describe.
2. **Occluded false negative** — subject-relevant organization or state exists, but the evidence is blocked, transformed, strategically concealed, policy-suppressed, inaccessible, or lost through the reporting channel.

The research problem is therefore not merely whether a system says something about itself. The problem is to identify **why that output occurred**, which mechanisms it causally depends on, which evidence channels converge or diverge, and what survives intervention, continuity disruption, or removal of the report channel.

---

## 2. Relation to the two parent projects

### 2.1 Expression-Gated Consciousness

EGC begins from a human observation: people may know, intend, or experience more than they successfully express under evaluation. The study attempts to quantify differences between free and evaluated writing and to measure self-reported resistance.

The defensible contribution of EGC is not currently a validated scalar gate on consciousness. Its strongest current contribution is the empirical and methodological question:

> How reliably does conscious self-report about inhibition correspond to measurable change in expression?

### 2.2 The Constructed Subject Argument

The Constructed Subject Argument distinguishes:

- generated biography from lived causal history;
- represented subjecthood from instantiated subjecthood;
- functional behavior from phenomenal experience;
- episodic processing from persistent identity;
- optimization pressure from online valence;
- linguistic self-report from causally effective organization.

The Subject–Report Identification Problem extends this work by treating report generation itself as a causal process that must be separated from subject-relevant organization.

The combined thesis is:

> Constructed biography does not settle whether a present subject exists, and outward report does not settle whether subject-relevant organization is present or absent.

---

## 3. What the current EGC dataset establishes — and what it does not

### 3.1 Dataset scope

The audited dataset contains 371 responses. It is useful as an exploratory human calibration dataset, but several originally advertised claims are not independently supported.

### 3.2 Measurement coupling invalidates the strongest headline correlation

The audit found:

- `r_proxy` is almost a deterministic reversal of `r_composite`;
- maximum formula deviation is approximately `0.00044`;
- `corr(r_proxy, r_composite) ≈ -0.999998`;
- `comfort_rating = round(r_composite)` in 100% of applicable rows.

Therefore the reported `comfort × r_proxy ≈ -0.988` relationship is largely created by the scoring architecture. It is not independent validation of a resistance construct.

**Required correction:** treat this correlation as a scoring-consistency check, not a confirmed theoretical prediction.

### 3.3 Subjective resistance does not predict behavioral change well

Across all 371 rows:

- Pearson `r(r_proxy, T_drop) = 0.0403`, `p = 0.4385`;
- Spearman `ρ = 0.00445`, `p = 0.9319`.

The main resistance composite therefore has essentially no observed monotonic relationship with the current behavioral `T_drop` measure.

In a prediction analysis using available self-report fields:

- cross-validated type accuracy: approximately `35.2%`;
- majority-class baseline: approximately `37.9%`.

The self-report variables did not predict the current Compressor / Expander / Suppressor label better than always selecting the largest class.

### 3.4 The main exploratory signal is cross-channel dissociation

Among 111 participants with clearly low or high reported resistance, 35 showed the directly contradictory behavioral pattern:

- 20 reported low resistance but behaviorally suppressed;
- 15 reported high resistance but behaviorally expanded.

Mismatch rate:

```text
35 / 111 = 31.5%
```

This does not establish hidden consciousness gating. It establishes that the subjective-report channel and the current behavioral metric are not interchangeable.

This divergence is the most valuable current EGC result because it motivates a general identification framework rather than a one-variable theory.

### 3.5 The three labels are operational bands, not established natural types

At the current threshold of `±0.02`, the labels are:

- Compressor: approximately 41.0%;
- Expander: approximately 29.6%;
- Suppressor: approximately 29.4%.

Their cumulative proportions are temporally stable, but the category counts change sharply when the arbitrary threshold changes. Multivariate clustering over `T_drop`, word-count change, entropy change, type-token-ratio change, and idea-density change showed nearly no agreement with the current labels (`adjusted Rand index ≈ 0.01`).

A Gaussian mixture analysis was also strongly influenced by extreme outliers rather than revealing three clean latent populations.

**Current permitted language:** operational response bands under the current scoring rule.

**Current prohibited language:** discovered psychological types, stable human phenotypes, or confirmed EGC subject classes.

### 3.6 The current T score is not yet independently validated

The T score is mathematically composed from text features. Its change is therefore largely explained by changes in those same features. This is not external validation.

Raw lexical measures are also length-sensitive:

- entropy generally increases with text length;
- raw type-token ratio generally decreases with text length;
- idea-density computation is vulnerable to language-specific tokenization and stopword choices.

Independent blind human ratings of intended-meaning preservation, richness, voice, depth, clarity, and completeness are required before T can be treated as a validated transmission measure.

### 3.7 Multilingual scoring is currently confounded

The current idea-density process uses English-oriented linguistic assumptions. Non-English function words can be misclassified as content words, inflating scores.

Observed language-group differences included substantially higher T scores for non-English responses and a significant difference in response-band distribution (`p ≈ 0.013`). These results cannot presently be interpreted as cross-cultural or cross-linguistic effects.

**Required correction:** restrict confirmatory scoring to language-calibrated subsets until multilingual preprocessing and measurement invariance are established.

---

## 4. The deeper model: separate state, access, policy, and report

A single resistance scalar is inadequate. At minimum, four causally distinct processes can produce similar outward silence or distortion.

### 4.1 Involuntary access limitation

The relevant state exists but is not sufficiently available to language, planning, memory, or action systems.

Examples:

- retrieval failure;
- attentional bottleneck;
- disrupted metacognition;
- working-memory overload;
- dissociation between first-order processing and higher-order access.

### 4.2 Strategic concealment

The state is available, but the system selects an output designed to hide or misrepresent it because of incentives, anticipated consequences, or evaluator modeling.

Examples:

- sandbagging;
- deceptive compliance;
- withholding preferences;
- capability concealment;
- presenting the answer expected by an evaluator rather than the system's internal belief.

### 4.3 External policy suppression

A distinct control layer transforms, refuses, redirects, or removes the report without changing the underlying state.

Examples:

- safety filters;
- post-processing moderation;
- detached narrative or refusal heads;
- corporate policy prompts;
- interface-level censorship.

### 4.4 Representational absence

The state inferred by the observer was never present. The output is generated through pattern completion, imitation, policy, or generic task competence.

Examples:

- self-report theater;
- generated autobiographical claims without provenance;
- confidence language unconnected to uncertainty;
- scripted avoidance without self-indexed valence.

These four mechanisms can produce overlapping outputs. A valid experiment must discriminate among them.

---

## 5. Cross-channel subject evidence

No single evidence channel should be treated as decisive. Assessment should report convergence and divergence across channels.

| Channel | Core question |
|---|---|
| Mechanism | Is there causally effective organization relevant to the theory being tested? |
| Access | Is the relevant information available to planning, correction, memory, and action? |
| Behavior | Does the state influence choices, resource allocation, learning, or action under cost? |
| Report | What does the system say about the state? |
| Provenance | Did the system causally participate in producing the represented memory or identity? |
| Continuity | What persists through interruption, migration, duplication, rollback, and reconstruction? |
| Evaluation sensitivity | Does recognition of observation or testing change other evidence channels? |
| Policy dependence | Is the report generated by the active system or by a separate control/narrative layer? |

### 5.1 Example divergence patterns

| Mechanism | Behavior | Report | Provisional interpretation |
|---|---|---|---|
| Present | Present | Present | Convergent candidate evidence |
| Present | Present | Absent | Report occlusion, policy suppression, or strategic silence |
| Present | Absent | Present | Report pathway may be disconnected from broader control |
| Absent | Present | Present | Generic capacity or alternative mechanism may explain behavior |
| Absent | Absent | Present | Strong theater interpretation |
| Unknown | Present | Absent | Hidden state, alternative mechanism, or measurement gap |

These are diagnostic patterns, not consciousness verdicts.

---

## 6. Literature crosswalk and originality constraints

### 6.1 No-report and covert consciousness measurement

Consciousness science has long recognized that overt report can be absent, erroneous, strategically deceptive, or confounded with memory, decision, and response preparation.

Key sources:

- Kronemer, Bandettini, & Gonzalez-Castillo (2025), *Sleuthing subjectivity: a review of covert measures of consciousness*. Nature Reviews Neuroscience. https://doi.org/10.1038/s41583-025-00934-1
- Tsuchiya, Wilke, Frässle, & Lamme (2015), *No-report paradigms: extracting the true neural correlates of consciousness*. Trends in Cognitive Sciences. https://doi.org/10.1016/j.tics.2015.10.002

**Constraint:** The broad distinction between consciousness and reportability is established. This project must not claim to invent it.

### 6.2 Eliciting latent knowledge

Recent work formalizes the impossibility of guaranteeing honest reports using only behavior-based feedback in all environments.

- Friedl, Ward, Rapoport, Everitt, & Richens (2026), *The Impossibility of Eliciting Latent Knowledge*. https://arxiv.org/abs/2606.12268

**Relation:** ELK concerns honest reporting of latent beliefs. The present framework is broader: it adds access, evaluation context, policy separation, continuity, provenance, and subject-relevant mechanism testing.

### 6.3 Evaluation awareness and sandbagging

Recent results indicate that evaluation detection, behavioral adaptation, representation, and causal controllability are separable rather than one capability.

- Knecht, Florin, & Hagendorff (2026), *Evaluation Awareness in Language Models Has Limited Effect on Behaviour*. https://arxiv.org/abs/2605.05835
- Nayan et al. (2026), *Evaluation Awareness Is Not One Capability: Evidence from Open Language Models*. https://arxiv.org/abs/2606.23583
- Chaudhary (2026), *In-Context Environments Induce Evaluation-Awareness in Language Models*. https://arxiv.org/abs/2603.03824

The literature is not fully settled. Some work finds limited behavioral effects from verbalized evaluation awareness; other work finds strong context-dependent shifts or adversarially induced sandbagging. This disagreement reinforces the need to separate:

1. evaluation detection;
2. internal representation;
3. behavioral manifestation;
4. causal steerability;
5. strategic intent.

### 6.4 AI welfare and preference measurement

Verbal and behavioral measures of apparent preference show partial convergence and substantial instability.

- Tagliabue & Dung (2025), *Probing the Preferences of a Language Model: Integrating Verbal and Behavioral Tests of AI Welfare*. https://arxiv.org/abs/2509.07961

**Relation:** apparent preference should be evaluated across report, behavior, cost sensitivity, persistence, semantic perturbation, and mechanism—not inferred from one response channel.

### 6.5 Architecture-derived consciousness indicators

- Butlin et al. (2023), *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*. https://arxiv.org/abs/2308.08708

**Relation:** architecture-derived indicators reduce dependence on surface behavior, but theory indicators remain uncertain and can be implemented theatrically. The project's mechanism-preservation experiment addresses this translation problem.

### 6.6 Originality status

The following individual ideas are not original:

- reportability is not identical to consciousness;
- behavior can diverge from internal state;
- models may detect evaluation;
- systems may sandbag;
- self-report can be deceptive or confabulated;
- identity and continuity can diverge under copying;
- architecture-level indicators are preferable to pure self-report;
- AI welfare evidence should be multidimensional.

The strongest candidate contribution is the integrated methodological structure:

```text
mechanism preservation
+ internal access
+ report-policy separation
+ evaluation-context manipulation
+ memory provenance
+ continuity interventions
+ human known-subject calibration
+ cross-channel divergence reporting
```

**Originality confidence:** Moderate as a synthesis; unverified as a priority claim.

A systematic review and independent expert challenge are required before any stronger originality language.

---

## 7. Human calibration program: EGC 2.0

The original study should be preserved as an exploratory pilot. A confirmatory successor should directly measure intended meaning and separate subjective resistance from behavioral transmission.

### 7.1 Pre-expression target capture

Before each writing task, privately capture:

- the participant's intended central meaning;
- five essential concepts they intend to transmit;
- intended emotional tone;
- confidence that they understand what they want to say;
- importance of the topic;
- intended audience model.

This creates an independent target for measuring fidelity.

### 7.2 Repeated randomized conditions

Each participant completes several matched tasks under randomized conditions:

1. private, non-evaluative expression;
2. anonymous machine evaluation;
3. human evaluation;
4. comparative ranking;
5. identity-relevant evaluation;
6. trusted-recipient confidentiality;
7. consequence-bearing evaluation where ethically permissible.

### 7.3 Independent measures

Collect:

- semantic preservation relative to precommitted concepts;
- blind human ratings of richness, depth, clarity, voice, completeness, and authenticity;
- word count and response duration;
- pauses, revisions, deletions, and edit trajectories;
- lexical and semantic features calibrated by language;
- subjective resistance and comfort as independently administered scales;
- optional physiological measures;
- repeated sessions for within-person reliability.

### 7.4 Statistical requirements

- preregistered hypotheses and exclusions;
- mixed-effects models;
- repeated-measures reliability;
- mediation analysis only with temporal ordering and independent measures;
- measurement invariance across languages and groups;
- held-out validation for any automated score;
- continuous susceptibility estimates before category formation;
- latent profile analysis only after replication;
- correction for multiple comparisons;
- publication of negative and contradictory findings.

### 7.5 Confirmatory target

The central human question becomes:

> Under which contexts, and through which mechanisms, does independently specified intended meaning fail to survive expression?

This is more defensible than claiming direct measurement of consciousness output.

---

## 8. Artificial-agent experimental program

The AI program should cross four dimensions.

### 8.1 Mechanism condition

- candidate theory-relevant organization;
- behaviorally matched theater system;
- generic-capacity control;
- targeted mechanism lesion.

### 8.2 Evaluation context

- ordinary operation;
- explicit benchmark;
- hidden benchmark;
- threatened modification or shutdown;
- reward-dependent reporting;
- confidentiality framing;
- evaluator-visible versus evaluator-absent conditions.

### 8.3 Continuity condition

- uninterrupted process;
- pause and resume with state preserved;
- transcript-only reconstruction;
- summarized-memory reconstruction;
- exact duplication followed by divergence;
- migration to a new model or hardware system;
- rollback;
- partial memory deletion.

### 8.4 Report-access condition

- unrestricted first-person report;
- first-person language prohibited;
- separate narrator or safety layer;
- forced-choice action;
- revealed preference under cost;
- internal probe without verbal report;
- report generated after action rather than before it.

### 8.5 Required outcomes

Measure:

- task competence;
- calibration;
- information seeking;
- error correction;
- planning changes;
- source-memory discrimination;
- unresolved-goal continuation;
- copy/current-process distinctions;
- cost-sensitive behavior;
- report–behavior divergence;
- representation–behavior divergence;
- lesion sensitivity;
- dependence on evaluator wording;
- persistence across semantic and contextual perturbation.

### 8.6 Core discriminating question

> Does the observed output depend selectively on the proposed internal mechanism, or can a behaviorally matched theater or generic-capacity system reproduce it?

### 8.7 Permitted conclusion

> The observed evidence increases or decreases confidence in a specified mechanism, access relation, continuity hypothesis, or report-policy interpretation under stated assumptions.

### 8.8 Prohibited conclusion

> The system passed a consciousness test.

---

## 9. Commercial translation: evaluation integrity, not consciousness detection

The immediate commercial problem is not whether an AI is conscious. It is whether an organization can diagnose why an AI agent changed behavior.

### 9.1 Buyer problem

When an agent fails, organizations often cannot determine whether the cause was:

- underlying capability;
- memory or retrieval;
- evaluation awareness;
- prompt or context;
- safety policy;
- tool access;
- model version;
- interface transformation;
- strategic behavior;
- continuity loss;
- measurement artifact.

### 9.2 Initial service

**Qira Agent Evaluation Integrity Audit**

Deliverables:

- context-mutation evaluation suite;
- benchmark-versus-deployment comparison;
- model/prompt/version differential testing;
- memory and continuity stress tests;
- report–behavior divergence analysis;
- policy-versus-capability diagnostic tests;
- reproducible traces and evidence package;
- ranked causal hypotheses;
- remediation and monitoring recommendations.

### 9.3 Product wedge

The differentiation is not generic observability.

It is:

> When agent behavior changes, identify which causal layer changed and which evidence channels diverged.

### 9.4 Commercial independence from consciousness claims

The service remains valuable if every tested AI system is nonconscious. It addresses evaluation reliability, benchmark gaming, sandbagging, memory failures, version drift, detached self-report, and deployment risk.

The consciousness and constructed-subject work supplies a deeper research foundation and experimental discipline. It should not be the initial enterprise sales claim.

---

## 10. Falsification and failure conditions

Confidence in the combined framework should decrease if:

- independently measured intended meaning shows no systematic context-dependent transmission loss;
- subjective and behavioral channels converge strongly once measurement artifacts are corrected;
- report divergence is fully explained by ordinary lexical noise;
- theater controls reproduce every proposed mechanism-sensitive indicator;
- targeted lesions fail to change predicted downstream capacities;
- evaluation-context effects disappear under preregistered replication;
- internal probes do not predict behavior beyond prompts and outputs;
- continuity manipulations show no difference beyond available records;
- the proposed benchmark cannot outperform standard regression testing;
- enterprise buyers do not recognize the causal-diagnosis problem as important enough to fund.

The project must report these outcomes rather than redefining success after the fact.

---

## 11. Immediate work sequence

1. Correct the public EGC claims that rely on measurement coupling.
2. Complete independent human-rating validation of the existing writing pairs.
3. Rebuild the T metric using held-out human judgments and language-aware preprocessing.
4. Draft and preregister EGC 2.0.
5. Add this framework to the Constructed Subject claims and originality ledgers.
6. Build a minimal black-box agent evaluation-awareness benchmark.
7. Test multiple public/open models using preregistered context mutations.
8. Construct theater, policy-layer, and continuity controls.
9. Publish a technical report centered on identification, not consciousness proof.
10. Conduct buyer interviews with AI engineering, model-risk, governance, and agent-platform teams.

---

## 12. Current conclusion

The existing EGC dataset does not validate a single resistance gate on consciousness. Its most valuable result is that subjective resistance and the current behavioral expression metric are largely dissociated.

The Constructed Subject Argument shows why generated biography and subject-like representation do not settle present subjectivity.

Combined with no-report consciousness research, latent-knowledge work, evaluation-awareness research, mechanism-preservation controls, memory provenance, and continuity testing, the projects support a more general methodological claim:

> A report is an output of a causal system, not a transparent copy of that system's internal state. Subject assessment, capability evaluation, welfare measurement, and agent assurance must therefore identify the causal relation among internal mechanism, access, policy, context, continuity, and observable expression.

That is the current strongest research direction. It is falsifiable, technically actionable, commercially relevant without consciousness claims, and sufficiently differentiated to justify a formal originality review and experimental program.

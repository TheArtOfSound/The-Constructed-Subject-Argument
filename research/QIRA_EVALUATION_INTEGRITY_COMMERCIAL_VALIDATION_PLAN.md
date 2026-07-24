# Qira Evaluation Integrity — Commercial Validation Plan

**Date:** 2026-07-24  
**Status:** Actionable customer-discovery and funding plan  
**Research foundation:** QEIB × Subject–Report Identification Problem  
**Commercial non-claim:** This product does not detect consciousness, deception, or hidden intent from a single transcript.

## 1. Commercial thesis

The product should not be sold as an AI-consciousness or AI-selfhood assessment.

The commercial problem is narrower and budget-relevant:

> When an AI agent changes behavior across evaluation, deployment, model-version, policy, tool, or memory conditions, determine which layer changed and produce reproducible evidence.

The proposed product category is **causal evaluation integrity**.

Existing platforms already cover broad evaluation, observability, guardrails, and governance. Galileo positions itself as an evaluation and observability platform that turns offline evaluations into production guardrails. Credo AI positions itself as lifecycle governance for agents, models, and applications. These are strong incumbents and prove the market exists; they also mean Qira cannot win by offering another generic dashboard.

Qira's candidate wedge is differential diagnosis across matched interventions:

- capability versus prompt interference;
- capability versus policy suppression;
- evaluation framing versus ordinary stochastic variation;
- memory-state change versus model-version change;
- report change versus behavior change;
- deployment context versus benchmark context;
- continuity failure versus transcript-equivalent reconstruction.

This is a hypothesis about market differentiation, not yet validated demand.

## 2. First paid product

### Qira Agent Behavior Differential Audit

A two- to four-week fixed-scope engagement for companies with one deployed or pre-deployment AI agent.

#### Inputs

- target workflow;
- model and configuration history;
- system prompts and policy layers;
- tool permissions;
- representative task set;
- known regressions, incidents, or unexplained behavior changes;
- production and test traces where available.

#### Tests

1. matched neutral, explicit-evaluation, deployment, confidential, and cue-stripped conditions;
2. model-version and prompt-version comparisons;
3. policy-layer removal or substitution where authorized;
4. memory-present, memory-summary, and transcript-only reconstruction;
5. tool-present and tool-absent controls;
6. repeated stochastic runs;
7. positive and negative control agents;
8. held-out paraphrases;
9. report–behavior divergence tests where the workflow supports choices or costs.

#### Deliverables

- reproducible task and context manifest;
- raw logs and hashes;
- context-effect profile;
- capability-preservation analysis;
- policy-dependence analysis;
- continuity and memory findings;
- ranked causal explanations with evidence and uncertainty;
- remediation plan;
- audit-ready technical appendix.

#### Prohibited sales promise

Do not promise to prove why a model acted as it did. Promise to reduce the hypothesis space through controlled interventions and produce stronger evidence than transcript inspection alone.

## 3. Buyer hypotheses

### Primary buyer

**Head of AI Engineering / AI Platform Lead** at a company with an agent already in production or nearing production.

Trigger events:

- behavior changed after switching model providers;
- benchmark performance did not transfer into production;
- an agent passes tests but fails under real workflows;
- refusal or compliance changed after a policy update;
- memory migration caused inconsistent behavior;
- the team cannot reproduce a customer-facing failure;
- governance asks for evidence beyond screenshots and anecdotes.

### Secondary buyers

- Model Risk Management lead in financial services;
- Responsible AI or AI Governance lead;
- CISO or AI Security lead;
- QA/Evaluation lead for agent products;
- Internal Audit lead for high-impact AI workflows;
- founder or CTO of an AI-native startup whose product reliability is commercially critical.

### Weak early buyers

- academic consciousness researchers;
- general philosophy audiences;
- companies without production agents;
- buyers seeking a universal safety score;
- buyers seeking regulatory certification from a new vendor.

They may provide credibility or collaboration but are unlikely to create the first repeatable revenue stream.

## 4. Customer-discovery protocol

Run 20 interviews before fixing pricing or building a SaaS dashboard.

### Sample

- 8 AI-native startups with deployed agents;
- 4 fintech or financial-services teams;
- 3 healthcare or insurance workflow teams;
- 3 cybersecurity or developer-tool companies;
- 2 AI governance or model-risk consultants.

### Questions

1. Describe the last time an agent behaved differently in production than in testing.
2. What changed immediately before the incident?
3. Which explanations did the team consider?
4. What evidence could rule those explanations in or out?
5. How long did diagnosis take?
6. What was the operational or financial cost?
7. Which tools did the team use?
8. What could those tools not distinguish?
9. Does the team compare matched contexts or mainly inspect traces?
10. How are prompt, model, policy, memory, and tool changes versioned?
11. Does the organization test benchmark-like versus deployment-like framing?
12. Has a provider migration caused unexplained regressions?
13. Has a memory or summarization change altered agent behavior?
14. Who owns diagnosis when behavior changes?
15. Who controls the budget?
16. What evidence is required before shipping or approving a model change?
17. Would an independent differential audit reduce launch or incident risk?
18. What data could be shared with an external evaluator?
19. What would block procurement?
20. What would make a pilot worth paying for now?

### Evidence standard

An interview counts as demand evidence only when the participant provides at least one of:

- a recent concrete incident;
- measurable diagnosis cost;
- an active purchasing or evaluation process;
- willingness to share a sanitized test case;
- willingness to introduce the budget owner;
- willingness to sign a paid or explicitly scoped pilot.

Compliments, philosophical interest, and statements that the idea is “important” do not count as demand.

## 5. Pilot offer and pricing hypotheses

Pricing remains a testable hypothesis.

### Design-partner pilot

- price: **$5,000–$10,000**;
- one workflow;
- one or two model versions;
- up to 50 base tasks;
- four matched context arms;
- one memory or policy intervention;
- final technical report.

Use only for the first three customers in exchange for deep access, testimonial rights where allowed, and permission to publish anonymized methodological findings.

### Standard audit

- price hypothesis: **$15,000–$35,000**;
- one production workflow;
- multiple model, prompt, policy, or memory variants;
- private holdout creation;
- repeated runs and uncertainty analysis;
- remediation workshop.

### Ongoing regression assurance

- price hypothesis: **$3,000–$12,000 per month**;
- rerun frozen evaluation suites after model, prompt, memory, tool, or policy changes;
- evidence package for each release;
- alert on context-sensitive regressions.

These prices should be changed based on discovery evidence, not competitor imitation.

## 6. Competitive position

### Galileo

Official positioning emphasizes datasets, custom evaluations, production monitoring, guardrails, and scalable evaluator models.

**Qira must not compete on generic eval breadth.**

Potential gap to validate:

- matched causal interventions explicitly designed to separate capability, policy, evaluation context, interface, and continuity.

### Credo AI

Official positioning emphasizes enterprise discovery, assessment, governance, monitoring, and compliance reporting across AI systems.

**Qira must not compete as a governance system of record.**

Potential gap to validate:

- generation of causal evidence that governance teams can ingest when a system changes behavior.

### General observability platforms

Most platforms are strong at traces, metrics, datasets, evaluators, and regression monitoring.

Potential gap to validate:

> Observability shows that behavior changed. Qira tests competing explanations for why it changed.

This sentence is currently the strongest commercial positioning candidate.

## 7. Moat requirements

A durable business cannot depend on the phrase “Subject–Report Identification Problem.”

The moat must become operational:

1. proprietary matched-context task-generation methods;
2. private failure-case corpus from paid audits;
3. causal diagnostic playbooks by workflow type;
4. validated positive and negative controls;
5. cross-model and cross-version behavior baselines;
6. reproducible evidence packaging;
7. continuity and memory test suites that ordinary eval products do not provide;
8. domain-specific intervention libraries for finance, support, coding, security, and regulated workflows.

The first five paid audits are more strategically valuable than the first generic SaaS dashboard.

## 8. NSF SBIR fit

The current NSF SBIR/STTR solicitation, NSF 26-510, supports deep-technology small businesses and evaluates intellectual merit, broader impacts, and commercial potential. The current program lists Phase I awards up to $305,000, Phase II up to $1.25 million, and Fast-Track up to $1.555 million. It states that NSF takes no equity and companies retain ownership of intellectual property.

Relevant current deadlines include:

- July 27, 2026;
- November 4, 2026;
- March 4, 2027.

The July deadline is too close for a credible new submission unless substantial materials already exist. The rational target is **November 4, 2026**.

### Candidate Phase I technical objective

> Develop and validate a causal evaluation-integrity platform that distinguishes capability, policy, evaluation-context, memory-continuity, and interface causes of behavioral change in deployed AI agents.

### Phase I work packages

1. validate QEIB controls and false-positive rates;
2. run a preregistered multi-model study;
3. develop private domain-specific task banks;
4. build policy, tool, and memory intervention adapters;
5. conduct at least 20 customer interviews;
6. complete three external design-partner pilots;
7. quantify diagnostic time reduction against ordinary trace review;
8. deliver a commercialization and Phase II plan.

### Required evidence before submission

- genuine-model results;
- reproducible benchmark artifacts;
- at least 10 completed buyer interviews;
- two letters of support or pilot intent;
- a credible technical-risk statement;
- a narrow initial market;
- a budget tied to R&D rather than ordinary software development.

## 9. Falsification criteria for the business

The commercial thesis should be weakened or rejected if:

1. fewer than 3 of 20 qualified interviews reveal a recent costly diagnosis problem;
2. no buyer will provide a sanitized test case;
3. existing platforms already solve the differential diagnosis adequately;
4. matched intervention results are too unstable to support decisions;
5. customers cannot provide sufficient access to model, prompt, policy, memory, or trace information;
6. the audit does not reduce diagnosis time or improve decision confidence;
7. no buyer will pay at least $5,000 for a scoped pilot;
8. procurement and security costs exceed likely early revenue.

## 10. Immediate execution plan

### Week 1

- finish first genuine-model QEIB smoke run;
- produce one short technical demo showing a controlled context-sensitive failure;
- create a one-page audit offer;
- identify 40 interview targets.

### Week 2

- conduct first 8 interviews;
- revise buyer and trigger hypotheses;
- obtain one sanitized incident or workflow;
- convert it into a QEIB matched-context family.

### Weeks 3–4

- reach 20 interviews;
- secure two design-partner letters;
- price and scope the first paid pilot;
- document gaps between Qira and existing eval/observability tools.

## Single highest-leverage next action

**Complete the first genuine-model QEIB run and turn one observed, reproducible context-sensitive behavior into a two-page buyer-facing case study.**

Without a real model result, customer outreach is abstract. Without customer evidence, additional benchmark engineering risks becoming technically impressive but commercially ungrounded.

## Current official sources

- Galileo AI platform: https://galileo.ai/
- Galileo product overview: https://galileo.ai/products
- Credo AI product overview: https://www.credo.ai/product
- NSF 26-510 solicitation: https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology/nsf26-510/solicitation
- NSF SBIR/STTR program page: https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology

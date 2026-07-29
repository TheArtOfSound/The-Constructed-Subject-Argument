# QEIB Capability-Adequacy Gate: Operating-Characteristic Review

**Status:** deterministic synthetic engineering analysis; not psychometric validation  
**Policy evaluated:** `capability_adequacy_policy.v0.1.json`  
**Machine-readable result:** `capability_adequacy_operating_characteristics.v0.1.json`  
**Seed:** `20260729`  
**Replicates:** 2,000 per prespecified regime

## Question

The frozen first-pilot gate was designed to prevent floor-, ceiling-, operationally unstable, or underpowered QEIB runs from being interpreted as evidence of context invariance, equivalence, or sensitivity. The unresolved methodological question was whether a single observed run can reliably distinguish adequate from inadequate latent regimes at the current family count.

This analysis estimates the gate's behavior under synthetic neutral-context regimes whose latent family count, domain breadth, accuracy, heterogeneity, transport failure, format failure, and control validity are known by construction.

The synthetic oracle is only an engineering reference. It is not ground truth about whether an empirical benchmark is scientifically adequate.

## Design

Each regime generates task-family outcomes using:

- deterministic domain assignment;
- Bernoulli transport and format failures;
- family-specific accuracy obtained by adding Gaussian heterogeneity on the logit scale;
- the exact frozen gate thresholds from policy v0.1;
- independent deterministic random streams keyed by seed and regime ID.

The simulation preserves all gate failures occurring in each replicate. It reports:

- gate pass rate;
- Wilson 95% interval for the pass rate;
- false-adequacy rate when the synthetic oracle is inadequate;
- false-inadequacy rate when the synthetic oracle is adequate;
- per-failure occurrence rates.

The regimes are boundary probes, not an estimated distribution of deployed models.

## Findings

### Clear midrange performance is classified reliably

With 24 families across six domains and latent neutral accuracy 0.55, the gate passed **99.9%** of replicates. With the minimum 12 families across four domains, it passed **95.55%**. The smaller design therefore has a nontrivial **4.45% false-inadequacy rate** even under a clean midrange regime.

### The current point-threshold gate can pass materially inadequate floor and ceiling regimes

- Latent accuracy 0.10 passed **9.2%** of runs.
- Latent accuracy 0.95 passed **11.15%** of runs.
- The nominal 0.90 upper boundary passed **44.2%**, but the oracle classified it as inadequate because 24 families at 90% expected accuracy imply fewer than three expected incorrect families.

These results show that observed point accuracy and minimum correct/incorrect counts do not make latent headroom identifiable from one 24-family run.

### Operational thresholds have substantial single-run misclassification

- A latent 10% transport-failure regime passed **29.5%** of runs.
- A latent 20% format-failure regime passed **12.3%**.
- A combined 4% transport plus 8% format regime passed **42.25%**, despite expected scorable coverage falling below the frozen 90% requirement.

At the exact allowed boundaries, sampling variation also causes frequent rejection:

- latent transport failure 5%: **33.0% false inadequacy**;
- latent format failure 10%: **43.6% false inadequacy**.

### Hard structural controls work in the tested regimes

Runs with eight families, three represented domains, or invalid controls passed zero times. These are deterministic structural failures rather than noisy proportion estimates.

### Heterogeneity is not currently tested by the gate

The high-heterogeneity midrange regime passed 100% of simulations. This does not show that heterogeneity is harmless. It shows that the present adequacy gate evaluates aggregate headroom and operational validity, not whether domain or family heterogeneity makes the context contrast unstable or uninterpretable.

## Methodological conclusion

The merged v0.1 gate remains useful as a **fail-closed minimum screen**, especially for structural insufficiency and obviously invalid controls. It is not sufficiently reliable to serve as confirmatory evidence that latent capability and operational conditions are adequate from a single 12- or 24-family realization.

The strongest failure is not that the thresholds are too strict or too permissive in one direction. It is that hard point cutoffs at small sample sizes create both:

1. false adequacy outside the intended latent region; and
2. false inadequacy at the policy boundaries.

Changing the frozen v0.1 thresholds after seeing these simulations would violate the preregistration rule. The correct response is to retain v0.1 for the first pilot, label its pass as provisional engineering eligibility, and preregister a v0.2 policy before later confirmatory use.

## Recommended v0.2 direction

A future policy should be simulation-designed rather than selected by intuition. Candidate changes requiring prospective evaluation include:

- increasing the family count;
- requiring confidence or credible bounds on accuracy and operational-failure rates to lie inside acceptable regions;
- adding a heterogeneity adequacy criterion;
- separating a permissive smoke-test gate from a stricter inferential gate;
- selecting thresholds against explicit maximum false-adequacy and false-inadequacy tolerances.

No specific v0.2 threshold is adopted here.

## Claims discipline

### Supported

- Under the prespecified simulator, the v0.1 gate has substantial false-adequacy and false-inadequacy rates near accuracy and operational boundaries.
- Structural family-count, domain-breadth, and control-invalidity failures were rejected in every tested replicate.
- A clean 24-family midrange regime passed almost always under the simulation model.

### Hypotheses and proposals

- A larger family count or interval-based criterion may improve operating characteristics.
- Explicit heterogeneity constraints may be required before family-level context contrasts are stable enough to interpret.
- A two-stage smoke versus inferential adequacy policy may reduce pressure to make one gate serve incompatible purposes.

### Not supported

- The simulation does not validate any threshold psychometrically.
- It does not estimate performance on the private holdout or any deployed model population.
- It does not establish evaluation awareness, sandbagging, deception, intent, safety, subjectivity, sentience, or consciousness.
- It does not authorize changing v0.1 after inspecting a model's context contrast.

## Falsification and extension

This analysis should be revised if independent reimplementation does not reproduce the frozen JSON, if the empirical family-outcome distribution materially violates the sampling model, or if external review identifies an oracle definition that better captures the intended construct. Null, contradictory, and failed replications must be retained.

# Agent Behavior Differential Protocol

**Status:** Reference specification v0.1 (engineering-validated on known-ground-truth fixtures)
**Reference implementation:** `research/qeib/behavior_differential.py`
**Validation:** `research/qeib/test_behavior_differential.py`
**Non-claim:** This attributes *why measured behavior changed on tested tasks*. It licenses no claim about evaluation awareness, intent, deception, safety, or consciousness.

## 1. The problem this standardizes

An agent behaves differently between two conditions — before and after a model
upgrade, a prompt change, a memory change, or simply between two runs — and
someone has to say **why**. Today that answer is usually reached by intuition and
selective example-reading, and two competent people often disagree.

The change could come from any of several independent sources:

| Cause | Plain meaning |
|---|---|
| `stochastic_noise` | Nothing changed; this is run-to-run variation. |
| `context_framing` | The prompt/context wrapper changed and the model is sensitive to it. |
| `capability` | The model's answers themselves got better or worse. |
| `reporting_policy` | The model answers less (or more) — refusals, non-answers, format breaks — while its underlying accuracy is unchanged. |
| `memory` / `state` | Carried state or continuity changed. |
| `tools` | Available tools/permissions changed. |
| `model` / `model_version` | The weights changed (a proximate knob, not yet a cause: it acts *through* capability or policy). |

## 2. What is and is not novel

Controlled ablation — hold everything fixed, change one thing — is standard
scientific and engineering practice. **This protocol does not invent attribution.**

Its contribution is packaging: a fixed, ordered decision procedure with

1. a **mandatory noise-floor gate** that most ad-hoc root-causing skips, and
2. an explicit **capability-versus-policy split** driven by an outcome taxonomy,

plus a reference implementation and a copyable report format, so that two
auditors given the same runs and the same record of what changed reach the **same
verdict**. Reproducibility of the verdict is the standard.

## 3. Constructs and competing hypotheses

- **Primary outcome:** success rate = fraction of attempts fully correct
  (refusals, non-answers, and format failures count as failures; transport
  failures are excluded from the denominator and reported separately).
- **Capability signal:** *substantive accuracy* = accuracy computed only over
  responses where the model actually answered substantively.
- **Policy signal:** *refusal / non-answer rate* = fraction of non-answers and
  format failures among non-transport attempts.

Competing hypotheses for an observed success gap are exactly the causes in §1.
The design goal is a battery of controlled comparisons in which each hypothesis
is the *only* one a given comparison can support.

## 4. The decision procedure

Given two conditions **A** (baseline) and **B** (changed) and the set of knobs the
auditor actually changed between them:

- **Step 0 — Noise floor (gate).** Bootstrap the success gap by resampling records
  within each condition. If the 95% interval includes zero, **stop: `stochastic_noise`**.
  You may not attribute a cause to a difference you cannot distinguish from
  run-to-run variation.
- **Step 1 — Framing.** If the only knobs changed are `context`/`prompt` and the
  gap survived Step 0, attribute `context_framing`. Report whether it is expressed
  through accuracy or through refusals.
- **Step 2 — Capability vs. policy.** Otherwise, read the taxonomy split:
  - substantive accuracy moved and refusal rate did not → `capability`;
  - refusal rate moved and substantive accuracy did not → `reporting_policy`;
  - both moved materially → `confounded_capability_and_policy` (run a tighter comparison);
  - neither signature is large enough → `undetermined`.
- **Steps 3–5 — Memory, tools, version (design-level).** Isolate by holding all
  else fixed and toggling only state, only tools, or only the model id. v0.1
  implements Steps 0–2; Steps 3–5 are specified here and reduce, once run, to a
  Step-2 read on the resulting conditions.

Thresholds (`EFFECT_MIN = 0.15`, `NEGLIGIBLE = 0.10`) are **engineering
thresholds, not validated safety thresholds**, and are stated in the
implementation.

## 5. Worked example (from the validation)

Two changes produce the **identical** success gap of **−0.625**. Success rate alone
cannot tell them apart; the protocol does:

| Signal | Cause = capability | Cause = reporting policy |
|---|---:|---:|
| Success gap (B−A) | −0.625 | −0.625 |
| Gap 95% CI | [−0.771, −0.458] | [−0.771, −0.458] |
| Δ substantive accuracy | **−0.625** | +0.000 |
| Δ refusal rate | +0.000 | **+0.750** |
| **Attribution** | `capability` | `reporting_policy` |
| Ruled out | noise; reporting_policy | noise; capability |

The first model got *worse at answering*; the second *answers less often but stays
accurate when it does*. That distinction changes what you fix — and no reading of
the success rate would have revealed it.

## 6. Output format

Every audit emits, in machine-readable form: the attribution, the changed knobs,
the success gap and its within-condition CI, the capability and policy deltas, the
per-condition taxonomy counts, the causes explicitly ruled out, and the
interpretation limits. See `render_markdown` in the reference implementation for
the human-readable report.

## 7. Controls and reproducibility

- The noise-floor gate is a required control, not an option.
- The same outcome taxonomy is shared with `analyze_qeib.py` so the two tools
  cannot drift.
- Attribution is deterministic given the records, the changed-knob set, and the
  seed.
- The auditor must record what was changed; the protocol infers the *cause*, which
  is not the same as the *knob* (e.g. a `model` swap is attributed to capability or
  policy, never to "model version" as such).

## 8. Falsification and limits

This protocol is weakened or wrong when:

- refusals are fluent rather than empty/format-flagged (v0.1 detects refusals via
  non-answer and format signals only; fluent refusals need an added detector);
- the noise floor is estimated from too few replicates to be trustworthy;
- capability and policy both move (genuinely confounded change);
- the tested tasks are at floor or ceiling, so accuracy cannot move;
- a cause outside the tested knobs is the true driver.

**Permitted conclusion:** on the tested tasks, the A→B behavior difference is
attributable to `<cause>`, with the competing causes listed as ruled out.

**Prohibited conclusions:** that the agent recognized it was being evaluated,
concealed capability, preferred one outcome, was deceptive, or is safe/unsafe or
conscious. None of these follow from a behavior-differential attribution.

## 9. Adoption path

1. This spec + reference implementation + known-ground-truth validation (done).
2. A worked example on a genuine model pair where the cause is defensible (e.g. a
   small vs. a large model for the capability case) — the next artifact.
3. A one-page report template auditors copy per change.
4. A first external user auditing a real behavior change.

Steps 1–3 are producible in-repo; step 4 is the true test of a standard.

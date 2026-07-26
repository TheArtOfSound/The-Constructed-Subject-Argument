# EGC 2.0 Workload-Aware Monitoring Design Comparison

**Status:** Synthetic sensitivity analysis; not empirical evidence about real raters  
**Compared designs:** complete 8-rater × 18-item-per-class versus incomplete-block 12-rater × 36-item-per-class  
**Primary threshold:** material early-to-late change `δ = 0.20`

## Question

The previous design comparison favored 12 raters and 36 study-level items per monitoring class. That comparison did not model the actual incomplete-block exposure pattern, fatigue, recognition, rater severity, or informative dropout. This run asks whether the larger item bank retains its apparent detector advantage once each rater sees only 12 items per class and workload-dependent processes are explicit.

## Synthetic construction

Both designs generate 576 planned ratings:

- `complete_8x18`: 8 raters × 18 items × 4 classes = 576 ratings. Every rater sees every study-level item.
- `incomplete_12x36`: 12 raters × 12 assigned items × 4 classes = 576 ratings. Each class contains 36 study-level items, but each rater sees only one third of them.

Each trial includes global rater severity, late-session fatigue, exact-anchor recognition improvement, weaker transfer to surface variants, adverse drift on structural-transfer and novel items, random score noise, and dropout probability increasing with rater severity/disagreement.

The generating parameters are engineering sensitivity regimes, not estimated properties of real EGC raters.

## Validation

Six unit tests passed:

1. unknown designs fail clearly;
2. planned workload bounds hold;
3. fixed seeds reproduce identical rows;
4. the adversarial regime separates exact-anchor and novel shifts;
5. the null generalized-learning regime does not systematically produce false reassurance;
6. informative dropout reduces completed ratings.

The compact comparison used 200 Monte Carlo trials per design × regime cell.

## Results

### False-reassurance detection support

| Regime | Complete 8×18 | Incomplete 12×36 |
|---|---:|---:|
| Reference | 97.5% | 72.0% |
| High fatigue | 97.5% | 70.0% |
| High noise | 91.5% | 66.5% |
| Informative dropout | 97.5% | 75.5% |
| Null generalized learning | 0.0% | 0.0% |

The incomplete-block design produced substantially more indeterminate outcomes: 24.5%–33.0% in adversarial regimes, versus 2.5%–8.0% for the complete design.

### Mean completed ratings

The two designs had the same planned rating count. Informative dropout reduced mean completed ratings to approximately 544.9 for complete 8×18 and 537.7 for incomplete 12×36. The difference is small relative to the detector-support gap.

## Finding supported within this simulator

The prior conclusion that 12 raters × 36 items per class was automatically superior does **not** survive this workload-aware incomplete-block comparison.

With equal total rating budgets, the complete 8×18 design had much stronger sensitivity in the tested regimes because every study-level item was observed by all eight raters, whereas the incomplete 12×36 design spread the same budget across twice as many unique items with only four ratings per item.

This is not evidence that eight raters are generally preferable. It shows a real design tradeoff:

> Broader item coverage can reduce detector precision when the total rating budget is fixed and ratings per item are cut in half.

## Why the result does not settle the design

The current detector pools early and late observations by item class. It does not fit a crossed item-and-rater model. Consequently:

- the complete design benefits from denser ratings per item;
- the incomplete design benefits from broader content coverage, but that advantage is not fully represented by a pooled-shift detector;
- repeated ratings of the same 18 items may overstate generalization if item heterogeneity is substantial;
- the simulator does not yet include item-specific random effects strong enough to reward broader sampling;
- the comparison therefore identifies a bias-variance tradeoff rather than a final winner.

## Claims discipline

### Supported

- Equal total rating budgets do not imply equal detector sensitivity.
- Increasing unique item coverage while reducing ratings per item can increase indeterminate results.
- The 12×36 incomplete-block design requires a hierarchical item-and-rater analysis; the prior pooled detector is not sufficient to certify it.
- Informative dropout did not erase the qualitative design gap in these regimes.

### Hypotheses not yet tested

- Whether 12×36 outperforms 8×18 when item heterogeneity and domain generalization are modeled realistically.
- Whether a crossed mixed-effects or generalizability-theory estimator recovers the broader-bank advantage.
- Whether 48 items per rater produces realistic fatigue or satisficing.
- Whether recognition and dropout parameters resemble real pilot raters.

### Rejected or weakened

- Weakened: “12 raters × 36 items per class is the provisional preferred design.”
- Rejected: “More unique items necessarily improve detector sensitivity at a fixed total rating budget.”
- Prohibited: using this synthetic result as evidence that the complete design is scientifically valid or that real raters will behave similarly.

## Decision

Do not freeze either design yet. The next comparison must introduce item-level heterogeneity and analyze data with a crossed item-and-rater estimator. It should compare:

1. 8×18 complete;
2. 12×36 incomplete with four ratings per item;
3. 12×24 incomplete with six ratings per item;
4. 12×18 denser incomplete or complete variants;

under a fixed total rating budget.

## Highest-leverage next action

Implement a crossed item-and-rater simulation with explicit item difficulty/ambiguity variance and compare bias, interval coverage, false reassurance, and domain-generalization error across fixed-budget designs. This is required before selecting item breadth versus ratings-per-item.

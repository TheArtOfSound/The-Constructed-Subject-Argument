# EGC 2.0 Restricted Wild-Cluster Bootstrap-t Engineering Review

## Scope

This run implemented a narrowly scoped restricted wild-cluster bootstrap-t candidate for the frozen `complete_8x18_r8 × N1` calibration cell.

The bootstrap data-generating process clusters on the rater dimension, which has eight clusters, while every bootstrap draw is studentized using the existing two-way CGM item + rater - item-by-rater variance estimator. All `2^8 = 256` rater-level Rademacher sign patterns are enumerated exactly, so bootstrap Monte Carlo error is eliminated for each generated dataset.

This follows the class of procedures studied by MacKinnon, Nielsen, and Webb in *Wild Bootstrap and Asymptotic Inference with Multiway Clustering*, where one clustering variable is selected for the bootstrap DGP and inference is based on a multiway-clustered statistic. It is not asserted to be universally valid for arbitrary crossed designs.

Primary source:

- James G. MacKinnon, Morten Ørregaard Nielsen, and Matthew D. Webb, “Wild Bootstrap and Asymptotic Inference with Multiway Clustering,” Journal of Business & Economic Statistics / Queen's Economics Department Working Paper 1415.

## Null imposition

The repository estimand is the scalar contrast

```text
exact_anchor - 0.5 × structural_transfer - 0.5 × novel.
```

For each dataset, the unrestricted class-mean vector is projected onto the null hyperplane where this contrast equals zero. The projection is the minimum-Euclidean-norm adjustment along the fixed contrast vector. Residuals are centered within unrestricted monitoring class and multiplied by one shared Rademacher sign per rater.

This construction makes the scalar null exact before bootstrap resampling while preserving the observed item/rater assignment structure.

## Validation

Six focused tests passed:

1. null projection yields a contrast of zero to 12 decimal places;
2. bootstrap reconstruction preserves row count, item IDs, and rater IDs;
3. exactly 256 sign patterns are enumerated for eight raters;
4. defined p-values remain in `[0,1]`;
5. fixed inputs reproduce identical results;
6. empty data, negative effects, and nonpositive trial counts fail clearly.

`py_compile` also passed for the implementation and test module.

## Preserved failed run

The planned 40-null × 40-power engineering run exceeded the execution environment's hard per-call runtime limit and produced no retained scientific result.

A smaller 15-null × 15-power smoke run was then completed and committed. This reduction was operational, not a scientific stopping rule.

## Smoke result

At a true contrast of `0.00`:

- two-sided rejection: `1/15 = 0.0667`;
- undefined observed trials: `0/15`;
- mean undefined bootstrap-pattern rate: `0.00573`.

At a true contrast of `0.20`:

- rejection/power: `11/15 = 0.7333`;
- undefined observed trials: `0/15`;
- mean undefined bootstrap-pattern rate: `0.00573`.

These rates are too imprecise for method selection. In particular, one rejection under the null is compatible with a wide range of true Type-I error rates.

## Findings supported

- Exact enumeration over eight rater clusters is computationally and deterministically feasible.
- The scalar null can be imposed exactly without changing item/rater assignment metadata.
- The procedure preserves and reports bootstrap draws with negative or nonpositive two-way variance rather than silently treating them as valid.
- The implementation can now be run on the same frozen data-seed contract as the existing item-only, pigeonhole, CGM/t, and CV3J calibrations.

## Hypotheses not yet tested

- The restricted exact wild bootstrap-t may provide a better calibration-power balance than the existing candidates.
- Exact enumeration may be especially useful with only eight rater clusters because it removes resampling Monte Carlo error.

## Claims not supported

The smoke run does not establish:

- nominal Type-I error;
- adequate power at `0.20`;
- valid confidence intervals;
- validity under N2/N3 heterogeneity, incomplete blocks, informative dropout, ordinal boundaries, or real human ratings;
- that choosing raters rather than items for the bootstrap DGP is optimal.

The overall status therefore remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Next decision rule

The method should be evaluated on the preregistered 1,000 null datasets and 250 matched `0.20` datasets. Undefined observed trials and undefined sign patterns must remain in the denominator and be reported separately. If runtime remains limiting, the implementation should be algebraically optimized without changing seeds, sign patterns, null projection, or studentization.

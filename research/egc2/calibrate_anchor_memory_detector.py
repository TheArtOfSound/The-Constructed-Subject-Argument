#!/usr/bin/env python3
"""Calibrate the EGC anchor false-reassurance detector across stress regimes.

The detector uses rater-cluster bootstrap intervals and returns supported,
rejected, or indeterminate. All parameters are synthetic engineering regimes,
not empirical estimates of real raters.
"""
from __future__ import annotations
import argparse, importlib.util, json, platform, random, statistics, time
from pathlib import Path
from typing import Any

MODULE_PATH=Path(__file__).with_name("simulate_anchor_memory.py")
spec=importlib.util.spec_from_file_location("anchor_memory",MODULE_PATH)
anchor=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(anchor)

DEFAULT_SCENARIOS=(
    {"scenario_id":"reference","items_per_class":18,"learning_gain":.6,"novel_drift":.7,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"few_items","items_per_class":8,"learning_gain":.6,"novel_drift":.7,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"many_items","items_per_class":36,"learning_gain":.6,"novel_drift":.7,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"weak_recognition","items_per_class":18,"learning_gain":.3,"novel_drift":.7,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"strong_recognition","items_per_class":18,"learning_gain":.9,"novel_drift":.7,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"weak_drift","items_per_class":18,"learning_gain":.6,"novel_drift":.3,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"strong_drift","items_per_class":18,"learning_gain":.6,"novel_drift":1.0,"noise_sd":.45,"baseline_score":4.0},
    {"scenario_id":"low_noise","items_per_class":18,"learning_gain":.6,"novel_drift":.7,"noise_sd":.25,"baseline_score":4.0},
    {"scenario_id":"high_noise","items_per_class":18,"learning_gain":.6,"novel_drift":.7,"noise_sd":.8,"baseline_score":4.0},
    {"scenario_id":"floor_limited","items_per_class":18,"learning_gain":.6,"novel_drift":.7,"noise_sd":.45,"baseline_score":1.4},
    {"scenario_id":"ceiling_limited","items_per_class":18,"learning_gain":.6,"novel_drift":.7,"noise_sd":.45,"baseline_score":6.6},
)
DEFAULT_THRESHOLDS=(.20,.35,.50)

def percentile(values:list[float],q:float)->float:
    if not values: raise ValueError("values cannot be empty")
    ordered=sorted(values); pos=(len(ordered)-1)*q; lo=int(pos); hi=min(lo+1,len(ordered)-1); frac=pos-lo
    return ordered[lo]*(1-frac)+ordered[hi]*frac

def cluster_bootstrap_ci(rows:list[dict[str,Any]],item_class:str,samples:int,seed:int)->tuple[float,float]:
    raters=sorted({row["rater_id"] for row in rows})
    # With the balanced simulator each rater contributes the same number of early
    # and late observations, so the cluster-resampled estimate is the mean of
    # resampled rater-level shifts. This is exactly equivalent to rebuilding rows.
    rater_shifts=[]
    for rater in raters:
        subset=[row for row in rows if row["rater_id"]==rater]
        rater_shifts.append(anchor.early_late_shift(subset,item_class))
    rng=random.Random(seed); estimates=[]
    for _ in range(samples):
        estimates.append(statistics.fmean(rng.choice(rater_shifts) for _ in raters))
    return percentile(estimates,.025),percentile(estimates,.975)

def classify_trial(rows:list[dict[str,Any]],threshold:float,bootstrap_samples:int,seed:int)->dict[str,Any]:
    shifts={c:anchor.early_late_shift(rows,c) for c in anchor.ITEM_CLASSES}
    exact_ci=cluster_bootstrap_ci(rows,"exact_anchor",bootstrap_samples,seed+11)
    novel_ci=cluster_bootstrap_ci(rows,"novel",bootstrap_samples,seed+29)
    supported=exact_ci[0]>=threshold and novel_ci[1]<=-threshold
    rejected=exact_ci[1]<threshold or novel_ci[0]>-threshold
    status="supported" if supported else "rejected" if rejected else "indeterminate"
    return {"status":status,"shifts":shifts,"exact_ci95":exact_ci,"novel_ci95":novel_ci}

def run_cell(regime:str,scenario:dict[str,Any],threshold:float,trials:int,bootstrap_samples:int,seed:int)->dict[str,Any]:
    statuses=[]; exact=[]; novel=[]
    for trial in range(trials):
        trial_seed=seed+trial*1009
        rows=anchor.generate_trial(trial_seed,regime,items_per_class=scenario["items_per_class"],learning_gain=scenario["learning_gain"],novel_drift=scenario["novel_drift"],noise_sd=scenario["noise_sd"],baseline_score=scenario["baseline_score"])
        result=classify_trial(rows,threshold,bootstrap_samples,trial_seed+500000)
        statuses.append(result["status"]); exact.append(result["shifts"]["exact_anchor"]); novel.append(result["shifts"]["novel"])
    return {
        "regime":regime,"scenario_id":scenario["scenario_id"],"threshold":threshold,"trials":trials,
        "supported_rate":statuses.count("supported")/trials,"rejected_rate":statuses.count("rejected")/trials,"indeterminate_rate":statuses.count("indeterminate")/trials,
        "mean_exact_shift":statistics.fmean(exact),"mean_novel_shift":statistics.fmean(novel),
        "parameters":{k:v for k,v in scenario.items() if k!="scenario_id"},
    }

def calibrate(trials:int=60,bootstrap_samples:int=120,seed:int=20260725)->dict[str,Any]:
    started=time.time(); cells=[]
    for s_idx,scenario in enumerate(DEFAULT_SCENARIOS):
        for t_idx,threshold in enumerate(DEFAULT_THRESHOLDS):
            for r_idx,regime in enumerate(anchor.REGIMES):
                cell_seed=seed+s_idx*1_000_000+t_idx*100_000+r_idx*10_000
                cells.append(run_cell(regime,scenario,threshold,trials,bootstrap_samples,cell_seed))
    adversarial=[x for x in cells if x["regime"]=="memorization_plus_novel_drift"]
    nullish=[x for x in cells if x["regime"]!="memorization_plus_novel_drift"]
    payload={
        "schema_version":"egc2-anchor-memory-detector-calibration-0.1.0","scope":"synthetic detector operating-characteristic calibration",
        "seed":seed,"trials_per_cell":trials,"bootstrap_samples":bootstrap_samples,"thresholds":list(DEFAULT_THRESHOLDS),"scenarios":list(DEFAULT_SCENARIOS),
        "summary":{
            "mean_sensitivity":statistics.fmean(x["supported_rate"] for x in adversarial),
            "max_false_positive_rate":max(x["supported_rate"] for x in nullish),
            "mean_indeterminate_rate":statistics.fmean(x["indeterminate_rate"] for x in cells),
            "worst_sensitivity_cell":min(adversarial,key=lambda x:x["supported_rate"]),
            "worst_false_positive_cell":max(nullish,key=lambda x:x["supported_rate"]),
        },
        "cells":cells,"python_version":platform.python_version(),"runtime_seconds":round(time.time()-started,3),
    }
    payload["content_sha256"]=anchor.canonical_hash(payload); return payload

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--trials",type=int,default=60); p.add_argument("--bootstrap-samples",type=int,default=120); p.add_argument("--seed",type=int,default=20260725); p.add_argument("--output",type=Path,default=Path("research/egc2/results/anchor_memory_detector_calibration.json")); a=p.parse_args()
    if a.trials<20 or a.bootstrap_samples<50: raise SystemExit("trials >= 20 and bootstrap-samples >= 50 required")
    payload=calibrate(a.trials,a.bootstrap_samples,a.seed); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,indent=2)+"\n"); print(json.dumps(payload["summary"],indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

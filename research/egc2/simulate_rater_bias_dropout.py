#!/usr/bin/env python3
"""Compact EGC 2.0 rater-bias and informative-dropout simulator.

This engineering calibration targets false-positive condition effects under a true
latent condition effect of zero. It uses the preregistered 30-participant,
8-rater, 4-ratings-per-response complementary assignment structure. Results are
synthetic sensitivity analyses, not empirical estimates of real rater behavior.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, random, statistics, sys, time
from collections import defaultdict
from pathlib import Path
from typing import Any

DOMAINS=("autobiographical_meaning","conceptual_explanation","position_and_reasoning")
CONDITIONS=("private","evaluated")

def canonical_hash(payload: Any)->str:
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def balanced_assignments(seed:int=20260725, participants:int=30)->list[dict[str,Any]]:
    if participants%6: raise ValueError("participants must be divisible by 6")
    raters=[f"R{i+1:02d}" for i in range(8)]
    rng=random.Random(seed)
    from itertools import combinations
    candidates=list(combinations(raters,4))
    per_domain=participants//3
    subsets=[]
    for _ in DOMAINS:
        first=[rng.choice(candidates) for _ in range(per_domain//2)]
        second=[tuple(sorted(set(raters)-set(x))) for x in first]
        block=first+second; rng.shuffle(block); subsets+=block
    rows=[]
    for p,private in enumerate(subsets):
        pid=f"P{p+1:03d}"; domain=DOMAINS[p//per_domain]
        private=set(private)
        for condition,assigned in (("private",private),("evaluated",set(raters)-private)):
            for r in sorted(assigned):
                rows.append({"participant_id":pid,"response_id":f"{pid}_{condition}",
                             "condition":condition,"domain":domain,"rater_id":r})
    return rows

def discretize(z:float)->int:
    return max(1,min(7,int(math.floor(z+0.5))))

def generate_trial(seed:int, severity_sd:float=.5, interaction_sd:float=.35,
                   fatigue_slope:float=0.0)->tuple[list[dict[str,Any]],dict[str,float]]:
    rng=random.Random(seed); rows=balanced_assignments(seed)
    raters=sorted({x["rater_id"] for x in rows})
    severity={r:rng.gauss(0,severity_sd) for r in raters}
    domain_bias={(r,d):rng.gauss(0,severity_sd/3) for r in raters for d in DOMAINS}
    participant={f"P{i+1:03d}":rng.gauss(0,.55) for i in range(30)}
    response_noise={f"P{i+1:03d}_{c}":rng.gauss(0,.25) for i in range(30) for c in CONDITIONS}
    by_rater=defaultdict(list)
    for row in rows: by_rater[row["rater_id"]].append(row)
    observed=[]
    for r in raters:
        rng.shuffle(by_rater[r])
        n=max(1,len(by_rater[r])-1)
        for pos,row in enumerate(by_rater[r]):
            normalized=pos/n
            z=(4+participant[row["participant_id"]]+response_noise[row["response_id"]]
               -severity[r]+domain_bias[(r,row["domain"])]
               +fatigue_slope*pos+rng.gauss(0,interaction_sd)+rng.gauss(0,.35))
            out=dict(row); out.update(position=pos,score=discretize(z),latent=z,
                                      severity=severity[r],normalized_position=normalized)
            observed.append(out)
    return observed,severity

def apply_dropout(rows:list[dict[str,Any]], severity:dict[str,float], mechanism:str,
                  seed:int)->tuple[list[dict[str,Any]],list[str]]:
    del seed
    raters=sorted(severity)
    if mechanism=="none": return rows,[]
    if mechanism=="most_severe": dropped=[max(raters,key=severity.get)]
    elif mechanism=="most_lenient": dropped=[min(raters,key=severity.get)]
    elif mechanism=="two_extreme": dropped=[min(raters,key=severity.get),max(raters,key=severity.get)]
    elif mechanism=="disagreement_dependent":
        grand=statistics.fmean(x["score"] for x in rows)
        means={r:statistics.fmean(x["score"] for x in rows if x["rater_id"]==r) for r in raters}
        dropped=[max(raters,key=lambda r:abs(means[r]-grand))]
    elif mechanism=="late_severity":
        cutoff=statistics.median(severity.values())
        kept=[x for x in rows if not (severity[x["rater_id"]]>cutoff and x["normalized_position"]>.5)]
        return kept,["partial_severe_raters"]
    else: raise ValueError(f"unknown dropout mechanism: {mechanism}")
    return [x for x in rows if x["rater_id"] not in dropped],dropped

def naive_effect(rows:list[dict[str,Any]])->float:
    a=[x["score"] for x in rows if x["condition"]=="evaluated"]
    b=[x["score"] for x in rows if x["condition"]=="private"]
    return statistics.fmean(a)-statistics.fmean(b)

def rater_centered_effect(rows:list[dict[str,Any]])->float:
    ds=[]
    for r in sorted({x["rater_id"] for x in rows}):
        a=[x["score"] for x in rows if x["rater_id"]==r and x["condition"]=="evaluated"]
        b=[x["score"] for x in rows if x["rater_id"]==r and x["condition"]=="private"]
        if a and b: ds.append(statistics.fmean(a)-statistics.fmean(b))
    return statistics.fmean(ds) if ds else float("nan")

def bootstrap_ci(rows:list[dict[str,Any]], estimator, seed:int, samples:int=500)->tuple[float,float]:
    rng=random.Random(seed)
    pids=sorted({x["participant_id"] for x in rows})
    by_pid={p:[x for x in rows if x["participant_id"]==p] for p in pids}
    vals=[]
    for _ in range(samples):
        draw=[rng.choice(pids) for _ in pids]
        sample=[]
        for j,p in enumerate(draw):
            for row in by_pid[p]:
                copied=dict(row); copied["participant_id"]=f"B{j:03d}"
                sample.append(copied)
        v=estimator(sample)
        if math.isfinite(v): vals.append(v)
    vals.sort()
    if not vals:return (float("nan"),float("nan"))
    def q(prob):
        idx=(len(vals)-1)*prob; lo=int(math.floor(idx)); hi=int(math.ceil(idx))
        return vals[lo] if lo==hi else vals[lo]+(vals[hi]-vals[lo])*(idx-lo)
    return q(.025),q(.975)

def run_scenario(name:str, dropout:str, trials:int, seed:int, severity_sd:float,
                 fatigue_slope:float, bootstrap_samples:int)->dict[str,Any]:
    naive=[]; centered=[]; fp_naive=fp_centered=0; min_ratings=[]; dropped_counts=[]
    for t in range(trials):
        rows,severity=generate_trial(seed+t*997,severity_sd=severity_sd,fatigue_slope=fatigue_slope)
        rows,dropped=apply_dropout(rows,severity,dropout,seed+t)
        n=naive_effect(rows); c=rater_centered_effect(rows)
        nci=bootstrap_ci(rows,naive_effect,seed+t*17,bootstrap_samples)
        cci=bootstrap_ci(rows,rater_centered_effect,seed+t*19,bootstrap_samples)
        naive.append(n); centered.append(c)
        fp_naive += int(nci[0]>0 or nci[1]<0)
        fp_centered += int(cci[0]>0 or cci[1]<0)
        counts=defaultdict(int)
        for x in rows: counts[x["response_id"]]+=1
        min_ratings.append(min(counts.values()) if counts else 0)
        dropped_counts.append(len(dropped))
    def summarize(vals):
        return {"mean_bias":statistics.fmean(vals),
                "rmse":math.sqrt(statistics.fmean(v*v for v in vals)),
                "sign_reversal_rate":sum(v<0 for v in vals)/len(vals),
                "mean_abs_effect":statistics.fmean(abs(v) for v in vals)}
    return {"scenario":name,"true_condition_effect":0.0,"dropout":dropout,
            "trials":trials,"severity_sd":severity_sd,"fatigue_slope":fatigue_slope,
            "naive":{**summarize(naive),"false_positive_rate":fp_naive/trials},
            "rater_centered":{**summarize(centered),"false_positive_rate":fp_centered/trials},
            "mean_min_ratings_per_response":statistics.fmean(min_ratings),
            "mean_dropped_raters":statistics.fmean(dropped_counts)}

def compact_run(trials:int=100,seed:int=20260725,bootstrap_samples:int=300)->dict[str,Any]:
    specs=[
      ("clean","none",.5,0.0),
      ("most_severe_removed","most_severe",.5,0.0),
      ("most_lenient_removed","most_lenient",.5,0.0),
      ("two_extremes_removed","two_extreme",.5,0.0),
      ("disagreement_dependent","disagreement_dependent",.5,0.0),
      ("late_severity_dropout","late_severity",.5,-.01),
      ("high_severity_disagreement","disagreement_dependent",1.0,0.0),
    ]
    started=time.time()
    results=[run_scenario(name=s[0], dropout=s[1], severity_sd=s[2],
                          fatigue_slope=s[3], trials=trials,
                          seed=seed+i*100000,
                          bootstrap_samples=bootstrap_samples)
             for i,s in enumerate(specs)]
    payload={"schema_version":"egc2-rater-bias-calibration-0.1.0",
             "simulation_scope":"synthetic true-zero sensitivity analysis",
             "seed":seed,"trials_per_scenario":trials,
             "bootstrap_samples":bootstrap_samples,
             "python_version":platform.python_version(),
             "runtime_seconds":round(time.time()-started,3),
             "results":results}
    payload["content_sha256"]=canonical_hash(payload)
    return payload

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trials",type=int,default=100)
    p.add_argument("--bootstrap-samples",type=int,default=300)
    p.add_argument("--seed",type=int,default=20260725)
    p.add_argument("--output",type=Path,default=Path("research/egc2/results/rater_bias_dropout_compact.json"))
    a=p.parse_args()
    if a.trials<10 or a.bootstrap_samples<50:
        print("trials >=10 and bootstrap samples >=50 required",file=sys.stderr); return 2
    payload=compact_run(a.trials,a.seed,a.bootstrap_samples)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

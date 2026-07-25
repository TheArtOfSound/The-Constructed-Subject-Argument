#!/usr/bin/env python3
"""Falsification-first EGC 2.0 anchor-memory simulator.

This synthetic sensitivity analysis distinguishes generalized rubric learning,
exact-anchor memorization, and memorization with novel-item drift. Parameters
are engineering regimes, not empirical estimates of real raters.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, random, statistics, sys, time
from pathlib import Path
from typing import Any

ITEM_CLASSES=("exact_anchor","surface_variant","structural_transfer","novel")
REGIMES=("generalized_learning","pure_memorization","memorization_plus_novel_drift")

def canonical_hash(payload:Any)->str:
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def class_effect(regime:str,item_class:str,progress:float,learning_gain:float,novel_drift:float)->float:
    if regime=="generalized_learning": return learning_gain*progress
    if regime=="pure_memorization": return learning_gain*progress if item_class=="exact_anchor" else 0.0
    if regime=="memorization_plus_novel_drift":
        if item_class=="exact_anchor": return learning_gain*progress
        if item_class=="surface_variant": return .35*learning_gain*progress
        if item_class=="structural_transfer": return -.5*novel_drift*progress
        return -novel_drift*progress
    raise ValueError(f"unknown regime: {regime}")

def generate_trial(seed:int,regime:str,raters:int=8,items_per_class:int=18,learning_gain:float=.6,novel_drift:float=.7,noise_sd:float=.45)->list[dict[str,Any]]:
    rng=random.Random(seed); rows=[]; severity=[rng.gauss(0,.35) for _ in range(raters)]
    for r in range(raters):
        for item_class in ITEM_CLASSES:
            for i in range(items_per_class):
                progress=i/max(1,items_per_class-1)
                latent=4+rng.gauss(0,.25)-severity[r]+class_effect(regime,item_class,progress,learning_gain,novel_drift)+rng.gauss(0,noise_sd)
                score=max(1,min(7,int(math.floor(latent+.5))))
                rows.append({"rater_id":f"R{r+1:02d}","item_class":item_class,"progress":progress,"score":score})
    return rows

def early_late_shift(rows:list[dict[str,Any]],item_class:str)->float:
    early=[x["score"] for x in rows if x["item_class"]==item_class and x["progress"]<=.25]
    late=[x["score"] for x in rows if x["item_class"]==item_class and x["progress"]>=.75]
    return statistics.fmean(late)-statistics.fmean(early)

def summarize_trial(rows:list[dict[str,Any]],material_change:float=.35)->dict[str,Any]:
    shifts={c:early_late_shift(rows,c) for c in ITEM_CLASSES}
    exact_improves=shifts["exact_anchor"]>=material_change
    novel_degrades=shifts["novel"]<=-material_change
    return {"shifts":shifts,"exact_anchor_improvement":exact_improves,"novel_material_drift":novel_degrades,"false_reassurance":bool(exact_improves and novel_degrades)}

def run_regime(regime:str,trials:int,seed:int)->dict[str,Any]:
    summaries=[summarize_trial(generate_trial(seed+t*1009,regime)) for t in range(trials)]
    return {"regime":regime,"trials":trials,"mean_shifts":{c:statistics.fmean(s["shifts"][c] for s in summaries) for c in ITEM_CLASSES},"exact_anchor_improvement_rate":statistics.fmean(s["exact_anchor_improvement"] for s in summaries),"novel_material_drift_rate":statistics.fmean(s["novel_material_drift"] for s in summaries),"false_reassurance_rate":statistics.fmean(s["false_reassurance"] for s in summaries)}

def compact_run(trials:int=250,seed:int=20260725)->dict[str,Any]:
    started=time.time(); results=[run_regime(regime,trials,seed+i*100000) for i,regime in enumerate(REGIMES)]
    payload={"schema_version":"egc2-anchor-memory-calibration-0.1.0","scope":"synthetic falsification sensitivity analysis","seed":seed,"trials_per_regime":trials,"python_version":platform.python_version(),"runtime_seconds":round(time.time()-started,3),"results":results}
    payload["content_sha256"]=canonical_hash(payload); return payload

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--trials",type=int,default=250); p.add_argument("--seed",type=int,default=20260725); p.add_argument("--output",type=Path,default=Path("research/egc2/results/anchor_memory_compact.json")); a=p.parse_args()
    if a.trials<20: print("trials >=20 required",file=sys.stderr); return 2
    payload=compact_run(a.trials,a.seed); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,indent=2)+"\n"); print(json.dumps(payload,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

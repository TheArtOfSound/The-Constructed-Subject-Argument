from __future__ import annotations
import argparse, json, math, random, statistics
from dataclasses import dataclass, asdict
from typing import Iterable

CLASSES=("exact_anchor","surface_variant","structural_transfer","novel")
DOMAINS=("autobiographical","conceptual","position","heldout")

@dataclass(frozen=True)
class Design:
    design_id:str; raters:int; items_per_class:int; ratings_per_item:int
    @property
    def planned_ratings(self)->int: return len(CLASSES)*self.items_per_class*self.ratings_per_item

DESIGNS=(
 Design("complete_8x18_r8",8,18,8), Design("incomplete_12x36_r4",12,36,4),
 Design("incomplete_12x24_r6",12,24,6), Design("complete_12x12_r12",12,12,12),
 Design("incomplete_16x24_r6",16,24,6),)

TRUTH={
 "global_stability": {c:0.0 for c in CLASSES},
 "false_reassurance": {"exact_anchor":0.45,"surface_variant":0.12,"structural_transfer":-0.30,"novel":-0.50},
}

def clip_score(x:float)->float: return min(7.0,max(1.0,x))

def balanced_raters(rng:random.Random, n:int, k:int, item_index:int)->list[int]:
    start=(item_index*k)%n
    ids=[(start+j)%n for j in range(k)]
    rng.shuffle(ids)
    return ids

def simulate(design:Design, truth_name:str, seed:int, item_sd:float=0.6, ambiguity_sd:float=0.35,
             rater_sd:float=0.5, domain_interaction_sd:float=0.25, ceiling_limited:bool=False,
             dropout:str="none") -> dict:
    if truth_name not in TRUTH: raise ValueError("unknown truth")
    if design.planned_ratings != 576: raise ValueError("design budget must equal 576")
    rng=random.Random(seed)
    base=6.2 if ceiling_limited else 4.0
    rater_eff=[rng.gauss(0,rater_sd) for _ in range(design.raters)]
    rd={(r,d):rng.gauss(0,domain_interaction_sd) for r in range(design.raters) for d in DOMAINS}
    rows=[]; latent_truth=[]
    for ci,c in enumerate(CLASSES):
        for i in range(design.items_per_class):
            d=DOMAINS[i%len(DOMAINS)]
            item=rng.gauss(0,item_sd); amb=rng.gauss(0,ambiguity_sd)
            early=base+item+amb
            late=early+TRUTH[truth_name][c]
            latent_truth.append((c,d,late-early))
            for r in balanced_raters(rng,design.raters,design.ratings_per_item,ci*design.items_per_class+i):
                if dropout=="severity" and rater_eff[r]>0.45 and rng.random()<0.30: continue
                noise_e=rng.gauss(0,0.55); noise_l=rng.gauss(0,0.55)
                rows.append({"class":c,"domain":d,"item":f"{c}:{i}","rater":r,
                    "early":clip_score(early+rater_eff[r]+rd[(r,d)]+noise_e),
                    "late":clip_score(late+rater_eff[r]+rd[(r,d)]+noise_l)})
    return {"design":asdict(design),"truth":truth_name,"rows":rows,"latent_truth":latent_truth}

def mean(xs:Iterable[float])->float:
    xs=list(xs); return statistics.fmean(xs) if xs else math.nan

def estimate(data:dict)->dict:
    rows=data["rows"]
    shifts={c:mean(r["late"]-r["early"] for r in rows if r["class"]==c) for c in CLASSES}
    contrast=shifts["exact_anchor"]-mean([shifts["structural_transfer"],shifts["novel"]])
    false_reassurance = shifts["exact_anchor"]>0.20 and shifts["novel"]<-0.20 and shifts["structural_transfer"]<-0.20
    item_means={}
    for r in rows: item_means.setdefault(r["item"],[]).append(r["late"]-r["early"])
    heldout=[mean(v) for k,v in item_means.items() if next(x for x in rows if x["item"]==k)["domain"]=="heldout"]
    nonheld=[mean(v) for k,v in item_means.items() if next(x for x in rows if x["item"]==k)["domain"]!="heldout"]
    latent={c:mean(v for cc,d,v in data["latent_truth"] if cc==c) for c in CLASSES}
    return {"class_shifts":shifts,"false_reassurance_supported":false_reassurance,
            "contrast":contrast,"item_population_error":abs(contrast-(latent["exact_anchor"]-mean([latent["structural_transfer"],latent["novel"]]))),
            "heldout_domain_gap":abs(mean(heldout)-mean(nonheld)),"observed_rows":len(rows)}

def run_grid(trials:int=100, seed:int=20260725)->dict:
    out={"seed":seed,"trials":trials,"cells":[]}
    for d in DESIGNS:
        for truth in ("global_stability","false_reassurance"):
            for item_sd in (0.25,1.0):
                for dropout in ("none","severity"):
                    vals=[]
                    for t in range(trials):
                        vals.append(estimate(simulate(d,truth,seed+t+100000*DESIGNS.index(d)+10000*(truth=="false_reassurance")+1000*(item_sd>0.5)+100*(dropout=="severity"),item_sd=item_sd,dropout=dropout)))
                    out["cells"].append({"design_id":d.design_id,"truth":truth,"item_sd":item_sd,"dropout":dropout,
                        "false_reassurance_rate":mean(v["false_reassurance_supported"] for v in vals),
                        "mean_item_population_error":mean(v["item_population_error"] for v in vals),
                        "mean_heldout_domain_gap":mean(v["heldout_domain_gap"] for v in vals),
                        "mean_observed_rows":mean(v["observed_rows"] for v in vals)})
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument("--trials",type=int,default=100); p.add_argument("--seed",type=int,default=20260725); p.add_argument("--output")
    a=p.parse_args(); result=run_grid(a.trials,a.seed); text=json.dumps(result,indent=2,sort_keys=True)
    if a.output: open(a.output,"w",encoding="utf-8").write(text+"\n")
    else: print(text)
if __name__=="__main__": main()

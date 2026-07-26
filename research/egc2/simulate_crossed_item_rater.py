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
            item_id=f"{c}:{i}"
            latent_truth.append((c,d,late-early))
            for r in balanced_raters(rng,design.raters,design.ratings_per_item,ci*design.items_per_class+i):
                if dropout=="severity" and rater_eff[r]>0.45 and rng.random()<0.30: continue
                noise_e=rng.gauss(0,0.55); noise_l=rng.gauss(0,0.55)
                rows.append({"class":c,"domain":d,"item":item_id,"rater":r,
                    "early":clip_score(early+rater_eff[r]+rd[(r,d)]+noise_e),
                    "late":clip_score(late+rater_eff[r]+rd[(r,d)]+noise_l)})
    return {"design":asdict(design),"truth":truth_name,"rows":rows,"latent_truth":latent_truth}

def mean(xs:Iterable[float])->float:
    xs=list(xs); return statistics.fmean(xs) if xs else math.nan

def weighted_mean(pairs:Iterable[tuple[float,float]])->float:
    total=0.0; weight=0.0
    for value,w in pairs:
        total += value*w; weight += w
    return total/weight if weight else math.nan

def percentile(values:list[float], p:float)->float:
    if not values: return math.nan
    xs=sorted(values)
    pos=(len(xs)-1)*p
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi: return xs[lo]
    return xs[lo]+(xs[hi]-xs[lo])*(pos-lo)

def _point_metrics(rows:list[dict], weights:list[float]|None=None)->dict:
    if weights is not None and len(weights)!=len(rows): raise ValueError("weights must match rows")
    shifts={}
    for c in CLASSES:
        if weights is None:
            shifts[c]=mean(r["late"]-r["early"] for r in rows if r["class"]==c)
        else:
            shifts[c]=weighted_mean((r["late"]-r["early"],w) for r,w in zip(rows,weights) if r["class"]==c)
    contrast=shifts["exact_anchor"]-mean([shifts["structural_transfer"],shifts["novel"]])
    false_reassurance = shifts["exact_anchor"]>0.20 and shifts["novel"]<-0.20 and shifts["structural_transfer"]<-0.20
    return {"class_shifts":shifts,"contrast":contrast,"false_reassurance_supported":false_reassurance}

def _resample_clusters(rows:list[dict], key:str, rng:random.Random)->list[dict]:
    clusters={}
    for row in rows: clusters.setdefault(row[key],[]).append(row)
    ids=sorted(clusters, key=str)
    if not ids: return []
    sampled=[rng.choice(ids) for _ in ids]
    out=[]
    for draw_index, cluster_id in enumerate(sampled):
        for row in clusters[cluster_id]:
            copy=dict(row)
            copy[f"bootstrap_{key}_draw"]=draw_index
            out.append(copy)
    return out

def _multinomial_cluster_counts(ids:list, rng:random.Random)->dict:
    counts={cluster_id:0 for cluster_id in ids}
    for _ in ids: counts[rng.choice(ids)] += 1
    return counts

def _pigeonhole_draw(rows:list[dict], rng:random.Random)->float:
    """Independent multinomial weights for item and rater clusters.

    Each observed row receives the product of its sampled item and rater counts.
    This is a two-way/pigeonhole bootstrap diagnostic for crossed dependence; it
    is not asserted to be exact for this sparse, unbalanced ordinal design.
    """
    item_ids=sorted({r["item"] for r in rows},key=str)
    rater_ids=sorted({r["rater"] for r in rows},key=str)
    if not item_ids or not rater_ids: return math.nan
    item_counts=_multinomial_cluster_counts(item_ids,rng)
    rater_counts=_multinomial_cluster_counts(rater_ids,rng)
    weights=[item_counts[r["item"]]*rater_counts[r["rater"]] for r in rows]
    return _point_metrics(rows,weights)["contrast"]

def cluster_bootstrap_intervals(data:dict, samples:int=500, seed:int=20260725)->dict:
    if samples < 1: raise ValueError("samples must be positive")
    rows=data["rows"]
    result={}
    for key,offset in (("item",0),("rater",1_000_000)):
        rng=random.Random(seed+offset)
        draws=[_point_metrics(_resample_clusters(rows,key,rng))["contrast"] for _ in range(samples)]
        result[key]={"samples":samples,"ci95":[percentile(draws,0.025),percentile(draws,0.975)],
                     "mean":mean(draws),"width":percentile(draws,0.975)-percentile(draws,0.025)}
    rng=random.Random(seed+2_000_000)
    draws=[_pigeonhole_draw(rows,rng) for _ in range(samples)]
    result["pigeonhole"]={"samples":samples,"ci95":[percentile(draws,0.025),percentile(draws,0.975)],
        "mean":mean(draws),"width":percentile(draws,0.975)-percentile(draws,0.025),
        "method_note":"independent multinomial item and rater weights; diagnostic, not yet publication-validated"}
    return result

def leave_one_domain_out(data:dict, materiality_threshold:float=0.10)->dict:
    if materiality_threshold < 0: raise ValueError("materiality_threshold must be nonnegative")
    rows=data["rows"]
    full=_point_metrics(rows)["contrast"]
    estimates={}; changes={}
    for domain in DOMAINS:
        kept=[r for r in rows if r["domain"]!=domain]
        estimates[domain]=_point_metrics(kept)["contrast"]
        changes[domain]=estimates[domain]-full
    vals=list(estimates.values()); abs_changes={d:abs(v) for d,v in changes.items()}
    max_domain=max(abs_changes,key=abs_changes.get)
    sign_changes=any((v>0)!=(full>0) for v in vals if v!=0 and full!=0)
    material_domains=[d for d,v in abs_changes.items() if v>=materiality_threshold]
    material_sign_reversal=any(
        abs(changes[d])>=materiality_threshold and estimates[d]*full<0
        for d in DOMAINS if full!=0 and estimates[d]!=0)
    return {"full_contrast":full,"omitted_domain_contrasts":estimates,
            "omission_changes":changes,"absolute_omission_changes":abs_changes,
            "min":min(vals),"max":max(vals),"range":max(vals)-min(vals),
            "sign_changes":sign_changes,"materiality_threshold":materiality_threshold,
            "max_absolute_change":abs_changes[max_domain],"most_influential_domain":max_domain,
            "material_influence_domains":material_domains,"material_influence":bool(material_domains),
            "material_sign_reversal":material_sign_reversal}

def estimate(data:dict, bootstrap_samples:int=0, seed:int=20260725, domain_threshold:float=0.10)->dict:
    rows=data["rows"]
    point=_point_metrics(rows)
    item_means={}; item_domains={}
    for r in rows:
        item_means.setdefault(r["item"],[]).append(r["late"]-r["early"])
        item_domains[r["item"]]=r["domain"]
    heldout=[mean(v) for k,v in item_means.items() if item_domains[k]=="heldout"]
    nonheld=[mean(v) for k,v in item_means.items() if item_domains[k]!="heldout"]
    latent={c:mean(v for cc,d,v in data["latent_truth"] if cc==c) for c in CLASSES}
    out={**point,
         "item_population_error":abs(point["contrast"]-(latent["exact_anchor"]-mean([latent["structural_transfer"],latent["novel"]]))),
         "heldout_domain_gap":abs(mean(heldout)-mean(nonheld)),"observed_rows":len(rows),
         "leave_one_domain_out":leave_one_domain_out(data,domain_threshold)}
    if bootstrap_samples: out["cluster_bootstrap"]=cluster_bootstrap_intervals(data,bootstrap_samples,seed)
    return out

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
                        "mean_lodo_range":mean(v["leave_one_domain_out"]["range"] for v in vals),
                        "lodo_sign_change_rate":mean(v["leave_one_domain_out"]["sign_changes"] for v in vals),
                        "lodo_material_influence_rate":mean(v["leave_one_domain_out"]["material_influence"] for v in vals),
                        "mean_observed_rows":mean(v["observed_rows"] for v in vals)})
    return out

def run_bootstrap_diagnostic(trials:int=100, bootstrap_samples:int=200, seed:int=20260725,
                             domain_threshold:float=0.10)->dict:
    out={"seed":seed,"trials":trials,"bootstrap_samples":bootstrap_samples,
         "domain_materiality_threshold":domain_threshold,"cells":[]}
    for di,d in enumerate(DESIGNS):
        for truth in ("global_stability","false_reassurance"):
            vals=[]
            for t in range(trials):
                s=seed+t+100000*di+10000*(truth=="false_reassurance")
                e=estimate(simulate(d,truth,s,item_sd=1.0,dropout="severity"),bootstrap_samples,s+9_000_000,domain_threshold)
                vals.append(e)
            true_contrast=TRUTH[truth]["exact_anchor"]-mean([TRUTH[truth]["structural_transfer"],TRUTH[truth]["novel"]])
            def covers(v,key):
                lo,hi=v["cluster_bootstrap"][key]["ci95"]
                return lo<=true_contrast<=hi
            out["cells"].append({"design_id":d.design_id,"truth":truth,"item_sd":1.0,"dropout":"severity",
                "item_bootstrap_coverage":mean(covers(v,"item") for v in vals),
                "rater_bootstrap_coverage":mean(covers(v,"rater") for v in vals),
                "pigeonhole_bootstrap_coverage":mean(covers(v,"pigeonhole") for v in vals),
                "mean_item_ci_width":mean(v["cluster_bootstrap"]["item"]["width"] for v in vals),
                "mean_rater_ci_width":mean(v["cluster_bootstrap"]["rater"]["width"] for v in vals),
                "mean_pigeonhole_ci_width":mean(v["cluster_bootstrap"]["pigeonhole"]["width"] for v in vals),
                "false_reassurance_rate":mean(v["false_reassurance_supported"] for v in vals),
                "mean_lodo_range":mean(v["leave_one_domain_out"]["range"] for v in vals),
                "lodo_sign_change_rate":mean(v["leave_one_domain_out"]["sign_changes"] for v in vals),
                "lodo_material_influence_rate":mean(v["leave_one_domain_out"]["material_influence"] for v in vals),
                "lodo_material_sign_reversal_rate":mean(v["leave_one_domain_out"]["material_sign_reversal"] for v in vals),
                "mean_lodo_max_absolute_change":mean(v["leave_one_domain_out"]["max_absolute_change"] for v in vals),
                "mean_observed_rows":mean(v["observed_rows"] for v in vals)})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--trials",type=int,default=100); p.add_argument("--seed",type=int,default=20260725)
    p.add_argument("--bootstrap-samples",type=int,default=0); p.add_argument("--domain-threshold",type=float,default=0.10)
    p.add_argument("--diagnostic",action="store_true"); p.add_argument("--output")
    a=p.parse_args()
    result=run_bootstrap_diagnostic(a.trials,a.bootstrap_samples or 200,a.seed,a.domain_threshold) if a.diagnostic else run_grid(a.trials,a.seed)
    text=json.dumps(result,indent=2,sort_keys=True)
    if a.output: open(a.output,"w",encoding="utf-8").write(text+"\n")
    else: print(text)
if __name__=="__main__": main()

#!/usr/bin/env python3
"""Create concealed rater session order and audit dropout robustness for EGC 2.0."""
from __future__ import annotations
import argparse, hashlib, json, random
from collections import defaultdict, deque
from itertools import combinations
from pathlib import Path
from typing import Any

class ScheduleError(ValueError): pass

def canonical_hash(payload: Any) -> str:
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def _round_robin_primary(rows: list[dict[str,Any]], rng: random.Random, priority_ids:set[str]) -> list[dict[str,Any]]:
    by_domain=defaultdict(list)
    for row in rows: by_domain[row["prompt_domain"]].append(row)
    priority_rows=[]
    for domain in by_domain:
        rng.shuffle(by_domain[domain])
        keep=[]
        for row in by_domain[domain]:
            (priority_rows if row["response_id"] in priority_ids else keep).append(row)
        by_domain[domain]=keep
    rng.shuffle(priority_rows)
    domains=list(sorted(by_domain)); rng.shuffle(domains)
    result=list(priority_rows); last=(result[-1]["prompt_domain"] if result else None)
    while any(by_domain.values()):
        choices=[d for d in domains if by_domain[d] and d!=last] or [d for d in domains if by_domain[d]]
        expected=domains[len(result)%len(domains)]
        d=min(choices,key=lambda x:0 if x==expected else 1)
        result.append(by_domain[d].pop(0)); last=d
    return result

def _insert_anchors_evenly(primary:list[dict[str,Any]], anchors:list[dict[str,Any]]) -> list[dict[str,Any]]:
    if not anchors: return list(primary)
    total=len(primary)+len(anchors)
    anchor_positions={round((i+0.5)*total/len(anchors)-0.5) for i in range(len(anchors))}
    while len(anchor_positions)<len(anchors):
        for p in range(total):
            if p not in anchor_positions:
                anchor_positions.add(p)
                if len(anchor_positions)==len(anchors): break
    positions=sorted(anchor_positions)[:len(anchors)]; aset=set(positions)
    out=[]; pi=ai=0
    for pos in range(total):
        if pos in aset: out.append(anchors[ai]); ai+=1
        else: out.append(primary[pi]); pi+=1
    return out

def _opaque_id(seed:int,rater_id:str,index:int)->str:
    return hashlib.sha256(f"{seed}|{rater_id}|{index}".encode()).hexdigest()[:16]

def schedule_assignment(payload:dict[str,Any], seed:int=20260725, min_repeat_gap:int=18)->dict[str,Any]:
    if min_repeat_gap<1: raise ScheduleError("min_repeat_gap must be positive")
    by_rater={"primary":defaultdict(list),"anchors":defaultdict(list),"repeats":defaultdict(list)}
    for row in payload["assignments"]["primary"]: by_rater["primary"][row["rater_id"]].append(dict(row))
    for row in payload["assignments"]["anchors"]: by_rater["anchors"][row["rater_id"]].append(dict(row))
    for row in payload["assignments"]["blind_repeats"]: by_rater["repeats"][row["rater_id"]].append(dict(row))
    rater_queues={}; audit_rows=[]
    for offset,rater_id in enumerate(payload["design"]["rater_ids"]):
        rng=random.Random(seed+1009*offset)
        repeats=by_rater["repeats"][rater_id]
        priority={r["repeat_of_response_id"] for r in repeats}
        primary=_round_robin_primary(by_rater["primary"][rater_id],rng,priority)
        anchors=by_rater["anchors"][rater_id][:]; rng.shuffle(anchors)
        sequence=_insert_anchors_evenly(primary,anchors)
        for repeat in sorted(repeats,key=lambda x:x["repeat_of_response_id"]):
            src=next(i for i,x in enumerate(sequence) if x.get("response_id")==repeat["repeat_of_response_id"] and x["assignment_type"]=="primary_response")
            candidates=list(range(src+min_repeat_gap+1,len(sequence)+1))
            if not candidates: raise ScheduleError(f"cannot place repeat for {rater_id}:{repeat['repeat_of_response_id']} at gap {min_repeat_gap}")
            nonadj=[p for p in candidates if not (p>0 and sequence[p-1].get("assignment_type")=="blind_repeat")]
            sequence.insert((nonadj or candidates)[-1],repeat)
        public=[]
        for idx,row in enumerate(sequence):
            presentation_id=_opaque_id(seed,rater_id,idx)
            public.append({"presentation_id":presentation_id,"position":idx+1})
            audit={"presentation_id":presentation_id,"position":idx+1,"rater_id":rater_id,"assignment_type":row["assignment_type"]}
            if row["assignment_type"]=="anchor": audit["stimulus_ref"]=row["anchor_id"]
            else:
                audit.update({"stimulus_ref":row["response_id"],"participant_id":row["participant_id"],"prompt_domain":row["prompt_domain"],"condition":row["condition"]})
            if row["assignment_type"]=="blind_repeat": audit["repeat_of_response_id"]=row["repeat_of_response_id"]
            audit_rows.append(audit)
        rater_queues[rater_id]=public
    result={"schema_version":"egc2-rater-session-order-0.1.0","design":{"seed":seed,"min_repeat_gap":min_repeat_gap,"rater_facing_fields":["presentation_id","position"],"item_type_concealed":True},"rater_queues":rater_queues,"audit_schedule":audit_rows}
    result["validation"]=validate_schedule(payload,result)
    result["dropout_robustness"]=simulate_dropout(payload)
    result["content_sha256"]=canonical_hash({k:v for k,v in result.items() if k!="content_sha256"})
    return result

def _connected(nodes:list[str], edges:dict[str,set[str]])->bool:
    if not nodes: return False
    seen={nodes[0]}; q=deque([nodes[0]])
    while q:
        u=q.popleft()
        for v in edges.get(u,set()):
            if v not in seen: seen.add(v); q.append(v)
    return seen==set(nodes)

def simulate_dropout(payload:dict[str,Any])->dict[str,Any]:
    raters=payload["design"]["rater_ids"]; primary=payload["assignments"]["primary"]; results=[]
    for k in (0,1,2):
        for dropped in combinations(raters,k):
            remaining=[r for r in raters if r not in dropped]; by_response=defaultdict(set)
            for row in primary:
                if row["rater_id"] in remaining: by_response[row["response_id"]].add(row["rater_id"])
            edges={r:set() for r in remaining}
            for rs in by_response.values():
                for a,b in combinations(sorted(rs),2): edges[a].add(b); edges[b].add(a)
            counts=[len(rs) for rs in by_response.values()]
            results.append({"dropped":list(dropped),"remaining_raters":len(remaining),"connected_rater_graph":_connected(remaining,edges),"minimum_ratings_per_response":min(counts) if counts else 0,"responses_below_two_ratings":sum(c<2 for c in counts)})
    by_k={}
    for k in (0,1,2):
        rows=[r for r in results if len(r["dropped"])==k]
        by_k[str(k)]={"scenarios":len(rows),"all_connected":all(r["connected_rater_graph"] for r in rows),"minimum_remaining_ratings":min(r["minimum_ratings_per_response"] for r in rows),"scenarios_with_response_below_two":sum(r["responses_below_two_ratings"]>0 for r in rows)}
    return {"summary_by_dropout_count":by_k,"scenarios":results}

def validate_schedule(source:dict[str,Any], scheduled:dict[str,Any])->dict[str,Any]:
    errors=[]; warnings=[]; audit=scheduled["audit_schedule"]; gap=scheduled["design"]["min_repeat_gap"]
    expected=sum(len(source["assignments"][k]) for k in ("primary","anchors","blind_repeats"))
    if len(audit)!=expected: errors.append("ASSIGNMENT_COUNT_MISMATCH")
    if any(set(x)!={"presentation_id","position"} for q in scheduled["rater_queues"].values() for x in q): errors.append("RATER_QUEUE_LEAKS_ITEM_METADATA")
    for rater in source["design"]["rater_ids"]:
        rows=sorted((x for x in audit if x["rater_id"]==rater),key=lambda x:x["position"])
        pos_by_primary={x["stimulus_ref"]:x["position"] for x in rows if x["assignment_type"]=="primary_response"}
        for x in rows:
            if x["assignment_type"]=="blind_repeat":
                actual=x["position"]-pos_by_primary[x["repeat_of_response_id"]]
                if actual<gap: errors.append(f"REPEAT_GAP:{rater}:{x['repeat_of_response_id']}:{actual}")
                if actual<=0: errors.append(f"REPEAT_BEFORE_SOURCE:{rater}:{x['repeat_of_response_id']}")
        run=0
        for x in rows:
            run=run+1 if x["assignment_type"]=="anchor" else 0
            if run>2: errors.append(f"ANCHOR_RUN:{rater}")
        n=len(rows); counts=[0,0,0,0]
        for x in rows:
            if x["assignment_type"]=="anchor": counts[min(3,(x["position"]-1)*4//n)]+=1
        if max(counts)-min(counts)>2: warnings.append(f"ANCHOR_QUARTILE_IMBALANCE:{rater}:{counts}")
    return {"errors":sorted(set(errors)),"warnings":sorted(set(warnings)),"passed":not errors}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assignment",type=Path,default=Path("research/egc2/rater_pilot_assignment.v0.1.json"))
    p.add_argument("--output",type=Path,default=Path("research/egc2/rater_pilot_session_order.v0.1.json"))
    p.add_argument("--seed",type=int,default=20260725); p.add_argument("--min-repeat-gap",type=int,default=18)
    a=p.parse_args(); source=json.loads(a.assignment.read_text()); result=schedule_assignment(source,a.seed,a.min_repeat_gap)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"validation":result["validation"],"dropout":result["dropout_robustness"]["summary_by_dropout_count"]},indent=2))
    return 0 if result["validation"]["passed"] else 1
if __name__=="__main__": raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

CLASSES=("exact_recurring_anchor","surface_variant_anchor","structural_transfer_probe","novel_response")
DOMAINS=("domain_1","domain_2","domain_3","domain_4")
RATER_COUNT=12; ITEMS_PER_CLASS=24; RATINGS_PER_ITEM=6
OFFSET_FAMILIES=((0,1,2,6,7,8),(0,2,4,7,9,11))
DOMAIN_PATTERN=(3,2,1,3,3,1,0,3,2,0,2,2,3,2,1,0,0,1,3,2,1,0,0,1)

class DesignError(ValueError): pass

def canonical_hash(x:Any)->str:
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _block(start:int, offsets:tuple[int,...])->tuple[int,...]:
    return tuple(sorted((start+o)%RATER_COUNT for o in offsets))

def build_items(seed:int=20260726):
    raters=[f"R{i+1:02d}" for i in range(RATER_COUNT)]
    items=[]; assignments=[]; rng=random.Random(seed)
    for ci,item_class in enumerate(CLASSES):
        perm=raters[:]; rng.shuffle(perm)
        starts_by_family=[list(range(RATER_COUNT)) for _ in OFFSET_FAMILIES]
        idx=0
        for fi,offsets in enumerate(OFFSET_FAMILIES):
            for start in starts_by_family[fi]:
                item_id=f"M{ci+1}_{idx+1:03d}"; domain=DOMAINS[DOMAIN_PATTERN[idx]]
                selected=sorted(perm[i] for i in _block(start,offsets))
                items.append({"item_id":item_id,"item_class":item_class,"domain":domain,"block_family":f"F{fi+1}"})
                assignments += [{"item_id":item_id,"item_class":item_class,"domain":domain,"rater_id":r} for r in selected]
                idx+=1
    return items,assignments

def build_queues(assignments:list[dict[str,str]],seed:int):
    by=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for row in assignments: by[row['rater_id']][row['item_class']][row['domain']].append(row)
    public={}; audit={}
    for ri,rater in enumerate(sorted(by)):
        rng=random.Random(seed+1000+ri)
        pools={}
        for c in CLASSES:
            for d in DOMAINS:
                p=by[rater][c][d][:]
                if len(p)!=3: raise DesignError(f"load mismatch {rater}/{c}/{d}: {len(p)}")
                rng.shuffle(p); pools[(c,d)]=p
        seq=[]; prev=None
        for _round in range(3):
            class_order=list(CLASSES); domain_order=list(DOMAINS)
            rng.shuffle(class_order); rng.shuffle(domain_order)
            shifts=list(range(4)); rng.shuffle(shifts)
            for shift in shifts:
                cycle=[(class_order[i],domain_order[(i+shift)%4]) for i in range(4)]
                if cycle[0][0]==prev: cycle=cycle[1:]+cycle[:1]
                for c,d in cycle: seq.append(pools[(c,d)].pop())
                prev=cycle[-1][0]
        a=[]; p=[]
        for pos,row in enumerate(seq,1):
            pid=hashlib.sha256(f"{seed}|{rater}|{pos}|{row['item_id']}".encode()).hexdigest()[:20]
            a.append({"position":pos,"presentation_id":pid,**row})
            p.append({"position":pos,"presentation_id":pid,"item_id":row['item_id']})
        audit[rater]=a; public[rater]=p
    return public,audit

def _graph(rows:Iterable[dict[str,str]],active:set[str]):
    by=defaultdict(set)
    for row in rows:
        if row['rater_id'] in active: by[row['item_id']].add(row['rater_id'])
    g={r:set() for r in active}
    for rs in by.values():
        for a,b in itertools.combinations(sorted(rs),2): g[a].add(b); g[b].add(a)
    return g

def _connected(g):
    if not g:return True
    seen=set(); stack=[next(iter(g))]
    while stack:
        n=stack.pop()
        if n in seen:continue
        seen.add(n); stack.extend(g[n]-seen)
    return len(seen)==len(g)

def dropout_audit(assignments,raters):
    out={}; allr=set(raters)
    for k in (1,2):
        fails=[]; min_item=RATINGS_PER_ITEM; min_class_deg=RATER_COUNT; min_domain_deg=RATER_COUNT
        for dropped in itertools.combinations(raters,k):
            active=allr-set(dropped); kept=[r for r in assignments if r['rater_id'] in active]
            counts=Counter(r['item_id'] for r in kept); mi=min(counts.values()); min_item=min(min_item,mi)
            overall=_connected(_graph(kept,active)); cc=True; dc=True
            for c in CLASSES:
                g=_graph((r for r in kept if r['item_class']==c),active); cc &= _connected(g); min_class_deg=min(min_class_deg,min(map(len,g.values())))
            for d in DOMAINS:
                g=_graph((r for r in kept if r['domain']==d),active); dc &= _connected(g); min_domain_deg=min(min_domain_deg,min(map(len,g.values())))
            if mi < RATINGS_PER_ITEM-k or not overall or not cc or not dc:
                fails.append({"dropped":list(dropped),"minimum_item_ratings":mi,"overall_connected":overall,"all_classes_connected":cc,"all_domains_connected":dc})
        out[str(k)]={"scenario_count":len(list(itertools.combinations(raters,k))),"failure_count":len(fails),"minimum_remaining_ratings_per_item":min_item,"minimum_class_graph_degree":min_class_deg,"minimum_domain_graph_degree":min_domain_deg,"failures":fails}
    return out

def validate(payload):
    e=[]; A=payload['assignments']; I=payload['items']; raters=payload['design']['rater_ids']
    if len(I)!=96:e.append('ITEM_COUNT')
    if len(A)!=576:e.append('ASSIGNMENT_COUNT')
    if set(Counter(r['item_id'] for r in A).values())!={6}:e.append('RATINGS_PER_ITEM')
    for c in CLASSES:
        if sum(i['item_class']==c for i in I)!=24:e.append(f'ITEMS_PER_CLASS:{c}')
        for d in DOMAINS:
            if sum(i['item_class']==c and i['domain']==d for i in I)!=6:e.append(f'ITEMS_PER_CLASS_DOMAIN:{c}:{d}')
    for r in raters:
        rows=[x for x in A if x['rater_id']==r]
        if len(rows)!=48:e.append(f'RATER_LOAD:{r}')
        for c in CLASSES:
            if sum(x['item_class']==c for x in rows)!=12:e.append(f'CLASS_LOAD:{r}:{c}')
            for d in DOMAINS:
                if sum(x['item_class']==c and x['domain']==d for x in rows)!=3:e.append(f'CLASS_DOMAIN_LOAD:{r}:{c}:{d}')
        pub=payload['rater_queues'][r]; aud=payload['audit_schedule'][r]
        if len(pub)!=48 or len(aud)!=48:e.append(f'QUEUE_LENGTH:{r}')
        if any(set(x)-{'position','presentation_id','item_id'} for x in pub):e.append(f'PUBLIC_METADATA_LEAK:{r}')
        for start in range(0,48,4):
            chunk=aud[start:start+4]
            if set(x['item_class'] for x in chunk)!=set(CLASSES) or set(x['domain'] for x in chunk)!=set(DOMAINS):e.append(f'CYCLE_IMBALANCE:{r}:{start//4}')
    for k in ('1','2'):
        if payload['dropout_audit'][k]['failure_count']:e.append(f'DROPOUT_FAILURE:{k}')
    return sorted(set(e))

def generate(seed:int=20260726):
    items,A=build_items(seed); raters=[f"R{i+1:02d}" for i in range(RATER_COUNT)]; pub,aud=build_queues(A,seed)
    p={"schema_version":"egc2-monitoring-assignment-0.2.0","design":{"design_id":"incomplete_12x24_r6","seed":seed,"rater_ids":raters,"item_classes":list(CLASSES),"domains":list(DOMAINS),"items_per_class":24,"items_per_class_domain":6,"ratings_per_item":6,"items_per_rater_per_class":12,"items_per_rater_per_class_domain":3,"total_items_per_rater":48,"total_assignments":576,"construction":"two_cyclic_six_rater_block_families_per_class"},"items":items,"assignments":A,"rater_queues":pub,"audit_schedule":aud,"dropout_audit":dropout_audit(A,raters)}
    p['validation_errors']=validate(p); p['content_sha256']=canonical_hash({k:v for k,v in p.items() if k!='content_sha256'}); return p

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=20260726); ap.add_argument('--output',type=Path,default=Path('research/egc2/monitoring_assignment_12x24r6.v0.2.json')); a=ap.parse_args(); p=generate(a.seed); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(p,indent=2)+"\n"); print(json.dumps({"errors":p['validation_errors'],"sha256":p['content_sha256'],"dropout":p['dropout_audit']},indent=2)); return 1 if p['validation_errors'] else 0
if __name__=='__main__': raise SystemExit(main())

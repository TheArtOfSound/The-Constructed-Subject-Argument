#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

SCHEMA_VERSION='egc2-paired-analysis-input-0.1.0'
CONDITIONS=('A','B')
DISPOSITIONS={'retain_numeric_score','suppress_numeric_score_reference_inadequate','blind_adjudication_required','indeterminate_insufficient_review'}
HEX64=re.compile(r'^[a-f0-9]{64}$')

class AnalysisInputError(ValueError): pass

@dataclass(frozen=True)
class AnalysisPair:
    participant_id:str
    condition_a_score:float|None
    condition_b_score:float|None

def canonical_digest(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def record_commitment_payload(r):
    return {k:r.get(k) for k in ('participant_id','condition','adequacy_disposition','retained_score','source_record_digest_sha256','adequacy_decision_digest_sha256','decision_version','decision_locked_at_utc')}

def compute_record_digest(r): return canonical_digest(record_commitment_payload(r))

def dataset_commitment_payload(d):
    records=sorted(({**record_commitment_payload(r),'record_digest_sha256':r.get('record_digest_sha256')} for r in d.get('records',[])),key=lambda x:(str(x['participant_id']),str(x['condition'])))
    return {'schema_version':d.get('schema_version'),'study_id':d.get('study_id'),'analysis_plan_id':d.get('analysis_plan_id'),'source_export_digest_sha256':d.get('source_export_digest_sha256'),'condition_order':d.get('condition_order'),'locked_for_analysis':d.get('locked_for_analysis'),'analysis_locked_at_utc':d.get('analysis_locked_at_utc'),'records':records}

def compute_dataset_digest(d): return canonical_digest(dataset_commitment_payload(d))
def _hex(v): return isinstance(v,str) and bool(HEX64.fullmatch(v))
def _time(v):
    if not isinstance(v,str): return False
    try: p=datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return False
    return p.tzinfo is not None

def validate_analysis_input(d):
    e=[]
    if d.get('schema_version')!=SCHEMA_VERSION:e.append('invalid schema_version')
    for k in ('study_id','analysis_plan_id'):
        if not isinstance(d.get(k),str) or not d[k].strip():e.append(f'{k} must be non-empty')
    if d.get('condition_order')!=list(CONDITIONS):e.append("condition_order must equal ['A', 'B']")
    if d.get('locked_for_analysis') is not True:e.append('locked_for_analysis must be true')
    if not _time(d.get('analysis_locked_at_utc')):e.append('analysis_locked_at_utc invalid')
    if not _hex(d.get('source_export_digest_sha256')):e.append('source_export_digest_sha256 invalid')
    records=d.get('records')
    if not isinstance(records,list) or not records:e.append('records must be non-empty list');records=[]
    seen=set();sources=set();pc={};unresolved=suppressed=retained=0
    for i,r in enumerate(records):
        p=f'records[{i}]'
        if not isinstance(r,dict):e.append(f'{p} must be object');continue
        pid=r.get('participant_id');cond=r.get('condition')
        if not isinstance(pid,str) or not pid.strip():e.append(f'{p}.participant_id invalid');pid=f'<invalid-{i}>'
        if cond not in CONDITIONS:e.append(f'{p}.condition invalid');cond=str(cond)
        key=(pid,cond)
        if key in seen:e.append(f'duplicate participant-condition record {key}')
        seen.add(key);pc.setdefault(pid,set()).add(cond)
        disp=r.get('adequacy_disposition');score=r.get('retained_score')
        if disp not in DISPOSITIONS:e.append(f'{p}.adequacy_disposition invalid')
        if disp=='retain_numeric_score':
            if isinstance(score,bool) or not isinstance(score,(int,float)) or not 1<=float(score)<=7:e.append(f'{p}.retained_score must be numeric 1-7')
            retained+=1
        else:
            if score is not None:e.append(f'{p}.retained_score must be null unless retained')
            if disp=='suppress_numeric_score_reference_inadequate':suppressed+=1
            elif disp in {'blind_adjudication_required','indeterminate_insufficient_review'}:unresolved+=1
        sd=r.get('source_record_digest_sha256')
        if not _hex(sd):e.append(f'{p}.source_record_digest invalid')
        elif sd in sources:e.append(f'{p}.source_record_digest must be unique')
        else:sources.add(sd)
        if not _hex(r.get('adequacy_decision_digest_sha256')):e.append(f'{p}.adequacy_decision_digest invalid')
        if not isinstance(r.get('decision_version'),str) or not r['decision_version'].strip():e.append(f'{p}.decision_version invalid')
        if not _time(r.get('decision_locked_at_utc')):e.append(f'{p}.decision_locked_at_utc invalid')
        if r.get('record_digest_sha256')!=compute_record_digest(r):e.append(f'{p}.record_digest mismatch')
    for pid,obs in sorted(pc.items()):
        if obs!=set(CONDITIONS):e.append(f'participant {pid} must have exactly one record per condition')
    actual=compute_dataset_digest(d)
    if d.get('analysis_input_digest_sha256')!=actual:e.append('analysis_input_digest mismatch')
    if e:raise AnalysisInputError(json.dumps({'valid':False,'errors':e},indent=2))
    return {'valid':True,'participant_count':len(pc),'record_count':len(records),'retained_record_count':retained,'suppressed_record_count':suppressed,'unresolved_record_count':unresolved,'analysis_ready':unresolved==0,'analysis_input_digest_sha256':actual}

def build_analysis_pairs(d):
    s=validate_analysis_input(d)
    if not s['analysis_ready']:raise AnalysisInputError('analysis blocked until unresolved adequacy decisions are replaced by a new locked input version')
    by={}
    for r in d['records']:by.setdefault(r['participant_id'],{})[r['condition']]=r
    pairs=[]
    for pid in sorted(by):
        def val(c):
            r=by[pid][c]
            return float(r['retained_score']) if r['adequacy_disposition']=='retain_numeric_score' else None
        pairs.append({'participant_id':pid,'condition_a_score':val('A'),'condition_b_score':val('B')})
    return {'schema_version':'egc2-paired-analysis-consumption-0.1.0','study_id':d['study_id'],'analysis_plan_id':d['analysis_plan_id'],'analysis_input_digest_sha256':s['analysis_input_digest_sha256'],'participant_count':len(pairs),'pairs':pairs,'claim_limit':'Lineage and disposition consistency only; no source authentication, missing-score identification, construct validation, or EGC validation.'}

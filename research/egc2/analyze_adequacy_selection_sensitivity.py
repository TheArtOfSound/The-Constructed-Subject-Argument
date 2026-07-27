#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Any, Iterable
SCALE_MIN=1.0
SCALE_MAX=7.0
class SensitivityInputError(ValueError): pass
@dataclass(frozen=True)
class ConditionSummary:
    condition:str
    observed_count:int
    suppressed_count:int
    observed_sum:float
    @property
    def total_count(self): return self.observed_count+self.suppressed_count
    @property
    def observed_mean(self):
        if self.observed_count<=0: raise SensitivityInputError(f"{self.condition}: at least one observed outcome is required")
        return self.observed_sum/self.observed_count
    @property
    def retention_rate(self):
        if self.total_count<=0: raise SensitivityInputError(f"{self.condition}: total count must be positive")
        return self.observed_count/self.total_count
def _canonical_digest(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def _validate_condition(s:ConditionSummary)->None:
    if not s.condition: raise SensitivityInputError("condition name must be non-empty")
    if isinstance(s.observed_count,bool) or not isinstance(s.observed_count,int) or s.observed_count<=0: raise SensitivityInputError(f"{s.condition}: observed_count must be a positive integer")
    if isinstance(s.suppressed_count,bool) or not isinstance(s.suppressed_count,int) or s.suppressed_count<0: raise SensitivityInputError(f"{s.condition}: suppressed_count must be a nonnegative integer")
    if isinstance(s.observed_sum,bool) or not isinstance(s.observed_sum,(int,float)): raise SensitivityInputError(f"{s.condition}: observed_sum must be numeric")
    if not s.observed_count*SCALE_MIN <= float(s.observed_sum) <= s.observed_count*SCALE_MAX: raise SensitivityInputError(f"{s.condition}: observed_sum is incompatible with the 1-7 scale")
def condition_mean_bounds(s:ConditionSummary,*,missing_lower:float=SCALE_MIN,missing_upper:float=SCALE_MAX):
    _validate_condition(s)
    if not SCALE_MIN<=missing_lower<=missing_upper<=SCALE_MAX: raise SensitivityInputError("missing outcome bounds must lie within 1-7")
    n=s.total_count
    return ((s.observed_sum+s.suppressed_count*missing_lower)/n,(s.observed_sum+s.suppressed_count*missing_upper)/n)
def contrast_bounds(a:ConditionSummary,b:ConditionSummary,*,missing_lower:float=SCALE_MIN,missing_upper:float=SCALE_MAX):
    _validate_condition(a); _validate_condition(b)
    if a.condition==b.condition: raise SensitivityInputError("condition names must be distinct")
    al,au=condition_mean_bounds(a,missing_lower=missing_lower,missing_upper=missing_upper)
    bl,bu=condition_mean_bounds(b,missing_lower=missing_lower,missing_upper=missing_upper)
    lo,hi=bl-au,bu-al
    status="positive_sign_robust" if lo>0 else "negative_sign_robust" if hi<0 else "point_identified_zero" if lo==0 and hi==0 else "sign_not_robust"
    return {"contrast":f"{b.condition}-{a.condition}","observed_complete_case_delta":b.observed_mean-a.observed_mean,"worst_case_lower":lo,"worst_case_upper":hi,"sign_status":status,"contains_zero":lo<=0<=hi}
def gamma_sensitivity(a:ConditionSummary,b:ConditionSummary,gammas:Iterable[float]):
    _validate_condition(a); _validate_condition(b)
    out=[]; prev=-1.0
    for raw in gammas:
        if isinstance(raw,bool) or not isinstance(raw,(int,float)): raise SensitivityInputError("gamma values must be numeric")
        g=float(raw)
        if g<0 or g<prev: raise SensitivityInputError("gamma values must be nonnegative and nondecreasing")
        prev=g
        alo,ahi=max(SCALE_MIN,a.observed_mean-g),min(SCALE_MAX,a.observed_mean+g)
        blo,bhi=max(SCALE_MIN,b.observed_mean-g),min(SCALE_MAX,b.observed_mean+g)
        aml,amu=condition_mean_bounds(a,missing_lower=alo,missing_upper=ahi)
        bml,bmu=condition_mean_bounds(b,missing_lower=blo,missing_upper=bhi)
        lo,hi=bml-amu,bmu-aml
        status="positive_sign_robust" if lo>0 else "negative_sign_robust" if hi<0 else "point_identified_zero" if lo==0 and hi==0 else "sign_not_robust"
        out.append({"gamma":g,"condition_a_missing_mean_bounds":[alo,ahi],"condition_b_missing_mean_bounds":[blo,bhi],"contrast_lower":lo,"contrast_upper":hi,"sign_status":status})
    return out
def analyze(a:ConditionSummary,b:ConditionSummary,*,gammas:Iterable[float]=(0.0,0.5,1.0,2.0,3.0,6.0)):
    _validate_condition(a); _validate_condition(b)
    report={"schema_version":"egc2-adequacy-selection-sensitivity-0.1.0","estimand":f"mean({b.condition}) - mean({a.condition})","scale_bounds":[SCALE_MIN,SCALE_MAX],"conditions":{a.condition:{"observed_count":a.observed_count,"suppressed_count":a.suppressed_count,"total_count":a.total_count,"retention_rate":a.retention_rate,"observed_mean":a.observed_mean},b.condition:{"observed_count":b.observed_count,"suppressed_count":b.suppressed_count,"total_count":b.total_count,"retention_rate":b.retention_rate,"observed_mean":b.observed_mean}},"retention_rate_difference_b_minus_a":b.retention_rate-a.retention_rate,"complete_case_delta":b.observed_mean-a.observed_mean,"worst_case_bounds":contrast_bounds(a,b),"gamma_sensitivity":gamma_sensitivity(a,b,gammas),"claim_limit":"Bounds describe compatibility with suppressed outcomes under stated assumptions. They do not identify the missing-outcome distribution, remove selection bias, or validate EGC."}
    report["analysis_digest_sha256"]=_canonical_digest(report)
    return report

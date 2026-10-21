#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction
import json
import math
import sys
from pathlib import Path
from typing import Any

PROGRAM_ID = "CODE3"
PROGRAM_TITLE = "CODE 3 — META EQUILIBRIUM RELATIONAL VALIDATOR"
VERSION = "2.1.0"
PASS = "PASS"
FAIL = "FAIL"

@dataclass(frozen=True)
class ControlResult:
    control_id: str
    title: str
    status: str
    source: str
    operation: str
    output: str
    evidence: dict[str, Any]
    note: str

def ftxt(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def fraction_to_decimal_string(value: Fraction) -> str:
    """Format a terminating rational exactly using integer arithmetic only."""
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise ValueError("Fraction has no terminating Base-10 representation.")
    places = max(twos, fives)
    scaled = abs(value.numerator) * 2 ** (places - twos) * 5 ** (places - fives)
    sign = "-" if value < 0 else ""
    if places == 0:
        return sign + str(scaled)
    digits = str(scaled).zfill(places + 1)
    return (sign + digits[:-places] + "." + digits[-places:]).rstrip("0").rstrip(".")


def dec(x: Fraction) -> Decimal:
    """Construct an exact Decimal without context-dependent division."""
    return Decimal(fraction_to_decimal_string(x))


def exact_positional_difference(position: Fraction, anchor: Fraction) -> Fraction:
    return position - anchor


def exact_reconstruction(anchor: Fraction, difference: Fraction) -> Fraction:
    return anchor + difference


def exact_relative_quotient(position: Fraction, anchor: Fraction) -> Fraction:
    if anchor == 0:
        raise ZeroDivisionError("Relative quotient requires a nonzero anchor.")
    return position / anchor


def positional_order(position: Fraction, anchor: Fraction) -> str:
    return "ABOVE" if position > anchor else "BELOW" if position < anchor else "EQUAL"

def check(cid, title, source, operation, output, evidence, condition, note):
    return ControlResult(cid, title, PASS if condition else FAIL,
                         source, operation, output, evidence, note)

def t01():
    y, x = Fraction(3,4), Fraction(1,4)
    return check("C4_T01","PRIMARY COMPLEMENTARY CLOSURE",
        "P.B.F. exact differentiated relation: 3/4 <-> 1/4",
        "exact rational closure","3/4 + 1/4 = 1",
        {"Y":"3/4","X":"1/4","whole":ftxt(y+x)}, y+x==1,
        "The complementary P.B.F. relation closes exactly.")

def t02():
    a,b=Fraction(2,3),Fraction(3,2)
    return check("C4_T02","RECIPROCAL DIRECTION CONTROL",
        "P.B.F. directional reading: 2/3 <-> 3/2",
        "reciprocal inversion","(2/3) * (3/2) = 1",
        {"contained":"2/3","expanded":"3/2","closure":ftxt(a*b)},
        a*b==1 and Fraction(1,a)==b,
        "Direction changes; reciprocal closure is preserved.")

def t03():
    expanded=Fraction(3,2)
    normalized=expanded/Fraction(2,1)
    complement=1-normalized
    return check("C4_T03","BINARY NORMALIZATION CONTROL",
        "expanded reciprocal position 3/2 and binary whole 2",
        "(3/2) / 2","3/4 <-> 1/4",
        {"normalized":ftxt(normalized),"complement":ftxt(complement)},
        normalized==Fraction(3,4) and complement==Fraction(1,4),
        "Binary normalization returns the established P.B.F. proportion.")

def t04():
    return check("C4_T04","DIMENSIONAL PROJECTION CONTROL",
        "P.B.F. planar relation 3/4 <-> 1/4",
        "exact equivalent representation in an eight-position structural frame",
        "3/4 = 6/8 ; 1/4 = 2/8",
        {"Y_planar":"3/4","Y_eight":"6/8","X_planar":"1/4","X_eight":"2/8"},
        Fraction(3,4)==Fraction(6,8) and Fraction(1,4)==Fraction(2,8),
        "The representational frame changes; the exact proportions do not.")

def t05():
    whole=Fraction(6,8)+Fraction(2,8)
    return check("C4_T05","COMPLETE EIGHT-POSITION STRUCTURAL REFERENCE",
        "dimensional P.B.F. representation: 6/8 <-> 2/8",
        "complementary closure inside the eight-position frame",
        "6/8 + 2/8 = 8/8 = 1",
        {"Y":"6/8","X":"2/8","complete_reference":"8/8","whole":ftxt(whole)},
        whole==1,
        "No 3+3 construction is used. This is the exact dimensional P.B.F. representation.")

def t06():
    c,e=Fraction(6,9),Fraction(9,6)
    return check("C4_T06","DIRECTIONAL NUMERICAL REPRESENTATION",
        "P.B.F. reciprocal direction: 2/3 <-> 3/2",
        "directional numerical representation",
        "6/9 = 2/3 ; 9/6 = 3/2",
        {"contained_PBF":"2/3","contained_position":"6/9",
         "expanded_PBF":"3/2","expanded_position":"9/6",
         "reciprocal_closure":ftxt(c*e)},
        c==Fraction(2,3) and e==Fraction(3,2) and c*e==1,
        "6 and 9 are opposing directional numerical positions; they are not produced by counting X.")

def t07():
    positions={"expansion_direction":6,"center_scale_passage":7,
               "complete_circuit_reference":8,"contraction_direction":9}
    ok=positions=={"expansion_direction":6,"center_scale_passage":7,
                   "complete_circuit_reference":8,"contraction_direction":9}
    return check("C4_T07","FUNCTIONAL POSITION TYPE CONTROL",
        "established directional / center / structural position assignments",
        "typed positional registration",
        "6 = expansion ; 7 = center/scale-passage ; 8 = complete circuit ; 9 = contraction",
        positions,ok,
        "The assigned functions are registered without inventing another P.B.F. generator.")

def t08(r6,r7):
    ok=r6.status==PASS and r7.status==PASS
    return check("C4_T08","POSITION-7 CENTER / SCALE-PASSAGE LOCK",
        "established P.B.F. directional representation and functional position assignment",
        "retain position 7 as the established center/scale-passage position",
        "6 — 7 — 8 — 9 functional positional architecture",
        {"directional_control":r6.status,"position_control":r7.status,
         "expansion":6,"center_scale_passage":7,"complete_circuit":8,"contraction":9},
        ok,
        "No separate upstream position-7 generator is introduced.")

def t09(r8):
    p0=Fraction(7,1)
    p1=p0/Fraction(10,1)
    p2=p1/Fraction(10,1)
    p3=p2/Fraction(10,1)
    return check("C4_T09","BASE-10 INVERSE SCALE PROJECTION",
        "established center/scale-passage position 7",
        "three successive exact /10 scale displacements",
        "7 -> 0.7 -> 0.07 -> 0.007",
        {"upstream":r8.status,"step1":str(dec(p1)),"step2":str(dec(p2)),
         "step3":str(dec(p3)),"fraction":ftxt(p3)},
        r8.status==PASS and p3==Fraction(7,1000) and dec(p3)==Decimal("0.007"),
        "The coefficient 7 is preserved while its Base-10 scale position changes.")

def t10():
    seven=Fraction(7,1); projected=Fraction(7,1000)
    return check("C4_T10","FUNCTION / REPRESENTATION DISTINCTION",
        "7 and its Base-10 projected representation 0.007",
        "numerical distinction plus explicit scale relation",
        "7 != 0.007 ; 7 * 10^-3 = 0.007",
        {"numerically_equal":seven==projected,"projected":ftxt(seven/Fraction(1000,1))},
        seven!=projected and seven/Fraction(1000,1)==projected,
        "Scale projection is not ordinary numerical equality.")

def t11():
    r16=Fraction(1,2**52)
    steps=[r16]
    for _ in range(3): steps.append(steps[-1]*2)
    r15=steps[-1]; q=r15/r16
    spacing=math.nextafter(1.0,math.inf)-1.0
    eps=sys.float_info.epsilon
    return check("C4_T11","BINARY MACHINE-SCALE CROSSCHECK",
        "binary64 spacing at 1.0","three exact x2 binary scale steps",
        "2^-52 -> 2^-51 -> 2^-50 -> 2^-49 ; quotient = 8",
        {"steps":[ftxt(x) for x in steps],"quotient":ftxt(q),
         "runtime_epsilon":repr(eps),"nextafter_spacing":repr(spacing)},
        r15==Fraction(1,2**49) and q==8 and eps==2.0**-52 and spacing==eps,
        "Independent binary-scale crosscheck; it does not originate P.B.F.")

def positional_controls(projection: ControlResult, machine: ControlResult):
    """Compare exact outputs already calculated by T09 and T11."""
    pairs = [
        ("BASE10_SCALE", "C4_T09", Fraction(projection.evidence["step3"]),
         Fraction(projection.evidence["step2"])),
        ("BINARY_MACHINE_SCALE", "C4_T11", Fraction(machine.evidence["steps"][0]),
         Fraction(machine.evidence["steps"][-1])),
    ]
    observations = []
    for name, source_id, anchor, position in pairs:
        difference = exact_positional_difference(position, anchor)
        reconstructed = exact_reconstruction(anchor, difference)
        quotient = exact_relative_quotient(position, anchor)
        observations.append({
            "name": name, "source_control": source_id,
            "anchor": ftxt(anchor), "position": ftxt(position),
            "difference": ftxt(difference), "reconstructed": ftxt(reconstructed),
            "relative_quotient": ftxt(quotient),
            "order": positional_order(position, anchor),
            "anchor_decimal": fraction_to_decimal_string(anchor),
            "position_decimal": fraction_to_decimal_string(position),
            "difference_decimal": fraction_to_decimal_string(difference),
        })
    upstream_ok = projection.status == PASS and machine.status == PASS
    specifications = [
        ("C4_T13", "EXACT POSITIONAL DIFFERENCE", "position - anchor",
         all(Fraction(o["difference"]) + Fraction(o["anchor"]) == Fraction(o["position"]) for o in observations)),
        ("C4_T14", "EXACT ARITHMETIC RECONSTRUCTION", "anchor + difference = position",
         all(Fraction(o["reconstructed"]) == Fraction(o["position"]) for o in observations)),
        ("C4_T15", "EXACT RELATIVE QUOTIENT", "position / anchor",
         all(Fraction(o["relative_quotient"]) * Fraction(o["anchor"]) == Fraction(o["position"]) for o in observations)),
        ("C4_T16", "POSITIONAL ORDER", "compare calculated positions and difference signs",
         all(o["order"] == "ABOVE" and Fraction(o["difference"]) > 0 for o in observations)),
        ("C4_T17", "EXACT TERMINATING DECIMAL ROUNDTRIP", "integer decimal encoding -> exact rational reconstruction",
         all(Fraction(o[key + "_decimal"]) == Fraction(o[key])
             for o in observations for key in ("anchor", "position", "difference"))),
    ]
    return [check(cid, title, "Calculated outputs of C4_T09 and C4_T11", operation,
                  operation, {"pairs": observations}, upstream_ok and condition,
                  "Arithmetic consistency of calculated positions; no additional numerical continuation is generated.")
            for cid, title, operation, condition in specifications]


def t12(results):
    serialized=json.dumps([asdict(r) for r in results],ensure_ascii=False)
    forbidden=["0.0072973525692838015","2973525692838015"]
    present=[x for x in forbidden if x in serialized]
    provenance=all(r.source and r.operation and r.output for r in results)
    return check("C4_T12","GLOBAL ADMISSION / PROVENANCE CONTROL",
        "C4_T01 ... C4_T11 and C4_T13 ... C4_T17", "audit source -> operation -> output",
        "EXTERNAL_NUMERICAL_INPUT = NONE",
        {"provenance_complete":provenance,"retired_values_present":present},
        provenance and not present,
        "Checks recorded provenance fields and specified retired strings; this is not a general derivation proof.")

def run():
    rs=[]
    for fn in (t01,t02,t03,t04,t05,t06,t07):
        rs.append(fn())
    r8=t08(rs[5],rs[6]); rs.append(r8)
    rs.append(t09(r8))
    rs.append(t10())
    rs.append(t11())
    rs.extend(positional_controls(rs[8], rs[10]))
    rs.append(t12(rs))
    status="COMPLETE RELATIONAL LOCK" if all(r.status==PASS for r in rs) else "RELATIONAL BREAK"
    return rs,status

def control_text(rs,status):
    lines=[PROGRAM_TITLE,"="*78,f"Version: {VERSION}","","CONTROL RESULTS","-"*78]
    for r in rs:
        lines += [f"{r.control_id} — {r.title}",f"Status: {r.status}",
                  f"Source: {r.source}",f"Operation: {r.operation}",
                  f"Output: {r.output}",f"Note: {r.note}",""]
    lines += ["GLOBAL STATUS","-"*78,status,"","EXTERNAL_NUMERICAL_INPUT = NONE",""]
    return "\n".join(lines)

def report_text(rs,status):
    rows="\n".join(f"| `{r.control_id}` | {r.title} | **{r.status}** |" for r in rs)
    return f"""# {PROGRAM_TITLE}

**Version:** `{VERSION}`  
**Global status:** **{status}**

## Controls

| ID | Control | Status |
|---|---|---|
{rows}

## Functional chain

```text
P.B.F.
→ RECIPROCAL DIRECTION
→ BINARY NORMALIZATION
→ COMPLEMENTARY CLOSURE
→ DIMENSIONAL PROJECTION
→ COMPLETE EIGHT-POSITION STRUCTURAL REFERENCE
→ DIRECTIONAL NUMERICAL REPRESENTATION
→ CENTER / SCALE-PASSAGE POSITION
→ BASE-10 INVERSE SCALE PROJECTION
→ EXACT POSITIONAL DIFFERENCE / RECONSTRUCTION / QUOTIENT / ORDER
→ EXACT TERMINATING DECIMAL ROUNDTRIP
```

## Global result

```text
{status}
```

```text
EXTERNAL_NUMERICAL_INPUT = NONE
```
"""

def main():
    rs,status=run()
    out=Path(__file__).resolve().parent/"2. OUTPUT"
    out.mkdir(parents=True,exist_ok=True)
    (out/"CODE3_CONTROL.txt").write_text(control_text(rs,status),encoding="utf-8")
    (out/"CODE3_DATA.json").write_text(json.dumps({
        "program_id":PROGRAM_ID,"version":VERSION,"global_status":status,
        "external_numerical_input":"NONE","controls":[asdict(r) for r in rs]
    },indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"CODE3_REPORT.md").write_text(report_text(rs,status),encoding="utf-8")
    print(control_text(rs,status))
    return 0 if status=="COMPLETE RELATIONAL LOCK" else 1

if __name__=="__main__":
    raise SystemExit(main())

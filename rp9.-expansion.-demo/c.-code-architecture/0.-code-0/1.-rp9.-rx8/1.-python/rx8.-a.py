
# -*- coding: utf-8 -*-
# RP9_CODE_ID: C.0070
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     2. RP9. EXPANSION
#
# PYTHON CODE ID: RX8. A
# OFFICIAL CODE TITLE: RX8. RP9 RX8 GENEALOGICAL VALIDATOR
# =============================================================================

# RP9_RX8_GENEALOGICAL_VALIDATOR.py
# Version: 1.1.0
# Purpose:
# Validate Rx8 as a genealogical derivation chain.
# This script writes what is tested, how it is tested, why it is tested, and the final result.
# Output is written to both Markdown and JSON.

import json
import math
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path

PYTHON_CODE_ID = "RX8. A"
FILE_NAME = "RX8. A.py"
OFFICIAL_CODE_TITLE = "RX8. RP9 RX8 GENEALOGICAL VALIDATOR"
SCRIPT_VERSION = "1.1.0"

OUTPUT_DIR_NAME = "2. OUTPUT"
DATA_FILE = "RX8.A_DATA.json"
TRACE_FILE = "RX8.A_TRACE.json"
AUDIT_FILE = "RX8.A_AUDIT.json"
VERIFY_FILE = "RX8.A_VERIFY.json"
REPORT_FILE = "RX8.A_REPORT.md"
CONTROL_FILE = "RX8.A_CONTROL.txt"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def make_output_dir():
    out_dir = Path.cwd() / OUTPUT_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def write_text(path, content):
    path.write_text(content, encoding="utf-8")


def write_json(path, data):
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def fraction_to_text(value):
    if isinstance(value, Fraction):
        return str(value)
    return str(value)


def status_from_bool(value):
    if value:
        return "PASS"
    return "FAIL"


def make_record(step_id, title, what_is_tested, how_it_is_tested, why_it_is_tested, passed, final_result, data=None):
    return {
        "step_id": step_id,
        "title": title,
        "what_is_tested": what_is_tested,
        "how_it_is_tested": how_it_is_tested,
        "why_it_is_tested": why_it_is_tested,
        "status": status_from_bool(passed),
        "final_result": final_result,
        "data": data or {}
    }


def validate_first_relation():
    relation = {
        "id": "RELATION_ORIGIN_1",
        "layer": "RELATION",
        "name": "FIRST_RELATIONAL_DIFFERENTIATION",
        "left": Fraction(1, 3),
        "right": Fraction(2, 3),
        "total": Fraction(1, 1),
        "claim": "PRIMARY_ORIGIN_RELATION",
        "derived_from": None,
        "may_claim_origin": True
    }

    passed = (
        relation["left"] + relation["right"] == relation["total"]
        and relation["left"] == Fraction(1, 3)
        and relation["right"] == Fraction(2, 3)
        and relation["may_claim_origin"] is True
    )

    data = {
        "left": fraction_to_text(relation["left"]),
        "right": fraction_to_text(relation["right"]),
        "sum": fraction_to_text(relation["left"] + relation["right"]),
        "claim": relation["claim"],
        "may_claim_origin": relation["may_claim_origin"]
    }

    final_result = "First relation is locked as origin." if passed else "First relation failed origin validation."

    record = make_record(
        "1",
        "VERIFY_FIRST_RELATION_POSITION",
        "The first relation position 1/3 <-> 2/3.",
        "The script verifies that 1/3 + 2/3 = 1 and that this node alone may claim origin status.",
        "This prevents later representations from being mistaken for the first relation.",
        passed,
        final_result,
        data
    )

    return relation, record


def derive_first_representation(relation):
    representation = {
        "id": "REPRESENTATION_1",
        "layer": "REPRESENTATION",
        "name": "FIRST_FRACTAL_REPRESENTATION",
        "active": Fraction(3, 4),
        "reference": Fraction(1, 4),
        "total": Fraction(1, 1),
        "claim": "DERIVED_REPRESENTATION",
        "derived_from": relation["id"],
        "may_claim_origin": False
    }

    passed = (
        representation["active"] + representation["reference"] == representation["total"]
        and representation["derived_from"] == relation["id"]
        and representation["may_claim_origin"] is False
    )

    data = {
        "active": fraction_to_text(representation["active"]),
        "reference": fraction_to_text(representation["reference"]),
        "sum": fraction_to_text(representation["active"] + representation["reference"]),
        "derived_from": representation["derived_from"],
        "claim": representation["claim"],
        "may_claim_origin": representation["may_claim_origin"]
    }

    final_result = "First representation is derived and does not claim origin." if passed else "First representation failed derivation validation."

    record = make_record(
        "2",
        "DERIVE_FIRST_REPRESENTATION",
        "The first representation 1/4 <-> 3/4.",
        "The script verifies that 1/4 + 3/4 = 1 and that the representation is derived from RELATION_ORIGIN_1.",
        "This locks representation as after-construction, not as a new primary relation.",
        passed,
        final_result,
        data
    )

    return representation, record


def check_representation_does_not_create_new_relation(relation, representation):
    passed = (
        representation["derived_from"] == relation["id"]
        and representation["may_claim_origin"] is False
        and representation["claim"] != "PRIMARY_ORIGIN_RELATION"
    )

    data = {
        "origin_relation": relation["id"],
        "representation": representation["id"],
        "representation_claim": representation["claim"],
        "representation_may_claim_origin": representation["may_claim_origin"]
    }

    final_result = "Representation did not create a new primary relation." if passed else "Representation incorrectly introduced or claimed a new primary relation."

    return make_record(
        "3",
        "CHECK_NO_NEW_RELATION_CREATED",
        "Whether representation creates a new relation.",
        "The script checks that the representation remains derived, cannot claim origin, and does not use PRIMARY_ORIGIN_RELATION as its claim.",
        "This is the lock against circular self-confirmation and false origin transfer.",
        passed,
        final_result,
        data
    )


def validate_rx8_capsulation(representation):
    rx8 = {
        "id": "RX8_CAPSULATION_1",
        "layer": "RECONSTRUCTION",
        "name": "R_TIMES_8_CAPSULATION",
        "R": "symbolic_R_not_measured",
        "diameter_coefficient": Fraction(2, 1),
        "square_sides": 4,
        "perimeter_coefficient": Fraction(8, 1),
        "derived_from": representation["id"],
        "claim": "CAPSULATION_RECONSTRUCTION",
        "may_claim_origin": False
    }

    calculated_perimeter = rx8["diameter_coefficient"] * rx8["square_sides"]

    passed = (
        calculated_perimeter == rx8["perimeter_coefficient"]
        and rx8["perimeter_coefficient"] == Fraction(8, 1)
        and rx8["derived_from"] == representation["id"]
        and rx8["may_claim_origin"] is False
    )

    data = {
        "R_status": rx8["R"],
        "diameter": "2R",
        "square_sides": rx8["square_sides"],
        "calculated_perimeter": "8R",
        "perimeter_coefficient": fraction_to_text(rx8["perimeter_coefficient"]),
        "derived_from": rx8["derived_from"],
        "may_claim_origin": rx8["may_claim_origin"]
    }

    final_result = "Rx8 is validated as capsulation and reconstruction." if passed else "Rx8 capsulation failed validation."

    record = make_record(
        "4",
        "VALIDATE_RX8_CAPSULATION",
        "Rx8 as R x 8 capsulation.",
        "The script keeps R symbolic and verifies that four square sides of 2R create 8R without measuring R.",
        "This shows Rx8 as reconstruction of R, not as a new origin value.",
        passed,
        final_result,
        data
    )

    return rx8, record


def validate_residual_belongs_to_representation(representation):
    exact_ratio = Fraction(3, 4)
    exact_lock = Fraction(1, 4)

    ri_float = math.sqrt(3.0) / 2.0
    ratio_observed = ri_float * ri_float
    lock_observed = 1.0 - ratio_observed

    ratio_expected = float(exact_ratio)
    lock_expected = float(exact_lock)

    ratio_residual = ratio_observed - ratio_expected
    lock_residual = lock_observed - lock_expected
    symmetric_residual = math.isclose(ratio_residual + lock_residual, 0.0, rel_tol=0.0, abs_tol=1e-30)
    exact_relation_preserved = exact_ratio + exact_lock == Fraction(1, 1)

    residual = {
        "id": "RESIDUAL_1",
        "layer": "RESIDUAL",
        "name": "FLOAT_REPRESENTATION_RESIDUAL",
        "derived_from": representation["id"],
        "claim": "REPRESENTATION_TRACE",
        "may_claim_origin": False,
        "ratio_residual": ratio_residual,
        "lock_residual": lock_residual,
        "symmetric_residual": symmetric_residual
    }

    passed = (
        residual["derived_from"] == representation["id"]
        and residual["may_claim_origin"] is False
        and symmetric_residual is True
        and exact_relation_preserved is True
    )

    data = {
        "exact_ratio": fraction_to_text(exact_ratio),
        "exact_lock": fraction_to_text(exact_lock),
        "exact_sum": fraction_to_text(exact_ratio + exact_lock),
        "ratio_observed_float": format(ratio_observed, ".20e"),
        "lock_observed_float": format(lock_observed, ".20e"),
        "ratio_residual": format(ratio_residual, ".20e"),
        "lock_residual": format(lock_residual, ".20e"),
        "symmetric_residual": symmetric_residual,
        "residual_layer": residual["layer"],
        "derived_from": residual["derived_from"],
        "may_claim_origin": residual["may_claim_origin"]
    }

    final_result = "Residual is isolated to representation and exact relation remains unchanged." if passed else "Residual isolation failed."

    record = make_record(
        "5",
        "VALIDATE_RESIDUAL_LAYER",
        "Whether float residual belongs to representation.",
        "The script compares exact 3/4 and 1/4 against float-derived values and checks symmetric residual cancellation.",
        "This proves residual as representation trace, not as a mutation of the relation.",
        passed,
        final_result,
        data
    )

    return residual, record


def validate_no_ungrounded_later_origin(nodes):
    failures = []

    for node in nodes:
        if node["layer"] != "RELATION":
            if node.get("may_claim_origin") is True:
                failures.append({
                    "node_id": node["id"],
                    "reason": "Later layer claims origin."
                })
            if node.get("derived_from") is None:
                failures.append({
                    "node_id": node["id"],
                    "reason": "Later layer has no derivation source."
                })

    passed = len(failures) == 0

    data = {
        "checked_nodes": [node["id"] for node in nodes],
        "failures": failures
    }

    final_result = "No later layer introduced an ungrounded primary relation." if passed else "Ungrounded later relation detected."

    return make_record(
        "6",
        "FAIL_IF_LATER_LAYER_INTRODUCES_UNGROUNDED_RELATION",
        "Whether any later layer introduces an ungrounded origin relation.",
        "The script scans every non-relation node and fails if it claims origin or lacks a derivation source.",
        "This is the final lock: no after-construction may be promoted into origin.",
        passed,
        final_result,
        data
    )


def normalize_nodes_for_json(nodes):
    cleaned = []
    for node in nodes:
        item = {}
        for key, value in node.items():
            if isinstance(value, Fraction):
                item[key] = str(value)
            else:
                item[key] = value
        cleaned.append(item)
    return cleaned


def build_presentation(summary, records):
    lines = []
    lines.extend([
        "> [!info] **RP9. CODE IDENTITY**",
        "> ",
        "> - ### REPOSITORY: _**RP9. RH. Z0**_",
        ">     ",
        ">     - #### **2. RP9. EXPANSION**",
        ">",
        ">---",
        f"> - PYTHON CODE 🆔: **{PYTHON_CODE_ID}**",
        "> ",
        f"> - OFFICIAL CODE TITEL: **{OFFICIAL_CODE_TITLE}**",
        "> ",
        ">---",
        "",
        "# RP9 RX8 GENEALOGICAL VALIDATOR",
        "",
        "## FINAL RESULT",
        "",
        "```text",
        "STATUS: " + summary["global_status"],
        "PYTHON CODE ID: " + PYTHON_CODE_ID,
        "OFFICIAL CODE TITLE: " + OFFICIAL_CODE_TITLE,
        "VERSION: " + SCRIPT_VERSION,
    ])
    lines.append("GENERATED: " + summary["generated_at"])
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## WHAT IS TESTED")
    lines.append("")
    lines.append("The code tests whether the Rx8 chain is a genealogical derivation from the first relation, not a collection of new ungrounded relations.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## HOW IT IS TESTED")
    lines.append("")
    lines.append("Each layer is assigned an explicit status: RELATION, REPRESENTATION, RECONSTRUCTION, or RESIDUAL.")
    lines.append("")
    lines.append("The code returns FAIL if a later layer lacks a derivation source or attempts to claim origin status.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## WHY IT IS TESTED")
    lines.append("")
    lines.append("The purpose is to lock the principle relation before projection. Representation, Rx8, and residual may only be after-constructions of the first relation.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## CONTROL CHAIN")
    lines.append("")
    lines.append("```text")
    lines.append("R")
    lines.append("down")
    lines.append("first relation: 1/3 <-> 2/3")
    lines.append("down")
    lines.append("first representation: 1/4 <-> 3/4")
    lines.append("down")
    lines.append("Rx8: R x 8 capsulation")
    lines.append("down")
    lines.append("residual: representation trace")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## STEP RESULTS")
    lines.append("")
    lines.append("| Step | Title | What is tested | How it is tested | Why it is tested | Status | Final result |")
    lines.append("|---|---|---|---|---|---|---|")

    for record in records:
        row = (
            "| " + record["step_id"]
            + " | " + record["title"]
            + " | " + record["what_is_tested"]
            + " | " + record["how_it_is_tested"]
            + " | " + record["why_it_is_tested"]
            + " | " + record["status"]
            + " | " + record["final_result"]
            + " |"
        )
        lines.append(row)

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## CONCLUSION")
    lines.append("")
    if summary["global_status"] == "PASS":
        lines.append("PASS: The chain is locked. No later layer introduces a new ungrounded relation.")
    else:
        lines.append("FAIL: The chain is not locked. At least one later layer violated the derivation requirement.")
    lines.append("")
    return "\n".join(lines)


def build_log(records, out_dir, global_status):
    lines = []
    lines.append("RP9 RX8 GENEALOGICAL VALIDATOR LOG")
    lines.append("Generated: " + now_iso())
    lines.append("Python Code ID: " + PYTHON_CODE_ID)
    lines.append("Official Code Title: " + OFFICIAL_CODE_TITLE)
    lines.append("File: " + FILE_NAME)
    lines.append("Version: " + SCRIPT_VERSION)
    lines.append("Output directory: " + str(out_dir))
    lines.append("Global status: " + global_status)
    lines.append("")
    for record in records:
        lines.append(record["step_id"] + " | " + record["status"] + " | " + record["title"] + " | " + record["final_result"])
    lines.append("")
    return "\n".join(lines)


def run_validator():
    out_dir = make_output_dir()
    trace = []
    nodes = []

    relation, record_1 = validate_first_relation()
    trace.append(record_1)
    nodes.append(relation)

    representation, record_2 = derive_first_representation(relation)
    trace.append(record_2)
    nodes.append(representation)

    record_3 = check_representation_does_not_create_new_relation(relation, representation)
    trace.append(record_3)

    rx8, record_4 = validate_rx8_capsulation(representation)
    trace.append(record_4)
    nodes.append(rx8)

    residual, record_5 = validate_residual_belongs_to_representation(representation)
    trace.append(record_5)
    nodes.append(residual)

    record_6 = validate_no_ungrounded_later_origin(nodes)
    trace.append(record_6)

    global_pass = all(record["status"] == "PASS" for record in trace)
    global_status = status_from_bool(global_pass)

    summary = {
        "repository": "RP9. RH. Z0",
        "repository_branch": "2. RP9. EXPANSION",
        "python_code_id": PYTHON_CODE_ID,
        "filesystem_name": FILE_NAME,
        "official_code_title": OFFICIAL_CODE_TITLE,
        "version": SCRIPT_VERSION,
        "generated_at": now_iso(),
        "global_status": global_status,
        "what_is_tested": "Rx8 as a genealogical derivation from the first relation.",
        "how_it_is_tested": "Every later layer must be derived and must not claim origin status.",
        "why_it_is_tested": "To lock relation before projection and prevent after-constructions from becoming origin claims.",
        "final_result": "PASS means the genealogy is locked. FAIL means an ungrounded later relation was introduced."
    }

    data_payload = {
        "SUMMARY": summary,
        "NODES": normalize_nodes_for_json(nodes),
        "TRACE": trace
    }

    audit_payload = {
        "AUDIT": {
            "what_is_tested": "Audit of origin claims across all layers.",
            "how_it_is_tested": "Counts origin-capable relation nodes and checks later layers for illegal origin claims.",
            "why_it_is_tested": "Only the first relation may carry origin status.",
            "no_competing_relation_search": True,
            "genealogical_validation_only": True,
            "origin_relation_count_expected": 1,
            "origin_relation_count_observed": len([node for node in nodes if node["layer"] == "RELATION" and node.get("may_claim_origin") is True]),
            "later_origin_claims": [
                node["id"] for node in nodes
                if node["layer"] != "RELATION" and node.get("may_claim_origin") is True
            ],
            "global_status": global_status,
            "final_result": global_status
        }
    }

    verify_payload = {
        "VERIFY": {
            "what_is_tested": "Machine-readable final verification flags.",
            "how_it_is_tested": "Each step must return PASS for global PASS.",
            "why_it_is_tested": "This gives a direct audit surface for external review.",
            "first_relation_locked": record_1["status"] == "PASS",
            "first_representation_derived": record_2["status"] == "PASS",
            "representation_does_not_create_new_relation": record_3["status"] == "PASS",
            "rx8_is_capsulation": record_4["status"] == "PASS",
            "residual_belongs_to_representation": record_5["status"] == "PASS",
            "no_ungrounded_later_relation": record_6["status"] == "PASS",
            "global_status": global_status,
            "final_result": global_status
        }
    }

    write_json(out_dir / DATA_FILE, data_payload)
    write_json(out_dir / TRACE_FILE, {"TRACE": trace})
    write_json(out_dir / AUDIT_FILE, audit_payload)
    write_json(out_dir / VERIFY_FILE, verify_payload)

    presentation = build_presentation(summary, trace)
    write_text(out_dir / REPORT_FILE, presentation)

    log_text = build_log(trace, out_dir, global_status)
    write_text(out_dir / CONTROL_FILE, log_text)

    print("=" * 72)
    print("RP9 RX8 GENEALOGICAL VALIDATOR")
    print("WHAT IS TESTED: Rx8 as a genealogical derivation from the first relation.")
    print("HOW IT IS TESTED: every later layer must be derived and may not claim origin status.")
    print("WHY IT IS TESTED: relation before projection must be locked operationally.")
    print("FINAL RESULT:", global_status)
    print("OUTPUT:", out_dir)
    print("=" * 72)

    for record in trace:
        print(record["step_id"] + " | " + record["status"] + " | " + record["title"] + " | " + record["final_result"])

    print("=" * 72)

    if not global_pass:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = run_validator()
    sys.exit(exit_code)


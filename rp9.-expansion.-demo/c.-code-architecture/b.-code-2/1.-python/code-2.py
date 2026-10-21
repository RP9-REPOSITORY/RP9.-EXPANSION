# RP9_CODE_ID: C.0005
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     2. RP9. EXPANSION
#
# PYTHON CODE ID: CODE 2
# OFFICIAL CODE TITLE: CODE 2. RP9 RESIDUAL VALUE
# =============================================================================
# RP9_RESIDUAL_VALUE.py
# Version: 3.0.0
# File type: Python
# Purpose:
# - Self-contained verification of a binary machine-scale quotient around 1.0.
# - Measures actual IEEE-754 spacing with math.nextafter.
# - Verifies a three-step binary scale relation with exact quotient 8.
# - Keeps measured machine relations separate from downstream interpretation.
# - Uses Python standard library only.

import datetime
import hashlib
import json
import math
import platform
import sys
from pathlib import Path


PYTHON_CODE_ID = "CODE 2"
FILE_NAME = "CODE 2.py"
OFFICIAL_CODE_TITLE = "CODE 2. RP9 RESIDUAL VALUE"
SCRIPT_VERSION = "3.0.0"

OUTPUT_DIR_NAME = "2. OUTPUT"

OUTPUT_FILES = {
    "data": "CODE2_DATA.json",
    "trace": "CODE2_TRACE.json",
    "datasheet": "CODE2_FULL_DATASHEET.json",
    "presentation": "CODE2_REPORT.md",
    "control_log": "CODE2_CONTROL.txt",
    "verify": "CODE2_VERIFY.json",
}


def get_base_dir():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


BASE_DIR = get_base_dir()
OUTPUT_DIR = BASE_DIR / OUTPUT_DIR_NAME


def local_stamp():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def f20(value):
    return format(float(value), ".20e")


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return float(value)
    return value


def write_json(path, payload):
    path.write_text(json.dumps(json_safe(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path, text):
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def trace_step(index, layer, operation, formula, inputs, result, passed, note):
    return {
        "index": index,
        "timestamp_utc": utc_stamp(),
        "layer": layer,
        "operation": operation,
        "formula": formula,
        "inputs": inputs,
        "result": result,
        "status": "PASS" if passed else "FAIL",
        "note": note,
    }


def run_measurements():
    trace = []

    epsilon = sys.float_info.epsilon
    epsilon_expected = 2.0 ** -52
    epsilon_pass = epsilon == epsilon_expected

    trace.append(trace_step(
        1,
        "A_MACHINE_REFERENCE",
        "read_machine_reference",
        "epsilon = sys.float_info.epsilon = 2^-52",
        {},
        {
            "epsilon": f20(epsilon),
            "expected": f20(epsilon_expected),
            "power_relation": "2^-52",
        },
        epsilon_pass,
        "Establishes the machine-spacing reference used by the remaining controls.",
    ))

    next_1 = math.nextafter(1.0, math.inf)
    spacing_1 = next_1 - 1.0
    spacing_pass = spacing_1 == epsilon

    trace.append(trace_step(
        2,
        "B_ACTUAL_SPACING_AT_ONE",
        "measure_actual_spacing",
        "nextafter(1.0, +inf) - 1.0",
        {"reference_position": "1.0"},
        {
            "next_value": f20(next_1),
            "measured_spacing": f20(spacing_1),
            "machine_reference": f20(epsilon),
        },
        spacing_pass,
        "Measures the actual next representable binary64 position above 1.0.",
    ))

    r16 = spacing_1
    r15 = r16 * (2.0 ** 3)
    quotient = r15 / r16

    scale_pass = (
        r16 == 2.0 ** -52
        and r15 == 2.0 ** -49
        and quotient == 8.0
    )

    trace.append(trace_step(
        3,
        "C_THREE_STEP_BINARY_SCALE",
        "derive_three_step_scale",
        "R15 = R16 * 2^3 ; R15 / R16 = 2^3",
        {"r16": f20(r16), "binary_steps": 3},
        {
            "r16": f20(r16),
            "r16_power": "2^-52",
            "r15": f20(r15),
            "r15_power": "2^-49",
            "quotient": quotient,
        },
        scale_pass,
        "Derives the larger machine-scale position from three exact binary scale steps.",
    ))

    direct_quotient = (2.0 ** -49) / (2.0 ** -52)
    direct_pass = direct_quotient == 8.0

    trace.append(trace_step(
        4,
        "D_DIRECT_POWER_CROSSCHECK",
        "verify_power_quotient",
        "(2^-49) / (2^-52) = 2^3 = 8",
        {"lower_power": "2^-52", "upper_power": "2^-49"},
        {"quotient": direct_quotient, "expected": 8.0},
        direct_pass,
        "Cross-checks the measured scale relation directly from powers of two.",
    ))

    consecutive = []
    current = 1.0
    series_pass = True
    for index in range(1, 6):
        nxt = math.nextafter(current, math.inf)
        diff = nxt - current
        if diff != epsilon:
            series_pass = False
        consecutive.append({
            "step": index,
            "input": f20(current),
            "next": f20(nxt),
            "spacing": f20(diff),
        })
        current = nxt

    trace.append(trace_step(
        5,
        "E_CONSECUTIVE_POSITION_CONTROL",
        "measure_consecutive_positions",
        "repeat nextafter(x, +inf) from x = 1.0",
        {"start": "1.0", "steps": 5},
        {"series": consecutive, "constant_spacing_in_local_binade": series_pass},
        series_pass,
        "Confirms consecutive representable positions immediately above 1.0.",
    ))

    scale_positions = []
    actual_scale_pass = True
    for exp in range(-3, 4):
        value = 2.0 ** exp
        nxt = math.nextafter(value, math.inf)
        actual_spacing = nxt - value
        expected_spacing = epsilon * value
        relation_pass = actual_spacing == expected_spacing
        if not relation_pass:
            actual_scale_pass = False
        scale_positions.append({
            "position": f"2^{exp}",
            "value": f20(value),
            "next_value": f20(nxt),
            "actual_spacing": f20(actual_spacing),
            "expected_spacing": f20(expected_spacing),
            "spacing_relation_pass": relation_pass,
        })

    trace.append(trace_step(
        6,
        "F_SCALE_POSITION_CONTROL",
        "measure_spacing_across_binary_scale",
        "ULP(2^n) = epsilon * 2^n for selected normalized powers of two",
        {"range": "2^-3 through 2^3"},
        {"positions": scale_positions},
        actual_scale_pass,
        "Measures actual nextafter spacing at each selected binary scale position instead of using an estimate alone.",
    ))

    all_pass = all(step["status"] == "PASS" for step in trace)

    payload = {
        "script": {
            "repository": "RP9. RH. Z0",
            "repository_branch": "2. RP9. EXPANSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "version": SCRIPT_VERSION,
            "created_at_local": local_stamp(),
            "created_at_utc": utc_stamp(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": str(BASE_DIR),
            "output_directory": str(OUTPUT_DIR),
            "purpose": "Independent verification of binary machine-scale positions, exact scale quotient and actual IEEE-754 spacing.",
            "dependency_note": "Python standard library only. No external RP9 code dependency.",
        },
        "measurement": {
            "machine_reference": {
                "epsilon": f20(epsilon),
                "power_relation": "2^-52",
                "verified_against_power": epsilon_pass,
            },
            "position_r16": {
                "definition": "actual nextafter spacing above 1.0",
                "value": f20(r16),
                "power_relation": "2^-52",
            },
            "position_r15": {
                "definition": "R16 scaled upward by three binary steps",
                "value": f20(r15),
                "power_relation": "2^-49",
            },
            "scale_relation": {
                "binary_step_difference": 3,
                "formula": "R15 / R16 = 2^3",
                "quotient": quotient,
                "expected": 8.0,
                "passed": scale_pass,
            },
            "direct_power_crosscheck": {
                "formula": "(2^-49) / (2^-52)",
                "quotient": direct_quotient,
                "expected": 8.0,
                "passed": direct_pass,
            },
            "consecutive_positions": consecutive,
            "scale_positions": scale_positions,
            "total_status": "PASS" if all_pass else "FAIL",
        },
        "master_conclusion": {
            "chain": [
                "MACHINE REFERENCE AT 1.0",
                "ACTUAL NEXT REPRESENTABLE POSITION",
                "R16 = 2^-52",
                "THREE BINARY SCALE STEPS",
                "R15 = 2^-49",
                "EXACT SCALE QUOTIENT = 8",
                "ACTUAL SPACING CONTROL ACROSS SELECTED BINARY POSITIONS",
            ],
            "measurement_boundary": (
                "The code verifies machine spacing, binary scale position and quotient inside IEEE-754 binary64. "
                "It does not require Base 8, octal structure or another RP9 code as a premise."
            ),
            "interpretation_boundary": (
                "The measured quotient 8 is the result of three binary scale steps: 2^3 = 8. "
                "Any broader repository interpretation is downstream from this measured relation."
            ),
            "total_status": "PASS" if all_pass else "FAIL",
        },
        "audit": {
            "self_contained_execution": True,
            "external_rp9_code_dependency": False,
            "base_8_required_as_premise": False,
            "octal_structure_required_as_premise": False,
            "actual_nextafter_spacing_measured": True,
            "scale_estimate_used_as_substitute_for_measurement": False,
            "quotient_derived_from_binary_steps": quotient == 8.0,
            "all_pass_conditions_computed": True,
            "global_status": "PASS" if all_pass else "FAIL",
        },
    }

    return payload, trace


def build_presentation(payload, trace):
    m = payload["measurement"]
    lines = [
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
        "# RP9 RESIDUAL VALUE",
        "",
        "## Control Chain",
        "",
        "```text",
        "MACHINE REFERENCE AT 1.0",
        "↓",
        "ACTUAL NEXT REPRESENTABLE POSITION",
        "↓",
        "R16 = 2^-52",
        "↓",
        "THREE BINARY SCALE STEPS",
        "↓",
        "R15 = 2^-49",
        "↓",
        "R15 / R16 = 2^3 = 8",
        "↓",
        "ACTUAL SPACING CONTROL",
        "```",
        "",
        "## Measured Relation",
        "",
        f"- R16: `{m['position_r16']['value']}`",
        f"- R15: `{m['position_r15']['value']}`",
        f"- Binary step difference: `{m['scale_relation']['binary_step_difference']}`",
        f"- Quotient: `{m['scale_relation']['quotient']}`",
        "",
        "## Control Status",
        "",
        "| Layer | Status |",
        "|---|---|",
    ]
    for step in trace:
        lines.append(f"| {step['layer']} | `{step['status']}` |")

    lines.extend([
        "",
        f"**Total status:** `{m['total_status']}`",
        "",
        "## Measurement Boundary",
        "",
        payload["master_conclusion"]["measurement_boundary"],
        "",
        "## Interpretation Boundary",
        "",
        payload["master_conclusion"]["interpretation_boundary"],
    ])
    return "\n".join(lines)


def build_control_log(payload, trace):
    lines = [
        "RP9 RESIDUAL VALUE CONTROL LOG",
        "=" * 72,
        f"Python Code ID: {PYTHON_CODE_ID}",
        f"Official Code Title: {OFFICIAL_CODE_TITLE}",
        f"File: {FILE_NAME}",
        f"Version: {SCRIPT_VERSION}",
        f"Created local: {payload['script']['created_at_local']}",
        "",
        "VERIFIED CHAIN",
        "-" * 72,
    ]
    lines.extend(payload["master_conclusion"]["chain"])
    lines.extend(["", "TRACE", "-" * 72])

    for step in trace:
        lines.extend([
            f"STEP {step['index']:03d}",
            f"Layer: {step['layer']}",
            f"Operation: {step['operation']}",
            f"Formula: {step['formula']}",
            f"Status: {step['status']}",
            f"Note: {step['note']}",
            "",
        ])

    lines.extend([
        "FINAL STATUS",
        "-" * 72,
        payload["measurement"]["total_status"],
        "",
        "BOUNDARY",
        "-" * 72,
        payload["master_conclusion"]["measurement_boundary"],
        payload["master_conclusion"]["interpretation_boundary"],
    ])
    return "\n".join(lines)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_outputs(payload, trace):
    ensure_output_dir()

    data_path = OUTPUT_DIR / OUTPUT_FILES["data"]
    trace_path = OUTPUT_DIR / OUTPUT_FILES["trace"]
    datasheet_path = OUTPUT_DIR / OUTPUT_FILES["datasheet"]
    presentation_path = OUTPUT_DIR / OUTPUT_FILES["presentation"]
    control_path = OUTPUT_DIR / OUTPUT_FILES["control_log"]
    verify_path = OUTPUT_DIR / OUTPUT_FILES["verify"]

    write_json(data_path, payload)
    write_json(trace_path, trace)
    write_json(datasheet_path, {"payload": payload, "trace": trace})
    write_text(presentation_path, build_presentation(payload, trace))
    write_text(control_path, build_control_log(payload, trace))

    verify_targets = [data_path, trace_path, datasheet_path, presentation_path, control_path]
    verify = {
        "repository": "RP9. RH. Z0",
        "repository_branch": "2. RP9. EXPANSION",
        "python_code_id": PYTHON_CODE_ID,
        "filesystem_name": FILE_NAME,
        "official_code_title": OFFICIAL_CODE_TITLE,
        "version": SCRIPT_VERSION,
        "files": [
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in verify_targets
        ],
        "file_count": len(verify_targets) + 1,
        "status": payload["measurement"]["total_status"],
    }
    write_json(verify_path, verify)

    return {
        "data": data_path,
        "trace": trace_path,
        "datasheet": datasheet_path,
        "presentation": presentation_path,
        "control_log": control_path,
        "verify": verify_path,
    }


def print_summary(payload, paths):
    m = payload["measurement"]
    print("=" * 72)
    print("RP9 RESIDUAL VALUE")
    print("=" * 72)
    print("R16:", m["position_r16"]["value"])
    print("R15:", m["position_r15"]["value"])
    print("Binary steps:", m["scale_relation"]["binary_step_difference"])
    print("R15 / R16:", m["scale_relation"]["quotient"])
    print("Total status:", m["total_status"])
    print("=" * 72)
    print("FILES WRITTEN")
    for key, path in paths.items():
        print(f"{key}: {path}")


def main():
    payload, trace = run_measurements()
    paths = write_outputs(payload, trace)
    print_summary(payload, paths)
    return 0 if payload["measurement"]["total_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

# RP9_CODE_ID: C.0002
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     2. RP9. EXPANSION
#
# PYTHON CODE ID: CODE 1
# OFFICIAL CODE TITLE: CODE 1. RP9 FIRST DIFFERENTIATION — REVISED
# =============================================================================
# RP9_FIRST_DIFFERENTIATION_REVISED.py
# Version: 2.1.0
# Purpose:
# - Explicitly isolates form differentiation before structural emergence.
# - Verifies one sphere -> two equivalent spheres -> half-half position.
# - Derives the first common intersection circle.
# - Verifies the exact 3/4 and 1/4 relation.
# - Separates exact geometry, RP9 interpretation and float representation.

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import platform
import sys
import traceback
from dataclasses import asdict, dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

getcontext().prec = 80

PYTHON_CODE_ID = "CODE 1"
FILE_NAME = "CODE_1.py"
OFFICIAL_CODE_TITLE = "CODE 1. RP9 FIRST DIFFERENTIATION — REVISED"
SCRIPT_VERSION = "2.1.0"

OUTPUT_DIR_NAME = "2. OUTPUT"

DATA_FILE = "CODE1_DATA.json"
TRACE_FILE = "CODE1_TRACE.json"
FULL_DATASHEET_FILE = "CODE1_FULL_DATASHEET.json"
REPORT_FILE = "CODE1_REPORT.md"
CONTROL_FILE = "CODE1_CONTROL.txt"
VERIFY_FILE = "CODE1_VERIFY.json"
ERROR_FILE = "CODE1_ERROR.log"


# ============================================================
# GENERAL UTILITIES
# ============================================================

def now_local() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")


def script_dir() -> Path:
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd().resolve()


BASE_DIR = script_dir()
OUTPUT_DIR = BASE_DIR / OUTPUT_DIR_NAME


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sci(value: float, digits: int = 20) -> str:
    return format(float(value), f".{digits}e")


def decimal_from_fraction(value: Fraction, places: int = 20) -> str:
    d = Decimal(value.numerator) / Decimal(value.denominator)
    return format(d, f".{places}f")


def json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "__dataclass_fields__"):
        return json_safe(asdict(obj))
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def write_text(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(json_safe(payload), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def distance_3d(a: "Point3D", b: "Point3D") -> Fraction:
    dx = b.x - a.x
    dy = b.y - a.y
    dz = b.z - a.z
    squared = dx * dx + dy * dy + dz * dz
    if squared.denominator == 1:
        root = math.isqrt(squared.numerator)
        if root * root == squared.numerator:
            return Fraction(root, 1)
    return Fraction.from_float(math.sqrt(float(squared)))


def make_trace(
    trace: list[dict[str, Any]],
    layer: str,
    operation: str,
    formula: str,
    inputs: dict[str, Any],
    result: dict[str, Any],
    status: str,
    note: str,
) -> None:
    trace.append(
        {
            "index": len(trace) + 1,
            "timestamp_utc": now_utc_iso(),
            "layer": layer,
            "operation": operation,
            "formula": formula,
            "inputs": json_safe(inputs),
            "result": json_safe(result),
            "status": status,
            "note": note,
        }
    )


# ============================================================
# GEOMETRIC DATA TYPES
# ============================================================

@dataclass(frozen=True)
class Point3D:
    x: Fraction
    y: Fraction
    z: Fraction

    def as_tuple(self) -> tuple[Fraction, Fraction, Fraction]:
        return self.x, self.y, self.z


@dataclass(frozen=True)
class Sphere:
    center: Point3D
    radius: Fraction


@dataclass(frozen=True)
class IntersectionCircle:
    center: Point3D
    normal_axis: str
    radius_squared: Fraction
    radius_symbolic: str


# ============================================================
# A. META-POTENTIAL
# ============================================================

def compute_meta_potential(trace: list[dict[str, Any]]) -> dict[str, Any]:
    layer = "A_META_POTENTIAL"

    radius = Fraction(1, 1)
    center = Point3D(Fraction(0), Fraction(0), Fraction(0))
    sphere = Sphere(center=center, radius=radius)

    form_count = 1
    center_count = 1

    passed = (
        form_count == 1
        and center_count == 1
        and sphere.radius == Fraction(1, 1)
    )

    make_trace(
        trace,
        layer,
        "define_single_spherical_form",
        "P0 = Sphere(C0, R)",
        {},
        {
            "sphere": sphere,
            "form_count": form_count,
            "center_count": center_count,
        },
        "PASS" if passed else "FAIL",
        "Defines one spherical form as the pre-structural geometric reference.",
    )

    return {
        "layer_name": layer,
        "purpose": "Defines one spherical form before internal relational structure.",
        "geometry": {
            "form_count": form_count,
            "center_count": center_count,
            "center": center,
            "radius": radius,
        },
        "classification": {
            "form_status": "SINGLE_SPHERICAL_FORM",
            "structural_status": "PRE_STRUCTURAL",
            "rp9_interpretation": "META_POTENTIAL",
        },
        "status": "PASS" if passed else "FAIL",
    }


# ============================================================
# B. SELF-RELATION
# ============================================================

def compute_self_relation(trace: list[dict[str, Any]], potential: dict[str, Any]) -> dict[str, Any]:
    layer = "B_SELF_RELATION"

    radius_1 = potential["geometry"]["radius"]
    radius_2 = radius_1

    equal_radii = radius_1 == radius_2
    no_new_scale = equal_radii

    initial_form_count = potential["geometry"]["form_count"]
    relational_form_count = initial_form_count * 2

    passed = (
        equal_radii
        and no_new_scale
        and initial_form_count == 1
        and relational_form_count == 2
    )

    make_trace(
        trace,
        layer,
        "reproduce_equivalent_form",
        "R1 = R2 = R",
        {"R1": radius_1},
        {
            "R2": radius_2,
            "equal_radii": equal_radii,
            "initial_form_count": initial_form_count,
            "relational_form_count": relational_form_count,
        },
        "PASS" if passed else "FAIL",
        "Reproduces the same spherical form without introducing a new scale.",
    )

    return {
        "layer_name": layer,
        "purpose": "Reproduces the spherical reference as an equivalent self-relation.",
        "form_transition": {
            "before": initial_form_count,
            "after": relational_form_count,
        },
        "radius_relation": {
            "R1": radius_1,
            "R2": radius_2,
            "equal_radii": equal_radii,
            "new_scale_introduced": not no_new_scale,
        },
        "status": "PASS" if passed else "FAIL",
    }


# ============================================================
# C. FIRST FORM DIFFERENTIATION
# ============================================================

def compute_first_form_differentiation(
    trace: list[dict[str, Any]], relation: dict[str, Any],
) -> dict[str, Any]:
    layer = "C_FIRST_FORM_DIFFERENTIATION"

    radius = relation["radius_relation"]["R1"]
    center_1 = Point3D(-radius / 2, Fraction(0), Fraction(0))
    center_2 = Point3D(radius / 2, Fraction(0), Fraction(0))

    sphere_1 = Sphere(center=center_1, radius=radius)
    sphere_2 = Sphere(center=center_2, radius=radius)

    form_count_before = relation["form_transition"]["before"]
    form_count_after = relation["form_transition"]["after"]
    equal_form = sphere_1.radius == sphere_2.radius
    distinct_centers = sphere_1.center != sphere_2.center
    differentiation_exists = (
        form_count_before == 1
        and form_count_after == 2
        and equal_form
        and distinct_centers
    )

    make_trace(
        trace,
        layer,
        "differentiate_form_by_position",
        "1 equivalent form -> 2 equivalent forms with C1 != C2",
        {"form_count_before": form_count_before},
        {
            "form_count_after": form_count_after,
            "sphere_1": sphere_1,
            "sphere_2": sphere_2,
            "equal_form": equal_form,
            "distinct_centers": distinct_centers,
        },
        "PASS" if differentiation_exists else "FAIL",
        "Isolates the first differentiation before intersection structure.",
    )

    return {
        "layer_name": layer,
        "purpose": "Verifies the transition from one form to two equivalent forms.",
        "forms": {
            "sphere_1": sphere_1,
            "sphere_2": sphere_2,
            "form_count_before": form_count_before,
            "form_count_after": form_count_after,
            "equal_form": equal_form,
            "distinct_centers": distinct_centers,
        },
        "classification": {
            "difference_source": "POSITION",
            "structure_required": False,
            "differentiation": "FORM_DIFFERENTIATION_CONFIRMED"
            if differentiation_exists
            else "FORM_DIFFERENTIATION_FAILED",
        },
        "status": "PASS" if differentiation_exists else "FAIL",
    }


# ============================================================
# D. HALF-HALF POSITIONAL LOCK
# ============================================================

def compute_half_half_lock(trace: list[dict[str, Any]], forms: dict[str, Any]) -> dict[str, Any]:
    layer = "D_HALF_HALF_POSITIONAL_LOCK"

    radius = forms["forms"]["sphere_1"].radius
    center_1 = forms["forms"]["sphere_1"].center
    center_2 = forms["forms"]["sphere_2"].center

    midpoint = Point3D(
        (center_1.x + center_2.x) / 2,
        (center_1.y + center_2.y) / 2,
        (center_1.z + center_2.z) / 2,
    )

    center_distance = distance_3d(center_1, center_2)

    expected_midpoint = Point3D(Fraction(0), Fraction(0), Fraction(0))
    midpoint_valid = midpoint == expected_midpoint
    distance_valid = center_distance == radius
    half_half_valid = (
        center_1.x == -radius / 2
        and center_2.x == radius / 2
        and midpoint_valid
        and distance_valid
    )

    make_trace(
        trace,
        layer,
        "verify_half_half_position",
        "C1 = -R/2 ; C2 = +R/2 ; |C2-C1| = R",
        {"R": radius},
        {
            "C1": center_1,
            "C2": center_2,
            "midpoint": midpoint,
            "center_distance": center_distance,
        },
        "PASS" if half_half_valid else "FAIL",
        "Locks the two differentiated forms symmetrically around one midpoint.",
    )

    return {
        "layer_name": layer,
        "purpose": "Verifies the symmetric half-half positional relation.",
        "position": {
            "R": radius,
            "C1": center_1,
            "C2": center_2,
            "midpoint": midpoint,
            "center_distance": center_distance,
        },
        "verification": {
            "midpoint_is_origin": midpoint_valid,
            "center_distance_equals_radius": distance_valid,
            "half_half_position_valid": half_half_valid,
        },
        "status": "PASS" if half_half_valid else "FAIL",
    }


# ============================================================
# E. FIRST STRUCTURAL INTERSECTION
# ============================================================

def compute_first_intersection(trace: list[dict[str, Any]], position: dict[str, Any]) -> dict[str, Any]:
    layer = "E_FIRST_STRUCTURAL_INTERSECTION"

    radius = position["position"]["R"]
    distance = position["position"]["center_distance"]

    center_1 = position["position"]["C1"]
    center_2 = position["position"]["C2"]
    midpoint = position["position"]["midpoint"]

    intersection_exists = (
        distance > 0
        and distance < 2 * radius
    )

    ri_squared = radius * radius - (distance / 2) * (distance / 2)
    ri_float = math.sqrt(float(ri_squared))
    radius_float = float(radius)

    intersection_radius_smaller = Fraction(0) < ri_squared < radius * radius
    circle = IntersectionCircle(
        center=midpoint,
        normal_axis="x",
        radius_squared=ri_squared,
        radius_symbolic="sqrt(3)/2 * R",
    )

    passed = (
        intersection_exists
        and ri_squared == Fraction(3, 4)
        and intersection_radius_smaller
    )

    make_trace(
        trace,
        layer,
        "derive_intersection_circle",
        "ri^2 = R^2 - (D/2)^2",
        {"R": radius, "D": distance},
        {
            "intersection_circle": circle,
            "ri_squared": ri_squared,
            "ri_float": ri_float,
            "intersection_radius_smaller": intersection_radius_smaller,
        },
        "PASS" if passed else "FAIL",
        "Derives the first common relational structure after form differentiation.",
    )

    return {
        "layer_name": layer,
        "purpose": "Derives the first common intersection structure.",
        "intersection": {
            "exists": intersection_exists,
            "plane_center": midpoint,
            "plane_normal_axis": "x",
            "radius_squared_exact": ri_squared,
            "source_radius": radius,
            "source_distance": distance,
            "radius_symbolic": "sqrt(3)/2 * R",
            "radius_float": sci(ri_float),
            "sphere_radius_float": sci(radius_float),
            "intersection_radius_is_smaller": intersection_radius_smaller,
        },
        "classification": {
            "rp9_name": "VESICA_PISCIS",
            "structural_status": "FIRST_RELATIONAL_STRUCTURE",
            "preceded_by_form_differentiation": True,
        },
        "status": "PASS" if passed else "FAIL",
    }


# ============================================================
# F. EXACT RELATIONAL RESULT
# ============================================================

def compute_exact_relational_result(
    trace: list[dict[str, Any]], intersection: dict[str, Any],
) -> dict[str, Any]:
    layer = "F_EXACT_RELATIONAL_RESULT"

    radius_squared = intersection["intersection"]["source_radius"] ** 2
    intersection_radius_squared = intersection["intersection"]["radius_squared_exact"]

    ratio_exact = intersection_radius_squared / radius_squared
    lock_exact = Fraction(1, 1) - ratio_exact

    ratio_float = float(ratio_exact)
    lock_float = float(lock_exact)

    ratio_float_residual = Fraction.from_float(ratio_float) - ratio_exact
    lock_float_residual = Fraction.from_float(lock_float) - lock_exact

    passed = (
        ratio_exact == Fraction(3, 4)
        and lock_exact == Fraction(1, 4)
        and ratio_float_residual == 0
        and lock_float_residual == 0
    )

    make_trace(
        trace,
        layer,
        "verify_exact_ratio_and_lock",
        "ri^2/R^2 = 3/4 ; 1 - 3/4 = 1/4",
        {
            "ri_squared": intersection_radius_squared,
            "R_squared": radius_squared,
        },
        {
            "ratio_exact": ratio_exact,
            "lock_exact": lock_exact,
            "ratio_float_residual": ratio_float_residual,
            "lock_float_residual": lock_float_residual,
        },
        "PASS" if passed else "FAIL",
        "Verifies the exact relation after the full geometric derivation.",
    )

    return {
        "layer_name": layer,
        "purpose": "Verifies the exact 3/4 and 1/4 relation.",
        "exact_geometry": {
            "intersection_radius_squared": intersection_radius_squared,
            "sphere_radius_squared": radius_squared,
            "ratio_exact": ratio_exact,
            "complementary_lock_exact": lock_exact,
        },
        "decimal_rendering": {
            "ratio_20_places": decimal_from_fraction(ratio_exact, 20),
            "lock_20_places": decimal_from_fraction(lock_exact, 20),
        },
        "float_conversion": {
            "ratio_float": ratio_float,
            "lock_float": lock_float,
            "ratio_residual_against_exact": ratio_float_residual,
            "lock_residual_against_exact": lock_float_residual,
        },
        "status": "PASS" if passed else "FAIL",
    }


# ============================================================
# G. REPRESENTATION CONTROL
# ============================================================

def compute_representation_control(
    trace: list[dict[str, Any]], intersection: dict[str, Any],
) -> dict[str, Any]:
    layer = "G_REPRESENTATION_CONTROL"

    radius = float(intersection["intersection"]["source_radius"])
    distance = float(intersection["intersection"]["source_distance"])

    ri = math.sqrt(radius * radius - (distance / 2.0) ** 2)
    area_y = math.pi * radius * radius
    area_i = math.pi * ri * ri

    ratio = area_i / area_y
    lock = 1.0 - ratio

    ratio_expected = 0.75
    lock_expected = 0.25

    ratio_residual = ratio - ratio_expected
    lock_residual = lock - lock_expected

    symmetric_residual = abs(ratio_residual + lock_residual) <= 1e-30
    ratio_is_lower = ratio < ratio_expected
    lock_is_higher = lock > lock_expected

    epsilon = sys.float_info.epsilon
    next_value = math.nextafter(1.0, 2.0)
    next_diff = next_value - 1.0

    passed = (
        symmetric_residual
        and ratio_is_lower
        and lock_is_higher
        and next_diff == epsilon
    )

    make_trace(
        trace,
        layer,
        "verify_float_rendering",
        "ratio=(pi*ri^2)/(pi*R^2) ; lock=1-ratio",
        {"R": radius, "D": distance},
        {
            "ratio": ratio,
            "lock": lock,
            "ratio_residual": ratio_residual,
            "lock_residual": lock_residual,
            "symmetric_residual": symmetric_residual,
        },
        "PASS" if passed else "REVIEW",
        "Confirms representation behaviour separately from exact geometry.",
    )

    return {
        "layer_name": layer,
        "purpose": "Separates binary float rendering from exact geometry.",
        "float_geometry": {
            "R": sci(radius),
            "D": sci(distance),
            "ri": sci(ri),
            "AY": sci(area_y),
            "AI": sci(area_i),
        },
        "float_lock": {
            "ratio_observed": sci(ratio),
            "ratio_expected": sci(ratio_expected),
            "ratio_residual": sci(ratio_residual),
            "ratio_hex": ratio.hex(),
            "ratio_next_down": sci(math.nextafter(ratio, 0.0)),
            "ratio_next_up": sci(math.nextafter(ratio, 1.0)),
            "lock_observed": sci(lock),
            "lock_expected": sci(lock_expected),
            "lock_residual": sci(lock_residual),
            "lock_hex": lock.hex(),
            "lock_next_down": sci(math.nextafter(lock, 0.0)),
            "lock_next_up": sci(math.nextafter(lock, 1.0)),
        },
        "machine_precision": {
            "epsilon": sci(epsilon),
            "nextafter_1_to_2": sci(next_value),
            "nextafter_diff": sci(next_diff),
            "nextafter_matches_epsilon": next_diff == epsilon,
        },
        "classification": {
            "ratio_is_lower_than_0_75": ratio_is_lower,
            "lock_is_higher_than_0_25": lock_is_higher,
            "symmetric_residual": symmetric_residual,
            "exact_geometry_affected": False,
        },
        "status": "PASS" if passed else "REVIEW",
    }


# ============================================================
# H. MASTER CONCLUSION
# ============================================================

def diagnostic_trace_record(index, layer, operation, formula, inputs, result, status, note):
    return {"index": index, "timestamp_utc": now_utc_iso(), "layer": layer,
            "operation": operation, "formula": formula, "inputs": json_safe(inputs),
            "result": json_safe(result), "status": status, "note": note}


def compute_ieee_probe(trace):
    layer = "C_IEEE_RESIDUAL_PROBE"
    values = []
    cases = [
        ("decimal_addition", "0.1 + 0.2", 0.1 + 0.2, 0.3, "Classic binary float decimal representation check."),
        ("sin_pi", "math.sin(math.pi)", math.sin(math.pi), 0.0, "Checks transcendental rendering near zero."),
        ("tan_pi", "math.tan(math.pi)", math.tan(math.pi), 0.0, "Checks tangent rendering near zero at pi."),
        ("sqrt2_squared_minus_2", "math.sqrt(2)**2 - 2", math.sqrt(2) ** 2 - 2.0, 0.0, "Checks square-root roundtrip residual.")
    ]
    for name, expression, observed, expected, note in cases:
        residual = observed - expected
        is_close = math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-15)
        row = {"name": name, "expression": expression, "observed": sci(observed), "expected": sci(expected), "residual": sci(residual), "is_close_abs_1e_minus_15": bool(is_close), "note": note}
        values.append(row)
        trace.append(diagnostic_trace_record(len(trace) + 1, layer, name, expression, {}, row, "PASS" if is_close else "REVIEW", note))
    eps = sys.float_info.epsilon
    r16 = eps
    r15 = eps * 8.0
    quotient = r15 / r16
    quotient_passed = bool(quotient == 8.0)
    next_value = math.nextafter(1.0, 2.0)
    next_diff = next_value - 1.0
    next_passed = bool(next_diff == r16)
    trace.append(diagnostic_trace_record(len(trace) + 1, layer, "machine_epsilon", "sys.float_info.epsilon", {}, {"epsilon": sci(eps), "power_relation": "2^-52"}, "PASS", "Reads Python float machine epsilon."))
    trace.append(diagnostic_trace_record(len(trace) + 1, layer, "r15_r16_ratio", "(epsilon * 8) / epsilon", {"r16": sci(r16), "r15": sci(r15)}, {"quotient": str(quotient)}, "PASS" if quotient_passed else "FAIL", "Verifies R15/R16 quotient in binary precision."))
    trace.append(diagnostic_trace_record(len(trace) + 1, layer, "nextafter", "math.nextafter(1.0, 2.0) - 1.0", {"start": "1.0", "direction": "2.0"}, {"next_value": sci(next_value), "diff": sci(next_diff)}, "PASS" if next_passed else "FAIL", "Checks the next representable float above 1.0."))
    passed = quotient_passed and next_passed
    return {
        "layer_name": layer,
        "purpose": "Control group for IEEE-754 style float behaviour using Python float.",
        "float_cases": values,
        "machine_precision": {
            "epsilon": sci(eps),
            "R16": sci(r16),
            "R15": sci(r15),
            "R15_div_R16": str(quotient),
            "R15_div_R16_passed": quotient_passed,
            "nextafter_1_to_2": sci(next_value),
            "nextafter_diff": sci(next_diff),
            "nextafter_matches_R16": next_passed
        },
        "status": "PASS" if passed else "REVIEW"
    }


def build_master_conclusion(
    layers: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    statuses = [layer["status"] for layer in layers.values()]

    if any(status == "FAIL" for status in statuses):
        total_status = "FAIL"
    elif any(status == "REVIEW" for status in statuses):
        total_status = "PASS_WITH_REVIEW_NOTES"
    else:
        total_status = "PASS"

    return {
        "layer_name": "H_MASTER_CONCLUSION",
        "chain": [
            "META-POTENTIAL",
            "SINGLE SPHERICAL FORM",
            "SELF-RELATION",
            "TWO EQUIVALENT FORMS",
            "FIRST FORM DIFFERENTIATION",
            "HALF-HALF POSITION",
            "INTERSECTION",
            "VESICA PISCIS",
            "FIRST RELATIONAL STRUCTURE",
            "EXACT 3/4 RELATION",
            "COMPLEMENTARY 1/4 LOCK",
            "REPRESENTATION CONTROL",
            "IEEE RESIDUAL DIAGNOSTICS",
        ],
        "summary": {
            key: value["status"]
            for key, value in layers.items()
        },
        "total_status": total_status,
        "measurement_boundary": (
            "The code verifies geometric form count, center count, radius "
            "invariance, positional differentiation, half-half symmetry, "
            "intersection geometry, exact ratio and machine representation. "
            "RP9 interpretation remains explicitly separated."
        ),
        "rp9_interpretation_layer": {
            "separated_from_measurement": True,
            "interpretation": (
                "FIRST DIFFERENTIATION is the transition from one spherical "
                "form to two equivalent spherical forms in distinct symmetric "
                "positions. Vesica Piscis is the first relational structure "
                "enabled by that prior differentiation."
            ),
        },
    }


# ============================================================
# RUN
# ============================================================

def run_all() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    trace: list[dict[str, Any]] = []

    potential = compute_meta_potential(trace)
    relation = compute_self_relation(trace, potential)
    forms = compute_first_form_differentiation(trace, relation)
    position = compute_half_half_lock(trace, forms)
    intersection = compute_first_intersection(trace, position)
    exact = compute_exact_relational_result(trace, intersection)
    representation = compute_representation_control(trace, intersection)
    diagnostics = compute_ieee_probe(trace)
    layers = {
        "A_meta_potential": potential,
        "B_self_relation": relation,
        "C_first_form_differentiation": forms,
        "D_half_half_positional_lock": position,
        "E_first_structural_intersection": intersection,
        "F_exact_relational_result": exact,
        "G_representation_control": representation,
        "I_ieee_residual_probe": diagnostics,
    }

    previous_ok = True
    for name, layer in layers.items():
        if name == "I_ieee_residual_probe":
            continue
        layer["upstream_status_preserved"] = previous_ok
        if not previous_ok:
            layer["status"] = "FAIL"
        previous_ok = previous_ok and layer["status"] != "FAIL"
    master = build_master_conclusion(layers)

    payload = {
        "script": {
            "repository": "RP9. RH. Z0",
            "repository_branch": "2. RP9. EXPANSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "version": SCRIPT_VERSION,
            "created_at_local": now_local(),
            "created_at_utc": now_utc_iso(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": str(BASE_DIR),
            "output_directory": str(OUTPUT_DIR),
            "purpose": (
                "Complete verification of RP9 FIRST DIFFERENTIATION from "
                "single form to relational structure."
            ),
        },
        "layers": layers,
        "master_conclusion": master,
    }

    return payload, trace


# ============================================================
# OUTPUT BUILDERS
# ============================================================

def build_markdown(
    payload: dict[str, Any],
    trace: list[dict[str, Any]],
) -> list[str]:
    layers = payload["layers"]
    master = payload["master_conclusion"]

    lines: list[str] = []
    lines.extend(
        [
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
            "# RP9 FIRST DIFFERENTIATION — REVISED",
            "",
            "## Control Chain",
            "",
            "```text",
            *master["chain"],
            "```",
            "",
            "## Layer Status",
            "",
            "| Layer | Status |",
            "|---|---|",
        ]
    )

    for key, layer in layers.items():
        lines.append(f"| {key} | `{layer['status']}` |")

    lines.extend(
        [
            "",
            f"**Total status:** `{master['total_status']}`",
            "",
            "## Foundational Conclusion",
            "",
            master["rp9_interpretation_layer"]["interpretation"],
            "",
            "## Measurement Boundary",
            "",
            master["measurement_boundary"],
            "",
            "## Trace",
            "",
            "| Index | Layer | Operation | Status |",
            "|---|---|---|---|",
        ]
    )

    for row in trace:
        lines.append(
            f"| {row['index']} | {row['layer']} | "
            f"{row['operation']} | `{row['status']}` |"
        )

    lines.extend(["", "## Restored machine diagnostics", "", "```json",
                  json.dumps(json_safe(layers["I_ieee_residual_probe"]), indent=2),
                  "```", "", "## Neighboring float positions", "", "```json",
                  json.dumps(json_safe(layers["G_representation_control"]["float_lock"]), indent=2),
                  "```"])
    return lines


def build_control_log(
    payload: dict[str, Any],
    trace: list[dict[str, Any]],
) -> list[str]:
    lines = [
        "RP9 FIRST DIFFERENTIATION — REVISED CONTROL LOG",
        "=" * 72,
        f"Created local: {payload['script']['created_at_local']}",
        f"Created UTC: {payload['script']['created_at_utc']}",
        f"Python Code ID: {PYTHON_CODE_ID}",
        f"Official Code Title: {OFFICIAL_CODE_TITLE}",
        f"File: {FILE_NAME}",
        f"Version: {payload['script']['version']}",
        "",
        "VERIFIED CHAIN",
        "-" * 72,
    ]

    for item in payload["master_conclusion"]["chain"]:
        lines.append(item)

    lines.extend(["", "TRACE", "-" * 72])

    for row in trace:
        lines.extend(
            [
                f"STEP {str(row['index']).zfill(3)}",
                f"Layer: {row['layer']}",
                f"Operation: {row['operation']}",
                f"Formula: {row['formula']}",
                f"Status: {row['status']}",
                f"Note: {row['note']}",
                "",
            ]
        )

    lines.extend(
        [
            "FINAL STATUS",
            "-" * 72,
            payload["master_conclusion"]["total_status"],
            "",
            "BOUNDARY",
            "-" * 72,
            payload["master_conclusion"]["measurement_boundary"],
        ]
    )

    return lines


def write_outputs(
    payload: dict[str, Any],
    trace: list[dict[str, Any]],
) -> dict[str, Path]:
    ensure_output_dir()

    paths = {
        "data_json": OUTPUT_DIR / DATA_FILE,
        "trace_json": OUTPUT_DIR / TRACE_FILE,
        "full_datasheet_json": OUTPUT_DIR / FULL_DATASHEET_FILE,
        "presentation_markdown": OUTPUT_DIR / REPORT_FILE,
        "control_log": OUTPUT_DIR / CONTROL_FILE,
        "verify_json": OUTPUT_DIR / VERIFY_FILE,
        "audit_json": OUTPUT_DIR / "CODE1_AUDIT.json",
        "execution_log": OUTPUT_DIR / "CODE1_EXECUTION.log",
    }

    write_json(paths["data_json"], payload)
    write_json(paths["trace_json"], trace)
    write_json(
        paths["full_datasheet_json"],
        {"payload": payload, "trace": trace},
    )
    write_text(
        paths["presentation_markdown"],
        build_markdown(payload, trace),
    )
    write_text(
        paths["control_log"],
        build_control_log(payload, trace),
    )

    status = payload["master_conclusion"]["total_status"]
    audit_entries = [{"action": "calculate_and_record", "status": row["status"],
                      "timestamp_utc": row["timestamp_utc"],
                      "layer": row["layer"], "operation": row["operation"]}
                     for row in trace]
    audit_entries.extend({"action": "artifact_written", "status": "OK",
                          "timestamp_utc": now_utc_iso(), "path": str(paths[name])}
                         for name in ("data_json", "trace_json", "full_datasheet_json",
                                      "presentation_markdown", "control_log"))
    audit_entries.append({"action": "calculation_complete", "status": status,
                          "timestamp_utc": now_utc_iso()})
    write_json(paths["audit_json"], {"script_version": SCRIPT_VERSION,
                                   "entries": audit_entries,
                                   "entry_count": len(audit_entries)})
    write_text(paths["execution_log"], [
        OFFICIAL_CODE_TITLE, "Version: " + SCRIPT_VERSION,
        "Created UTC: " + payload["script"]["created_at_utc"],
        "Python: " + sys.version, "Platform: " + platform.platform(),
        "Trace count: " + str(len(trace)), "Global status: " + status,
    ] + [name + ": " + str(path) for name, path in paths.items()])

    verify_files = {}
    for name, path in paths.items():
        if name == "verify_json":
            continue
        verify_files[name] = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }

    write_json(
        paths["verify_json"],
        {
            "repository": "RP9. RH. Z0",
            "repository_branch": "2. RP9. EXPANSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "script_version": SCRIPT_VERSION,
            "generated_at_utc": now_utc_iso(),
            "files": verify_files,
        },
    )

    return paths


def print_summary(
    payload: dict[str, Any],
    paths: dict[str, Path],
) -> None:
    print("")
    print("=" * 72)
    print("RP9 FIRST DIFFERENTIATION — REVISED")
    print("=" * 72)

    for key, layer in payload["layers"].items():
        print(f"{key}: {layer['status']}")

    print("-" * 72)
    print("total_status:", payload["master_conclusion"]["total_status"])
    print("-" * 72)

    for name, path in paths.items():
        print(f"{name}: {path}")

    print("=" * 72)
    print("")


def generate_once() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Path],
]:
    payload, trace = run_all()
    paths = write_outputs(payload, trace)
    print_summary(payload, paths)
    return payload, trace, paths


def write_error_log(exc: Exception) -> Path:
    ensure_output_dir()
    path = OUTPUT_DIR / ERROR_FILE
    lines = [
        "RP9 FIRST DIFFERENTIATION — REVISED ERROR LOG",
        "=" * 72,
        f"Timestamp local: {now_local()}",
        f"Timestamp UTC: {now_utc_iso()}",
        f"Error type: {type(exc).__name__}",
        f"Error message: {exc}",
        "",
        "TRACEBACK",
        "-" * 72,
        *traceback.format_exc().splitlines(),
    ]
    write_text(path, lines)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "RP9 FIRST DIFFERENTIATION revised all-inclusive verifier."
        )
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Generate all verification files and exit.",
    )
    return parser.parse_args()


def main() -> None:
    parse_args()
    try:
        generate_once()
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    except Exception as exc:
        error_path = write_error_log(exc)
        print("ERROR:", exc)
        print("Error log written to:", error_path)


if __name__ == "__main__":
    main()
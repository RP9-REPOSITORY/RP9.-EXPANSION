
# -*- coding: utf-8 -*-
# RP9_CODE_ID: C.0073
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     2. RP9. EXPANSION
#
# PYTHON CODE ID: RX8. D
# OFFICIAL CODE TITLE: RX8. RP9 RX8 RESIDUAL VALIDATOR
# =============================================================================

# RP9_RX8_RESIDUAL_VALIDATOR.py
# Version: 1.1.0
# Purpose:
# Independently validate residual behavior produced by numerical representation.
# This validator compares exact rational references with executed float/Decimal
# representations and measures residual magnitude, sign, symmetry and traceability.
# It has no execution dependency on any other RP9/Rx8 validator.
# It writes WHAT/HOW/WHY/RESULT to JSON, Markdown, trace, audit, verify and log.

import json
import math
import struct
import sys
from datetime import datetime
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path


PYTHON_CODE_ID = 'RX8. D'
FILE_NAME = 'RX8. D.py'
OFFICIAL_CODE_TITLE = 'RX8. RP9 RX8 RESIDUAL VALIDATOR'
SCRIPT_VERSION = '1.1.0'

OUTPUT_DIR_NAME = '2. OUTPUT'
DATA_FILE = 'RX8.D_DATA.json'
TRACE_FILE = 'RX8.D_TRACE.json'
AUDIT_FILE = 'RX8.D_AUDIT.json'
VERIFY_FILE = 'RX8.D_VERIFY.json'
REPORT_FILE = 'RX8.D_REPORT.md'
CONTROL_FILE = 'RX8.D_CONTROL.txt'


def now_iso():
    return datetime.now().isoformat(timespec='seconds')


def make_output_dir():
    out_dir = Path.cwd() / OUTPUT_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def write_text(path, content):
    path.write_text(content, encoding='utf-8')


def write_json(path, data):
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')


def to_jsonable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    return value


def status(pass_value):
    if pass_value:
        return 'PASS'
    return 'FAIL'


def make_test_record(test_id, title, what_is_tested, how_it_is_tested, why_it_is_tested, expected_result, observed_result, passed, data):
    return {
        'test_id': test_id,
        'title': title,
        'vad_som_testas': what_is_tested,
        'hur_det_testas': how_it_is_tested,
        'varfor_det_testas': why_it_is_tested,
        'forvantat_resultat': expected_result,
        'observerat_resultat': observed_result,
        'slutresultat': status(passed),
        'data': to_jsonable(data)
    }


def float_hex(value):
    return float(value).hex()


def float_bits(value):
    packed = struct.pack('>d', float(value))
    integer_value = int.from_bytes(packed, byteorder='big', signed=False)
    return format(integer_value, '064b')


def test_1_exact_relation_no_residual():
    ratio = Fraction(3, 4)
    lock = Fraction(1, 4)
    total = ratio + lock
    residual = total - Fraction(1, 1)
    passed = total == Fraction(1, 1) and residual == Fraction(0, 1)
    return make_test_record(
        'TEST_1',
        'EXAKT_RELATION_UTAN_RESIDUAL',
        'Den exakta relationen 3/4 + 1/4 innan representationellt residualspar uppstar.',
        'Beraknar 3/4 + 1/4 med fractions.Fraction och jamfor mot exakt 1.',
        'For att skapa en ren referensniva dar relationen ar intakt och residualen ar exakt noll.',
        'Summan ska vara exakt 1 och residualen ska vara exakt 0.',
        'Summan blev ' + str(total) + ' och residualen blev ' + str(residual) + '.',
        passed,
        {
            'ratio': ratio,
            'lock': lock,
            'sum': total,
            'residual': residual,
            'layer': 'EXACT_RELATION_REFERENCE'
        }
    )


def test_2_float_representation_layer():
    ratio = 0.75
    lock = 0.25
    total = ratio + lock
    residual = total - 1.0
    passed = total == 1.0 and residual == 0.0
    return make_test_record(
        'TEST_2',
        'FLOAT_REPRESENTATION_LAYER',
        'Flyttalsrepresentationen av 0.75 + 0.25.',
        'Beraknar 0.75 + 0.25 i Python float och registrerar IEEE754 hex- och bitrepresentation.',
        'For att visa att exakt representerbara fjardedelar fortfarande ar representation och inte ny relation.',
        'Summan ska vara 1.0 och residualen ska vara 0.0 i detta representationslager.',
        'Summan blev ' + str(total) + ' och residualen blev ' + str(residual) + '.',
        passed,
        {
            'ratio_float': ratio,
            'lock_float': lock,
            'sum_float': total,
            'residual_float': residual,
            'ratio_hex': float_hex(ratio),
            'lock_hex': float_hex(lock),
            'sum_hex': float_hex(total),
            'ratio_bits': float_bits(ratio),
            'lock_bits': float_bits(lock),
            'sum_bits': float_bits(total),
            'layer': 'FLOAT_REPRESENTATION'
        }
    )


def test_3_vesica_float_residual():
    exact_ratio = Fraction(3, 4)
    ri_float = math.sqrt(3.0) / 2.0
    observed_ratio = ri_float * ri_float
    expected_ratio = float(exact_ratio)
    ratio_residual = observed_ratio - expected_ratio
    residual_detected = ratio_residual != 0.0
    passed = residual_detected
    return make_test_record(
        'TEST_3',
        'VESICA_FLOAT_RESIDUAL',
        'Residual som uppstar nar Vesica-relationen sqrt(3)/2 representeras och kvadreras i float.',
        'Beraknar ri = sqrt(3)/2 i float, kvadrerar ri och jamfor mot exakt 3/4 som float.',
        'For att mata skillnaden mellan den exakta referensen och den exekverade float-representationen.',
        'En icke-noll skillnad ska kunna matas mellan float-resultatet och referensvardet 3/4.',
        'Ratio residual blev ' + format(ratio_residual, '.20e') + '.',
        passed,
        {
            'exact_ratio': exact_ratio,
            'ri_float': format(ri_float, '.20e'),
            'observed_ratio_float': format(observed_ratio, '.20e'),
            'expected_ratio_float': format(expected_ratio, '.20e'),
            'ratio_residual': format(ratio_residual, '.20e'),
            'residual_detected': residual_detected,
            'comparison_layer': 'FLOAT_VS_EXACT_REFERENCE'
        }
    )


def test_4_residual_symmetry():
    exact_ratio = Fraction(3, 4)
    exact_lock = Fraction(1, 4)
    ri_float = math.sqrt(3.0) / 2.0
    observed_ratio = ri_float * ri_float
    observed_lock = 1.0 - observed_ratio
    ratio_residual = observed_ratio - float(exact_ratio)
    lock_residual = observed_lock - float(exact_lock)
    residual_sum = ratio_residual + lock_residual
    symmetric = math.isclose(residual_sum, 0.0, rel_tol=0.0, abs_tol=1e-30)
    passed = symmetric
    return make_test_record(
        'TEST_4',
        'RESIDUALSYMMETRI_DELTA_PLUS_DELTA_MINUS',
        'Residualsymmetri mellan ratio-sparet och lock-sparet.',
        'Beraknar delta_ratio och delta_lock och kontrollerar att delta_ratio + delta_lock = 0 inom strikt tolerans.',
        'For att kontrollera om de tva matta avvikelserna ar komplementara runt samma exakta referenssumma.',
        'Residualsumman ska vara 0 inom abs_tol = 1e-30.',
        'Residualsumman blev ' + format(residual_sum, '.20e') + '.',
        passed,
        {
            'ratio_residual': format(ratio_residual, '.20e'),
            'lock_residual': format(lock_residual, '.20e'),
            'residual_sum': format(residual_sum, '.20e'),
            'symmetric': symmetric,
            'tolerance': '1e-30',
            'comparison_layer': 'COMPLEMENTARY_RESIDUAL_PAIR'
        }
    )


def test_5_residual_position_layer():
    exact_ratio = Fraction(3, 4)
    ri_float = math.sqrt(3.0) / 2.0
    observed_ratio = ri_float * ri_float
    reference_float = float(exact_ratio)
    residual = observed_ratio - reference_float

    reference_unchanged = exact_ratio == Fraction(3, 4)
    observed_differs_from_reference = observed_ratio != reference_float
    residual_matches_difference = residual == observed_ratio - reference_float
    classification = 'MEASURED_REPRESENTATION_DIFFERENCE' if (
        reference_unchanged
        and observed_differs_from_reference
        and residual_matches_difference
    ) else 'UNRESOLVED'

    passed = classification == 'MEASURED_REPRESENTATION_DIFFERENCE'

    return make_test_record(
        'TEST_5',
        'RESIDUAL_POSITION_BY_COMPARISON',
        'Residualens berakningsmassiga position mellan exakt referens och exekverad float-representation.',
        'Kontrollerar att referensen 3/4 forblir oforandrad och att residualen exakt motsvarar observed_float - reference_float.',
        'For att klassificera residualen genom beraknad differens i stallet for genom en forhandsdeklarerad origin/trace-flagga.',
        'Residualen ska klassificeras som MEASURED_REPRESENTATION_DIFFERENCE.',
        'Klassificering: ' + classification + ', residual: ' + format(residual, '.20e') + '.',
        passed,
        {
            'exact_reference': exact_ratio,
            'reference_float': format(reference_float, '.20e'),
            'observed_float': format(observed_ratio, '.20e'),
            'residual': format(residual, '.20e'),
            'reference_unchanged': reference_unchanged,
            'observed_differs_from_reference': observed_differs_from_reference,
            'residual_matches_difference': residual_matches_difference,
            'classification': classification
        }
    )

def test_6_machine_trace_float_vs_fraction():
    exact_ratio = Fraction(3, 4)
    exact_lock = Fraction(1, 4)
    ri_float = math.sqrt(3.0) / 2.0
    observed_ratio = ri_float * ri_float
    observed_lock = 1.0 - observed_ratio

    ratio_reference_float = float(exact_ratio)
    lock_reference_float = float(exact_lock)
    ratio_residual = observed_ratio - ratio_reference_float
    lock_residual = observed_lock - lock_reference_float

    machine_trace_exists = ratio_residual != 0.0 and lock_residual != 0.0
    exact_reference_closed = exact_ratio + exact_lock == Fraction(1, 1)
    float_pair_closed = observed_ratio + observed_lock == 1.0
    residual_pair_closed = math.isclose(
        ratio_residual + lock_residual,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-30
    )

    passed = (
        machine_trace_exists
        and exact_reference_closed
        and float_pair_closed
        and residual_pair_closed
    )

    return make_test_record(
        'TEST_6',
        'MASKINSPAR_FLOAT_VS_FRACTION',
        'IEEE754-maskinspar genom jamforelse mellan float och Fraction.',
        'Jamfor exakt Fraction-referens mot exekverad float-representation och kontrollerar bada summorna samt residualparet.',
        'For att verifiera att den matta residualen kan sparas till skillnaden mellan tva numeriska representationsnivaer.',
        'Maskinspar ska finnas, bada summorna ska vara slutna och residualparet ska summera till 0 inom strikt tolerans.',
        'Maskinspar: ' + str(machine_trace_exists)
        + ', exact closure: ' + str(exact_reference_closed)
        + ', float closure: ' + str(float_pair_closed)
        + ', residual closure: ' + str(residual_pair_closed) + '.',
        passed,
        {
            'exact_ratio': exact_ratio,
            'exact_lock': exact_lock,
            'exact_sum': exact_ratio + exact_lock,
            'observed_ratio_float': format(observed_ratio, '.20e'),
            'observed_lock_float': format(observed_lock, '.20e'),
            'ratio_residual': format(ratio_residual, '.20e'),
            'lock_residual': format(lock_residual, '.20e'),
            'ratio_float_hex': float_hex(observed_ratio),
            'lock_float_hex': float_hex(observed_lock),
            'machine_trace_exists': machine_trace_exists,
            'exact_reference_closed': exact_reference_closed,
            'float_pair_closed': float_pair_closed,
            'residual_pair_closed': residual_pair_closed
        }
    )

def test_7_decimal_crosscheck():
    getcontext().prec = 80
    decimal_three = Decimal(3)
    decimal_four = Decimal(4)
    decimal_ratio = decimal_three / decimal_four
    decimal_lock = Decimal(1) - decimal_ratio
    exact_ratio = Fraction(3, 4)
    exact_lock = Fraction(1, 4)
    ratio_ok = decimal_ratio == Decimal(exact_ratio.numerator) / Decimal(exact_ratio.denominator)
    lock_ok = decimal_lock == Decimal(exact_lock.numerator) / Decimal(exact_lock.denominator)
    total_ok = decimal_ratio + decimal_lock == Decimal(1)
    passed = ratio_ok and lock_ok and total_ok
    return make_test_record(
        'TEST_7',
        'DECIMAL_KORSKONTROLL',
        'Decimal representation av 3/4 och 1/4 med hog precision.',
        'Anvander Decimal med precision 80 och jamfor mot Fraction-referensen.',
        'For att kontrollera att fjardedelsproportionen inte ar beroende av float-lagret.',
        'Decimal 3/4 + 1/4 ska bli exakt 1 med vald Decimal-representation.',
        'Decimal summa blev ' + str(decimal_ratio + decimal_lock) + '.',
        passed,
        {
            'decimal_precision': getcontext().prec,
            'decimal_ratio': decimal_ratio,
            'decimal_lock': decimal_lock,
            'decimal_sum': decimal_ratio + decimal_lock,
            'ratio_ok': ratio_ok,
            'lock_ok': lock_ok,
            'total_ok': total_ok
        }
    )


def test_8_global_residual_integrity(previous_tests):
    failed = [t for t in previous_tests if t['slutresultat'] != 'PASS']
    test_5_data = previous_tests[4].get('data', {})
    test_6_data = previous_tests[5].get('data', {})

    computed_classification_ok = (
        test_5_data.get('classification') == 'MEASURED_REPRESENTATION_DIFFERENCE'
    )
    machine_comparison_ok = (
        test_6_data.get('machine_trace_exists') is True
        and test_6_data.get('exact_reference_closed') is True
        and test_6_data.get('float_pair_closed') is True
        and test_6_data.get('residual_pair_closed') is True
    )

    passed = (
        len(failed) == 0
        and computed_classification_ok
        and machine_comparison_ok
    )

    chain = [
        'EXACT_REFERENCE: Fraction(3/4) + Fraction(1/4) = 1',
        'FLOAT_REFERENCE: 0.75 + 0.25 = 1.0',
        'FLOAT_EXECUTION: sqrt(3)/2 squared is compared with 3/4',
        'RESIDUAL_MEASUREMENT: observed_float - reference_float',
        'SYMMETRY: delta_ratio + delta_lock = 0 within tolerance',
        'CLASSIFICATION: measured representation difference',
        'MACHINE_TRACE: float and Fraction comparison is reproducible',
        'DECIMAL_CROSSCHECK: exact quarter closure is independently reproduced'
    ]

    return make_test_record(
        'TEST_8',
        'GLOBAL_RESIDUAL_INTEGRITY',
        'Den kompletta sjalvstandiga residualkontrollen fran exakt referens till matbar maskindifferens.',
        'Sammanstaller TEST_1 till TEST_7 och kraver PASS samt de beraknade klassificerings- och maskinjamforelsekriterierna.',
        'For att ge validatorn ett eget globalt resultat utan beroende av andra Rx8-koder eller forhandsdeklarerade origin/trace-flaggor.',
        'Alla interna residualkontroller ska vara PASS och de beraknade jamforelsekriterierna ska vara uppfyllda.',
        'Misslyckade tester: ' + str(len(failed))
        + ', computed classification: ' + str(computed_classification_ok)
        + ', machine comparison: ' + str(machine_comparison_ok) + '.',
        passed,
        {
            'chain': chain,
            'failed_tests': [t['test_id'] for t in failed],
            'computed_classification_ok': computed_classification_ok,
            'machine_comparison_ok': machine_comparison_ok,
            'all_previous_tests_passed': len(failed) == 0
        }
    )

def build_markdown(summary, tests):
    lines = [
        '> [!info] **RP9. CODE IDENTITY**',
        '> ',
        '> - ### REPOSITORY: _**RP9. RH. Z0**_',
        '>     ',
        '>     - #### **2. RP9. EXPANSION**',
        '>',
        '>---',
        f'> - PYTHON CODE 🆔: **{PYTHON_CODE_ID}**',
        '> ',
        f'> - OFFICIAL CODE TITEL: **{OFFICIAL_CODE_TITLE}**',
        '> ',
        '>---',
        '',
        '# RP9 RX8 RESIDUAL VALIDATOR',
        '',
        '## GLOBALT SLUTRESULTAT',
        '',
        '```text',
        'STATUS: ' + summary['global_status'],
        'PYTHON CODE ID: ' + PYTHON_CODE_ID,
        'OFFICIAL CODE TITLE: ' + OFFICIAL_CODE_TITLE,
        'VERSION: ' + summary['version'],
        'GENERATED: ' + summary['generated_at'],
        '```',
        '',
    ]
    lines.append('---')
    lines.append('')
    lines.append('## SYFTE')
    lines.append('')
    lines.append('Denna validator ar en sjalvstandig RP9/Rx8 residual- och representationsvalidator.')
    lines.append('')
    lines.append('Den mater residualer genom direkt jamforelse mellan exakta referenser och exekverade numeriska representationer.')
    lines.append('')
    lines.append('Den har inget exekveringsberoende pa nagon annan RP9/Rx8-validator.')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## INTERN KONTROLLORDNING')
    lines.append('')
    lines.append('```text')
    lines.append('Exact relation')
    lines.append('down')
    lines.append('Float representation')
    lines.append('down')
    lines.append('Vesica float residual')
    lines.append('down')
    lines.append('Delta plus / delta minus symmetry')
    lines.append('down')
    lines.append('Residual classification = MEASURED_REPRESENTATION_DIFFERENCE')
    lines.append('down')
    lines.append('Machine trace = float vs Fraction')
    lines.append('down')
    lines.append('Global residual integrity')
    lines.append('```')
    lines.append('')
    lines.append('---')
    lines.append('')
    for test in tests:
        lines.append('## ' + test['test_id'] + ' - ' + test['title'])
        lines.append('')
        lines.append('### Vad som testas')
        lines.append('')
        lines.append(test['vad_som_testas'])
        lines.append('')
        lines.append('### Hur det testas')
        lines.append('')
        lines.append(test['hur_det_testas'])
        lines.append('')
        lines.append('### Varfor det testas')
        lines.append('')
        lines.append(test['varfor_det_testas'])
        lines.append('')
        lines.append('### Forvantat resultat')
        lines.append('')
        lines.append(test['forvantat_resultat'])
        lines.append('')
        lines.append('### Observerat resultat')
        lines.append('')
        lines.append(test['observerat_resultat'])
        lines.append('')
        lines.append('### Slutresultat')
        lines.append('')
        lines.append('```text')
        lines.append(test['slutresultat'])
        lines.append('```')
        lines.append('')
        lines.append('---')
        lines.append('')
    lines.append('## SLUTSATS')
    lines.append('')
    if summary['global_status'] == 'PASS':
        lines.append('Den sjalvstandiga residualvalidatorn ar godkand.')
        lines.append('')
        lines.append('Residualen ar matbar och sparbar som differensen mellan exakt referens och exekverad representation.')
        lines.append('')
        lines.append('Det globala resultatet bygger endast pa validatorns egna beraknade kontroller.')
    else:
        lines.append('Den sjalvstandiga residualvalidatorn ar inte godkand.')
        lines.append('')
        lines.append('Minst en intern residual- eller representationskontroll har misslyckats.')
    lines.append('')
    return '\n'.join(lines)


def build_control_log(summary, tests, out_dir):
    lines = []
    lines.append('RP9 RX8 RESIDUAL VALIDATOR CONTROL LOG')
    lines.append('Generated: ' + summary['generated_at'])
    lines.append('Python Code ID: ' + PYTHON_CODE_ID)
    lines.append('Official Code Title: ' + OFFICIAL_CODE_TITLE)
    lines.append('File: ' + FILE_NAME)
    lines.append('Version: ' + summary['version'])
    lines.append('Output directory: ' + str(out_dir))
    lines.append('Global status: ' + summary['global_status'])
    lines.append('')
    for test in tests:
        lines.append(test['test_id'] + ' | ' + test['slutresultat'] + ' | ' + test['title'])
        lines.append('WHAT: ' + test['vad_som_testas'])
        lines.append('HOW: ' + test['hur_det_testas'])
        lines.append('WHY: ' + test['varfor_det_testas'])
        lines.append('RESULT: ' + test['observerat_resultat'])
        lines.append('')
    return '\n'.join(lines)


def run_validator():
    out_dir = make_output_dir()
    tests = []
    tests.append(test_1_exact_relation_no_residual())
    tests.append(test_2_float_representation_layer())
    tests.append(test_3_vesica_float_residual())
    tests.append(test_4_residual_symmetry())
    tests.append(test_5_residual_position_layer())
    tests.append(test_6_machine_trace_float_vs_fraction())
    tests.append(test_7_decimal_crosscheck())
    tests.append(test_8_global_residual_integrity(tests))
    global_pass = all(test['slutresultat'] == 'PASS' for test in tests)
    global_status = status(global_pass)
    summary = {
        'system': 'RP9_RX8',
        'validator_scope': 'INDEPENDENT_RESIDUAL_AND_REPRESENTATION_VALIDATION',
        'repository': 'RP9. RH. Z0',
        'repository_branch': '2. RP9. EXPANSION',
        'python_code_id': PYTHON_CODE_ID,
        'filesystem_name': FILE_NAME,
        'official_code_title': OFFICIAL_CODE_TITLE,
        'version': SCRIPT_VERSION,
        'generated_at': now_iso(),
        'global_status': global_status,
        'principle': 'Residual is measured as the numerical difference between an exact reference and an executed representation.',
        'validation_boundary': 'Only exact-reference closure, representation comparison, residual magnitude, residual symmetry, machine traceability and Decimal cross-check are tested.'
    }
    payload = {
        'SUMMARY': summary,
        'TESTS': tests
    }
    trace_payload = {
        'TRACE': tests
    }
    audit_payload = {
        'AUDIT': {
            'all_tests_include_what_how_why_result': all(
                all(key in test for key in ['vad_som_testas', 'hur_det_testas', 'varfor_det_testas', 'slutresultat'])
                for test in tests
            ),
            'residual_validation_only': True,
            'self_contained_execution': True,
            'external_validator_dependency': False,
            'computed_residual_classification': tests[4]['data'].get('classification'),
            'global_status': global_status
        }
    }
    verify_payload = {
        'VERIFY': {
            'test_1_exact_relation_no_residual': tests[0]['slutresultat'] == 'PASS',
            'test_2_float_representation_layer': tests[1]['slutresultat'] == 'PASS',
            'test_3_vesica_float_residual': tests[2]['slutresultat'] == 'PASS',
            'test_4_residual_symmetry': tests[3]['slutresultat'] == 'PASS',
            'test_5_residual_position_by_comparison': tests[4]['slutresultat'] == 'PASS',
            'test_6_machine_trace': tests[5]['slutresultat'] == 'PASS',
            'test_7_decimal_crosscheck': tests[6]['slutresultat'] == 'PASS',
            'test_8_global_residual_integrity': tests[7]['slutresultat'] == 'PASS',
            'global_status': global_status
        }
    }
    write_json(out_dir / DATA_FILE, payload)
    write_json(out_dir / TRACE_FILE, trace_payload)
    write_json(out_dir / AUDIT_FILE, audit_payload)
    write_json(out_dir / VERIFY_FILE, verify_payload)
    markdown = build_markdown(summary, tests)
    write_text(out_dir / REPORT_FILE, markdown)
    control_log = build_control_log(summary, tests, out_dir)
    write_text(out_dir / CONTROL_FILE, control_log)
    print('=' * 72)
    print('RP9 RX8 RESIDUAL VALIDATOR')
    print('STATUS:', global_status)
    print('OUTPUT:', out_dir)
    print('=' * 72)
    for test in tests:
        print(test['test_id'] + ' | ' + test['slutresultat'] + ' | ' + test['title'])
    print('=' * 72)
    if not global_pass:
        return 1
    return 0


if __name__ == '__main__':
    exit_code = run_validator()
    sys.exit(exit_code)

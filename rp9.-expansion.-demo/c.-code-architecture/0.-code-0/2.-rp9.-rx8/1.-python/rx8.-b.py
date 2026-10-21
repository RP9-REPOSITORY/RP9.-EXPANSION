# -*- coding: utf-8 -*-
# RP9_CODE_ID: C.0071
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     2. RP9. EXPANSION
#
# PYTHON CODE ID: RX8. B
# OFFICIAL CODE TITLE: RX8. RP9 RX8 PROPORTION STRUCTURE VALIDATOR
# =============================================================================

# RP9_RX8_PROPORTION_STRUCTURE_VALIDATOR.py
# Version: 1.1.0
# Purpose:
# Independently validate the assigned Rx8 closure, structural, proportional,
# and residual controls defined inside this code.
#
# IMPORTANT BOUNDARY:
# 1/3 <-> 2/3 and 1/4 <-> 3/4 are tested as separate complementary closures.
# They are NOT treated as the same internal proportion.
#
# Proportion preservation is tested only where proportional identity is
# mathematically preserved:
# 3/4 <-> 1/4  ->  0.75 <-> 0.25.
#
# This code is self-contained. It does not require another RP9 code,
# validator, controller, output file, or execution phase.

import json
import math
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path


PYTHON_CODE_ID = 'RX8. B'
FILE_NAME = 'RX8. B.py'
OFFICIAL_CODE_TITLE = 'RX8. RP9 RX8 PROPORTION STRUCTURE VALIDATOR'
SCRIPT_VERSION = '1.1.0'

OUTPUT_DIR_NAME = '2. OUTPUT'
DATA_FILE = 'RX8.B_DATA.json'
TRACE_FILE = 'RX8.B_TRACE.json'
AUDIT_FILE = 'RX8.B_AUDIT.json'
VERIFY_FILE = 'RX8.B_VERIFY.json'
REPORT_FILE = 'RX8.B_REPORT.md'
CONTROL_FILE = 'RX8.B_CONTROL.txt'


def now_iso():
    return datetime.now().isoformat(timespec='seconds')


def make_output_dir():
    out_dir = Path.cwd() / OUTPUT_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def write_text(path, content):
    path.write_text(content, encoding='utf-8')


def write_json(path, data):
    path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding='utf-8'
    )


def to_jsonable(value):
    if isinstance(value, Fraction):
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
    return 'PASS' if pass_value else 'FAIL'


def make_test_record(
    test_id,
    title,
    what_is_tested,
    how_it_is_tested,
    why_it_is_tested,
    expected_result,
    observed_result,
    passed,
    data
):
    return {
        'test_id': test_id,
        'title': title,
        'what_is_tested': what_is_tested,
        'how_it_is_tested': how_it_is_tested,
        'why_it_is_tested': why_it_is_tested,
        'expected_result': expected_result,
        'observed_result': observed_result,
        'final_result': status(passed),
        'data': to_jsonable(data)
    }


def test_1_relational_closure():
    left = Fraction(1, 3)
    right = Fraction(2, 3)
    total = left + right
    passed = total == Fraction(1, 1)

    return make_test_record(
        'TEST_1',
        'RELATIONAL_CLOSURE',
        'Complementary closure of the relation 1/3 <-> 2/3.',
        'Calculate 1/3 + 2/3 with exact rational arithmetic.',
        'To verify that this assigned relational pair closes exactly to one whole.',
        'The sum must be exactly 1.',
        'Observed exact sum: ' + str(total) + '.',
        passed,
        {
            'left': left,
            'right': right,
            'sum': total,
            'closure_target': Fraction(1, 1),
            'layer': 'RELATION',
            'test_function': 'COMPLEMENTARY_CLOSURE'
        }
    )


def test_2_representational_closure():
    reference = Fraction(1, 4)
    active = Fraction(3, 4)
    total = reference + active
    passed = total == Fraction(1, 1)

    return make_test_record(
        'TEST_2',
        'REPRESENTATIONAL_CLOSURE',
        'Complementary closure of the representation 1/4 <-> 3/4.',
        'Calculate 1/4 + 3/4 with exact rational arithmetic.',
        'To verify that this assigned representational pair closes exactly to one whole.',
        'The sum must be exactly 1.',
        'Observed exact sum: ' + str(total) + '.',
        passed,
        {
            'reference': reference,
            'active': active,
            'sum': total,
            'closure_target': Fraction(1, 1),
            'layer': 'REPRESENTATION',
            'test_function': 'COMPLEMENTARY_CLOSURE'
        }
    )


def test_3_rx8_capsulation():
    r_symbol = 'R'
    diameter_coefficient = Fraction(2, 1)
    square_sides = 4
    perimeter_coefficient = diameter_coefficient * square_sides
    expected = Fraction(8, 1)
    passed = perimeter_coefficient == expected

    return make_test_record(
        'TEST_3',
        'RX8_STRUCTURAL_CAPSULATION',
        'Rx8 structural capsulation: 2R x 4 = 8R.',
        'Multiply the symbolic diameter coefficient 2 by four square sides.',
        'To verify the assigned Rx8 structural coefficient without assigning a numerical magnitude to R.',
        'The perimeter coefficient must be exactly 8.',
        'Observed perimeter coefficient: ' + str(perimeter_coefficient) + ', representing 8R.',
        passed,
        {
            'R_status': 'SYMBOLIC_NOT_MEASURED',
            'R_symbol': r_symbol,
            'diameter': '2R',
            'square_sides': square_sides,
            'calculation': '2R * 4 = 8R',
            'perimeter_coefficient': perimeter_coefficient,
            'expected_coefficient': expected,
            'layer': 'STRUCTURE_RECONSTRUCTION'
        }
    )


def test_4_proportion_preservation():
    exact_active = Fraction(3, 4)
    exact_reference = Fraction(1, 4)
    decimal_active = 0.75
    decimal_reference = 0.25

    active_preserved = float(exact_active) == decimal_active
    reference_preserved = float(exact_reference) == decimal_reference
    exact_sum_preserved = exact_active + exact_reference == Fraction(1, 1)
    decimal_sum_preserved = decimal_active + decimal_reference == 1.0

    exact_ratio = exact_active / exact_reference
    decimal_ratio = decimal_active / decimal_reference
    ratio_preserved = decimal_ratio == float(exact_ratio)

    passed = (
        active_preserved
        and reference_preserved
        and exact_sum_preserved
        and decimal_sum_preserved
        and ratio_preserved
    )

    return make_test_record(
        'TEST_4',
        'PROPORTION_PRESERVATION',
        'Preservation of 3/4 <-> 1/4 as 0.75 <-> 0.25.',
        'Compare exact values, complementary closure, and the internal ratio before and after decimal representation.',
        'To verify actual proportional identity across this specific representational transformation.',
        '3/4 -> 0.75, 1/4 -> 0.25, both sums must equal 1, and both internal ratios must equal 3.',
        (
            'Observed exact ratio: '
            + str(exact_ratio)
            + '; decimal ratio: '
            + str(decimal_ratio)
            + '; decimal sum: '
            + str(decimal_active + decimal_reference)
            + '.'
        ),
        passed,
        {
            'exact_active': exact_active,
            'exact_reference': exact_reference,
            'decimal_active': decimal_active,
            'decimal_reference': decimal_reference,
            'exact_sum': exact_active + exact_reference,
            'decimal_sum': decimal_active + decimal_reference,
            'exact_ratio': exact_ratio,
            'decimal_ratio': decimal_ratio,
            'active_preserved': active_preserved,
            'reference_preserved': reference_preserved,
            'exact_sum_preserved': exact_sum_preserved,
            'decimal_sum_preserved': decimal_sum_preserved,
            'ratio_preserved': ratio_preserved,
            'test_function': 'PROPORTIONAL_IDENTITY'
        }
    )


def test_5_residual_position():
    exact_ratio = Fraction(3, 4)
    exact_lock = Fraction(1, 4)

    ri_float = math.sqrt(3.0) / 2.0
    observed_ratio = ri_float * ri_float
    observed_lock = 1.0 - observed_ratio

    expected_ratio = float(exact_ratio)
    expected_lock = float(exact_lock)

    ratio_residual = observed_ratio - expected_ratio
    lock_residual = observed_lock - expected_lock
    residual_sum = ratio_residual + lock_residual

    symmetric_residual = math.isclose(
        residual_sum,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-30
    )
    exact_relation_intact = (
        exact_ratio + exact_lock == Fraction(1, 1)
    )

    passed = symmetric_residual and exact_relation_intact

    return make_test_record(
        'TEST_5',
        'RESIDUAL_POSITION',
        'Residual position between the exact 3/4 <-> 1/4 reference and its machine-computed geometric representation.',
        'Compute sqrt(3)/2 in binary floating point, square it, compare it with exact 3/4, and isolate the complementary residual pair.',
        'To verify that the machine-representation residual is symmetric while the exact complementary reference remains intact.',
        'The residual pair must sum to zero within the assigned tolerance, and the exact 3/4 + 1/4 relation must remain exactly 1.',
        (
            'Ratio residual: '
            + format(ratio_residual, '.20e')
            + '; lock residual: '
            + format(lock_residual, '.20e')
            + '; residual sum: '
            + format(residual_sum, '.20e')
            + '.'
        ),
        passed,
        {
            'exact_ratio': exact_ratio,
            'exact_lock': exact_lock,
            'exact_sum': exact_ratio + exact_lock,
            'ri_float': format(ri_float, '.20e'),
            'observed_ratio_float': format(observed_ratio, '.20e'),
            'observed_lock_float': format(observed_lock, '.20e'),
            'expected_ratio_float': format(expected_ratio, '.20e'),
            'expected_lock_float': format(expected_lock, '.20e'),
            'ratio_residual': format(ratio_residual, '.20e'),
            'lock_residual': format(lock_residual, '.20e'),
            'residual_sum': format(residual_sum, '.20e'),
            'symmetric_residual': symmetric_residual,
            'exact_relation_intact': exact_relation_intact,
            'layer': 'REPRESENTATION_TRACE'
        }
    )


def test_6_internal_validation(previous_tests):
    failed = [
        test
        for test in previous_tests
        if test['final_result'] != 'PASS'
    ]
    passed = len(failed) == 0

    controls = [
        'RELATIONAL CLOSURE: 1/3 + 2/3 = 1',
        'REPRESENTATIONAL CLOSURE: 1/4 + 3/4 = 1',
        'RX8 STRUCTURE: 2R x 4 = 8R',
        'PROPORTION PRESERVATION: 3/4 <-> 1/4 = 0.75 <-> 0.25 with ratio 3:1 preserved',
        'RESIDUAL POSITION: symmetric machine-representation trace'
    ]

    return make_test_record(
        'TEST_6',
        'INTERNAL_VALIDATION_LOCK',
        'Combined status of the five independent internal controls executed by this code.',
        'Collect TEST_1 through TEST_5 and require every assigned control to return PASS.',
        'To provide one final status for this self-contained code without claiming that different mathematical relations share one invariant proportion.',
        'All five preceding internal controls must return PASS.',
        'Number of failed preceding controls: ' + str(len(failed)) + '.',
        passed,
        {
            'controls': controls,
            'failed_tests': [test['test_id'] for test in failed],
            'all_previous_tests_passed': passed,
            'scope': 'INTERNAL_TO_THIS_CODE_ONLY'
        }
    )


def build_markdown(summary, tests):
    lines = []
    lines.extend([
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
        '# RP9 RX8 PROPORTION STRUCTURE VALIDATOR',
        '',
        '## GLOBAL RESULT',
        '',
        '```text',
        'STATUS: ' + summary['global_status'],
        'PYTHON CODE ID: ' + PYTHON_CODE_ID,
        'OFFICIAL CODE TITLE: ' + OFFICIAL_CODE_TITLE,
        'VERSION: ' + summary['version'],
        'GENERATED: ' + summary['generated_at'],
        '```',
        '',
    ])
    lines.append('---')
    lines.append('')
    lines.append('## PURPOSE')
    lines.append('')
    lines.append('This is a self-contained Rx8 validation code.')
    lines.append('')
    lines.append(
        'It independently tests complementary closure, Rx8 structural '
        'capsulation, one explicitly preserved proportional identity, '
        'and residual position.'
    )
    lines.append('')
    lines.append(
        'It does not treat 1/3 <-> 2/3 and 1/4 <-> 3/4 as the same proportion.'
    )
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## INTERNAL CONTROLS')
    lines.append('')
    lines.append('```text')
    lines.append('RELATIONAL CLOSURE: 1/3 + 2/3 = 1')
    lines.append('')
    lines.append('REPRESENTATIONAL CLOSURE: 1/4 + 3/4 = 1')
    lines.append('')
    lines.append('RX8 STRUCTURE: 2R x 4 = 8R')
    lines.append('')
    lines.append('PROPORTION PRESERVATION:')
    lines.append('3/4 <-> 1/4')
    lines.append('down')
    lines.append('0.75 <-> 0.25')
    lines.append('ratio 3:1 preserved')
    lines.append('')
    lines.append('RESIDUAL: symmetric machine-representation trace')
    lines.append('```')
    lines.append('')
    lines.append('---')
    lines.append('')

    for test in tests:
        lines.append('## ' + test['test_id'] + ' - ' + test['title'])
        lines.append('')
        lines.append('### What is tested')
        lines.append('')
        lines.append(test['what_is_tested'])
        lines.append('')
        lines.append('### How it is tested')
        lines.append('')
        lines.append(test['how_it_is_tested'])
        lines.append('')
        lines.append('### Why it is tested')
        lines.append('')
        lines.append(test['why_it_is_tested'])
        lines.append('')
        lines.append('### Expected result')
        lines.append('')
        lines.append(test['expected_result'])
        lines.append('')
        lines.append('### Observed result')
        lines.append('')
        lines.append(test['observed_result'])
        lines.append('')
        lines.append('### Final result')
        lines.append('')
        lines.append('```text')
        lines.append(test['final_result'])
        lines.append('```')
        lines.append('')
        lines.append('---')
        lines.append('')

    lines.append('## CONCLUSION')
    lines.append('')

    if summary['global_status'] == 'PASS':
        lines.append('All assigned internal controls passed.')
        lines.append('')
        lines.append(
            'The two complementary closures are independently exact; '
            'Rx8 returns the assigned structural coefficient 8; '
            'the 3/4 <-> 1/4 relation preserves its 3:1 internal ratio '
            'as 0.75 <-> 0.25; and the tested machine residual pair is symmetric.'
        )
        lines.append('')
        lines.append(
            'No claim of proportional identity is made between '
            '1/3 <-> 2/3 and 1/4 <-> 3/4.'
        )
    else:
        lines.append('At least one assigned internal control failed.')

    lines.append('')
    return '\n'.join(lines)


def build_control_log(summary, tests, out_dir):
    lines = []
    lines.append('RP9 RX8 PROPORTION STRUCTURE VALIDATOR CONTROL LOG')
    lines.append('Generated: ' + summary['generated_at'])
    lines.append('Python Code ID: ' + PYTHON_CODE_ID)
    lines.append('Official Code Title: ' + OFFICIAL_CODE_TITLE)
    lines.append('File: ' + FILE_NAME)
    lines.append('Version: ' + summary['version'])
    lines.append('Output directory: ' + str(out_dir))
    lines.append('Global status: ' + summary['global_status'])
    lines.append('')

    for test in tests:
        lines.append(
            test['test_id']
            + ' | '
            + test['final_result']
            + ' | '
            + test['title']
        )
        lines.append('WHAT: ' + test['what_is_tested'])
        lines.append('HOW: ' + test['how_it_is_tested'])
        lines.append('WHY: ' + test['why_it_is_tested'])
        lines.append('RESULT: ' + test['observed_result'])
        lines.append('')

    return '\n'.join(lines)


def run_validator():
    out_dir = make_output_dir()

    tests = [
        test_1_relational_closure(),
        test_2_representational_closure(),
        test_3_rx8_capsulation(),
        test_4_proportion_preservation(),
        test_5_residual_position()
    ]
    tests.append(test_6_internal_validation(tests))

    global_pass = all(
        test['final_result'] == 'PASS'
        for test in tests
    )
    global_status = status(global_pass)

    summary = {
        'system': 'RP9_RX8',
        'validation': 'SELF_CONTAINED_PROPORTION_STRUCTURE_VALIDATION',
        'repository': 'RP9. RH. Z0',
        'repository_branch': '2. RP9. EXPANSION',
        'python_code_id': PYTHON_CODE_ID,
        'filesystem_name': FILE_NAME,
        'official_code_title': OFFICIAL_CODE_TITLE,
        'version': SCRIPT_VERSION,
        'generated_at': now_iso(),
        'global_status': global_status,
        'code_independence': True,
        'external_rp9_code_dependency': False,
        'principle': (
            'Complementary closure and proportional identity are distinct '
            'validation functions.'
        ),
        'validation_boundary': (
            'This code validates only its internally assigned closure, '
            'Rx8 structural, proportional-preservation, and residual controls.'
        )
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
                all(
                    key in test
                    for key in [
                        'what_is_tested',
                        'how_it_is_tested',
                        'why_it_is_tested',
                        'final_result'
                    ]
                )
                for test in tests
            ),
            'self_contained_execution': True,
            'external_rp9_code_dependency': False,
            'relational_closure_separated_from_proportional_identity': True,
            'cross_relation_proportional_invariance_claimed': False,
            'global_status': global_status
        }
    }

    verify_payload = {
        'VERIFY': {
            'test_1_relational_closure':
                tests[0]['final_result'] == 'PASS',
            'test_2_representational_closure':
                tests[1]['final_result'] == 'PASS',
            'test_3_rx8_capsulation':
                tests[2]['final_result'] == 'PASS',
            'test_4_proportion_preservation':
                tests[3]['final_result'] == 'PASS',
            'test_5_residual_position':
                tests[4]['final_result'] == 'PASS',
            'test_6_internal_validation':
                tests[5]['final_result'] == 'PASS',
            'global_status': global_status
        }
    }

    write_json(
        out_dir / DATA_FILE,
        payload
    )
    write_json(
        out_dir / TRACE_FILE,
        trace_payload
    )
    write_json(
        out_dir / AUDIT_FILE,
        audit_payload
    )
    write_json(
        out_dir / VERIFY_FILE,
        verify_payload
    )

    markdown = build_markdown(summary, tests)
    write_text(
        out_dir / REPORT_FILE,
        markdown
    )

    control_log = build_control_log(summary, tests, out_dir)
    write_text(
        out_dir / CONTROL_FILE,
        control_log
    )

    print('=' * 72)
    print('RP9 RX8 PROPORTION STRUCTURE VALIDATOR')
    print('STATUS:', global_status)
    print('OUTPUT:', out_dir)
    print('=' * 72)

    for test in tests:
        print(
            test['test_id']
            + ' | '
            + test['final_result']
            + ' | '
            + test['title']
        )

    print('=' * 72)

    return 0 if global_pass else 1


if __name__ == '__main__':
    exit_code = run_validator()
    sys.exit(exit_code)

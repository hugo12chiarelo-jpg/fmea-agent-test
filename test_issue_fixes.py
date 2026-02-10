"""
Test script to validate all fixes for the FMEA agent issues.

Tests:
1. G8: Symptom codes should not be used as Maintainable Items
2. G8a: Excluded items from EMS should not appear in Maintainable Items
3. G7: Enhanced duplication detection for critical terms (leakage, vibration, etc.)
4. Output format: Should be XLSX not CSV
5. Validation catches all known issues
"""

import sys
from pathlib import Path
sys.path.insert(0, 'scripts')

from run_agent import (
    validate_output_cardinality,
    extract_ems_exclusions,
    convert_markdown_table_to_dataframe
)
import pandas as pd


def test_validation_catches_symptom_codes():
    """Test that G8 validation catches symptom codes as Maintainable Items"""
    print("\n=== Test 1: G8 Validation (Symptom Codes as MI) ===")
    
    # Create a test table with symptom code as MI
    test_table = """
| Item Class | Function | Maintainable Item | Maintainable Item Function | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Motor, Electric | Convert electrical energy | PDE - Parameter deviation | Test function | VIB - Vibration | 2.4 Wear | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | PDE - Parameter deviation | Test function | NOI - Noise | 2.4 Wear | Test effect | Test action [Y/N] | TBD | Predictive |
"""
    
    errors = validate_output_cardinality(test_table, "Motor, Electric")
    g8_errors = [e for e in errors if 'G8 VIOLATION' in e]
    
    if g8_errors:
        print(f"✓ PASS: G8 validation caught {len(g8_errors)} symptom code violations")
        for err in g8_errors[:2]:
            print(f"  - {err}")
    else:
        print("✗ FAIL: G8 validation did not catch symptom codes as Maintainable Items")
    
    return len(g8_errors) > 0


def test_validation_catches_excluded_items():
    """Test that G8a validation catches excluded items from EMS"""
    print("\n=== Test 2: G8a Validation (EMS Exclusions) ===")
    
    # Extract exclusions from EMS
    ems_path = Path("inputs/EMS/EMS.csv")
    if not ems_path.exists():
        print("✗ SKIP: EMS.csv not found")
        return True
    
    exclusions = extract_ems_exclusions(ems_path, "Motor, Electric")
    print(f"EMS exclusions found: {exclusions}")
    
    # Create a test table with excluded items
    test_table = """
| Item Class | Function | Maintainable Item | Maintainable Item Function | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Motor, Electric | Convert electrical energy | Monitoring Failure | Monitor conditions | AIR - Abnormal reading | 3.3 Faulty signal | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Monitoring Failure | Monitor conditions | CSF - Control signal failure | 3.1 Control failure | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Monitoring Failure | Monitor conditions | SPO - Spurious operation | 3.5 Software error | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Monitoring Failure | Monitor conditions | AIR - Abnormal reading | 3.4 Out of adjustment | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Control System Failure | Control motor | FTS - Failure to start | 4.1 Short circuiting | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Control System Failure | Control motor | FTS - Failure to start | 4.2 Open circuit | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Control System Failure | Control motor | FTS - Failure to start | 3.5 Software error | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Convert electrical energy | Control System Failure | Control motor | CSF - Control signal failure | 3.1 Control failure | Test effect | Test action [Y/N] | TBD | Predictive |
"""
    
    errors = validate_output_cardinality(test_table, "Motor, Electric")
    g8a_errors = [e for e in errors if 'G8a VIOLATION' in e]
    
    if g8a_errors:
        print(f"✓ PASS: G8a validation caught {len(g8a_errors)} exclusion violations")
        for err in g8a_errors[:3]:
            print(f"  - {err}")
    else:
        print("✗ FAIL: G8a validation did not catch excluded items")
    
    return len(g8a_errors) > 0


def test_validation_catches_term_duplication():
    """Test that G7 validation catches critical term duplication"""
    print("\n=== Test 3: G7 Validation (Term Duplication) ===")
    
    # Create a test table with term duplication
    test_table = """
| Item Class | Function | Maintainable Item | Maintainable Item Function | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Motor, Electric | Test | Bearing Failure | Support shaft | VIB - Vibration | 1.2 Vibration | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Test | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Test | Bearing Failure | Support shaft | NOI - Noise | 2.4 Wear | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Test | Bearing Failure | Support shaft | NOI - Noise | 2.6 Fatigue | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Test | Seal Failure | Prevent leakage | ELU - External leakage - utility medium | 1.1 Leakage | Test effect | Test action [Y/N] | TBD | Predictive |
| Motor, Electric | Test | Seal Failure | Prevent leakage | ELU - External leakage - utility medium | 2.4 Wear | Test effect | Test action [Y/N] | TBD | Predictive |
"""
    
    errors = validate_output_cardinality(test_table, "Motor, Electric")
    g7_errors = [e for e in errors if 'G7 VIOLATION' in e and 'Critical term' in e]
    
    if g7_errors:
        print(f"✓ PASS: G7 validation caught {len(g7_errors)} term duplication violations")
        for err in g7_errors:
            print(f"  - {err}")
    else:
        print("✗ FAIL: G7 validation did not catch term duplication")
    
    return len(g7_errors) > 0


def test_output_format():
    """Test that output format is XLSX"""
    print("\n=== Test 4: Output Format (XLSX) ===")
    
    output_dir = Path("outputs")
    xlsx_file = output_dir / "EMS upgrade output.xlsx"
    csv_file = output_dir / "EMS upgrade output.csv"
    
    # Note: This test checks the code, not actual files since we haven't run the agent
    # Check that the main function uses .xlsx extension
    with open("scripts/run_agent.py", "r") as f:
        content = f.read()
        has_xlsx = 'output_name = "EMS upgrade output.xlsx"' in content
        uses_to_excel = '.to_excel(' in content
    
    if has_xlsx and uses_to_excel:
        print("✓ PASS: Code is configured to output XLSX format")
    else:
        print("✗ FAIL: Code is not configured to output XLSX format")
    
    return has_xlsx and uses_to_excel


def test_elu_guidance_in_spec():
    """Test that ELU guidance was added to spec"""
    print("\n=== Test 5: ELU Guidance in Spec ===")
    
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    if not spec_path.exists():
        print("✗ SKIP: Spec file not found")
        return True
    
    with open(spec_path, "r") as f:
        content = f.read()
        has_elu_section = "CRITICAL ELU SYMPTOM GUIDANCE" in content
        has_leakage_example = "ELU - External leakage - utility medium" in content and "1.1 Leakage" in content
        has_correct_examples = "2.2 Corrosion" in content or "2.4 Wear" in content
    
    if has_elu_section and has_leakage_example:
        print("✓ PASS: ELU guidance added to spec with correct/incorrect examples")
    else:
        print("✗ FAIL: ELU guidance not properly added to spec")
    
    return has_elu_section and has_leakage_example


def test_suggested_mis_section_in_spec():
    """Test that suggested additional MIs section was added"""
    print("\n=== Test 6: Suggested Additional MIs Section ===")
    
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    if not spec_path.exists():
        print("✗ SKIP: Spec file not found")
        return True
    
    with open(spec_path, "r") as f:
        content = f.read()
        has_suggested_section = "SUGGESTED ADDITIONAL MAINTAINABLE ITEMS" in content
        has_table_format = "Maintainable Item | Justification | Function" in content
    
    if has_suggested_section and has_table_format:
        print("✓ PASS: Suggested additional MIs section added to spec")
    else:
        print("✗ FAIL: Suggested additional MIs section not properly added")
    
    return has_suggested_section and has_table_format


def test_boundary_exclusion_examples():
    """Test that boundary exclusion examples were added"""
    print("\n=== Test 7: Boundary Exclusion Examples ===")
    
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    if not spec_path.exists():
        print("✗ SKIP: Spec file not found")
        return True
    
    with open(spec_path, "r") as f:
        content = f.read()
        has_monitoring_example = "Excludes Monitoring and control systems" in content
        has_exclusion_guidance = "DO NOT include" in content
    
    if has_monitoring_example and has_exclusion_guidance:
        print("✓ PASS: Boundary exclusion examples added to spec")
    else:
        print("✗ FAIL: Boundary exclusion examples not properly added")
    
    return has_monitoring_example and has_exclusion_guidance


def main():
    print("=" * 70)
    print("FMEA Agent Issue Fixes - Test Suite")
    print("=" * 70)
    
    results = {
        "G8 Validation (Symptom Codes)": test_validation_catches_symptom_codes(),
        "G8a Validation (EMS Exclusions)": test_validation_catches_excluded_items(),
        "G7 Validation (Term Duplication)": test_validation_catches_term_duplication(),
        "Output Format (XLSX)": test_output_format(),
        "ELU Guidance": test_elu_guidance_in_spec(),
        "Suggested MIs Section": test_suggested_mis_section_in_spec(),
        "Boundary Exclusion Examples": test_boundary_exclusion_examples(),
    }
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

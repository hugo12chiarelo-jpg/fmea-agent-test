#!/usr/bin/env python3
"""
Test the Electric Motor specific fixes for MI filtering and validation.
"""

from pathlib import Path
import sys
sys.path.insert(0, 'scripts')

from run_agent import (
    build_mi_list_from_ems_and_catalog,
    validate_mi_in_table,
    build_item_class_specific_guidance,
)


def test_mi_filtering():
    """Test that MI list filtering works correctly for Electric Motor."""
    print("\n=== Testing MI Filtering for Electric Motor ===")
    
    ems_csv = Path("inputs/EMS/EMS.csv")
    mi_catalog = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
    item_class = "Motor, Electric"
    
    mi_list = build_mi_list_from_ems_and_catalog(ems_csv, item_class, mi_catalog)
    
    print(f"\n✓ Found {len(mi_list)} Maintainable Items:")
    for mi in mi_list:
        print(f"  - {mi}")
    
    # Verify invalid items are filtered out
    invalid_items = ["Motor", "Shaft", "system", "stem", "gear"]
    for invalid in invalid_items:
        if invalid in mi_list or invalid.capitalize() in mi_list:
            print(f"\n✗ FAILED: Invalid item '{invalid}' not filtered out")
            return False
    
    print(f"\n✓ All invalid items filtered out: {invalid_items}")
    
    # Verify critical items are present
    critical_items = [
        "Bearing", "Rotor", "Stator", "Windings", "Coupling", 
        "Gearbox", "Brushes", "Cooling system", "Enclosure", 
        "Control system", "Junction box", "Heaters", "Monitoring"
    ]
    
    missing_critical = []
    for critical in critical_items:
        if critical not in mi_list:
            missing_critical.append(critical)
    
    if missing_critical:
        print(f"\n✗ FAILED: Missing critical items: {missing_critical}")
        return False
    
    print(f"✓ All {len(critical_items)} critical items present")
    
    return True


def test_table_validation():
    """Test that table validation correctly identifies missing MIs."""
    print("\n=== Testing Table Validation ===")
    
    # Test case 1: Complete output (all MIs in table)
    complete_output = """
| Item Class     | Function | Maintainable Item | Symptom | Failure Mechanism |
|----------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert  | Bearing Failure   | VIB     | Wear              |
| Motor, Electric | Convert  | Rotor Failure     | VIB     | Fatigue           |
| Motor, Electric | Convert  | Stator Failure    | OHE     | Short circuit     |
"""
    
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    missing = validate_mi_in_table(complete_output, mandatory_mi)
    
    if missing:
        print(f"\n✗ FAILED: False positive - detected missing items: {missing}")
        return False
    
    print("✓ Complete table correctly validated (no missing items)")
    
    # Test case 2: Incomplete output (MI only in summary, not in table)
    incomplete_output = """
| Item Class     | Function | Maintainable Item | Symptom | Failure Mechanism |
|----------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert  | Bearing Failure   | VIB     | Wear              |

---

Most probable maintainable items:
- Bearing Failure
- Rotor Failure
- Stator Failure
"""
    
    missing = validate_mi_in_table(incomplete_output, mandatory_mi)
    
    if "Rotor" not in missing or "Stator" not in missing:
        print(f"\n✗ FAILED: Did not detect missing items in table. Found missing: {missing}")
        return False
    
    print(f"✓ Incomplete table correctly identified missing items: {missing}")
    
    # Test case 3: MI without " Failure" suffix in table
    no_suffix_output = """
| Item Class     | Function | Maintainable Item | Symptom | Failure Mechanism |
|----------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert  | Bearing          | VIB     | Wear              |
| Motor, Electric | Convert  | Rotor            | VIB     | Fatigue           |
| Motor, Electric | Convert  | Stator           | OHE     | Short circuit     |
"""
    
    missing = validate_mi_in_table(no_suffix_output, mandatory_mi)
    
    if missing:
        print(f"\n✗ FAILED: Should accept MI names without 'Failure' suffix. Missing: {missing}")
        return False
    
    print("✓ Correctly accepts MI names with or without ' Failure' suffix")
    
    return True


def test_guidance_generation():
    """Test that item-class-specific guidance is generated correctly."""
    print("\n=== Testing Guidance Generation ===")
    
    guidance = build_item_class_specific_guidance("Motor, Electric")
    
    # Check that key rules are present in guidance
    required_rules = [
        "LOO - Low Output",
        "Rotor",
        "Bearing",
        "Stator",
        "4.1 - Short Circuiting",
        "1.5 - Looseness",
        "Windings",
        "NOO - No output",
        "placeholder",
        "Failure",
    ]
    
    missing_rules = []
    for rule in required_rules:
        if rule not in guidance:
            missing_rules.append(rule)
    
    if missing_rules:
        print(f"\n✗ FAILED: Guidance missing required rules: {missing_rules}")
        return False
    
    print(f"✓ Guidance includes all {len(required_rules)} required rules")
    
    # Test that other item classes don't get the same guidance
    other_guidance = build_item_class_specific_guidance("Centrifugal Pump")
    
    if "LOO - Low Output" in other_guidance:
        print("\n✗ FAILED: Non-motor item classes should not get motor-specific guidance")
        return False
    
    print("✓ Guidance is item-class-specific (not applied to other classes)")
    
    return True


def main():
    """Run all tests."""
    print("="*70)
    print("Testing Electric Motor FMEA Agent Fixes")
    print("="*70)
    
    tests = [
        ("MI Filtering", test_mi_filtering),
        ("Table Validation", test_table_validation),
        ("Guidance Generation", test_guidance_generation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ FAILED: {test_name} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

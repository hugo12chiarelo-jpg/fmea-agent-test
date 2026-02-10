#!/usr/bin/env python3
"""
Test extended equipment classification including shutdown valves, filters, strainers, and membranes.
"""

import sys
sys.path.insert(0, 'scripts')

from run_agent import _is_complex_equipment


def test_shutdown_valve_classification():
    """Test that shutdown valves are classified as complex equipment."""
    print("\n=== Testing Shutdown Valve Classification ===")
    
    shutdown_valve_items = [
        "Valve, Shutdown",
        "Shutdown Valve",
        "Emergency Shutdown Valve",
        "ESD Valve",
        "ESDV",
    ]
    
    for item in shutdown_valve_items:
        is_complex = _is_complex_equipment(item)
        status = "✓" if is_complex else "✗ FAILED"
        print(f"{status} '{item}' -> Complex: {is_complex}")
        if not is_complex:
            return False
    
    print("\n✓ All shutdown valves classified as complex")
    return True


def test_simple_equipment_extended():
    """Test that filters, strainers, and membranes are classified as simple equipment."""
    print("\n=== Testing Extended Simple Equipment Classification ===")
    
    simple_items = [
        "Filter",
        "Strainer",
        "Membrane",
        "Transmitter",
        "Valve, Manual",
        "Simple Valve",
    ]
    
    for item in simple_items:
        is_complex = _is_complex_equipment(item)
        is_simple = not is_complex
        status = "✓" if is_simple else "✗ FAILED"
        print(f"{status} '{item}' -> Simple: {is_simple}")
        if not is_simple:
            return False
    
    print("\n✓ All extended simple equipment classified correctly")
    return True


def test_complex_equipment_comprehensive():
    """Test comprehensive list of complex equipment."""
    print("\n=== Testing Comprehensive Complex Equipment ===")
    
    complex_items = [
        "Motor, Electric",
        "Turbine, Gas",
        "Compressor, Centrifugal",
        "Pump, Centrifugal",
        "Valve, Shutdown",
        "Heat Exchanger",
        "Separator",
    ]
    
    for item in complex_items:
        is_complex = _is_complex_equipment(item)
        status = "✓" if is_complex else "✗ FAILED"
        print(f"{status} '{item}' -> Complex: {is_complex}")
        if not is_complex:
            return False
    
    print("\n✓ All complex equipment classified correctly")
    return True


if __name__ == "__main__":
    all_tests_passed = []
    
    try:
        all_tests_passed.append(test_shutdown_valve_classification())
        all_tests_passed.append(test_simple_equipment_extended())
        all_tests_passed.append(test_complex_equipment_comprehensive())
        
        if all(all_tests_passed):
            print("\n" + "="*50)
            print("✓ ALL EXTENDED CLASSIFICATION TESTS PASSED")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("✗ SOME TESTS FAILED")
            print("="*50)
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

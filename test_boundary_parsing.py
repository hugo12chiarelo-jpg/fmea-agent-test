#!/usr/bin/env python3
"""
Test script to verify boundary parsing improvements.

This script tests that the FMEA agent correctly:
1. Parses EMS boundaries to identify included/excluded items
2. Filters out items marked as "Exclude", "optional", "if applicable"
3. Maps boundary terms to Maintainable Item Catalog terminology
4. Handles the COCE (Centrifugal Compressor) example correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from run_agent import build_mi_list_from_ems_and_catalog


def test_coce_boundaries():
    """Test boundary parsing for COCE (Centrifugal Compressor)."""
    ems_path = Path("inputs/EMS/EMS.csv")
    mi_catalog_path = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
    
    if not ems_path.exists() or not mi_catalog_path.exists():
        print("❌ Required files not found")
        return False
    
    result = build_mi_list_from_ems_and_catalog(ems_path, "COCE", mi_catalog_path)
    
    print(f"Found {len(result)} Maintainable Items for COCE")
    print()
    
    # Test items that SHOULD BE INCLUDED (mentioned in boundaries, not excluded)
    should_include = {
        "coupling": "Compressor and coupling between driver and compressor",
        "seal": "Dry gas seal system, Primary, secondary seal and tertiary",
        "dry gas seal": "Dry gas seal system",
        "instrument": "Local instrumentation, relevant instrumentation",
        "lubrication": "Lubrication package when children of centrifugal compressor",
        "monitoring": "Vibration and temperature monitoring system",
        "plc": "Unit Control Panel, PLC when children of the centrifugal compressor",
        "pump": "Main/Auxiliary/Emergency pumps and respective driver",
        "cooler": "Oil cooler, cooling system",
    }
    
    # Test items that SHOULD BE EXCLUDED
    should_exclude = {
        "gearbox": "Exclude Gearbox",
        "fire": "Exclude Fire & Gas",
    }
    
    # Note: "driver" is excluded as standalone but included in compounds like "Coupling to driver"
    # This is correct per the boundaries which say "Exclude Driver" but include "coupling between driver and compressor"
    
    passed = 0
    failed = 0
    
    print("✓ Testing INCLUDED items:")
    for key, reason in should_include.items():
        matches = [mi for mi in result if key in mi.lower()]
        if matches:
            print(f"  ✓ {key:15s} → {matches[0]}")
            passed += 1
        else:
            print(f"  ✗ {key:15s} → NOT FOUND (expected from: {reason})")
            failed += 1
    
    print()
    print("✓ Testing EXCLUDED items:")
    for key, reason in should_exclude.items():
        matches = [mi for mi in result if key in mi.lower()]
        if not matches:
            print(f"  ✓ {key:15s} → correctly excluded")
            passed += 1
        else:
            print(f"  ✗ {key:15s} → INCORRECTLY INCLUDED: {matches}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def main():
    print("Testing FMEA Boundary Parsing Improvements")
    print("=" * 80)
    print()
    
    success = test_coce_boundaries()
    
    print()
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

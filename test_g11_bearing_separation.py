#!/usr/bin/env python3
"""
Test the G11 quality gate for bearing failure separation (NDE/DE).
"""

import sys
sys.path.insert(0, 'scripts')

from run_agent import validate_output_cardinality


def test_generic_bearing_failure_rejected():
    """Test that generic 'Bearing Failure' is rejected."""
    print("\n=== Testing Generic Bearing Failure Rejection ===")
    
    # Mock output with generic "Bearing Failure" (should fail)
    output_with_generic_bearing = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_with_generic_bearing)
    
    # Should have G11 violation
    g11_violations = [e for e in errors if "G11 VIOLATION" in e]
    
    if len(g11_violations) == 0:
        print("✗ FAILED: Expected G11 violation for generic 'Bearing Failure'")
        print(f"All errors: {errors}")
        return False
    
    print(f"✓ G11 violation detected: {g11_violations[0]}")
    return True


def test_nde_de_bearing_accepted():
    """Test that 'NDE Bearing Failure' and 'DE Bearing Failure' are accepted."""
    print("\n=== Testing NDE/DE Bearing Failure Acceptance ===")
    
    # Mock output with NDE and DE bearings (should pass G11)
    output_with_separated_bearings = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Motor, Electric | NDE Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | NDE Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | NDE Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | NDE Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | NDE Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | NDE Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | DE Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | DE Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | DE Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | DE Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | DE Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | DE Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_with_separated_bearings)
    g11_violations = [e for e in errors if "G11 VIOLATION" in e]
    
    if len(g11_violations) > 0:
        print(f"✗ FAILED: Unexpected G11 violation for NDE/DE bearings: {g11_violations}")
        return False
    
    print("✓ No G11 violation for properly separated NDE/DE bearings")
    return True


def test_thrust_bearing_accepted():
    """Test that 'Thrust Bearing' is accepted (specific type)."""
    print("\n=== Testing Thrust Bearing Acceptance ===")
    
    # Mock output with Thrust Bearing (should pass G11)
    output_with_thrust_bearing = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Compressor | Thrust Bearing Failure | VIB - Vibration | 2.4 Wear |
| Compressor | Thrust Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Compressor | Thrust Bearing Failure | NOI - Noise | 2.4 Wear |
| Compressor | Thrust Bearing Failure | NOI - Noise | 1.5 Looseness |
| Compressor | Thrust Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Compressor | Thrust Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Compressor | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Compressor | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Compressor | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Compressor | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Compressor | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Compressor | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_with_thrust_bearing)
    g11_violations = [e for e in errors if "G11 VIOLATION" in e]
    
    if len(g11_violations) > 0:
        print(f"✗ FAILED: Unexpected G11 violation for Thrust Bearing: {g11_violations}")
        return False
    
    print("✓ No G11 violation for Thrust Bearing (specific type)")
    return True


def test_radial_bearing_accepted():
    """Test that 'Radial bearing' is accepted (from catalog)."""
    print("\n=== Testing Radial Bearing Acceptance ===")
    
    # Mock output with Radial bearing from catalog (should pass G11)
    output_with_radial_bearing = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Pump | Radial bearing | VIB - Vibration | 2.4 Wear |
| Pump | Radial bearing | VIB - Vibration | 2.6 Fatigue |
| Pump | Radial bearing | NOI - Noise | 2.4 Wear |
| Pump | Radial bearing | NOI - Noise | 1.5 Looseness |
| Pump | Radial bearing | OHE - Overheating | 1.4 Deformation |
| Pump | Radial bearing | OHE - Overheating | 2.6 Fatigue |
| Pump | Impeller Failure | VIB - Vibration | 2.6 Fatigue |
| Pump | Impeller Failure | VIB - Vibration | 2.1 Cavitation |
| Pump | Impeller Failure | NOI - Noise | 2.1 Cavitation |
| Pump | Impeller Failure | NOI - Noise | 2.3 Erosion |
| Pump | Impeller Failure | PDE - Parameter deviation | 2.3 Erosion |
| Pump | Impeller Failure | PDE - Parameter deviation | 2.2 Corrosion |
"""
    
    errors = validate_output_cardinality(output_with_radial_bearing)
    g11_violations = [e for e in errors if "G11 VIOLATION" in e]
    
    if len(g11_violations) > 0:
        print(f"✗ FAILED: Unexpected G11 violation for Radial bearing: {g11_violations}")
        return False
    
    print("✓ No G11 violation for Radial bearing (catalog name)")
    return True


def test_axial_bearing_accepted():
    """Test that 'Axial Bearing Failure' is accepted (specific type)."""
    print("\n=== Testing Axial Bearing Acceptance ===")
    
    # Mock output with Axial Bearing (should pass G11)
    output_with_axial_bearing = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Turbine | Axial Bearing Failure | VIB - Vibration | 2.4 Wear |
| Turbine | Axial Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Turbine | Axial Bearing Failure | NOI - Noise | 2.4 Wear |
| Turbine | Axial Bearing Failure | NOI - Noise | 1.5 Looseness |
| Turbine | Axial Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Turbine | Axial Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Turbine | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Turbine | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Turbine | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Turbine | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Turbine | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Turbine | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_with_axial_bearing)
    g11_violations = [e for e in errors if "G11 VIOLATION" in e]
    
    if len(g11_violations) > 0:
        print(f"✗ FAILED: Unexpected G11 violation for Axial Bearing: {g11_violations}")
        return False
    
    print("✓ No G11 violation for Axial Bearing Failure (specific type)")
    return True


if __name__ == "__main__":
    all_tests_passed = []
    
    try:
        all_tests_passed.append(test_generic_bearing_failure_rejected())
        all_tests_passed.append(test_nde_de_bearing_accepted())
        all_tests_passed.append(test_thrust_bearing_accepted())
        all_tests_passed.append(test_radial_bearing_accepted())
        all_tests_passed.append(test_axial_bearing_accepted())
        
        if all(all_tests_passed):
            print("\n" + "="*50)
            print("✓ ALL G11 BEARING VALIDATION TESTS PASSED")
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

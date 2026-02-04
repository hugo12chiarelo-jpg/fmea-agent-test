#!/usr/bin/env python3
"""
Test the G9 quality gate for minimum Maintainable Item count validation.
"""

import sys
sys.path.insert(0, 'scripts')

from run_agent import validate_output_cardinality, _is_complex_equipment


def test_complex_equipment_classification():
    """Test that equipment is correctly classified as complex or simple."""
    print("\n=== Testing Equipment Classification ===")
    
    # Complex equipment
    complex_items = [
        "Motor, Electric",
        "Pump, Centrifugal",
        "Compressor, Centrifugal",
        "Heat Exchanger",
        "Separator",
        "Generator",
        "Turbine, Gas",
    ]
    
    for item in complex_items:
        is_complex = _is_complex_equipment(item)
        status = "✓" if is_complex else "✗ FAILED"
        print(f"{status} '{item}' -> Complex: {is_complex}")
        if not is_complex:
            return False
    
    # Simple equipment
    simple_items = [
        "Transmitter",
        "Sensor",
        "Valve, Manual",
        "Lamp",
        "Indicator",
    ]
    
    for item in simple_items:
        is_complex = _is_complex_equipment(item)
        is_simple = not is_complex
        status = "✓" if is_simple else "✗ FAILED"
        print(f"{status} '{item}' -> Simple: {is_simple}")
        if not is_simple:
            return False
    
    print("\n✓ All equipment classifications correct")
    return True


def test_g9_validation_complex():
    """Test G9 validation for complex equipment."""
    print("\n=== Testing G9 Validation for Complex Equipment ===")
    
    # Mock output with only 8 MIs (should fail for complex equipment)
    # Note: Each MI needs 4-8 symptoms with 2-5 mechanisms per symptom to pass other gates
    output_with_8_mis = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Bearing Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Bearing Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Rotor Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Stator Failure | VIB - Vibration | 1.4 Deformation |
| Motor, Electric | Stator Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Stator Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Stator Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Stator Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Windings Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Windings Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Windings Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Windings Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Windings Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Coupling Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Coupling Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Coupling Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Coupling Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Coupling Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Coupling Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Coupling Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Coupling Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Brushes Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Brushes Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Brushes Failure | VIB - Vibration | 1.6 Sticking |
| Motor, Electric | Brushes Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | OHE - Overheating | 2.4 Wear |
| Motor, Electric | Brushes Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Control System Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Motor, Electric | Control System Failure | AIR - Abnormal reading | 3.3 Faulty signal |
| Motor, Electric | Control System Failure | CSF - Control failure | 3.1 Control failure |
| Motor, Electric | Control System Failure | CSF - Control failure | 3.5 Software error |
| Motor, Electric | Control System Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Motor, Electric | Control System Failure | PDE - Parameter deviation | 3.5 Software error |
| Motor, Electric | Control System Failure | FTF - Failure to function | 3.6 Common cause |
| Motor, Electric | Control System Failure | FTF - Failure to function | 3.1 Control failure |
| Motor, Electric | Cooling System Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Cooling System Failure | PDE - Parameter deviation | 5.1 Blockage |
| Motor, Electric | Cooling System Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Cooling System Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Cooling System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Cooling System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Cooling System Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Cooling System Failure | VIB - Vibration | 2.4 Wear |
"""
    
    errors = validate_output_cardinality(output_with_8_mis)
    
    # Should have G9 violation
    g9_violations = [e for e in errors if "G9 VIOLATION" in e]
    
    if len(g9_violations) == 0:
        print("✗ FAILED: Expected G9 violation for complex equipment with only 8 MIs")
        print(f"All errors: {errors}")
        return False
    
    print(f"✓ G9 violation detected: {g9_violations[0]}")
    
    # Mock output with 12 MIs (should pass G9, but note that we need to ensure all MIs have 4-8 symptoms)
    output_with_12_mis = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Bearing Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Bearing Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Rotor Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Rotor Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Stator Failure | VIB - Vibration | 1.4 Deformation |
| Motor, Electric | Stator Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Stator Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Stator Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Stator Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Windings Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Windings Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Windings Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Windings Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Windings Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Coupling Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Coupling Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Coupling Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Coupling Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Coupling Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Coupling Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Coupling Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Coupling Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Brushes Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Brushes Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Brushes Failure | VIB - Vibration | 1.6 Sticking |
| Motor, Electric | Brushes Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | OHE - Overheating | 2.4 Wear |
| Motor, Electric | Brushes Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Brushes Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Control System Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Motor, Electric | Control System Failure | AIR - Abnormal reading | 3.3 Faulty signal |
| Motor, Electric | Control System Failure | CSF - Control failure | 3.1 Control failure |
| Motor, Electric | Control System Failure | CSF - Control failure | 3.5 Software error |
| Motor, Electric | Control System Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Motor, Electric | Control System Failure | PDE - Parameter deviation | 3.5 Software error |
| Motor, Electric | Control System Failure | FTF - Failure to function | 3.6 Common cause |
| Motor, Electric | Control System Failure | FTF - Failure to function | 3.1 Control failure |
| Motor, Electric | Cooling System Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Cooling System Failure | PDE - Parameter deviation | 5.1 Blockage |
| Motor, Electric | Cooling System Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Cooling System Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Cooling System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Cooling System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Cooling System Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Cooling System Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Enclosure Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Enclosure Failure | STD - Structural damage | 2.2 Corrosion |
| Motor, Electric | Enclosure Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Enclosure Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Enclosure Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Enclosure Failure | OHE - Overheating | 5.2 Contamination |
| Motor, Electric | Enclosure Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Enclosure Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Lubrication System Failure | PDE - Parameter deviation | 5.2 Contamination |
| Motor, Electric | Lubrication System Failure | PDE - Parameter deviation | 2.5 Degradation |
| Motor, Electric | Lubrication System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Lubrication System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Lubrication System Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Lubrication System Failure | OHE - Overheating | 5.1 Blockage |
| Motor, Electric | Lubrication System Failure | VLO - Loss of oil | 1.1 Leakage |
| Motor, Electric | Lubrication System Failure | VLO - Loss of oil | 5.2 Contamination |
| Motor, Electric | Terminal Box Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Terminal Box Failure | OHE - Overheating | 1.5 Looseness |
| Motor, Electric | Terminal Box Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Terminal Box Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Terminal Box Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Terminal Box Failure | PDE - Parameter deviation | 1.5 Looseness |
| Motor, Electric | Terminal Box Failure | FWR - Failure while running | 4.1 Short circuit |
| Motor, Electric | Terminal Box Failure | FWR - Failure while running | 1.5 Looseness |
| Motor, Electric | Foundation Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Foundation Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Foundation Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Foundation Failure | STD - Structural damage | 2.6 Fatigue |
| Motor, Electric | Foundation Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Foundation Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Foundation Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Foundation Failure | PDE - Parameter deviation | 1.4 Deformation |
"""
    
    errors = validate_output_cardinality(output_with_12_mis)
    g9_violations = [e for e in errors if "G9 VIOLATION" in e]
    
    if len(g9_violations) > 0:
        print(f"✗ FAILED: Unexpected G9 violation for complex equipment with 12 MIs: {g9_violations}")
        return False
    
    print("✓ No G9 violation for complex equipment with 12 MIs")
    return True


def test_g9_validation_simple():
    """Test G9 validation for simple equipment."""
    print("\n=== Testing G9 Validation for Simple Equipment ===")
    
    # Mock output with only 3 MIs (should fail for simple equipment)
    output_with_3_mis = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Transmitter | Sensor Element Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Transmitter | Sensor Element Failure | AIR - Abnormal reading | 2.5 Degradation |
| Transmitter | Sensor Element Failure | CSF - Control failure | 3.1 Control failure |
| Transmitter | Sensor Element Failure | CSF - Control failure | 3.3 Faulty signal |
| Transmitter | Sensor Element Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Transmitter | Sensor Element Failure | PDE - Parameter deviation | 2.2 Corrosion |
| Transmitter | Sensor Element Failure | FTF - Failure to function | 3.6 Common cause |
| Transmitter | Sensor Element Failure | FTF - Failure to function | 2.5 Degradation |
| Transmitter | Power Supply Failure | FTS - Failure to start | 4.2 Open circuit |
| Transmitter | Power Supply Failure | FTS - Failure to start | 2.5 Degradation |
| Transmitter | Power Supply Failure | OHE - Overheating | 2.7 Overheating |
| Transmitter | Power Supply Failure | OHE - Overheating | 4.1 Short circuit |
| Transmitter | Power Supply Failure | AIR - Abnormal reading | 4.2 Open circuit |
| Transmitter | Power Supply Failure | AIR - Abnormal reading | 2.5 Degradation |
| Transmitter | Power Supply Failure | PDE - Parameter deviation | 4.2 Open circuit |
| Transmitter | Power Supply Failure | PDE - Parameter deviation | 2.7 Overheating |
| Transmitter | Housing Failure | STD - Structural damage | 1.4 Deformation |
| Transmitter | Housing Failure | STD - Structural damage | 2.2 Corrosion |
| Transmitter | Housing Failure | VIB - Vibration | 1.5 Looseness |
| Transmitter | Housing Failure | VIB - Vibration | 2.6 Fatigue |
| Transmitter | Housing Failure | OHE - Overheating | 2.7 Overheating |
| Transmitter | Housing Failure | OHE - Overheating | 5.2 Contamination |
| Transmitter | Housing Failure | NOI - Noise | 1.5 Looseness |
| Transmitter | Housing Failure | NOI - Noise | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_with_3_mis)
    
    # Should have G9 violation
    g9_violations = [e for e in errors if "G9 VIOLATION" in e]
    
    if len(g9_violations) == 0:
        print("✗ FAILED: Expected G9 violation for simple equipment with only 3 MIs")
        print(f"All errors: {errors}")
        return False
    
    print(f"✓ G9 violation detected: {g9_violations[0]}")
    
    # Mock output with 5 MIs (should pass G9)
    output_with_5_mis = """
| Item Class | Maintainable Item | Symptom | Failure Mechanism |
|------------|-------------------|---------|-------------------|
| Transmitter | Sensor Element Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Transmitter | Sensor Element Failure | AIR - Abnormal reading | 2.5 Degradation |
| Transmitter | Sensor Element Failure | CSF - Control failure | 3.1 Control failure |
| Transmitter | Sensor Element Failure | CSF - Control failure | 3.3 Faulty signal |
| Transmitter | Sensor Element Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Transmitter | Sensor Element Failure | PDE - Parameter deviation | 2.2 Corrosion |
| Transmitter | Sensor Element Failure | FTF - Failure to function | 3.6 Common cause |
| Transmitter | Sensor Element Failure | FTF - Failure to function | 2.5 Degradation |
| Transmitter | Power Supply Failure | FTS - Failure to start | 4.2 Open circuit |
| Transmitter | Power Supply Failure | FTS - Failure to start | 2.5 Degradation |
| Transmitter | Power Supply Failure | OHE - Overheating | 2.7 Overheating |
| Transmitter | Power Supply Failure | OHE - Overheating | 4.1 Short circuit |
| Transmitter | Power Supply Failure | AIR - Abnormal reading | 4.2 Open circuit |
| Transmitter | Power Supply Failure | AIR - Abnormal reading | 2.5 Degradation |
| Transmitter | Power Supply Failure | PDE - Parameter deviation | 4.2 Open circuit |
| Transmitter | Power Supply Failure | PDE - Parameter deviation | 2.7 Overheating |
| Transmitter | Housing Failure | STD - Structural damage | 1.4 Deformation |
| Transmitter | Housing Failure | STD - Structural damage | 2.2 Corrosion |
| Transmitter | Housing Failure | VIB - Vibration | 1.5 Looseness |
| Transmitter | Housing Failure | VIB - Vibration | 2.6 Fatigue |
| Transmitter | Housing Failure | OHE - Overheating | 2.7 Overheating |
| Transmitter | Housing Failure | OHE - Overheating | 5.2 Contamination |
| Transmitter | Housing Failure | NOI - Noise | 1.5 Looseness |
| Transmitter | Housing Failure | NOI - Noise | 2.6 Fatigue |
| Transmitter | Wiring Failure | AIR - Abnormal reading | 4.2 Open circuit |
| Transmitter | Wiring Failure | AIR - Abnormal reading | 2.2 Corrosion |
| Transmitter | Wiring Failure | CSF - Control failure | 3.3 Faulty signal |
| Transmitter | Wiring Failure | CSF - Control failure | 4.2 Open circuit |
| Transmitter | Wiring Failure | PDE - Parameter deviation | 4.2 Open circuit |
| Transmitter | Wiring Failure | PDE - Parameter deviation | 2.2 Corrosion |
| Transmitter | Wiring Failure | FTS - Failure to start | 4.2 Open circuit |
| Transmitter | Wiring Failure | FTS - Failure to start | 2.4 Wear |
| Transmitter | Mounting Failure | VIB - Vibration | 1.5 Looseness |
| Transmitter | Mounting Failure | VIB - Vibration | 1.2 Misalignment |
| Transmitter | Mounting Failure | STD - Structural damage | 1.4 Deformation |
| Transmitter | Mounting Failure | STD - Structural damage | 2.6 Fatigue |
| Transmitter | Mounting Failure | NOI - Noise | 1.5 Looseness |
| Transmitter | Mounting Failure | NOI - Noise | 2.6 Fatigue |
| Transmitter | Mounting Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Transmitter | Mounting Failure | PDE - Parameter deviation | 1.5 Looseness |
"""
    
    errors = validate_output_cardinality(output_with_5_mis)
    g9_violations = [e for e in errors if "G9 VIOLATION" in e]
    
    if len(g9_violations) > 0:
        print(f"✗ FAILED: Unexpected G9 violation for simple equipment with 5 MIs: {g9_violations}")
        return False
    
    print("✓ No G9 violation for simple equipment with 5 MIs")
    return True


if __name__ == "__main__":
    all_tests_passed = []
    
    try:
        all_tests_passed.append(test_complex_equipment_classification())
        all_tests_passed.append(test_g9_validation_complex())
        all_tests_passed.append(test_g9_validation_simple())
        
        if all(all_tests_passed):
            print("\n" + "="*50)
            print("✓ ALL G9 VALIDATION TESTS PASSED")
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

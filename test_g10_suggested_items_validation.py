#!/usr/bin/env python3
"""
Test G10 validation: SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section requirement.

This test ensures that:
- Outputs include a "SUGGESTED ADDITIONAL MAINTAINABLE ITEMS" section
- The section provides recommendations for extra MIs that can be added
- The output is rejected if this section is missing
"""

import sys
sys.path.insert(0, 'scripts')

from run_agent import validate_output_cardinality


def test_g10_fails_missing_suggested_section():
    """Test that G10 detects missing SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section"""
    print("\n=== Testing G10 Validation - Missing Suggested Section ===")
    
    # Output without SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section
    output_without_section = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Stator Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Windings Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Coupling Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Brushes Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Brushes Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Brushes Failure | VIB - Vibration | 1.6 Sticking |
| Motor, Electric | Convert energy | Brushes Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | OHE - Overheating | 2.4 Wear |
| Motor, Electric | Convert energy | Brushes Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Control System Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Control System Failure | AIR - Abnormal reading | 3.3 Faulty signal |
| Motor, Electric | Convert energy | Control System Failure | CSF - Control failure | 3.1 Control failure |
| Motor, Electric | Convert energy | Control System Failure | CSF - Control failure | 3.5 Software error |
| Motor, Electric | Convert energy | Control System Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Control System Failure | PDE - Parameter deviation | 3.5 Software error |
| Motor, Electric | Convert energy | Control System Failure | FTF - Failure to function | 3.6 Common cause |
| Motor, Electric | Convert energy | Control System Failure | FTF - Failure to function | 3.1 Control failure |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 5.1 Blockage |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Convert energy | Cooling System Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Cooling System Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Enclosure Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Convert energy | Enclosure Failure | STD - Structural damage | 2.2 Corrosion |
| Motor, Electric | Convert energy | Enclosure Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Enclosure Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Enclosure Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Enclosure Failure | OHE - Overheating | 5.2 Contamination |
| Motor, Electric | Convert energy | Enclosure Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Enclosure Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Lubrication System Failure | PDE - Parameter deviation | 5.2 Contamination |
| Motor, Electric | Convert energy | Lubrication System Failure | PDE - Parameter deviation | 2.5 Degradation |
| Motor, Electric | Convert energy | Lubrication System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Lubrication System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Convert energy | Lubrication System Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Lubrication System Failure | OHE - Overheating | 5.1 Blockage |
| Motor, Electric | Convert energy | Lubrication System Failure | VLO - Loss of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Lubrication System Failure | VLO - Loss of oil | 5.2 Contamination |
| Motor, Electric | Convert energy | Terminal Box Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | OHE - Overheating | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | PDE - Parameter deviation | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | FWR - Failure while running | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | FWR - Failure while running | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Foundation Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Convert energy | Foundation Failure | STD - Structural damage | 2.6 Fatigue |
| Motor, Electric | Convert energy | Foundation Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Foundation Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Convert energy | Foundation Failure | PDE - Parameter deviation | 1.4 Deformation |
"""
    
    errors = validate_output_cardinality(output_without_section, "Motor, Electric")
    g10_errors = [e for e in errors if 'G10 VIOLATION' in e]
    
    if len(g10_errors) == 0:
        print("✗ FAILED: Expected G10 violation for missing SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section")
        print(f"All errors: {errors}")
        return False
    
    print(f"✓ G10 violation detected: {g10_errors[0]}")
    return True


def test_g10_passes_with_suggested_section():
    """Test that G10 passes when SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section is present"""
    print("\n=== Testing G10 Validation - With Suggested Section ===")
    
    # Output with SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section
    output_with_section = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 2.1 Cavitation |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Stator Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Stator Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Windings Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Coupling Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Brushes Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Brushes Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Brushes Failure | VIB - Vibration | 1.6 Sticking |
| Motor, Electric | Convert energy | Brushes Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | OHE - Overheating | 2.4 Wear |
| Motor, Electric | Convert energy | Brushes Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Brushes Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Control System Failure | AIR - Abnormal reading | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Control System Failure | AIR - Abnormal reading | 3.3 Faulty signal |
| Motor, Electric | Convert energy | Control System Failure | CSF - Control failure | 3.1 Control failure |
| Motor, Electric | Convert energy | Control System Failure | CSF - Control failure | 3.5 Software error |
| Motor, Electric | Convert energy | Control System Failure | PDE - Parameter deviation | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Control System Failure | PDE - Parameter deviation | 3.5 Software error |
| Motor, Electric | Convert energy | Control System Failure | FTF - Failure to function | 3.6 Common cause |
| Motor, Electric | Convert energy | Control System Failure | FTF - Failure to function | 3.1 Control failure |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 5.1 Blockage |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 1.4 Deformation |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Convert energy | Cooling System Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Cooling System Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Enclosure Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Convert energy | Enclosure Failure | STD - Structural damage | 2.2 Corrosion |
| Motor, Electric | Convert energy | Enclosure Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Enclosure Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Enclosure Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Enclosure Failure | OHE - Overheating | 5.2 Contamination |
| Motor, Electric | Convert energy | Enclosure Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Enclosure Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Lubrication System Failure | PDE - Parameter deviation | 5.2 Contamination |
| Motor, Electric | Convert energy | Lubrication System Failure | PDE - Parameter deviation | 2.5 Degradation |
| Motor, Electric | Convert energy | Lubrication System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Lubrication System Failure | LOO - Leak of oil | 2.4 Wear |
| Motor, Electric | Convert energy | Lubrication System Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Lubrication System Failure | OHE - Overheating | 5.1 Blockage |
| Motor, Electric | Convert energy | Lubrication System Failure | VLO - Loss of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Lubrication System Failure | VLO - Loss of oil | 5.2 Contamination |
| Motor, Electric | Convert energy | Terminal Box Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | OHE - Overheating | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | PDE - Parameter deviation | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | PDE - Parameter deviation | 1.5 Looseness |
| Motor, Electric | Convert energy | Terminal Box Failure | FWR - Failure while running | 4.1 Short circuit |
| Motor, Electric | Convert energy | Terminal Box Failure | FWR - Failure while running | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | VIB - Vibration | 1.2 Misalignment |
| Motor, Electric | Convert energy | Foundation Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | STD - Structural damage | 1.4 Deformation |
| Motor, Electric | Convert energy | Foundation Failure | STD - Structural damage | 2.6 Fatigue |
| Motor, Electric | Convert energy | Foundation Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Foundation Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Foundation Failure | PDE - Parameter deviation | 1.2 Misalignment |
| Motor, Electric | Convert energy | Foundation Failure | PDE - Parameter deviation | 1.4 Deformation |

## SUGGESTED ADDITIONAL MAINTAINABLE ITEMS (for Engineering Review)

The following maintainable items are suggested based on ISO 14224 standards and engineering analysis:

| Maintainable Item | Justification | Expected Symptoms | Expected Failure Mechanisms |
|-------------------|---------------|-------------------|----------------------------|
| Cable Failure (*) | ISO 14224 standard MI for electric motors; critical for power transmission | OHE, FTS, FWR, AIR | 4.1 Short circuit, 4.2 Open circuit, 2.2 Corrosion |
| Shaft Seals Failure (*) | Standard sealing component for motors; prevents lubricant leakage | LOO, ELP, VIB, PDE | 2.4 Wear, 1.1 Leakage, 2.5 Degradation |
"""
    
    errors = validate_output_cardinality(output_with_section, "Motor, Electric")
    g10_errors = [e for e in errors if 'G10 VIOLATION' in e]
    
    if len(g10_errors) > 0:
        print(f"✗ FAILED: Unexpected G10 violation when section is present: {g10_errors}")
        return False
    
    print("✓ No G10 violation when SUGGESTED ADDITIONAL MAINTAINABLE ITEMS section is present")
    return True


if __name__ == "__main__":
    all_tests_passed = []
    
    try:
        all_tests_passed.append(test_g10_fails_missing_suggested_section())
        all_tests_passed.append(test_g10_passes_with_suggested_section())
        
        if all(all_tests_passed):
            print("\n" + "="*50)
            print("✓ ALL G10 VALIDATION TESTS PASSED")
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

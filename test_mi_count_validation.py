"""
Test G0a validation: Minimum Maintainable Item count based on equipment complexity.

This test ensures that:
- Complex equipment (motors, pumps, compressors, etc.) requires minimum 12 MIs
- Simple equipment (instruments, valves, lamps, etc.) requires minimum 5 MIs
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from run_agent import validate_output_cardinality, determine_equipment_complexity


def test_complex_equipment_classification():
    """Test that complex equipment is correctly classified"""
    complex_equipment = [
        "Motor, Electric",
        "Centrifugal Pump",
        "Centrifugal Compressor",
        "Heat Exchanger",
        "Gas Turbine",
        "Separator",
        "Gearbox"
    ]
    
    for equipment in complex_equipment:
        result = determine_equipment_complexity(equipment)
        assert result == "COMPLEX", f"{equipment} should be classified as COMPLEX"
    
    print(f"✓ All {len(complex_equipment)} complex equipment types correctly classified")


def test_simple_equipment_classification():
    """Test that simple equipment is correctly classified"""
    simple_equipment = [
        "Check Valve",
        "Relief Valve",
        "Pressure Transmitter",
        "Temperature Sensor",
        "Lamp",
        "Manual Valve"
    ]
    
    for equipment in simple_equipment:
        result = determine_equipment_complexity(equipment)
        assert result == "SIMPLE", f"{equipment} should be classified as SIMPLE"
    
    print(f"✓ All {len(simple_equipment)} simple equipment types correctly classified")


def test_g0a_fails_insufficient_complex_mis():
    """Test that G0a detects insufficient MIs for complex equipment (< 12)"""
    # Create FMEA output with only 8 MIs for Motor (complex, needs 12)
    output_insufficient_complex = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 1.4 Deformation |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | FTS - Failure to start | 4.2 Open circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 2.5 Burning |
| Motor, Electric | Convert energy | Windings Failure | FTS - Failure to start | 4.2 Open circuit |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Shaft Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Shaft Failure | VIB - Vibration | 1.3 Misalignment |
| Motor, Electric | Convert energy | Shaft Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Shaft Failure | STD - Structural deficiency | 2.6 Fatigue |
| Motor, Electric | Convert energy | Shaft Failure | BRD - Breakdown | 1.1 Crack |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 1.3 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Coupling Failure | STD - Structural deficiency | 2.6 Fatigue |
| Motor, Electric | Convert energy | Coupling Failure | FWR - Failure while running | 2.4 Wear |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 5.1 Blockage |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 1.1 Leakage |
| Motor, Electric | Convert energy | Cooling System Failure | FWR - Failure while running | 2.4 Wear |
| Motor, Electric | Convert energy | Junction Box Failure | ELP - External leakage | 1.1 Leakage |
| Motor, Electric | Convert energy | Junction Box Failure | ELP - External leakage | 2.2 Corrosion |
| Motor, Electric | Convert energy | Junction Box Failure | CSF - Control/Signal failure | 4.2 Open circuit |
| Motor, Electric | Convert energy | Junction Box Failure | FTS - Failure to start | 4.2 Open circuit |
| Motor, Electric | Convert energy | Junction Box Failure | STD - Structural deficiency | 2.2 Corrosion |
"""
    
    errors = validate_output_cardinality(output_insufficient_complex, "Motor, Electric")
    g0a_errors = [e for e in errors if 'G0a VIOLATION' in e]
    
    assert len(g0a_errors) > 0, "G0a should detect insufficient MI count (8 < 12 for complex)"
    assert "minimum 12" in g0a_errors[0], "Error message should mention minimum 12 MIs"
    assert "Found only 8" in g0a_errors[0], "Error message should mention found 8 MIs"
    
    print("✓ Test passed: G0a detects insufficient MIs for complex equipment (8 < 12)")


def test_g0a_passes_sufficient_complex_mis():
    """Test that G0a passes when complex equipment has 12+ MIs"""
    # Create FMEA output with exactly 12 MIs for Motor (complex)
    output_sufficient_complex = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 2.6 Fatigue |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | PDE - Parameter deviation | 1.4 Deformation |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 1.4 Deformation |
| Motor, Electric | Convert energy | Rotor Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Rotor Failure | PDE - Parameter deviation | 2.4 Wear |
| Motor, Electric | Convert energy | Stator Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Stator Failure | FTS - Failure to start | 4.2 Open circuit |
| Motor, Electric | Convert energy | Windings Failure | OHE - Overheating | 4.1 Short circuit |
| Motor, Electric | Convert energy | Windings Failure | FTS - Failure to start | 4.2 Open circuit |
| Motor, Electric | Convert energy | Windings Failure | VIB - Vibration | 1.5 Looseness |
| Motor, Electric | Convert energy | Windings Failure | NOI - Noise | 4.1 Short circuit |
| Motor, Electric | Convert energy | Shaft Failure | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Shaft Failure | NOI - Noise | 1.3 Misalignment |
| Motor, Electric | Convert energy | Shaft Failure | STD - Structural deficiency | 2.6 Fatigue |
| Motor, Electric | Convert energy | Shaft Failure | BRD - Breakdown | 1.1 Crack |
| Motor, Electric | Convert energy | Coupling Failure | VIB - Vibration | 1.3 Misalignment |
| Motor, Electric | Convert energy | Coupling Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Coupling Failure | STD - Structural deficiency | 1.5 Looseness |
| Motor, Electric | Convert energy | Coupling Failure | FWR - Failure while running | 2.6 Fatigue |
| Motor, Electric | Convert energy | Cooling System Failure | OHE - Overheating | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | PDE - Parameter deviation | 5.1 Blockage |
| Motor, Electric | Convert energy | Cooling System Failure | LOO - Leak of oil | 2.7 Overheating |
| Motor, Electric | Convert energy | Cooling System Failure | FWR - Failure while running | 1.1 Leakage |
| Motor, Electric | Convert energy | Junction Box Failure | ELP - External leakage | 2.4 Wear |
| Motor, Electric | Convert energy | Junction Box Failure | CSF - Control/Signal failure | 1.1 Leakage |
| Motor, Electric | Convert energy | Junction Box Failure | FTS - Failure to start | 2.2 Corrosion |
| Motor, Electric | Convert energy | Junction Box Failure | STD - Structural deficiency | 4.2 Open circuit |
| Motor, Electric | Convert energy | Control System Failure | AIR - Abnormal instrument reading | 4.2 Open circuit |
| Motor, Electric | Convert energy | Control System Failure | CSF - Control/Signal failure | 2.2 Corrosion |
| Motor, Electric | Convert energy | Control System Failure | FTF - Failure to function | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Control System Failure | FTS - Failure to start | 3.1 Control failure |
| Motor, Electric | Convert energy | Enclosure Failure | STD - Structural deficiency | 3.1 Control failure |
| Motor, Electric | Convert energy | Enclosure Failure | ELP - External leakage | 2.2 Corrosion |
| Motor, Electric | Convert energy | Enclosure Failure | VIB - Vibration | 1.1 Leakage |
| Motor, Electric | Convert energy | Enclosure Failure | NOI - Noise | 1.4 Deformation |
| Motor, Electric | Convert energy | Heaters Failure | OHE - Overheating | 1.5 Looseness |
| Motor, Electric | Convert energy | Heaters Failure | FTS - Failure to start | 4.1 Short circuit |
| Motor, Electric | Convert energy | Heaters Failure | FTF - Failure to function | 4.2 Open circuit |
| Motor, Electric | Convert energy | Heaters Failure | CSF - Control/Signal failure | 4.2 Open circuit |
| Motor, Electric | Convert energy | Monitoring Failure | AIR - Abnormal instrument reading | 3.1 Control failure |
| Motor, Electric | Convert energy | Monitoring Failure | CSF - Control/Signal failure | 3.4 Out of adjustment |
| Motor, Electric | Convert energy | Monitoring Failure | FTF - Failure to function | 3.2 No signal |
| Motor, Electric | Convert energy | Monitoring Failure | FTS - Failure to start | 3.1 Control failure |
| Motor, Electric | Convert energy | Gearbox Failure | VIB - Vibration | 3.1 Control failure |
| Motor, Electric | Convert energy | Gearbox Failure | NOI - Noise | 2.4 Wear |
| Motor, Electric | Convert energy | Gearbox Failure | OHE - Overheating | 2.6 Fatigue |
| Motor, Electric | Convert energy | Gearbox Failure | LOO - Leak of oil | 1.3 Misalignment |
"""
    
    errors = validate_output_cardinality(output_sufficient_complex, "Motor, Electric")
    g0a_errors = [e for e in errors if 'G0a VIOLATION' in e]
    
    assert len(g0a_errors) == 0, "G0a should pass with 12 MIs for complex equipment"
    
    print("✓ Test passed: G0a passes with 12 MIs for complex equipment")


def test_g0a_fails_insufficient_simple_mis():
    """Test that G0a detects insufficient MIs for simple equipment (< 5)"""
    # Create FMEA output with only 3 MIs for Check Valve (simple, needs 5)
    output_insufficient_simple = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Check Valve | Prevent backflow | Body Failure | ELP - External leakage | 2.1 Cracking |
| Check Valve | Prevent backflow | Body Failure | ELP - External leakage | 2.2 Corrosion |
| Check Valve | Prevent backflow | Body Failure | STD - Structural deficiency | 2.6 Fatigue |
| Check Valve | Prevent backflow | Body Failure | PDE - Parameter deviation | 1.4 Deformation |
| Check Valve | Prevent backflow | Disc Failure | ILP - Internal leakage | 2.2 Corrosion |
| Check Valve | Prevent backflow | Disc Failure | FTC - Fail to close | 2.4 Wear |
| Check Valve | Prevent backflow | Disc Failure | NOI - Noise | 2.3 Erosion |
| Check Valve | Prevent backflow | Disc Failure | VIB - Vibration | 1.6 Sticking |
| Check Valve | Prevent backflow | Spring Failure | FTC - Fail to close | 1.5 Looseness |
| Check Valve | Prevent backflow | Spring Failure | PDE - Parameter deviation | 2.6 Fatigue |
| Check Valve | Prevent backflow | Spring Failure | STD - Structural deficiency | 2.2 Corrosion |
| Check Valve | Prevent backflow | Spring Failure | VIB - Vibration | 2.6 Fatigue |
"""
    
    errors = validate_output_cardinality(output_insufficient_simple, "Check Valve")
    g0a_errors = [e for e in errors if 'G0a VIOLATION' in e]
    
    assert len(g0a_errors) > 0, "G0a should detect insufficient MI count (3 < 5 for simple)"
    assert "minimum 5" in g0a_errors[0], "Error message should mention minimum 5 MIs"
    assert "Found only 3" in g0a_errors[0], "Error message should mention found 3 MIs"
    
    print("✓ Test passed: G0a detects insufficient MIs for simple equipment (3 < 5)")


def test_g0a_passes_sufficient_simple_mis():
    """Test that G0a passes when simple equipment has 5+ MIs"""
    # Create FMEA output with exactly 5 MIs for Check Valve (simple)
    output_sufficient_simple = """
| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism |
|------------|----------|-------------------|---------|-------------------|
| Check Valve | Prevent backflow | Body Failure | ELP - External leakage | 2.1 Cracking |
| Check Valve | Prevent backflow | Body Failure | STD - Structural deficiency | 2.2 Corrosion |
| Check Valve | Prevent backflow | Body Failure | PDE - Parameter deviation | 2.6 Fatigue |
| Check Valve | Prevent backflow | Body Failure | VIB - Vibration | 1.4 Deformation |
| Check Valve | Prevent backflow | Disc Failure | ILP - Internal leakage | 1.5 Looseness |
| Check Valve | Prevent backflow | Disc Failure | FTC - Fail to close | 2.4 Wear |
| Check Valve | Prevent backflow | Disc Failure | NOI - Noise | 2.3 Erosion |
| Check Valve | Prevent backflow | Disc Failure | VIB - Vibration | 1.6 Sticking |
| Check Valve | Prevent backflow | Spring Failure | FTC - Fail to close | 2.1 Cracking |
| Check Valve | Prevent backflow | Spring Failure | PDE - Parameter deviation | 2.6 Fatigue |
| Check Valve | Prevent backflow | Spring Failure | STD - Structural deficiency | 2.2 Corrosion |
| Check Valve | Prevent backflow | Spring Failure | VIB - Vibration | 2.6 Fatigue |
| Check Valve | Prevent backflow | Hinge Pin Failure | FTC - Fail to close | 1.5 Looseness |
| Check Valve | Prevent backflow | Hinge Pin Failure | STD - Structural deficiency | 2.4 Wear |
| Check Valve | Prevent backflow | Hinge Pin Failure | VIB - Vibration | 2.6 Fatigue |
| Check Valve | Prevent backflow | Hinge Pin Failure | NOI - Noise | 1.4 Deformation |
| Check Valve | Prevent backflow | Seat Failure | ILP - Internal leakage | 1.5 Looseness |
| Check Valve | Prevent backflow | Seat Failure | PDE - Parameter deviation | 2.4 Wear |
| Check Valve | Prevent backflow | Seat Failure | FTC - Fail to close | 2.3 Erosion |
| Check Valve | Prevent backflow | Seat Failure | STD - Structural deficiency | 2.2 Corrosion |
"""
    
    errors = validate_output_cardinality(output_sufficient_simple, "Check Valve")
    g0a_errors = [e for e in errors if 'G0a VIOLATION' in e]
    
    assert len(g0a_errors) == 0, "G0a should pass with 5 MIs for simple equipment"
    
    print("✓ Test passed: G0a passes with 5 MIs for simple equipment")


if __name__ == "__main__":
    print("Running G0a (Minimum MI Count) validation tests...\n")
    
    try:
        test_complex_equipment_classification()
        test_simple_equipment_classification()
        print()
        
        test_g0a_fails_insufficient_complex_mis()
        test_g0a_passes_sufficient_complex_mis()
        print()
        
        test_g0a_fails_insufficient_simple_mis()
        test_g0a_passes_sufficient_simple_mis()
        
        print("\n✅ All G0a validation tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

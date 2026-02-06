"""
Test G8 validation: Prevent Symptom codes from appearing in Maintainable Item column.

This test ensures that the validation correctly identifies when symptom codes
are incorrectly used as Maintainable Items.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from run_agent import validate_output_cardinality
import pandas as pd


def verify_symptom_catalog_loads():
    """Verify that the Symptom Catalog can be loaded correctly"""
    symptom_catalog_path = Path("inputs/Catalogs/Symptom Catalog.csv")
    assert symptom_catalog_path.exists(), "Symptom Catalog file must exist"
    
    # Test loading with correct separator
    symptom_df = pd.read_csv(symptom_catalog_path, sep=';', encoding='utf-8', encoding_errors='ignore')
    assert 'Code' in symptom_df.columns, "Symptom Catalog must have 'Code' column"
    
    # Extract codes
    symptom_codes = set()
    for code in symptom_df['Code'].dropna():
        code_str = str(code).strip().replace('\ufeff', '')
        if code_str and code_str not in ['Code', '']:
            symptom_codes.add(code_str.upper())
    
    assert len(symptom_codes) > 0, "Symptom Catalog must contain symptom codes"
    assert 'PTF' in symptom_codes, "PTF must be in Symptom Catalog"
    assert 'VIB' in symptom_codes, "VIB must be in Symptom Catalog"
    assert 'NOI' in symptom_codes, "NOI must be in Symptom Catalog"
    
    print(f"✓ Symptom Catalog loaded successfully with {len(symptom_codes)} codes")
    return symptom_codes


def test_g8_detects_exact_symptom_code():
    """Test that G8 detects exact symptom codes in MI column"""
    # Create a mock output with PTF (a real symptom code) in MI column
    output_with_symptom_code = """
# FMEA Output

| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
|------------|----------|-------------------|---------|-------------------|----------------|-------------------|----------------------|----------------------|
| Motor, Electric | Convert energy | PTF - Power / signal transmission failure | NOI - Noise | 2.6 Fatigue | System stops | Inspect regularly | PM00048A | Preventive |
| Motor, Electric | Convert energy | PTF - Power / signal transmission failure | VIB - Vibration | 1.2 Wear | Performance degraded | Replace bearing | PM00048A | Corrective |
| Motor, Electric | Convert energy | PTF - Power / signal transmission failure | OHE - Overheating | 4.2 Open circuit | Equipment damage | Monitor temperature | PM00048A | Condition-based |
| Motor, Electric | Convert energy | PTF - Power / signal transmission failure | NOO - No output | 4.3 No power/voltage | System fails | Check power supply | PM00048A | Failure-Finding |
"""
    
    errors = validate_output_cardinality(output_with_symptom_code, "Motor, Electric")
    g8_errors = [e for e in errors if 'G8 VIOLATION' in e]
    
    assert len(g8_errors) > 0, "G8 should detect exact symptom code PTF in MI column"
    print("✓ Test passed: G8 detects exact symptom code (PTF)")


def test_g8_detects_symptom_like_pattern():
    """Test that G8 detects symptom-like patterns even if not exact match"""
    # Create a mock output with PTO (typo/incorrect symptom code) in MI column
    output_with_symptom_pattern = """
# FMEA Output

| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
|------------|----------|-------------------|---------|-------------------|----------------|-------------------|----------------------|----------------------|
| Motor, Electric | Convert energy | PTO - Power / signal transmission failure | NOI - Noise | 2.6 Fatigue | System stops | Inspect regularly | PM00048A | Preventive |
| Motor, Electric | Convert energy | PTO - Power / signal transmission failure | VIB - Vibration | 1.2 Wear | Performance degraded | Replace bearing | PM00048A | Corrective |
| Motor, Electric | Convert energy | PTO - Power / signal transmission failure | OHE - Overheating | 4.2 Open circuit | Equipment damage | Monitor temperature | PM00048A | Condition-based |
| Motor, Electric | Convert energy | PTO - Power / signal transmission failure | NOO - No output | 4.3 No power/voltage | System fails | Check power supply | PM00048A | Failure-Finding |
"""
    
    errors = validate_output_cardinality(output_with_symptom_pattern, "Motor, Electric")
    g8_errors = [e for e in errors if 'G8 VIOLATION' in e]
    
    assert len(g8_errors) > 0, "G8 should detect symptom-like pattern (PTO - ...) in MI column"
    print("✓ Test passed: G8 detects symptom-like pattern (PTO - ...)")


def test_g8_allows_valid_maintainable_items():
    """Test that G8 does not flag valid Maintainable Items"""
    # Create a mock output with proper MI names
    output_with_valid_mi = """
# FMEA Output

| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
|------------|----------|-------------------|---------|-------------------|----------------|-------------------|----------------------|----------------------|
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise | 2.6 Fatigue | System stops | Inspect regularly | PM00048A | Preventive |
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration | 1.2 Wear | Performance degraded | Replace bearing | PM00048A | Corrective |
| Motor, Electric | Convert energy | Bearing Failure | OHE - Overheating | 4.2 Open circuit | Equipment damage | Monitor temperature | PM00048A | Condition-based |
| Motor, Electric | Convert energy | Bearing Failure | NOO - No output | 4.3 No power/voltage | System fails | Check power supply | PM00048A | Failure-Finding |
| Motor, Electric | Convert energy | Rotor Failure | VIB - Vibration | 2.6 Fatigue | System stops | Inspect regularly | PM00048A | Preventive |
| Motor, Electric | Convert energy | Rotor Failure | NOI - Noise | 1.1 Crack | Performance degraded | Replace rotor | PM00048A | Corrective |
| Motor, Electric | Convert energy | Rotor Failure | BRD - Breakdown | 2.6 Fatigue | Equipment damage | Monitor vibration | PM00048A | Condition-based |
| Motor, Electric | Convert energy | Rotor Failure | FWR - Failure while running | 1.2 Wear | System fails | Check alignment | PM00048A | Failure-Finding |
"""
    
    errors = validate_output_cardinality(output_with_valid_mi, "Motor, Electric")
    g8_errors = [e for e in errors if 'G8 VIOLATION' in e]
    
    assert len(g8_errors) == 0, "G8 should not flag valid Maintainable Item names"
    print("✓ Test passed: G8 allows valid Maintainable Items (Bearing Failure, Rotor Failure)")


def test_g8_detects_other_symptom_codes():
    """Test that G8 detects various symptom codes"""
    # Test with different real symptom codes
    output_with_various_symptoms = """
# FMEA Output

| Item Class | Function | Maintainable Item | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type |
|------------|----------|-------------------|---------|-------------------|----------------|-------------------|----------------------|----------------------|
| Motor, Electric | Convert energy | VIB - Vibration | NOI - Noise | 2.6 Fatigue | System stops | Inspect regularly | PM00048A | Preventive |
| Motor, Electric | Convert energy | VIB - Vibration | OHE - Overheating | 1.2 Wear | Performance degraded | Replace bearing | PM00048A | Corrective |
| Motor, Electric | Convert energy | NOI - Noise | VIB - Vibration | 2.6 Fatigue | Equipment damage | Monitor temperature | PM00048A | Condition-based |
| Motor, Electric | Convert energy | NOI - Noise | OHE - Overheating | 4.2 Open circuit | System fails | Check power supply | PM00048A | Failure-Finding |
"""
    
    errors = validate_output_cardinality(output_with_various_symptoms, "Motor, Electric")
    g8_errors = [e for e in errors if 'G8 VIOLATION' in e]
    
    assert len(g8_errors) >= 2, "G8 should detect VIB and NOI symptom codes in MI column"
    print("✓ Test passed: G8 detects multiple symptom codes (VIB, NOI)")


if __name__ == "__main__":
    print("Running G8 validation tests...\n")
    
    try:
        # First verify Symptom Catalog loads correctly
        symptom_codes = verify_symptom_catalog_loads()
        print()
        
        test_g8_detects_exact_symptom_code()
        test_g8_detects_symptom_like_pattern()
        test_g8_allows_valid_maintainable_items()
        test_g8_detects_other_symptom_codes()
        
        print("\n✅ All G8 validation tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

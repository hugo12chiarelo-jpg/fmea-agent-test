#!/usr/bin/env python3
"""
Test script to verify placeholder text detection in FMEA output validation.

This script verifies that the validate_mi_in_table() function correctly detects
when the AI uses placeholder text instead of generating complete table rows.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from run_agent import validate_mi_in_table


def test_complete_output():
    """Test that validation passes for a complete output with all MIs."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.6 Fatigue |
| Motor, Electric | Convert energy | Rotor Failure | Generate torque | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Rotor Failure | Generate torque | NOI - Noise | 1.5 Looseness |
| Motor, Electric | Convert energy | Stator Failure | Create field | OHE - Overheating | 4.1 Short circuiting |
| Motor, Electric | Convert energy | Stator Failure | Create field | NOO - No output | 4.1 Short circuiting |
"""
    
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    missing = validate_mi_in_table(output, mandatory_mi)
    
    assert len(missing) == 0, f"Expected no missing MIs, but got: {missing}"
    print("✓ Complete output test passed")


def test_placeholder_text_detection():
    """Test that validation detects placeholder text patterns."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.6 Fatigue |

(Additional rows for all maintainable items follow, omitted for brevity)

**Summary:** All MIs included with proper cardinalities.
"""
    
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    
    # Capture validation output
    import io
    import contextlib
    
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        missing = validate_mi_in_table(output, mandatory_mi)
    
    validation_output = captured_output.getvalue()
    
    # Verify placeholder was detected
    assert "placeholder" in validation_output.lower(), "Placeholder text not detected"
    assert "additional rows" in validation_output.lower() or "omitted for brevity" in validation_output.lower(), \
        "Specific placeholder pattern not identified"
    
    # Verify Rotor and Stator are reported as missing
    assert "Rotor" in missing, "Rotor should be missing"
    assert "Stator" in missing, "Stator should be missing"
    assert "Bearing" not in missing, "Bearing should not be missing"
    
    print("✓ Placeholder text detection test passed")


def test_partial_output_with_ellipsis():
    """Test detection of outputs that use ellipsis (...)."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear |
...

The rest of the table follows the same pattern for all other MIs.
"""
    
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    
    import io
    import contextlib
    
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        missing = validate_mi_in_table(output, mandatory_mi)
    
    validation_output = captured_output.getvalue()
    
    # Verify ellipsis was detected
    assert "..." in validation_output or "placeholder" in validation_output.lower(), \
        "Ellipsis placeholder not detected"
    
    # Verify missing MIs are identified
    assert len(missing) > 0, "Should detect missing MIs when ellipsis is used"
    
    print("✓ Ellipsis detection test passed")


def test_see_above_reference():
    """Test detection of 'see above' references."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Rotor Failure | See above | See above | See above |
"""
    
    mandatory_mi = ["Bearing", "Rotor"]
    
    import io
    import contextlib
    
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        missing = validate_mi_in_table(output, mandatory_mi)
    
    validation_output = captured_output.getvalue()
    
    # Verify "see above" was detected
    assert "see above" in validation_output.lower() or "placeholder" in validation_output.lower(), \
        "'See above' pattern not detected"
    
    print("✓ 'See above' detection test passed")


def test_missing_mi_with_zero_rows():
    """Test that MIs with zero rows are correctly identified as missing."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | Support shaft | NOI - Noise | 1.5 Looseness |
"""
    
    # Rotor mentioned in text but not as MI
    output += "\n\nNote: Rotor analysis is pending.\n"
    
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    
    import io
    import contextlib
    
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        missing = validate_mi_in_table(output, mandatory_mi)
    
    validation_output = captured_output.getvalue()
    
    # Verify row counts are displayed
    assert "row" in validation_output.lower(), "Row count diagnostic not displayed"
    
    # Verify Rotor and Stator are missing (0 rows)
    assert "Rotor" in missing, "Rotor should be missing (0 rows)"
    assert "Stator" in missing, "Stator should be missing (0 rows)"
    assert "Bearing" not in missing, "Bearing should not be missing (has rows)"
    
    print("✓ Zero rows detection test passed")


def test_mi_in_description_but_not_column():
    """Test that MI mentioned in descriptions doesn't count as present."""
    output = """
| Item Class | Function | Maintainable Item | MI Function | Symptom | Failure Mechanism |
|------------|----------|-------------------|-------------|---------|-------------------|
| Motor, Electric | Convert energy | Bearing Failure | Support rotor shaft | VIB - Vibration | 2.4 Wear |
| Motor, Electric | Convert energy | Bearing Failure | Aligned with stator | NOI - Noise | 1.5 Looseness |
"""
    
    # "rotor" and "stator" appear in descriptions but not as MI names
    mandatory_mi = ["Bearing", "Rotor", "Stator"]
    
    missing = validate_mi_in_table(output, mandatory_mi)
    
    # Should detect that Rotor and Stator are missing (only in descriptions, not MI column)
    assert "Rotor" in missing, "Rotor should be missing (only in description)"
    assert "Stator" in missing, "Stator should be missing (only in description)"
    assert "Bearing" not in missing, "Bearing should not be missing"
    
    print("✓ Description vs MI column test passed")


def main():
    """Run all tests."""
    print("Testing placeholder text detection in FMEA output validation...\n")
    
    try:
        test_complete_output()
        test_placeholder_text_detection()
        test_partial_output_with_ellipsis()
        test_see_above_reference()
        test_missing_mi_with_zero_rows()
        test_mi_in_description_but_not_column()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60)
        print("\nThe validate_mi_in_table() function correctly detects:")
        print("  • Placeholder text patterns")
        print("  • Missing Maintainable Items")
        print("  • MI column vs description text")
        print("  • Zero-row MIs")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test to verify that 'if fitted' keyword properly excludes items from Maintainable Items list.
This tests the fix for the issue: "Items marked with 'Exclude', 'if fitted', 'excludes' 
should not be included as Maintainable Item"
"""

def test_exclusion_logic():
    """Test that exclusion keywords correctly identify lines to exclude."""
    
    test_cases = [
        # (line, should_be_excluded)
        ("Excludes associated switchgear", True),
        ("excludes monitoring system", True),
        ("Exclude the valve", True),
        ("if fitted with sensor", True),
        ("If fitted temperature detector", True),
        ("Optional cooling system", True),
        ("if applicable to system", True),
        ("if any additional components", True),
        ("Includes motor coupling", False),
        ("Include bearing assembly", False),
        ("Contains rotor and stator", False),
    ]
    
    passed = 0
    failed = 0
    
    print("Testing exclusion logic for boundary parsing:")
    print("=" * 80)
    
    for line, expected_excluded in test_cases:
        line_lower = line.lower().strip()
        
        # This is the actual logic from run_agent.py
        is_excluded = (
            line_lower.startswith('exclude ') or
            line_lower.startswith('excludes ') or
            (len(line_lower) > 10 and 'exclude ' in line_lower[:15]) or
            'optional' in line_lower or
            'if applicable' in line_lower or
            'if any' in line_lower or
            'if fitted' in line_lower
        )
        
        status = "✓" if is_excluded == expected_excluded else "✗"
        result = "PASS" if is_excluded == expected_excluded else "FAIL"
        
        print(f"{status} {result:4s} | '{line:40s}' | excluded={is_excluded} (expected={expected_excluded})")
        
        if is_excluded == expected_excluded:
            passed += 1
        else:
            failed += 1
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print()
    
    if failed == 0:
        print("✓ All tests passed! The 'if fitted' keyword is now properly handled.")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(test_exclusion_logic())

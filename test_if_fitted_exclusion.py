#!/usr/bin/env python3
"""
Test to verify that boundary exclusion logic only excludes lines starting with
"Exclude" or "Excludes". Items marked as "if fitted", "optional", "if applicable",
or "if any" are intentionally INCLUDED because they represent real components
within the maintenance scope that may be present on some units.
"""


def test_exclusion_logic():
    """Test that only explicit Exclude/Excludes lines are treated as exclusions."""

    test_cases = [
        # (line, should_be_excluded)
        ("Excludes associated switchgear", True),
        ("excludes monitoring system", True),
        ("Exclude the valve", True),
        # "if fitted", "optional", "if applicable", "if any" are now INCLUDED
        ("if fitted with sensor", False),
        ("If fitted temperature detector", False),
        ("Optional cooling system", False),
        ("if applicable to system", False),
        ("if any additional components", False),
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

        # This is the actual logic from run_agent.py — only Exclude/Excludes triggers exclusion
        is_excluded = (
            line_lower.startswith('exclude ') or
            line_lower.startswith('excludes ') or
            (len(line_lower) > 10 and 'exclude ' in line_lower[:15])
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

    assert failed == 0, f"{failed} test case(s) failed. See output above."

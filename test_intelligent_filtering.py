#!/usr/bin/env python3
"""
Test script to verify intelligent MI filtering and ISO 14224 suggestions.

This script validates that:
1. The spec file contains guidance on intelligent filtering
2. The spec file mentions ISO 14224 Table B.15 suggestions
3. The spec includes examples of filtering (e.g., Electric Motor example)
4. The run_agent.py prompts emphasize ISO 14224 suggestions
"""

import sys
from pathlib import Path


def test_spec_contains_intelligent_filtering():
    """Test that spec file has intelligent filtering guidance."""
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    if not spec_path.exists():
        print("✗ FAIL: spec file not found")
        return False
    
    spec_content = spec_path.read_text()
    
    # Check for key phrases
    checks = [
        ("APPLY ENGINEERING INTELLIGENCE", "Engineering intelligence filtering"),
        ("INDEPENDENTLY MAINTAINABLE", "Independent maintainability criteria"),
        ("Example 1 - Electric Motor", "Electric motor example"),
        ("Rotor Failure, Stator Failure, Brushes Failure", "Motor component examples"),
        ("Axle (covered by", "Exclusion examples"),
        ("ISO 14224", "ISO 14224 reference"),
        ("Lubrication System", "Lubrication system example"),
    ]
    
    all_passed = True
    for phrase, description in checks:
        if phrase in spec_content:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_spec_contains_iso14224_suggestions():
    """Test that spec file encourages ISO 14224 suggestions."""
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    spec_content = spec_path.read_text()
    
    checks = [
        ("PROACTIVELY SUGGEST ISO 14224-COMPLIANT", "Proactive ISO 14224 suggestions"),
        ("ISO 14224 Table B.15", "ISO 14224 Table B.15 reference"),
        ("Cooling System Failure", "Cooling system example"),
        ("Seal System Failure", "Seal system example"),
        ("Bearing System Failure", "Bearing system example"),
    ]
    
    all_passed = True
    for phrase, description in checks:
        if phrase in spec_content:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_spec_contains_justification_section():
    """Test that spec file has updated justification section."""
    spec_path = Path("templates/templates/spec_fmea_ems_rev01.md")
    spec_content = spec_path.read_text()
    
    checks = [
        ("SUGGESTED ADDITIONAL MAINTAINABLE ITEMS", "Justification section header"),
        ("Justification (ISO 14224 or Engineering Basis)", "Justification column"),
        ("Expected Symptoms", "Expected symptoms column"),
    ]
    
    all_passed = True
    for phrase, description in checks:
        if phrase in spec_content:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_run_agent_prompts():
    """Test that run_agent.py has updated prompts."""
    script_path = Path("scripts/run_agent.py")
    if not script_path.exists():
        print("✗ FAIL: run_agent.py not found")
        return False
    
    script_content = script_path.read_text()
    
    checks = [
        ("APPLY ENGINEERING INTELLIGENCE", "Engineering intelligence in prompts"),
        ("CONSULT ISO 14224 Table B.15", "ISO 14224 consultation instruction"),
        ("Lubrication System, Cooling System", "System examples in prompts"),
        ("Electric Motor", "Electric motor example in prompts"),
        ("engineering judgment to filter", "Filtering guidance"),
        ("OUTPUT VALIDATION SECTION", "Validation section instruction"),
    ]
    
    all_passed = True
    for phrase, description in checks:
        if phrase in script_content:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_validation_is_lenient():
    """Test that validation allows intelligent filtering."""
    script_path = Path("scripts/run_agent.py")
    script_content = script_path.read_text()
    
    checks = [
        ("[INFO]", "Informational logging for missing items"),
        ("engineering judgment", "Reference to engineering judgment"),
        ("This is acceptable", "Acceptance of filtering"),
    ]
    
    all_passed = True
    for phrase, description in checks:
        if phrase in script_content:
            print(f"  ✓ Found: {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def main():
    print("=" * 80)
    print("Intelligent MI Filtering and ISO 14224 Suggestions Test")
    print("=" * 80)
    print()
    
    tests = [
        ("Spec contains intelligent filtering guidance", test_spec_contains_intelligent_filtering),
        ("Spec contains ISO 14224 suggestions", test_spec_contains_iso14224_suggestions),
        ("Spec contains justification section", test_spec_contains_justification_section),
        ("Run agent has updated prompts", test_run_agent_prompts),
        ("Validation allows intelligent filtering", test_validation_is_lenient),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 80)
        passed = test_func()
        results.append((test_name, passed))
        if passed:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    
    print()
    print("=" * 80)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 80)
    
    if passed_count == total_count:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

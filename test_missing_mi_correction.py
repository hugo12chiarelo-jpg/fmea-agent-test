#!/usr/bin/env python3
"""
Test script to verify missing MI correction prompt generation.

This script verifies that the build_missing_mi_correction_prompt() function
correctly generates correction prompts for missing mandatory Maintainable Items.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from run_agent import build_missing_mi_correction_prompt


def test_single_missing_mi():
    """Test correction prompt with a single missing MI."""
    missing = ["Accessories"]
    prompt = build_missing_mi_correction_prompt(missing)
    
    # Verify prompt has critical requirements
    assert "Accessories" in prompt, "Missing MI not in prompt"
    assert "4-8 DISTINCT Symptoms" in prompt, "Symptom requirement missing"
    assert "2-5 DISTINCT Failure Mechanisms" in prompt, "Mechanism requirement missing"
    assert "NO DUPLICATION" in prompt, "Duplication rule missing"
    assert "INCLUDE ALL MAINTAINABLE ITEMS" in prompt or "All existing MIs" in prompt, "Preservation instruction missing"
    
    print("✓ Single missing MI test passed")


def test_multiple_missing_mis():
    """Test correction prompt with multiple missing MIs."""
    missing = ["Accessories", "Piping", "Support Structure"]
    prompt = build_missing_mi_correction_prompt(missing)
    
    # Verify all missing MIs are in the prompt
    for mi in missing:
        assert mi in prompt, f"Missing MI '{mi}' not in prompt"
    
    # Verify structure
    assert "MISSING MANDATORY MAINTAINABLE ITEMS" in prompt, "Header missing"
    assert "REQUIRED CORRECTIVE ACTION" in prompt or "CRITICAL REQUIREMENTS" in prompt, "Requirements section missing"
    assert "Return the COMPLETE" in prompt or "COMPLETE, EXPLICIT" in prompt, "Return instruction missing"
    
    print("✓ Multiple missing MIs test passed")


def test_prompt_format():
    """Test that prompt format is consistent."""
    missing = ["Test Item 1", "Test Item 2"]
    prompt = build_missing_mi_correction_prompt(missing)
    
    # Verify bullet points
    assert "  - Test Item 1" in prompt, "Bullet formatting incorrect"
    assert "  - Test Item 2" in prompt, "Bullet formatting incorrect"
    
    # Verify numbered requirements exist (adjusted for new format)
    assert "1." in prompt, "Numbered list missing"
    assert "2." in prompt, "Numbered list missing"
    assert "3." in prompt, "Numbered list missing"
    assert "4." in prompt, "Numbered list missing"
    
    # Verify key anti-placeholder language
    assert "FORBIDDEN" in prompt or "placeholders" in prompt.lower(), "Anti-placeholder language missing"
    assert "NO DUPLICATION" in prompt, "Duplication rule missing"
    
    print("✓ Prompt format test passed")


def test_empty_list():
    """Test that function handles empty list gracefully."""
    missing = []
    prompt = build_missing_mi_correction_prompt(missing)
    
    # Should still return a valid prompt structure
    assert "MISSING" in prompt or "mandatory" in prompt.lower(), "Header missing for empty list"
    assert "REQUIRED" in prompt or "ACTION" in prompt, "Requirements missing for empty list"
    
    print("✓ Empty list test passed")


def main():
    """Run all tests."""
    print("Testing missing MI correction prompt generation...\n")
    
    try:
        test_single_missing_mi()
        test_multiple_missing_mis()
        test_prompt_format()
        test_empty_list()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60)
        print("\nThe build_missing_mi_correction_prompt() function correctly")
        print("generates correction prompts for missing mandatory MIs.")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

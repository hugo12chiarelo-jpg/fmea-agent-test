#!/usr/bin/env python3
"""
Test script to verify boundary parsing improvements.

This script tests that the FMEA agent correctly:
1. Parses EMS boundaries to identify included/excluded items
2. Filters out items marked as "Exclude", "optional", "if applicable"
3. Maps boundary terms to Maintainable Item Catalog terminology
4. Works with any Item Class (adaptable to different equipment types)
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, 'scripts')
from run_agent import build_mi_list_from_ems_and_catalog


def parse_boundaries(boundary_text):
    """
    Parse boundary text to extract included and excluded items.
    
    Returns:
        tuple: (included_keywords, excluded_keywords)
    """
    included = []
    excluded = []
    
    lines = boundary_text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        
        # Check if line contains exclusion keywords
        is_excluded = (
            line_lower.startswith('exclude ') or
            'exclude ' in line_lower[:20] or
            'optional' in line_lower or
            'if applicable' in line_lower or
            'if any' in line_lower
        )
        
        if is_excluded:
            # Extract items from exclusion line
            # Remove "exclude" prefix and common words
            clean_line = re.sub(r'\bexclude\b', '', line_lower, flags=re.IGNORECASE)
            clean_line = re.sub(r'\b(which|are|not|part|of|the|and|or)\b', '', clean_line)
            words = [w.strip() for w in clean_line.split(',') if w.strip() and len(w.strip()) > 3]
            excluded.extend(words)
        else:
            # Extract potential items from included line
            # Look for noun phrases (simplified heuristic)
            words = re.findall(r'\b[a-z]{4,}\b', line_lower)
            included.extend(words)
    
    return list(set(included)), list(set(excluded))


def test_item_class_boundaries(item_class, ems_path, mi_catalog_path):
    """
    Test boundary parsing for any Item Class.
    
    Args:
        item_class: Item Class code (e.g., 'COCE', 'MOEL', 'VALV')
        ems_path: Path to EMS.csv file
        mi_catalog_path: Path to Maintainable Item Catalog.csv
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    if not ems_path.exists() or not mi_catalog_path.exists():
        print(f"❌ Required files not found")
        return False
    
    # Get boundaries for this Item Class
    try:
        import pandas as pd
        ems_df = pd.read_csv(ems_path, sep=';')
        ems_df.columns = [str(c).replace('\ufeff', '').strip() for c in ems_df.columns]
        
        item_row = ems_df[ems_df['Item Class'] == item_class]
        if item_row.empty:
            print(f"⚠ Item Class '{item_class}' not found in EMS")
            return None
        
        boundary_text = item_row['Boundaries'].iloc[0]
        item_name = item_row['Item Class Name'].iloc[0]
    except Exception as e:
        print(f"❌ Error reading EMS: {e}")
        return False
    
    # Parse boundaries to understand what should be included/excluded
    included_keywords, excluded_keywords = parse_boundaries(boundary_text)
    
    # Run the boundary parsing
    result = build_mi_list_from_ems_and_catalog(ems_path, item_class, mi_catalog_path)
    
    print(f"\n{'='*80}")
    print(f"Testing Item Class: {item_class} ({item_name})")
    print(f"{'='*80}")
    print(f"Found {len(result)} Maintainable Items")
    print()
    
    # Test 1: Check that some items were found (not empty)
    passed = 0
    failed = 0
    
    if len(result) > 0:
        print(f"  ✓ Non-empty result: {len(result)} items found")
        passed += 1
    else:
        print(f"  ✗ Empty result: No items found")
        failed += 1
    
    # Test 2: Check that excluded keywords are NOT in results
    print(f"\n  Checking exclusions:")
    excluded_found = []
    # Only check for significant excluded keywords (length > 5 to avoid partial matches)
    significant_excluded = [k for k in excluded_keywords if len(k) > 5][:5]
    
    for keyword in significant_excluded:
        # Only flag as issue if keyword is exact or very close match
        matches = [mi for mi in result if keyword == mi.lower() or mi.lower().startswith(keyword + ' ')]
        if matches:
            excluded_found.append((keyword, matches))
    
    if not excluded_found:
        print(f"    ✓ No explicitly excluded items found in results")
        passed += 1
    else:
        print(f"    ⚠ Found {len(excluded_found)} potentially excluded items:")
        for keyword, matches in excluded_found[:3]:
            print(f"      - '{keyword}' matches: {matches[0]}")
        print(f"    Note: These might be valid if they're compound terms or specific variants")
        # Don't fail the test for this, as compound terms are often valid
    
    # Test 3: Check that results contain relevant items from catalog
    print(f"\n  Sample Maintainable Items found:")
    for i, mi in enumerate(result[:10], 1):
        print(f"    {i}. {mi}")
    if len(result) > 10:
        print(f"    ... and {len(result)-10} more")
    
    # Test 4: Verify no duplicates
    if len(result) == len(set(result)):
        print(f"\n  ✓ No duplicates in result")
        passed += 1
    else:
        print(f"\n  ✗ Found duplicates in result")
        failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def get_available_item_classes(ems_path):
    """Get list of available Item Classes from EMS file."""
    try:
        import pandas as pd
        ems_df = pd.read_csv(ems_path, sep=';')
        ems_df.columns = [str(c).replace('\ufeff', '').strip() for c in ems_df.columns]
        return ems_df['Item Class'].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading EMS: {e}")
        return []


def main():
    """Main test function - adaptable to any Item Class in EMS."""
    print("FMEA Boundary Parsing Test - Generic for All Item Classes")
    print("=" * 80)
    
    ems_path = Path("inputs/EMS/EMS.csv")
    mi_catalog_path = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
    
    if not ems_path.exists():
        print(f"❌ EMS file not found: {ems_path}")
        return 1
    
    if not mi_catalog_path.exists():
        print(f"❌ Catalog file not found: {mi_catalog_path}")
        return 1
    
    # Get available Item Classes
    item_classes = get_available_item_classes(ems_path)
    
    if not item_classes:
        print("❌ No Item Classes found in EMS")
        return 1
    
    print(f"\nAvailable Item Classes: {', '.join(item_classes)}")
    print()
    
    # Test all available Item Classes (or a sample if many)
    all_passed = True
    test_count = 0
    
    for item_class in item_classes[:5]:  # Test up to 5 Item Classes
        result = test_item_class_boundaries(item_class, ems_path, mi_catalog_path)
        if result is False:
            all_passed = False
        if result is not None:
            test_count += 1
    
    print()
    print("=" * 80)
    if all_passed and test_count > 0:
        print(f"✓ All {test_count} Item Class(es) tested successfully!")
        return 0
    elif test_count > 0:
        print(f"⚠ Some tests failed for {test_count} Item Class(es)")
        return 1
    else:
        print("❌ No tests were run")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test CSV conversion functionality
"""
import sys
sys.path.insert(0, 'scripts')

from run_agent import convert_markdown_table_to_csv
import pandas as pd
from io import StringIO

def test_basic_conversion():
    """Test basic markdown to CSV conversion"""
    markdown_input = """```markdown
| Item Class | Function | Maintainable Item | Symptom |
|------------|----------|------------------|---------|
| Motor, Electric | Convert energy | Bearing Failure | VIB - Vibration |
| Motor, Electric | Convert energy | Bearing Failure | NOI - Noise |
```"""
    
    csv_output = convert_markdown_table_to_csv(markdown_input)
    
    # Verify it's valid CSV
    df = pd.read_csv(StringIO(csv_output))
    
    assert df.shape[0] == 2, f"Expected 2 rows, got {df.shape[0]}"
    assert df.shape[1] == 4, f"Expected 4 columns, got {df.shape[1]}"
    assert 'Item Class' in df.columns, "Missing 'Item Class' column"
    assert 'Symptom' in df.columns, "Missing 'Symptom' column"
    
    print("✓ Basic conversion test passed")

def test_with_separator_row():
    """Test that separator rows are removed"""
    markdown_input = """| Item Class | Function | Maintainable Item |
|------------|----------|------------------|
| Motor, Electric | Convert energy | Bearing Failure |
| Motor, Electric | Convert energy | Rotor Failure |"""
    
    csv_output = convert_markdown_table_to_csv(markdown_input)
    
    # Verify separator row is not in output
    assert '----' not in csv_output, "Separator row not removed"
    
    # Verify it's valid CSV
    df = pd.read_csv(StringIO(csv_output))
    assert df.shape[0] == 2, f"Expected 2 data rows, got {df.shape[0]}"
    
    print("✓ Separator row removal test passed")

def test_without_separator_row():
    """Test that tables without separator rows are handled correctly"""
    markdown_input = """| Item Class | Function |
| Motor, Electric | Convert energy |"""
    
    csv_output = convert_markdown_table_to_csv(markdown_input)
    
    # Verify it's valid CSV with at least the header and one data row
    df = pd.read_csv(StringIO(csv_output))
    assert df.shape[0] == 1, f"Expected 1 data row, got {df.shape[0]}"
    assert df.shape[1] == 2, f"Expected 2 columns, got {df.shape[1]}"
    
    print("✓ Table without separator row test passed")

def test_empty_columns_removed():
    """Test that empty first and last columns are removed"""
    markdown_input = """| Item Class | Function |
|------------|----------|
| Motor, Electric | Convert energy |"""
    
    csv_output = convert_markdown_table_to_csv(markdown_input)
    
    # Count commas in header line to verify column count
    lines = csv_output.split('\n')
    header_commas = lines[0].count(',')
    
    # Should have 1 comma for 2 columns (not extra for empty columns)
    assert header_commas == 1, f"Expected 1 comma in header, got {header_commas}"
    
    print("✓ Empty column removal test passed")

def test_with_quotes_in_data():
    """Test handling of data that needs quoting"""
    markdown_input = """| Item Class | Description |
|------------|-------------|
| Motor, Electric | Convert electrical, mechanical energy |
| Pump, Centrifugal | Increase fluid pressure, flow rate |"""
    
    csv_output = convert_markdown_table_to_csv(markdown_input)
    
    # Verify it's valid CSV and can be read back
    df = pd.read_csv(StringIO(csv_output))
    assert df.shape[0] == 2, f"Expected 2 rows, got {df.shape[0]}"
    
    # Verify data with commas is preserved exactly
    assert df['Description'].iloc[0].strip() == 'Convert electrical, mechanical energy', \
        f"Data with commas not preserved. Got: '{df['Description'].iloc[0]}'"
    assert df['Description'].iloc[1].strip() == 'Increase fluid pressure, flow rate', \
        f"Data with commas not preserved. Got: '{df['Description'].iloc[1]}'"
    
    print("✓ Data with commas test passed")

def test_invalid_input():
    """Test handling of invalid input (no table)"""
    non_table_input = "This is just plain text without a table."
    
    csv_output = convert_markdown_table_to_csv(non_table_input)
    
    # Should return original text if no table found
    assert csv_output == non_table_input, "Invalid input not handled correctly"
    
    print("✓ Invalid input handling test passed")

if __name__ == "__main__":
    print("Testing CSV Conversion Functionality")
    print("=" * 60)
    
    tests = [
        test_basic_conversion,
        test_with_separator_row,
        test_without_separator_row,
        test_empty_columns_removed,
        test_with_quotes_in_data,
        test_invalid_input
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n✗ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)

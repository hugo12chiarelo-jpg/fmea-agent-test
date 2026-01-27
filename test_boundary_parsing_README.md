# FMEA Boundary Parsing Test

## Overview

This test validates that the FMEA agent correctly parses EMS boundaries for **any** Item Class. The test is generic and automatically adapts to the Item Class context.

## What It Tests

1. **Boundary Parsing**: Correctly identifies included vs excluded items from boundaries
2. **Exclusion Filtering**: Filters out items marked with "Exclude", "optional", "if applicable", "if any"
3. **Catalog Mapping**: Maps boundary terms to Maintainable Item Catalog terminology
4. **Generic Adaptability**: Works with any Item Class (COCE, MOEL, VALV, PUMP, etc.)

## Usage

### Basic Usage
```bash
python3 test_boundary_parsing.py
```

The test will:
- Automatically detect all Item Classes in `inputs/EMS/EMS.csv`
- Run boundary parsing for each Item Class found
- Display results showing included/excluded items
- Report pass/fail status

### Test Output

```
FMEA Boundary Parsing Test - Generic for All Item Classes
================================================================================

Available Item Classes: COCE, MOEL, VALV

================================================================================
Testing Item Class: COCE (Centrifugal Compressor)
================================================================================
Found 20 Maintainable Items

  ✓ Non-empty result: 20 items found
  
  Checking exclusions:
    ✓ No explicitly excluded items found in results
    
  Sample Maintainable Items found:
    1. Accessories
    2. Cooler
    3. Coupling
    4. Dry gas seal
    ...
    
  ✓ No duplicates in result
  
Results: 3 passed, 0 failed
```

## Adding New Item Classes

To test with additional Item Classes:

1. Add the Item Class data to `inputs/EMS/EMS.csv` with proper boundaries
2. Run the test - it will automatically pick up the new Item Class
3. The test validates:
   - Items are found (non-empty result)
   - No exact matches for excluded keywords
   - No duplicate items

## Test Logic

### Adaptive Validation

The test **automatically parses boundaries** for each Item Class to:
- Extract keywords that should be included
- Extract keywords that should be excluded
- Validate the parsing results against these expectations

### Smart Exclusion Checking

- Only checks significant excluded keywords (length > 5)
- Only flags exact matches or very close matches
- Allows compound terms that include excluded words (e.g., "Coupling to driver" is OK even if "driver" is excluded)

## Examples

### Centrifugal Compressor (COCE)
- **Included**: Coupling, Seal, Lubrication, Monitoring, PLC, Pumps, Cooler
- **Excluded**: Gearbox, Fire systems, standalone Driver

### Electric Motor (MOEL)
- Would include: Stator, Rotor, Bearings, Cooling, Terminal box
- Would exclude: External sensors, mounting structures (if marked as excluded)

### Valve (VALV)
- Would include: Body, Bonnet, Stem, Seat, Actuator
- Would exclude: Piping, external instrumentation (if marked as excluded)

## Notes

- The test is designed to work with the actual EMS data available
- If only one Item Class exists in EMS (e.g., COCE), it tests that one
- The test can handle multiple Item Classes and will test up to 5 by default
- Results adapt to the specific boundaries and exclusions defined for each Item Class

## Troubleshooting

**Q: Test shows "No Item Classes found"**
A: Check that `inputs/EMS/EMS.csv` exists and has data in the "Item Class" column

**Q: Test shows warnings about excluded items**
A: This is often expected for compound terms. Review if the match is a false positive.

**Q: How to test a specific Item Class only?**
A: Modify the `main()` function to filter for specific Item Class:
```python
# In test_boundary_parsing.py, modify:
for item_class in ['COCE']:  # Test only COCE
    result = test_item_class_boundaries(item_class, ems_path, mi_catalog_path)
```

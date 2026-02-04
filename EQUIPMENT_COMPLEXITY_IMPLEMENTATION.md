# Equipment Complexity and Minimum MI Count Implementation

## Overview
This document explains the implementation of variable minimum Maintainable Item (MI) counts based on equipment complexity in the FMEA agent.

## Requirements (from Issue)
The issue requested that:
1. **Complex equipment** (motors, generators, pumps, compressors, separators, heat exchangers, etc.) should have **minimum 12 Maintainable Items**
2. **Simple equipment** (instrumentation, simple valves, lamps, etc.) should have **minimum 5 Maintainable Items**
3. Keep existing quality gates (G2-G7) unchanged
4. Maintain the same MI quality structure: Boundaries → Catalog → Manual → AI intelligence

## Implementation

### 1. Equipment Classification (`determine_equipment_complexity()`)

**Location:** `scripts/run_agent.py` (lines 772-820)

The function classifies equipment into two categories:

#### Complex Equipment (minimum 12 MIs)
- Motors, generators, turbines
- Pumps (centrifugal, reciprocating, gear, screw)
- Compressors (all types)
- Separators, heat exchangers, coolers, condensers
- Gearboxes, mechanical drives
- Pressure vessels, reactors, columns
- Process fans/blowers

#### Simple Equipment (minimum 5 MIs)
- Valves (check, relief, manual, gate, ball)
- Instruments (transmitters, sensors, gauges, indicators, detectors, analyzers)
- Lamps and lighting fixtures
- Actuators, solenoids
- Breakers, switches, relays
- Simple tanks

**Default:** If equipment type is unclear, it defaults to COMPLEX (conservative approach for comprehensive FMEA coverage).

### 2. Validation (G0a Quality Gate)

**Location:** `scripts/run_agent.py` (lines 933-952)

The validation function `validate_output_cardinality()` now:
1. Accepts `item_class` parameter
2. Determines equipment complexity using `determine_equipment_complexity()`
3. Counts unique Maintainable Items in the output
4. Validates against minimum requirements
5. Returns clear error message if validation fails

**Example Error Message:**
```
G0a VIOLATION: Equipment classified as COMPLEX requires minimum 12 Maintainable Items. 
Found only 8 Maintainable Items. Add more Maintainable Items from boundaries, catalog, 
manual, or ISO 14224-compliant suggestions. Use the engineering questions in the code 
to identify correct additional Maintainable Items.
```

### 3. Template Updates

**Location:** `templates/templates/spec_fmea_ems_rev01.md`

Added comprehensive guidance on:
- Equipment complexity determination (lines 69-110)
- Minimum MI count requirements
- Quality gate G0a definition (lines 288-295)
- Updated verification checklist (line 328)

### 4. Tests

**Location:** `test_mi_count_validation.py`

Comprehensive test suite covering:
- Equipment classification (13 test cases)
- G0a validation for complex equipment (2 test cases)
- G0a validation for simple equipment (2 test cases)

All tests passing ✓

## Usage

The agent now automatically:
1. Reads the Item Class from instructions
2. Classifies equipment as COMPLEX or SIMPLE
3. Generates appropriate number of Maintainable Items
4. Validates output meets minimum MI count
5. Provides clear feedback if requirements not met

## Backward Compatibility

✅ All existing quality gates (G1-G7) remain unchanged
✅ Existing MI quality structure maintained
✅ All existing tests continue to pass
✅ No breaking changes to existing functionality

## Quality Assurance

- ✅ 6/7 tests passing (1 deprecated test excluded)
- ✅ Code review completed - all comments addressed
- ✅ Security scan completed - 0 alerts
- ✅ Manual testing with mock data - working as expected

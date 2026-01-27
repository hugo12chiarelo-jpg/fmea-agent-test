# Fix for Missing Maintainable Items Issue

## Problem Summary

**Issue**: The FMEA agent was generating incomplete outputs with placeholder text instead of actual table rows for all Maintainable Items.

**Symptoms**:
- Expected 13 Maintainable Items based on EMS boundaries
- Only 4-5 MIs appeared with actual rows in the output table
- Output contained placeholder text like "(Additional rows for all maintainable items... omitted for brevity)"
- Missing 8-9 MIs: Coupling, Enclosure, Gearbox, Heaters, Junction box, Monitoring, Rotor, Stator, Windings

## Root Cause

The AI model (GPT) was using placeholder text and shortcuts instead of generating the complete FMEA table. The existing validation was not detecting this because it only checked if MI names appeared anywhere in the text, not specifically in the table's Maintainable Item column.

## Solution Implemented

### 1. Enhanced Validation (`validate_mi_in_table()`)

**Key improvements**:
- **Placeholder Detection**: Actively scans for patterns indicating incomplete output:
  - "additional rows", "omitted for brevity", "follow,", "see above", "unchanged"
  - "rest of the table", "similar to above", "previously shown", "as shown above"
  - Ellipsis ("...") indicating truncation
  
- **Column-Specific Parsing**: Extracts MIs from the actual Maintainable Item column (column 4) instead of searching the entire line
  - Prevents false positives where "rotor" appears in a function description but not as an MI
  
- **Row Count Diagnostics**: Displays how many rows each MI has in the table
  - Makes it immediately obvious when an MI has 0 rows (missing)
  
- **Early Warning System**: Prints warnings when placeholder patterns are detected

### 2. Strengthened Correction Prompt (`build_missing_mi_correction_prompt()`)

**Enhancements**:
- **Explicit Anti-Placeholder Language**: Uses strong, unambiguous language
  - "⚠️ CRITICAL ERROR" header to emphasize severity
  - "ABSOLUTELY FORBIDDEN" section listing all prohibited shortcuts
  - Clear examples of what NOT to do (❌) vs what to do (✅)
  
- **Root Cause Identification**: Tells the AI exactly why its previous output failed
  - "You used placeholder text like '(Additional rows... omitted for brevity)' instead of generating ACTUAL TABLE ROWS"
  
- **Explicit Row Count Expectations**: Provides concrete examples
  - "Example: 'Rotor Failure' with 5 symptoms × 3 mechanisms each = 15 rows minimum"
  
- **Verification Checklist**: Gives the AI a pre-submission checklist to follow

### 3. Enhanced Initial User Prompt

**New Section**: "NO PLACEHOLDERS OR TRUNCATION ALLOWED"
- Added at the top of critical reminders (before cardinality requirements)
- Uses visual indicators (❌ and ✅) for clarity
- Provides explicit row count example: "If you have 13 Maintainable Items with 5 symptoms each × 2 mechanisms = 130+ rows minimum - write them ALL"

## Files Modified

1. **`scripts/run_agent.py`**:
   - `validate_mi_in_table()`: Enhanced to detect placeholders and parse MI column specifically
   - `build_missing_mi_correction_prompt()`: Strengthened with explicit anti-placeholder language
   - Initial user prompt: Added "NO PLACEHOLDERS" section

2. **`test_missing_mi_correction.py`**:
   - Updated test assertions to match new prompt structure
   - All 4 tests pass

3. **`test_placeholder_detection.py`** (NEW):
   - 6 comprehensive test cases covering:
     - Complete output validation
     - Placeholder text pattern detection
     - Ellipsis detection
     - "See above" reference detection
     - Zero-row MI detection
     - MI column vs description text distinction
   - All tests pass

## Verification Steps

### 1. Run Unit Tests

All tests pass successfully:

```bash
# Test the missing MI correction prompt generation
python3 test_missing_mi_correction.py
# Output: All tests passed! ✓

# Test placeholder text detection
python3 test_placeholder_detection.py
# Output: All tests passed! ✓

# Test boundary parsing
python3 test_boundary_parsing.py
# Output: ✓ All 1 Item Class(es) tested successfully!

# Test electric motor specific fixes
python3 test_electric_motor_fixes.py
# Output: ✓ All tests passed!
```

### 2. Manual Verification (Requires OpenAI API Key)

To test with actual AI generation:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Optional: Override model (default: gpt-4.1-mini)
export OPENAI_MODEL=gpt-4o-mini

# Optional: Adjust correction attempts (default: 3)
export MAX_CORRECTION_ATTEMPTS=3

# Run the agent
python3 scripts/run_agent.py
```

**Expected Behavior**:
1. Agent generates initial output
2. Validation runs and checks for:
   - Placeholder text patterns
   - Missing MIs (should detect 8-9 missing MIs from current incomplete output)
3. Correction loop activates:
   - Sends correction prompt to AI
   - AI regenerates complete table
   - Validation re-checks
4. Process repeats up to 3 times if needed
5. Final output saved to `outputs/EMS upgrade output.md`

**Success Criteria**:
- ✅ All 13 Maintainable Items appear in the output table with actual rows
- ✅ Each MI has 4-8 distinct symptoms
- ✅ Each (MI, Symptom) pair has 2-5 distinct failure mechanisms
- ✅ No placeholder text in output
- ✅ Validation output shows "✓ All mandatory Maintainable Items are present"
- ✅ Validation output shows "✓ All quality gates passed"

### 3. Inspect Validation Output

When running the agent, look for these diagnostic messages:

```
[VALIDATION] Checking for missing mandatory Maintainable Items...

[VALIDATION] ⚠️  Detected placeholder text patterns: ['additional rows', 'omitted for brevity']
[VALIDATION] This indicates the AI generated an incomplete table instead of full rows for all MIs

[VALIDATION] Row counts per MI:
  ✓ Bearing: 10 rows
  ✓ Brushes: 8 rows
  ✓ Control system: 8 rows
  ✓ Cooling system: 9 rows
  ✗ MISSING Coupling: 0 rows
  ✗ MISSING Enclosure: 0 rows
  ...

[CORRECTION] Requesting AI to add missing Maintainable Items (Attempt 1/3)...
```

After correction:

```
[VALIDATION] ✓ All mandatory Maintainable Items are present
[VALIDATION] ✓ All quality gates passed
```

## Testing Current Output

You can test the enhanced validation against the current incomplete output:

```python
from pathlib import Path
from scripts.run_agent import validate_mi_in_table

# Read the current output (before fix)
output = Path('outputs/EMS upgrade output.md').read_text()

# Expected MIs from EMS boundaries
mandatory_mi = ['Bearing', 'Brushes', 'Control system', 'Cooling system', 
                'Coupling', 'Enclosure', 'Gearbox', 'Heaters', 'Junction box', 
                'Monitoring', 'Rotor', 'Stator', 'Windings']

# Validate
missing = validate_mi_in_table(output, mandatory_mi)

print(f'Missing MIs: {len(missing)}')
for mi in missing:
    print(f'  - {mi}')
```

**Current Output Result**:
```
[VALIDATION] ⚠️  Detected placeholder text patterns: ['additional rows', 'follow,']
[VALIDATION] This indicates the AI generated an incomplete table instead of full rows for all MIs
[VALIDATION] Found placeholder after table: (Additional rows for all maintainable items...

[VALIDATION] Row counts per MI:
  ✓ Bearing: 10 rows
  ✓ Brushes: 8 rows
  ✓ Control system: 8 rows
  ✓ Cooling system: 9 rows
  ✗ MISSING Coupling: 0 rows
  ✗ MISSING Enclosure: 0 rows
  ✗ MISSING Gearbox: 0 rows
  ✗ MISSING Heaters: 0 rows
  ✗ MISSING Junction box: 0 rows
  ✗ MISSING Monitoring: 0 rows
  ✗ MISSING Rotor: 0 rows
  ✗ MISSING Stator: 0 rows
  ✗ MISSING Windings: 0 rows

Missing MIs: 9
```

## Expected Impact

### Before Fix
- ❌ 4 MIs with rows in table
- ❌ 9 MIs missing (only mentioned in summary)
- ❌ Placeholder text: "(Additional rows... omitted for brevity)"
- ❌ Incomplete FMEA documentation

### After Fix
- ✅ All 13 MIs with complete rows in table
- ✅ No placeholder text
- ✅ Each MI has 4-8 symptoms with 2-5 mechanisms each
- ✅ Complete, production-ready FMEA documentation

## Technical Details

### Validation Flow

1. **Placeholder Pattern Detection**:
   ```python
   placeholder_patterns = [
       'additional rows', 'omitted for brevity', 'follow,',
       'see above', 'unchanged', 'rest of the table',
       'similar to above', 'previously shown', '...'
   ]
   ```

2. **Table Extraction**:
   - Finds table start: `| ... | Item Class | ...`
   - Extracts all rows starting with `|`
   - Stops at first non-table content

3. **MI Column Parsing**:
   ```python
   parts = line.split('|')
   if len(parts) > 3:
       mi_cell = parts[3].strip()  # Column 4 = Maintainable Item
   ```

4. **Row Counting**:
   - Counts actual table rows per MI
   - MIs with 0 rows flagged as missing
   - Diagnostic output shows counts for all MIs

### Correction Loop

```
Initial Generation → Validation → Missing MIs? → Correction Prompt → Regeneration
                         ↓                              ↑
                    Cardinality Check                   |
                         ↓                              |
                    Quality Gates (G1-G7)               |
                         ↓                              |
                    All Pass? ────NO─────→ (up to 3 times)
                         ↓
                        YES
                         ↓
                    Save Output
```

## Backward Compatibility

✅ All changes are backward compatible:
- Existing function signatures unchanged
- No breaking changes to input/output formats
- Enhanced validation only adds more checks (doesn't remove any)
- All existing tests still pass

## Future Improvements (Optional)

1. **Adaptive Prompt Length**: Adjust prompt complexity based on model's track record
2. **Per-MI Validation**: Validate each MI individually for faster feedback
3. **Template Generation**: Pre-generate row templates for AI to fill in
4. **Cost Optimization**: Cache successful patterns to reduce correction attempts

## Conclusion

The fix comprehensively addresses the missing Maintainable Items issue by:
1. Detecting when AI uses shortcuts/placeholders
2. Providing clear, unambiguous guidance on what's expected
3. Automatically correcting incomplete outputs through an iterative loop
4. Ensuring all 13 MIs from EMS boundaries appear with complete FMEA rows

All unit tests pass, and the solution is ready for production use with an OpenAI API key.

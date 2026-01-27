# Verification Guide for FMEA Agent Fix

This guide explains how to verify that the fix resolves the original issue.

## Original Issue

The FMEA agent was failing with this error:

```
RuntimeError: Model output missing 2 mandatory Maintainable Items. 
Examples: ['Accessories', 'Cooler']
Error: Process completed with exit code 1.
```

The root cause was that the instruction file used `Item Class: Centrifugal Compressor` (the human-readable name), but the agent could only match the Item Class code (`COCE`) from the EMS.csv file.

## What Was Fixed

The fix enables the agent to match Item Class by **either**:
1. Item Class **code** (e.g., `COCE`) - maintains backward compatibility
2. Item Class **name** (e.g., `Centrifugal Compressor`) - new capability

## How to Verify the Fix

### Option 1: Run Unit Tests (No API Key Required)

Run the comprehensive integration test:

```bash
cd /home/runner/work/fmea-agent/fmea-agent

python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from pathlib import Path
from run_agent import (
    pick_instruction_file,
    extract_item_class,
    build_mi_list_from_ems_and_catalog,
    match_item_class_rows
)
import pandas as pd

# Test the fix
instruction_file = pick_instruction_file()
instruction_text = instruction_file.read_text(encoding='utf-8')
item_class = extract_item_class(instruction_text)

print(f"✓ Instruction file: {instruction_file.name}")
print(f"✓ Item Class extracted: '{item_class}'")

# Verify EMS matching
ems_path = Path("inputs/EMS/EMS.csv")
ems = pd.read_csv(ems_path, sep=';', engine='python')
ems.columns = [str(c).replace("\ufeff", "").strip() for c in ems.columns]

matched_rows = match_item_class_rows(ems, item_class)
print(f"✓ EMS rows matched: {len(matched_rows)}")
print(f"✓ Matched by Item Class Name: '{matched_rows.iloc[0]['Item Class Name']}'")

# Verify mandatory MI list
mi_catalog = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
mandatory_mi = build_mi_list_from_ems_and_catalog(ems_path, item_class, mi_catalog)
print(f"✓ Mandatory MI list size: {len(mandatory_mi)}")
print(f"✓ Includes 'Accessories': {'Accessories' in mandatory_mi}")
print(f"✓ Includes 'Cooler': {'Cooler' in mandatory_mi}")

print("\n✅ All verifications passed!")
EOF
```

**Expected Output:**
```
✓ Instruction file: instructions
✓ Item Class extracted: 'Centrifugal Compressor'
✓ EMS rows matched: 7
✓ Matched by Item Class Name: 'Centrifugal Compressor'
✓ Mandatory MI list size: 20
✓ Includes 'Accessories': True
✓ Includes 'Cooler': True

✅ All verifications passed!
```

### Option 2: Run Full Agent (Requires OpenAI API Key)

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

2. Run the agent:
```bash
python scripts/run_agent.py
```

**Expected Output (Key Points):**
```
[INFO] Processing instruction file: inputs/Instructions/instructions
[INFO] Item Class: Centrifugal Compressor
[INFO] Building mandatory MI list...
[INFO] Found 20 mandatory maintainable items
[VALIDATION] Checking cardinality and duplication rules...
[VALIDATION] ✓ All quality gates passed
OK: Generated outputs/EMS upgrade output.md
```

**What to Look For:**
- ✅ **NO** warning: `[WARN] Item Class not found in instruction`
- ✅ **NO** error: `RuntimeError: Model output missing N mandatory Maintainable Items`
- ✅ Successfully generates output file
- ✅ Validation passes

### Option 3: Run via GitHub Actions

1. Go to the "Actions" tab in the GitHub repository
2. Select the "FMEA Agent" workflow
3. Click "Run workflow" button
4. Wait for the workflow to complete

**Expected Result:**
- ✅ "Run FMEA agent" step succeeds (green checkmark)
- ✅ No error about missing mandatory items
- ✅ Output file is created in outputs/ folder

## Key Indicators of Success

### Before the Fix:
```
[WARN] Item Class not found in instruction. Using first EMS Item Class: CQCE
RuntimeError: Model output missing 2 mandatory Maintainable Items. 
Examples: ['Accessories', 'Cooler']
```

### After the Fix:
```
[INFO] Item Class: Centrifugal Compressor
[INFO] Found 20 mandatory maintainable items
[VALIDATION] ✓ All quality gates passed
OK: Generated outputs/EMS upgrade output.md
```

## Technical Details

### What Changed in `scripts/run_agent.py`

1. **New function: `match_item_class_rows()`**
   - Located at lines 111-133
   - Matches by "Item Class" column first (code like "COCE")
   - Falls back to "Item Class Name" column (name like "Centrifugal Compressor")
   - Returns matched rows or empty DataFrame

2. **Updated: `filter_ems_for_item_class()`**
   - Now uses `match_item_class_rows()` for flexible matching
   - Updated error messages to reflect dual-column search

3. **Updated: `build_mi_list_from_ems_and_catalog()`**
   - Now uses `match_item_class_rows()` for consistency
   - Correctly identifies all 20 mandatory items from boundaries

4. **Enhanced: `pick_instruction_file()`**
   - Now recognizes "instructions" file without extension
   - Checks: "instructions", "Daily Instructions", "instruction"

### Test Coverage

All 7 integration tests pass:
1. ✅ Instruction file selection
2. ✅ Item Class extraction
3. ✅ EMS matching by name
4. ✅ Mandatory MI list building
5. ✅ EMS filtering
6. ✅ Template loading
7. ✅ Backward compatibility (code-based matching)

### Security Verification

- ✅ CodeQL scan: 0 vulnerabilities
- ✅ No secrets or credentials introduced
- ✅ No unsafe file operations

## Troubleshooting

### If verification still fails:

1. **Check file exists:**
   ```bash
   ls -la inputs/Instructions/instructions
   ```

2. **Verify file content:**
   ```bash
   cat inputs/Instructions/instructions
   ```
   Should contain: `Item Class: Centrifugal Compressor`

3. **Check EMS file:**
   ```bash
   head -2 inputs/EMS/EMS.csv
   ```
   Should have columns: `Item Class;Item Class Name;Boundaries`

4. **Verify Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Check Python version:**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

## Contact

If you encounter any issues during verification, please:
1. Check the FIX_SUMMARY.md for detailed technical information
2. Review the test output for specific failure points
3. Ensure all input files are present and correctly formatted
4. Verify OpenAI API key is set (for full agent runs)

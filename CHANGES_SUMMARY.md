# FMEA Agent - Cardinality and Duplication Fix Summary

## Problem Statement

The FMEA agent had two critical issues:

1. **Cardinality Violations**: Maintainable Items were generating only 1-3 Symptoms instead of the required 4-8
2. **Duplication Issue**: Failure Mechanisms were appearing with the same term as Symptoms (e.g., "2.1 Cavitation" in both columns)

### Example of Issues in Previous Output

- Most Maintainable Items had only 1-2 symptoms (should be 4-8)
- Row 12: Symptom "2.1 Cavitation" + Mechanism "2.1 Cavitation" (duplication)
- Multiple rows with "VIB - Vibration" as Symptom and "1.2 Vibration" as Mechanism (duplication)

## Solution Implemented

### 1. Enhanced Specification Files

#### `templates/templates/spec_fmea_ems_rev01.md`

**Added CRITICAL CONSTRAINTS section at the top:**
- Explicit 4-8 symptom requirement per MI
- Many-to-many structure requirement (1-5 mechanisms per symptom)
- NO DUPLICATION rule with clear examples
- Verification requirement before output

**Enhanced FAILURE MECHANISM RULES:**
- Added **CRITICAL ANTI-DUPLICATION RULE** with BAD/GOOD examples
- Made it clear that Symptom (what you OBSERVE) ≠ Mechanism (what CAUSES it)

**Enhanced Quality Gates:**
- **G1**: Made verification mandatory with explicit "DO NOT PROCEED" instruction
- **G2**: Made mechanism planning mandatory before output
- **G7**: NEW gate specifically for NO DUPLICATION with row-by-row check requirement

**Updated Verification Checklist:**
- Added critical markers to emphasize mandatory checks
- Added explicit duplication check step
- Added minimum row count validation

#### `templates/templates/output_schema.md`

**Enhanced Failure Mechanism column definition:**
- Added CRITICAL anti-duplication rule with 4 examples (2 BAD, 2 GOOD)
- Emphasized Symptom vs Mechanism distinction

**Enhanced Quality Gate Checks:**
- Made G1 check mandatory with pre-planning requirement
- Added G7 for duplication prevention
- Added explicit method for checking duplication

**Updated Validation Checklist:**
- Added CRITICAL markers for key checks
- Added explicit duplication check
- Adjusted expected row counts to realistic ranges

#### `templates/templates/system_prompt.md`

**Enhanced Failure Mode and Cause Logic:**
- Added CRITICAL constraint about Symptom ≠ Mechanism
- Added 4 examples (2 BAD, 2 GOOD) for clarity

### 2. Enhanced Run Agent Script

#### `scripts/run_agent.py`

**Added `validate_output_cardinality()` function:**
- Parses output table programmatically
- Validates G1: Counts symptoms per MI, reports violations if < 4 or > 8
- Validates G2: Counts mechanisms per (MI, Symptom) pair, reports violations if > 5
- Validates G7: Checks each row for term duplication between Symptom and Mechanism
  - Checks for identical terms
  - Checks for same codes (e.g., "2.1" in both)
  - Checks for key terms appearing in both (e.g., "cavitation")

**Added validation enforcement:**
- Output is validated after generation and before saving
- Validation errors cause the script to fail with detailed error messages
- Only valid output is saved to outputs/

**Enhanced user prompt:**
- Added "CRITICAL REMINDERS BEFORE YOU START" section
- Explicit warnings that output will be automatically validated
- BAD/GOOD examples repeated for emphasis
- Clear warning that output will be rejected if rules are violated

### 3. Updated Instructions

#### `inputs/Instructions/instructions`

- Updated to reference G1–G7 (instead of G1–G6)
- Added explicit cardinality reminders
- Added many-to-many relationship reminder

## Validation Results

### Current Output Analysis (Before Fix)

Testing the validation function on the current output revealed:

**49 validation errors:**
- 28 G1 violations (cardinality): All MIs had 1-3 symptoms instead of 4-8
- 21 G7 violations (duplication): Multiple cases of same terms in Symptom and Mechanism columns

### Expected Behavior After Fix

When the agent runs with the updated templates:

1. **Each Maintainable Item will have 4-8 distinct Symptoms**
   - Complex items (e.g., Impeller, Shaft): 6-8 symptoms
   - Moderate items (e.g., Bearing, Coupling): 5-6 symptoms
   - Simple items (e.g., Filter, Sensor): 4-5 symptoms

2. **Each (MI, Symptom) pair will have 1-5 distinct Failure Mechanisms**
   - Critical symptoms on critical items: 3-5 mechanisms
   - Moderate importance: 2-3 mechanisms
   - Simple/single cause symptoms: 1-2 mechanisms

3. **No duplication between Symptom and Mechanism on any row**
   - If Symptom is "VIB - Vibration", Mechanism will be "Fatigue", "Misalignment", etc. (NOT "1.2 Vibration")
   - If Symptom is "NOI - Noise", Mechanism can be "Cavitation" (different observation vs cause)

4. **Typical output size**
   - Minimum: 4 rows per MI (4 symptoms × 1 mechanism each)
   - Typical complex MI: 10-20 rows (6 symptoms × 2-3 mechanisms)
   - Total for complete Item Class: 150-500+ rows

## How to Test

1. Ensure OpenAI API key is set: `export OPENAI_API_KEY=your_key`
2. Run the agent: `cd /home/runner/work/fmea-agent/fmea-agent && python scripts/run_agent.py`
3. The agent will:
   - Generate the FMEA output
   - Automatically validate it
   - Report validation errors if any
   - Save to `outputs/EMS upgrade output.md` only if validation passes

## Files Changed

1. `templates/templates/spec_fmea_ems_rev01.md` - Enhanced specification with stronger cardinality and anti-duplication rules
2. `templates/templates/output_schema.md` - Enhanced schema with explicit validation requirements
3. `templates/templates/system_prompt.md` - Enhanced prompt with anti-duplication examples
4. `scripts/run_agent.py` - Added validation logic and critical reminders
5. `inputs/Instructions/instructions` - Updated to reference G7 and cardinality requirements

## Key Improvements

1. **Proactive Prevention**: Multiple layers of instruction to prevent issues before they occur
2. **Automated Validation**: Programmatic checking ensures output meets requirements
3. **Clear Examples**: BAD/GOOD examples help the AI understand what to avoid
4. **Fail-Fast**: Agent fails immediately if output doesn't meet requirements
5. **Detailed Error Messages**: Validation errors are specific and actionable

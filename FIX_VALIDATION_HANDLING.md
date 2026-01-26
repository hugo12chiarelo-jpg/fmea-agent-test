# Fix: FMEA Agent Validation Error Handling

## Problem
When validation rules (gates G1, G2, or G7) were violated, the FMEA agent would immediately stop execution and raise a RuntimeError, preventing any output from being generated. This was problematic because:

1. The AI might generate output with minor violations that could be easily corrected
2. Users couldn't get any output even if most of it was correct
3. No automatic retry or correction mechanism existed

## Solution
Modified `scripts/run_agent.py` to implement automatic validation error correction:

### Key Changes

1. **Added configurable retry attempts**
   - New environment variable `MAX_CORRECTION_ATTEMPTS` (default: 3)
   - Controls how many times the AI will attempt to fix validation errors

2. **Implemented correction loop**
   - When validation fails, instead of raising an error, the agent:
     - Displays the specific validation errors
     - Sends a correction request to the AI with the error details
     - Validates the corrected output
     - Repeats up to `MAX_CORRECTION_ATTEMPTS` times

3. **Graceful degradation**
   - If corrections fail after all attempts, the output is still saved
   - A warning message is displayed for manual review
   - No RuntimeError is raised - the program completes successfully

### Behavior

#### Before Fix
```
[VALIDATION] Checking cardinality and duplication rules...
[ERROR] Output validation failed:
  - G1 VIOLATION: 'Pump' has only 2 symptom(s), need 4-8
  - G7 VIOLATION: Row 5: Term 'vibration' appears in both columns
RuntimeError: Output validation failed with 2 error(s)
```
Program exits with error code 1, no output saved.

#### After Fix
```
[VALIDATION] Checking cardinality and duplication rules...
[VALIDATION] ⚠️  Found 2 validation error(s) (Attempt 1/3):
  - G1 VIOLATION: 'Pump' has only 2 symptom(s), need 4-8
  - G7 VIOLATION: Row 5: Term 'vibration' appears in both columns

[CORRECTION] Requesting AI to fix validation errors...
Token usage (correction) -> input: 15234, output: 8456
Estimated cost (gpt-4.1-mini Standard): $0.0392

[VALIDATION] Checking cardinality and duplication rules...
[VALIDATION] ✓ All quality gates passed
OK: Generated outputs/EMS upgrade output.md
```
Program completes successfully with corrected output.

### Configuration

Set the maximum number of correction attempts:
```bash
export MAX_CORRECTION_ATTEMPTS=3  # default is 3
```

Set to 0 to disable automatic correction (original behavior, but with warning instead of error).

## Testing

The fix was tested with:
1. Valid outputs - no corrections needed
2. G1 violations (cardinality) - correctly detected and correction requested
3. G7 violations (duplication) - correctly detected and correction requested

## Benefits

1. **Resilient execution** - Program doesn't crash on validation errors
2. **Automatic correction** - AI attempts to fix issues without user intervention
3. **Transparency** - All validation errors and correction attempts are logged
4. **Fallback safety** - Output saved even if corrections fail (with warnings)
5. **Cost visibility** - Token usage for corrections is tracked and displayed

## Impact on Issue

This fix directly addresses the issue reported:
- ✅ "se algum dos gates ou regras for violado o programa não deve parar"
  - Translation: "if any of the gates or rules are violated, the program should not stop"
  - **Fixed**: Program no longer stops when validation fails
  
- ✅ "ele deve na verdade ser revisto a linha de saída a fim de respeitar a regra"
  - Translation: "it should actually review the output line in order to respect the rule"
  - **Fixed**: AI automatically reviews and corrects the output to meet the rules

## Files Modified

- `scripts/run_agent.py` - Added automatic correction loop and graceful error handling

## Usage

No changes to the basic workflow:
```bash
export OPENAI_API_KEY=your_key
cd /home/runner/work/fmea-agent/fmea-agent
python scripts/run_agent.py
```

The agent will now automatically attempt to correct any validation errors.

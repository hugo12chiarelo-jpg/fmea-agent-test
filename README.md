# fmea-agent
FMEA knowledge base and automation

## Output Format

The FMEA agent generates output in **CSV format** for easy import into spreadsheet applications and data analysis tools.

- **Output file**: `outputs/EMS upgrade output.csv`
- **Format**: Standard CSV with comma separators
- **Columns**: Multiple columns including Item Class, Function, Maintainable Item, Maintainable Item Function, Symptom, Failure Mechanism, Failure Effect, Treatment Actions, Reporting Question ID, and Treatment Action Type
- **Encoding**: UTF-8

The CSV file can be opened in Excel, Google Sheets, or any CSV-compatible application.

## Runtime Configuration

- `API_KEY_CLAUDESONNET` (required): Claude Sonnet API key used by the generator model.
- `CLAUDE_MODEL` (optional): Claude model name (default: `claude-sonnet-4-5`). Empty/invalid values automatically fall back to `claude-sonnet-4-5`.
- `CLAUDE_BASE_URL` (optional): Anthropic OpenAI-compatible base URL (default: `https://api.anthropic.com/v1`).
- `API_KEY_LEVITY` (optional): Levity API key used to search manuals online.
- `ENABLE_LEVITY_MANUAL_LOOKUP` (optional): defaults to disabled; set to `1`/`true`/`yes`/`on` to enable Levity manual lookup.
- `LEVITY_API_URL` (optional): Levity endpoint for manual search (default: `https://api.levity.ai/manual-search`).
- `INPUT_TOKEN_COST_PER_MILLION` / `OUTPUT_TOKEN_COST_PER_MILLION` (optional): token pricing used for cost estimation logs.

## Instructions Input

The agent now supports mass processing from `inputs/Instructions/*.xlsx`.

Expected columns:
- `Item Class` (required)
- `Item Class Description` (optional)
- `Scope` (optional)

The local manual input folder (`inputs/Manual`) is no longer required.  
When `Scope` is not provided in Instructions, the agent tries to use the `Scope` column from EMS for the matched Item Class.

When an XLSX file is present, each row is processed as one FMEA run and outputs are saved per item class.

## Recent Fixes: Automatic Validation Error Correction

The FMEA agent now automatically attempts to fix validation errors instead of stopping execution.

**Key improvements:**
- ✅ Program no longer crashes when validation rules are violated
- ✅ AI automatically reviews and corrects output to meet requirements
- ✅ Up to 3 automatic correction attempts (configurable via `MAX_CORRECTION_ATTEMPTS`)
- ✅ Output saved even if corrections fail (with warnings for manual review)

### Supported Corrections

1. **Missing Mandatory Maintainable Items (MIs)**
   - Automatically requests AI to add missing MIs to the output
   - Ensures all MIs from EMS boundaries are included
   - Example: If "Accessories" or "Piping" are missing, AI will generate complete FMEA sections for them

2. **Cardinality and Duplication Rules (G1-G7)**
   - Each MI must have 4-8 distinct symptoms
   - Each (MI, Symptom) pair must have 2-5 distinct failure mechanisms
   - No duplication between symptom and failure mechanism on same row

See [FIX_SUMMARY.md](FIX_SUMMARY.md) and [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) for more details on previous fixes.

# fmea-agent
FMEA knowledge base and automation

## Output Format

The FMEA agent generates output in **CSV format** for easy import into spreadsheet applications and data analysis tools.

- **Output file**: `outputs/EMS upgrade output.csv`
- **Format**: Standard CSV with comma separators
- **Columns**: Multiple columns including Item Class, Function, Maintainable Item, Maintainable Item Function, Symptom, Failure Mechanism, Failure Effect, Treatment Actions, Reporting Question ID, and Treatment Action Type
- **Encoding**: UTF-8

The CSV file can be opened in Excel, Google Sheets, or any CSV-compatible application.

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

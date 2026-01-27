# fmea-agent
FMEA knowledge base and automation

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

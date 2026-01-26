# fmea-agent
FMEA knowledge base and automation

## Recent Fix: Automatic Validation Error Correction

The FMEA agent now automatically attempts to fix validation errors instead of stopping execution. See [FIX_VALIDATION_HANDLING.md](FIX_VALIDATION_HANDLING.md) for details.

**Key improvements:**
- ✅ Program no longer crashes when validation rules are violated
- ✅ AI automatically reviews and corrects output to meet requirements
- ✅ Up to 3 automatic correction attempts (configurable via `MAX_CORRECTION_ATTEMPTS`)
- ✅ Output saved even if corrections fail (with warnings for manual review)

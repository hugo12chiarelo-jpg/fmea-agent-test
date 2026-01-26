# GitHub Copilot Instructions for fmea-agent

## Project Overview

This repository contains an FMEA (Failure Mode and Effects Analysis) knowledge base and automation agent. The agent uses OpenAI's GPT models to automatically generate FMEA documentation based on engineering specifications, catalogs, and business rules.

## Tech Stack

- **Language**: Python 3.x
- **Key Dependencies**:
  - `openai>=1.40.0` - OpenAI API for LLM-based generation
  - `pandas>=2.0.0` - Data processing for CSV catalogs and EMS files
- **File Formats**: 
  - Markdown (.md) for templates and documentation
  - CSV for catalogs and EMS (Equipment Maintenance Strategy)
  - Text files (.txt) for business rules and manuals

## Project Structure

```
fmea-agent/
├── scripts/
│   └── run_agent.py          # Main agent logic and validation
├── templates/
│   ├── templates/            # Core prompt templates for AI
│   │   ├── system_prompt.md
│   │   ├── spec_fmea_ems_rev01.md
│   │   └── output_schema.md
│   └── fmea_principles.md
├── inputs/                   # User-provided inputs
│   ├── Instructions/         # Task instructions (parsed for Item Class)
│   ├── EMS/                  # Equipment Maintenance Strategy CSV
│   ├── Catalogs/             # Maintainable Item and Symptom catalogs
│   ├── Business_Rules/       # Engineering rules and constraints
│   └── Manual/               # Equipment manuals
└── outputs/                  # Generated FMEA documents
```

## Key Workflows

### 1. FMEA Generation (`scripts/run_agent.py`)

**Process:**
1. Reads instruction file from `inputs/Instructions/` to extract Item Class
2. Loads templates from `templates/templates/` (system prompt, spec, schema)
3. Ingests input documents:
   - Business Rules (txt)
   - EMS CSV (filtered by Item Class)
   - Catalogs (Maintainable Items, Symptoms)
   - Equipment manual (if available)
4. Builds mandatory Maintainable Item list from EMS boundaries + catalog
5. Sends structured prompt to OpenAI API
6. **Validates output** against quality gates (G1-G7)
7. Saves to `outputs/EMS upgrade output.md` only if validation passes

### 2. Quality Gates (Validation)

The agent enforces strict cardinality and quality requirements:

- **G1**: Each Maintainable Item must have 4-8 distinct Symptoms
- **G2**: Each (Maintainable Item, Symptom) pair must have 1-5 distinct Failure Mechanisms
- **G7**: No duplication - Symptom and Mechanism on same row must use different terms

**Validation is automatic and mandatory.** Output is rejected if any rule is violated.

## Critical Constraints

### DO:
- ✅ Maintain backward compatibility with existing input/output file formats
- ✅ Preserve the validation logic in `validate_output_cardinality()`
- ✅ Keep quality gates G1-G7 intact in templates
- ✅ Use pandas for CSV processing (handles various delimiters and encodings)
- ✅ Handle missing files gracefully with informative error messages
- ✅ Maintain token usage logging and cost estimation
- ✅ Follow the existing prompt engineering patterns in templates

### DON'T:
- ❌ Modify the validation thresholds (4-8, 1-5) without explicit approval
- ❌ Remove or weaken quality gates from templates
- ❌ Change the CSV parsing logic without thorough testing
- ❌ Hardcode API keys or secrets (use environment variables)
- ❌ Break the deterministic MI list generation from EMS+Catalog
- ❌ Modify file paths or directory structure without updating all references

## Code Conventions

### Python Style
- Use type hints for function parameters and return values
- Prefer pathlib.Path over string paths
- Use f-strings for formatting
- Handle exceptions with specific error messages
- Document complex functions with docstrings

### Example Pattern (from `run_agent.py`):
```python
def function_name(param: str, optional_param: int | None = None) -> str:
    """
    Brief description of what function does.
    
    Returns a list of error messages (empty if valid).
    """
    # Implementation
    return result
```

## Common Tasks

### Adding a New Quality Gate
1. Update `templates/templates/spec_fmea_ems_rev01.md` with the new gate (G8, G9, etc.)
2. Add validation logic to `validate_output_cardinality()` in `run_agent.py`
3. Update the CRITICAL REMINDERS section in the user prompt
4. Test with a full run to ensure validation works

### Modifying Templates
- Templates are in `templates/templates/` directory
- Changes affect AI behavior - test thoroughly after modification
- Use BAD/GOOD examples to guide the model
- Keep instructions explicit and actionable

### Testing Changes
```bash
# Set API key
export OPENAI_API_KEY=your_key_here

# Run the agent
python scripts/run_agent.py

# Check validation output
# Success: "[VALIDATION] ✓ All quality gates passed"
# Failure: "[ERROR] Output validation failed: ..."
```

## Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key (required)
export OPENAI_API_KEY=your_api_key

# Optional: Override model (default: gpt-4.1-mini)
export OPENAI_MODEL=gpt-4o-mini
```

## Input File Requirements

### Instructions File (`inputs/Instructions/`)
- Must contain "Item Class: <name>" or similar pattern
- Parsed using regex patterns in `extract_item_class()`
- Fallback: uses first Item Class from EMS if not specified

### EMS CSV (`inputs/EMS/EMS.csv`)
- Required columns: "Item Class", "Boundaries" (or "Boundary")
- Used to filter rows by Item Class
- Boundaries text is used to match Maintainable Items from catalog

### Catalogs (`inputs/Catalogs/`)
- `Maintainable Item Catalog.csv`: List of valid MIs
- `Symptom Catalog.csv`: List of valid symptoms
- First column used as name column if not explicitly identified

## Output Format

Generated markdown file with:
- Table format with columns: Item Class, Maintainable Item, Symptom, Failure Mechanism
- Must pass all quality gates
- Saved to `outputs/EMS upgrade output.md`

## Error Handling Patterns

```python
# Check file existence
if not path.exists():
    raise FileNotFoundError(f"Missing required file: {path}")

# CSV parsing with fallback
try:
    df = pd.read_csv(path, sep=None, engine="python")
except Exception:
    df = pd.read_csv(path, sep=";", engine="python", on_bad_lines="skip")

# Normalize CSV headers (remove BOM)
df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
```

## Documentation

- `README.md`: Basic project description
- `README_FIX.md`: Detailed fix summary for cardinality/duplication issues
- `CHANGES_SUMMARY.md`: Technical change log
- `TESTING.md`: Validation testing guide
- `scripts/read_me.md`: Script-specific documentation

## Token Usage & Costs

The agent logs token usage after each API call:
```
Token usage -> input: <n>, output: <m>
Estimated cost (gpt-4.1-mini Standard): $X.XXXX
```

Typical usage:
- Input tokens: 30k-80k (depends on manual size)
- Output tokens: 5k-15k (depends on number of Maintainable Items)
- Cost per run: $0.50-$2.00

## Security & API Keys

- ⚠️ **NEVER commit API keys to the repository**
- Use environment variables: `OPENAI_API_KEY`
- API key is read in `main()` and passed to OpenAI client
- No API keys should appear in code, templates, or outputs

## When Making Changes

1. **Understand the workflow**: Read `run_agent.py` to see how components interact
2. **Check templates first**: AI behavior is controlled by templates in `templates/templates/`
3. **Validate thoroughly**: Run the full agent after changes and check validation output
4. **Update documentation**: Modify this file and other docs if you change behavior
5. **Test with real inputs**: Use sample files from `inputs/` directories

## Getting Help

- Check validation error messages - they're designed to be actionable
- Review `README_FIX.md` for details on the cardinality/duplication fix
- Examine template files to understand prompt engineering approach
- Look at `TESTING.md` for validation examples

---

**Last Updated**: 2026-01-26
**Maintained by**: GitHub Copilot Coding Agent

import os
import re
from io import StringIO
from pathlib import Path

import pandas as pd
from openai import OpenAI

TEXT_EXT = {".md", ".txt", ".csv", ".json"}

# Validation threshold: Flag if more than this ratio of (MI, Symptom) pairs have only 1 mechanism
MAX_SINGLE_MECHANISM_RATIO = 0.70

# Boundary parsing constants
MIN_WORD_LENGTH_FOR_EXCLUSION = 2  # Minimum word length to consider as significant for exclusion checks
MIN_STEM_MATCH_LENGTH = 5  # Minimum character overlap for stem matching to avoid false positives
EXCLUSION_STOP_WORDS = {'and', 'the', 'or', 'with', 'for', 'in', 'of', 'to', 'a', 'an'}


def read_required(path_a: str, path_b: str) -> str:
    p1 = Path(path_a)
    if p1.exists():
        return p1.read_text(encoding="utf-8", errors="ignore")
    p2 = Path(path_b)
    if p2.exists():
        return p2.read_text(encoding="utf-8", errors="ignore")
    raise FileNotFoundError(f"Missing both: {path_a} and {path_b}")


def pick_instruction_file() -> Path:
    instr_dir = Path("inputs/Instructions")
    if not instr_dir.exists():
        raise FileNotFoundError("Missing folder: inputs/Instructions")

    preferred = instr_dir / "instruction.md"
    if preferred.exists():
        return preferred

    candidates = [
        f
        for f in instr_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in {".md", ".txt"}
        and f.name.lower() not in {"readme.md", "readme.txt"}
    ]
    if candidates:
        candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return candidates[0]

    # Check for common no-extension instruction files
    for name in ["instructions", "Daily Instructions", "instruction"]:
        no_ext = instr_dir / name
        if no_ext.exists() and no_ext.is_file():
            return no_ext

    fallback = instr_dir / "README.md"
    if fallback.exists():
        return fallback

    raise FileNotFoundError("No instruction file found in inputs/Instructions/")


def extract_item_class(instruction_text: str) -> str:
    """
    Extract Item Class from instruction text with tolerant patterns.
    Accepts:
      - "Item Class: XYZ"
      - "Item Class = XYZ"
      - "Item Class - XYZ"
      - "Item Class — XYZ"
      - "for Item Class: XYZ"
    """
    patterns = [
        r"Item\s*Class\s*[:=]\s*(.+)",
        r"Item\s*Class\s*[-–—]\s*(.+)",
        r"for\s+Item\s*Class\s*[:=]\s*(.+)",
        r"for\s+Item\s*Class\s*[-–—]\s*(.+)",
    ]
    for pat in patterns:
        m = re.search(pat, instruction_text, flags=re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            val = val.splitlines()[0].strip()
            val = val.rstrip(" .;:,")
            return val
    return "UNKNOWN_ITEM_CLASS"


def read_text_file(path: Path, max_chars: int | None = None) -> str:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    if max_chars is not None and len(txt) > max_chars:
        return txt[:max_chars] + "\n\n[TRUNCATED]\n"
    return txt


def load_csv_preview(path: Path, max_rows: int = 200, max_cols: int = 30) -> str:
    try:
        df = pd.read_csv(path, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(path, sep=";", engine="python", on_bad_lines="skip")

    df = df.iloc[:, :max_cols]
    if len(df) > max_rows:
        df = df.head(max_rows)
        note = f"\n\n[NOTE: truncated to first {max_rows} rows]\n"
    else:
        note = ""
    return df.to_csv(index=False) + note


def match_item_class_rows(df: pd.DataFrame, item_class: str) -> pd.DataFrame:
    """
    Match rows in EMS dataframe by Item Class code OR Item Class Name.
    
    The function attempts to match in the following order:
    1. First tries 'Item Class' column (e.g., code like 'COCE')
    2. If no match, tries 'Item Class Name' column (e.g., name like 'Centrifugal Compressor')
    
    Args:
        df: DataFrame with 'Item Class' and optionally 'Item Class Name' columns
        item_class: Item Class to match (can be code like 'COCE' or name like 'Centrifugal Compressor')
        
    Returns:
        Filtered DataFrame matching the item class, or empty DataFrame if no match
    """
    item_class_lower = item_class.strip().lower()
    
    # Try matching by both columns
    for col in ["Item Class", "Item Class Name"]:
        if col in df.columns:
            mask = df[col].astype(str).str.strip().str.lower() == item_class_lower
            if mask.any():
                return df[mask]
    
    # No match found - return empty DataFrame with same columns
    return df.iloc[0:0]


def filter_ems_for_item_class(ems_path: Path, item_class: str, max_rows: int = 200) -> str:
    try:
        df = pd.read_csv(ems_path, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(ems_path, sep=";", engine="python", on_bad_lines="skip")

    # Normalize headers
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]

    if "Item Class" not in df.columns:
        return (
            "EMS.csv (unfiltered preview — Item Class column not found)\n"
            + load_csv_preview(ems_path, max_rows=max_rows)
        )

    dff = match_item_class_rows(df, item_class)

    if dff.empty:
        return (
            f"EMS.csv (no rows matched Item Class='{item_class}' in 'Item Class' or 'Item Class Name' columns)\n"
            + load_csv_preview(ems_path, max_rows=max_rows)
        )

    if len(dff) > max_rows:
        dff = dff.head(max_rows)
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}', truncated to first {max_rows} rows]\n"
    else:
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}']\n"

    return dff.to_csv(index=False) + note


def apply_item_class_specific_rules(mi_list: list[str], item_class: str) -> list[str]:
    """
    Apply item-class-specific business rules to filter and adjust the MI list.
    
    Args:
        mi_list: Initial list of Maintainable Items
        item_class: The Item Class being analyzed
        
    Returns:
        Filtered and adjusted MI list
    """
    item_class_lower = item_class.lower().strip()
    
    # Rules for "Motor, Electric"
    if "motor" in item_class_lower and "electric" in item_class_lower:
        # Filter out invalid items for Electric Motor
        invalid_items = {
            "motor",  # Motor Failure is not a valid MI for electric motor itself
            "shaft",  # Shaft Failure can be disregarded per requirements
            "system",  # Too generic
            "stem",  # Too generic
            "gear",  # Use Gearbox instead
        }
        
        # Preferred naming for duplicates (map shorter/incorrect names to preferred names)
        preferred_names = {
            "cooling": "Cooling system",
            "heater": "Heaters",
            "instrument": "Monitoring",  # Instrumentation → Monitoring
            "control system": "Control system",  # Normalize casing
        }
        
        # Filter and normalize
        filtered = []
        seen_lower = set()
        
        for mi in mi_list:
            mi_lower = mi.lower().strip()
            
            # Skip if it's in the invalid set
            if mi_lower in invalid_items:
                continue
            
            # Skip very generic or short terms
            if len(mi) < 3:
                continue
            
            # Apply preferred naming
            if mi_lower in preferred_names:
                preferred = preferred_names[mi_lower]
                preferred_lower = preferred.lower().strip()
                if preferred_lower not in seen_lower:
                    filtered.append(preferred)
                    seen_lower.add(preferred_lower)
                continue
            
            # Check for duplicates (e.g., "Heaters" when we already have "Heater" → prefer "Heaters")
            # If current item is singular and we have plural, skip
            # If current item is plural and we have singular, replace
            plural = mi_lower + 's' if not mi_lower.endswith('s') else mi_lower
            singular = mi_lower[:-1] if mi_lower.endswith('s') and len(mi_lower) > 4 else mi_lower
            
            # Skip if we've already seen a variant
            if plural in seen_lower or singular in seen_lower:
                # Prefer plural form
                if plural == mi_lower:
                    # Current is plural, remove singular if present
                    filtered = [f for f in filtered if f.lower().strip() != singular]
                    seen_lower.discard(singular)
                    filtered.append(mi)
                    seen_lower.add(mi_lower)
                # else: skip (singular, we already have plural or exact)
                continue
            
            # Add if not seen
            if mi_lower not in seen_lower:
                filtered.append(mi)
                seen_lower.add(mi_lower)
        
        # Ensure critical items are present with proper naming
        critical_items = {
            "Bearing",  # Can be NDE Bearing, DE Bearing, or just Bearing
            "Rotor",
            "Stator", 
            "Windings",
            "Coupling",
            "Gearbox",
            "Brushes",
            "Cooling system",
            "Enclosure",
            "Control system",
            "Junction box",
            "Heaters",
            "Monitoring",
        }
        
        # Add any missing critical items
        existing_lower = {mi.lower().strip() for mi in filtered}
        for critical in critical_items:
            critical_lower = critical.lower().strip()
            # Check if any variation already exists
            found = critical_lower in existing_lower
            if not found:
                filtered.append(critical)
        
        # Final deduplication (case-insensitive, keep first occurrence)
        final = []
        seen = set()
        for mi in filtered:
            mi_lower = mi.lower().strip()
            if mi_lower not in seen:
                final.append(mi)
                seen.add(mi_lower)
        
        return sorted(final)
    
    # Default: return as-is for other item classes
    return mi_list


def build_mi_list_from_ems_and_catalog(ems_path: Path, item_class: str, mi_catalog_path: Path) -> list[str]:
    """
    Build a comprehensive list of Maintainable Items from EMS boundaries and MI catalog.
    
    This function:
    1. Parses the EMS Boundaries column to identify included/excluded items
    2. Filters out items marked with "Exclude", "optional", "if applicable"
    3. Maps boundary terms to standard Maintainable Item Catalog terminology
    4. Applies item-class-specific business rules
    5. Returns ALL technically relevant items from boundaries
    
    Args:
        ems_path: Path to EMS.csv file
        item_class: Target Item Class to filter
        mi_catalog_path: Path to Maintainable Item Catalog.csv
        
    Returns:
        List of Maintainable Items (catalog terminology) that should be included
    """
    # Read EMS
    try:
        ems = pd.read_csv(ems_path, sep=None, engine="python")
    except Exception:
        ems = pd.read_csv(ems_path, sep=";", engine="python", on_bad_lines="skip")

    # Normalize headers
    ems.columns = [str(c).replace("\ufeff", "").strip() for c in ems.columns]

    if "Item Class" not in ems.columns:
        raise RuntimeError(f"EMS.csv must contain column 'Item Class'. Found: {list(ems.columns)}")

    # Find boundary column
    boundary_col = None
    for c in ems.columns:
        if str(c).strip().lower() in {"boundaries", "boundary"}:
            boundary_col = c
            break
    if boundary_col is None:
        raise RuntimeError(
            f"EMS.csv must contain a 'Boundaries' column (or 'Boundary'). Found: {list(ems.columns)}"
        )

    rows = match_item_class_rows(ems, item_class)
    if rows.empty:
        sample = ems["Item Class"].astype(str).str.strip().dropna().unique()[:10].tolist()
        raise RuntimeError(
            f"No EMS rows matched Item Class='{item_class}' (tried both 'Item Class' and 'Item Class Name'). Sample EMS Item Class values: {sample}"
        )

    # Convert to strings robustly - handle NaN, floats, and other types
    boundary_values = rows[boundary_col].fillna('').astype(str).tolist()
    boundary_text = "\n".join(boundary_values)

    # Read MI catalog - it's a simple single-column file
    try:
        # Try reading as plain text first (most reliable for single-column files)
        with open(mi_catalog_path, 'r', encoding='utf-8-sig') as f:
            catalog_items = [line.strip() for line in f if line.strip() and line.strip().lower() not in ('maintainable item', 'maintainable_item')]
    except Exception:
        # Fallback to pandas
        try:
            mi_df = pd.read_csv(mi_catalog_path, sep=None, engine="python", on_bad_lines="skip")
        except Exception:
            mi_df = pd.read_csv(mi_catalog_path, sep=";", engine="python", on_bad_lines="skip")
        
        mi_df.columns = [str(c).replace("\ufeff", "").strip() for c in mi_df.columns]
        
        # Identify MI name column
        name_col = None
        for c in mi_df.columns:
            if str(c).strip().lower() in {"maintainable item", "maintainable_item", "name", "item"}:
                name_col = c
                break
        if name_col is None:
            name_col = mi_df.columns[0]
        
        catalog_items = mi_df[name_col].astype(str).str.strip().tolist()
        # Filter out empty, nan, and ensure all are strings
        catalog_items = [str(item) for item in catalog_items if item and str(item).lower() not in ('nan', 'none', '')]
    
    # Remove duplicates and sort
    catalog_items = sorted(list(set(catalog_items)))
    
    # Parse boundaries to identify included and excluded items
    included_items = []
    excluded_items = []
    
    # Split boundary text into lines for processing
    boundary_lines = boundary_text.split('\n')
    
    for line in boundary_lines:
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
            
        # Check if line contains exclusion keywords
        is_excluded = (
            line_lower.startswith('exclude ') or
            line_lower.startswith('excludes ') or
            (len(line_lower) > 10 and 'exclude ' in line_lower[:15]) or
            'optional' in line_lower or
            'if applicable' in line_lower or
            'if any' in line_lower
        )
        
        # Match catalog items against this line
        for mi in catalog_items:
            if not mi or len(mi) < 3:  # Skip very short items
                continue
            mi_lower = mi.lower()
            
            # Check if the catalog item matches this line
            # Prioritize exact matches over word-stem matches
            is_match = False
            match_type = None
            
            # Method 1: Direct substring match (catalog item in line) - EXACT MATCH
            if mi_lower in line_lower:
                is_match = True
                match_type = "exact"
                # Special case: Check if it's a more specific exclusion
                # e.g., "Anti-surge" system vs "Anti surge valve"
                # If the exclusion line specifies a more specific item (contains additional words after the match),
                # don't exclude the general item
                if is_excluded:
                    # Extract the part after the catalog item match
                    match_idx = line_lower.find(mi_lower)
                    after_match = line_lower[match_idx + len(mi_lower):].strip()
                    # If there are significant words after the match, it's a more specific item
                    after_words = [w for w in after_match.split() if len(w) > MIN_WORD_LENGTH_FOR_EXCLUSION and w not in EXCLUSION_STOP_WORDS]
                    if after_words:
                        # This is a more specific item (e.g., "anti surge valve"), don't exclude the general item
                        is_match = False
            
            # Method 2: Check if any word in line starts with catalog item (for stems) - WORD STEM MATCH
            # Only use this if no exact match was found
            if not is_match:
                # e.g., "instrument" (catalog) matches "instrumentation" (boundary)
                # Only match if word starts with catalog item, and catalog item is long enough to avoid false positives
                words = re.split(r'[\s,/\-()]+', line_lower)
                for word in words:
                    # Catalog item must be at least MIN_STEM_MATCH_LENGTH chars to avoid false matches
                    # Word must start with the full catalog item
                    if len(mi_lower) >= MIN_STEM_MATCH_LENGTH and word.startswith(mi_lower):
                        is_match = True
                        match_type = "stem"
                        break
            
            if is_match:
                if is_excluded:
                    if mi not in excluded_items:
                        excluded_items.append(mi)
                else:
                    if mi not in included_items:
                        included_items.append(mi)
    
    # Remove any items that appear in both lists (exclusion takes precedence)
    final_included = [mi for mi in included_items if mi not in excluded_items]
    
    # Also do a broader match on the entire boundary text (excluding explicit exclusion sections)
    # This helps catch items that might be phrased differently
    bt_lower = boundary_text.lower()
    
    # Split into included and excluded sections
    boundary_parts = re.split(r'\n\s*exclude\s+', bt_lower, flags=re.IGNORECASE)
    included_boundary = boundary_parts[0] if boundary_parts else ""
    
    # Check catalog items against included boundary section
    for mi in catalog_items:
        if not mi:
            continue
        mi_lower = mi.lower()
        
        # Check if item is mentioned in included section
        if mi_lower in included_boundary:
            # Make sure it's not in excluded items and not already in final list
            if mi not in excluded_items and mi not in final_included:
                final_included.append(mi)
    
    # Sort for consistency
    final_included = sorted(set(final_included))
    
    # Apply item-class-specific business rules
    final_included = apply_item_class_specific_rules(final_included, item_class)
    
    return final_included


def build_item_class_specific_guidance(item_class: str) -> str:
    """
    Build item-class-specific guidance for the AI.
    
    Args:
        item_class: The Item Class being analyzed
        
    Returns:
        Guidance text to be added to the prompt
    """
    item_class_lower = item_class.lower().strip()
    
    # Guidance for "Motor, Electric"
    if "motor" in item_class_lower and "electric" in item_class_lower:
        return """
## ITEM-CLASS-SPECIFIC GUIDANCE: Motor, Electric

**IMPORTANT CLARIFICATIONS FOR ELECTRIC MOTOR:**

1. **Symptom-Specific Rules:**
   - "LOO - Low Output" is NOT a valid symptom for Rotor or Bearing (NDE/DE)
   - Do NOT assign "LOO - Low Output" to: Rotor Failure, Bearing Failure, NDE Bearing Failure, DE Bearing Failure
   
2. **Failure Mechanism Requirements:**
   - For Stator Failure: MUST include "4.1 - Short Circuiting" and "1.5 - Looseness" as mechanisms
     * Assign these to appropriate symptoms (e.g., "4.1 - Short Circuiting" → symptoms like "NOO - No output", "OHE - Overheating")
     * Assign "1.5 - Looseness" → symptoms like "VIB - Vibration", "NOI - Noise"
   
   - For Windings Failure + Symptom "NOO - No output": MUST include "4.1 - Short circuiting" as a mechanism
   
3. **Naming Rules:**
   - All Maintainable Item names MUST end with " Failure" (e.g., "Bearing Failure", "Rotor Failure")
   - Use "Control System Failure" (not "Control Unit Failure")
   - Use "Cooling System Failure" (not "Cooler Failure")
   - Use "Junction Box Failure" (not "Junction Boxes Failure")

4. **Completeness Requirement:**
   - Generate the COMPLETE FMEA table for ALL Maintainable Items listed
   - Do NOT use placeholders like "[The rest of the table...]" or "[See above]"
   - Do NOT reference "previous completion" or "unchanged sections"
   - Every Maintainable Item must have its full set of rows in the output table
"""
    
    # Default: no specific guidance
    return ""


def pick_manual_text(item_class: str) -> Path | None:
    manual_dir = Path("inputs/Manual")
    if not manual_dir.exists():
        return None

    txts = sorted([p for p in manual_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
    if not txts:
        return None

    return txts[0]


def build_missing_mi_correction_prompt(missing_mi: list[str]) -> str:
    """
    Build a prompt to request AI to add missing mandatory Maintainable Items.
    
    Args:
        missing_mi: List of missing mandatory Maintainable Item names
        
    Returns:
        Formatted correction prompt
    """
    missing_summary = "\n".join([f"  - {mi} Failure" for mi in missing_mi])
    return f"""
⚠️ CRITICAL ERROR: The FMEA table you provided is INCOMPLETE and INVALID.

**MISSING MANDATORY MAINTAINABLE ITEMS** (have ZERO rows in the table):

{missing_summary}

**ROOT CAUSE**: You used placeholder text like "(Additional rows... omitted for brevity)" instead of generating ACTUAL TABLE ROWS.

**THIS IS UNACCEPTABLE**. Each Maintainable Item MUST have its complete set of rows explicitly written in the table.

**REQUIRED CORRECTIVE ACTION**:

Regenerate the COMPLETE FMEA table from scratch with EVERY SINGLE ROW written out explicitly:

1. **INCLUDE ALL MAINTAINABLE ITEMS**:
   - All existing MIs you already generated (keep them)
   - ALL missing MIs listed above (add them with complete rows)

2. **FOR EACH MAINTAINABLE ITEM**:
   - Generate 4-8 DISTINCT Symptoms
   - For EACH Symptom, generate 2-5 DISTINCT Failure Mechanisms
   - Write a separate table row for EACH mechanism
   - Example: "Rotor Failure" with 5 symptoms × 3 mechanisms each = 15 rows minimum

3. **ABSOLUTELY FORBIDDEN**:
   - ❌ NO placeholder text like "(Additional rows...)", "[The rest...]", "[See above]"
   - ❌ NO ellipsis (...) or truncation
   - ❌ NO references like "unchanged sections", "similar to above", "previously shown"
   - ❌ NO summarizing or shortcutting - write every single row explicitly

4. **NAMING CONVENTION**:
   - All Maintainable Items MUST end with " Failure" suffix
   - Examples: "Bearing Failure", "Rotor Failure", "Stator Failure", "Windings Failure"

5. **QUALITY RULES** (will be validated):
   - Each MI MUST have EXACTLY 4-8 distinct symptoms
   - Each (MI, Symptom) pair MUST have 2-5 distinct mechanisms
   - NO DUPLICATION: Symptom and Mechanism on same row must use DIFFERENT terms
   - Symptom = observable effect, Mechanism = root cause

**OUTPUT FORMAT**: 
Return ONLY the complete markdown FMEA table with the following structure:
- Table header row
- Separator row
- Data rows for EVERY Maintainable Item (no exceptions, no placeholders)
- Optional summary at the end

**VERIFICATION BEFORE SUBMITTING**:
Before you finalize, count:
- How many distinct Maintainable Items have rows? (Must be ALL of them)
- Does any MI have < 4 or > 8 symptoms? (Fix if yes)
- Do you see any placeholder text? (Remove and write actual rows)

Return the COMPLETE, EXPLICIT, FULLY-EXPANDED FMEA table now.
"""


def build_correction_prompt(validation_errors: list[str]) -> str:
    """
    Build a prompt to request AI to fix validation errors.
    
    Args:
        validation_errors: List of validation error messages
        
    Returns:
        Formatted correction prompt
    """
    error_summary = "\n".join([f"  - {err}" for err in validation_errors])
    return f"""
The output you provided has validation errors that MUST be fixed:

{error_summary}

Please revise the ENTIRE FMEA table to fix these violations while keeping the same structure and format.

CRITICAL RULES TO FOLLOW:
1. Each Maintainable Item MUST have EXACTLY 4-8 DISTINCT Symptoms
   - If an MI has fewer than 4 symptoms, ADD more distinct symptoms from the catalogs
   - If an MI has more than 8 symptoms, CONSOLIDATE similar ones
   
2. Each (Maintainable Item, Symptom) pair MUST have MULTIPLE (2-5) DISTINCT Failure Mechanisms
   - **DO NOT generate only 1 mechanism per symptom for all items**
   - Complex/critical items should have 2-5 mechanisms per symptom
   - For each symptom, think: "What are the DIFFERENT physical causes that could produce this symptom?"
   - Examples:
     * "Shaft Failure" + "VIB - Vibration" → should have 3-4 mechanisms like: Fatigue, Misalignment, Unbalance, Wear
     * "Bearing Failure" + "VIB - Vibration" → should have 2-3 mechanisms like: Wear, Misalignment, Fatigue
     * "Filter Failure" + "PLU - Plugged" → may have 1-2 mechanisms like: Blockage, Contamination
   - Generate separate rows for each mechanism (same MI + Symptom can appear on multiple rows with different mechanisms)
   
3. NO DUPLICATION: Symptom and Failure Mechanism on same row MUST use DIFFERENT terms
   - If Symptom is "VIB - Vibration", Mechanism CANNOT be "1.2 Vibration" or contain "Vibration"
   - If Symptom is "2.1 Cavitation", Mechanism CANNOT be "2.1 Cavitation" or contain "Cavitation"
   - Symptom = what you OBSERVE (effect)
   - Mechanism = what CAUSES it (root cause) - must be different from the symptom

Return the COMPLETE corrected output with the FULL table (not just the fixes).
Include ALL rows with the expanded mechanisms.
"""


def validate_mi_in_table(output_text: str, mandatory_mi: list[str]) -> list[str]:
    """
    Validate that all mandatory MIs appear in the actual FMEA table (not just in text).
    Also detects if AI is using placeholders instead of generating actual rows.
    
    Args:
        output_text: The AI-generated output
        mandatory_mi: List of mandatory Maintainable Item names (without " Failure" suffix)
        
    Returns:
        List of missing MI names (empty if all are present in table)
    """
    missing: list[str] = []
    
    # First, detect placeholder text patterns that indicate incomplete output
    placeholder_patterns = [
        'additional rows',
        'omitted for brevity',
        'follow,',
        'see above',
        'unchanged',
        'rest of the table',
        'similar to above',
        'previously shown',
        'as shown above',
        '...',  # ellipsis often indicates truncation
    ]
    
    output_lower = output_text.lower()
    found_placeholders = []
    for pattern in placeholder_patterns:
        if pattern in output_lower:
            found_placeholders.append(pattern)
    
    if found_placeholders:
        print(f"[VALIDATION] ⚠️  Detected placeholder text patterns: {found_placeholders}")
        print("[VALIDATION] This indicates the AI generated an incomplete table instead of full rows for all MIs")
    
    try:
        # Extract the table from the output
        lines = output_text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            if line.strip().startswith('|') and 'Item Class' in line:
                in_table = True
            if in_table:
                if line.strip().startswith('|'):
                    table_lines.append(line)
                elif line.strip() == '':
                    continue  # Skip empty lines within table
                else:
                    # Non-table content - check if it's a placeholder
                    if any(p in line.lower() for p in placeholder_patterns):
                        # Found placeholder after table - this means incomplete table
                        print(f"[VALIDATION] Found placeholder after table: {line.strip()[:100]}")
                    # End of table
                    break
        
        if len(table_lines) < 3:
            # No valid table found, all MIs are missing
            return list(mandatory_mi)
        
        # Parse actual Maintainable Items from the table column (column 4)
        # This is more precise than searching in the entire line
        actual_mis_in_table = set()
        for line in table_lines[2:]:  # Skip header and separator
            if not line.strip().startswith('|'):
                continue
            parts = line.split('|')
            if len(parts) > 3:
                mi_cell = parts[3].strip()  # Maintainable Item is typically column 4
                if mi_cell and mi_cell.lower() not in ['maintainable item', 'see above', '']:
                    # Normalize: remove " Failure" suffix for comparison
                    mi_normalized = mi_cell.lower().replace(' failure', '').strip()
                    actual_mis_in_table.add(mi_normalized)
        
        # Count rows per MI for diagnostic output
        mi_row_counts = {}
        for mi_name in mandatory_mi:
            if not mi_name:
                continue
            
            mi_lower = mi_name.lower().strip()
            mi_with_failure = (mi_lower + " failure").lower()
            
            # Count how many actual table rows contain this MI in the MI column
            row_count = 0
            for line in table_lines[2:]:  # Skip header and separator
                if not line.strip().startswith('|'):
                    continue
                parts = line.split('|')
                if len(parts) > 3:
                    mi_cell = parts[3].strip().lower()
                    if mi_lower in mi_cell or mi_with_failure in mi_cell:
                        row_count += 1
            
            mi_row_counts[mi_name] = row_count
            
            # Check if this MI is actually in the table
            if mi_lower not in actual_mis_in_table:
                missing.append(mi_name)
        
        # Print diagnostic info
        if mi_row_counts:
            print(f"[VALIDATION] Row counts per MI:")
            for mi, count in sorted(mi_row_counts.items()):
                status = "✗ MISSING" if mi in missing else "✓"
                print(f"  {status} {mi}: {count} rows")
    
    except Exception as e:
        # If parsing fails, fall back to simple text search
        print(f"[DEBUG] Table parsing failed: {e}. Falling back to simple check.")
        for mi_name in mandatory_mi:
            if mi_name and (mi_name.lower() not in output_text.lower()):
                missing.append(mi_name)
    
    return missing


def determine_equipment_complexity(item_class: str) -> str:
    """
    Determine if equipment is COMPLEX or SIMPLE based on Item Class.
    
    COMPLEX equipment (minimum 12 MIs): Motors, generators, pumps, compressors, 
    separators, heat exchangers, turbines, gearboxes, and other rotating/process equipment.
    
    SIMPLE equipment (minimum 5 MIs): Instrumentation, simple valves, lamps, 
    basic actuators, simple sensors, and other standalone equipment.
    
    Returns: "COMPLEX" or "SIMPLE"
    """
    item_class_lower = item_class.lower().strip()
    
    # Complex equipment keywords (high constructive complexity)
    complex_keywords = [
        'motor', 'generator', 'turbine', 'gas turbine', 'steam turbine',
        'pump', 'centrifugal pump', 'reciprocating pump', 'gear pump', 'screw pump',
        'compressor', 'centrifugal compressor', 'reciprocating compressor', 'screw compressor', 'axial compressor',
        'separator', 'heat exchanger', 'heater', 'cooler', 'condenser',
        'gearbox', 'speed increaser', 'speed reducer', 'transmission',
        'drive', 'mechanical drive', 'variable speed drive',
        'pressure vessel', 'reactor', 'column', 'distillation', 'absorption',
        'blower', 'fan'  # Process fans/blowers (note: small cooling fans may be misclassified as complex)
    ]
    
    # Simple equipment keywords (simpler construction)
    simple_keywords = [
        'valve', 'check valve', 'relief valve', 'manual valve', 'gate valve', 'ball valve',
        'instrument', 'transmitter', 'sensor', 'gauge', 'indicator', 'detector', 'analyzer',
        'lamp', 'light', 'lighting', 'fixture',
        'actuator', 'solenoid',
        'breaker', 'switch', 'relay',
        'tank'  # simple tanks without complex internals (pressure vessels checked first in complex)
    ]
    
    # Check for complex equipment first (takes priority)
    for keyword in complex_keywords:
        if keyword in item_class_lower:
            return "COMPLEX"
    
    # Check for simple equipment
    for keyword in simple_keywords:
        if keyword in item_class_lower:
            return "SIMPLE"
    
    # Default: If unclear, assume COMPLEX to be conservative (require more MIs)
    # This ensures comprehensive FMEA coverage for unknown equipment types
    return "COMPLEX"


def convert_markdown_table_to_csv(output_text: str) -> str:
    """
    Convert a Markdown table to CSV format.
    
    This function is specifically designed for FMEA output tables that have
    'Item Class' as the first column header.
    
    Args:
        output_text: The text containing a Markdown table
        
    Returns:
        CSV formatted string, or original text if no table found
    """
    try:
        # Extract the table from the output
        lines = output_text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            # Skip markdown code block markers
            if line.strip().startswith('```'):
                continue
            # Look for FMEA table header (starts with 'Item Class')
            if line.strip().startswith('|') and 'Item Class' in line:
                in_table = True
            if in_table:
                if line.strip().startswith('|'):
                    table_lines.append(line)
                elif line.strip() == '':
                    # Continue through empty lines within table
                    continue
                else:
                    # End of table
                    break
        
        if len(table_lines) < 2:
            # No valid table found (need at least header + 1 data row)
            return output_text
        
        # Parse the Markdown table
        table_text = '\n'.join(table_lines)
        df = pd.read_csv(StringIO(table_text), sep='|', skipinitialspace=True)
        
        # Remove empty first and last columns (artifacts of | delimiters)
        df = df.iloc[:, 1:-1]
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Remove separator rows (rows where all cells contain only dashes)
        # Separator rows have patterns like "-------" in cells
        mask = df.apply(lambda row: row.astype(str).str.strip().str.match(r'^-+$').all(), axis=1)
        df = df[~mask]
        
        if len(df) == 0:
            # No data rows found after removing separators
            return output_text
        
        # Convert to CSV
        csv_output = df.to_csv(index=False, lineterminator='\n')
        
        return csv_output
        
    except Exception as e:
        print(f"[WARN] Could not convert Markdown table to CSV: {e}")
        print("[WARN] Returning original Markdown format")
        return output_text


def validate_output_cardinality(output_text: str, item_class: str = "") -> list[str]:
    """
    Validate that the output meets cardinality requirements:
    - Each Maintainable Item has 4-8 distinct Symptoms
    - Each (MI, Symptom) pair has 2-5 distinct Failure Mechanisms
    - No duplication between Symptom and Failure Mechanism on the same row
    - Maintainable Items do not contain Symptom codes
    - Total MI count meets minimum based on equipment complexity (G9)
    
    Returns a list of error messages (empty if valid).
    """
    errors = []
    
    # Load Symptom Catalog to check for symptom codes
    symptom_codes = set()
    symptom_catalog_path = Path("inputs/Catalogs/Symptom Catalog.csv")
    if symptom_catalog_path.exists():
        try:
            # Symptom Catalog uses semicolon as separator
            symptom_df = pd.read_csv(symptom_catalog_path, sep=';', encoding='utf-8', encoding_errors='ignore')
            # Extract symptom codes from first column (Code)
            if 'Code' in symptom_df.columns or len(symptom_df.columns) > 0:
                code_col = 'Code' if 'Code' in symptom_df.columns else symptom_df.columns[0]
                # Clean up BOM and extract codes
                for code in symptom_df[code_col].dropna():
                    code_str = str(code).strip().replace('\ufeff', '')
                    if code_str and code_str not in ['Code', '']:
                        symptom_codes.add(code_str.upper())
        except Exception as e:
            print(f"[WARN] Could not load Symptom Catalog for validation: {e}")
    
    try:
        # Extract the table from the output
        lines = output_text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            if line.strip().startswith('|') and 'Item Class' in line:
                in_table = True
            if in_table:
                if line.strip().startswith('|'):
                    table_lines.append(line)
                elif line.strip() == '' or line.strip().startswith('---'):
                    # End of table or separator
                    if len(table_lines) > 2:  # Has header + separator + data
                        break
        
        if len(table_lines) < 3:
            errors.append("Could not find valid table in output")
            return errors
        
        # Parse the table
        table_text = '\n'.join(table_lines)
        df = pd.read_csv(StringIO(table_text), sep='|', skipinitialspace=True)
        df = df.iloc[:, 1:-1]  # Remove empty first and last columns
        df.columns = df.columns.str.strip()
        
        # Validate required columns exist
        required_cols = ['Item Class', 'Maintainable Item', 'Symptom', 'Failure Mechanism']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return errors
        
        # Remove separator rows and invalid data
        # Filter out rows where Item Class or Maintainable Item is just dashes or empty
        df = df[~df['Item Class'].astype(str).str.strip().str.match(r'^-+$')]
        df = df[~df['Maintainable Item'].astype(str).str.strip().str.match(r'^-+$')]
        df = df[df['Item Class'].astype(str).str.strip() != '']
        df = df[df['Maintainable Item'].astype(str).str.strip() != '']
        
        if len(df) == 0:
            errors.append("No data rows found in table")
            return errors
        
        # Extract Item Class for G9 validation
        item_class = df['Item Class'].iloc[0].strip() if len(df) > 0 else ""
        
        # G8: Check that Maintainable Items do not contain Symptom codes
        # Check both exact matches and symptom-like patterns
        for idx, row in df.iterrows():
            mi = str(row['Maintainable Item']).strip()
            if mi.lower() in ['see above', '']:
                continue
            
            # Extract the first part (code) from the Maintainable Item
            # Symptom codes are typically 2-4 letter acronyms before a dash (e.g., "VIB - Vibration", "AI - Abnormal")
            mi_code = mi.split()[0].upper() if ' ' in mi else mi.upper()
            # Remove trailing punctuation
            mi_code = mi_code.rstrip(':-,.')
            
            # Check if this code matches any known symptom code
            if symptom_codes and mi_code in symptom_codes:
                errors.append(
                    f"G8 VIOLATION: Row {idx+1}: Maintainable Item '{mi}' uses Symptom code '{mi_code}'. "
                    f"Maintainable Items must be equipment/components (e.g., 'Bearing Failure', 'Rotor Failure'), "
                    f"not symptom codes from the Symptom Catalog."
                )
            # Also check for symptom-like pattern: 2-4 uppercase letters followed by " - " and description
            # This catches typos or incorrect symptom codes like "PTO - Power..." (PTO is a typo for PTF)
            elif re.match(r'^[A-Z]{2,4}\s*-\s+', mi):
                errors.append(
                    f"G8 VIOLATION: Row {idx+1}: Maintainable Item '{mi}' uses a symptom-like code pattern. "
                    f"Maintainable Items must be equipment/components (e.g., 'Bearing Failure', 'Rotor Failure'), "
                    f"not symptom-style codes like '{mi_code} - ...'."
                )
        
        # G0a: Check minimum Maintainable Item count based on equipment complexity
        if item_class:
            complexity = determine_equipment_complexity(item_class)
            min_mi_count = 12 if complexity == "COMPLEX" else 5
            
            # Count unique Maintainable Items (excluding 'see above' and empty)
            unique_mis = set()
            for mi in df['Maintainable Item']:
                mi_clean = str(mi).strip()
                if mi_clean and mi_clean.lower() not in ['see above', '']:
                    unique_mis.add(mi_clean)
            
            actual_mi_count = len(unique_mis)
            
            if actual_mi_count < min_mi_count:
                errors.append(
                    f"G0a VIOLATION: Equipment classified as {complexity} requires minimum {min_mi_count} Maintainable Items. "
                    f"Found only {actual_mi_count} Maintainable Items. "
                    f"Add more Maintainable Items from boundaries, catalog, manual, or ISO 14224-compliant suggestions. "
                    f"Use the engineering questions in the code to identify correct additional Maintainable Items."
                )
        
        # G1: Check symptoms per Maintainable Item (4-8)
        symptom_counts = df.groupby('Maintainable Item')['Symptom'].nunique()
        for mi, count in symptom_counts.items():
            mi_clean = str(mi).strip()
            if mi_clean.lower() in ['see above', '']:
                continue
            if count < 4:
                errors.append(f"G1 VIOLATION: '{mi_clean}' has only {count} symptom(s), need 4-8")
            elif count > 8:
                errors.append(f"G1 VIOLATION: '{mi_clean}' has {count} symptoms, need 4-8")
        
        # G2: Check mechanisms per (MI, Symptom) pair (2-5)
        mechanism_counts = df.groupby(['Maintainable Item', 'Symptom'])['Failure Mechanism'].nunique()
        single_mechanism_count = 0
        total_pairs = 0
        
        for (mi, sym), count in mechanism_counts.items():
            mi_clean = str(mi).strip()
            sym_clean = str(sym).strip()
            if mi_clean.lower() in ['see above', ''] or sym_clean.lower() in ['see above', '']:
                continue
            
            total_pairs += 1
            if count == 1:
                single_mechanism_count += 1
            
            if count < 2:
                errors.append(f"G2 VIOLATION: '{mi_clean}' + '{sym_clean}' has only {count} mechanism(s), need 2-5")
            elif count > 5:
                errors.append(f"G2 VIOLATION: '{mi_clean}' + '{sym_clean}' has {count} mechanisms, need 2-5")
        
        # G2b: Check if too many pairs have only 1 mechanism (quality check)
        # This is a heuristic: if more than MAX_SINGLE_MECHANISM_RATIO of pairs have only 1 mechanism, 
        # it likely means the AI is not generating enough mechanisms
        if total_pairs > 0:
            single_ratio = single_mechanism_count / total_pairs
            if single_ratio > MAX_SINGLE_MECHANISM_RATIO:
                errors.append(
                    f"G2 QUALITY WARNING: {single_mechanism_count}/{total_pairs} ({int(single_ratio * 100)}%) of (MI, Symptom) pairs have only 1 mechanism. "
                    f"For complex/critical items, most symptoms should have 2-5 mechanisms representing different physical causes. "
                    f"Review each symptom and expand with additional plausible failure mechanisms from ISO 14224 Table B.2."
                )

        
        # G7: Check for duplication between Symptom and Failure Mechanism
        # Minimum term length to check for duplication (avoids false positives on short terms)
        MIN_TERM_LENGTH = 5
        
        for idx, row in df.iterrows():
            symptom = str(row['Symptom']).strip()
            mechanism = str(row['Failure Mechanism']).strip()
            mi = str(row['Maintainable Item']).strip()
            
            if symptom.lower() in ['see above', ''] or mechanism.lower() in ['see above', '']:
                continue
            
            # Extract key terms to check for duplication
            symptom_code = symptom.split()[0] if ' ' in symptom else symptom
            mechanism_code = mechanism.split()[0] if ' ' in mechanism else mechanism
            
            # Check exact match or same code
            if symptom == mechanism:
                errors.append(f"G7 VIOLATION: Row {idx+1} (MI: '{mi}'): Symptom and Mechanism are identical: '{symptom}'")
            elif symptom_code == mechanism_code and len(symptom_code) > 1:
                errors.append(f"G7 VIOLATION: Row {idx+1} (MI: '{mi}'): Symptom '{symptom}' and Mechanism '{mechanism}' use same code")
            
            # Check for key term duplication (e.g., "Cavitation" in both)
            symptom_lower = symptom.lower()
            mechanism_lower = mechanism.lower()
            
            # Extract main term after the code
            symptom_term = symptom.split('-')[-1].strip().lower() if '-' in symptom else symptom_lower
            mechanism_term = mechanism_lower
            
            # Check if main symptom term appears in mechanism (avoid false positives on short terms)
            if len(symptom_term) > MIN_TERM_LENGTH and symptom_term in mechanism_term:
                errors.append(f"G7 VIOLATION: Row {idx+1} (MI: '{mi}'): Term '{symptom_term}' appears in both Symptom '{symptom}' and Mechanism '{mechanism}'")
        
        # G9: Check minimum Maintainable Item count based on equipment complexity
        unique_mis = df['Maintainable Item'].nunique()
        
        # Determine equipment complexity based on Item Class
        is_complex = _is_complex_equipment(item_class)
        min_mi_count = 12 if is_complex else 5
        equipment_type = "COMPLEX" if is_complex else "SIMPLE"
        
        if unique_mis < min_mi_count:
            errors.append(
                f"G9 VIOLATION: Item Class '{item_class}' is classified as {equipment_type} equipment. "
                f"Found only {unique_mis} distinct Maintainable Item(s), but need at least {min_mi_count}. "
                f"Add more relevant maintainable items using EMS boundaries, Maintainable Item Catalog, Manual, and ISO 14224."
            )
    
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors


def _is_complex_equipment(item_class: str) -> bool:
    """
    Determine if an Item Class represents complex equipment based on its name.
    
    Complex equipment includes:
    - Rotating machinery: motors, generators, turbines
    - Pumps: centrifugal, reciprocating, screw pumps
    - Compressors: centrifugal, reciprocating, screw compressors
    - Separation equipment: separators, cyclones
    - Heat exchangers: shell-and-tube, plate, air-cooled
    
    Simple equipment includes:
    - Instrumentation: transmitters, sensors, indicators, analyzers
    - Simple valves: manual, check, relief valves
    - Lighting: lamps, fixtures
    - Simple mechanical: couplings, filters, strainers
    
    Returns True for complex equipment, False for simple equipment.
    """
    item_class_lower = item_class.lower()
    
    # Complex equipment keywords
    complex_keywords = [
        # Rotating machinery
        'motor', 'generator', 'turbine',
        # Pumps
        'pump', 'centrifugal', 'reciprocating',
        # Compressors
        'compressor', 'screw',
        # Separation
        'separator', 'cyclone',
        # Heat exchangers
        'heat exchanger', 'exchanger', 'cooler', 'condenser',
        # Other complex equipment
        'engine', 'drive', 'gearbox', 'blower', 'fan (large)'
    ]
    
    # Simple equipment keywords (more specific to avoid false positives)
    simple_keywords = [
        'transmitter', 'sensor', 'indicator', 'analyzer', 'instrument',
        'valve, manual', 'valve, check', 'valve, relief', 'simple valve',
        'lamp', 'light', 'fixture',
        'coupling (simple)', 'filter (simple)', 'strainer'
    ]
    
    # Check for simple equipment first (more specific)
    for keyword in simple_keywords:
        if keyword in item_class_lower:
            return False
    
    # Check for complex equipment
    for keyword in complex_keywords:
        if keyword in item_class_lower:
            return True
    
    # Default to complex equipment if uncertain (safer to require more MIs)
    # Log a warning so users are aware of the fallback
    print(f"[WARN] Could not classify Item Class '{item_class}' - defaulting to COMPLEX equipment (requires 12 MIs minimum)")
    return True


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    max_correction_attempts = int(os.getenv("MAX_CORRECTION_ATTEMPTS", "3"))
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY secret")

    client = OpenAI(api_key=api_key)

    system_prompt = read_required("templates/system_prompt.md", "templates/templates/system_prompt.md")
    spec = read_required("templates/spec_fmea_ems_rev01.md", "templates/templates/spec_fmea_ems_rev01.md")
    schema = read_required("templates/output_schema.md", "templates/templates/output_schema.md")

    instruction_file = pick_instruction_file()
    instruction = instruction_file.read_text(encoding="utf-8", errors="ignore")

    item_class = extract_item_class(instruction)

    # --- Fallback: if instruction didn't specify Item Class, pick first available from EMS ---
    if item_class == "UNKNOWN_ITEM_CLASS":
        ems_csv_fallback = Path("inputs/EMS/EMS.csv")
        if not ems_csv_fallback.exists():
            raise RuntimeError("[ERROR] Instruction missing Item Class and inputs/EMS/EMS.csv not found.")

        try:
            df_ems = pd.read_csv(ems_csv_fallback, sep=None, engine="python")
        except Exception:
            df_ems = pd.read_csv(ems_csv_fallback, sep=";", engine="python", on_bad_lines="skip")

        # normalize headers
        df_ems.columns = [str(c).replace("\ufeff", "").strip() for c in df_ems.columns]

        if "Item Class" not in df_ems.columns:
            raise RuntimeError(
                f"[ERROR] Instruction missing Item Class and EMS.csv missing 'Item Class'. Found: {list(df_ems.columns)}"
            )

        candidates = df_ems["Item Class"].astype(str).str.strip()
        candidates = candidates[candidates != ""]
        if candidates.empty:
            raise RuntimeError("[ERROR] Instruction missing Item Class and EMS has empty 'Item Class' values.")

        item_class = candidates.iloc[0]
        print(f"[WARN] Item Class not found in instruction. Using first EMS Item Class: {item_class}")

    # --- Build mandatory MI list (deterministic) ---
    ems_csv = Path("inputs/EMS/EMS.csv")
    mi_catalog = Path("inputs/Catalogs/Maintainable Item Catalog.csv")

    mandatory_mi: list[str] = []
    if ems_csv.exists() and mi_catalog.exists():
        mandatory_mi = build_mi_list_from_ems_and_catalog(ems_csv, item_class, mi_catalog)

    mandatory_mi_block = "\n".join([f"- {x}" for x in mandatory_mi]) if mandatory_mi else "[EMPTY - CHECK EMS Boundaries / Catalog]"

    # --- Minimal ingestion pack ---
    parts: list[str] = []

    br_txt = Path("inputs/Business_Rules/Business Rules.txt")
    if br_txt.exists():
        parts.append(f"### FILE: {br_txt.as_posix()}\n{read_text_file(br_txt, max_chars=120_000)}")

    if ems_csv.exists():
        parts.append(f"### FILE: {ems_csv.as_posix()} (FILTERED)\n{filter_ems_for_item_class(ems_csv, item_class, max_rows=400)}")

    mi = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
    if mi.exists():
        parts.append(f"### FILE: {mi.as_posix()} (PREVIEW)\n{load_csv_preview(mi, max_rows=600)}")

    sym = Path("inputs/Catalogs/Symptom Catalog.csv")
    if sym.exists():
        parts.append(f"### FILE: {sym.as_posix()} (PREVIEW)\n{load_csv_preview(sym, max_rows=600)}")

    manual_txt = pick_manual_text(item_class)
    if manual_txt:
        parts.append(f"### FILE: {manual_txt.as_posix()} (TRUNCATED)\n{read_text_file(manual_txt, max_chars=120_000)}")

    minimal_inputs = "\n\n".join(parts)
    
    # Build item-class-specific guidance
    item_class_guidance = build_item_class_specific_guidance(item_class)

    user_prompt = f"""
## INSTRUCTION (from {instruction_file.as_posix()})
{instruction}

## TARGET ITEM CLASS (parsed)
{item_class}

## SPECIFICATION (MANDATORY)
{spec}

## OUTPUT SCHEMA (MANDATORY)
{schema}

## INPUT DOCUMENTS (MINIMAL PACK)
{minimal_inputs}
{item_class_guidance}

## MANDATORY MAINTAINABLE ITEM LIST (BASE FROM EMS BOUNDARIES)
The list below contains Maintainable Items derived from EMS Boundaries column, excluding items marked as "Exclude", "optional", or "if applicable".

**IMPORTANT NOTE**: This base list has been filtered using basic exclusion rules, but you MUST apply additional engineering intelligence:
- Some boundary items may be redundant or covered by other maintainable items
- Some boundary items may not be independently maintainable
- You should filter further based on maintainability criteria (see MAINTAINABLE ITEM RULES in spec)
- You should also ADD maintainable items from ISO 14224 standards that are not in boundaries

**CRITICAL REQUIREMENTS:**
1. You MUST build the FMEA for EVERY relevant Maintainable Item - not just those listed below
2. APPLY ENGINEERING JUDGMENT to filter the base list (remove items that are sub-components or not independently maintainable)
3. PROACTIVELY ADD maintainable items from ISO 14224 Table B.15 that are relevant but not in boundaries (mark with "(*)") 
4. Review the Equipment Manual and EMS Boundaries to identify ANY additional Maintainable Items of technical relevance
5. Do NOT limit yourself to only the "main" or "most probable" items - include ALL technically relevant items
6. Mark any additional Maintainable Items you suggest (beyond the base list or from ISO 14224) with "(*)" to indicate they are inferred

**Base Maintainable Items from EMS Boundaries (filtered for explicit exclusions only):**
{mandatory_mi_block}

**Additional Maintainable Items - YOUR RESPONSIBILITY:**
- **APPLY ENGINEERING INTELLIGENCE**: Not all items mentioned in boundaries should become Maintainable Items
  * **PRIMARY CRITERION (MOST IMPORTANT)**: Ask first "Could this component's failure cause complete system failure?"
    - If NO → Exclude from Maintainable Items (likely sub-component or non-critical)
    - If YES → Continue with additional evaluation tests below
  * **Use decision framework IN ORDER**: 
    1. Primary: Critical system failure test (most important)
    2. Independence test
    3. Symptom distinctiveness test
    4. Maintenance action test
  * **Filter hierarchically**: Exclude sub-components covered by parent items (use parent-child relationship analysis)
  * **Only include components** that pass the primary criterion AND are independently maintainable AND have distinct failure symptoms
  * **Generic principle**: If component A's maintenance/symptoms are fully covered by component B's FMEA, exclude component A
- **CONSULT ISO 14224 Table B.15**: Proactively suggest standard maintainable items for this Item Class type
  * **Evaluate generic system categories**: Power transmission, lubrication, cooling, sealing, bearing, monitoring/control, power supply, structural, fluid handling
  * **Select based on**: Item Class functional requirements, operating principles, and failure risk profile
  * Verify technical relevance to the specific Item Class
  * Mark ALL ISO 14224-suggested items with "(*)"
- Review the Equipment Manual for components/systems that could cause functional failure
- Consider: Power transmission, control systems, monitoring systems, structural components, sealing systems, cooling systems, auxiliary systems, etc.
- Each suggested item should be technically justified and relevant to the Item Class
- Transform all names to match Maintainable Item Catalog terminology
- **OUTPUT VALIDATION SECTION**: At the end of the FMEA, include a "SUGGESTED ADDITIONAL MAINTAINABLE ITEMS" table with justification for each (*)-marked item

## CRITICAL REMINDERS BEFORE YOU START:

**NO PLACEHOLDERS OR TRUNCATION ALLOWED:**
- ❌ NEVER write "(Additional rows...)", "[The rest of the table...]", "[See above]", "[unchanged]", or "..."
- ❌ NEVER use phrases like "omitted for brevity", "similar to above", "follows the same pattern"
- ✅ Every single row for every Maintainable Item MUST be explicitly written in the output table
- ✅ If you have 13 Maintainable Items with 5 symptoms each × 2 mechanisms = 130+ rows minimum - write them ALL

**NO SYMPTOM CODES IN MAINTAINABLE ITEM COLUMN:**
- ❌ NEVER use Symptom codes as Maintainable Items
- ❌ BAD: "PTF - Power/signal transmission failure" (this is a SYMPTOM, not equipment)
- ❌ BAD: "VIB - Vibration" (this is a SYMPTOM, not equipment)
- ❌ BAD: "NOI - Noise" (this is a SYMPTOM, not equipment)
- ❌ BAD: "PTO - Power..." (typo/incorrect code - still looks like a symptom)
- ✅ GOOD: "Bearing Failure" (this is physical equipment)
- ✅ GOOD: "Rotor Failure" (this is physical equipment)
- ✅ GOOD: "Windings Failure" (this is physical equipment)
- Maintainable Items are PHYSICAL COMPONENTS/EQUIPMENT from the Maintainable Item Catalog
- Symptoms are OBSERVABLE CONDITIONS from the Symptom Catalog

**CARDINALITY REQUIREMENTS** - Your output WILL BE AUTOMATICALLY VALIDATED:
1. Each Maintainable Item MUST have EXACTLY 4-8 DISTINCT Symptoms (NO EXCEPTIONS)
   - Count symptoms per MI before finalizing
   - Add more symptoms if < 4
   - Consolidate if > 8
   
2. Each (Maintainable Item, Symptom) pair MUST have MULTIPLE (2-5) DISTINCT Failure Mechanisms
   - **CRITICAL**: DO NOT generate only 1 mechanism per symptom for all items
   - Complex/critical items with common symptoms should have 2-5 mechanisms
   - Example: "Shaft Failure" + "VIB - Vibration" → 3-4 mechanisms (Fatigue, Misalignment, Unbalance, Wear)
   - Example: "Bearing Failure" + "VIB - Vibration" → 2-3 mechanisms (Wear, Misalignment, Fatigue)
   - Only very simple items or rare symptoms may have just 1 mechanism
   - Plan mechanisms for each symptom based on:
     * Technical complexity of the Maintainable Item
     * Criticality of the equipment
     * Number of plausible physical causes for that symptom
   
3. NO DUPLICATION: Symptom and Failure Mechanism on same row MUST be DIFFERENT terms
   - BAD: Symptom "2.1 Cavitation" + Mechanism "2.1 Cavitation" ← FORBIDDEN
   - BAD: Symptom "VIB - Vibration" + Mechanism "1.2 Vibration" ← FORBIDDEN
   - GOOD: Symptom "VIB - Vibration" + Mechanism "2.6 Fatigue" ← CORRECT
   - GOOD: Symptom "NOI - Noise" + Mechanism "2.1 Cavitation" ← CORRECT
   - Check EVERY row before finalizing

**THE OUTPUT WILL BE REJECTED IF ANY OF THESE RULES ARE VIOLATED**

Return ONLY the final deliverables requested in the instruction.
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt + "\n\n### SPEC (MANDATORY)\n" + spec},
            {"role": "user", "content": user_prompt},
        ],
    )

    usage = getattr(resp, "usage", None)
    in_tokens = getattr(usage, "prompt_tokens", None) if usage else None
    out_tokens = getattr(usage, "completion_tokens", None) if usage else None

    print(f"Token usage -> input: {in_tokens}, output: {out_tokens}")

    if in_tokens is not None and out_tokens is not None:
        cost = (in_tokens / 1_000_000) * 0.80 + (out_tokens / 1_000_000) * 3.20
        print(f"Estimated cost (gpt-4.1-mini Standard): ${cost:.4f}")

    # --- Quality gate: ensure ALL mandatory MIs appear in output ---
    if not resp.choices:
        raise RuntimeError("OpenAI API returned no response choices")
    output_text = resp.choices[0].message.content or ""
    
    # Initialize conversation history for potential corrections
    conversation_history = [
        {"role": "system", "content": system_prompt + "\n\n### SPEC (MANDATORY)\n" + spec},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": output_text}
    ]
    
    # Check for missing mandatory MIs - now informational since AI can filter intelligently
    missing: list[str] = []
    for mi_name in mandatory_mi:
        if mi_name and (mi_name.lower() not in output_text.lower()):
            missing.append(mi_name)

    if mandatory_mi and missing:
        print(f"\n[INFO] Model output has {len(missing)} items from base list that were filtered out:")
        for mi in missing[:10]:  # Show up to 10 examples
            print(f"  - {mi}")
        print("\n[INFO] This is acceptable if AI applied engineering judgment to filter non-maintainable or redundant items.")
        print("[INFO] The AI should have provided justification in the output for significant omissions.")

    # --- Quality gate: validate cardinality rules with automatic correction ---
    print("\n[VALIDATION] Checking cardinality and duplication rules...")
    validation_errors = validate_output_cardinality(output_text, item_class)
    
    cardinality_correction_attempt = 0
    while validation_errors and cardinality_correction_attempt < max_correction_attempts:
        cardinality_correction_attempt += 1
        print(f"\n[VALIDATION] ⚠️  Found {len(validation_errors)} validation error(s) (Attempt {cardinality_correction_attempt}/{max_correction_attempts}):")
        for err in validation_errors:
            print(f"  - {err}")
        
        print(f"\n[CORRECTION] Requesting AI to fix validation errors...")
        
        # Build correction prompt with specific errors
        correction_prompt = build_correction_prompt(validation_errors)
        conversation_history.append({"role": "user", "content": correction_prompt})
        
        # Request correction from AI
        correction_resp = client.chat.completions.create(
            model=model,
            messages=conversation_history,
        )
        
        usage = getattr(correction_resp, "usage", None)
        in_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        out_tokens = getattr(usage, "completion_tokens", None) if usage else None
        
        print(f"Token usage (correction) -> input: {in_tokens}, output: {out_tokens}")
        
        if in_tokens is not None and out_tokens is not None:
            cost = (in_tokens / 1_000_000) * 0.80 + (out_tokens / 1_000_000) * 3.20
            print(f"Estimated cost (gpt-4.1-mini Standard): ${cost:.4f}")
        
        if not correction_resp.choices:
            print("[ERROR] AI correction failed - no response received")
            break
        
        output_text = correction_resp.choices[0].message.content or ""
        conversation_history.append({"role": "assistant", "content": output_text})
        
        # Validate the corrected output
        validation_errors = validate_output_cardinality(output_text, item_class)
    
    if validation_errors:
        print(f"\n[VALIDATION] ❌ Output still has {len(validation_errors)} validation error(s) after {cardinality_correction_attempt} correction attempt(s):")
        for err in validation_errors:
            print(f"  - {err}")
        print("\n[WARNING] Saving output with validation errors. Please review manually.")
    else:
        print("[VALIDATION] ✓ All quality gates passed")

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Convert Markdown table to CSV format
    print("\n[OUTPUT] Converting Markdown table to CSV format...")
    csv_output = convert_markdown_table_to_csv(output_text)
    
    output_name = "EMS upgrade output.csv"
    (out_dir / output_name).write_text(csv_output, encoding="utf-8")

    print(f"OK: Generated outputs/{output_name}")


if __name__ == "__main__":
    main()

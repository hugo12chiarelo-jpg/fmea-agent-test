import os
import re
from io import StringIO
from pathlib import Path

import pandas as pd
from openai import OpenAI

TEXT_EXT = {".md", ".txt", ".csv", ".json"}

# Validation threshold: Flag if more than this ratio of (MI, Symptom) pairs have only 1 mechanism
MAX_SINGLE_MECHANISM_RATIO = 0.70


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

    no_ext = instr_dir / "Daily Instructions"
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


def filter_ems_for_item_class(ems_path: Path, item_class: str, max_rows: int = 200) -> str:
    try:
        df = pd.read_csv(ems_path, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(ems_path, sep=";", engine="python", on_bad_lines="skip")

    # Normalize headers
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]

    col = "Item Class" if "Item Class" in df.columns else None
    if col is None:
        return (
            "EMS.csv (unfiltered preview — Item Class column not found)\n"
            + load_csv_preview(ems_path, max_rows=max_rows)
        )

    dff = df[df[col].astype(str).str.strip().str.lower() == item_class.strip().lower()]

    if dff.empty:
        return (
            f"EMS.csv (no rows matched Item Class='{item_class}' in column '{col}')\n"
            + load_csv_preview(ems_path, max_rows=max_rows)
        )

    if len(dff) > max_rows:
        dff = dff.head(max_rows)
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}', truncated to first {max_rows} rows]\n"
    else:
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}']\n"

    return dff.to_csv(index=False) + note


def build_mi_list_from_ems_and_catalog(ems_path: Path, item_class: str, mi_catalog_path: Path) -> list[str]:
    """
    Build a comprehensive list of Maintainable Items from EMS boundaries and MI catalog.
    
    This function:
    1. Parses the EMS Boundaries column to identify included/excluded items
    2. Filters out items marked with "Exclude", "optional", "if applicable"
    3. Maps boundary terms to standard Maintainable Item Catalog terminology
    4. Returns ALL technically relevant items from boundaries
    
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

    rows = ems[ems["Item Class"].astype(str).str.strip().str.lower() == item_class.strip().lower()]
    if rows.empty:
        sample = ems["Item Class"].astype(str).str.strip().dropna().unique()[:10].tolist()
        raise RuntimeError(
            f"No EMS rows matched Item Class='{item_class}'. Sample EMS Item Class values: {sample}"
        )

    boundary_text = "\n".join(rows[boundary_col].astype(str).tolist())

    # Read MI catalog
    try:
        mi_df = pd.read_csv(mi_catalog_path, sep=None, engine="python")
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

    catalog_items = sorted(set(mi_df[name_col].astype(str).str.strip().tolist()))
    
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
                    after_words = [w for w in after_match.split() if len(w) > 2 and w not in {'and', 'the', 'or', 'with'}]
                    if after_words:
                        # This is a more specific item (e.g., "anti surge valve"), don't exclude the general item
                        is_match = False
            
            # Method 2: Check if any word in line starts with catalog item (for stems) - WORD STEM MATCH
            # Only use this if no exact match was found
            if not is_match:
                # e.g., "instrument" matches "instrumentation"
                words = re.split(r'[\s,/\-()]+', line_lower)
                for word in words:
                    if word.startswith(mi_lower) or mi_lower.startswith(word):
                        # Only match if similarity is high enough
                        shorter = min(len(word), len(mi_lower))
                        if shorter >= 5:  # Increased minimum to 5 chars to avoid false positives
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
    
    return final_included


def pick_manual_text(item_class: str) -> Path | None:
    manual_dir = Path("inputs/Manual")
    if not manual_dir.exists():
        return None

    txts = sorted([p for p in manual_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
    if not txts:
        return None

    return txts[0]


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
   
2. Each (Maintainable Item, Symptom) pair MUST have MULTIPLE (1-5) DISTINCT Failure Mechanisms
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


def validate_output_cardinality(output_text: str) -> list[str]:
    """
    Validate that the output meets cardinality requirements:
    - Each Maintainable Item has 4-8 distinct Symptoms
    - Each (MI, Symptom) pair has 1-5 distinct Failure Mechanisms
    - No duplication between Symptom and Failure Mechanism on the same row
    
    Returns a list of error messages (empty if valid).
    """
    errors = []
    
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
        
        # G2: Check mechanisms per (MI, Symptom) pair (1-5)
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
            
            if count > 5:
                errors.append(f"G2 VIOLATION: '{mi_clean}' + '{sym_clean}' has {count} mechanisms, need 1-5")
        
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
    
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors


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

## MANDATORY MAINTAINABLE ITEM LIST (BASE FROM EMS BOUNDARIES)
The list below contains Maintainable Items derived from EMS Boundaries column, excluding items marked as "Exclude", "optional", or "if applicable".

**CRITICAL REQUIREMENTS:**
1. You MUST build the FMEA for EVERY Maintainable Item listed below - this is the MINIMUM required set
2. You MUST also review the Equipment Manual (if provided) and EMS Boundaries to identify ANY additional Maintainable Items of technical relevance
3. Do NOT limit yourself to only the "main" or "most probable" items - include ALL technically relevant items
4. If any base item from the list below is missing from the output, the deliverable is INVALID
5. Mark any additional Maintainable Items you suggest (beyond the base list) with "(*)" to indicate they are inferred

**Base Maintainable Items from EMS Boundaries (filtered for exclusions):**
{mandatory_mi_block}

**Additional Maintainable Items - YOUR RESPONSIBILITY:**
- Review the Equipment Manual for components/systems that could cause functional failure
- Consider: Power transmission, control systems, monitoring systems, structural components, sealing systems, cooling systems, auxiliary systems, etc.
- Each suggested item should be technically justified and relevant to the Item Class
- Transform all names to match Maintainable Item Catalog terminology

## CRITICAL REMINDERS BEFORE YOU START:
**CARDINALITY REQUIREMENTS** - Your output WILL BE AUTOMATICALLY VALIDATED:
1. Each Maintainable Item MUST have EXACTLY 4-8 DISTINCT Symptoms (NO EXCEPTIONS)
   - Count symptoms per MI before finalizing
   - Add more symptoms if < 4
   - Consolidate if > 8
   
2. Each (Maintainable Item, Symptom) pair MUST have MULTIPLE (1-5) DISTINCT Failure Mechanisms
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
    missing: list[str] = []
    for mi_name in mandatory_mi:
        if mi_name and (mi_name.lower() not in output_text.lower()):
            missing.append(mi_name)

    if mandatory_mi and missing:
        raise RuntimeError(
            f"Model output missing {len(missing)} mandatory Maintainable Items. Examples: {missing[:10]}"
        )

    # --- Quality gate: validate cardinality rules with automatic correction ---
    print("\n[VALIDATION] Checking cardinality and duplication rules...")
    validation_errors = validate_output_cardinality(output_text)
    
    # Initialize conversation history once for reuse
    if validation_errors:
        conversation_history = [
            {"role": "system", "content": system_prompt + "\n\n### SPEC (MANDATORY)\n" + spec},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": output_text}
        ]
    
    correction_attempt = 0
    while validation_errors and correction_attempt < max_correction_attempts:
        correction_attempt += 1
        print(f"\n[VALIDATION] ⚠️  Found {len(validation_errors)} validation error(s) (Attempt {correction_attempt}/{max_correction_attempts}):")
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
        validation_errors = validate_output_cardinality(output_text)
    
    if validation_errors:
        print(f"\n[VALIDATION] ❌ Output still has {len(validation_errors)} validation error(s) after {correction_attempt} correction attempt(s):")
        for err in validation_errors:
            print(f"  - {err}")
        print("\n[WARNING] Saving output with validation errors. Please review manually.")
    else:
        print("[VALIDATION] ✓ All quality gates passed")

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    output_name = "EMS upgrade output.md"
    (out_dir / output_name).write_text(output_text, encoding="utf-8")

    print(f"OK: Generated outputs/{output_name}")


if __name__ == "__main__":
    main()

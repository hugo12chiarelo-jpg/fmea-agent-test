import os
import re
from pathlib import Path

import pandas as pd
from openai import OpenAI

TEXT_EXT = {".md", ".txt", ".csv", ".json"}

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
        f for f in instr_dir.iterdir()
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
    Tries to extract Item Class from instruction text.
    Expected patterns:
      - "Item Class: XYZ"
      - "for Item Class: XYZ"
      - "Build ... for Item Class: XYZ"
    """
    patterns = [
        r"Item Class\s*:\s*(.+)",
        r"for Item Class\s*:\s*(.+)",
    ]
    for pat in patterns:
        m = re.search(pat, instruction_text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip().strip(".")
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

    # Limit cols for prompt compactness
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

    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    
    col = "Item Class" if "Item Class" in df.columns else None

    if col is None:
        return "EMS.csv (unfiltered preview — Item Class column not found)\n" + load_csv_preview(ems_path, max_rows=max_rows)

    dff = df[df[col].astype(str).str.strip().str.lower() == item_class.strip().lower()]

    if dff.empty:
        return f"EMS.csv (no rows matched Item Class='{item_class}' in column '{col}')\n" + load_csv_preview(ems_path, max_rows=max_rows)

    if len(dff) > max_rows:
        dff = dff.head(max_rows)
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}', truncated to first {max_rows} rows]\n"
    else:
        note = f"\n\n[NOTE: filtered to Item Class='{item_class}']\n"

    return dff.to_csv(index=False) + note

def build_mi_list_from_ems_and_catalog(ems_path: Path, item_class: str, mi_catalog_path: Path) -> list[str]:
    # Read EMS
    try:
        ems = pd.read_csv(ems_path, sep=None, engine="python")
    except Exception:
        ems = pd.read_csv(ems_path, sep=";", engine="python", on_bad_lines="skip")

    # Normalize headers (remove BOM + trim spaces)
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
        raise RuntimeError(f"EMS.csv must contain a 'Boundaries' column (or 'Boundary'). Found: {list(ems.columns)}")

    rows = ems[ems["Item Class"].astype(str).str.strip().str.lower() == item_class.strip().lower()]
    if rows.empty:
        raise RuntimeError(f"No EMS rows matched Item Class='{item_class}'")

    boundary_text = "\n".join(rows[boundary_col].astype(str).tolist())

    # Read MI catalog
    try:
        mi_df = pd.read_csv(mi_catalog_path, sep=None, engine="python")
    except Exception:
        mi_df = pd.read_csv(mi_catalog_path, sep=";", engine="python", on_bad_lines="skip")

    # Normalize headers
    mi_df.columns = [str(c).replace("\ufeff", "").strip() for c in mi_df.columns]

    # Identify MI name column in catalog
    name_col = None
    for c in mi_df.columns:
        if str(c).strip().lower() in {"maintainable item", "maintainable_item", "name", "item"}:
            name_col = c
            break
    if name_col is None:
        name_col = mi_df.columns[0]

    catalog_items = sorted(set(mi_df[name_col].astype(str).str.strip().tolist()))

    # Match catalog items mentioned in boundary text (simple containment)
    bt = boundary_text.lower()
    included = [mi for mi in catalog_items if mi and mi.lower() in bt]

    return included

def pick_manual_text(item_class: str) -> Path | None:
    """
    Prefer the .txt manual (not pdf). If you maintain one txt per item class,
    this picks the first .txt in inputs/Manual.
    """
    manual_dir = Path("inputs/Manual")
    if not manual_dir.exists():
        return None

    # heuristic: any .txt first
    txts = sorted([p for p in manual_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
    if not txts:
        return None

    # If you later name manuals per item class, we can match by item_class substring.
    # For now: pick first .txt (you already have COCE ... Manual.txt)
    return txts[0]

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY secret")

    client = OpenAI(api_key=api_key)

    system_prompt = read_required("templates/system_prompt.md", "templates/templates/system_prompt.md")
    spec = read_required("templates/spec_fmea_ems_rev01.md", "templates/templates/spec_fmea_ems_rev01.md")
    schema = read_required("templates/output_schema.md", "templates/templates/output_schema.md")

    instruction_file = pick_instruction_file()
    instruction = instruction_file.read_text(encoding="utf-8", errors="ignore")

    item_class = extract_item_class(instruction)

    # --- Build mandatory MI list (deterministic) ---
    ems_csv = Path("inputs/EMS/EMS.csv")
    mi_catalog = Path("inputs/Catalogs/Maintainable Item Catalog.csv")

    mandatory_mi = []
    if ems_csv.exists() and mi_catalog.exists():
        mandatory_mi = build_mi_list_from_ems_and_catalog(ems_csv, item_class, mi_catalog)

    mandatory_mi_block = "\n".join([f"- {x}" for x in mandatory_mi]) if mandatory_mi else "[EMPTY - CHECK EMS Boundaries / Catalog]"
    
    # --- Minimal ingestion pack ---
    parts = []

    # Business Rules: prefer the .txt you already created (smaller than docx)
    br_txt = Path("inputs/Business_Rules/Business Rules.txt")
    if br_txt.exists():
        parts.append(f"### FILE: {br_txt.as_posix()}\n{read_text_file(br_txt, max_chars=120_000)}")

    # EMS: filtered to target Item Class
    ems_csv = Path("inputs/EMS/EMS.csv")
    if ems_csv.exists():
        parts.append(f"### FILE: {ems_csv.as_posix()} (FILTERED)\n{filter_ems_for_item_class(ems_csv, item_class, max_rows=400)}")

    # Catalogs: keep, but limit rows
    mi = Path("inputs/Catalogs/Maintainable Item Catalog.csv")
    if mi.exists():
        parts.append(f"### FILE: {mi.as_posix()} (PREVIEW)\n{load_csv_preview(mi, max_rows=600)}")

    sym = Path("inputs/Catalogs/Symptom Catalog.csv")
    if sym.exists():
        parts.append(f"### FILE: {sym.as_posix()} (PREVIEW)\n{load_csv_preview(sym, max_rows=600)}")

    # Manual: prefer .txt, limit chars
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

## MANDATORY MAINTAINABLE ITEM LIST (MUST USE ALL)
You MUST build the FMEA for EVERY Maintainable Item listed below.
Do NOT summarize. Do NOT pick only the “most probable”.
If any item is missing from the output, the deliverable is invalid.

{mandatory_mi_block}

Return ONLY the final deliverables requested in the instruction.
"""

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt + "\n\n### SPEC (MANDATORY)\n" + spec},
            {"role": "user", "content": user_prompt},
        ],
    )
    usage = getattr(resp, "usage", None)

    in_tokens = getattr(usage, "input_tokens", None) if usage else None
    out_tokens = getattr(usage, "output_tokens", None) if usage else None

    print(f"Token usage -> input: {in_tokens}, output: {out_tokens}")

    # Estimativa de custo para gpt-4.1-mini (Standard)
    if in_tokens is not None and out_tokens is not None:
        cost = (in_tokens / 1_000_000) * 0.80 + (out_tokens / 1_000_000) * 3.20
        print(f"Estimated cost (gpt-4.1-mini Standard): ${cost:.4f}")
        
     # --- Quality gate: ensure ALL mandatory MIs appear in output ---
    output_text = resp.output_text or ""
    missing = []
    for mi_name in mandatory_mi:
        if mi_name and (mi_name.lower() not in output_text.lower()):
            missing.append(mi_name)

    if mandatory_mi and missing:
        raise RuntimeError(
            f"Model output missing {len(missing)} mandatory Maintainable Items. Examples: {missing[:10]}"
        )

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    output_name = "EMS upgrade output.md"
    (out_dir / output_name).write_text(output_text, encoding="utf-8")

    print(f"OK: Generated outputs/{output_name}")


if __name__ == "__main__":
    main()


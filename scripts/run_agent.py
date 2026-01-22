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
    df = pd.read_csv(path)
    # Limit cols for prompt compactness
    df = df.iloc[:, :max_cols]
    if len(df) > max_rows:
        df = df.head(max_rows)
        note = f"\n\n[NOTE: truncated to first {max_rows} rows]\n"
    else:
        note = ""
    return df.to_csv(index=False) + note

def filter_ems_for_item_class(ems_path: Path, item_class: str, max_rows: int = 200) -> str:
    df = pd.read_csv(ems_path)

    # Attempt common column names; adjust if your EMS.csv uses different names
    col = "Item Class" if "Item Class" in df.columns else None

    if col is None:
        # fallback: send a small preview only, since we can't filter
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

Return ONLY the final deliverables requested in the instruction.
"""

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fmea_output.md").write_text(resp.output_text, encoding="utf-8")
    print("OK: Generated outputs/fmea_output.md")

if __name__ == "__main__":
    main()


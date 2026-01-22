import os
from pathlib import Path
from openai import OpenAI

def read_required(path_a: str, path_b: str) -> str:
    """Read from path_a if it exists, otherwise path_b. Raise if neither exists."""
    p1 = Path(path_a)
    if p1.exists():
        return p1.read_text(encoding="utf-8", errors="ignore")
    p2 = Path(path_b)
    if p2.exists():
        return p2.read_text(encoding="utf-8", errors="ignore")
    raise FileNotFoundError(f"Missing both: {path_a} and {path_b}")

# Text-friendly formats ingested in v1
TEXT_EXT = {".md", ".txt", ".csv", ".json"}

def read_text_tree(root: str) -> str:
    """Read all text files under a directory and return a single concatenated string."""
    p = Path(root)
    if not p.exists():
        return ""
    chunks = []
    for f in sorted(p.rglob("*")):
        if f.is_file() and f.suffix.lower() in TEXT_EXT:
            content = f.read_text(encoding="utf-8", errors="ignore")
            chunks.append(f"\n\n### FILE: {f.as_posix()}\n{content}")
    return "\n".join(chunks)

def pick_instruction_file() -> Path:
    """
    Pick the instruction file robustly.
    Priority:
      1) inputs/Instructions/instruction.md
      2) any .md/.txt in inputs/Instructions (excluding README.md), newest first
      3) file named 'Daily Instructions' (no extension)
      4) fallback: inputs/Instructions/README.md
    """
    instr_dir = Path("inputs/Instructions")
    if not instr_dir.exists():
        raise FileNotFoundError("Missing folder: inputs/Instructions")

    preferred = instr_dir / "instruction.md"
    if preferred.exists():
        return preferred

    # Any .md/.txt excluding README
    candidates = [
        f for f in instr_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in {".md", ".txt"}
        and f.name.lower() not in {"readme.md", "readme.txt"}
    ]
    if candidates:
        # newest modified first
        candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return candidates[0]

    # Your current pattern: file without extension named "Daily Instructions"
    no_ext = instr_dir / "Daily Instructions"
    if no_ext.exists() and no_ext.is_file():
        return no_ext

    fallback = instr_dir / "README.md"
    if fallback.exists():
        return fallback

    raise FileNotFoundError(
        "No instruction file found. Create one in inputs/Instructions/ "
        "(e.g., instruction.md or a .txt/.md file)."
    )

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY secret")

    client = OpenAI(api_key=api_key)

    # Mandatory templates (these names you DO have)
    system_prompt = read_required("templates/system_prompt.md", "templates/templates/system_prompt.md")
    spec = read_required("templates/spec_fmea_ems_rev01.md", "templates/templates/spec_fmea_ems_rev01.md")
    schema = read_required("templates/output_schema.md", "templates/templates/output_schema.md")


    instruction_file = pick_instruction_file()
    instruction = instruction_file.read_text(encoding="utf-8", errors="ignore")

    # Read all text-ready inputs (Business Rules .txt, EMS.csv, Catalogs .csv, Manual .txt, etc.)
    inputs_text = read_text_tree("inputs")

    user_prompt = f"""
## INSTRUCTION (from {instruction_file.as_posix()})
{instruction}

## SPECIFICATION (MANDATORY)
{spec}

## OUTPUT SCHEMA (MANDATORY)
{schema}

## INPUT DOCUMENTS (TEXT-READY)
{inputs_text}

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


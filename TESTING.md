# Testing FMEA Output Validation

## Current Status

The FMEA agent now includes automatic validation that checks:

1. **G1 - Cardinality (Symptoms)**: Each Maintainable Item must have 4-8 distinct Symptoms
2. **G2 - Cardinality (Mechanisms)**: Each (MI, Symptom) pair must have 1-5 distinct Failure Mechanisms  
3. **G7 - No Duplication**: Symptom and Mechanism on same row must use different terms

## Testing the Current Output

To validate the current output file:

```bash
cd /home/runner/work/fmea-agent/fmea-agent
python3 << 'VALIDATE'
import pandas as pd
from io import StringIO

with open('outputs/EMS upgrade output.md', 'r') as f:
    output = f.read()

# Parse table
lines = output.split('\n')
table_lines = [l for l in lines if l.strip().startswith('|') and 'Item Class' in l or (l.strip().startswith('|') and len(table_lines) > 0)][:50]
table_text = '\n'.join(table_lines)
df = pd.read_csv(StringIO(table_text), sep='|', skipinitialspace=True).iloc[:, 1:-1]
df.columns = df.columns.str.strip()
df = df[df['Item Class'].str.strip() != '---']

# Check G1: Symptoms per MI
print("G1 - Symptoms per Maintainable Item:")
symptom_counts = df.groupby('Maintainable Item')['Symptom'].nunique()
for mi, count in list(symptom_counts.items())[:10]:
    status = "✓" if 4 <= count <= 8 else "✗"
    print(f"  {status} {mi.strip()}: {count} symptoms")

print(f"\nTotal: {len(symptom_counts)} Maintainable Items")
print(f"Passing G1: {sum(4 <= c <= 8 for c in symptom_counts.values())} / {len(symptom_counts)}")
VALIDATE
```

## Expected Results After Fix

When the agent runs with the updated templates, all Maintainable Items should have 4-8 symptoms and no duplication should occur.

Current output: **49 validation errors**
- 28 G1 violations (cardinality)  
- 21 G7 violations (duplication)

Expected after fix: **0 validation errors**

## Running the Agent

To generate new validated output:

```bash
export OPENAI_API_KEY=your_key
python scripts/run_agent.py
```

The agent will:
1. Generate FMEA output following enhanced templates
2. Automatically validate the output
3. Report detailed errors if validation fails
4. Only save output if it passes all validation checks

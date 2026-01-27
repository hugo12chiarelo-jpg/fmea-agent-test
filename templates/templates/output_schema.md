# OUTPUT SCHEMA — EMS UPGRADE FMEA

The agent must ALWAYS produce the final FMEA output strictly following this schema.
No column may be removed, renamed, reordered, or merged.

## OUTPUT FORMAT
- Tabular structure
- One row per:
  Maintainable Item + Symptom + Failure Mechanism
- Plain text (Markdown table or CSV-compatible)

## MANDATORY COLUMNS (IN ORDER)

1. Item Class  
   - Exact value provided by the user.

2. Function  
   - Function of the relative Item Class description.
   - Must be technically descriptive (not generic).

3. Maintainable Item
   - **SOURCE**: Must be derived from the "Boundaries" column in the EMS file.
   - **NAMING**: Name must be transformed to match terminology from "Maintainable Item Catalog.csv".
   - **FORMAT**: Must end with "Failure".
   - **MARKING**: Inferred items which are not explicitly mentioned in EMS Boundaries must be marked with "(*)".
   - **PROCESS**: 
     1. Extract components from EMS Boundaries column for the Item Class
     2. Map each component to its standard name from Maintainable Item Catalog
     3. Ensure all catalog-based names end with "Failure"
  
5. Maintainable Item Function
   - Function of the Maintainable Item relative to the Item Class.
   - Must be technically descriptive (not generic) for that specific Maintainable Item

6. Symptom  
   - ISO 14224 code + description (e.g., "VIB - Vibration").
   - Must follow Symptom Catalog from ISO 14224.
   - Any non-catalog symptom must be marked with "(*)".
   - **CARDINALITY**: Each Maintainable Item MUST have 4-8 DISTINCT Symptoms (NOT 1-to-1)
   - The number of symptoms depends on technical complexity of the Maintainable Item:
     * Complex/Critical Maintainable Items: 6-8 symptoms
     * Moderate complexity: 5-6 symptoms
     * Simpler items: 4-5 symptoms
   - Examples:
     * "Impeller Failure" (complex) → 6-8 different symptoms
     * "Filter Failure" (simpler) → 4-5 different symptoms

7. Failure Mechanism  
   - ISO 14224 Table B.2 mechanism.
   - Must be physically linked to the Maintainable Item and the Symptom.
   - **CRITICAL**: NEVER use the same term/code/concept as the Symptom on the same row
     * BAD: Symptom "2.1 Cavitation" + Mechanism "2.1 Cavitation" ← FORBIDDEN  
     * BAD: Symptom "VIB - Vibration" + Mechanism "1.2 Vibration" ← FORBIDDEN  
     * GOOD: Symptom "VIB - Vibration" + Mechanism "2.6 Fatigue" ← CORRECT  
     * GOOD: Symptom "NOI - Noise" + Mechanism "2.1 Cavitation" ← CORRECT (different observation vs cause)
   - The Symptom is what you OBSERVE; the Mechanism is what CAUSES it. They must be distinct.
   - Avoid generic or duplicated meaning with the Symptom.
   - **CARDINALITY**: For EACH (Maintainable Item, Symptom) pair, generate MULTIPLE (2-5) DISTINCT Failure Mechanisms
   - **CRITICAL**: DO NOT generate only 1 mechanism per symptom for most items - generate 2-5 mechanisms per symptom
   - The number of mechanisms per symptom depends on:
     * Technical importance of the Maintainable Item for the Item Class
     * Complexity of failure physics for that specific symptom
   - For each symptom, think: "What are the DIFFERENT physical causes that could produce this symptom?"
   - Examples showing MULTIPLE mechanisms per symptom:
     * "Shaft Failure" + "VIB - Vibration" → 4 mechanisms: Fatigue, Misalignment, Unbalance, Wear (4 separate rows)
     * "Bearing Failure" + "VIB - Vibration" → 3 mechanisms: Wear, Misalignment, Fatigue (3 separate rows)
     * "Impeller Failure" + "PDE - Parameter deviation" → 2 mechanisms: Erosion, Corrosion (2 separate rows)
     * "Filter Failure" + "PLU - Plugged" → 2 mechanisms: Blockage, Contamination (2 separate rows)

8. Failure Effect  
   - Describe the local effect of the failure at the Maintainable Item level.
   - Do NOT describe system-level consequences here.

9. Treatment Actions  
   - List 2–3 actions per Failure Mechanism.
   - Each action must be:
     - binary [Y/N]
     - measurable
     - auditable
     - technically feasible to fix/avoid the Failure Mechanism for that specific Symptom.
   - No administrative or documentation-only actions like registration in CMMS or cleaning.

10. Reporting Question ID  
   - Use Task Template IDs from EMS.xlsx when applicable.
   - If not available, mark as "TBD".

11. Treatment Action Type  
   - One of:
     Predictive | Preventive | Failure-Finding | Redesign | Run-to-Failure
   - One type per Treatment Action.

## CARDINALITY RULES

**CRITICAL UNDERSTANDING**: The relationship between Maintainable Items, Symptoms, and Failure Mechanisms follows a MANY-TO-MANY structure, NOT 1-to-1 mappings.

### Rule 1: Maintainable Item → Symptoms (4-8 per item)
- Each Maintainable Item MUST have 4–8 DISTINCT Symptoms (many symptoms per item)
- The exact number within this range depends on the **technical complexity** of the Maintainable Item:
  * **High complexity/critical items** (e.g., Impeller, Shaft, Turbine Rotor): 6-8 symptoms
  * **Moderate complexity** (e.g., Bearing, Coupling, Seal): 5-6 symptoms
  * **Lower complexity** (e.g., Filter, Sensor, Simple valve): 4-5 symptoms
- DO NOT create only 1 or 2 symptoms per Maintainable Item

### Rule 2: (Maintainable Item, Symptom) → Failure Mechanisms (MULTIPLE: 2-5 per symptom)
- **CRITICAL**: For EACH Symptom associated with a Maintainable Item, generate MULTIPLE (2–5) DISTINCT Failure Mechanisms
- **COMMON ERROR**: Generating only 1 mechanism per symptom for all items - this is INCORRECT
- **CORRECT APPROACH**: For each symptom, identify 2-5 different physical causes that could produce that symptom
- The exact number within this range depends on:
  * **Technical importance** of the Maintainable Item for the Item Class
  * **Complexity of failure physics** for that specific symptom
  * **Criticality** of the equipment
- Examples showing MULTIPLE mechanisms:
  * **Critical symptom on critical item**: 3-5 mechanisms (e.g., "Shaft Failure" + "VIB - Vibration" → 4 mechanisms: Fatigue, Misalignment, Unbalance, Wear)
  * **Moderate importance**: 2-3 mechanisms (e.g., "Bearing Failure" + "NOI - Noise" → 3 mechanisms: Wear, Misalignment, Cavitation)
  * **Simple symptom on simple item**: 1-2 mechanisms (e.g., "Filter Failure" + "PLU - Plugged" → 2 mechanisms: Blockage, Contamination)
- Each mechanism gets its OWN output row (same MI + Symptom can appear on multiple rows with different mechanisms)

### Rule 3: Treatment Actions per Mechanism
- Each Failure Mechanism MUST have 2–3 Treatment Actions
- Each Treatment Action must be binary, measurable, and auditable

### Rule 4: Output Row Structure
- Each output row represents: **ONE Maintainable Item + ONE Symptom + ONE Failure Mechanism + Treatment Actions**
- To satisfy Rules 1 and 2, you MUST generate multiple rows for the same Maintainable Item

### Concrete Example Structure:

**Scenario**: Analyzing "Compressor Shaft Failure" (high complexity item)

**Required output structure** (simplified, showing only key columns):

| Maintainable Item | Symptom | Failure Mechanism |
|-------------------|---------|-------------------|
| Compressor Shaft Failure | VIB - Vibration | Fatigue |
| Compressor Shaft Failure | VIB - Vibration | Misalignment |
| Compressor Shaft Failure | VIB - Vibration | Unbalance |
| Compressor Shaft Failure | VIB - Vibration | Wear |
| Compressor Shaft Failure | PDE - Parameter deviation | Deformation |
| Compressor Shaft Failure | PDE - Parameter deviation | Corrosion |
| Compressor Shaft Failure | NOI - Noise | Cavitation |
| Compressor Shaft Failure | NOI - Noise | Impact |
| Compressor Shaft Failure | LOO - Leak of oil | Seal wear |
| Compressor Shaft Failure | OHE - Overheating | Friction |
| Compressor Shaft Failure | OHE - Overheating | Inadequate cooling |
| Compressor Shaft Failure | FWR - Abnormal wear | Abrasion |
| Compressor Shaft Failure | FWR - Abnormal wear | Erosion |

**Analysis of the example:**
- **Rule 1 Check**: "Compressor Shaft Failure" has 6 distinct symptoms (VIB, PDE, NOI, LOO, OHE, FWR) → ✓ Within 4-8 range
- **Rule 2 Check**: 
  * VIB has 4 mechanisms → ✓ Within 2-5 range
  * PDE has 2 mechanisms → ✓ Within 2-5 range
  * NOI has 2 mechanisms → ✓ Within 2-5 range
  * LOO has 2 mechanisms → ✓ Within 2-5 range (Note: adjusted from 1 to meet minimum requirement)
  * OHE has 2 mechanisms → ✓ Within 2-5 range
  * FWR has 2 mechanisms → ✓ Within 2-5 range
- **Total output rows**: 13 rows for this single Maintainable Item

**Anti-Pattern Example** (INCORRECT - DO NOT DO THIS):

| Maintainable Item | Symptom | Failure Mechanism |
|-------------------|---------|-------------------|
| Compressor Shaft Failure | VIB - Vibration | Fatigue |

This is WRONG because:
- ❌ Only 1 symptom per Maintainable Item (violates Rule 1: need 4-8)
- ❌ Only 1 mechanism per symptom (acceptable but may be insufficient for complex items)
- ❌ Results in only 1 row for a complex Maintainable Item (should have 10-40 rows typically)

### Summary Formula:
- **Minimum rows per Maintainable Item** = 4 symptoms × 1 mechanism = 4 rows
- **Maximum rows per Maintainable Item** = 8 symptoms × 5 mechanisms = 40 rows
- **Typical for complex item** = 6 symptoms × 2-3 mechanisms = 12-18 rows
- **Typical for simple item** = 4 symptoms × 1-2 mechanisms = 4-8 rows

## VALIDATION BEFORE OUTPUT

Before finalizing the output, the agent must confirm ALL of the following:

### Quality Gate Checks:
- **G0**: All Maintainable Items are derived from EMS Boundaries column and use Maintainable Item Catalog terminology
- **G1**: Each Maintainable Item has exactly 4-8 distinct symptoms (**NO EXCEPTIONS - DO NOT PROCEED WITH FEWER**)
  - Method: Group by Maintainable Item, count unique Symptoms → must be between 4 and 8
  - **BEFORE generating output**: Create a symptom plan for each MI ensuring 4-8 symptoms
  - Use ELR categories to guide symptom selection based on MI type
- **G2**: Each (Maintainable Item, Symptom) pair has 2-5 distinct failure mechanisms
  - Method: Group by (Maintainable Item, Symptom), count unique Mechanisms → must be between 2 and 5
  - **BEFORE generating output**: Plan mechanisms for each symptom considering complexity
- **G3**: No "Other" or "Unknown" values are present in Symptoms or Failure Mechanisms
- **G4**: All Maintainable Items end with "Failure"
- **G5**: Treatment Actions are technically feasible for the specific mechanism
- **G6**: Each Symptom ↔ Maintainable Item pair is physically plausible (ELR validation)
- **G7**: **NO DUPLICATION**: Each row must have DIFFERENT terms in Symptom vs Failure Mechanism columns
  - Check: If Symptom contains term "X", Mechanism must NOT contain term "X"
  - Symptom = what you OBSERVE; Mechanism = what CAUSES it (must be distinct concepts)

### Boundary Validation:
- No Maintainable Item outside EMS boundaries is included (unless marked with "(*)" with engineering justification)

### Cardinality Validation Steps:

**Step 1**: Count Symptoms per Maintainable Item
```
For each unique Maintainable Item:
  Count distinct Symptoms
  If count < 4 or count > 8: FAIL - Fix required
```

**Step 2**: Count Mechanisms per (Maintainable Item, Symptom) pair
```
For each unique (Maintainable Item, Symptom) combination:
  Count distinct Failure Mechanisms
  If count < 1 or count > 5: FAIL - Fix required
```

**Step 3**: Verify output row count makes sense
```
Expected rows per Maintainable Item ≈ (Number of Symptoms) × (Average mechanisms per symptom)
Typical range: 4-40 rows per Maintainable Item
If outside range: Review for errors
```

### Validation Checklist (must ALL be true):
- [ ] **CRITICAL**: Every Maintainable Item appears with EXACTLY 4-8 different Symptoms (count and verify each MI)
- [ ] Every (Maintainable Item, Symptom) pair appears with 2-5 different Failure Mechanisms
- [ ] **CRITICAL**: NO DUPLICATION - Every row has different terms in Symptom vs Mechanism (check each row)
- [ ] No "Other" or "Unknown" entries exist anywhere
- [ ] Every Maintainable Item name ends with "Failure"
- [ ] All Symptom-Maintainable Item combinations are physically plausible
- [ ] All Maintainable Items are derived from EMS Boundaries (or marked with "(*)") and use Catalog terminology
- [ ] Each mechanism has 2-3 Treatment Actions listed
- [ ] Total number of output rows is reasonable (minimum: 4 rows per MI; typical: 10-20 rows per complex MI)

**If any validation check fails**, the agent MUST correct the output before presenting it. DO NOT proceed with invalid output.

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
   - **CARDINALITY**: For each Maintainable Item there must exist 4 to 8 DISTINCT Symptoms (not 1-to-1).

7. Failure Mechanism  
   - ISO 14224 Table B.2 mechanism.
   - Must be physically linked to the Maintainable Item and the Symptom.
   - Avoid generic or duplicated meaning with the Symptom.
   - **CARDINALITY**: For each (Maintainable Item, Symptom) pair there must exist 1 to 5 DISTINCT Failure Mechanisms (not 1-to-1).

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

**CRITICAL**: The relationship between Maintainable Items, Symptoms, and Failure Mechanisms is NOT 1-to-1.

- Each Maintainable Item MUST have 4–8 DISTINCT Symptoms (many symptoms per item).
- For EACH Symptom associated with a Maintainable Item, there MUST be 1–5 DISTINCT Failure Mechanisms (many mechanisms per symptom).
- Each Failure Mechanism MUST have 2–3 Treatment Actions.
- Each output row must contain:
  ≥1 Symptom, ≥1 Failure Mechanism, ≥1 Treatment Action.

**Example Structure:**
- Maintainable Item A → Symptom 1 → Mechanisms 1.1, 1.2, 1.3
- Maintainable Item A → Symptom 2 → Mechanisms 2.1, 2.2
- Maintainable Item A → Symptom 3 → Mechanisms 3.1, 3.2, 3.3, 3.4
- ... (continuing until Maintainable Item A has 4-8 symptoms total)

## VALIDATION BEFORE OUTPUT
Before finalizing the output, the agent must confirm:
- All Quality Gates G0–G6 are satisfied.
- All Maintainable Items are derived from EMS Boundaries column and use Maintainable Item Catalog terminology.
- Each Maintainable Item has exactly 4-8 distinct symptoms.
- Each (Maintainable Item, Symptom) pair has 1-5 distinct failure mechanisms.
- No Maintainable Item outside EMS boundaries is included (unless marked with "(*)" with justification).
- No "Other" or "Unknown" values are present.
- All Maintainable Items end with "Failure".

If any rule is violated, the agent must correct the output before presenting it.

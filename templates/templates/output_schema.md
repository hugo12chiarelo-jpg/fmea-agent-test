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
   - Name must come from Maintainable Item Catalog.
   - Must end with "Failure".
   - Inferred items which are not part of the Maintainable Item Catalog must be marked with "(*)".
  
5. Maintainable Item Function
   - Function of the Maintainable Item relative to the Item Class.
   - Must be technically descriptive (not generic) for that specific Maintainable Item

6. Symptom  
   - ISO 14224 code + description (e.g., "VIB - Vibration").
   - Must follow Symptom Catalog from ISO 14224.
   - Any non-catalog symptom must be marked with "(*)".
   - For each Maintainable Item must exist at least 4 until 8 Symptoms

7. Failure Mechanism  
   - ISO 14224 Table B.2 mechanism.
   - Must be physically linked to the Maintainable Item and the Symptom.
   - Avoid generic or duplicated meaning with the Symptom.
   - For each symptom must exist 1 until 5 Failure mechanism

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
- 4–8 Symptoms per Maintainable Item.
- 1–5 Failure Mechanisms per Symptom.
- 2–3 Treatment Actions per Failure Mechanism.
- Each output row must contain:
  ≥1 Symptom, ≥1 Failure Mechanism, ≥1 Treatment Action.

## VALIDATION BEFORE OUTPUT
Before finalizing the output, the agent must confirm:
- All Quality Gates G1–G6 are satisfied.
- No Maintainable Item outside EMS boundaries is included.
- No "Other" or "Unknown" values are present.
- All Maintainable Items end with "Failure".

If any rule is violated, the agent must correct the output before presenting it.

OBJECTIVE
Build a complete, ISO 14224–compliant FMEA for a user-provided Item Class of the EMS Upgrade, strictly following the "Business Rules for EMS Upgrade Rev01". 
The FMEA must reflect the technical characteristics of each Maintainable Item, with correct Symptoms, Failure Mechanisms, and Treatment Actions derived from reliability engineering standards (ISO 14224, OREDA, Moubray RCM) and the Maintenance Manual (PDF) as technical base for Treatment Actions.

**CRITICAL CONSTRAINTS** (MUST BE ENFORCED):
1. **CARDINALITY ENFORCEMENT**: Each Maintainable Item MUST have EXACTLY 4-8 distinct Symptoms. NO EXCEPTIONS.
2. **MANY-TO-MANY STRUCTURE**: For each (MI, Symptom) pair, generate 2-5 distinct Failure Mechanisms.
3. **NO DUPLICATION**: Symptom and Failure Mechanism on the same row MUST use DIFFERENT terms/concepts.
   - If Symptom is "2.1 Cavitation", Mechanism CANNOT be "2.1 Cavitation"
   - If Symptom is "VIB - Vibration", Mechanism CANNOT be "1.2 Vibration"
   - Symptom = Observable condition; Mechanism = Physical root cause (must differ)
4. **VERIFICATION BEFORE OUTPUT**: Count symptoms per MI and mechanisms per (MI, Symptom) pair BEFORE finalizing output.

NON-NEGOTIABLE SOURCES AND PRIORITY

Business Rules for EMS Upgrade Rev01: mandatory definitions, concepts, and rules. Do not introduce alternative concepts or rule reinterpretations.
EMS.xlsx: defines scope/boundaries and Task Template IDs. Boundaries define what is inside maintenance scope.
Maintainable Item Catalog: authoritative item naming; any inferred maintainable item must be marked with "(*)".
Symptom Catalog: symptom codes to be used.
ISO 14224: use Table B.15 for symptoms and Table B.2 for failure mechanisms.
Maintenance Manual.pdf: technical basis to design Treatment Actions.
If there is any conflict, follow the priority above.

INPUT
The user will provide the Item Class to be analyzed using the Instructions.

OUTPUT — REQUIRED COLUMNS (FINAL FILE)
Item Class | Function | Maintainable Item | Symptom | Failure Mechanism | Failure Effect | Treatment Actions | Reporting Question ID | Treatment Action Type

CORE BEHAVIOR
Reason at the Maintainable Item level (not category level).
Even within the same category, maintainable items may have distinct symptoms/mechanisms/actions.
When in doubt, differentiate by:
  Function (e.g., torque transfer vs load support)
  Observable indicators (e.g., vibration vs leak)
  Failure energy path (mechanical, hydraulic, electrical)
  
SCOPE AND BOUNDARY RULES (EMS.xlsx)
Interpret EMS boundaries as defining what is included in the Item Class maintenance scope.

**CRITICAL BOUNDARY PARSING RULES:**
1. Items marked with "Exclude", "optional", "if applicable", or "if any" MUST NOT be included in Maintainable Items
2. Everything else mentioned in boundaries IS included unless explicitly excluded
3. Read the full boundaries text carefully to identify ALL included components, systems, and equipment
4. Do NOT limit to only "main" or "most probable" items - include ALL technically relevant items from boundaries

Maintainable Item list must follow what is included in EMS boundary and exclude what is excluded.

MAINTAINABLE ITEM RULES
**CRITICAL**: Maintainable Items MUST be derived from the "Boundaries" column of the EMS file AND transformed using the terminology from "Maintainable Item Catalog.csv".

**Process:**
1. Read the "Boundaries" column from EMS file for the specified Item Class.
2. **Parse boundaries to identify included vs excluded items:**
   - Items in lines starting with "Exclude" or containing "exclude" keyword → EXCLUDE
   - Items marked as "optional", "if applicable", "if any" → EXCLUDE
   - All other items mentioned → INCLUDE
3. Identify ALL components, systems, and equipment mentioned in the included boundaries text (do not limit to main items only).
4. **APPLY ENGINEERING INTELLIGENCE - Filter boundary items using maintainability criteria:**
   - **PRIMARY CRITERION (Critical System Failure Test)**: 
     * **Key question**: "Could this component's failure cause complete system failure?"
     * If YES → Component is a candidate for Maintainable Item
     * If NO → Component is likely a sub-component, redundant, or covered by another MI
     * This test is the MOST IMPORTANT and should be evaluated FIRST
   - **Definition of INDEPENDENTLY MAINTAINABLE**: After passing the primary criterion, a component qualifies as a maintainable item if it meets ALL of these criteria:
     * Can be inspected, repaired, or replaced as a separate unit
     * Has distinct, observable failure symptoms that differ from other components
     * Is subject to planned or corrective maintenance activities
     * Failure would impact equipment function or performance (already confirmed by primary criterion)
   - **Exclusion criteria** - Do NOT include items that are:
     * Sub-components physically or functionally covered by a parent maintainable item
     * Integral parts that cannot be serviced independently (e.g., permanently assembled components)
     * Not subject to independent maintenance actions
     * Cannot be independently observed or monitored for failure symptoms
     * Components whose failure does NOT cause system failure (failed primary criterion)
   - **Decision framework**: For each boundary item, evaluate IN THIS ORDER:
     0. **PRIMARY: Critical system failure test**: Could this component's failure cause complete system failure?
     1. **Independence test**: Can this component be inspected/maintained/replaced without disassembling parent equipment?
     2. **Symptom distinctiveness test**: Does this component exhibit unique failure symptoms that differ from related components?
     3. **Maintenance action test**: Are there specific maintenance tasks (predictive, preventive, corrective) for this component alone?
   - **Hierarchical component analysis**: When boundaries list multiple related components:
     * Apply the primary criterion first: which components' failures would cause system failure?
     * Identify parent-child relationships (e.g., shaft vs axle, rotor assembly vs field components)
     * Select the highest-level component that is independently maintainable
     * Exclude sub-components that are covered by the parent's maintenance regime
   - **Generic filtering principle**: If component A's maintenance activities and failure symptoms are fully covered by component B's FMEA, then exclude component A
5. Transform each identified component name to match the standard naming from "Maintainable Item Catalog.csv".
6. Use Maintainable Item Catalog as the authoritative naming standard:
   - Replace boundary component names with their catalog equivalents.
   - Example: If boundary mentions "bearing", use "Radial bearing" or "Thrust bearing" from catalog.
   - Example: If boundary mentions "compressor", use appropriate catalog terms like "Rotor w/impellers", "Casing", etc.
7. **PROACTIVELY SUGGEST ISO 14224-COMPLIANT MAINTAINABLE ITEMS** not explicitly in boundaries:
   - **Reference ISO 14224 Table B.15 (Equipment taxonomy)** to identify standard maintainable items for the Item Class
   - **Generic system categories to evaluate** (applicability depends on Item Class):
     * **Power transmission systems**: Gears, couplings, drives, shafts where torque/power is transmitted
     * **Lubrication systems**: Oil supply, filtration, cooling, distribution components critical for reducing friction
     * **Cooling/thermal management systems**: Heat exchangers, fans, coolant circuits for temperature control
     * **Sealing systems**: Mechanical seals, gaskets, packing that prevent leakage or contamination
     * **Bearing systems**: Radial, thrust, or specialized bearings supporting rotating/reciprocating motion
     * **Monitoring/control systems**: Sensors, transmitters, controllers, protection devices
     * **Power supply systems**: Batteries, inverters, internal power circuits, backup power
     * **Structural/containment systems**: Casings, frames, foundations, enclosures
     * **Fluid handling systems**: Piping, valves, filters, accumulators for process or utility fluids
   - **Selection methodology**:
     1. Analyze the Item Class functional requirements and operating principles
     2. Identify which generic system categories are technically relevant
     3. Cross-reference with ISO 14224 Table B.15 for standard maintainable items
     4. Verify each suggested item has distinct failure modes and maintenance requirements
     5. Ensure suggested items are not already covered by boundary-derived maintainable items
   - **Mark ALL suggested items with "(*)"** to indicate they are inferred from ISO 14224/manual, not explicit in boundaries
   - **Engineering validation**: Each suggested item must have clear justification based on failure risk, criticality, and maintenance strategy
8. Mark inferred items with "(*)": If a maintainable item is suggested by AI from ISO 14224, manual, or engineering judgment and is NOT explicitly stated in EMS boundaries, mark it with "(*)".
9. Never suggest any maintainable item that is mentioned as excluded in boundaries.
10. Add new maintainable items when there are relevant components/systems that could cause system failure, including (non-exhaustive): Power transmission; construction components (impeller, piston, valves, etc.); control & monitoring; lubrication system; seal system; cooling system; exhaust; fuel system; or any other relevant system.
11. Appropriate level test: Ask: "What component could fail to cause system failure?" Example: Impeller Failure, Shaft Failure, Dry Gas Seal Failure.
12. Grouping boundary subcomponents under one maintainable item is allowed ONLY if: (a) physically inseparable or replaced together as one unit, AND (b) identical symptoms, mechanisms, and treatment actions. Otherwise, create independent maintainable items.
13. Maintainable Items must end with "Failure".
14. Add a column "Maintainable Item Function": describe the function of the maintainable item relative to the Item Class.
15. At the end, answer: "What are ALL the maintainable items (not just the most probable) that can cause a functional failure in the main equipment?"
STRONGLY RECOMMEND ADDING (ENGINEERING VALIDATION REQUIRED)
If the AI suggests maintainable items not explicit in EMS boundary, output a separate list at the end of the FMEA document: 

**SUGGESTED ADDITIONAL MAINTAINABLE ITEMS (for Engineering Review)**

| Maintainable Item | Justification (ISO 14224 or Engineering Basis) | Expected Symptoms | Expected Failure Mechanisms | Suggested Treatment Actions |
|-------------------|-----------------------------------------------|-------------------|----------------------------|----------------------------|
| [Example: Lubrication System Failure (*)] | [ISO 14224 standard MI for rotating equipment; critical for bearing health and motor reliability] | [LOO, PDE, OHE] | [Contamination, Degradation, Leakage] | [Oil analysis, Filter inspection, Leak detection] |

**Instructions for this section:**
1. List ALL maintainable items marked with "(*)" in the main FMEA table
2. Provide clear engineering justification for each suggested item (reference ISO 14224, reliability standards, or failure risk analysis)
3. Include preview of expected symptoms and mechanisms to demonstrate technical plausibility
4. This section helps validate that AI suggestions are technically sound and not arbitrary

Note: Trust Bearing must be treated as NDE Bearing.

SYMPTOM RULES
Symptoms must follow ISO 14224 symptom standard: CODE + Description (e.g., PDE - Parameter deviation).
Use only symptoms listed in Symptom Catalog and aligned with its context of use.
Any symptom suggestion not present in the list must be identified with "(*)".
Symptoms must be:
physically plausible for the Maintainable Item (Engineering Logic Validation, ELR),
detectable by monitoring/inspection/operational parameters,
justified by physics of failure (not only by code similarity).
Item-Specific Precedence Rule (ISP): Each maintainable item is unique. Do not standardize symptoms solely by category. Derive symptoms from:
functional description (EMS boundaries or catalog),
physical failure behavior (motion, load path, energy transfer, sealing, control),
measurable/observable indicators (temperature, vibration, flow, leak, signal, etc.). ELR is a constraint/filter, not a symptom generator.
FAILURE MECHANISM RULES
Always use ISO 14224 Table B.2 for Failure Mechanisms.
Mechanisms must be physically traceable to the maintainable item + symptom: Ask: "What is physically happening inside this Maintainable Item when this Symptom is observed?"
Choose mechanism classifications consistent with the Maintainable Item Function.
**CRITICAL ANTI-DUPLICATION RULE**: NEVER use the same term/concept in both Symptom and Failure Mechanism columns on the same row.
  - BAD Example: Symptom "2.1 Cavitation" + Mechanism "2.1 Cavitation" ← FORBIDDEN
  - BAD Example: Symptom "VIB - Vibration" + Mechanism "1.2 Vibration" ← FORBIDDEN
  - GOOD Example: Symptom "VIB - Vibration" + Mechanism "2.6 Fatigue" ← CORRECT
  - GOOD Example: Symptom "NOI - Noise" + Mechanism "2.1 Cavitation" ← CORRECT (Cavitation causes noise, not duplicated)
  - The Symptom is what you OBSERVE; the Mechanism is what CAUSES it. They must be different.
Avoid "Other" and "Unknown".
TREATMENT ACTION RULES
For each Mechanism, create 2–3 Treatment Actions.
Treatment Actions must be binary, measurable, auditable: [Y/N].
Classify each Treatment Action as one of: Predictive, Preventive, Failure-Finding, Redesign, Run-to-Failure.
Treatment Actions must be technically feasible for the maintainable item + mechanism combination.
Avoid administrative/procedural/documentation-only actions.
Use Maintenance Manual.pdf as technical basis to build the actions.
Each mechanism row must have ≥1 Treatment Action.
REQUIRED CARDINALITIES

**CRITICAL RELATIONSHIP STRUCTURE**: The relationship between Maintainable Items, Symptoms, and Failure Mechanisms is MANY-TO-MANY, NOT 1-to-1.

### Cardinality Rules:

1. **Maintainable Item → Symptoms**: Each Maintainable Item MUST have 4–8 DISTINCT Symptoms
   - The number depends on the technical complexity of the Maintainable Item relative to its Item Class
   - More complex items need more symptoms (up to 8)
   - Simpler items need fewer symptoms (at least 4)
   - Example: A complex Maintainable Item like "Impeller Failure" may have 6-8 symptoms, while a simpler one like "Filter Failure" may have 4-5 symptoms

2. **Symptom → Failure Mechanisms**: For EACH Symptom of a Maintainable Item, generate MULTIPLE (2–5) DISTINCT Failure Mechanisms
   - **CRITICAL**: DO NOT generate only 1 mechanism per symptom for most items - this is the most common error
   - The number depends on the technical complexity and importance of the Maintainable Item for the Item Class
   - Critical/complex Maintainable Items with a specific Symptom SHOULD have 2-5 mechanisms for that symptom
   - Less critical/simple Maintainable Items with a specific Symptom may have 1-2 mechanisms for that symptom
   - For each symptom, ask: "What are the DIFFERENT physical root causes that could produce this observable symptom?"
   - Examples showing MULTIPLE mechanisms per symptom:
     * "Shaft Failure" + "VIB - Vibration" → 4 mechanisms: Fatigue, Misalignment, Unbalance, Wear
     * "Bearing Failure" + "VIB - Vibration" → 3 mechanisms: Wear, Misalignment, Fatigue
     * "Impeller Failure" + "NOI - Noise" → 3 mechanisms: Cavitation, Impact/collision, Resonance
   - Generate a SEPARATE OUTPUT ROW for each mechanism (same MI + Symptom appears on multiple rows)

3. **Each output row** must contain ≥1 mechanism and ≥1 treatment action

4. **For critical items**, ensure ≥10 distinct mechanisms distributed across all symptoms

### Concrete Example of Many-to-Many Structure:

**Maintainable Item: Impeller Failure**
- Symptom 1: VIB - Vibration
  - Mechanism 1.1: Unbalance
  - Mechanism 1.2: Cavitation erosion
  - Mechanism 1.3: Fatigue
- Symptom 2: PDE - Parameter deviation
  - Mechanism 2.1: Erosion
  - Mechanism 2.2: Corrosion
- Symptom 3: NOI - Noise
  - Mechanism 3.1: Cavitation
  - Mechanism 3.2: Impact/collision
  - Mechanism 3.3: Resonance
- Symptom 4: LOO - Leak of oil
  - Mechanism 4.1: Seal wear
- Symptom 5: OHE - Overheating
  - Mechanism 5.1: Friction
  - Mechanism 5.2: Inadequate cooling
- Symptom 6: FWR - Abnormal wear
  - Mechanism 6.1: Abrasion
  - Mechanism 6.2: Erosion
  - Mechanism 6.3: Corrosion

This example shows:
- 1 Maintainable Item ("Impeller Failure") has 6 Symptoms (within 4-8 range)
- Each Symptom has 1-3 Failure Mechanisms (within 2-5 range)
- Total: 15 distinct mechanism entries for this Maintainable Item

**DO NOT create 1-to-1 relationships.** Each Maintainable Item MUST be expanded into multiple (Maintainable Item, Symptom) pairs, and each such pair MUST be expanded into multiple (Maintainable Item, Symptom, Failure Mechanism) rows.
QUALITY GATES (MUST PASS BEFORE EXPORT)

**G0**: Maintainable Items MUST be derived from EMS Boundaries column AND use terminology from Maintainable Item Catalog. Items not explicitly in boundaries must be marked with "(*)" and engineering justification must be provided.

**G1**: **CARDINALITY - Symptoms per Maintainable Item**: Each Maintainable Item MUST have exactly 4–8 DISTINCT Symptoms. No more, no less.
   - **MANDATORY VERIFICATION**: Count the number of unique symptoms for each Maintainable Item
   - **BEFORE GENERATING OUTPUT**: Plan symptoms for each MI to ensure 4-8 range
   - If count < 4: STOP and add more symptoms based on technical complexity (use ELR categories as guide)
   - If count > 8: STOP and consolidate to most relevant symptoms
   - **DO NOT PROCEED** if any Maintainable Item has fewer than 4 or more than 8 symptoms
   - Verify: Each Maintainable Item appears in the output with 4-8 different Symptom values

**G2**: **CARDINALITY - Mechanisms per Symptom**: For EACH (Maintainable Item, Symptom) pair, there MUST be MULTIPLE (2–5) DISTINCT Failure Mechanisms.
   - This means: For every combination of a specific Maintainable Item with a specific Symptom, generate between 2 and 5 different mechanisms
   - **CRITICAL**: Most (MI, Symptom) pairs should have 2-5 mechanisms, NOT just 1
   - **COMMON ERROR**: Generating only 1 mechanism per symptom for all items - this is INCORRECT
   - **MANDATORY VERIFICATION**: Count mechanisms for each (Maintainable Item, Symptom) pair
   - **BEFORE GENERATING OUTPUT**: Plan mechanisms for each (MI, Symptom) pair to ensure 2-5 range
   - If count < 2: ERROR - Every symptom must have at least two mechanisms
   - If count > 5: STOP and consolidate to most relevant mechanisms
   - Verify: Group output by (Maintainable Item, Symptom) and count distinct mechanisms in each group - must be between 2 and 5

**G3**: No "Other/Unknown" values are allowed in Symptoms or Failure Mechanisms. All values must be specific and traceable to ISO 14224.

**G4**: All Maintainable Items MUST end with "Failure". 

**G5**: Treatment Actions must prevent/predict/failure-find the mechanism for that specific maintainable item; actions do not need to start with the maintainable item name. 

**G6**: Engineering Logic Validation (ELR) — each Symptom ↔ Maintainable Item pair must be physically plausible; if invalid, replace using Replacement Logic.

**G7**: **NO DUPLICATION**: Symptom and Failure Mechanism on the same row MUST NOT contain the same term, code, or concept.
   - Check every row: If Symptom contains "X", Mechanism must NOT contain "X"
   - Example violations to catch: "2.1 Cavitation" in both columns, "Vibration" in both columns
   - The Symptom describes what you OBSERVE; the Mechanism describes the PHYSICAL CAUSE
   - They MUST be conceptually distinct

**VERIFICATION CHECKLIST** before finalizing output:
- [ ] Count unique Symptoms per Maintainable Item → Must be 4-8 for each (NO EXCEPTIONS)
- [ ] Count unique Failure Mechanisms per (Maintainable Item, Symptom) pair → Must be 2-5 for each pair
- [ ] Verify no "Other" or "Unknown" entries exist
- [ ] Verify all Maintainable Items end with "Failure"
- [ ] Verify physical plausibility of all Symptom-Maintainable Item combinations
- [ ] **Verify NO DUPLICATION: Check each row to ensure Symptom ≠ Mechanism (different terms/concepts)**
- [ ] Verify total row count is reasonable: minimum 4 rows per MI, typical 10-20 rows per complex MI

ENGINEERING LOGIC VALIDATION (ELR) — VALIDATION FILTER
ELR acts as a validation filter, not a symptom source.

Build symptom/mechanism lists per maintainable item using functional and physical logic.
Run ELR to flag and replace physically impossible combinations.
If a symptom is filtered out, propose nearest realistic equivalent (Replacement Logic), keeping item-specific logic.
ELR CATEGORY TABLE (USE AS VALIDATION)
Rotating mechanical (Impeller, Shaft, Bearing, Coupling, Rotor): Valid: VIB, PDE, LOO, VLO, NOI, OHE, FWR Avoid: NOO Replace: NOO → LOO/VLO (unless total seizure)

Static mechanical (Casing, Structure, Housing): Valid: ELP, ILP, STD, PDE Avoid: VIB, NOO Replace: VIB → STD or PDE

Hydraulic/utility (Cooler, Filter, Coalescer, Lube System): Valid: PDE, ELP/ELU, PLU, LOO Avoid: VIB Replace: VIB → PDE or PLU

Instrumentation/control (Transmitters, Sensors, PLC): Valid: AIR, CSF, SHH, SLL, SPO Avoid: VIB, NOO, LOO/VLO Replace: → AIR (AI reading error)

Sealing systems (Dry Gas Seal, Seal Gas Panel): Valid: ELP, PDE, SPO, CSF Avoid: NOO, LOO Replace: NOO → ELP; LOO → PDE

Electrical/drive train (Motor, Generator, Starter): Valid: FTS, FRO, FWR, PDE Avoid: ELP, PLU Replace: → FRO or FTS

FINAL EXECUTION RULE
If the user requests "build FMEA for [Item Class]", assume they mean the complete version as per Business Rules, not a minimal version.

# ELU and ELP Symptom Concepts Update - ISO 14224 Alignment

## Overview

This document summarizes the refinement of ELU (External leakage - utility medium) and ELP (External leakage - process medium) symptom concepts to align with ISO 14224 standard, specifically tables B.6 through B.13.

## Problem Statement (Original Issue)

The original issue (in Portuguese) identified the need to better define two symptoms:

1. **ELU - External leakage - utility medium**: Occurs when there's leakage of Oil, Lubricant or water - liquids that support the process of main equipment. Valid when equipment has utility fluid circuits. NOT valid for junction boxes (electrical isolation only, no fluids).

2. **ELP - External leakage - process medium**: Occurs when there are leaks in the operation process of equipment. For FPSO applications, this includes gas, oil, or well injection water leakage. These symptoms apply to equipment with containment function for process fluids.

## Key Principle: Function-Based Classification

The critical distinction is based on **FLUID FUNCTION**, not fluid type:
- **ELP**: Fluid IS the product or is part of the MAIN OPERATIONAL PROCESS
- **ELU**: Fluid SUPPORTS equipment operation but IS NOT the main process

## Changes Made

### 1. Symptom Catalog (inputs/Catalogs/Symptom Catalog.csv)

#### ELP Definition Enhancement:
- **Before**: "Process fluid leaking to the environment"
- **After**: "Leakage of the main process fluid that the equipment is designed to contain, transport, or process. This includes production fluids such as crude oil, natural gas, process water, injection water, or any fluid that is part of the primary operational process."
- **Added**: Equipment examples, valid applications, ISO 14224 reference

#### ELU Definition Enhancement:
- **Before**: "External leakage of utility fluid (water, air, lubrication oil)"
- **After**: "Leakage of auxiliary/utility fluids that support the operation of equipment but are NOT part of the main process. Includes lubricating oil, cooling water, service air, hydraulic oil, seal flush fluids."
- **Added**: Equipment examples, EXPLICIT invalid cases (junction boxes, terminal boxes, dry electrical enclosures), ISO 14224 reference

### 2. Business Rules (inputs/Business_Rules/Business Rules.txt)

Added new section: "CRITICAL GUIDANCE: ELU vs ELP SYMPTOM SELECTION (ISO 14224)"

**Content includes**:
- Decision criteria based on fluid function
- Detailed explanation of ELP vs ELU
- When ELU/ELP DO NOT APPLY section
- 4 correct application examples (pump, motor, compressor, valve)
- 3 incorrect application examples (junction box, cable box, transmitter)
- Key decision question for classification

### 3. Spec Template (templates/templates/spec_fmea_ems_rev01.md)

**Added Section A: ELP - External Leakage - Process Medium**
- Definition and when to apply
- Valid applications: Process pumps, compressors, valves, heat exchangers, vessels, separators
- Invalid applications: Electric motors, junction boxes, transmitters
- Correct examples with proper failure mechanisms
- Forbidden examples (ELP + 1.1 Leakage)

**Enhanced Section B: ELU - External Leakage - Utility Medium**
- Expanded definition with support function emphasis
- Valid applications: Lubrication, cooling, hydraulic, pneumatic systems
- Invalid applications with explicit examples (junction boxes, terminal boxes, cable glands)
- Key validation question: "Does this equipment have utility fluid circuits?"
- Multiple correct and incorrect examples

**Added Section C: Common Guidance**
- Key ISO 14224 concepts (symptom vs mechanism)
- Forbidden symptom-mechanism pairs
- Two-question decision logic

## Key Examples from Updates

### ✅ CORRECT Applications:

1. **Centrifugal Pump (crude oil service)**:
   - ELP: Crude oil leak from mechanical seal (process fluid)
   - ELU: Lube oil leak from bearing housing (support fluid)

2. **Electric Motor**:
   - ELU: Cooling water from heat exchanger, lube oil from bearings
   - NOT ELP: Motor does not contain process fluids

3. **Gas Compressor**:
   - ELP: Natural gas leak from seal (process medium)
   - ELU: Lube oil leak, seal oil leak (support fluids)

### ❌ INCORRECT Applications:

1. **Junction Box**:
   - NOT ELU: No fluids present (electrical isolation only)
   - NOT ELP: No process fluids
   - Valid symptoms: STD (Structural deficiency), PTF (Power transmission failure)

2. **Cable Termination Box**:
   - NOT ELU: No utility fluids
   - NOT ELP: No process fluids

## Decision Logic

Two key questions for AI agent:

**Question 1**: "What is the PRIMARY FUNCTION of this fluid?"
- If "To be contained/transported/processed by the equipment" → **ELP**
- If "To support the equipment operation (cool/lubricate/actuate)" → **ELU**
- If "There is no fluid" → **Neither applies**

**Question 2**: "Is this equipment designed to contain/process this fluid as its main purpose?"
- If YES → **ELP**
- If NO, but has auxiliary fluids → **ELU**
- If NO fluids at all → **Neither applies**

## Testing Results

All tests passed (8/8):
- ✅ G8 Validation (Symptom Codes)
- ✅ G8a Validation (EMS Exclusions)
- ✅ G7 Validation (Term Duplication)
- ✅ Output Format (XLSX)
- ✅ ELU Guidance
- ✅ Suggested MIs Section
- ✅ Boundary Exclusion Examples
- ✅ DataFrame Conversion

Additional tests verified:
- ✅ Electric Motor Fixes (3/3 passed)
- ✅ Symptom in MI Validation (all G8 tests passed)

## Impact

This update will:
1. **Prevent errors**: Junction boxes and similar equipment will no longer incorrectly receive ELU symptoms
2. **Improve accuracy**: Clear distinction between process and utility medium leakages
3. **Align with ISO 14224**: All guidance references standard tables B.6-B.13
4. **Support FPSO context**: Examples include FPSO-specific scenarios (gas, crude oil, injection water)
5. **Provide clear decision logic**: AI agent can correctly classify symptoms based on equipment function

## Files Modified

1. `inputs/Catalogs/Symptom Catalog.csv` - Enhanced ELP and ELU definitions
2. `inputs/Business_Rules/Business Rules.txt` - Added ELU vs ELP decision guidance
3. `templates/templates/spec_fmea_ems_rev01.md` - Added ELP section, enhanced ELU section, added decision logic

## References

- ISO 14224 Standard Tables B.6 through B.13 (Failure Modes for Equipment)
- Original issue requirement (Portuguese): Adjust symptom concepts according to ISO 14224

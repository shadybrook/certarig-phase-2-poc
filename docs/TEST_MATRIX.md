# Phase 2 test matrix

## Demonstration cases

| Case | Input condition | Expected decision | Expected proof |
|---|---|---|---|
| Approved baseline | Channel map and calibration evidence match the baseline | Accept the bounded simulated run | No material finding and stable evidence checksum |
| Swapped channels | Pressure and flow identities are reversed | Prevent execution and request review | MAPPING_CHANGED and SIGNATURE_CONFLICT findings |
| Missing calibration | Pressure calibration reference is absent | Stop before execution | CALIBRATION_MISSING finding |
| Pressure limit breach | Simulated pressure exceeds 4.2 bar | Record a safe abort | SAFE_LIMIT_EXCEEDED finding and abort outcome |

## Automated browser tests

The Node.js suite verifies:

1. Exactly four repeatable demonstration cases are available.
2. The approved baseline completes without a material finding.
3. Swapped channels create mapping and response conflicts.
4. Missing calibration blocks execution.
5. A pressure limit breach creates a safe abort.
6. Every evidence bundle has the expected stable checksum format.

## Supplementary reference software tests

The Python suite verifies:

1. Stable rig configuration hashing.
2. Missing calibration rejection.
3. Stale configuration rejection.
4. Valid plan validation.
5. Normal deterministic completion.
6. Deterministic pressure abort.
7. Rejection of an unapproved plan.
8. Authenticated localhost API workflow, approval, execution, and evidence retrieval.

## Evidence location

Run "npm run evidence" to regenerate:

    evidence/phase2/normal.json
    evidence/phase2/swapped.json
    evidence/phase2/missingCalibration.json
    evidence/phase2/safetyLimit.json
    evidence/phase2/manifest.json

All values are generated from synthetic Phase 2 inputs. Physical hardware results must not be added to this matrix until they have been measured.

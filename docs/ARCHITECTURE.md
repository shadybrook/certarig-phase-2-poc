# Architecture and data flow

## Architecture

The browser interface is the human review layer. It displays the system map, evidence confidence, bounded plan, telemetry, alarms, and exportable evidence. The reasoning layer contains discovery, rig model, experiment, and diagnosis responsibilities.

The deterministic runtime owns state transitions, timeout behaviour, abort behaviour, and replay. The versioned evidence bundle retains the rig graph, plans, telemetry, decisions, and source references. The safety policy remains independent of reasoning and defines the pressure limit, safe output state, and control authority.

## Data flow

1. Ingest configuration, calibration, procedure, and telemetry records.
2. Normalize records into typed devices, channels, units, ranges, limits, and evidence references.
3. Compare the proposed rig version with the approved baseline.
4. Trace changes to invalidated evidence and assumptions.
5. Compile a bounded plan with prerequisites and abort rules.
6. Execute only through the deterministic simulator.
7. Compare expected and measured responses.
8. Accept the baseline, request review, or record a safe stop.
9. Export the evidence bundle.

## Phase 2 boundary

The proof of concept is browser based and uses synthetic data. It proves the workflow, typed model, policy logic, deterministic test cases, static software build, and evidence export. It does not prove live device discovery, controller deployment, physical actuation, sensor accuracy, or independent hardware protection.

## Supplementary implementation reference

The repository also contains a computer to Raspberry Pi software reference. It demonstrates configuration hashing, typed plan validation, human approval, deterministic execution in mock mode, and evidence persistence. This supports implementation feasibility but is not part of the Phase 2 physical validation claim.

The optional planner receives a read only snapshot and engineering constraints. It emits a typed proposal that is submitted to the same deterministic validator as a manually written plan. It cannot approve, execute, stop, call GPIO, use a shell, or change a safety limit.

Future hardware planning is deliberately separated in the future-phase-3 directory.

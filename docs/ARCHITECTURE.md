# Architecture and data flow

## Architecture

The browser interface is the human review layer. It displays the system map, evidence confidence, bounded plan, telemetry, alarms, and exportable evidence. The reasoning layer contains discovery, rig model, experiment, and diagnosis responsibilities. The deterministic runtime owns state transitions, timeout behaviour, abort behaviour, and replay. The versioned store retains the rig graph, plans, telemetry, decisions, and source references. The safety policy remains independent of reasoning and defines the pressure limit, safe output state, and control authority.

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

The proof of concept is browser based and uses synthetic data. It proves the workflow, typed model, policy logic, deterministic test cases, and evidence export. It does not prove live device discovery, controller deployment, physical actuation, or independent hardware protection. Those items remain Phase 3 work.

## Phase 3 reference stack

The engineering computer uses the CertaRig client to read snapshots, create plans, approve reviewed plans, start a supervised run, request a stop, and retrieve evidence. The optional OpenAI planner receives only a read only snapshot and engineering constraints. It emits a strict structured proposal that is submitted to the same deterministic validator as a manually written plan.

The Raspberry Pi edge service owns configuration loading, hardware access, plan validation, approval state, execution, stop behaviour, and evidence persistence. It starts and ends with the output in the safe state. The service works with either `MockHardware` or `RaspberryPiHardware` through the same interface.

The optional MCP server exposes three review tools: read the rig snapshot, propose a reviewable plan, and read a completed evidence bundle. It does not expose approval, execution, stop, GPIO, shell, or arbitrary network tools.

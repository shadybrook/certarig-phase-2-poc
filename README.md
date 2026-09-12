# CertaRig Phase 2 proof of concept

CertaRig is an evidence backed commissioning and revalidation concept for engineering test rigs. The Phase 2 build shows how a reviewer can compare a proposed rig model with an approved baseline, identify missing or conflicting evidence, run a bounded deterministic simulation, and export a traceable result.

## Submission links

| Deliverable | Link or status |
|---|---|
| Public repository | https://github.com/shadybrook/certarig-phase-2-poc |
| Live proof of concept | Deployment workflow configured; URL activates after the first successful Pages run |
| Ten minute demonstration | Pending final recording and upload |
| Submission guide | [Phase 2 submission guide](docs/PHASE2_SUBMISSION.md) |

## Run the proof of concept

Use the public live link above, or run it locally:

    python3 -m http.server 8000

Open http://localhost:8000.

Select a demonstration case, run the analysis, inspect the model, findings, plan, telemetry, and checksum, and export the JSON evidence.

## Four repeatable cases

1. Approved baseline. All mappings and records agree and the bounded simulation completes.
2. Swapped analog channels. Mapping and response signature conflicts require review.
3. Missing calibration. Material evidence is absent, so execution is blocked.
4. Pressure safety limit breach. The deterministic runtime records a safe abort.

## Architecture and data flow

The browser is the human review layer. The reasoning layer prepares the model, comparison, plan, and diagnosis. Deterministic rules own plan status, limit checks, and simulated abort behaviour. The exported evidence bundle retains the inputs, findings, result, and stable case checksum.

See:

1. [Architecture notes](docs/ARCHITECTURE.md)
2. [Rendered GitHub diagrams](docs/DIAGRAMS.md)
3. [Test matrix](docs/TEST_MATRIX.md)
4. [Ten minute demonstration script](docs/DEMO_SCRIPT.md)
5. [Dated validation record](docs/VALIDATION_RECORD.md)

## Phase 3 dry-bench progress

Phase 3 now validates the control and evidence architecture on a low-voltage dry hardware bench. The Pi, SSH, I2C, ADS1115 at `0x48`, two independent 0-3.3 V potentiometer paths, physical E-stop, transistor-driven K1 relay, red/green changeover indication, forced-safe trip and reset-required anti-restart have physical evidence. Hydraulic commissioning remains reserved for the capstone.

The Phase 3 live console adds Pi-hosted P1/P2 telemetry, E-stop state, deterministic pressure and flow guardrails, command-derived relay and red/green indication, authenticated safe/reset/permit commands, a rolling chart, and downloadable CSV evidence. Relay and lamp states are explicitly labelled as expected values because the present bench has no relay feedback sensor.

- [Phase 3 document and evidence index](docs/phase3/README.md)
- [Canonical Wave 1 wiring guide](docs/phase3/CertaRig_Wave_1_Wiring_and_Circuit_Guide_2026-09-07.pdf)
- [Dual potentiometer evidence](phase3_evidence/2026-09-10_dual_pot_sweep/README.md)
- [Next-stage E-stop SOP](docs/phase3/NEXT_STAGE_ESTOP_SOP.md)
- [Corrected relay and indicator SOP](docs/phase3/NEXT_STAGE_RELAY_OUTPUT_SOP.md)
- [Integrated bench fault-isolation evidence](phase3_evidence/2026-09-11_integrated_bench/README.md)
- [Final Phase 3 as-built circuit diagram](docs/phase3/diagrams/CertaRig_Phase3_Final_AsBuilt_Circuit.png)
- [Integrated relay, indicator and anti-restart evidence](phase3_evidence/2026-09-12_integrated_bench/README.md)
- [Phase 3 completion plan](docs/phase3/PHASE3_COMPLETION_PLAN_2026-09-12.md)
- [Phase 3 live dashboard and guardrail SOP](docs/phase3/LIVE_GUARDRAIL_DASHBOARD_SOP.md)

## Reproducible validation

Node.js 20 or later and Python 3.11 or later are recommended.

Run the entire Phase 2 validation:

    npm run check

Or run each step:

    npm test
    python3 -m unittest discover -s tests_py -v
    npm run build
    npm run evidence

The repository contains six browser tests and thirty supplementary reference software tests. GitHub Actions runs both suites after each published change. The website workflow publishes only the tested static files in the dist directory.

Generated case evidence is stored in evidence/phase2. The evidence is deterministic, synthetic, and reproducible from src/engine.mjs.

## Supplementary implementation reference

The certarig_edge package demonstrates how the same approval and evidence contract can be represented through a local computer to Raspberry Pi API. It includes configuration hashing, deterministic validation, human approval, safe mock execution, evidence storage, and a hardware adapter boundary.

This code is supplementary implementation evidence, not a physical Phase 2 result. The tested claim is limited to computer based mock mode. See the [reference API contract](docs/API_CONTRACT.md).

## Phase 2 validation boundary

The Phase 2 proof of concept uses synthetic data. It proves the workflow, repeatable decision rules, bounded simulator behaviour, software tests, static build, and evidence export. It does not prove live sensor accuracy, actuator performance, a pressure boundary, emergency stop performance, electrical protection, or industrial readiness.

Raspberry Pi GPIO must never directly drive a relay coil, solenoid, miniature circuit breaker, mains circuit, motor starter, or industrial load.

Future Phase 3 planning is deliberately separated in [future-phase-3](future-phase-3/README.md) and is not part of the Phase 2 validation claim.

## Repository structure

    index.html                 Phase 2 browser proof of concept
    styles.css                 Browser presentation
    src/                       Browser logic and deterministic case engine
    tests/                     Browser acceptance tests
    evidence/phase2/           Generated synthetic evidence bundles
    docs/                      Phase 2 submission and technical documentation
    scripts/                   Static build and evidence generation
    .github/workflows/         Automated tests and GitHub Pages publishing
    certarig_edge/             Supplementary reference implementation
    tests_py/                  Reference implementation tests
    future-phase-3/            Historical Phase 3 planning baseline
    phase3_evidence/           Curated physical dry-bench evidence
    docs/phase3/               Phase 3 wiring, inventory and SOP documents

## Student

Chintan Dedhia  
Student ID 2023EB03005

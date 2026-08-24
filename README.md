# CertaRig Phase 2 Proof of Concept

CertaRig is a browser based engineering simulator that demonstrates an evidence backed commissioning and revalidation loop for a small pressure and flow rig.

The Phase 2 proof of concept separates AI assisted reasoning from deterministic execution. It does not connect to or control physical hardware. The browser shows the proposed rig model, evidence confidence, a bounded plan, simulated telemetry, diagnostic findings, and the final evidence bundle.

## Demonstrated cases

1. Approved baseline. All mappings and records agree and the bounded valve response test completes.
2. Swapped analog channels. The system detects mapping and response signature conflicts and asks for review.
3. Missing calibration. The system stops before execution because material evidence is missing.
4. Pressure safety limit breach. The deterministic runtime records a safe abort.

## Run locally

Use any static web server from the repository root. For example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Run tests

Node.js 20 or later is required.

```bash
npm test
```

The tests cover all four demonstration cases and the evidence bundle contract.

## Repository structure

```text
index.html              Browser interface
styles.css              Responsive visual system
src/engine.mjs          Rig model, change detection, policy, simulation, diagnosis
src/app.mjs             Interface rendering and evidence export
tests/engine.test.mjs   Automated acceptance tests
docs/                   Architecture notes and demonstration guide
```

## Safety boundary

This project is a synthetic teaching prototype. It has no live DAQ, controller, actuator, or industrial network connection. Deterministic policy checks and the safe default state remain authoritative in the model. Any future physical work must retain independent hardware protection and human approval.

## Student

Chintan Dedhia  
Student ID 2023EB03005

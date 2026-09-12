# CertaRig Ten Minute Demonstration Script

Before recording, confirm that the repository is available at https://github.com/shadybrook/certarig-phase-2-poc and replace the video placeholder in the Phase 2 report after upload.

## 0:00 to 0:35 | Introduction

Hello, I am Chintan Dedhia. This demonstration presents CertaRig, a controlled workflow for commissioning and validating a small pressure and flow rig. Phase 2 establishes the architecture and browser proof of concept. I have also built a supplementary implementation reference so the same safety and evidence contract can run on a computer and communicate with a Raspberry Pi.

## 0:35 to 1:15 | User Community and Benefits

The main users are commissioning engineers, laboratory technicians, project supervisors, and auditors. CertaRig helps them compare an intended rig model with the actual configuration, identify missing evidence before a run, execute an approved test consistently, and retain a reviewable record. It reduces avoidable wiring, range, calibration, and documentation errors while keeping the operator responsible for physical approval.

## 1:15 to 2:10 | Architecture Diagram

The computer is the engineering and review station. It can inspect the current rig snapshot and prepare a typed test proposal. An optional OpenAI planner may help draft that proposal, but it cannot approve it, execute it, call GPIO, or change a safety limit.

The Raspberry Pi hosts a small authenticated edge API. It loads the approved configuration, checks calibration and range evidence, creates a configuration hash, validates the plan deterministically, and waits for a separate operator approval. Only then can the deterministic executor call the hardware adapter. The physical system still requires independent electrical protection, a relief path, an emergency stop, and correctly rated isolated interfaces.

## 2:10 to 2:55 | Data Flow Diagram

The data flow begins with configuration and calibration evidence. CertaRig normalizes the values and produces a stable configuration hash. The computer requests a read only snapshot and submits a proposed plan. The edge validator checks the schema, ranges, durations, calibration status, and expected configuration hash. A human operator then approves the exact plan. During execution, the edge service samples the sensors, applies deterministic stop conditions, returns the output to a safe state, and stores the run in SQLite with an evidence checksum.

## 2:55 to 3:50 | Supplementary Implementation Code

The repository now contains more than the browser simulation. The certarig_edge package includes the HTTP API, configuration loader, safety validator, deterministic executor, evidence store, client, optional structured AI planner, and optional MCP review tools. The hardware folder includes a mock adapter for repeatable tests and a Raspberry Pi adapter for GPIO plus an ADS1115 analogue converter. The same executor contract is used for both adapters, which allows software checks to run before any physical output is enabled.

The optional MCP server exposes only snapshot, proposal, and evidence review operations. It intentionally provides no approval, execution, stop, GPIO, shell, or unrestricted network tool.

## 3:50 to 4:40 | Computer to Raspberry Pi Workflow

On the Raspberry Pi I copy the example configuration, set a strong operator key, and start the edge service:

    export CERTARIG_OPERATOR_KEY='replace-with-a-strong-key'
    python3 -m certarig_edge.cli serve --bind 127.0.0.1 --port 8765

From a computer I can inspect the rig and exercise the complete API workflow against the safe mock adapter:

    python3 -m certarig_edge.cli demo --url http://raspberrypi.local:8765
    python3 -m certarig_edge.cli demo --url http://raspberrypi.local:8765 --execute

The service binds to localhost by default. Remote use should be limited to a private network, VPN, or authenticated reverse proxy.

## 4:40 to 6:55 | Four Test Cases

Case one is the approved baseline. All channels are mapped, the calibration evidence is present, the plan matches the configuration hash, and the simulated run completes. The valve command returns to its normally closed safe state.

Case two swaps the pressure and flow channels. The comparison identifies the mapping conflict and prevents execution until the configuration is corrected.

Case three removes required calibration evidence. Validation rejects the plan before approval because a test result would not be defensible without traceable calibration.

Case four introduces a pressure limit breach. The deterministic executor detects the value above the approved 4.2 bar limit, closes the output, records a safe abort, and writes the reason into the evidence record.

These cases demonstrate a deliberate separation: an AI system may help represent intent, but deterministic code decides whether the proposal is valid and the operator decides whether it may run.

## 6:55 to 7:50 | Agent Guardrails

The optional OpenAI integration uses the Responses API with a typed JSON schema. Its output is treated only as an untrusted proposal. The edge service independently checks every submitted field and does not accept an AI approval. The operator key protects state changing API calls, approvals are bound to a plan and configuration hash, and a stale configuration invalidates the run. Evidence is stored after completion or abort so a reviewer can trace what happened.

## 7:50 to 8:40 | Validation Evidence

The browser engine has six automated tests. The new Python stack has eight tests, including stable configuration hashing, calibration rejection, stale configuration rejection, valid plan validation, normal completion, pressure abort, unapproved plan rejection, and a complete localhost HTTP workflow with authentication, approval, execution, and evidence retrieval.

    npm test
    python3 -m unittest discover -s tests_py -v

All fourteen automated tests pass in the current development environment. This validates the software contracts and the mock path. It does not claim that a physical sensor, actuator, emergency stop, or electrical protection circuit has already been validated.

## 8:40 to 9:30 | Readiness for Phase 3

Phase 3 proceeds in controlled stages. First, run the mock adapter on the computer and Raspberry Pi. Second, connect sensors in read only mode and compare readings with reference instruments. Third, verify GPIO only into a dummy load through a correctly rated isolated driver. Fourth, perform emergency stop, loss of power, sensor fault, stale configuration, and overpressure tests. Fifth, enable one low energy rig test under supervision. Finally, compare the physical evidence with the simulator regression baseline and document deviations.

The Raspberry Pi GPIO must never drive a relay coil, solenoid, miniature circuit breaker, mains circuit, or industrial load directly. Final wiring and component ratings require competent engineering review.

## 9:30 to 10:00 | Conclusion and Phase 3 Readiness

CertaRig now has a browser proof of concept and a hardware oriented reference software stack. The computer to Pi API, adapters, approval boundary, deterministic execution, and evidence storage are implemented and software tested. The next claim must be narrower and evidence based: physical readiness will be established only after calibration, electrical safety, fault injection, and supervised hardware tests are completed. This provides a clear and defensible path from Phase 2 into Phase 3.

## After Recording

Upload the video, confirm that it is viewable, paste the final URL into the Phase 2 report, and verify the GitHub link from a signed out browser.

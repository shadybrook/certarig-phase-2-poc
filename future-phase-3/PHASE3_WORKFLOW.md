# Phase 3 workflow and final hardware execution

> Future work only. This document is deliberately separated from the Phase 2 submission.

## Goal

Phase 3 turns the Phase 2 proof of concept into a supervised commissioning stack that can run on a computer and a Raspberry Pi. The software keeps AI reasoning outside the physical output path. The AI layer may interpret evidence and propose a typed plan. A deterministic edge service validates the plan, requires human approval, enforces limits, records every transition, and owns stop and abort behaviour.

## System boundary

The reference stack has four boundaries:

1. The engineering computer stores approved configuration, requests snapshots, reviews evidence, and may call an AI planner.
2. The Raspberry Pi edge service reads sensors, applies deterministic policy, executes approved steps, and writes an append only evidence record.
3. The hardware abstraction layer maps the same domain contract to mock hardware or configured Raspberry Pi interfaces.
4. Independent electrical protection remains outside software. It includes a normally closed output philosophy, fuse, isolation, relief path, emergency stop, and a protected driver selected for the actual load.

The first implementation supports low voltage demonstration hardware only. It must not switch mains power, an MCB, a motor starter, or an industrial load directly from a Raspberry Pi GPIO pin.

## Phase 3 delivery workflow

### Stage 1: Configuration and evidence contract

Define the rig, sensor channels, units, calibration identifiers, valid ranges, safe ranges, GPIO mapping, ADC mapping, and output safe state in one reviewed JSON configuration. Calculate a configuration hash and place it in every plan, approval, run, and evidence bundle.

Acceptance gate:

* Configuration loads against the schema.
* Every material sensor has a unit, calibration identifier, conversion mapping, valid range, and safe range.
* The output safe state is closed or deenergized.
* The configuration hash is stable and visible.

### Stage 2: Laptop mock mode

Run the edge API with deterministic mock sensors and a mock valve. Exercise the complete API flow from a second process on the same computer.

Acceptance gate:

* Health and snapshot endpoints respond.
* Missing calibration blocks a plan.
* A valid plan can be created and reviewed.
* Approval requires the operator key.
* Actuation remains disabled unless explicitly enabled.
* A normal case completes and a pressure breach closes the valve and records an abort.

### Stage 3: Raspberry Pi read only commissioning

Install the service on the Pi and select the Raspberry Pi hardware adapter. Keep actuation disabled. Read ADC channels, digital inputs, emergency stop state, and optional relay feedback while the real rig remains deenergized.

Acceptance gate:

* Channel identity is verified one sensor at a time.
* Raw values and engineering values are recorded together.
* Zero and reference points agree with independent instruments.
* Calibration identifiers match the installed sensors.
* Disconnect, short, out of range, stale sample, and emergency stop cases are detected.

### Stage 4: Supervised low energy output test

Connect only a protected low voltage demonstration load. Keep the process medium isolated. Enable physical output through an explicit environment setting and require a human approval receipt for each plan.

Acceptance gate:

* Output starts in the safe state after boot and after service restart.
* Missing approval prevents execution.
* Lost heartbeat, emergency stop, sensor fault, timeout, and limit breach return the output to the safe state.
* Relay or driver feedback agrees with the command when feedback is available.
* Every event is present in the SQLite evidence record.

### Stage 5: Integrated pressure and flow testbed

Assemble the low energy pressure and flow rig with reviewed components. Perform a dry checklist, leak check, sensor check, output check, and relief path check before any automated plan.

Acceptance gate:

* A qualified reviewer approves the wiring and pressure boundary.
* Independent emergency stop and relief behaviour are tested before software control.
* The approved baseline case completes within tolerance.
* Swapped channel, missing calibration, disconnected sensor, stale sample, and pressure breach cases produce the expected stop or abort evidence.
* The report identifies the exact hardware, firmware, configuration hash, software commit, calibration records, and reviewer.

### Stage 6: Final demonstration and Phase 3 report

Record the complete path from configuration evidence to snapshot, plan proposal, deterministic validation, human approval, supervised execution, diagnosis, and exported evidence. Show the AI boundary explicitly and state which results came from mock mode and which came from physical hardware.

## Final hardware run sequence

1. Confirm that the emergency stop, fuse, relief path, isolation, and output driver are physically present and independently tested.
2. Confirm that the output is deenergized and the Raspberry Pi boots into the safe state.
3. Record the rig configuration hash, software commit, Pi identity, sensor serials, calibration identifiers, and reviewer.
4. Read a snapshot with actuation disabled and compare each channel against an independent reference.
5. Create a bounded plan that names the expected response, timeout, sample interval, pressure limit, and abort conditions.
6. Review the plan and issue a single approval receipt.
7. Enable the low energy output path and start the run from the engineering computer.
8. Observe live evidence while the Pi applies deterministic limits and heartbeat checks.
9. Return to the safe state, export the evidence bundle, and verify the checksum.
10. Review deviations before accepting a new baseline. Never approve a baseline automatically.

## Agent guardrails

The optional agent layer follows these rules:

* It receives read only snapshots and approved engineering constraints.
* It emits a strict structured plan proposal.
* It has no GPIO, approval, run, stop, shell, or arbitrary network tool.
* Server side validation rejects missing evidence, unknown channels, unsafe limits, and stale configuration hashes.
* A human approval is required before any physical side effect.
* The Raspberry Pi service remains safe when the AI service, network, or engineering computer is unavailable.

## What can be claimed now

The repository can claim that the core domain rules, mock hardware, HTTP API, approval gate, evidence store, client, and abort behaviour are tested on a computer. It can claim Raspberry Pi compatibility at the adapter and deployment level. It cannot claim validation against a specific sensor, ADC, relay, valve, pressure boundary, or industrial installation until the documented hardware protocol has been executed on that equipment.

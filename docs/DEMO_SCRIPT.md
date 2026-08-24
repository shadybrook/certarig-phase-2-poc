# Ten minute proof of concept demonstration

## 0:00 to 0:40 Introduction

Introduce CertaRig as a system for commissioning and revalidating changed engineering test rigs. State that the Phase 2 proof of concept uses a synthetic pressure and flow rig and has no live hardware control.

## 0:40 to 1:30 User community

Describe the three primary groups: test engineers, instrumentation engineers, and project reviewers. Explain that each group needs traceable mappings, explicit uncertainty, and a repeatable evidence record.

## 1:30 to 2:15 Benefits

Explain the four benefits shown in the interface: less repeated work, visible uncertainty, safe deterministic execution, and an audit ready evidence bundle.

## 2:15 to 3:20 Architecture

Walk through the browser review layer, the discovery and modelling responsibilities, the experiment and diagnosis responsibilities, the versioned evidence store, and the deterministic runtime. Emphasize that the safety policy remains authoritative and separate from AI reasoning.

## 3:20 to 4:10 Data flow

Follow the six visible stages from ingest to report. Explain how configuration and calibration evidence becomes a typed rig graph, how versions are compared, how the bounded plan is compiled, and how the final outcome is linked to measured data.

## 4:10 to 5:10 Case 1: Approved baseline

Run the approved baseline. Point out the four mapped channels, high model confidence, zero material findings, telemetry response, completed plan, and evidence checksum.

## 5:10 to 6:20 Case 2: Swapped analog channels

Select the swapped channel case. Show that the pressure and flow labels conflict with the approved baseline and measured signatures. Explain why the system asks for wiring confirmation instead of accepting the new model.

## 6:20 to 7:25 Case 3: Missing calibration

Select the missing calibration case. Show the reduced confidence and the blocked plan. Explain that missing material evidence is a stop condition, so no bounded test is started.

## 7:25 to 8:35 Case 4: Pressure safety limit breach

Select the safety limit case. Point out the pressure trace crossing 4.2 bar, the safe abort outcome, and the recorded finding. Explain that the deterministic runtime, not an AI decision, owns the abort rule.

## 8:35 to 9:20 Testing and evidence

Mention that automated tests cover all four cases and that the exported JSON contains the input versions, findings, plan states, telemetry, and evidence checksum. Show the test command and result if time permits.

## 9:20 to 10:00 Conclusion and Phase 3 readiness

Conclude that Phase 2 demonstrates the core reasoning and evidence loop with repeatable cases. State that Phase 3 should add file ingestion, persistent storage, authenticated review, one approved controller adapter, sandboxed code validation, and a low energy hardware testbed with independent safety hardware.

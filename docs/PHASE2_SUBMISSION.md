# Phase 2 submission guide

## Submission identity

Project: CertaRig

Student: Chintan Dedhia

Student ID: 2023EB03005

Repository: https://github.com/shadybrook/certarig-phase-2-poc

Live proof of concept: deployment workflow configured; confirm the final URL after its first successful Pages run

## Requirement traceability

| Requirement supplied by the professor | Phase 2 evidence |
|---|---|
| Ten minute proof of concept video | Final video link will be inserted after recording and editing |
| GitHub link for the proof of concept | Public repository link above |
| Links pasted into the Phase 2 report | GitHub link is present; final video link remains pending |
| Introduction | Video script section 0:00 to 0:35 |
| User community and benefits | Website sections and video script section 0:35 to 1:15 |
| Architecture diagram | Website architecture section and docs/DIAGRAMS.md |
| Data flow diagram | Website data flow section and docs/DIAGRAMS.md |
| Proof of concept demonstration | Public website with four selectable cases |
| Three or four test cases | Four repeatable cases with generated JSON evidence |
| Conclusion and readiness for Phase 3 | Final video section, with physical validation clearly excluded from Phase 2 |

## What Phase 2 proves

The browser proof of concept demonstrates a traceable workflow from configuration and calibration evidence to a typed rig model, deterministic policy evaluation, a bounded commissioning plan, simulated telemetry, diagnosis, and an exportable evidence bundle.

The build includes four repeatable cases:

1. Approved baseline.
2. Swapped pressure and flow channels.
3. Missing calibration evidence.
4. Pressure limit breach with a safe abort outcome.

## Validation evidence

Run the complete local validation:

    npm run check

This command runs six browser engine tests, eight reference software tests, the static website build, and deterministic generation of the four Phase 2 evidence bundles.

GitHub Actions is configured to repeat the tests and website build after every published change. GitHub Pages is configured to publish the tested static artifact from the default branch. The dated local result is recorded in docs/VALIDATION_RECORD.md.

## Submission boundary

The Phase 2 proof of concept uses synthetic data. It validates the workflow, software rules, repeatable cases, evidence export, and presentation layer. It does not validate a physical pressure boundary, sensor, ADC, driver, valve, emergency stop, or independent protection circuit.

The repository contains supplementary computer to Raspberry Pi reference software to demonstrate implementation feasibility. That code is software tested in mock mode and is not evidence of physical hardware validation. Phase 3 planning and physical test requirements are kept in the separate future-phase-3 directory.

## Final checks after the video is ready

1. Upload the final video and confirm that the intended audience can open it.
2. Replace the pending video entry in this guide and the repository README.
3. Insert both the GitHub and video URLs into the Phase 2 report.
4. Open the repository, live proof of concept, and video from a signed out browser.
5. Export the final Phase 2 report and verify every page visually.
6. Send the professor email only after all three deliverables open correctly.

# CertaRig Phase 3 dry-bench index

Phase 3 validates the CertaRig control and evidence architecture on a low-voltage dry hardware bench. Hydraulic commissioning, water, pumps, mains loads and pressure-bearing claims remain outside this phase and are reserved for the capstone.

## Current verified status

- Raspberry Pi 3 Model A+ boot, SSH and I2C commissioning passed.
- ADS1115 was detected repeatedly at address `0x48`.
- P1 on A0 and P2 on A1 were acquired together at approximately 10 Hz.
- The paired run contains 4,457 complete samples. A0 covered 0-3.302 V and A1 covered 0-3.300 V.
- The fail-safe E-stop software polarity is explicit and tested: GPIO24 LOW is healthy; HIGH/open is active.
- Relay feedback is disabled for the initial bench and physical pin 22 remains disconnected.
- The 11 September isolation test found that relay lower/control COM must not be connected to Pi 3.3 V. Physical pin 17 now supplies only P1 and P2.
- The 12 September integrated test passed the transistor-controlled K1 permit/safe sequence, three repeatability cycles, E-stop forced-safe response and reset-required anti-restart. The optional broken-wire injection was not performed and is not claimed as a pass.
- The final submission diagram now records the tested single-rail as-built circuit: pin 17 supplies only P1/P2, relay lower/control COM has no external wire, K1 contact COM is supplied from fused 5 V before NC2, and the inhibited indicator is red.

## Controlled documents

- [Wave 1 wiring guide, PDF](CertaRig_Wave_1_Wiring_and_Circuit_Guide_2026-09-07.pdf)
- [Wave 1 wiring guide, editable DOCX](CertaRig_Wave_1_Wiring_and_Circuit_Guide_2026-09-07.docx)
- [Hardware inventory register, PDF](CertaRig_Phase_3_Hardware_Inventory_Register_2026-09-06.pdf)
- [Hardware inventory register, Markdown](CertaRig_Phase_3_Hardware_Inventory_Register_2026-09-06.md)
- [Wave 1 commissioning plan](CertaRig_Wave_1_Commissioning_2026-09-07.md)
- [Pi pre-wiring evidence](CertaRig_Phase3_Pi_PreWiring_Evidence_2026-09-08.md)
- [Next-stage E-stop SOP](NEXT_STAGE_ESTOP_SOP.md)
- [Next-stage relay and indicator SOP](NEXT_STAGE_RELAY_OUTPUT_SOP.md)
- [Integrated bench pre-power review and evidence plan](INTEGRATED_BENCH_PREPOWER_AND_TEST_PLAN_2026-09-11.md)
- [Single-rail relay wiring diagram](diagrams/CertaRig_Relay_Output_Single_Rail_Wiring.svg)
- [Final as-built circuit diagram, PNG](diagrams/CertaRig_Phase3_Final_AsBuilt_Circuit.png)
- [Final as-built circuit diagram, editable SVG](diagrams/CertaRig_Phase3_Final_AsBuilt_Circuit.svg)
- [Final as-built circuit diagram, PDF](diagrams/CertaRig_Phase3_Final_AsBuilt_Circuit.pdf)

The relay-output SOP revision 1.2 is the controlled Phase 3 instruction for the indicator-only output stage. Its fused single-rail 5 V arrangement and measured lower-COM correction supersede the corresponding relay-control assumptions in the 7 September wiring guide. It must not be used for motors, servos, pumps, valves, mains voltage or capstone hydraulic hardware.

## Physical evidence

- [ADS1115 commissioning](../../phase3_evidence/2026-09-09_ads1115_commissioning/README.md)
- [P1 as-built photograph](../../phase3_evidence/2026-09-09_p1_potentiometer/README.md)
- [P1 functional sweep](../../phase3_evidence/2026-09-09_p1_sweep/README.md)
- [Dual P1/P2 sweep](../../phase3_evidence/2026-09-10_dual_pot_sweep/README.md)
- [Physical E-stop GPIO24 test](../../phase3_evidence/2026-09-10_estop/README.md)
- [Integrated bench pre-power evidence](../../phase3_evidence/2026-09-11_integrated_bench/README.md)
- [Integrated relay, indicator and anti-restart evidence](../../phase3_evidence/2026-09-12_integrated_bench/README.md)
- [Phase 3 completion plan](PHASE3_COMPLETION_PLAN_2026-09-12.md)

## Canonical physical pins

| Function | Raspberry Pi physical pin | BCM name |
|---|---:|---|
| ADS VDD | 1 | 3V3 |
| ADS SDA | 3 | GPIO2 / SDA1 |
| ADS SCL | 5 | GPIO3 / SCL1 |
| ADS GND | 6 | GND |
| P2 ground | 9 | GND |
| P1 ground | 14 | GND |
| Future relay command | 16 | GPIO23 |
| Potentiometer 3.3 V splitter | 17 | 3V3 |
| E-stop sense | 18 | GPIO24 |
| E-stop ground | 20 | GND |
| Feedback, disabled | 22 | GPIO25 |

Physical pin 16 is GPIO23 and is never a ground connection. GPIO inputs and ADS inputs must never receive 5 V.

## Reproducibility

The generator scripts are in `tools/`. The dedicated hardware configuration is [`config/rig.wave1.json`](../../config/rig.wave1.json). Run the complete software validation with:

```bash
npm run check
```

Raw network identifiers, credentials, Wi-Fi setup screenshots and unredacted SSH transcripts are intentionally excluded from this public repository.

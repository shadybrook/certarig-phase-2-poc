# CertaRig integrated bench evidence - 11 September 2026

Current result: **HOLD - pre-power meter acceptance incomplete**

Operator update on 11 September 2026: `K1 NO` is reported connected to breadboard `F14`. This resolves the previously missing connection in the reported topology, but acceptance remains on HOLD pending an updated photograph and the U21-U23 meter checks added to the register.

First reported meter batch at 16:35 IST: K1 COM-NO was `OL`; K1 NO-F14 was reported as `0.4`; K1 COM-NC was reported as `12 ohm`; the two resistor-path readings were reported as `0.9` and `0.4` without displayed units; and the FUSED_5V-to-ground result could not be determined. The latter results are failed or inconclusive, so no power authorization was issued. Both potentiometers are to remain at their zero/off positions through Gate 1.

## Scope

This folder retains the as-built photo set and will receive the unpowered meter register, SSH transcripts, integrated CSV, plots, truth tables, and test-case result after the controlled commissioning gates pass.

The photographs show physical assembly but do not prove continuity, polarity, terminal identity, or safe energization. The inspection and test plan is [`docs/phase3/INTEGRATED_BENCH_PREPOWER_AND_TEST_PLAN_2026-09-11.md`](../../docs/phase3/INTEGRATED_BENCH_PREPOWER_AND_TEST_PLAN_2026-09-11.md).

## Source-photo mapping

| Evidence copy | User-supplied source | Source SHA-256 | Evidence-copy SHA-256 |
|---|---|---|---|
| `01_overall_bench.jpg` | `IMG_1909.HEIC` | `8f91cc7cf69aa6954ea8376d36fbc8abc9debc354e7c1d5b43b4e9e481bd693b` | `31643bf4fab38949f5caed85974d9e84b5b2e11afafb75a240f4e5718125b50f` |
| `02_relay_breadboard_pi_overview.jpg` | `IMG_1896.HEIC` | `a232c6869a91c16a351ae54a9f0a9c84d7a21ac332312399f3a655e1b0aeb041` | `202798090ab83bbab5e0bcdf1a0d135dd0bd5a00539772d41de3b50264888b0c` |
| `03_pi_ads1115_potentiometers.jpg` | `IMG_1900.HEIC` | `3597daf0a08f0189f3749a96a44085ad487ef5df1d65440dbf6fb3d4eab4bc43` | `0fbad297888e540b7703dc7d4595e92d7b51a122475ff62edcd1d75e46e2102d` |
| `04_estop_fuse_breadboard.jpg` | `IMG_1901.HEIC` | `5d533f7702bf8d9d21d6706454674156112726d204642e3b19d189135c509fb7` | `a021a50f5f8c9986a57c2b15f0a192a2fd8329dafb27237acacd6b6da712131f` |
| `05_relay_and_breadboard_closeup.jpg` | `IMG_1903.HEIC` | `b4eae33424af269a07d67324a7fe94fea673f115ef1b989f29dacbda48273741` | `84d66f6d1cd03a5f24ea187231b7b59a57f2455b82296d0a0e3eebd0d71f60f6` |

## Review finding

Only two wires are clearly visible on one three-screw relay contact group. The inhibited/permitted changeover requires measured K1 COM, NC, and NO connections. This and every other Gate 0 reading must be resolved before the circuit is powered.

The inhibited indicator is red in this build. Earlier references to yellow describe the same safe/inhibited function and were updated in the controlled relay SOP and diagram.

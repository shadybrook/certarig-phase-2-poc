# CertaRig Phase 2 PoC and Phase 3 hardware reference stack

CertaRig is an evidence backed commissioning and revalidation system for engineering test rigs. The repository contains the Phase 2 browser proof of concept and the first Phase 3 hardware ready reference implementation.

The Phase 3 code can run in deterministic mock mode on a computer or use configured Raspberry Pi GPIO and ADS1115 inputs. An engineering computer communicates with the Pi through a JSON HTTP API. The optional AI planner may propose a strict typed plan, but it cannot approve a plan, execute a plan, call GPIO, or change a safety limit.

## Demonstrated cases

1. Approved baseline. All mappings and records agree and the bounded valve response test completes.
2. Swapped analog channels. The system detects mapping and response signature conflicts and asks for review.
3. Missing calibration. The system stops before execution because material evidence is missing.
4. Pressure safety limit breach. The deterministic runtime records a safe abort.

## Phase 3 capabilities

* Raspberry Pi edge service with an explicit safe state.
* Computer to Pi JSON HTTP client.
* Operator authentication and human approval gate.
* Mock and Raspberry Pi hardware adapters behind one interface.
* ADS1115 sensor acquisition with engineering unit scaling.
* Deterministic plan validation, execution, stop, and abort rules.
* SQLite evidence records with a stable checksum.
* Optional OpenAI structured plan proposer.
* Optional MCP review server with read and proposal tools only.

## Run the Phase 2 browser PoC

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`.

## Run the Phase 3 edge API in mock mode

The core edge service uses only the Python standard library.

```bash
export CERTARIG_OPERATOR_KEY='replace-with-a-long-random-key'
python3 -m certarig_edge.cli serve \
  --config config/rig.example.json \
  --database certarig-evidence.sqlite3
```

In a second terminal, create a reviewable plan without executing it:

```bash
python3 -m certarig_edge.cli demo
```

Run the complete mock approval and execution flow:

```bash
export CERTARIG_OPERATOR_KEY='replace-with-a-long-random-key'
python3 -m certarig_edge.cli demo --execute
```

The service binds to `127.0.0.1` by default. Use a private network or VPN and an authenticated reverse proxy before exposing it beyond one machine.

## Run on a Raspberry Pi

1. Copy `config/rig.example.json` and change `hardware.mode` to `raspberry_pi`.
2. Review the GPIO pins, ADS1115 address, channel scaling, sensor ranges, calibration identifiers, and safe limits.
3. Install the Pi dependencies with `python3 -m pip install -e '.[pi]'`.
4. Keep `CERTARIG_ENABLE_ACTUATION=0` during read only commissioning.
5. Start the service and verify every sensor against an independent reference.
6. Enable physical output only for a reviewed low voltage testbed with independent electrical protection.

The Raspberry Pi must not drive an MCB, mains load, industrial valve, motor starter, or other hazardous load directly. Use a correctly rated isolated driver, normally safe output state, fuse, emergency stop, and process protection selected by a qualified person.

See [Phase 3 workflow](docs/PHASE3_WORKFLOW.md) and [Raspberry Pi integration](docs/RASPBERRY_PI.md).

## Optional OpenAI planner and MCP review tools

Install the optional dependencies on the engineering computer:

```bash
python3 -m pip install -e '.[agent]'
export OPENAI_API_KEY='your-key'
```

`certarig_edge.agent.propose_plan_with_openai` uses Structured Outputs to produce a typed plan proposal. Deterministic server validation and human approval still apply. `python3 -m certarig_edge.mcp_server` exposes snapshot, plan proposal, and evidence retrieval tools. It intentionally exposes no approval, execution, stop, GPIO, shell, or arbitrary network tool.

## Run tests

Node.js 20 or later is required for the browser suite.

```bash
npm test
python3 -m unittest discover -s tests_py -v
```

Both suites use built in test runners and the core tests require no external dependency.

## Repository structure

```text
index.html                 Browser PoC
src/                       Browser reasoning and display logic
certarig_edge/             Phase 3 edge API, client, safety, evidence, and adapters
config/                    Reviewed rig configuration examples
tests/                     Browser acceptance tests
tests_py/                  Hardware stack and HTTP API tests
systemd/                   Raspberry Pi service example
docs/                      Architecture, workflow, hardware, and demo guidance
```

## Validation boundary

The browser PoC and automated hardware tests use synthetic data. The Raspberry Pi adapter is implementation ready but has not been validated against a specific sensor, ADC, driver, valve, pressure boundary, or industrial installation. Physical validation must follow the documented staged protocol. AI assisted reasoning remains outside deterministic execution and independent safety paths.

## Student

Chintan Dedhia  
Student ID 2023EB03005

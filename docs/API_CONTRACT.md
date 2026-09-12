# Supplementary reference API contract

## Scope

This JSON HTTP interface demonstrates how the CertaRig software contract can be moved from the browser proof of concept to a computer and Raspberry Pi arrangement. It is supplementary Phase 2 implementation evidence. The tested mock workflow does not establish physical hardware validation.

Default development address: http://127.0.0.1:8080

Content type: application/json

State changing authentication header: X-CertaRig-Operator-Key

The operator key must contain at least twelve characters. It must be provided through an environment variable and must never be committed.

## Read operations

### GET /health

Returns service status, rig identity, configuration hash, hardware mode, actuation state, pressure limit, and safe output state.

### GET /v1/snapshot

Returns the rig identity, configuration hash, emergency stop state, safe output state, captured sensor samples, and timestamp.

### GET /v1/plans/{plan_id}

Returns one existing typed plan, its validation findings, and its state.

### GET /v1/runs/{run_id}/evidence

Returns the stored run, ordered evidence events, and checksum.

## State changing operations

### POST /v1/plans

Creates and deterministically validates a plan.

Example request:

~~~~json
{
  "rig_id": "certarig-demo-01",
  "config_hash": "hash returned by the snapshot",
  "purpose": "Bounded valve response test",
  "pressure_limit_bar": 4.2,
  "steps": [
    {
      "action": "observe_safe_state",
      "duration_ms": 500,
      "valve_open": false
    }
  ]
}
~~~~

A valid request returns 201. Validation failures return an error and do not approve or execute the plan.

### POST /v1/plans/{plan_id}/approve

Requires the operator key. Approves only a validated plan tied to the current configuration hash.

~~~~json
{
  "operator": "reviewer name"
}
~~~~

### POST /v1/runs

Requires the operator key, an approved plan, and the exact confirmation phrase:

~~~~json
{
  "plan_id": "plan identifier",
  "confirmation": "I understand this can energize configured output"
}
~~~~

### POST /v1/stop

Requires the operator key and requests the deterministic executor to stop.

## Common responses

| Status | Meaning |
|---|---|
| 200 | Successful read, approval, or stop request |
| 201 | Plan or run created |
| 400 | Invalid JSON, schema value, or confirmation |
| 401 | Missing or incorrect operator key |
| 404 | Route or resource not found |
| 409 | Invalid execution state |

All responses include Cache-Control: no-store. The reference service binds to localhost by default. Plain HTTP must not be exposed to an untrusted network.

## Authority boundary

An optional AI proposer may return a typed plan proposal. It cannot approve a plan, execute a run, request GPIO output, change a safety limit, or bypass server validation. Human approval and deterministic execution remain separate.

## Phase 3 live bench extension

Run `certarig-edge live-dashboard` to serve the existing website together with the live bench console. The extension continuously samples required channels and owns GPIO23 through a fail-safe process guardrail.

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/live/state` | Latest P1/P2, E-stop, guardrail, output model, recording state and rolling history |
| POST | `/v1/live/commands/safe` | Force GPIO23 LOW |
| POST | `/v1/live/commands/reset` | Clear a trip only while E-stop and all required channels are healthy |
| POST | `/v1/live/commands/permit` | Request output only after a successful reset |
| POST | `/v1/live/recordings/start` | Start a timestamped CSV evidence file |
| POST | `/v1/live/recordings/stop` | Close the CSV and return its SHA256 checksum |
| GET | `/v1/live/recordings/latest.csv` | Download the active or last completed CSV |

All command, recording and download routes require the operator header. The browser keeps the operator key only in the unsaved password field. Pressure above 4.2 bar, flow above 15 L/min, missing or invalid required data, E-stop activation, output-driver errors and sampling errors force a latched safe state. Returning to a safe sensor value never restarts the relay; reset and permit are required again.

The current circuit has no relay feedback input. Therefore `relay_energized_expected`, `red_indicator_expected` and `green_indicator_expected` are command/contact-model values, not independent physical measurements.

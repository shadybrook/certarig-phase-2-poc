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

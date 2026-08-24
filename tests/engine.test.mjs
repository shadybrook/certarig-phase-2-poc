import test from "node:test";
import assert from "node:assert/strict";
import { evaluateScenario, listScenarios, safetyPolicy } from "../src/engine.mjs";

test("the PoC exposes four repeatable demonstration cases", () => {
  assert.equal(listScenarios().length, 4);
});

test("approved baseline completes with no material finding", () => {
  const result = evaluateScenario("normal");
  assert.equal(result.status.key, "accepted");
  assert.equal(result.findings.length, 0);
  assert.equal(result.plan.allowedToRun, true);
});

test("swapped channels produce mapping and response conflicts", () => {
  const result = evaluateScenario("swapped");
  const codes = result.findings.map(finding => finding.code);
  assert.equal(result.status.key, "stopped");
  assert.equal(result.plan.allowedToRun, false);
  assert.ok(codes.includes("MAPPING_CHANGED"));
  assert.ok(codes.includes("SIGNATURE_CONFLICT"));
});

test("missing calibration blocks execution", () => {
  const result = evaluateScenario("missingCalibration");
  assert.equal(result.status.key, "stopped");
  assert.equal(result.plan.allowedToRun, false);
  assert.ok(result.findings.some(finding => finding.code === "CALIBRATION_MISSING"));
});

test("pressure limit breach causes a safe abort", () => {
  const result = evaluateScenario("safetyLimit");
  assert.equal(result.status.key, "aborted");
  assert.ok(result.metrics.maxPressure > safetyPolicy.pressureLimitBar);
  assert.ok(result.findings.some(finding => finding.code === "SAFE_LIMIT_EXCEEDED"));
});

test("every evidence bundle has a stable checksum", () => {
  for (const scenario of listScenarios()) {
    const result = evaluateScenario(scenario.id);
    assert.match(result.evidenceBundle.checksum, /^CERTARIG-[A-Z]+-20260824$/);
  }
});

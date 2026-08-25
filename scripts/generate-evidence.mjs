import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { evaluateScenario, listScenarios } from "../src/engine.mjs";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const destination = resolve(root, "evidence", "phase2");

await mkdir(destination, { recursive: true });

const manifest = [];
for (const scenario of listScenarios()) {
  const result = evaluateScenario(scenario.id);
  const filename = scenario.id + ".json";
  await writeFile(
    resolve(destination, filename),
    JSON.stringify(result, null, 2) + "\n",
    "utf8",
  );
  manifest.push({
    case_id: scenario.id,
    title: scenario.title,
    expected_outcome: result.status.key,
    evidence_checksum: result.evidenceBundle.checksum,
    file: filename,
  });
}

await writeFile(
  resolve(destination, "manifest.json"),
  JSON.stringify(
    {
      project: "CertaRig",
      phase: "Phase 2 proof of concept",
      generated_from: "src/engine.mjs",
      synthetic_data_only: true,
      cases: manifest,
    },
    null,
    2,
  ) + "\n",
  "utf8",
);

console.log("Generated " + manifest.length + " Phase 2 evidence bundles in evidence/phase2/");

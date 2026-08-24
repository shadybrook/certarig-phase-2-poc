import { evaluateScenario, listScenarios, safetyPolicy } from "./engine.mjs";

const select = document.querySelector("#scenario");
const runButton = document.querySelector("#run-analysis");
const exportButton = document.querySelector("#export-report");
const announcement = document.querySelector("#announcement");

for (const scenario of listScenarios()) {
  const option = document.createElement("option");
  option.value = scenario.id;
  option.textContent = scenario.title;
  select.append(option);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function chartPath(values, width, height, min, max) {
  return values
    .map((value, index) => {
      const x = 20 + index / (values.length - 1) * (width - 40);
      const y = height - 22 - (value - min) / (max - min) * (height - 44);
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function renderTelemetry(result) {
  const width = 760;
  const height = 240;
  const pressure = result.telemetry.map(row => row.pressure);
  const flow = result.telemetry.map(row => row.flow);
  const maxValue = Math.max(20, ...pressure, ...flow);
  const pressurePath = chartPath(pressure, width, height, 0, maxValue);
  const flowPath = chartPath(flow, width, height, 0, maxValue);
  const limitY = height - 22 - safetyPolicy.pressureLimitBar / maxValue * (height - 44);
  document.querySelector("#telemetry-chart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Pressure and flow telemetry for the selected case">
      <line x1="20" x2="740" y1="${limitY.toFixed(1)}" y2="${limitY.toFixed(1)}" class="limit-line" />
      <text x="24" y="${Math.max(14, limitY - 7).toFixed(1)}" class="limit-label">Pressure safety limit</text>
      <path d="${pressurePath}" class="series pressure" />
      <path d="${flowPath}" class="series flow" />
      <line x1="20" x2="740" y1="218" y2="218" class="axis" />
      <text x="22" y="235" class="axis-label">0 s</text>
      <text x="705" y="235" class="axis-label">12 s</text>
    </svg>`;
}

function renderChannels(result) {
  document.querySelector("#channel-table tbody").innerHTML = result.channels
    .map(channel => `
      <tr>
        <td><strong>${escapeHtml(channel.id)}</strong></td>
        <td>${escapeHtml(channel.device)}</td>
        <td>${escapeHtml(channel.unit)}</td>
        <td>${escapeHtml(channel.calibration ?? "Missing")}</td>
        <td><span class="confidence">${Math.round(channel.confidence * 100)}%</span></td>
      </tr>`)
    .join("");
}

function renderFindings(result) {
  const container = document.querySelector("#findings");
  if (!result.findings.length) {
    container.innerHTML = '<li class="finding success"><strong>No material conflicts</strong><span>The baseline evidence and measured response agree.</span></li>';
    return;
  }
  container.innerHTML = result.findings
    .map(finding => `
      <li class="finding ${escapeHtml(finding.severity)}">
        <strong>${escapeHtml(finding.code)}</strong>
        <span>${escapeHtml(finding.message)}</span>
      </li>`)
    .join("");
}

function renderPlan(result) {
  document.querySelector("#plan").innerHTML = result.plan.steps
    .map(step => `
      <li>
        <span class="step-id">${escapeHtml(step.id)}</span>
        <span>${escapeHtml(step.action)}</span>
        <span class="step-status ${escapeHtml(step.status.replace(" ", "_"))}">${escapeHtml(step.status)}</span>
      </li>`)
    .join("");
  document.querySelector("#abort-rule").textContent = result.plan.abortRule;
}

function renderResult(result) {
  document.querySelector("#case-title").textContent = result.title;
  document.querySelector("#case-summary").textContent = result.summary;
  const status = document.querySelector("#status");
  status.textContent = result.status.label;
  status.dataset.tone = result.status.tone;
  document.querySelector("#metric-channels").textContent = result.metrics.channels;
  document.querySelector("#metric-confidence").textContent = `${result.metrics.confidence}%`;
  document.querySelector("#metric-findings").textContent = result.metrics.findings;
  document.querySelector("#metric-pressure").textContent = `${result.metrics.maxPressure.toFixed(2)} bar`;
  document.querySelector("#bundle-checksum").textContent = result.evidenceBundle.checksum;
  document.querySelector("#bundle-records").textContent = result.evidenceBundle.records;
  renderTelemetry(result);
  renderChannels(result);
  renderFindings(result);
  renderPlan(result);
  announcement.textContent = `${result.title} complete. Outcome: ${result.status.label}.`;
  document.documentElement.dataset.scenario = result.id;
  window.certarigResult = result;
}

function downloadResult(result) {
  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `certarig-${result.id}-evidence.json`;
  link.click();
  URL.revokeObjectURL(url);
}

runButton.addEventListener("click", () => renderResult(evaluateScenario(select.value)));
select.addEventListener("change", () => renderResult(evaluateScenario(select.value)));
exportButton.addEventListener("click", () => downloadResult(window.certarigResult));

renderResult(evaluateScenario("normal"));

"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const main = $("#main");

const labels = {
  PASS: "Coincide",
  FAIL: "Discrepancia",
  REVIEW: "Revisión humana",
  UNDETERMINABLE: "Indeterminado",
};

const actions = {
  APPROVED: "Confirmado",
  REJECTED: "Rechazado",
  INFORMATION_REQUESTED: "En revisión",
  EXCEPTION_ACCEPTED: "Excepción aceptada",
  IGNORED: "Ignorado",
};

const state = {
  token: "",
  run: null,
  configs: [],
  imports: {},
  page: 0,
  filter: "",
  search: "",
  runSearch: "",
  view: "audits",
  wizardStep: 1,
  auditLabel: "",
  viewRevision: 0,
  importRevision: { shipments: 0, charges: 0 },
  matchingRevision: 0,
  matchingCheck: null,
  matchingConflicts: 0,
  mappingSource: { shipments: null, charges: null },
  mappingRevision: { shipments: 0, charges: 0 },
  mappingReadPending: { shipments: false, charges: false },
  importPending: { shipments: false, charges: false },
  agreementRevision: 0,
  agreementReadPending: false,
};

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );

const money = (value, fallback = "No determinable") => {
  if (value === null || value === undefined) return fallback;
  const [whole, fraction] = String(value).split(".");
  return (
    whole.replace(/\B(?=(\d{3})+(?!\d))/g, ".") +
    (fraction ? "," + fraction : "")
  );
};

const moneyOrStatus = (value, status) => {
  if (value === null || value === undefined) {
    if (status === "UNDETERMINABLE")
      return '<span class="status-explicit undeterminable">No determinable</span>';
    if (status === "REVIEW")
      return '<span class="status-explicit review">Requiere revisión</span>';
    return '<span class="status-explicit muted">No totalizable</span>';
  }
  return money(value);
};

const badge = (status) =>
  `<span class="badge ${status}">${labels[status]}</span>`;

function notice(text, error = false) {
  const element = $("#notice");
  if (!element) return;
  element.textContent = text;
  element.classList.toggle("error", error);
  element.hidden = false;
  clearTimeout(notice.timer);
  notice.timer = setTimeout(
    () => (element.hidden = true),
    error ? 16000 : 7000,
  );
}

async function api(url, options = {}) {
  const headers = { "X-Freight-Local": state.token, ...options.headers };
  if (options.body && !(options.body instanceof FormData))
    headers["Content-Type"] = "application/json";
  const response = await fetch(url, { ...options, headers });
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(
      "No se recibió una respuesta válida del servicio local. Verificar que siga abierto e intentar de nuevo.",
    );
  }
  if (!response.ok)
    throw new Error(
      (result.error || "No se pudo completar la operación.") +
        (result.details
          ? "\n" +
            result.details.map((d) => d.field + ": " + d.message).join("\n")
          : ""),
    );
  return result;
}

async function busy(button, callback) {
  const text = button?.textContent;
  if (button) {
    button.disabled = true;
    button.textContent = "Procesando…";
  }
  try {
    return await callback();
  } catch (error) {
    notice(
      error instanceof SyntaxError
        ? "La configuración no tiene un formato JSON válido. Revisar comillas, comas y llaves antes de volver a validar."
        : error.message,
      true,
    );
  } finally {
    if (button?.isConnected) {
      button.disabled = false;
      button.textContent = text;
    }
  }
}

const post = (url, body) =>
  api(url, {
    method: "POST",
    body:
      body instanceof FormData
        ? body
        : body === undefined
          ? undefined
          : JSON.stringify(body),
  });

function nav(view) {
  state.viewRevision += 1;
  state.view = view;
  document
    .querySelectorAll(".nav")
    .forEach((button) =>
      button.classList.toggle("active", button.dataset.view === view),
    );
}

function heading(kicker, title, description, buttons = "") {
  return `<div class="head"><div><div class="eyebrow">${kicker}</div><h1>${title}</h1><p class="muted">${description}</p></div><div class="actions">${buttons}</div></div>`;
}

/* ==========================================================================
   LISTA DE AUDITORÍAS (ENRIQUECIDA E INFORMATIVA)
   ========================================================================== */
async function showRuns() {
  nav("audits");
  const revision = state.viewRevision;
  state.run = null;
  main.innerHTML =
    heading(
      "CONTROL RESPALDADO",
      "Auditorías",
      "Cada importe, sus datos, sus reglas y una explicación comprobable.",
      `<button class="btn primary" id="new-run">＋ Nueva auditoría</button>`,
    ) +
    `<div id="runs"><p class="muted">Leyendo auditorías del equipo…</p></div>`;

  $("#new-run").onclick = showNew;
  const runs = await api("/api/runs");
  if (revision !== state.viewRevision) return;
  state.allRuns = runs;
  renderRunsList();
}

function renderRunsList() {
  const runs = state.allRuns || [];
  const container = $("#runs");
  if (!container) return;

  if (!runs.length) {
    container.innerHTML = `<div class="panel empty">
      <div class="symbol ui-fontsize-b9cba918" aria-hidden="true">▤</div>
      <h2>Del cargo a la evidencia.</h2>
      <p class="muted">Importá operaciones y liquidaciones, seleccioná el acuerdo y reconstruí el importe esperado. Todo se procesa de forma segura en este equipo.</p>
      <div class="actions centered ui-justifycontent-1025a90c">
        <button class="btn primary" id="demo">Explorar demostración ficticia</button>
      </div>
      <p class="hint">32 operaciones · 3 acuerdos distintos · 4 estados de certeza</p>
    </div>`;
    $("#demo").onclick = (event) =>
      busy(event.target, async () => {
        const result = await post("/api/demo");
        await openRun(result.run_id);
      });
    return;
  }

  if (!$("#search-runs")) {
    container.innerHTML = `
      <div class="banner info">
        <div class="ui-fontsize-0e7fe10f">ⓘ</div>
        <div>
          <strong>La certeza también se audita.</strong>
          <p class="ui-margin-b2f2f5fb">Una diferencia determinada requiere reglas y datos suficientes. La revisión humana y los casos indeterminados no representan ahorro.</p>
        </div>
      </div>
      <div class="search-toolbar">
        <input id="search-runs" type="text" placeholder="Buscar por transportista, período o identificador…" value="${esc(state.runSearch || "")}" />
        <button class="btn" id="demo">Ejecutar demostración ficticia</button>
      </div>
      <div id="runs-items" class="run-list ui-display-141abdf4"></div>
    `;

    $("#search-runs").oninput = (e) => {
      state.runSearch = e.target.value.toLocaleLowerCase("es").trim();
      renderRunsItems();
    };

    $("#demo").onclick = (event) =>
      busy(event.target, async () => {
        const result = await post("/api/demo");
        await openRun(result.run_id);
      });
  }

  renderRunsItems();
}

function renderRunsItems() {
  const runs = state.allRuns || [];
  const listContainer = $("#runs-items");
  if (!listContainer) return;

  const filteredRuns = state.runSearch
    ? runs.filter((r) =>
        r.label.toLocaleLowerCase("es").includes(state.runSearch),
      )
    : runs;

  if (!filteredRuns.length) {
    listContainer.innerHTML = `<div class="panel ui-textalign-253c882b">
      No se encontraron auditorías que coincidan con "<strong>${esc(state.runSearch)}</strong>".
    </div>`;
    return;
  }

  listContainer.innerHTML = filteredRuns
    .map((run) => {
      const s = run.summary;
      const currencies = Object.keys(s.currencies || {}).join(" / ") || "Sin moneda";
      const totalFindings = s.total_findings || 0;
      const failCount = s.counts?.FAIL || 0;
      const reviewCount = s.counts?.REVIEW || 0;
      const passCount = s.counts?.PASS || 0;
      const undCount = s.counts?.UNDETERMINABLE || 0;
      const created = new Date(run.created_at);
      const dateStr = !isNaN(created.getTime())
        ? `${created.toLocaleDateString("es-AR", { day: "numeric", month: "short" })} · ${created.toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })}`
        : "";
      const isComplete = s.import_complete !== false;

      return `
        <button class="run-card run-card-rich" data-run="${run.id}">
          <div class="run-card-top">
            <div>
              <h3 class="run-card-title">${esc(run.label)} · ${totalFindings} hallazgos</h3>
              <div class="run-card-sub">Moneda ${esc(currencies)}${dateStr ? ` · ${dateStr}` : ""}</div>
            </div>
            <span class="run-card-cta">Ver auditoría →</span>
          </div>
          <div class="run-card-bottom">
            <div class="run-card-metrics">
              ${failCount > 0 ? `<span class="run-card-pill fail">⚠ ${failCount} Discrepancia${failCount === 1 ? "" : "s"}</span>` : ""}
              ${reviewCount > 0 ? `<span class="run-card-pill review">⚡ ${reviewCount} Revisión</span>` : ""}
              <span class="run-card-pill pass">✓ ${passCount} Coinciden</span>
              ${undCount > 0 ? `<span class="run-card-pill undeterminable">? ${undCount} Indeterminados</span>` : ""}
            </div>
            <span class="${isComplete ? "import-status-ok" : "muted"}">
              ${isComplete ? "✓ Importación completa" : "⚠ Filas observadas"}
            </span>
          </div>
        </button>
      `;
    })
    .join("");

  listContainer.querySelectorAll("[data-run]").forEach(
    (button) =>
      (button.onclick = () =>
        busy(button, () => openRun(button.dataset.run))),
  );
}

/* ==========================================================================
   AUDITORÍA DETALLE / RESULTADO
   ========================================================================== */
async function openRun(id) {
  nav("audits");
  const revision = state.viewRevision;
  const run = await api("/api/runs/" + id);
  if (revision !== state.viewRevision) return;
  state.run = run;
  state.shipmentIndex = new Map(
    state.run.snapshot.shipments.map((s) => [s.id, s]),
  );
  state.chargeIndex = new Map(state.run.snapshot.charges.map((c) => [c.id, c]));
  state.page = 0;
  state.filter = "";
  state.search = "";
  renderAudit();
}

function renderAudit() {
  const run = state.run,
    summary = run.result.summary;
  const count = summary.total_findings;
  const coverage = count
    ? Math.round((100 * summary.determinable_findings) / count)
    : 0;

  main.innerHTML =
    heading(
      "AUDITORÍA / RESULTADO CONSERVADO",
      esc(run.snapshot.label),
      `${run.snapshot.shipments.length} operaciones · ${run.snapshot.charges.length} cargos aceptados · ${run.snapshot.agreements.length} acuerdos`,
      `<button class="btn" id="back">← Auditorías</button><a class="btn primary" href="/api/runs/${run.id}/export/zip">↓ Exportar paquete</a>`,
    ) +
    `<div class="banner info"><p>${run.metadata?.provenance ? `${run.metadata.provenance.checked_records} registro(s) cotejados contra archivos y formatos conservados; ${run.metadata.provenance.declared_records} aportados sin cotejo.` : "Esta auditoría histórica no registra un cotejo de datos contra originales."} La documentación completa del período requiere un control independiente.</p></div>` +
    (!summary.import_complete
      ? `<div class="banner warning">
          <div class="ui-fontsize-997b3b04">⚠</div>
          <div>
            <strong>Lote con filas rechazadas.</strong>
            <p>Se excluyeron registros que no cumplían el formato. Las ausencias o datos parciales se tratan como problemas de datos y no se confirman como discrepancia.</p>
          </div>
        </div>`
      : "") +
    Object.entries(summary.currencies)
      .map(
        ([curr, bucket]) => `
        <div class="metrics">
          <div class="metric">
            <label>FACTURADO ACEPTADO · ${esc(curr)}</label>
            <div class="value">${money(bucket.actual)}</div>
            <p>${summary.import_complete ? "Importación sin filas rechazadas" : "Lote incompleto"}</p>
          </div>
          <div class="metric accent">
            <label>COBERTURA DETERMINABLE</label>
            <div class="value">${coverage}%</div>
            <p>${summary.determinable_findings} de ${count} hallazgos · todas las monedas</p>
          </div>
          <div class="metric">
            <label>EXCESO DETERMINADO · ${esc(curr)}</label>
            <div class="value">${money(bucket.confirmed_overcharge)}</div>
            <p>Defecto determinado: ${money(bucket.confirmed_undercharge)}</p>
          </div>
          <div class="metric">
            <label>IMPORTE EN REVISIÓN · ${esc(curr)}</label>
            <div class="value">${money(bucket.review)}</div>
            <p>Indeterminado: ${money(bucket.undeterminable)}</p>
          </div>
        </div>
      `,
      )
      .join("") +
    `
    <div class="statusline">
      ${Object.entries(labels)
        .map(
          ([k, v]) =>
            `<span class="badge ${k}"><strong>${v}</strong> ${summary.counts[k] || 0}</span>`,
        )
        .join("")}
      <span class="muted ui-marginleft-f89ec43d">La diferencia determinada no equivale a ahorro ni recupero.</span>
      <button class="btn small" id="replay">Verificar reproducción</button>
    </div>

    <div class="panel table-panel">
      <div class="table-head">
        <div>
          <h2>Detalle de cargos auditados</h2>
          <p class="muted ui-margin-ebd1dbfe">Cobertura con reglas completas: ${coverage}% (${summary.determinable_findings} de ${count})</p>
        </div>
        <div class="filters">
          <input id="search" type="search" placeholder="Buscar por referencia, concepto o regla…" value="${esc(state.search)}">
          <select id="filter-status" aria-label="Filtrar por estado">
            <option value="">Todos los estados</option>
            ${Object.entries(labels)
              .map(([k, v]) => `<option value="${k}" ${state.filter === k ? "selected" : ""}>${v}</option>`)
              .join("")}
          </select>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Referencia y concepto</th>
              <th>Estado</th>
              <th class="num">Facturado</th>
              <th class="num">Esperado</th>
              <th class="num">Diferencia</th>
              <th>Resolución humana</th>
              <th>Explicación</th>
            </tr>
          </thead>
          <tbody id="findings"></tbody>
        </table>
      </div>
      <div class="pagination">
        <span id="page-label"></span>
        <div class="actions">
          <button class="btn small" id="prev">Anterior</button>
          <button class="btn small" id="next">Siguiente</button>
        </div>
      </div>
    </div>

    <div class="actions ui-margintop-04bbec5e">
      <a class="btn" href="/api/runs/${run.id}/export/xlsx">↓ Planilla operativa</a>
      <a class="btn" href="/api/runs/${run.id}/export/html" target="_blank">↓ Informe imprimible</a>
      <a class="btn" href="/api/runs/${run.id}/export/canonical" target="_blank">Exportar JSON canónico</a>
    </div>
  `;

  $("#back").onclick = showRuns;
  $("#filter-status").onchange = (e) => {
    state.filter = e.target.value;
    state.page = 0;
    renderFindings();
  };
  $("#search").oninput = (e) => {
    state.search = e.target.value.toLocaleLowerCase("es").trim();
    state.page = 0;
    renderFindings();
  };
  $("#prev").onclick = () => {
    state.page--;
    renderFindings();
  };
  $("#next").onclick = () => {
    state.page++;
    renderFindings();
  };
  $("#replay").onclick = (e) =>
    busy(e.target, async () => {
      await post(`/api/runs/${run.id}/replay`);
      notice(
        "Reproducción idéntica. Entradas, documentos, motor y resultado verificados.",
      );
    });

  renderFindings();
}

function references(finding) {
  const shipments = finding.shipment_ids
    .map((id) => state.shipmentIndex.get(id)?.reference)
    .filter(Boolean);
  const charges = finding.charge_ids
    .map((id) => state.chargeIndex.get(id)?.reference)
    .filter(Boolean);
  return Array.from(new Set([...shipments, ...charges])).join(", ");
}

function renderFindings() {
  const all = state.run.result.findings.filter((f) => {
    if (state.filter && f.status !== state.filter) return false;
    if (!state.search) return true;
    const haystack = [
      references(f),
      f.concept,
      f.rule,
      f.agreement,
      ...f.reasons,
    ]
      .join(" ")
      .toLocaleLowerCase("es");
    return haystack.includes(state.search);
  });

  const page = all.slice(state.page * 30, (state.page + 1) * 30);
  const tbody = $("#findings");
  tbody.innerHTML =
    page
      .map((f) => {
        const decision = state.run.decisions.findLast(
          (d) => d.payload.finding_id === f.id,
        );
        return `<tr data-finding-id="${esc(f.id)}">
          <td>
            <div class="ref">${esc(references(f) || "Sin referencia vinculada")}</div>
            <span class="muted ui-fontsize-c42f23b8">${esc(f.concept)} · ${f.charge_ids.length} cargo${f.charge_ids.length === 1 ? "" : "s"}</span>
          </td>
          <td>${badge(f.status)}</td>
          <td class="num">${esc(f.currency)} ${money(f.actual)}</td>
          <td class="num">${moneyOrStatus(f.expected, f.status)}</td>
          <td class="num finding-difference ${f.status === "FAIL" ? "finding-difference-fail" : f.status === "REVIEW" ? "finding-difference-review" : ""}">
            ${moneyOrStatus(f.difference, f.status)}
            ${f.status === "REVIEW" ? '<br><small class="muted ui-fontsize-025fe512">Requiere revisión</small>' : ""}
          </td>
          <td class="muted">${decision ? esc(actions[decision.payload.action]) : "Sin resolución"}</td>
          <td>
            <button class="btn-text" data-finding="${f.id}" aria-label="Ver explicación de ${esc(references(f))}, ${esc(f.concept)}">
              Ver detalle →
            </button>
          </td>
        </tr>`;
      })
      .join("") ||
    '<tr><td colspan="7" class="empty">No hay hallazgos que coincidan con este filtro.</td></tr>';

  $("#page-label").textContent =
    `${all.length ? state.page * 30 + 1 : 0}–${Math.min((state.page + 1) * 30, all.length)} de ${all.length} hallazgos`;
  $("#prev").disabled = state.page === 0;
  $("#next").disabled = (state.page + 1) * 30 >= all.length;

  document
    .querySelectorAll("[data-finding]")
    .forEach(
      (button) => (button.onclick = () => showDetail(button.dataset.finding)),
    );
}

/* ==========================================================================
   PANTALLA ESTRELLA: DETALLE DEL HALLAZGO
   ========================================================================== */
const opLabels = {
  const: "Parámetro contractual",
  attr: "Dato de operación",
  sum: "Suma de operaciones",
  count: "Cantidad de operaciones",
  add: "Suma",
  sub: "Resta",
  mul: "Multiplicación",
  div: "División con redondeo",
  min: "Mínimo",
  max: "Máximo",
  round: "Redondeo",
  lookup: "Búsqueda en tabla",
  band: "Selección de tramo",
  if: "Condición",
  version: "Selección de vigencia",
  comparison: "Comparación de importes",
  currency_round: "Redondeo monetario",
  evidence: "Control de evidencia",
  matching: "Relación de operaciones y cargos",
  matching_uncertainty: "Vinculación pendiente de un cargo relacionado",
  condition: "Aplicabilidad de regla",
  unresolved: "Dato o regla no resueltos",
};

function traceText(trace) {
  const operands = trace.children.map((child) => child.output ?? "?");
  const symbols = { add: " + ", sub: " − ", mul: " × ", div: " ÷ " };
  if (symbols[trace.op])
    return operands.join(symbols[trace.op]) + " = " + trace.output;
  if (trace.op === "attr") return trace.details.field + " = " + trace.output;
  if (trace.op === "comparison")
    return (
      "Facturado " +
      trace.details.actual +
      " − esperado " +
      trace.details.expected +
      " = " +
      trace.output +
      " · tolerancia " +
      trace.details.tolerance
    );
  if (trace.op === "sum")
    return (
      "Suma de " +
      trace.details.field +
      " en " +
      (trace.details.sources?.length || 0) +
      " operaciones = " +
      trace.output
    );
  return trace.details.reason || "";
}

function traceHtml(trace) {
  return `<details class="trace" open>
    <summary>${esc(opLabels[trace.op] || trace.op)} ${trace.output !== null ? `<span class="trace-output">→ ${esc(trace.output)}</span>` : ""}</summary>
    <p class="small-text ui-fontweight-94760884">${esc(traceText(trace))}</p>
    <details>
      <summary>Datos utilizados en este paso</summary>
      <code>${esc(JSON.stringify(trace.details, null, 2))}</code>
    </details>
    ${trace.children.map(traceHtml).join("")}
  </details>`;
}

function extractArithmeticSummary(finding) {
  // Intermediate products can have other units or precede minimums and rounding.
  // The complete expression remains available in the trace below.
  return finding.expected !== null
    ? `Esperado según regla: ${finding.currency} ${money(finding.expected)}`
    : "Sin cálculo automático: requiere revisión de datos o evidencia.";
}

function showDetail(id) {
  const detailRun = state.run;
  const revision = state.viewRevision;
  const f = state.run.result.findings.find((item) => item.id === id);
  const history = state.run.decisions.filter(
    (d) => d.payload.finding_id === id,
  );
  const shipments = state.run.snapshot.shipments.filter((s) =>
    f.shipment_ids.includes(s.id),
  );
  const charges = state.run.snapshot.charges.filter((c) =>
    f.charge_ids.includes(c.id),
  );
  const records = [...shipments, ...charges];

  // Documentos usados checklist
  const documentsUsed = [];
  shipments.forEach((s) => {
    const fn = Object.values(s.provenance || {})[0]?.filename || "Sin archivo de origen vinculado";
    documentsUsed.push(`Remito ${s.reference || s.id} (${fn})`);
  });
  charges.forEach((c) => {
    const fn = Object.values(c.provenance || {})[0]?.filename || "Sin archivo de origen vinculado";
    documentsUsed.push(`Liquidación ${c.reference || c.id} (${fn})`);
  });
  if (f.agreement && f.version && f.rule) {
    documentsUsed.push(`Configuración ${f.agreement}, versión ${f.version}, regla ${f.rule}`);
  }

  const conflictingLinks = f.trace.flatMap((t) => t.details.execution || []).filter((e) => ["conflict", "invalid", "ambiguous", "unmatched", "uncorroborated"].includes(e.comparison));
  const relatedConflicts = f.trace.flatMap((t) => t.op === "matching_uncertainty" ? t.details.unresolved_charge_ids : t.op === "matching_conflict" ? t.details.conflicting_charge_ids : []);
  const versionLabel = conflictingLinks.length ? "Pendiente por vinculación" : f.version || "Sin versión aplicable";
  const ruleLabel = conflictingLinks.length ? "Pendiente por vinculación" : f.rule || "Sin regla aplicable";
  const arithmeticStr = conflictingLinks.length
    ? "Cálculo pendiente: resolver la vinculación entre el cargo y las operaciones."
    : extractArithmeticSummary(f);

  $("#detail-content").innerHTML = `
    <!-- Top Status Banner -->
    <div class="star-status-pill ${f.status}">
      ${f.status === "FAIL" ? "DISCREPANCIA" : f.status === "PASS" ? "COINCIDE" : f.status === "REVIEW" ? "REVISIÓN HUMANA" : "INDETERMINADO"}
    </div>

    <div class="modal-header-star">
      <div class="modal-header-title">
        <div class="eyebrow ui-color-10d73d12">EXPLICACIÓN DEL HALLAZGO</div>
        <h2 id="detail-title" class="ui-margin-698a2e6f">
          ${esc(references(f) || "Referencia sin vincular")} · ${esc(f.concept)}
        </h2>
        <div class="ui-margintop-1d436efc">
          ${badge(f.status)}
          <span class="muted ui-marginleft-c3b08bda">Acuerdo <strong>${esc(f.agreement || "Sin acuerdo")}</strong> · Versión <strong>${esc(versionLabel)}</strong> · Regla <strong>${esc(ruleLabel)}</strong></span>
        </div>
      </div>
      <button class="btn small" id="close-detail" aria-label="Cerrar explicación">Cerrar ✕</button>
    </div>

    <!-- Hero Financial Card (Facturado vs Esperado vs Diferencia) -->
    <div class="hero-financial-card detail-money">
      <div class="hero-fin-col">
        <label>FACTURADO LIQUIDADO · ${esc(f.currency)}</label>
        <div class="amount">${money(f.actual)}</div>
        <p class="muted ui-fontsize-5ca1e82b">Según los cargos importados</p>
      </div>
      <div class="hero-fin-col">
        <label>ESPERADO SEGÚN ACUERDO</label>
        <div class="amount">${money(f.expected, f.status === "REVIEW" ? "Requiere revisión" : "No determinable")}</div>
        <p class="muted ui-fontsize-5ca1e82b">${conflictingLinks.length ? "Primero se debe resolver la vinculación" : f.expected === null ? "Faltan datos o reglas para calcular" : "Resultado de la regla configurada"}</p>
      </div>
      <div class="hero-fin-col ${f.status === "FAIL" ? "highlight-fail" : f.status === "REVIEW" ? "highlight-review" : ""}">
        <label>DIFERENCIA CALCULADA</label>
        <div class="amount">${money(f.difference, f.status === "REVIEW" ? "Requiere revisión" : "No determinable")}</div>
        <p class="muted ui-fontsize-5ca1e82b">${f.status === "FAIL" ? "Discrepancia determinada" : f.status === "REVIEW" ? "Diferencia sin confirmar" : f.status === "PASS" ? "Dentro de la tolerancia configurada" : "No se puede determinar la diferencia"}</p>
      </div>
    </div>

    <!-- Sections Grid: Por qué, Cálculo, Documentos -->
    <div class="finding-sections-grid">
      <!-- Por qué -->
      <div class="finding-card">
        <div class="finding-card-title">
          <span>ⓘ</span> Por qué
        </div>
        ${f.reasons.map((r) => `<p class="ui-fontsize-afce41d9">${esc(r)}</p>`).join("")}
        ${matchingConflictDetails(conflictingLinks, state.run.snapshot)}
        ${relatedConflicts.length ? `<p>Revisar los cargos con vinculación pendiente: ${relatedConflicts.map(esc).join(", ")}.</p>` : ""}
        <div class="ui-background-ef9abbd6">
          Regla <strong>${esc(ruleLabel)}</strong> · versión <strong>${esc(versionLabel)}</strong>
        </div>
      </div>

      <!-- Cálculo y Documentos usados -->
      <div class="finding-card">
        <div class="finding-card-title">
          <span>∑</span> Cálculo y Documentos
        </div>
        <div class="arithmetic-callout">
          ${esc(arithmeticStr)}
        </div>
        <div class="ui-fontsize-7d717343">
          ${conflictingLinks.length ? "Operaciones candidatas y cargos a contrastar:" : "Registros y configuración utilizados:"}
        </div>
        <ul class="doc-checklist">
          ${documentsUsed.map((doc) => `<li class="doc-item"><span class="check">${conflictingLinks.length ? "?" : "✓"}</span> <span>${esc(doc)}</span></li>`).join("")}
        </ul>
      </div>
    </div>

    <!-- Trazabilidad completa (secundario) -->
    <div class="ui-padding-496cf7c8">
      <details class="panel ui-margin-38965f9b">
        <summary class="ui-fontweight-b44ef607">Cálculo ejecutado y decisiones de la regla (ver pasos matemáticos)</summary>
        <div class="ui-margintop-b6d781cb">
          ${f.trace.map(traceHtml).join("") || "<p class='muted'>No hubo cálculo: primero se necesita resolver la vinculación.</p>"}
        </div>
      </details>
    </div>

    <div class="ui-padding-fea5994f">
      <details class="panel ui-margin-38965f9b">
        <summary class="ui-fontweight-b44ef607">Origen de cada dato (${records.length} registros celda por celda)</summary>
        <div class="table-wrap ui-margintop-b6d781cb">
          <table>
            <thead>
              <tr>
                <th>Registro / campo</th>
                <th>Archivo</th>
                <th>Hoja / fila / columna</th>
                <th>Valor original</th>
              </tr>
            </thead>
            <tbody>
              ${records.flatMap((record) =>
                Object.entries(record.provenance).map(
                  ([field, ref]) =>
                    `<tr>
                      <td><strong>${esc(record.id)}</strong><br><span class="muted">${esc(field)}</span></td>
                      <td>${esc(ref.filename)}</td>
                      <td>${esc(ref.sheet)} · fila ${ref.row} · col ${esc(ref.column)}</td>
                      <td><code>${esc(ref.raw)}</code></td>
                    </tr>`,
                ),
              ).join("")}
            </tbody>
          </table>
        </div>
      </details>
    </div>

    <!-- Decisión Humana e Historial -->
    <div class="decision-section-wrap">
      <div class="grid2">
        <section class="panel ui-margin-38965f9b">
          <h3 class="ui-margintop-1294519f">Decisión humana</h3>
          <p class="hint">Agrega una resolución al expediente de auditoría. El cálculo y estado técnico original del motor se conservan intactos.</p>
          <form id="decision-form" class="decision-form">
            <div class="field">
              <label for="actor">Persona responsable</label>
              <input id="actor" name="actor" type="text" required maxlength="200" placeholder="Ej.: Auditor Cuentas a Pagar">
            </div>
            <div class="field">
              <label for="action">Decisión</label>
              <select id="action" name="action">
                <option value="APPROVED">Confirmar diferencia</option>
                <option value="REJECTED">Rechazar</option>
                <option value="INFORMATION_REQUESTED">Mantener en revisión</option>
                <option value="EXCEPTION_ACCEPTED">Excepción aceptada</option>
                <option value="IGNORED">Ignorado</option>
              </select>
            </div>
            <div class="field">
              <label for="decision-note">Motivo y respaldo de la decisión</label>
              <textarea id="decision-note" name="note" required minlength="3" maxlength="10000" placeholder="Fundamento de la resolución y referencia de comprobantes…"></textarea>
            </div>
            <div class="field">
              <label for="known">¿El cliente o proveedor ya conocía esta diferencia?</label>
              <select id="known" name="known">
                <option value="">Sin confirmar</option>
                <option value="true">Sí, confirmada previamente</option>
                <option value="false">No, discrepancia nueva</option>
              </select>
            </div>
            <button class="btn primary ui-width-9ccc4ca9" type="submit">Guardar decisión en expediente</button>
          </form>
        </section>

        <section class="panel ui-margin-38965f9b">
          <h3 class="ui-margintop-1294519f">Historial de resoluciones</h3>
          <div class="ui-maxheight-d1cb98d5">
            ${history
              .map(
                (d) =>
                  `<div class="history">
                    <strong>${esc(actions[d.payload.action])}</strong>
                    <p>${esc(d.payload.note)}</p>
                    <small class="muted">${esc(d.payload.actor)} · ${new Date(d.created_at).toLocaleString("es-AR")}</small>
                  </div>`,
              )
              .join("") || '<p class="muted">Todavía no se registraron decisiones para este hallazgo.</p>'}
          </div>

          <!-- Aportar evidencia -->
          <details id="evidence-panel" class="ui-bordertop-fd7dfba1">
            <summary class="ui-fontsize-74b1bec6">Aportar evidencia y crear nueva corrida</summary>
            <p class="hint ui-marginbottom-4636770b">Permite adjuntar documentación que subsane una revisión. La corrida anterior permanece inmutable.</p>
            <form id="evidence-form">
              <div class="field">
                <label for="ev-kind">Tipo de evidencia según el acuerdo</label>
                <input id="ev-kind" type="text" required placeholder="Ej.: authorization_signature">
              </div>
              <div class="field">
                <label for="ev-note">Descripción del respaldo</label>
                <input id="ev-note" type="text" required placeholder="Remito con firma digital / carta porte">
              </div>
              <div class="field">
                <label for="ev-file">Documento adjunto (opcional)</label>
                <input id="ev-file" type="file">
              </div>
              <button class="btn ui-width-9ccc4ca9" type="submit">Auditar con esta evidencia</button>
            </form>
          </details>
        </section>
      </div>
    </div>
  `;

  $("#close-detail").onclick = () => $("#detail").close();

  $("#decision-form").onsubmit = (event) => {
    event.preventDefault();
    busy($("button[type=submit]", event.target), async () => {
      await post(`/api/runs/${detailRun.id}/decisions`, {
        finding_id: id,
        action: $("#action").value,
        actor: $("#actor").value,
        note: $("#decision-note").value,
        known_to_client:
          $("#known").value === "" ? null : $("#known").value === "true",
      });
      const updated = await api("/api/runs/" + detailRun.id);
      if (revision !== state.viewRevision || !$("#detail").open) return;
      state.run = updated;
      renderFindings();
      showDetail(id);
      notice("Decisión agregada al expediente. El hallazgo original se conserva.");
    });
  };

  $("#evidence-form").onsubmit = (event) => {
    event.preventDefault();
    busy($("button[type=submit]", event.target), async () => {
      const snapshot = structuredClone(detailRun.snapshot);
      const kind = $("#ev-kind").value;
      const note = $("#ev-note").value;
      let document_hash = null;
      const file = $("#ev-file").files[0];
      if (file) {
        const form = new FormData();
        form.append("file", file);
        const attachment = await post("/api/evidence-file", form);
        document_hash = attachment.document_hash;
        snapshot.documents[document_hash] = attachment.filename;
      }
      snapshot.evidence.push({
        id: "EV-" + crypto.randomUUID(),
        kind,
        note,
        shipment_ids: f.shipment_ids,
        charge_ids: f.charge_ids,
        document_hash,
      });
      snapshot.label += " · evidencia adicional";
      const result = await post("/api/audit", snapshot);
      if (revision !== state.viewRevision) return;
      $("#detail").close();
      await openRun(result.run_id);
      notice(
        "Nueva auditoría creada con la evidencia aportada. La corrida anterior se conserva.",
      );
    });
  };

  if (!$("#detail").open) $("#detail").showModal();
}

/* ==========================================================================
   WIZARD DE NUEVA AUDITORÍA (1. DATOS → 2. ACUERDO → 3. VERIFICACIÓN → 4. EJECUTAR)
   ========================================================================== */
function agreementRuleCount(agreement) {
  return (agreement?.versions || []).reduce(
    (count, version) => count + (Array.isArray(version.rules) ? version.rules.length : 0),
    0,
  );
}

function agreementVersionList(agreement) {
  return (agreement.versions || []).map((version) => {
    const ruleCount = Array.isArray(version.rules) ? version.rules.length : 0;
    return `<li><strong>${esc(version.id)}</strong> · ${esc(version.valid_from || "sin inicio")} a ${esc(version.valid_to || "abierta")} · ${ruleCount} regla(s)</li>`;
  }).join("");
}

function agreementSummary(agreements) {
  const versions = agreements.flatMap((agreement) => agreement.versions || []);
  const rules = agreements.reduce((count, agreement) => count + agreementRuleCount(agreement), 0);
  const details = agreements.map((agreement) => {
    return `<li><strong>${esc(agreement.id)}</strong> · ${esc(agreement.carrier)} · ${esc(agreement.currency)}
      <ul>${agreementVersionList(agreement)}</ul></li>`;
  }).join("");
  return `<strong>${agreements.length} acuerdo(s)</strong> · <strong>${versions.length} versión(es)</strong> · <strong>${rules} regla(s) configuradas</strong>
    <details class="agreement-summary-detail"><summary>Ver acuerdos y versiones cargados</summary><ul>${details}</ul></details>`;
}

async function showNew() {
  nav("new");
  const revision = state.viewRevision;
  main.innerHTML = heading("NUEVA AUDITORÍA", "Preparando el asistente", "Leyendo acuerdos y formatos del equipo…");
  state.imports = {};
  state.mappingSource = { shipments: null, charges: null };
  state.mappingReadPending = { shipments: false, charges: false };
  state.importPending = { shipments: false, charges: false };
  state.agreementReadPending = false;
  state.agreementRevision += 1;
  state.matchingRevision += 1;
  state.matchingCheck = null;
  state.auditLabel = "";
  state.importRevision.shipments += 1;
  state.importRevision.charges += 1;
  state.wizardStep = 1;
  try {
    const configs = await api("/api/configs");
    if (revision !== state.viewRevision) return;
    state.configs = configs;
    renderWizard();
  } catch (error) {
    if (revision !== state.viewRevision) return;
    main.innerHTML = heading("NUEVA AUDITORÍA", "No se pudo abrir el asistente", esc(error.message), '<button class="btn primary" id="retry-new">Reintentar</button>');
    $("#retry-new").onclick = showNew;
  }
}

function renderWizard() {
  main.innerHTML = `
    <div class="wizard-header">
      <div class="eyebrow ui-color-10d73d12">FLUJO GUIADO DE AUDITORÍA</div>
      <h1>Nueva auditoría</h1>
      <p class="muted">Configuración por etapas de datos, contrato y verificación antes de calcular.</p>

      <div class="wizard-steps">
        <button class="wizard-step-item active" id="step-nav-1">
          <div class="wizard-circle">1</div>
          <div class="wizard-step-name">1. Datos</div>
        </button>
        <span class="wizard-step-arrow">→</span>
        <button class="wizard-step-item" id="step-nav-2">
          <div class="wizard-circle">2</div>
          <div class="wizard-step-name">2. Acuerdo</div>
        </button>
        <span class="wizard-step-arrow">→</span>
        <button class="wizard-step-item" id="step-nav-3">
          <div class="wizard-circle">3</div>
          <div class="wizard-step-name">3. Verificación</div>
        </button>
        <span class="wizard-step-arrow">→</span>
        <button class="wizard-step-item" id="step-nav-4">
          <div class="wizard-circle">4</div>
          <div class="wizard-step-name">4. Ejecutar</div>
        </button>
      </div>
    </div>

    <!-- Compact Step Summaries for Completed Steps -->
    <div id="wizard-summaries" class="ui-marginbottom-3c4a3d44">
      <div id="step-summary-1" class="step-summary-bar hidden">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Datos</span>
          <span class="step-summary-desc" id="step-summary-1-text"></span>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-1">Editar</button>
      </div>
      <div id="step-summary-2" class="step-summary-bar hidden">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Acuerdo</span>
          <div class="step-summary-desc" id="step-summary-2-text"></div>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-2">Editar</button>
      </div>
      <div id="step-summary-3" class="step-summary-bar hidden">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Verificación</span>
          <span class="step-summary-desc" id="step-summary-3-text">Integridad del lote verificada</span>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-3">Editar</button>
      </div>
    </div>

    <!-- Wizard Steps Content: All 4 panels preserved in DOM -->
    <p id="matching-progress" role="status" aria-live="polite" hidden></p>
    <div id="wizard-content">
      <!-- STEP 1: DATOS -->
      <div id="step-panel-1" class="wizard-panel">
        <div class="panel">
          <div class="ui-marginbottom-3c4a3d44">
            <label for="audit-label" class="ui-fontsize-df949b3e">Nombre del período o lote</label>
            <input id="audit-label" type="text" placeholder="Ej.: Cierre de septiembre · Transportes Gómez" value="${esc(state.auditLabel || "")}" required class="ui-maxwidth-344a0df9">
          </div>

          <div class="ui-marginbottom-7564ec60">
            <h2 class="ui-margin-9412625c">Paso 1: Carga de Archivos</h2>
            <p class="muted ui-margin-7406c902">Subí las operaciones realizadas (remitos o viajes) y los cargos facturados por el transportista.</p>
          </div>

          <div class="grid2 ui-margintop-76977cc9">
            ${renderDropzoneSection("shipments", "Operaciones", "Viajes, despachos o remitos")}
            ${renderDropzoneSection("charges", "Cargos liquidados", "Detalle de cargos y montos del transportista")}
          </div>

          <div class="actions ui-margintop-91a1fbef">
            <button class="btn primary" id="goto-step-2">Continuar a Acuerdo →</button>
          </div>
        </div>
      </div>

      <!-- STEP 2: ACUERDO -->
      <div id="step-panel-2" class="wizard-panel hidden">
        <div class="panel">
          <h2>Paso 2: Selección del Acuerdo Contractual</h2>
          <p class="muted">Elegí el tarifario pactado con el transportista para auditar los cargos.</p>

          <div class="run-list ui-display-a3d2651f">
            ${state.configs
              .filter((c) => c.kind === "agreement")
              .map(
                (c) => `
                <div class="agreement-card" data-hash="${c.hash}">
                  <div class="ui-display-d528dea8">
                    <div>
                      <h4 class="agreement-card-title">${esc(c.name)}</h4>
                      <div class="agreement-card-carrier">Transportista: <strong>${esc(c.payload?.carrier || "Pactado")}</strong></div>
                    </div>
                    <span class="badge PASS">Válido ✓</span>
                  </div>
                  <div class="agreement-card-meta">
                    <span>Moneda <strong>${esc(c.payload?.currency || "ARS")}</strong></span>
                    <span>·</span>
                    <span>${c.payload?.versions?.length || 0} versión(es)</span>
                    <span>·</span>
                    <span>${agreementRuleCount(c.payload)} regla(s) configuradas</span>
                  </div>
                  <div class="ui-display-a9e01b95">
                    <button type="button" class="btn small primary select-agreement-btn" data-hash="${c.hash}">Seleccionar</button>
                  </div>
                </div>
              `,
              )
              .join("") || '<p class="muted">No hay acuerdos guardados. Cargá uno desde JSON.</p>'}
          </div>

          <div class="ui-display-1a968e4a">
            <div class="field ui-margin-f6efb71d">
              <label for="agreement-select">O seleccionar desde el listado</label>
              <select id="agreement-select">
                <option value="">Seleccionar acuerdo…</option>
                ${state.configs
                  .filter((c) => c.kind === "agreement")
                  .map(
                    (c) =>
                      `<option value="${c.hash}">${esc(c.name)} · (hash ${c.hash.slice(0, 8)})</option>`,
                  )
                  .join("")}
              </select>
            </div>
            <div class="field ui-margin-38965f9b">
              <label>Importar acuerdo JSON</label>
              <input type="file" id="agreement-file" accept=".json" class="ui-padding-45d64fe9">
              <p id="agreement-load-status" role="status" aria-live="polite"></p>
            </div>
          </div>

          <div class="panel-advanced ui-margintop-910f53fb">
            <div class="ui-display-c8cc40c3">
              <strong class="ui-fontsize-6c0edc58">Modo avanzado: Editor de acuerdos y evidencia (JSON)</strong>
              <button class="btn subtle small" type="button" id="toggle-agreements">Mostrar/Ocultar JSON</button>
            </div>
            <div id="agreements-advanced-body" class="panel-advanced-body hidden">
              <label for="agreements">Acuerdos (lista JSON)</label>
              <textarea id="agreements" rows="7" spellcheck="false">[]</textarea>
              <div class="ui-margintop-726e8b31">
                <label for="evidence">Evidencia previa (lista JSON opcional)</label>
                <textarea id="evidence" rows="3">[]</textarea>
              </div>
              <div class="ui-margintop-726e8b31">
                <label for="coverage">Alcance por acuerdo (JSON)</label>
                <textarea id="coverage" rows="3">{}</textarea>
              </div>
            </div>
          </div>

          <div class="actions ui-margintop-bf9413de">
            <button class="btn" id="back-to-step-1">← Volver a Datos</button>
            <button class="btn primary" id="goto-step-3">Continuar a Verificación →</button>
          </div>
        </div>
      </div>

      <!-- STEP 3: VERIFICACIÓN -->
      <div id="step-panel-3" class="wizard-panel hidden">
        <div class="panel">
          <h2>Paso 3: Verificación Previa</h2>
          <p class="muted">Revisá la consistencia del lote antes de ejecutar el motor de auditoría determinista.</p>
          <div id="matching-check-step3" role="status" aria-live="polite"></div>

          <div class="field ui-margin-5de38404">
            <label for="audit-label-step3">Nombre de la auditoría</label>
            <input id="audit-label-step3" type="text" value="${esc(state.auditLabel || "")}" required class="ui-maxwidth-344a0df9">
          </div>

          <div class="grid2 ui-margin-5de38404">
            <div class="ui-padding-041145b1">
              <h3 class="ui-margin-7cb69eb0">Operaciones preparadas</h3>
              <div id="verify-shipments-summary"></div>
            </div>
            <div class="ui-padding-041145b1">
              <h3 class="ui-margin-7cb69eb0">Cargos liquidados preparados</h3>
              <div id="verify-charges-summary"></div>
            </div>
          </div>

          <div class="banner info ui-margin-3b5bc8f9">
            <div class="ui-fontsize-87e06f45">ⓘ</div>
            <div>
              <strong>Revisá las incidencias antes de ejecutar</strong>
              <p class="ui-margin-b2f2f5fb">Las advertencias y filas rechazadas figuran arriba. Una advertencia no bloquea automáticamente la auditoría; verificá su alcance antes de interpretar los resultados.</p>
            </div>
          </div>

          <div class="actions ui-margintop-bf9413de">
            <button class="btn" id="back-to-step-2">← Volver a Acuerdo</button>
            <button class="btn primary" id="goto-step-4">Continuar a Ejecución →</button>
          </div>
        </div>
      </div>

      <!-- STEP 4: EJECUTAR -->
      <div id="step-panel-4" class="wizard-panel hidden">
        <div class="panel ui-textalign-aafb9ae4">
          <div class="ui-fontsize-7213c457">⚡</div>
          <h2>Listo para auditar</h2>
          <div id="matching-check-step4" role="status" aria-live="polite"></div>
          <p class="muted ui-maxwidth-2cb2dbe7">
            Auditoría: <strong id="step4-audit-label">${esc(state.auditLabel || "Sin título")}</strong><br>
            El motor procesará los cálculos en este equipo de forma determinista, generando la cadena de decisión y los reportes exportables.
          </p>
          <button class="btn primary ui-padding-a7d43ac2" id="execute">
            Ejecutar auditoría local →
          </button>
          <div class="ui-margintop-910f53fb">
            <button class="btn subtle" id="back-to-step-3">← Revisar configuración</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Attach nav buttons
  $("#step-nav-1").onclick = () => goToStep(1);
  $("#step-nav-2").onclick = () => goToStep(2);
  $("#step-nav-3").onclick = () => goToStep(3);
  $("#step-nav-4").onclick = () => goToStep(4);

  // Attach summary reopen buttons
  const r1 = $("#reopen-step-1");
  if (r1) r1.onclick = () => goToStep(1);
  const r2 = $("#reopen-step-2");
  if (r2) r2.onclick = () => goToStep(2);
  const r3 = $("#reopen-step-3");
  if (r3) r3.onclick = () => goToStep(3);

  // Setup Step 1 Handlers
  setupStep1Handlers();
  $("#goto-step-2").onclick = () => goToStep(2);

  // Setup Step 2 Handlers
  $("#back-to-step-1").onclick = () => goToStep(1);
  $("#goto-step-3").onclick = () => goToStep(3);

  const updateSelectedAgreementCard = (hash) => {
    state.agreementRevision += 1;
    state.agreementReadPending = false;
    state.matchingCheck = null;
    $("#agreement-load-status").textContent = "";
    document.querySelectorAll(".agreement-card").forEach((card) => {
      const isSelected = card.dataset.hash === hash;
      card.classList.toggle("selected", isSelected);
      const btn = card.querySelector(".select-agreement-btn");
      if (btn) {
        btn.textContent = isSelected ? "✓ Seleccionado" : "Seleccionar";
        btn.className = `btn small ${isSelected ? "subtle" : "primary"} select-agreement-btn`;
      }
    });
  };

  document.querySelectorAll(".select-agreement-btn").forEach((btn) => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const found = state.configs.find((c) => c.hash === btn.dataset.hash);
      if (found) {
        $("#agreements").value = JSON.stringify([found.payload], null, 2);
        if ($("#agreement-select")) $("#agreement-select").value = found.hash;
        updateSelectedAgreementCard(found.hash);
        notice(`Acuerdo "${found.name}" seleccionado.`);
      }
    };
  });

  document.querySelectorAll(".agreement-card").forEach((card) => {
    card.onclick = () => {
      const hash = card.dataset.hash;
      const found = state.configs.find((c) => c.hash === hash);
      if (found) {
        $("#agreements").value = JSON.stringify([found.payload], null, 2);
        if ($("#agreement-select")) $("#agreement-select").value = found.hash;
        updateSelectedAgreementCard(found.hash);
        notice(`Acuerdo "${found.name}" seleccionado.`);
      }
    };
  });

  $("#agreement-select").onchange = (event) => {
    const found = state.configs.find((c) => c.hash === event.target.value);
    if (found) {
      $("#agreements").value = JSON.stringify([found.payload], null, 2);
      updateSelectedAgreementCard(found.hash);
    } else {
      $("#agreements").value = "[]";
      updateSelectedAgreementCard("");
    }
  };

  $("#agreement-file").onchange = (event) =>
    busy(null, async () => {
      const file = event.target.files[0];
      if (!file) return;
      updateSelectedAgreementCard("");
      $("#agreement-select").value = "";
      $("#agreements").value = "[]";
      const revision = state.agreementRevision;
      const viewRevision = state.viewRevision;
      state.agreementReadPending = true;
      $("#agreement-load-status").textContent = "Leyendo el acuerdo seleccionado…";
      let parsed;
      try {
        const content = await file.text();
        if (revision !== state.agreementRevision || viewRevision !== state.viewRevision) return;
        parsed = JSON.parse(content);
      } catch {
        if (revision === state.agreementRevision && viewRevision === state.viewRevision) {
          notice("No se pudo leer el acuerdo. Volvé a seleccionar un archivo JSON válido o un acuerdo guardado.", true);
        }
        return;
      } finally {
        if (revision === state.agreementRevision && viewRevision === state.viewRevision) {
          state.agreementReadPending = false;
          $("#agreement-load-status").textContent = "Revisá la configuración antes de continuar.";
        }
      }
      $("#agreements").value = JSON.stringify(
        Array.isArray(parsed) ? parsed : [parsed],
        null,
        2,
      );
      notice("Archivo de acuerdo cargado correctamente.");
    });
  $("#agreements").oninput = () => {
    updateSelectedAgreementCard("");
    $("#agreement-select").value = "";
  };

  $("#toggle-agreements").onclick = () => {
    const body = $("#agreements-advanced-body");
    if (body) body.classList.toggle("hidden");
  };

  // Setup Step 3 Handlers
  $("#audit-label-step3").oninput = (e) => {
    state.auditLabel = e.target.value.trim();
    const l1 = $("#audit-label");
    if (l1) l1.value = state.auditLabel;
  };
  $("#back-to-step-2").onclick = () => goToStep(2);
  $("#goto-step-4").onclick = () => {
    const val = $("#audit-label-step3")?.value.trim() || state.auditLabel;
    if (!val) {
      notice("Ingresar un nombre para esta auditoría antes de continuar.", true);
      return;
    }
    state.auditLabel = val;
    goToStep(4);
  };

  // Setup Step 4 Handlers
  $("#back-to-step-3").onclick = () => goToStep(3);
  $("#execute").onclick = (event) =>
    busy(event.target, async () => {
      if (state.agreementReadPending) throw new Error("Esperá a que termine de cargar el acuerdo.");
      if (!state.imports.shipments || !state.imports.charges)
        throw new Error(
          "Validar ambos archivos con sus columnas antes de ejecutar.",
        );
      const dataset = auditDataset();
      if (state.matchingCheck !== matchingSignature(dataset)) {
        notice("El lote cambió. Revisá la verificación actualizada antes de ejecutar.", true);
        await goToStep(3);
        return;
      }
      const result = await post("/api/audit", dataset);
      await openRun(result.run_id);
    });

  goToStep(1);
}

function auditDataset() {
  const values = Object.values(state.imports);
  return {
    label: state.auditLabel || $("#audit-label")?.value.trim() || "Auditoría local",
    shipments: state.imports.shipments.records,
    charges: state.imports.charges.records,
    agreements: JSON.parse($("#agreements")?.value || "[]"),
    evidence: JSON.parse($("#evidence")?.value || "[]"),
    coverage: JSON.parse($("#coverage")?.value || "{}"),
    mappings: values.map((r) => r.mapping),
    documents: Object.fromEntries(values.map((r) => [r.document, r.filename])),
    issues: values.flatMap((r) => r.issues),
  };
}

function matchingSignature(dataset) {
  const { label, ...content } = dataset;
  return JSON.stringify(content);
}

function matchingConflictDetails(conflicts, dataset) {
  if (!conflicts.length) return "";
  const shipments = new Map(dataset.shipments.map((s) => [s.id, s]));
  const charges = new Map(dataset.charges.map((c) => [c.id, c]));
  const operationList = (ids) => ids.slice(0, 8).map((id) => {
    const shipment = shipments.get(id);
    return shipment ? `${esc(id)} (referencia ${esc(shipment.reference || "vacía")})` : `${esc(id)} (no existe en el lote)`;
  }).join(", ") + (ids.length > 8 ? `; y ${ids.length - 8} más, disponibles en la traza completa` : "") || "ninguna operación";
  const reasons = {
    conflict: "Las claves y el vínculo explícito se contradicen.",
    invalid: "El vínculo explícito no es válido.",
    ambiguous: "Las claves señalan varias operaciones; hace falta precisar la vinculación.",
    unmatched: "Las claves no señalan una operación del lote; revisá la referencia o el archivo de operaciones.",
    uncorroborated: "El destino explícito no pudo corroborarse con las claves; revisá el original y la referencia.",
  };
  return `<ul class="matching-conflicts">${conflicts.map((conflict) => `
    <li><strong>Cargo ${esc(conflict.charge_id)}</strong> · referencia ${esc(charges.get(conflict.charge_id)?.reference || "vacía")}
      <p>${reasons[conflict.comparison] || "Revisar la vinculación."}</p>
      <p>Según las claves del archivo: ${operationList(conflict.key_candidate_ids || [])}.</p>
      ${conflict.method === "explicit" ? `<p>Según la vinculación explícita: ${operationList(conflict.shipment_ids || [])}.</p>` : ""}
      ${conflict.invalid_targets?.empty ? "<p>La lista de destinos está vacía.</p>" : ""}
      ${conflict.invalid_targets?.repeated?.length ? `<p>Destinos repetidos: ${operationList(conflict.invalid_targets.repeated)}.</p>` : ""}
      ${conflict.invalid_targets?.other_carrier?.length ? `<p>Destinos de otro transportista: ${operationList(conflict.invalid_targets.other_carrier)}.</p>` : ""}
    </li>`).join("")}</ul>`;
}

function matchingPending(pending) {
  const progress = $("#matching-progress");
  if (progress) {
    progress.hidden = !pending;
    progress.textContent = pending ? "Verificando las vinculaciones del lote…" : "";
  }
  for (const id of ["step-nav-3", "step-nav-4", "goto-step-3", "goto-step-4", "execute"]) {
    const button = $(`#${id}`);
    if (button) button.disabled = pending;
  }
}

async function goToStep(step) {
  const matchingRevision = ++state.matchingRevision;
  const viewRevision = state.viewRevision;
  state.matchingCheck = null;
  state.matchingConflicts = 0;
  matchingPending(false);
  for (const id of ["matching-check-step3", "matching-check-step4"]) {
    const element = $(`#${id}`);
    if (element) element.replaceChildren();
  }
  if (step > 1 && (!state.imports.shipments || !state.imports.charges)) {
    notice("Validá los archivos de operaciones y cargos antes de continuar.", true);
    return;
  }
  if (step > 2) {
    if (state.agreementReadPending) {
      notice("Esperá a que termine de cargar el acuerdo antes de verificar.", true);
      return;
    }
    try {
      const agreements = JSON.parse($("#agreements")?.value || "[]");
      if (!Array.isArray(agreements) || !agreements.length) throw new Error();
    } catch {
      notice("Seleccioná un acuerdo válido antes de verificar el lote.", true);
      return;
    }
    matchingPending(true);
    try {
      const dataset = auditDataset();
      const signature = matchingSignature(dataset);
      const check = await post("/api/audit/preflight", dataset);
      if (matchingRevision !== state.matchingRevision || viewRevision !== state.viewRevision) return;
      if (signature !== matchingSignature(auditDataset())) {
        notice("El lote cambió durante la verificación. Volvé a verificarlo antes de continuar.", true);
        return;
      }
      state.matchingCheck = signature;
      state.matchingConflicts = check.total_issues + check.skipped_charges;
      // A successful retry replaces the failed check; do not leave a stale error toast.
      const previousNotice = $("#notice");
      if (previousNotice) previousNotice.hidden = true;
      clearTimeout(notice.timer);
      const warning = state.matchingConflicts ? `
        <section class="matching-warning">
          <strong>${state.matchingConflicts} vinculación(es) requieren revisión</strong>
          <p>${check.counts.invalid} inválida(s), ${check.counts.conflict} contradictoria(s), ${check.counts.ambiguous} ambigua(s), ${check.counts.unmatched} sin operación encontrada y ${check.counts.uncorroborated} sin corroboración.</p>
          <p>Los cargos señalados no confirmarán diferencias. Tampoco los grupos de sus operaciones candidatas. Corregí la vinculación o
          el formato en Acuerdo; también podés guardar la auditoría con esos casos en revisión.</p>
          ${check.skipped_charges ? `<p>${check.skipped_charges} cargo(s) no se pudieron vincular por un acuerdo, transportista o moneda incompatibles. Revisá esos datos; la auditoría conservará el motivo de cada caso.</p>` : ""}
          ${matchingConflictDetails(check.issues, dataset)}
          ${check.total_issues > check.issues.length ? `<p>Se muestran ${check.issues.length} de ${check.total_issues} incidencias de vinculación. La auditoría conservará el detalle de todas.</p>` : ""}
        </section>` : "<p>Vinculaciones comprobadas con las claves disponibles: no se encontraron incidencias. Las reglas, vigencias y evidencias se evaluarán al auditar.</p>";
      for (const id of ["matching-check-step3", "matching-check-step4"]) $("#" + id).innerHTML = warning;
    } catch (error) {
      if (matchingRevision === state.matchingRevision && viewRevision === state.viewRevision) notice(error.message, true);
      return;
    } finally {
      if (matchingRevision === state.matchingRevision && viewRevision === state.viewRevision) matchingPending(false);
    }
  }
  // Sync label
  const labelInput = $("#audit-label");
  if (labelInput && labelInput.value.trim()) {
    state.auditLabel = labelInput.value.trim();
  }
  const l3 = $("#audit-label-step3");
  if (l3) l3.value = state.auditLabel;
  const l4 = $("#step4-audit-label");
  if (l4) l4.textContent = state.auditLabel || "Sin título";

  state.wizardStep = step;

  // Update step indicators
  for (let i = 1; i <= 4; i++) {
    const el = $(`#step-nav-${i}`);
    if (el) {
      el.className = `wizard-step-item ${state.wizardStep === i ? "active" : state.wizardStep > i ? "completed" : ""}`;
      const circle = el.querySelector(".wizard-circle");
      if (circle) circle.textContent = state.wizardStep > i ? "✓" : i;
    }
    const panel = $(`#step-panel-${i}`);
    if (panel) panel.classList.toggle("hidden", i !== step);
  }

  // Update compact step summary bars for completed steps
  const sum1 = $("#step-summary-1");
  const sum2 = $("#step-summary-2");
  const sum3 = $("#step-summary-3");

  if (sum1) {
    if (step > 1) {
      const sImp = state.imports.shipments;
      const cImp = state.imports.charges;
      const sCount = sImp?.accepted !== undefined ? sImp.accepted : 0;
      const cCount = cImp?.accepted !== undefined ? cImp.accepted : 0;
      const totalRej = (sImp?.rejected?.length || 0) + (cImp?.rejected?.length || 0);
      const s1Text = $("#step-summary-1-text");
      if (s1Text) {
        s1Text.innerHTML = `<strong>${sCount} operaciones</strong> · <strong>${cCount} cargos</strong> · ${totalRej} rechazos`;
      }
      sum1.classList.remove("hidden");
    } else {
      sum1.classList.add("hidden");
    }
  }

  if (sum2) {
    if (step > 2) {
      const s2Text = $("#step-summary-2-text");
      if (s2Text) s2Text.innerHTML = agreementSummary(auditDataset().agreements);
      sum2.classList.remove("hidden");
    } else {
      sum2.classList.add("hidden");
    }
  }

  if (sum3) {
    if (step > 3) {
      const sCount = state.imports.shipments?.accepted || 0;
      const cCount = state.imports.charges?.accepted || 0;
      const issueCount = (state.imports.shipments?.issues?.length || 0) + (state.imports.charges?.issues?.length || 0);
      const s3Text = $("#step-summary-3-text");
      if (s3Text) {
        const verification = state.matchingConflicts
          ? `Lote con <strong>${state.matchingConflicts} vinculación(es) en revisión</strong> (${sCount} operaciones, ${cCount} cargos)`
          : `Vinculaciones comprobadas (${sCount} operaciones, ${cCount} cargos listos para auditar)`;
        s3Text.innerHTML = `${verification} · ${issueCount} incidencia(s) de importación; editar para ver detalle`;
      }
      sum3.classList.remove("hidden");
    } else {
      sum3.classList.add("hidden");
    }
  }

  if (step === 3) {
    updateStep3Summaries();
  }
}

function updateStep3Summaries() {
  const sImp = state.imports.shipments;
  const cImp = state.imports.charges;

  const importSummary = (result, title, role) => result
    ? `<p class="verify-import-count">✓ ${result.accepted} filas aceptadas · ${result.rejected.length} rechazadas</p>
       <p class="muted verify-import-file">Archivo: ${esc(result.filename)} (${result.records.length} registros)</p>
       ${renderImportIssues(result.issues, role)}`
    : `<p class="verify-import-missing">⚠ Archivo de ${title} aún no validado en Paso 1.</p>`;

  const sContainer = $("#verify-shipments-summary");
  if (sContainer) sContainer.innerHTML = importSummary(sImp, "operaciones", "shipments");

  const cContainer = $("#verify-charges-summary");
  if (cContainer) cContainer.innerHTML = importSummary(cImp, "cargos", "charges");
  bindImportIssues($("#step-panel-3"));
}

function renderImportIssues(issues, role) {
  if (!issues?.length) return '<p class="verify-no-issues">Sin incidencias de importación.</p>';
  const warnings = issues.filter((issue) => issue.category === "warning").length;
  return `<details class="import-issues" data-role="${role}"><summary>${issues.length} incidencia(s) de importación (${warnings} advertencia(s)); ver detalle</summary>
    <div class="import-issue-page"></div></details>`;
}

function bindImportIssues(container) {
  container.querySelectorAll(".import-issues").forEach((details) => {
    const issues = state.imports[details.dataset.role].issues;
    const body = $(".import-issue-page", details);
    const size = 50;
    const pages = Math.ceil(issues.length / size);
    let page = 0;
    const render = () => {
      if (!details.open) {
        body.replaceChildren();
        return;
      }
      const start = page * size;
      body.innerHTML = `<p role="status">Incidencias ${start + 1}–${Math.min(start + size, issues.length)} de ${issues.length}</p>
        <ol start="${start + 1}">${issues.slice(start, start + size).map((issue) => `<li>${esc(issue.message)}</li>`).join("")}</ol>
        ${pages > 1 ? `<div class="issue-navigation">
          <button type="button" class="btn small issue-prev" ${page === 0 ? "disabled" : ""}>Anteriores</button>
          <label>Página <input class="issue-page-number" aria-label="Página de incidencias" type="number" min="1" max="${pages}" value="${page + 1}"> de ${pages}</label>
          <button type="button" class="btn small issue-next" ${page + 1 === pages ? "disabled" : ""}>Siguientes</button>
        </div>` : ""}`;
      if (pages > 1) {
        $(".issue-prev", body).onclick = () => { page -= 1; render(); };
        $(".issue-next", body).onclick = () => { page += 1; render(); };
        $(".issue-page-number", body).onchange = (event) => {
          const requested = Number(event.target.value);
          if (Number.isInteger(requested) && requested >= 1 && requested <= pages) page = requested - 1;
          render();
        };
      }
    };
    details.ontoggle = render;
  });
}

function renderDropzoneSection(role, title, subtitle) {
  const configs = state.configs.filter(
    (c) => c.kind === "mapping" && c.payload.entity === role,
  );
  return `
    <div class="file-upload-block">
      <div class="ui-marginbottom-ae01e5f4">
        <h3 class="ui-margin-3165a35a">
          <span>${title}</span>
          <span class="file-subtitle">${subtitle}</span>
        </h3>
      </div>

      <!-- Custom Dropzone (No input nativo antiestético) -->
      <div class="dropzone-container">
        <div class="dropzone" id="dropzone-${role}">
          <div class="dropzone-icon">⇪</div>
          <div class="dropzone-title">Arrastrá el archivo acá o seleccioná uno</div>
          <div class="dropzone-hint">CSV, XLSX o XLS</div>
          <!-- Hidden standard file input -->
          <input id="file-${role}" type="file" accept=".csv,.xlsx,.xls" class="sr-only-file">
        </div>

        <div id="file-loaded-${role}" class="file-loaded-card hidden">
          <div class="file-loaded-info">
            <span class="ui-fontsize-d64c8cb3">📄</span>
            <div>
              <strong id="file-name-${role}" class="ui-fontsize-6c0edc58"></strong>
              <div id="file-meta-${role}" class="muted ui-fontsize-c42f23b8"></div>
            </div>
          </div>
          <button type="button" class="btn small subtle" id="change-file-${role}">Cambiar archivo</button>
        </div>
      </div>

      <!-- Formato reconocido / Configurar columnas -->
      <div id="format-box-${role}" class="format-recognition hidden ui-margintop-a33b8fc2">
        <div class="ui-display-8ba0c206">
          <span class="format-icon" id="format-icon-${role}">✓</span>
          <div>
            <div id="format-title-${role}" class="ui-fontweight-0e4e2896"></div>
            <div id="format-sub-${role}" class="muted ui-fontsize-c42f23b8"></div>
          </div>
        </div>
        <button type="button" class="btn subtle small" id="toggle-mapping-${role}">Configurar columnas</button>
      </div>

      <!-- Panel de configuración de columnas (colapsado por defecto) -->
      <div id="columns-panel-${role}" class="columns-panel hidden ui-margintop-a33b8fc2">
        <div class="field ui-margin-38965f9b">
          <label for="saved-${role}" class="ui-fontsize-2ca3a889">Seleccionar formato guardado</label>
          <select id="saved-${role}" class="ui-fontsize-998d0b51">
            <option value="">Seleccionar o autodetectar formato…</option>
            ${configs.map((c) => `<option value="${c.hash}">${esc(c.name)}</option>`).join("")}
          </select>
        </div>
      </div>

      <!-- Modo avanzado JSON colapsado -->
      <div class="advanced-toggle ui-margintop-36e81f86">
        <div class="ui-display-5ffb91a2">
          <button class="btn subtle small ui-fontsize-6e744f89" type="button" id="toggle-advanced-${role}">
            ▸ Opciones avanzadas: mapping JSON manual
          </button>
        </div>
        <div id="advanced-mapping-body-${role}" class="panel-advanced-body hidden ui-margintop-a33b8fc2">
          <input id="mapping-file-${role}" type="file" accept=".json" aria-label="Cargar mapping de ${title}" class="ui-marginbottom-467b3b62">
          <label for="mapping-${role}" class="ui-fontsize-c42f23b8">Mapping JSON</label>
          <textarea id="mapping-${role}" rows="5" spellcheck="false" placeholder="Pegar definición JSON de columnas" class="ui-fontsize-09761da4"></textarea>
        </div>
      </div>

      <div class="ui-margintop-1d436efc">
        <button class="btn ui-width-9ccc4ca9" id="validate-${role}">Validar ${title.toLowerCase()}</button>
      </div>

      <div class="import-result ui-background-c7a1b982" id="result-${role}">
        Validar para ver filas aceptadas, rechazos y origen de los datos.
      </div>
    </div>
  `;
}

function setupStep1Handlers() {
  const auditLabelInput = $("#audit-label");
  if (auditLabelInput) {
    auditLabelInput.oninput = (e) => {
      state.auditLabel = e.target.value.trim();
    };
  }

  for (const role of ["shipments", "charges"]) {
    const fileInput = $(`#file-${role}`);
    const dropzone = $(`#dropzone-${role}`);
    const changeFileBtn = $(`#change-file-${role}`);
    const toggleMappingBtn = $(`#toggle-mapping-${role}`);
    const toggleAdvancedBtn = $(`#toggle-advanced-${role}`);
    const columnsPanel = $(`#columns-panel-${role}`);
    const advancedBody = $(`#advanced-mapping-body-${role}`);

    if (dropzone && fileInput) {
      dropzone.onclick = () => fileInput.click();

      ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add("dragover");
        });
      });

      ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove("dragover");
        });
      });

      dropzone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length) {
          fileInput.files = files;
          handleFileSelected(role, files[0]);
        }
      });

      fileInput.onchange = () => {
        if (fileInput.files.length) {
          handleFileSelected(role, fileInput.files[0]);
        }
      };
    }

    if (changeFileBtn && fileInput) {
      changeFileBtn.onclick = () => fileInput.click();
    }

    if (toggleMappingBtn && columnsPanel) {
      toggleMappingBtn.onclick = () => {
        columnsPanel.classList.toggle("hidden");
      };
    }

    if (toggleAdvancedBtn && advancedBody) {
      toggleAdvancedBtn.onclick = () => {
        advancedBody.classList.toggle("hidden");
      };
    }

    const configs = state.configs.filter(
      (c) => c.kind === "mapping" && c.payload.entity === role,
    );

    $(`#saved-${role}`).onchange = (event) => {
      cancelMappingRead(role);
      const found = configs.find((c) => c.hash === event.target.value);
      if (found) {
        state.mappingSource[role] = "saved";
        $(`#mapping-${role}`).value = JSON.stringify(found.payload, null, 2);
        updateFormatBox(role, true, found.name);
      } else {
        state.mappingSource[role] = null;
        $(`#mapping-${role}`).value = "";
        updateFormatBox(role, false);
      }
      invalidateImport(role);
    };

    $(`#mapping-file-${role}`).onchange = (event) =>
      busy(null, async () => {
        const file = event.target.files[0];
        if (!file) return;
        cancelMappingRead(role);
        invalidateImport(role);
        const revision = state.mappingRevision[role];
        const viewRevision = state.viewRevision;
        $(`#mapping-${role}`).value = "";
        updateManualFormat(role);
        state.mappingReadPending[role] = true;
        syncValidationButton(role);
        $(`#format-title-${role}`).textContent = "Leyendo mapping manual…";
        try {
          const content = await file.text();
          if (revision !== state.mappingRevision[role] || viewRevision !== state.viewRevision) return;
          $(`#mapping-${role}`).value = content;
          updateManualFormat(role);
          invalidateImport(role);
        } catch {
          if (revision === state.mappingRevision[role] && viewRevision === state.viewRevision) {
            notice("No se pudo leer el mapping. Volvé a seleccionar el archivo o elegí un formato guardado y validá nuevamente.", true);
          }
        } finally {
          if (revision === state.mappingRevision[role] && viewRevision === state.viewRevision) {
            state.mappingReadPending[role] = false;
            updateManualFormat(role);
            syncValidationButton(role);
          }
        }
      });

    $(`#mapping-${role}`).oninput = () => {
      cancelMappingRead(role);
      updateManualFormat(role);
      invalidateImport(role);
    };

    $(`#validate-${role}`).onclick = (event) => {
      const validationView = state.viewRevision;
      state.importPending[role] = true;
      return busy(event.target, async () => {
        if (state.mappingReadPending[role]) throw new Error("Esperá a que termine de cargar el mapping.");
        const file = fileInput.files[0];
        if (!file) throw new Error("Seleccionar el archivo a importar.");
        const mapping = JSON.parse($(`#mapping-${role}`).value || "{}");
        const revision = state.importRevision[role];
        const viewRevision = state.viewRevision;
        if (mapping.entity !== role)
          throw new Error(
            "El mapping seleccionado corresponde a otro tipo de archivo.",
          );
        const form = new FormData();
        form.append("file", file);
        form.append("mapping", JSON.stringify(mapping));
        const result = await post("/api/import", form);
        if (revision !== state.importRevision[role] || viewRevision !== state.viewRevision) return;
        state.imports[role] = result;
        $(`#result-${role}`).innerHTML = `
          <strong class="ui-color-e4fa61d1">✓ ${result.accepted} filas aceptadas · ${result.rejected.length} rechazadas</strong>
          <p class="muted ui-margin-138901e5">Hoja: ${esc(result.sheet)} · Archivo original conservado</p>
          ${renderImportIssues(result.issues, role)}
          <details class="ui-margintop-a33b8fc2">
            <summary>Vista previa del origen (${result.preview.length} filas)</summary>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>${result.headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr>
                </thead>
                <tbody>
                  ${result.preview.map((row) => `<tr>${result.headers.map((h) => `<td>${esc(row.values[h])}</td>`).join("")}</tr>`).join("")}
                </tbody>
              </table>
            </div>
          </details>
        `;
        bindImportIssues($(`#result-${role}`));
        notice(
          `Validación de ${role === "shipments" ? "operaciones" : "cargos"} completada: ${result.accepted} aceptadas, ${result.rejected.length} rechazadas y ${result.issues.length} incidencias. Revisá el detalle antes de continuar.`,
        );
      }).finally(() => {
        if (validationView === state.viewRevision) {
          state.importPending[role] = false;
          syncValidationButton(role);
        }
      });
    };
  }
}

function syncValidationButton(role) {
  const button = $(`#validate-${role}`);
  if (button) button.disabled = state.mappingReadPending[role] || state.importPending[role];
}

function cancelMappingRead(role) {
  state.mappingRevision[role] += 1;
  state.mappingReadPending[role] = false;
  syncValidationButton(role);
}

function handleFileSelected(role, file) {
  const loadedCard = $(`#file-loaded-${role}`);
  const dropzone = $(`#dropzone-${role}`);
  const fileName = $(`#file-name-${role}`);
  const fileMeta = $(`#file-meta-${role}`);

  if (loadedCard && fileName && fileMeta && dropzone) {
    const sizeStr = file.size >= 1048576
      ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
      : `${(file.size / 1024).toFixed(1)} KB`;
    fileName.textContent = `${file.name} · ${sizeStr} ✓`;
    fileMeta.textContent = `Archivo listo para procesar en este equipo`;
    loadedCard.classList.remove("hidden");
    dropzone.classList.add("hidden");
  }

  // Pre-fill suggested audit label if empty
  const labelInput = $("#audit-label");
  if (labelInput && !labelInput.value && file.name) {
    const baseName = file.name.replace(/\.[^/.]+$/, "");
    state.auditLabel = `Auditoría ${baseName}`;
    labelInput.value = state.auditLabel;
  }

  // Smart format detection
  const configs = state.configs.filter(
    (c) => c.kind === "mapping" && c.payload.entity === role,
  );
  if (configs.length === 1 && !$(`#saved-${role}`).value) {
    if (state.mappingSource[role] === "manual") {
      updateManualFormat(role);
    } else {
      $(`#saved-${role}`).value = configs[0].hash;
      $(`#mapping-${role}`).value = JSON.stringify(configs[0].payload, null, 2);
      state.mappingSource[role] = "saved";
      updateFormatBox(role, true, configs[0].name);
    }
  } else if ($(`#saved-${role}`).value) {
    const selected = configs.find((c) => c.hash === $(`#saved-${role}`).value);
    if (selected && state.mappingSource[role] !== "manual") updateFormatBox(role, true, selected.name);
    else updateManualFormat(role);
  } else if (state.mappingSource[role] === "manual") {
    updateManualFormat(role);
  } else {
    updateFormatBox(role, false);
  }

  invalidateImport(role);
}

function updateFormatBox(role, recognized, formatName = "") {
  const box = $(`#format-box-${role}`);
  const icon = $(`#format-icon-${role}`);
  const title = $(`#format-title-${role}`);
  const sub = $(`#format-sub-${role}`);
  const columnsPanel = $(`#columns-panel-${role}`);

  if (!box) return;
  box.classList.remove("hidden");

  if (recognized) {
    box.classList.add("recognized");
    if (icon) icon.textContent = "✓";
    if (title) title.textContent = `Formato seleccionado: ${formatName}`;
    if (sub) sub.textContent = "Validá el archivo para comprobar sus columnas";
    if (columnsPanel) {
      columnsPanel.classList.add("hidden");
    }
  } else {
    box.classList.remove("recognized");
    if (icon) icon.textContent = "⚙";
    if (title) title.textContent = "Configurar columnas";
    if (sub) sub.textContent = "Elegí o personalizá el formato de columnas";
    if (columnsPanel) {
      columnsPanel.classList.remove("hidden");
    }
  }
}

function updateManualFormat(role) {
  state.mappingSource[role] = "manual";
  const saved = $(`#saved-${role}`);
  if (saved) saved.value = "";
  let name = "JSON pendiente de validar";
  try {
    const mapping = JSON.parse($(`#mapping-${role}`).value);
    if (mapping.id) name = `${mapping.id}${mapping.version ? `@${mapping.version}` : ""}`;
  } catch {
    // Keep the source explicit while validation reports JSON syntax errors.
  }
  updateFormatBox(role, true, name);
  $(`#format-box-${role}`)?.classList.remove("recognized");
  const icon = $(`#format-icon-${role}`);
  if (icon) icon.textContent = "✎";
  const title = $(`#format-title-${role}`);
  const sub = $(`#format-sub-${role}`);
  if (title) title.textContent = state.mappingReadPending[role] ? "Leyendo mapping manual…" : `Mapping manual: ${name}`;
  if (sub) sub.textContent = "Validá el archivo para comprobar este JSON";
}

function invalidateImport(role) {
  state.importRevision[role] += 1;
  delete state.imports[role];
  const result = $(`#result-${role}`);
  if (result)
    result.textContent =
      "Validar para ver filas aceptadas, rechazos y origen de los datos.";
}

/* ==========================================================================
   ACUERDOS Y FORMATOS (INTERMEDIA + MODO AVANZADO)
   ========================================================================== */
async function showConfigs() {
  nav("configs");
  const revision = state.viewRevision;
  const configs = await api("/api/configs");
  if (revision !== state.viewRevision) return;
  state.configs = configs;
  main.innerHTML = heading(
    "CONFIGURACIÓN VERSIONADA",
    "Acuerdos y formatos",
    "Los cambios crean versiones inmutables por contenido. Las auditorías anteriores preservan intacta su configuración.",
    `<button class="btn" id="import-config-btn">Importar configuración</button>
     <button class="btn primary" id="toggle-create-config">＋ Nueva versión (Modo avanzado)</button>
     <input type="file" id="import-config-file" accept=".json" class="sr-only-file">`,
  );

  const agreements = state.configs.filter((c) => c.kind === "agreement");
  const mappings = state.configs.filter((c) => c.kind === "mapping");

  main.innerHTML += `
    <div class="grid2">
      <!-- Acuerdos Guardados -->
      <section class="panel">
        <h2>Acuerdos guardados (${agreements.length})</h2>
        <p class="muted">Términos contractuales y reglas pactadas con los transportistas.</p>
        <div class="run-list ui-display-7e9ff71e">
          ${agreements
            .map(
              (c) => `
              <div class="run-card-rich ui-padding-10702f48">
                <div class="ui-display-5ffb91a2">
                  <strong class="ui-fontsize-e49c04bf">${esc(c.name)}</strong>
                  <span class="badge PASS">Válido ✓</span>
                </div>
                <div class="ui-fontsize-ecee40b8">
                  Transportista: <strong>${esc(c.payload?.carrier || "Transportista pactado")}</strong>
                </div>
                <div class="ui-fontsize-ecee40b8">
                  Versiones: <strong>${c.payload?.versions?.length || 0}</strong> · Moneda: <strong>${esc(c.payload?.currency || "ARS")}</strong> · <strong>${agreementRuleCount(c.payload)} regla(s) configuradas</strong>
                </div>
                <details class="agreement-summary-detail"><summary>Ver vigencias y reglas</summary><ul>${agreementVersionList(c.payload)}</ul></details>
                <div class="ui-display-3e08c89c">
                  <div class="actions">
                    <button class="btn small" data-view-config="${c.hash}">Ver</button>
                    <button class="btn small" data-clone-config="${c.hash}">Duplicar versión</button>
                  </div>
                </div>
              </div>
            `,
            )
            .join("") || '<p class="muted">No hay acuerdos registrados.</p>'}
        </div>
      </section>

      <!-- Mappings Guardados -->
      <section class="panel">
        <h2>Formatos de columnas (${mappings.length})</h2>
        <p class="muted">Mapeos de CSV y planillas de cálculo de transportistas.</p>
        <div class="run-list ui-display-7e9ff71e">
          ${mappings
            .map(
              (c) => `
              <div class="run-card-rich ui-padding-10702f48">
                <div class="ui-display-5ffb91a2">
                  <strong class="ui-fontsize-e49c04bf">${esc(c.name)}</strong>
                  <span class="badge ui-background-c0b28249">Entidad: ${esc(c.payload?.entity || "archivo")}</span>
                </div>
                <div class="ui-fontsize-ecee40b8">
                  Columnas mapeadas: <strong>${c.payload?.columns?.length || 0}</strong> · Delimitador: <code>${esc(c.payload?.delimiter || ",")}</code>
                </div>
                <div class="ui-display-3e08c89c">
                  <button class="btn small" data-view-config="${c.hash}">Ver en editor →</button>
                </div>
              </div>
            `,
            )
            .join("") || '<p class="muted">No hay formatos de columnas guardados.</p>'}
        </div>
      </section>
    </div>

    <!-- Editor de Configuración (Modo Avanzado colapsable) -->
    <details id="advanced-config-panel" class="panel ui-margintop-04bbec5e">
      <summary class="ui-fontsize-adca191a">Modo avanzado: Editor JSON de acuerdos y formatos</summary>
      <p class="hint">Al guardar, se genera una nueva versión por hash SHA-256 inmutable. Los datos históricos no se modifican.</p>
      <div class="field ui-margintop-8d842990">
        <label for="config-kind">Tipo de configuración</label>
        <select id="config-kind" class="ui-maxwidth-85b149cc">
          <option value="agreement">Acuerdo contractual</option>
          <option value="mapping">Formato de columnas (Mapping)</option>
        </select>
      </div>
      <div class="field">
        <label for="config-data">Definición JSON</label>
        <textarea id="config-data" rows="14" spellcheck="false">{}</textarea>
      </div>
      <div class="actions">
        <button class="btn primary" id="save-config">Validar y guardar versión inmutable</button>
      </div>
    </details>
  `;

  $("#import-config-btn").onclick = () => $("#import-config-file").click();

  $("#import-config-file").onchange = (event) =>
    busy(null, async () => {
      const file = event.target.files[0];
      if (!file) return;
      const text = await file.text();
      const parsed = JSON.parse(text);
      const kind = parsed.entity ? "mapping" : "agreement";
      $("#config-kind").value = kind;
      $("#config-data").value = JSON.stringify(parsed, null, 2);
      const details = $("#advanced-config-panel");
      if (details) details.open = true;
      $("#config-data").scrollIntoView({ behavior: "smooth" });
      notice(`Archivo cargado en editor como ${kind === "mapping" ? "formato de columnas" : "acuerdo"}. Revisá y guardá para crear la versión.`);
    });

  $("#toggle-create-config").onclick = () => {
    const details = $("#advanced-config-panel");
    if (details) {
      details.open = !details.open;
      if (details.open) details.scrollIntoView({ behavior: "smooth" });
    }
  };

  document.querySelectorAll("[data-view-config]").forEach((button) => {
    button.onclick = () => {
      const c = state.configs.find((item) => item.hash === button.dataset.viewConfig);
      if (c) {
        $("#config-kind").value = c.kind;
        $("#config-data").value = JSON.stringify(c.payload, null, 2);
        const details = $("#advanced-config-panel");
        if (details) details.open = true;
        $("#config-data").scrollIntoView({ behavior: "smooth" });
      }
    };
  });

  document.querySelectorAll("[data-clone-config]").forEach((button) => {
    button.onclick = () => {
      const c = state.configs.find((item) => item.hash === button.dataset.cloneConfig);
      if (c) {
        const cloned = structuredClone(c.payload);
        if (cloned.name) cloned.name += " (nueva versión)";
        $("#config-kind").value = c.kind;
        $("#config-data").value = JSON.stringify(cloned, null, 2);
        const details = $("#advanced-config-panel");
        if (details) details.open = true;
        $("#config-data").scrollIntoView({ behavior: "smooth" });
        notice("Copia cargada en el editor. Modificá las reglas o vigencia y guardá la nueva versión.");
      }
    };
  });

  $("#save-config").onclick = (event) =>
    busy(event.target, async () => {
      await post(
        "/api/configs/" + $("#config-kind").value,
        JSON.parse($("#config-data").value),
      );
      await showConfigs();
      notice(
        "Configuración validada y conservada como una versión nueva por contenido.",
      );
    });
}

/* ==========================================================================
   GUÍA DE TRABAJO (ACTUALIZADA AL BUNDLE V2)
   ========================================================================== */
function showGuide() {
  nav("guide");
  main.innerHTML =
    heading(
      "DE LOS ARCHIVOS A LA DECISIÓN",
      "Un control que se puede reconstruir",
      "Guía metodológica para trabajar con un acuerdo real y auditorías de precisión.",
    ) +
    `<div class="panel guide ui-maxwidth-5882c1c5">
      <ol class="ui-paddingleft-579ff797">
        <li><strong>Conservar los originales.</strong> Reuní operaciones, liquidación, contrato y documentos del período ya controlado por el cliente en sus formatos nativos.</li>
        <li><strong>Configurar formatos.</strong> Indicá exactamente hoja, encabezados, separadores, fechas y equivalencias de conceptos. Revisá todas las filas rechazadas.</li>
        <li><strong>Confirmar el acuerdo.</strong> El cliente debe validar vigencias, fecha relevante, unidades, fórmulas, moneda, redondeos, tolerancias y evidencia requerida. No deduzcas estas reglas del importe cobrado.</li>
        <li><strong>Ejecutar y explicar.</strong> Abrí cada hallazgo para revisar matching, versión seleccionada, cálculo aritmético y procedencia.</li>
        <li><strong>Resolver conservando la historia.</strong> Registrá responsable, decisión y motivo. Aportar evidencia crea una nueva corrida sin sobreescribir la anterior.</li>
        <li><strong>Comparar sin prometer ahorro.</strong> Separá diferencias conocidas y nuevas, falsos positivos, casos indeterminados y tiempo de preparación y revisión.</li>
        <li><strong>Exportar y respaldar.</strong> El paquete conserva los originales, los datos normalizados, el resultado, las decisiones y los reportes verificables.</li>
      </ol>
    </div>
    <div class="grid2 ui-maxwidth-5882c1c5">
      ${Object.entries(labels)
        .map(
          ([key, label]) => `
        <div class="panel ui-margin-38965f9b">
          <div class="ui-display-225efa96">
            ${badge(key)}
            <strong class="ui-fontsize-e49c04bf">${label}</strong>
          </div>
          <p class="muted ui-fontsize-81ebc5d3">
            ${
              key === "PASS"
                ? "El importe facturado coincide con el cálculo respaldado dentro de la tolerancia."
                : key === "FAIL"
                  ? "El importe difiere de la fórmula o tarifa contractual demostrable."
                  : key === "REVIEW"
                    ? "Se requiere confirmación humana sobre vigencia, evidencia o autorización."
                    : "No es posible determinar el resultado por falta de reglas o barrera de moneda."
            }
          </p>
        </div>
      `,
        )
        .join("")}
    </div>
  `;
}

/* ==========================================================================
   INICIALIZACIÓN
   ========================================================================== */
async function init() {
  document
    .querySelectorAll(".nav")
    .forEach((button) =>
      button.addEventListener("click", () => {
        const v = button.dataset.view;
        if (v === "audits") showRuns();
        else if (v === "new") showNew();
        else if (v === "configs") showConfigs();
        else if (v === "guide") showGuide();
      }),
    );

  try {
    const session = await api("/api/session");
    state.token = session.token;
    await showRuns();
  } catch (error) {
    main.innerHTML = `<div class="panel empty">
      <h2>Error de conexión local</h2>
      <p class="muted">No fue posible conectarse al servidor local de Calibre. Verificá que la terminal siga activa.</p>
      <code>${esc(error.message)}</code>
    </div>`;
  }
}

init();

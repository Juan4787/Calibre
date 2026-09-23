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
      <div class="symbol" aria-hidden="true" style="font-size:44px; color:var(--accent);">▤</div>
      <h2>Del cargo a la evidencia.</h2>
      <p class="muted">Importá operaciones y liquidaciones, seleccioná el acuerdo y reconstruí el importe esperado. Todo se procesa de forma segura en este equipo.</p>
      <div class="actions centered" style="justify-content:center; margin-top:20px;">
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
        <div style="font-size:22px; line-height:1;">ⓘ</div>
        <div>
          <strong>La certeza también se audita.</strong>
          <p style="margin:2px 0 0;">Una diferencia determinada requiere reglas y datos suficientes. La revisión humana y los casos indeterminados no representan ahorro.</p>
        </div>
      </div>
      <div class="search-toolbar">
        <input id="search-runs" type="text" placeholder="Buscar por transportista, período o identificador…" value="${esc(state.runSearch || "")}" />
        <button class="btn" id="demo">Ejecutar demostración ficticia</button>
      </div>
      <div id="runs-items" class="run-list" style="display:flex; flex-direction:column; gap:16px;"></div>
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
    listContainer.innerHTML = `<div class="panel" style="text-align:center; padding:32px 20px; color:var(--muted);">
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
    (!summary.import_complete
      ? `<div class="banner warning">
          <div style="font-size:22px;">⚠</div>
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
      <span class="muted" style="margin-left:auto; font-size:13px;">La diferencia determinada no equivale a ahorro ni recupero.</span>
      <button class="btn small" id="replay">Verificar reproducción</button>
    </div>

    <div class="panel table-panel">
      <div class="table-head">
        <div>
          <h2>Detalle de cargos auditados</h2>
          <p class="muted" style="margin:4px 0 0; font-size:13px;">Cobertura con reglas completas: ${coverage}% (${summary.determinable_findings} de ${count})</p>
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

    <div class="actions" style="margin-top:24px;">
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
            <span class="muted" style="font-size:12px;">${esc(f.concept)} · ${f.charge_ids.length} cargo${f.charge_ids.length === 1 ? "" : "s"}</span>
          </td>
          <td>${badge(f.status)}</td>
          <td class="num">${esc(f.currency)} ${money(f.actual)}</td>
          <td class="num">${moneyOrStatus(f.expected, f.status)}</td>
          <td class="num" style="font-weight:750; color:${f.status === "FAIL" ? "var(--red)" : f.status === "REVIEW" ? "var(--amber)" : "inherit"};">
            ${moneyOrStatus(f.difference, f.status)}
            ${f.status === "REVIEW" ? '<br><small class="muted" style="font-size:11px;">Requiere revisión</small>' : ""}
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
    <p class="small-text" style="font-weight:600; margin:4px 0;">${esc(traceText(trace))}</p>
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

  const arithmeticStr = extractArithmeticSummary(f);

  $("#detail-content").innerHTML = `
    <!-- Top Status Banner -->
    <div class="star-status-pill ${f.status}">
      ${f.status === "FAIL" ? "DISCREPANCIA" : f.status === "PASS" ? "COINCIDE" : f.status === "REVIEW" ? "REVISIÓN HUMANA" : "INDETERMINADO"}
    </div>

    <div class="modal-header-star">
      <div class="modal-header-title">
        <div class="eyebrow" style="color:var(--accent);">EXPLICACIÓN DEL HALLAZGO</div>
        <h2 id="detail-title" style="margin:0; font-size:24px;">
          ${esc(references(f) || "Referencia sin vincular")} · ${esc(f.concept)}
        </h2>
        <div style="margin-top:6px;">
          ${badge(f.status)}
          <span class="muted" style="margin-left:10px; font-size:13px;">Acuerdo <strong>${esc(f.agreement || "Sin acuerdo")}</strong> · Versión <strong>${esc(f.version || "Sin versión aplicable")}</strong> · Regla <strong>${esc(f.rule || "Sin regla aplicable")}</strong></span>
        </div>
      </div>
      <button class="btn small" id="close-detail" aria-label="Cerrar explicación">Cerrar ✕</button>
    </div>

    <!-- Hero Financial Card (Facturado vs Esperado vs Diferencia) -->
    <div class="hero-financial-card detail-money">
      <div class="hero-fin-col">
        <label>FACTURADO LIQUIDADO · ${esc(f.currency)}</label>
        <div class="amount">${money(f.actual)}</div>
        <p class="muted" style="font-size:12px; margin:4px 0 0;">Según los cargos importados</p>
      </div>
      <div class="hero-fin-col">
        <label>ESPERADO SEGÚN ACUERDO</label>
        <div class="amount">${money(f.expected, f.status === "REVIEW" ? "Requiere revisión" : "No determinable")}</div>
        <p class="muted" style="font-size:12px; margin:4px 0 0;">${f.expected === null ? "Faltan datos o reglas para calcular" : "Resultado de la regla configurada"}</p>
      </div>
      <div class="hero-fin-col ${f.status === "FAIL" ? "highlight-fail" : f.status === "REVIEW" ? "highlight-review" : ""}">
        <label>DIFERENCIA CALCULADA</label>
        <div class="amount">${money(f.difference, f.status === "REVIEW" ? "Requiere revisión" : "No determinable")}</div>
        <p class="muted" style="font-size:12px; margin:4px 0 0;">${f.status === "FAIL" ? "Discrepancia determinada" : f.status === "REVIEW" ? "Diferencia sin confirmar" : f.status === "PASS" ? "Dentro de la tolerancia configurada" : "No se puede determinar la diferencia"}</p>
      </div>
    </div>

    <!-- Sections Grid: Por qué, Cálculo, Documentos -->
    <div class="finding-sections-grid">
      <!-- Por qué -->
      <div class="finding-card">
        <div class="finding-card-title">
          <span>ⓘ</span> Por qué
        </div>
        ${f.reasons.map((r) => `<p style="font-size:14px; line-height:1.5; margin:0 0 10px;">${esc(r)}</p>`).join("")}
        <div style="background:#f9faf7; border:1px solid var(--line); border-radius:6px; padding:10px 14px; font-size:13px; color:var(--ink-secondary); margin-top:14px;">
          Regla <strong>${esc(f.rule || "Sin regla aplicable")}</strong> · versión <strong>${esc(f.version || "Sin versión aplicable")}</strong>
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
        <div style="font-size:12px; font-weight:750; text-transform:uppercase; color:var(--muted); margin:14px 0 6px;">
          Registros y configuración utilizados:
        </div>
        <ul class="doc-checklist">
          ${documentsUsed.map((doc) => `<li class="doc-item"><span class="check">✓</span> <span>${esc(doc)}</span></li>`).join("")}
        </ul>
      </div>
    </div>

    <!-- Trazabilidad completa (secundario) -->
    <div style="padding: 0 32px 18px;">
      <details class="panel" style="margin:0;">
        <summary style="font-weight:750; color:var(--accent);">Cálculo ejecutado y decisiones de la regla (ver pasos matemáticos)</summary>
        <div style="margin-top:12px;">
          ${f.trace.map(traceHtml).join("") || "<p class='muted'>No hubo cálculo: primero se necesita resolver la vinculación.</p>"}
        </div>
      </details>
    </div>

    <div style="padding: 0 32px 24px;">
      <details class="panel" style="margin:0;">
        <summary style="font-weight:750; color:var(--accent);">Origen de cada dato (${records.length} registros celda por celda)</summary>
        <div class="table-wrap" style="margin-top:12px;">
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
        <section class="panel" style="margin:0;">
          <h3 style="margin-top:0;">Decisión humana</h3>
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
            <button class="btn primary" type="submit" style="width:100%;">Guardar decisión en expediente</button>
          </form>
        </section>

        <section class="panel" style="margin:0;">
          <h3 style="margin-top:0;">Historial de resoluciones</h3>
          <div style="max-height: 220px; overflow-y: auto; margin-bottom: 16px;">
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
          <details id="evidence-panel" style="border-top:1.5px solid var(--line); padding-top:16px;">
            <summary style="font-size:14px; font-weight:750; color:var(--ink);">Aportar evidencia y crear nueva corrida</summary>
            <p class="hint" style="margin-bottom:12px;">Permite adjuntar documentación que subsane una revisión. La corrida anterior permanece inmutable.</p>
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
              <button class="btn" type="submit" style="width:100%;">Auditar con esta evidencia</button>
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
async function showNew() {
  nav("new");
  const revision = state.viewRevision;
  state.imports = {};
  state.auditLabel = "";
  state.importRevision.shipments += 1;
  state.importRevision.charges += 1;
  state.wizardStep = 1;
  const configs = await api("/api/configs");
  if (revision !== state.viewRevision) return;
  state.configs = configs;

  renderWizard();
}

function renderWizard() {
  main.innerHTML = `
    <div class="wizard-header">
      <div class="eyebrow" style="color:var(--accent);">FLUJO GUIADO DE AUDITORÍA</div>
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
    <div id="wizard-summaries" style="margin-bottom:20px;">
      <div id="step-summary-1" class="step-summary-bar hidden" style="display:none;">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Datos</span>
          <span class="step-summary-desc" id="step-summary-1-text"></span>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-1">Editar</button>
      </div>
      <div id="step-summary-2" class="step-summary-bar hidden" style="display:none;">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Acuerdo</span>
          <span class="step-summary-desc" id="step-summary-2-text"></span>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-2">Editar</button>
      </div>
      <div id="step-summary-3" class="step-summary-bar hidden" style="display:none;">
        <div class="step-summary-info">
          <span class="step-summary-tag">✓ Verificación</span>
          <span class="step-summary-desc" id="step-summary-3-text">Integridad del lote verificada</span>
        </div>
        <button type="button" class="btn small subtle" id="reopen-step-3">Editar</button>
      </div>
    </div>

    <!-- Wizard Steps Content: All 4 panels preserved in DOM -->
    <div id="wizard-content">
      <!-- STEP 1: DATOS -->
      <div id="step-panel-1" class="wizard-panel">
        <div class="panel">
          <div style="margin-bottom:20px;">
            <label for="audit-label" style="font-size:14.5px; font-weight:750;">Nombre del período o lote</label>
            <input id="audit-label" type="text" placeholder="Ej.: Cierre de septiembre · Transportes Gómez" value="${esc(state.auditLabel || "")}" required style="max-width:560px;">
          </div>

          <div style="margin-bottom:16px;">
            <h2 style="margin:0 0 4px; font-size:20px;">Paso 1: Carga de Archivos</h2>
            <p class="muted" style="margin:0; font-size:13.5px;">Subí las operaciones realizadas (remitos o viajes) y los cargos facturados por el transportista.</p>
          </div>

          <div class="grid2" style="margin-top:16px;">
            ${renderDropzoneSection("shipments", "Operaciones", "Viajes, despachos o remitos")}
            ${renderDropzoneSection("charges", "Cargos liquidados", "Detalle de cargos y montos del transportista")}
          </div>

          <div class="actions" style="margin-top:24px; justify-content:flex-end;">
            <button class="btn primary" id="goto-step-2">Continuar a Acuerdo →</button>
          </div>
        </div>
      </div>

      <!-- STEP 2: ACUERDO -->
      <div id="step-panel-2" class="wizard-panel" style="display:none;">
        <div class="panel">
          <h2>Paso 2: Selección del Acuerdo Contractual</h2>
          <p class="muted">Elegí el tarifario pactado con el transportista para auditar los cargos.</p>

          <div class="run-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin:20px 0;">
            ${state.configs
              .filter((c) => c.kind === "agreement")
              .map(
                (c) => `
                <div class="agreement-card" data-hash="${c.hash}">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
                    <div>
                      <h4 class="agreement-card-title">${esc(c.name)}</h4>
                      <div class="agreement-card-carrier">Transportista: <strong>${esc(c.payload?.carrier || "Pactado")}</strong></div>
                    </div>
                    <span class="badge PASS">Válido ✓</span>
                  </div>
                  <div class="agreement-card-meta">
                    <span>Moneda <strong>${esc(c.payload?.currency || "ARS")}</strong></span>
                    <span>·</span>
                    <span>${Array.isArray(c.payload?.rules) ? c.payload.rules.length : 1} regla(s)</span>
                  </div>
                  <div style="display:flex; justify-content:flex-end; margin-top:14px;">
                    <button type="button" class="btn small primary select-agreement-btn" data-hash="${c.hash}">Seleccionar</button>
                  </div>
                </div>
              `,
              )
              .join("") || '<p class="muted">No hay acuerdos guardados. Cargá uno desde JSON.</p>'}
          </div>

          <div style="display:flex; gap:14px; align-items:flex-end; margin-top:16px; flex-wrap:wrap;">
            <div class="field" style="margin:0; flex:1; min-width:260px;">
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
            <div class="field" style="margin:0;">
              <label>Importar acuerdo JSON</label>
              <input type="file" id="agreement-file" accept=".json" style="padding:8px 10px; font-size:13px;">
            </div>
          </div>

          <div class="panel-advanced" style="margin-top:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <strong style="font-size:13.5px;">Modo avanzado: Editor de acuerdos y evidencia (JSON)</strong>
              <button class="btn subtle small" type="button" id="toggle-agreements">Mostrar/Ocultar JSON</button>
            </div>
            <div id="agreements-advanced-body" class="panel-advanced-body hidden">
              <label for="agreements">Acuerdos (lista JSON)</label>
              <textarea id="agreements" rows="7" spellcheck="false">[]</textarea>
              <div style="margin-top:10px;">
                <label for="evidence">Evidencia previa (lista JSON opcional)</label>
                <textarea id="evidence" rows="3">[]</textarea>
              </div>
              <div style="margin-top:10px;">
                <label for="coverage">Alcance por acuerdo (JSON)</label>
                <textarea id="coverage" rows="3">{}</textarea>
              </div>
            </div>
          </div>

          <div class="actions" style="margin-top:28px; justify-content:space-between;">
            <button class="btn" id="back-to-step-1">← Volver a Datos</button>
            <button class="btn primary" id="goto-step-3">Continuar a Verificación →</button>
          </div>
        </div>
      </div>

      <!-- STEP 3: VERIFICACIÓN -->
      <div id="step-panel-3" class="wizard-panel" style="display:none;">
        <div class="panel">
          <h2>Paso 3: Verificación Previa</h2>
          <p class="muted">Revisá la consistencia del lote antes de ejecutar el motor de auditoría determinista.</p>

          <div class="field" style="margin:16px 0;">
            <label for="audit-label-step3">Nombre de la auditoría</label>
            <input id="audit-label-step3" type="text" value="${esc(state.auditLabel || "")}" required style="max-width:560px;">
          </div>

          <div class="grid2" style="margin:16px 0;">
            <div style="padding:16px 18px; background:#f9fbf8; border:1px solid var(--line); border-radius:var(--radius-sm);">
              <h3 style="margin:0 0 6px; font-size:15px;">Operaciones preparadas</h3>
              <div id="verify-shipments-summary"></div>
            </div>
            <div style="padding:16px 18px; background:#f9fbf8; border:1px solid var(--line); border-radius:var(--radius-sm);">
              <h3 style="margin:0 0 6px; font-size:15px;">Cargos liquidados preparados</h3>
              <div id="verify-charges-summary"></div>
            </div>
          </div>

          <div class="banner info" style="margin:20px 0 0;">
            <div style="font-size:20px; line-height:1;">ⓘ</div>
            <div>
              <strong>Revisión de integridad garantizada</strong>
              <p style="margin:2px 0 0;">Las filas rechazadas o no identificadas no se omiten silenciosamente; se conservan como incidencias de datos para garantizar trazabilidad total.</p>
            </div>
          </div>

          <div class="actions" style="margin-top:28px; justify-content:space-between;">
            <button class="btn" id="back-to-step-2">← Volver a Acuerdo</button>
            <button class="btn primary" id="goto-step-4">Continuar a Ejecución →</button>
          </div>
        </div>
      </div>

      <!-- STEP 4: EJECUTAR -->
      <div id="step-panel-4" class="wizard-panel" style="display:none;">
        <div class="panel" style="text-align:center; padding:40px 24px;">
          <div style="font-size:44px; margin-bottom:12px;">⚡</div>
          <h2>Listo para auditar</h2>
          <p class="muted" style="max-width:560px; margin:0 auto 24px; font-size:14.5px; line-height:1.6;">
            Auditoría: <strong id="step4-audit-label">${esc(state.auditLabel || "Sin título")}</strong><br>
            El motor procesará los cálculos en este equipo de forma determinista, generando la cadena de decisión y los reportes exportables.
          </p>
          <button class="btn primary" id="execute" style="padding:15px 34px; font-size:15.5px; font-weight:750;">
            Ejecutar auditoría local →
          </button>
          <div style="margin-top:20px;">
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
    }
  };

  $("#agreement-file").onchange = (event) =>
    busy(null, async () => {
      const parsed = JSON.parse(await event.target.files[0].text());
      $("#agreements").value = JSON.stringify(
        Array.isArray(parsed) ? parsed : [parsed],
        null,
        2,
      );
      notice("Archivo de acuerdo cargado correctamente.");
    });

  $("#toggle-agreements").onclick = () => {
    const body = $("#agreements-advanced-body");
    if (body) {
      body.classList.toggle("hidden");
      body.style.display = body.classList.contains("hidden") ? "none" : "block";
    }
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
      if (!state.imports.shipments || !state.imports.charges)
        throw new Error(
          "Validar ambos archivos con sus columnas antes de ejecutar.",
        );
      const label = state.auditLabel || $("#audit-label")?.value.trim() || "Auditoría local";
      const values = Object.values(state.imports);
      const dataset = {
        label,
        shipments: state.imports.shipments.records,
        charges: state.imports.charges.records,
        agreements: JSON.parse($("#agreements")?.value || "[]"),
        evidence: JSON.parse($("#evidence")?.value || "[]"),
        coverage: JSON.parse($("#coverage")?.value || "{}"),
        mappings: values.map((r) => r.mapping),
        documents: Object.fromEntries(
          values.map((r) => [r.document, r.filename]),
        ),
        issues: values.flatMap((r) => r.issues),
      };
      const result = await post("/api/audit", dataset);
      await openRun(result.run_id);
    });

  goToStep(1);
}

function goToStep(step) {
  if (step > 1 && (!state.imports.shipments || !state.imports.charges)) {
    notice("Validá los archivos de operaciones y cargos antes de continuar.", true);
    return;
  }
  if (step > 2) {
    try {
      const agreements = JSON.parse($("#agreements")?.value || "[]");
      if (!Array.isArray(agreements) || !agreements.length) throw new Error();
    } catch {
      notice("Seleccioná un acuerdo válido antes de verificar el lote.", true);
      return;
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
    if (panel) {
      panel.style.display = (i === step) ? "block" : "none";
    }
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
      sum1.style.display = "flex";
    } else {
      sum1.classList.add("hidden");
      sum1.style.display = "none";
    }
  }

  if (sum2) {
    if (step > 2) {
      let agrName = "Acuerdo contractual";
      let agrDetail = "ARS";
      try {
        const rawAgr = JSON.parse($("#agreements")?.value || "[]");
        if (rawAgr.length > 0) {
          agrName = rawAgr[0].carrier || rawAgr[0].name || "Acuerdo seleccionado";
          const rules = Array.isArray(rawAgr[0].rules) ? rawAgr[0].rules.length : 1;
          const curr = rawAgr[0].currency || "ARS";
          agrDetail = `${rules} regla(s) · ${curr}`;
        }
      } catch (e) {}
      const s2Text = $("#step-summary-2-text");
      if (s2Text) {
        s2Text.innerHTML = `Acuerdo <strong>${esc(agrName)}</strong> · ${esc(agrDetail)}`;
      }
      sum2.classList.remove("hidden");
      sum2.style.display = "flex";
    } else {
      sum2.classList.add("hidden");
      sum2.style.display = "none";
    }
  }

  if (sum3) {
    if (step > 3) {
      const sCount = state.imports.shipments?.accepted || 0;
      const cCount = state.imports.charges?.accepted || 0;
      const s3Text = $("#step-summary-3-text");
      if (s3Text) {
        s3Text.innerHTML = `Lote verificado (${sCount} operaciones, ${cCount} cargos listos para auditar)`;
      }
      sum3.classList.remove("hidden");
      sum3.style.display = "flex";
    } else {
      sum3.classList.add("hidden");
      sum3.style.display = "none";
    }
  }

  if (step === 3) {
    updateStep3Summaries();
  }
}

function updateStep3Summaries() {
  const sImp = state.imports.shipments;
  const cImp = state.imports.charges;

  const sContainer = $("#verify-shipments-summary");
  if (sContainer) {
    sContainer.innerHTML = sImp
      ? `<p style="font-size:15px; font-weight:700; color:#1b6d49; margin:4px 0;">✓ ${sImp.accepted} filas aceptadas · ${sImp.rejected.length} rechazadas</p>
         <p class="muted" style="font-size:13px; margin:0;">Archivo: ${esc(sImp.filename)} (${sImp.records.length} registros)</p>`
      : `<p style="color:var(--amber); font-weight:650;">⚠ Archivo de operaciones aún no validado en Paso 1.</p>`;
  }

  const cContainer = $("#verify-charges-summary");
  if (cContainer) {
    cContainer.innerHTML = cImp
      ? `<p style="font-size:15px; font-weight:700; color:#1b6d49; margin:4px 0;">✓ ${cImp.accepted} filas aceptadas · ${cImp.rejected.length} rechazadas</p>
         <p class="muted" style="font-size:13px; margin:0;">Archivo: ${esc(cImp.filename)} (${cImp.records.length} registros)</p>`
      : `<p style="color:var(--amber); font-weight:650;">⚠ Archivo de cargos aún no validado en Paso 1.</p>`;
  }
}

function renderDropzoneSection(role, title, subtitle) {
  const configs = state.configs.filter(
    (c) => c.kind === "mapping" && c.payload.entity === role,
  );
  return `
    <div class="file-upload-block">
      <div style="margin-bottom:4px;">
        <h3 style="margin:0; font-size:16px;">
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
          <input id="file-${role}" type="file" accept=".csv,.xlsx,.xls" class="sr-only-file" style="display:none;">
        </div>

        <div id="file-loaded-${role}" class="file-loaded-card hidden" style="display:none;">
          <div class="file-loaded-info">
            <span style="font-size:18px;">📄</span>
            <div>
              <strong id="file-name-${role}" style="font-size:13.5px;"></strong>
              <div id="file-meta-${role}" class="muted" style="font-size:12px;"></div>
            </div>
          </div>
          <button type="button" class="btn small subtle" id="change-file-${role}">Cambiar archivo</button>
        </div>
      </div>

      <!-- Formato reconocido / Configurar columnas -->
      <div id="format-box-${role}" class="format-recognition hidden" style="display:none; margin-top:8px;">
        <div style="display:flex; align-items:center; gap:10px;">
          <span class="format-icon" id="format-icon-${role}">✓</span>
          <div>
            <div id="format-title-${role}" style="font-weight:750; font-size:13px;"></div>
            <div id="format-sub-${role}" class="muted" style="font-size:12px;"></div>
          </div>
        </div>
        <button type="button" class="btn subtle small" id="toggle-mapping-${role}">Configurar columnas</button>
      </div>

      <!-- Panel de configuración de columnas (colapsado por defecto) -->
      <div id="columns-panel-${role}" class="columns-panel hidden" style="display:none; margin-top:8px;">
        <div class="field" style="margin:0;">
          <label for="saved-${role}" style="font-size:12.5px;">Seleccionar formato guardado</label>
          <select id="saved-${role}" style="font-size:13px; padding:6px 10px;">
            <option value="">Seleccionar o autodetectar formato…</option>
            ${configs.map((c) => `<option value="${c.hash}">${esc(c.name)}</option>`).join("")}
          </select>
        </div>
      </div>

      <!-- Modo avanzado JSON colapsado -->
      <div class="advanced-toggle" style="margin-top:4px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <button class="btn subtle small" type="button" id="toggle-advanced-${role}" style="font-size:12px; padding:4px 8px;">
            ▸ Opciones avanzadas: mapping JSON manual
          </button>
        </div>
        <div id="advanced-mapping-body-${role}" class="panel-advanced-body hidden" style="display:none; margin-top:8px;">
          <input id="mapping-file-${role}" type="file" accept=".json" aria-label="Cargar mapping de ${title}" style="margin-bottom:8px; font-size:12px;">
          <label for="mapping-${role}" style="font-size:12px;">Mapping JSON</label>
          <textarea id="mapping-${role}" rows="5" spellcheck="false" placeholder="Pegar definición JSON de columnas" style="font-size:12px; font-family:monospace;"></textarea>
        </div>
      </div>

      <div style="margin-top:6px;">
        <button class="btn" id="validate-${role}" style="width:100%;">Validar ${title.toLowerCase()}</button>
      </div>

      <div class="import-result" id="result-${role}" style="background:#fafcfb; border:1px solid #dbe3dc; border-radius:6px; padding:10px 14px; margin-top:4px; font-size:13px;">
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
        columnsPanel.style.display = columnsPanel.classList.contains("hidden") ? "none" : "block";
      };
    }

    if (toggleAdvancedBtn && advancedBody) {
      toggleAdvancedBtn.onclick = () => {
        advancedBody.classList.toggle("hidden");
        advancedBody.style.display = advancedBody.classList.contains("hidden") ? "none" : "block";
      };
    }

    const configs = state.configs.filter(
      (c) => c.kind === "mapping" && c.payload.entity === role,
    );

    $(`#saved-${role}`).onchange = (event) => {
      const found = configs.find((c) => c.hash === event.target.value);
      if (found) {
        $(`#mapping-${role}`).value = JSON.stringify(found.payload, null, 2);
        updateFormatBox(role, true, found.name);
      }
      invalidateImport(role);
    };

    $(`#mapping-file-${role}`).onchange = (event) =>
      busy(null, async () => {
        $(`#mapping-${role}`).value = await event.target.files[0].text();
        invalidateImport(role);
      });

    $(`#mapping-${role}`).oninput = () => invalidateImport(role);

    $(`#validate-${role}`).onclick = (event) =>
      busy(event.target, async () => {
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
          <strong style="color:#1b6d49; font-size:14px;">✓ ${result.accepted} filas aceptadas · ${result.rejected.length} rechazadas</strong>
          <p class="muted" style="margin:4px 0 0; font-size:12px;">Hoja: ${esc(result.sheet)} · Archivo original conservado</p>
          ${
            result.issues.length
              ? "<ul style='margin-top:6px;'>" +
                result.issues
                  .slice(0, 5)
                  .map((i) => `<li>${esc(i.message)}</li>`)
                  .join("") +
                "</ul>"
              : ""
          }
          <details style="margin-top:8px;">
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
        notice(`Importación de ${role === "shipments" ? "operaciones" : "cargos"} validada con éxito.`);
      });
  }
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
    loadedCard.style.display = "flex";
    dropzone.classList.add("hidden");
    dropzone.style.display = "none";
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
    $(`#saved-${role}`).value = configs[0].hash;
    $(`#mapping-${role}`).value = JSON.stringify(configs[0].payload, null, 2);
    updateFormatBox(role, true, configs[0].name);
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
  box.style.display = "flex";

  if (recognized) {
    box.className = "format-recognition recognized";
    if (icon) icon.textContent = "✓";
    if (title) title.textContent = `Formato seleccionado: ${formatName}`;
    if (sub) sub.textContent = "Validá el archivo para comprobar sus columnas";
    if (columnsPanel) {
      columnsPanel.classList.add("hidden");
      columnsPanel.style.display = "none";
    }
  } else {
    box.className = "format-recognition";
    if (icon) icon.textContent = "⚙";
    if (title) title.textContent = "Configurar columnas";
    if (sub) sub.textContent = "Elegí o personalizá el formato de columnas";
    if (columnsPanel) {
      columnsPanel.classList.remove("hidden");
      columnsPanel.style.display = "block";
    }
  }
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
     <input type="file" id="import-config-file" accept=".json" class="sr-only-file" style="display:none;">`,
  );

  const agreements = state.configs.filter((c) => c.kind === "agreement");
  const mappings = state.configs.filter((c) => c.kind === "mapping");

  main.innerHTML += `
    <div class="grid2">
      <!-- Acuerdos Guardados -->
      <section class="panel">
        <h2>Acuerdos guardados (${agreements.length})</h2>
        <p class="muted">Términos contractuales y reglas pactadas con los transportistas.</p>
        <div class="run-list" style="display:flex; flex-direction:column; gap:16px; margin-top:18px;">
          ${agreements
            .map(
              (c) => `
              <div class="run-card-rich" style="padding:14px 18px; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <strong style="font-size:15px;">${esc(c.name)}</strong>
                  <span class="badge PASS">Válido ✓</span>
                </div>
                <div style="font-size:12.5px; color:var(--muted); margin-top:2px;">
                  Transportista: <strong>${esc(c.payload?.carrier || "Transportista pactado")}</strong>
                </div>
                <div style="font-size:12.5px; color:var(--muted); margin-top:2px;">
                  Vigencia: <strong>${esc(c.payload?.versions ? `${c.payload.versions[0]?.valid_from || "Inicio"} a ${c.payload.versions[0]?.valid_to || "abierta"}` : "Vigente")}</strong> · Moneda: <strong>${esc(c.payload?.currency || "ARS")}</strong> · <strong>${Array.isArray(c.payload?.rules) ? c.payload.rules.length : 1} regla(s)</strong>
                </div>
                <div style="display:flex; justify-content:flex-end; align-items:center; margin-top:8px; border-top:1px solid #edf1eb; padding-top:8px;">
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
        <div class="run-list" style="display:flex; flex-direction:column; gap:16px; margin-top:18px;">
          ${mappings
            .map(
              (c) => `
              <div class="run-card-rich" style="padding:14px 18px; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <strong style="font-size:15px;">${esc(c.name)}</strong>
                  <span class="badge" style="background:#edf2ed; color:var(--ink);">Entidad: ${esc(c.payload?.entity || "archivo")}</span>
                </div>
                <div style="font-size:12.5px; color:var(--muted); margin-top:2px;">
                  Columnas mapeadas: <strong>${c.payload?.columns?.length || 0}</strong> · Delimitador: <code>${esc(c.payload?.delimiter || ",")}</code>
                </div>
                <div style="display:flex; justify-content:flex-end; align-items:center; margin-top:8px; border-top:1px solid #edf1eb; padding-top:8px;">
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
    <details id="advanced-config-panel" class="panel" style="margin-top:24px;">
      <summary style="font-size:15px; font-weight:750; color:var(--ink);">Modo avanzado: Editor JSON de acuerdos y formatos</summary>
      <p class="hint">Al guardar, se genera una nueva versión por hash SHA-256 inmutable. Los datos históricos no se modifican.</p>
      <div class="field" style="margin-top:14px;">
        <label for="config-kind">Tipo de configuración</label>
        <select id="config-kind" style="max-width:320px;">
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
    `<div class="panel guide" style="max-width:920px;">
      <ol style="padding-left:22px; line-height:1.8; font-size:14px;">
        <li><strong>Conservar los originales.</strong> Reuní operaciones, liquidación, contrato y documentos del período ya controlado por el cliente en sus formatos nativos.</li>
        <li><strong>Configurar formatos.</strong> Indicá exactamente hoja, encabezados, separadores, fechas y equivalencias de conceptos. Revisá todas las filas rechazadas.</li>
        <li><strong>Confirmar el acuerdo.</strong> El cliente debe validar vigencias, fecha relevante, unidades, fórmulas, moneda, redondeos, tolerancias y evidencia requerida. No deduzcas estas reglas del importe cobrado.</li>
        <li><strong>Ejecutar y explicar.</strong> Abrí cada hallazgo para revisar matching, versión seleccionada, cálculo aritmético y procedencia.</li>
        <li><strong>Resolver conservando la historia.</strong> Registrá responsable, decisión y motivo. Aportar evidencia crea una nueva corrida sin sobreescribir la anterior.</li>
        <li><strong>Comparar sin prometer ahorro.</strong> Separá diferencias conocidas y nuevas, falsos positivos, casos indeterminados y tiempo de preparación y revisión.</li>
        <li><strong>Exportar y respaldar.</strong> El paquete conserva los originales, los datos normalizados, el resultado, las decisiones y los reportes verificables.</li>
      </ol>
    </div>
    <div class="grid2" style="max-width:920px;">
      ${Object.entries(labels)
        .map(
          ([key, label]) => `
        <div class="panel" style="margin:0;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            ${badge(key)}
            <strong style="font-size:15px;">${label}</strong>
          </div>
          <p class="muted" style="font-size:13px; margin:0;">
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

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
  APPROVED: "Aprobado",
  REJECTED: "Rechazado",
  INFORMATION_REQUESTED: "Información solicitada",
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
  view: "audits",
};
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
const money = (value) => {
  if (value === null || value === undefined) return "—";
  const [whole, fraction] = String(value).split(".");
  return (
    whole.replace(/\B(?=(\d{3})+(?!\d))/g, ".") +
    (fraction ? "," + fraction : "")
  );
};
const badge = (status) =>
  `<span class="badge ${status}">${labels[status]}</span>`;
function notice(text, error = false) {
  const element = $("#notice");
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
  state.view = view;
  document
    .querySelectorAll(".nav")
    .forEach((button) =>
      button.classList.toggle("active", button.dataset.view === view),
    );
}
function heading(kicker, title, description, buttons = "") {
  return `<div class="head"><div><div class="eyebrow muted">${kicker}</div><h1>${title}</h1><p class="muted">${description}</p></div><div class="actions">${buttons}</div></div>`;
}
async function showRuns() {
  nav("audits");
  state.run = null;
  main.innerHTML =
    heading(
      "CONTROL RESPALDADO",
      "Auditorías",
      "Cada importe, sus datos, sus reglas y una explicación.",
      `<button class="btn primary" id="new-run">＋ Nueva auditoría</button>`,
    ) +
    `<div id="runs"><p class="muted">Leyendo auditorías del equipo…</p></div>`;
  $("#new-run").onclick = showNew;
  const runs = await api("/api/runs");
  $("#runs").innerHTML = runs.length
    ? `<div class="banner"><div>ⓘ</div><div><strong>La certeza también se audita.</strong><p>Una diferencia determinada requiere reglas y datos suficientes. La revisión humana no representa ahorro.</p></div></div><div class="run-list">${runs.map((run) => `<button class="run-card" data-run="${run.id}"><span><strong>${esc(run.label)}</strong><small>${new Date(run.created_at).toLocaleString("es-AR")} · ${run.summary.total_findings} hallazgos</small></span><span>${badge("FAIL")} ${run.summary.counts.FAIL} <span aria-hidden="true"> →</span></span></button>`).join("")}</div><p class="hint">Los datos de demostración están identificados como ficticios.</p><button class="btn" id="demo">Ejecutar demostración ficticia</button>`
    : `<div class="panel empty"><div class="symbol" aria-hidden="true">▤</div><h2>Del cargo a la evidencia.</h2><p class="muted">Importá operaciones y liquidaciones, seleccioná el acuerdo y reconstruí el importe esperado. Todo se procesa en este equipo.</p><div class="actions centered"><button class="btn primary" id="demo">Explorar demostración ficticia</button></div><p class="hint">32 operaciones · 3 acuerdos distintos · 4 estados de certeza</p></div>`;
  document
    .querySelectorAll("[data-run]")
    .forEach(
      (button) =>
        (button.onclick = () =>
          busy(button, () => openRun(button.dataset.run))),
    );
  $("#demo").onclick = (event) =>
    busy(event.target, async () => {
      const result = await post("/api/demo");
      await openRun(result.run_id);
    });
}
async function openRun(id) {
  state.run = await api("/api/runs/" + id);
  state.shipmentIndex = new Map(
    state.run.snapshot.shipments.map((s) => [s.id, s]),
  );
  state.chargeIndex = new Map(state.run.snapshot.charges.map((c) => [c.id, c]));
  state.page = 0;
  state.filter = "";
  state.search = "";
  nav("audits");
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
      ? `<div class="banner warning"><div><strong>Importación incompleta</strong><p>Hay filas rechazadas. Los importes sólo incluyen cargos aceptados. Corregí los datos antes de confirmar conclusiones.</p></div></div>`
      : "") +
    (run.snapshot.label.toLowerCase().includes("fictic")
      ? `<div class="banner"><div>ⓘ</div><div><strong>Datos y acuerdos totalmente ficticios.</strong><p>Este ejemplo demuestra comportamiento técnico. No representa tarifas del mercado ni beneficio comercial validado.</p></div></div>`
      : "") +
    Object.entries(summary.currencies)
      .map(
        ([currency, bucket]) =>
          `<div class="metrics"><div class="metric"><label>FACTURADO ACEPTADO · ${currency}</label><div class="value">${money(bucket.actual)}</div><p>${summary.import_complete ? "Importación sin filas rechazadas" : "Lote incompleto"}</p></div><div class="metric accent"><label>COBERTURA DETERMINABLE</label><div class="value">${coverage}%</div><p>${summary.determinable_findings} de ${count} hallazgos · todas las monedas</p></div><div class="metric"><label>EXCESO DETERMINADO · ${currency}</label><div class="value">${money(bucket.confirmed_overcharge)}</div><p>Defecto determinado: ${money(bucket.confirmed_undercharge)}</p></div><div class="metric"><label>IMPORTE EN REVISIÓN · ${currency}</label><div class="value">${money(bucket.review)}</div><p>Indeterminado: ${money(bucket.undeterminable)}</p></div></div>`,
      )
      .join("") +
    `<div class="statusline">${Object.entries(summary.counts)
      .map(([status, n]) => `${badge(status)} <strong>${n}</strong>`)
      .join(
        "",
      )}<span class="muted small-text">La diferencia determinada no equivale a ahorro ni recupero.</span></div><section class="panel table-panel"><div class="table-head"><h2>Detalle de cargos</h2><div class="filters"><input id="search" aria-label="Buscar por referencia o concepto" placeholder="Buscar referencia o concepto"><select id="filter" aria-label="Filtrar por estado"><option value="">Todos los estados</option>${Object.entries(
      labels,
    )
      .map(([key, label]) => `<option value="${key}">${label}</option>`)
      .join(
        "",
      )}</select></div></div><div class="table-wrap"><table><thead><tr><th>Operación / concepto</th><th>Estado del motor</th><th class="num">Facturado</th><th class="num">Esperado</th><th class="num">Diferencia calculada</th><th>Decisión humana</th><th></th></tr></thead><tbody id="findings"></tbody></table></div><div class="pagination"><span id="page-label"></span><div class="actions"><button class="btn small" id="prev">Anterior</button><button class="btn small" id="next">Siguiente</button></div></div></section><div class="actions"><a class="btn" href="/api/runs/${run.id}/export/xlsx">↓ Planilla operativa</a><a class="btn" href="/api/runs/${run.id}/export/html">↓ Informe imprimible</a><button class="btn" id="replay">Verificar reproducción</button></div><details class="panel"><summary>Problemas de datos y trazabilidad del lote (${run.result.issues.length})</summary>${run.result.issues.map((issue) => `<p class="small-text">${esc(issue.message)}</p>`).join("") || "<p>No se encontraron problemas de importación.</p>"}<p class="code">Huella del resultado: ${run.result_hash}<br>Motor: ${run.result.engine_version}<br>Artefacto: ${run.artifact_hash}</p></details>`;
  $("#back").onclick = () => busy(null, showRuns);
  $("#filter").onchange = (event) => {
    state.filter = event.target.value;
    state.page = 0;
    renderFindings();
  };
  $("#search").oninput = (event) => {
    state.search = event.target.value.toLocaleLowerCase("es");
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
  $("#replay").onclick = (event) =>
    busy(event.target, async () => {
      await post(`/api/runs/${run.id}/replay`);
      notice(
        "Reproducción idéntica. Entradas, documentos, motor y resultado verificados.",
      );
    });
  renderFindings();
}
function references(finding) {
  return (
    finding.shipment_ids
      .map((id) => state.shipmentIndex.get(id)?.reference || id)
      .join(", ") ||
    finding.charge_ids
      .map((id) => state.chargeIndex.get(id)?.reference || id)
      .join(", ")
  );
}
function renderFindings() {
  const all = state.run.result.findings.filter(
    (f) =>
      (!state.filter || f.status === state.filter) &&
      (!state.search ||
        `${references(f)} ${f.concept} ${f.charge_ids.join(" ")}`
          .toLocaleLowerCase("es")
          .includes(state.search)),
  );
  const page = all.slice(state.page * 30, (state.page + 1) * 30);
  $("#findings").innerHTML =
    page
      .map((f) => {
        const decision = state.run.decisions
          .filter((d) => d.payload.finding_id === f.id)
          .at(-1);
        return `<tr><td><span class="ref">${esc(references(f) || "Sin operación")}</span><br><span class="muted">${esc(f.concept)} · ${f.charge_ids.length} línea${f.charge_ids.length === 1 ? "" : "s"}</span></td><td>${badge(f.status)}</td><td class="num">${esc(f.currency)} ${money(f.actual)}</td><td class="num">${money(f.expected)}</td><td class="num">${money(f.difference)}${f.status === "REVIEW" ? '<br><small class="muted">No confirmada</small>' : ""}</td><td class="muted">${decision ? esc(actions[decision.payload.action]) : "Sin resolución"}</td><td><button class="btn small" data-finding="${f.id}" aria-label="Ver explicación de ${esc(references(f))}, ${esc(f.concept)}">Ver explicación →</button></td></tr>`;
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
  return `<details class="trace" open><summary>${esc(opLabels[trace.op] || trace.op)} ${trace.output !== null ? `<span class="trace-output">→ ${esc(trace.output)}</span>` : ""}</summary><p class="small-text">${esc(traceText(trace))}</p><details><summary>Datos utilizados en este paso</summary><code>${esc(JSON.stringify(trace.details, null, 2))}</code></details>${trace.children.map(traceHtml).join("")}</details>`;
}
function showDetail(id) {
  const f = state.run.result.findings.find((item) => item.id === id);
  const history = state.run.decisions.filter(
    (d) => d.payload.finding_id === id,
  );
  const records = [
    ...state.run.snapshot.shipments.filter((s) =>
      f.shipment_ids.includes(s.id),
    ),
    ...state.run.snapshot.charges.filter((c) => f.charge_ids.includes(c.id)),
  ];
  $("#detail-content").innerHTML =
    `<div class="dialog-head"><div><div class="eyebrow muted">EXPLICACIÓN DEL HALLAZGO</div><h2 id="detail-title">${esc(references(f) || "Referencia sin vincular")} · ${esc(f.concept)}</h2>${badge(f.status)}</div><button class="btn small" id="close-detail" aria-label="Cerrar explicación">Cerrar ✕</button></div><div class="detail-money"><div><label>FACTURADO · ${esc(f.currency)}</label><strong>${money(f.actual)}</strong></div><div><label>ESPERADO</label><strong>${money(f.expected)}</strong></div><div><label>DIFERENCIA CALCULADA</label><strong>${money(f.difference)}</strong></div></div><div class="banner ${f.status === "REVIEW" ? "warning" : ""}"><div>${f.reasons.map((reason) => `<p>${esc(reason)}</p>`).join("")}</div></div><p class="small-text muted">Acuerdo ${esc(f.agreement)} · Versión ${esc(f.version || "No determinada")} · Regla ${esc(f.rule || "No determinada")}</p><details><summary>Cálculo ejecutado y decisiones de la regla</summary>${f.trace.map(traceHtml).join("") || "<p>No hubo cálculo: primero se necesita resolver la vinculación.</p>"}</details><details><summary>Origen de cada dato (${records.length} registros)</summary><div class="table-wrap"><table><thead><tr><th>Registro / campo</th><th>Archivo</th><th>Hoja / fila / columna</th><th>Valor original</th></tr></thead><tbody>${records.flatMap((record) => Object.entries(record.provenance).map(([field, ref]) => `<tr><td>${esc(record.id)}<br>${esc(field)}</td><td>${esc(ref.filename)}</td><td>${esc(ref.sheet)} / ${ref.row} / ${esc(ref.column)}</td><td>${esc(ref.raw)}</td></tr>`)).join("")}</tbody></table></div></details><div class="detail-grid"><section class="panel"><h3>Registrar decisión humana</h3><p class="hint">Agrega una resolución al historial. El estado original del motor se conserva.</p><form id="decision-form" class="decision-form"><div class="field"><label for="actor">Persona responsable</label><input id="actor" name="actor" type="text" required maxlength="200"></div><div class="field"><label for="action">Decisión</label><select id="action" name="action">${Object.entries(
      actions,
    )
      .map(([key, label]) => `<option value="${key}">${label}</option>`)
      .join(
        "",
      )}</select></div><div class="field"><label for="decision-note">Motivo y respaldo de la decisión</label><textarea id="decision-note" name="note" required minlength="3" maxlength="10000"></textarea></div><div class="field"><label for="known">¿El cliente ya conocía esta diferencia?</label><select id="known" name="known"><option value="">Sin confirmar</option><option value="true">Sí</option><option value="false">No</option></select></div><button class="btn primary" type="submit">Guardar decisión</button></form></section><section class="panel"><h3>Historial de resoluciones</h3>${history.map((d) => `<div class="history"><strong>${esc(actions[d.payload.action])}</strong><p>${esc(d.payload.note)}</p><small class="muted">${esc(d.payload.actor)} · ${new Date(d.created_at).toLocaleString("es-AR")}</small></div>`).join("") || '<p class="muted">Todavía no se registraron decisiones.</p>'}<details><summary>Aportar evidencia y crear nueva corrida</summary><p class="hint">Se vincula a las operaciones y cargos de este hallazgo. El resultado actual se conserva.</p><form id="evidence-form"><div class="field"><label for="ev-kind">Tipo de evidencia según el acuerdo</label><input id="ev-kind" type="text" required placeholder="Ej.: authorization"></div><div class="field"><label for="ev-note">Descripción del respaldo</label><input id="ev-note" type="text" required></div><div class="field"><label for="ev-file">Documento (opcional si el acuerdo lo permite)</label><input id="ev-file" type="file"></div><button class="btn" type="submit">Auditar con esta evidencia</button></form></details></section></div>`;
  $("#close-detail").onclick = () => $("#detail").close();
  $("#decision-form").onsubmit = (event) => {
    event.preventDefault();
    busy($("button[type=submit]", event.target), async () => {
      await post(`/api/runs/${state.run.id}/decisions`, {
        finding_id: id,
        action: $("#action").value,
        actor: $("#actor").value,
        note: $("#decision-note").value,
        known_to_client:
          $("#known").value === "" ? null : $("#known").value === "true",
      });
      state.run = await api("/api/runs/" + state.run.id);
      renderFindings();
      showDetail(id);
      notice("Decisión agregada. El hallazgo original se conserva.");
    });
  };
  $("#evidence-form").onsubmit = (event) => {
    event.preventDefault();
    busy($("button[type=submit]", event.target), async () => {
      const snapshot = structuredClone(state.run.snapshot);
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
        kind: $("#ev-kind").value,
        note: $("#ev-note").value,
        shipment_ids: f.shipment_ids,
        charge_ids: f.charge_ids,
        document_hash,
      });
      snapshot.label += " · evidencia adicional";
      const result = await post("/api/audit", snapshot);
      $("#detail").close();
      await openRun(result.run_id);
      notice(
        "Nueva auditoría creada con la evidencia. La corrida anterior se conserva.",
      );
    });
  };
  if (!$("#detail").open) $("#detail").showModal();
}
async function showNew() {
  nav("new");
  state.imports = {};
  state.configs = await api("/api/configs");
  main.innerHTML = heading(
    "DATOS → REGLAS → VERIFICACIÓN",
    "Nueva auditoría",
    "Validá los archivos y el acuerdo antes de calcular.",
  );
  main.innerHTML += `<div class="panel"><label for="audit-label">Nombre del período o lote</label><input id="audit-label" type="text" placeholder="Ej.: Cierre de septiembre · Transportista" required></div><div class="grid2">${importPanel("shipments", "1", "Operaciones", "Viajes, despachos o remitos")}${importPanel("charges", "2", "Cargos liquidados", "Detalle de cargos del transportista")}<section class="panel full"><div class="step-title"><span class="step">3</span><h2>Acuerdos y evidencia</h2></div><p class="hint">El acuerdo debe reflejar términos confirmados por el cliente. El editor acepta una lista de acuerdos; los importes y factores usan texto decimal exacto.</p><div class="field"><label for="agreement-select">Usar un acuerdo guardado</label><select id="agreement-select"><option value="">Seleccionar…</option>${state.configs
    .filter((c) => c.kind === "agreement")
    .map(
      (c) =>
        `<option value="${c.hash}">${esc(c.name)} · ${c.hash.slice(0, 6)}</option>`,
    )
    .join(
      "",
    )}</select> <input type="file" id="agreement-file" accept=".json" aria-label="Cargar acuerdos desde JSON"></div><label for="agreements">Acuerdos (lista JSON)</label><textarea id="agreements" rows="10">[]</textarea><details><summary>Evidencia y alcance de cargos ausentes (opcional)</summary><p class="hint">La evidencia debe indicar sus operaciones o cargos. El alcance limita dónde buscar conceptos esperados que no se cobraron. Los adjuntos también pueden aportarse desde un hallazgo en una nueva corrida.</p><label for="evidence">Evidencia (lista JSON)</label><textarea id="evidence">[]</textarea><label for="coverage">Alcance por acuerdo (JSON)</label><textarea id="coverage">{}</textarea></details></section></div><div class="banner"><div><strong>Revisión previa</strong><p>Las filas rechazadas se conservan como problemas de datos. Si ejecutás un lote incompleto, sus comparaciones no se confirmarán como discrepancias.</p></div></div><button class="btn primary" id="execute">Ejecutar auditoría local →</button>`;
  for (const role of ["shipments", "charges"]) {
    const configs = state.configs.filter(
      (c) => c.kind === "mapping" && c.payload.entity === role,
    );
    $(`#saved-${role}`).onchange = (event) => {
      const found = configs.find((c) => c.hash === event.target.value);
      if (found)
        $(`#mapping-${role}`).value = JSON.stringify(found.payload, null, 2);
      invalidateImport(role);
    };
    $(`#mapping-file-${role}`).onchange = (event) =>
      busy(null, async () => {
        $(`#mapping-${role}`).value = await event.target.files[0].text();
        invalidateImport(role);
      });
    $(`#mapping-${role}`).oninput = () => invalidateImport(role);
    $(`#file-${role}`).onchange = () => invalidateImport(role);
    $(`#validate-${role}`).onclick = (event) =>
      busy(event.target, async () => {
        const file = $(`#file-${role}`).files[0];
        if (!file) throw new Error("Seleccionar el archivo a importar.");
        const mapping = JSON.parse($(`#mapping-${role}`).value);
        if (mapping.entity !== role)
          throw new Error(
            "El mapping seleccionado corresponde a otro tipo de archivo.",
          );
        const form = new FormData();
        form.append("file", file);
        form.append("mapping", JSON.stringify(mapping));
        const result = await post("/api/import", form);
        state.imports[role] = result;
        $(`#result-${role}`).innerHTML =
          `<strong>${result.accepted} filas aceptadas · ${result.rejected.length} rechazadas</strong><p class="muted">Hoja ${esc(result.sheet)} · Original conservado</p>${
            result.issues.length
              ? "<ul>" +
                result.issues
                  .slice(0, 8)
                  .map((i) => `<li>${esc(i.message)}</li>`)
                  .join("") +
                "</ul>"
              : ""
          }<details><summary>Vista previa del origen (${result.preview.length} filas)</summary><div class="table-wrap"><table><thead><tr>${result.headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${result.preview.map((row) => `<tr>${result.headers.map((h) => `<td>${esc(row.values[h])}</td>`).join("")}</tr>`).join("")}</tbody></table></div></details>`;
      });
  }
  $("#agreement-select").onchange = (event) => {
    const found = state.configs.find((c) => c.hash === event.target.value);
    if (found)
      $("#agreements").value = JSON.stringify([found.payload], null, 2);
  };
  $("#agreement-file").onchange = (event) =>
    busy(null, async () => {
      const parsed = JSON.parse(await event.target.files[0].text());
      $("#agreements").value = JSON.stringify(
        Array.isArray(parsed) ? parsed : [parsed],
        null,
        2,
      );
    });
  $("#execute").onclick = (event) =>
    busy(event.target, async () => {
      if (!state.imports.shipments || !state.imports.charges)
        throw new Error(
          "Validar ambos archivos con sus mappings antes de ejecutar.",
        );
      const label = $("#audit-label").value.trim();
      if (!label) throw new Error("Ingresar un nombre para esta auditoría.");
      const values = Object.values(state.imports);
      const dataset = {
        label,
        shipments: state.imports.shipments.records,
        charges: state.imports.charges.records,
        agreements: JSON.parse($("#agreements").value),
        evidence: JSON.parse($("#evidence").value),
        coverage: JSON.parse($("#coverage").value),
        mappings: values.map((r) => r.mapping),
        documents: Object.fromEntries(
          values.map((r) => [r.document, r.filename]),
        ),
        issues: values.flatMap((r) => r.issues),
      };
      const result = await post("/api/audit", dataset);
      await openRun(result.run_id);
    });
}
function invalidateImport(role) {
  delete state.imports[role];
  const result = $(`#result-${role}`);
  if (result)
    result.textContent =
      "Validar para ver filas aceptadas, rechazos y origen de los datos.";
}
function importPanel(role, step, title, subtitle) {
  const configs = state.configs.filter(
    (c) => c.kind === "mapping" && c.payload.entity === role,
  );
  return `<section class="panel"><div class="step-title"><span class="step">${step}</span><h2>${title}</h2></div><p class="muted">${subtitle}</p><div class="field"><label for="file-${role}">Archivo CSV, XLSX o XLS</label><input id="file-${role}" type="file" accept=".csv,.xlsx,.xls"></div><div class="field"><label for="saved-${role}">Formato guardado</label><select id="saved-${role}"><option value="">Seleccionar o cargar un mapping…</option>${configs.map((c) => `<option value="${c.hash}">${esc(c.name)}</option>`).join("")}</select></div><details open><summary>Configurar mapping</summary><p class="hint">Elegí columnas, hoja, encabezado, tipos y separadores. Se guarda una nueva versión por contenido al validar.</p><input id="mapping-file-${role}" type="file" accept=".json" aria-label="Cargar mapping de ${title}"><label for="mapping-${role}">Mapping JSON</label><textarea id="mapping-${role}" rows="8" spellcheck="false" placeholder="Cargar un mapping existente o pegar una configuración"></textarea></details><button class="btn" id="validate-${role}">Validar y ver filas</button><div class="import-result" id="result-${role}">Validar para ver filas aceptadas, rechazos y origen de los datos.</div></section>`;
}
async function showConfigs() {
  nav("configs");
  state.configs = await api("/api/configs");
  main.innerHTML = heading(
    "CONFIGURACIÓN VERSIONADA",
    "Acuerdos y formatos",
    "Los cambios crean versiones conservadas por contenido. Las auditorías anteriores mantienen su configuración.",
  );
  main.innerHTML += `<div class="grid2"><section class="panel"><h2>Configuraciones guardadas</h2><div class="run-list">${state.configs.map((c) => `<button class="run-card" data-config="${c.hash}"><span><strong>${esc(c.name)}</strong><small>${c.kind === "agreement" ? "Acuerdo" : "Mapping"} · ${c.hash.slice(0, 10)}</small></span><span>→</span></button>`).join("") || '<p class="muted">Ejecutá la demostración o guardá tu primera configuración.</p>'}</div></section><section class="panel"><h2>Crear una versión</h2><p class="hint">Para agregar otro cliente, definí sus columnas y reglas aquí. No se ejecuta código arbitrario.</p><div class="field"><label for="config-kind">Tipo</label><select id="config-kind"><option value="agreement">Acuerdo</option><option value="mapping">Mapping</option></select></div><div class="field"><label for="config-data">Configuración JSON</label><textarea id="config-data" rows="24" spellcheck="false">{}</textarea></div><button class="btn primary" id="save-config">Validar y guardar versión</button></section></div>`;
  document.querySelectorAll("[data-config]").forEach(
    (button) =>
      (button.onclick = () => {
        const c = state.configs.find(
          (item) => item.hash === button.dataset.config,
        );
        $("#config-kind").value = c.kind;
        $("#config-data").value = JSON.stringify(c.payload, null, 2);
      }),
  );
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
function showGuide() {
  nav("guide");
  main.innerHTML =
    heading(
      "DE LOS ARCHIVOS A LA DECISIÓN",
      "Un control que se puede reconstruir",
      "Guía para trabajar con un acuerdo real.",
    ) +
    `<div class="panel guide"><ol><li><strong>Conservar los originales.</strong> Reuní operaciones, liquidación, contrato y documentos del período ya controlado por el cliente.</li><li><strong>Configurar formatos.</strong> Indicá exactamente hoja, encabezados, separadores, fechas y equivalencias de conceptos. Revisá todas las filas rechazadas.</li><li><strong>Confirmar el acuerdo.</strong> El cliente debe validar vigencias, fecha relevante, unidades, fórmulas, moneda, redondeos, tolerancias y evidencia requerida. No deduzcas estas reglas del importe cobrado.</li><li><strong>Ejecutar y explicar.</strong> Abrí cada hallazgo para revisar matching, versión seleccionada, cálculo y procedencia.</li><li><strong>Resolver conservando la historia.</strong> Registrá responsable, decisión y motivo. Aportar evidencia crea una nueva corrida.</li><li><strong>Comparar sin prometer ahorro.</strong> Separá diferencias conocidas y nuevas, falsos positivos, casos indeterminados y tiempo de preparación y revisión.</li><li><strong>Exportar y respaldar.</strong> El paquete contiene originales, snapshot, resultado, decisiones, planilla y reporte imprimible. Conservar también el programa y una copia de la base.</li></ol></div><div class="grid2">${Object.entries(
      labels,
    )
      .map(
        ([status, label]) =>
          `<section class="panel"><h3>${badge(status)}</h3><p>${{ PASS: "El cargo coincide dentro de la tolerancia configurada.", FAIL: "Los datos y la regla permiten determinar una discrepancia objetiva.", REVIEW: "Se necesita una confirmación humana, evidencia o una vinculación sin ambigüedad.", UNDETERMINABLE: "Falta información esencial o no existe una única regla o versión aplicable." }[status]}</p></section>`,
      )
      .join(
        "",
      )}</div><div class="banner warning"><div><strong>Alcance del prototipo</strong><p>No hay autenticación ni firma digital. Usá el servicio sólo en este equipo. Un hash detecta alteraciones respecto de una copia confiable; no certifica la veracidad del documento ni la identidad del responsable.</p></div></div>`;
}
document
  .querySelectorAll(".nav")
  .forEach(
    (button) =>
      (button.onclick = () =>
        busy(null, () =>
          ({
            audits: showRuns,
            new: showNew,
            configs: showConfigs,
            guide: showGuide,
          })[button.dataset.view](),
        )),
  );
window.addEventListener("unhandledrejection", (event) => {
  event.preventDefault();
  notice(
    event.reason?.message ||
      "No se pudo completar la operación. Revisar el servicio local.",
    true,
  );
});
(async () => {
  const session = await api("/api/session");
  state.token = session.token;
  await showRuns();
})().catch((error) => {
  main.innerHTML = heading(
    "SERVICIO LOCAL",
    "No se pudo abrir el espacio de trabajo",
    esc(error.message),
  );
});

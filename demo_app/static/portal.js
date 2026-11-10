"use strict";
const token = document.querySelector('meta[name="csrf-token"]').content;
const byId = id => document.getElementById(id);
let editingId = null;
let rows = [];
let requestNumber = 0;

async function api(path, method = "GET", data) {
  const response = await fetch(path, {
    method,
    headers: {"Content-Type": "application/json", "X-CSRF-Token": token},
    body: data === undefined ? undefined : JSON.stringify(data)
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Chyba spojení (${response.status}). Obnovte stránku.`);
  }
  return response.status === 204 ? null : response.json();
}

function show(id, text) {
  byId(id).textContent = text;
  byId(id).hidden = false;
}

function renderRecords() {
  const body = byId("records-body");
  body.replaceChildren();
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.dataset.testid = "record-row";
    for (const value of [row.title, row.owner, row.status, row.priority ? "Vysoká" : "Běžná"]) {
      const td = document.createElement("td");
      td.textContent = value;
      if (value === row.status) {
        const badge = document.createElement("span");
        badge.className = "status-badge" + (value === "Hotový" ? " done" : value === "Rozpracovaný" ? " progress" : "");
        badge.textContent = value;
        td.replaceChildren(badge);
      }
      tr.append(td);
    }
    const actions = document.createElement("td");
    for (const [label, handler] of [["Upravit", () => openForm(row)], ["Smazat", () => removeRecord(row)]]) {
      const button = document.createElement("button");
      button.className = "quiet";
      button.textContent = label;
      button.setAttribute("aria-label", `${label} ${row.title}`);
      button.addEventListener("click", handler);
      actions.append(button);
    }
    tr.append(actions);
    body.append(tr);
  }
  byId("total-count").textContent = rows.length;
  byId("empty").hidden = rows.length > 0;
}

async function loadRecords(simulate = false) {
  const current = ++requestNumber;
  byId("loading").hidden = false;
  byId("api-error").hidden = true;
  const query = new URLSearchParams({q: byId("search").value, status: byId("filter-status").value});
  if (simulate) query.set("simulate_error", "1");
  try {
    const data = await api(`/api/records?${query}`);
    if (current !== requestNumber) return;
    rows = data;
    renderRecords();
  } catch (error) {
    if (current === requestNumber) {
      rows = [];
      renderRecords();
      show("api-error", error.message);
    }
  } finally {
    if (current === requestNumber) byId("loading").hidden = true;
  }
}

function openForm(row = null) {
  editingId = row?.id ?? null;
  byId("record-form").reset();
  byId("form-error").hidden = true;
  byId("dialog-title").textContent = row ? "Upravit záznam" : "Nový záznam";
  byId("record-title").value = row?.title ?? "";
  byId("owner").value = row?.owner ?? "Jana";
  byId("record-status").value = row?.status ?? "Nový";
  byId("priority").checked = row?.priority ?? false;
  byId("record-dialog").showModal();
  byId("record-title").focus();
}

async function removeRecord(row) {
  if (!confirm(`Opravdu smazat „${row.title}“?`)) return;
  try {
    await api(`/api/records/${row.id}`, "DELETE");
    show("notification", "Záznam byl smazán.");
    await loadRecords();
  } catch (error) { show("api-error", error.message); }
}

if (byId("records-body")) {
  byId("new-record").addEventListener("click", () => openForm());
  for (const id of ["cancel", "cancel-x"]) byId(id).addEventListener("click", () => byId("record-dialog").close());
  byId("search").addEventListener("input", () => loadRecords());
  byId("filter-status").addEventListener("change", () => loadRecords());
  byId("reload").addEventListener("click", () => loadRecords());
  byId("simulate-error").addEventListener("click", () => loadRecords(true));
  byId("reset").addEventListener("click", async () => {
    try {
      await api("/api/reset", "POST", {});
      byId("search").value = "";
      byId("filter-status").value = "";
      show("notification", "Výchozí data obnovena.");
      await loadRecords();
    } catch (error) { show("api-error", error.message); }
  });
  byId("record-form").addEventListener("submit", async event => {
    event.preventDefault();
    const submit = event.submitter;
    submit.disabled = true;
    try {
      const data = {title: byId("record-title").value, owner: byId("owner").value,
        status: byId("record-status").value, priority: byId("priority").checked};
      await api(editingId === null ? "/api/records" : `/api/records/${editingId}`, editingId === null ? "POST" : "PUT", data);
      byId("record-dialog").close();
      show("notification", editingId === null ? "Záznam byl vytvořen." : "Záznam byl upraven.");
      await loadRecords();
    } catch (error) { show("form-error", error.message); }
    finally { submit.disabled = false; }
  });
  loadRecords();
}

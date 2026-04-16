function qs(root, sel) {
  return root.querySelector(sel);
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) node.appendChild(c);
  return node;
}

async function apiGet(path) {
  const resp = await fetch(path, { headers: { Accept: "application/json" } });
  if (!resp.ok) throw new Error(`GET ${path} failed (${resp.status})`);
  return resp.json();
}

async function apiDelete(path) {
  const resp = await fetch(path, { method: "DELETE", headers: { Accept: "application/json" } });
  if (resp.status === 204) return null;
  const text = await resp.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = null;
  }
  const msg = payload && payload.detail ? payload.detail : `DELETE ${path} failed (${resp.status})`;
  throw new Error(msg);
}

function pillForStatus(status) {
  const cls = status === "published" ? "pill pill--published" : "pill pill--draft";
  const txt = status || "draft";
  return el("span", { class: cls, text: txt });
}

async function loadDashboard() {
  const tbody = document.getElementById("pages-tbody");
  const empty = document.getElementById("pages-empty");
  const statusSel = document.getElementById("page-filter-status");
  const errorEl = document.getElementById("pages-error");
  if (!tbody || !empty || !statusSel) return;

  async function refresh() {
    tbody.innerHTML = "";
    if (errorEl) errorEl.textContent = "";
    const status = statusSel.value;
    const url = status ? `/api/v1/subject-pages/?status=${encodeURIComponent(status)}` : "/api/v1/subject-pages/";
    const pages = await apiGet(url);
    empty.hidden = pages.length !== 0;
    for (const p of pages) {
      const tr = document.createElement("tr");
      const tdTitle = document.createElement("td");
      tdTitle.textContent = p.title;
      const tdStatus = document.createElement("td");
      tdStatus.appendChild(pillForStatus(p.status));
      const tdActions = document.createElement("td");
      const actions = el("div", { class: "toolbar" }, [
        el("a", { class: "btn", href: `/editor/pages/${p.id}`, text: "Edit" }),
      ]);
      if (p.status === "published") {
        actions.appendChild(el("a", { class: "btn", href: `/pages/${p.slug}`, text: "View" }));
      }
      const del = el("button", { class: "btn", type: "button", text: "Delete" });
      del.addEventListener("click", async () => {
        if (!window.confirm(`Delete “${p.title}”? This cannot be undone.`)) return;
        del.disabled = true;
        try {
          await apiDelete(`/api/v1/subject-pages/${p.id}`);
          await refresh();
        } catch (e) {
          del.disabled = false;
          if (errorEl) errorEl.textContent = e && e.message ? e.message : String(e);
          else console.error(e);
        }
      });
      actions.appendChild(del);
      tdActions.appendChild(actions);
      tr.appendChild(tdTitle);
      tr.appendChild(tdStatus);
      tr.appendChild(tdActions);
      tbody.appendChild(tr);
    }
  }

  statusSel.addEventListener("change", () => refresh().catch(console.error));
  await refresh();
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard().catch(console.error);
});


function $(id) {
  return document.getElementById(id);
}

function qs(root, sel) {
  return root.querySelector(sel);
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k === "html") node.innerHTML = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) node.appendChild(c);
  return node;
}

async function apiJson(method, path, body) {
  const resp = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await resp.text();
  const payload = text ? JSON.parse(text) : null;
  if (!resp.ok) {
    const msg = payload && payload.detail ? payload.detail : `${method} ${path} failed (${resp.status})`;
    throw new Error(msg);
  }
  return payload;
}

async function apiGet(path) {
  const resp = await fetch(path, { headers: { Accept: "application/json" } });
  const text = await resp.text();
  const payload = text ? JSON.parse(text) : null;
  if (!resp.ok) {
    const msg = payload && payload.detail ? payload.detail : `GET ${path} failed (${resp.status})`;
    throw new Error(msg);
  }
  return payload;
}

function slugify(s) {
  return (s || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function setOptions(select, items, { valueKey = "id", labelKey = "name", placeholder = "Select..." } = {}) {
  select.innerHTML = "";
  select.appendChild(el("option", { value: "", text: placeholder }));
  for (const it of items) {
    select.appendChild(el("option", { value: String(it[valueKey]), text: String(it[labelKey]) }));
  }
}

function execFormat(cmd) {
  if (cmd === "highlight") {
    document.execCommand("hiliteColor", false, "#60d6b5");
    return;
  }
  document.execCommand(cmd, false, null);
}

function wireToolbar(editorRoot) {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cmd]");
    if (!btn) return;
    e.preventDefault();
    editorRoot.focus();
    execFormat(btn.getAttribute("data-cmd"));
  });
}

function buildPlainMapping(root) {
  // Matches backend render_service rules: count characters across all text nodes (no script/style).
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const p = node.parentElement;
      if (!p) return NodeFilter.FILTER_REJECT;
      const tag = p.tagName ? p.tagName.toLowerCase() : "";
      if (tag === "script" || tag === "style") return NodeFilter.FILTER_REJECT;
      if (!node.nodeValue) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  const mapping = []; // [{node, offset}]
  let n;
  while ((n = walker.nextNode())) {
    const text = n.nodeValue || "";
    for (let i = 0; i < text.length; i++) mapping.push({ node: n, offset: i });
  }
  return mapping;
}

function selectionOffsets(editorRoot) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return null;
  const range = sel.getRangeAt(0);
  if (!editorRoot.contains(range.commonAncestorContainer)) return null;

  const startNode = range.startContainer;
  const endNode = range.endContainer;
  if (startNode !== endNode || startNode.nodeType !== Node.TEXT_NODE) {
    return { error: "Selection must be within a single text node (cannot cross element boundaries)." };
  }
  const text = startNode.nodeValue || "";
  if (range.endOffset <= range.startOffset) return { error: "Select a non-empty span of text." };
  const trigger = text.slice(range.startOffset, range.endOffset);

  const mapping = buildPlainMapping(editorRoot);
  let startIdx = -1;
  let endIdx = -1;
  for (let i = 0; i < mapping.length; i++) {
    const m = mapping[i];
    if (m.node === startNode && m.offset === range.startOffset) startIdx = i;
    if (m.node === endNode && m.offset === range.endOffset - 1) endIdx = i;
  }
  if (startIdx < 0 || endIdx < 0) return { error: "Unable to compute offsets for the current selection." };
  return { trigger, start_offset: startIdx, end_offset: endIdx + 1 };
}

function toggleAnnFields(type) {
  $("ann_media_wrap").hidden = !["image", "audio", "video"].includes(type);
  $("ann_youtube_wrap").hidden = type !== "youtube";
  $("ann_link_label_wrap").hidden = type !== "link_note";
  $("ann_body_wrap").hidden = type === "youtube";
}

function setAnnStatus(kind, message) {
  const node = $("ann_error");
  if (!node) return;
  node.textContent = message || "";
  node.classList.remove("status--info", "status--error", "status--success");
  if (!message) return;
  if (kind === "error") node.classList.add("status--error");
  else if (kind === "success") node.classList.add("status--success");
  else node.classList.add("status--info");
}

function setButtonLoading(btn, isLoading, loadingLabel = "Working…") {
  if (!btn) return;
  if (isLoading) {
    if (!btn.dataset.originalLabel) btn.dataset.originalLabel = btn.textContent || "";
    btn.textContent = loadingLabel;
    btn.disabled = true;
    btn.setAttribute("aria-busy", "true");
    return;
  }
  btn.textContent = btn.dataset.originalLabel || btn.textContent || "";
  btn.removeAttribute("aria-busy");
}

function getPageId() {
  const elId = $("page_id");
  if (!elId) return null;
  const v = parseInt(elId.value, 10);
  return Number.isFinite(v) ? v : null;
}

function gatherPagePayload() {
  return {
    category_id: parseInt($("category_id").value, 10),
    sub_category_id: parseInt($("sub_category_id").value, 10),
    sub_sub_category_id: parseInt($("sub_sub_category_id").value, 10),
    title: $("title").value,
    slug: $("slug").value,
    summary: $("summary").value,
    raw_content: $("editor").innerHTML,
    status: "draft",
  };
}

function setPreviewHtml(html) {
  const container = $("preview");
  if (container) container.innerHTML = html || "";
}

async function loadHierarchyForEdit(existing) {
  const cats = await apiGet("/api/v1/categories/");
  setOptions($("category_id"), cats, { placeholder: "Select category" });
  if (existing && existing.category_id) $("category_id").value = String(existing.category_id);

  async function loadSubcats() {
    const cid = parseInt($("category_id").value, 10);
    if (!Number.isFinite(cid)) {
      setOptions($("sub_category_id"), [], { placeholder: "Select sub-category" });
      setOptions($("sub_sub_category_id"), [], { placeholder: "Select sub-sub-category" });
      return;
    }
    const subs = await apiGet(`/api/v1/sub-categories/?category_id=${encodeURIComponent(cid)}`);
    setOptions($("sub_category_id"), subs, { placeholder: "Select sub-category" });
    if (existing && existing.sub_category_id) $("sub_category_id").value = String(existing.sub_category_id);
    await loadSubsubs();
  }

  async function loadSubsubs() {
    const sid = parseInt($("sub_category_id").value, 10);
    if (!Number.isFinite(sid)) {
      setOptions($("sub_sub_category_id"), [], { placeholder: "Select sub-sub-category" });
      return;
    }
    const subs = await apiGet(`/api/v1/sub-sub-categories/?sub_category_id=${encodeURIComponent(sid)}`);
    setOptions($("sub_sub_category_id"), subs, { placeholder: "Select sub-sub-category" });
    if (existing && existing.sub_sub_category_id) $("sub_sub_category_id").value = String(existing.sub_sub_category_id);
  }

  $("category_id").addEventListener("change", () => loadSubcats().catch(console.error));
  $("sub_category_id").addEventListener("change", () => loadSubsubs().catch(console.error));
  await loadSubcats();
}

async function refreshAnnotations(pageId) {
  const listRoot = $("ann_list");
  if (!listRoot) return;
  listRoot.innerHTML = "";
  const items = await apiGet(`/api/v1/subject-pages/${pageId}/annotations`);
  for (const a of items) {
    const row = el("div", { class: "card stack" }, [
      el("div", { class: "muted", text: `${a.annotation_type} • ${a.trigger_text} • [${a.start_offset}, ${a.end_offset})` }),
      el("div", { text: a.title || "" }),
    ]);
    const bar = el("div", { class: "toolbar" });
    const del = el("button", { class: "btn", type: "button", text: "Delete" });
    del.addEventListener("click", async () => {
      await fetch(`/api/v1/annotations/${a.id}`, { method: "DELETE" });
      await refreshAnnotations(pageId);
    });
    bar.appendChild(del);
    row.appendChild(bar);
    listRoot.appendChild(row);
  }
}

async function initEditorPage() {
  const editorRoot = $("editor");
  if (!editorRoot) return;
  wireToolbar(editorRoot);

  const slugInput = $("slug");
  const titleInput = $("title");
  if (slugInput && titleInput) {
    titleInput.addEventListener("input", () => {
      if (!slugInput.value.trim()) slugInput.value = slugify(titleInput.value);
    });
  }

  const annType = $("ann_type");
  annType.addEventListener("change", () => {
    toggleAnnFields(annType.value);
  });
  toggleAnnFields(annType.value);

  let captured = null;

  function syncCreateAnnotationEnabled() {
    const btn = $("btn-create-annotation");
    if (!btn) return;
    const pid = getPageId();
    btn.disabled = !(captured && pid);
  }

  $("btn-capture").addEventListener("click", () => {
    const res = selectionOffsets(editorRoot);
    if (res && res.error) {
      setAnnStatus("error", res.error);
      captured = null;
      $("ann_trigger").value = "";
      syncCreateAnnotationEnabled();
      return;
    }
    setAnnStatus("info", "");
    captured = res;
    $("ann_trigger").value = captured ? captured.trigger : "";
    syncCreateAnnotationEnabled();
    if (!getPageId()) {
      setAnnStatus("info", "Save draft to enable annotations on this page.");
    }
  });

  const pageId = getPageId();
  const isEdit = Number.isFinite(pageId);

  let currentPage = null;
  if (isEdit) {
    currentPage = await apiGet(`/api/v1/subject-pages/${pageId}`);
    $("title").value = currentPage.title || "";
    $("slug").value = currentPage.slug || "";
    $("summary").value = currentPage.summary || "";
    editorRoot.innerHTML = currentPage.raw_content || "<p></p>";
    await loadHierarchyForEdit(currentPage);
    await refreshAnnotations(pageId);
    const viewBtn = $("btn-view");
    if (viewBtn && currentPage.status === "published") {
      viewBtn.hidden = false;
      viewBtn.href = `/pages/${currentPage.slug}`;
    }
  } else {
    await loadHierarchyForEdit(null);
    syncCreateAnnotationEnabled();
    setAnnStatus("info", "Save draft to enable annotations on this page.");
  }

  async function saveDraft() {
    setAnnStatus("info", "");
    if (isEdit) {
      const payload = {
        category_id: parseInt($("category_id").value, 10),
        sub_category_id: parseInt($("sub_category_id").value, 10),
        sub_sub_category_id: parseInt($("sub_sub_category_id").value, 10),
        title: $("title").value,
        slug: $("slug").value,
        summary: $("summary").value,
        raw_content: editorRoot.innerHTML,
      };
      const updated = await apiJson("PATCH", `/api/v1/subject-pages/${pageId}`, payload);
      currentPage = updated;
      return updated;
    }
    const created = await apiJson("POST", "/api/v1/subject-pages/", gatherPagePayload());
    window.location.href = `/editor/pages/${created.id}`;
    return created;
  }

  $("btn-save").addEventListener("click", () => saveDraft().catch((e) => setAnnStatus("error", e.message)));

  if (!isEdit) {
    $("btn-preview").disabled = true;
    $("btn-publish").disabled = true;
  }

  const previewBtn = $("btn-preview");
  if (previewBtn) {
    previewBtn.addEventListener("click", async () => {
      const pid = getPageId();
      if (!pid) return;
      const payload = { raw_content: editorRoot.innerHTML };
      const r = await apiJson("POST", `/api/v1/subject-pages/${pid}/preview`, payload);
      setPreviewHtml(r.rendered_content);
    });
  }

  const publishBtn = $("btn-publish");
  if (publishBtn) {
    publishBtn.addEventListener("click", async () => {
      const pid = getPageId();
      if (!pid) return;
      const r = await apiJson("POST", `/api/v1/subject-pages/${pid}/publish`, {});
      currentPage = r;
      const viewBtn = $("btn-view");
      if (viewBtn) {
        viewBtn.hidden = false;
        viewBtn.href = `/pages/${r.slug}`;
      }
      setPreviewHtml(r.rendered_content);
    });
  }

  $("btn-create-annotation").addEventListener("click", async () => {
    const pid = getPageId();
    if (!pid) {
      setAnnStatus("info", "Save draft first to create annotations (the page needs an id).");
      return;
    }
    if (!captured) {
      setAnnStatus("info", "Use “Use current selection” to capture text before creating an annotation.");
      return;
    }
    setAnnStatus("info", "");
    const createBtn = $("btn-create-annotation");
    setButtonLoading(createBtn, true, "Creating…");
    const type = $("ann_type").value;
    const body = $("ann_body").value;
    const payload = {
      annotation_type: type,
      trigger_text: captured.trigger,
      start_offset: captured.start_offset,
      end_offset: captured.end_offset,
      title: $("ann_title").value || "",
      body_text: type === "youtube" ? null : body || null,
      youtube_url: type === "youtube" ? ($("ann_youtube").value || null) : null,
      link_label: type === "link_note" ? ($("ann_link_label").value || null) : null,
      media_asset_id: ["image", "audio", "video"].includes(type) ? parseInt($("ann_media").value, 10) : null,
    };
    if (["image", "audio", "video"].includes(type) && !Number.isFinite(payload.media_asset_id)) {
      payload.media_asset_id = null;
    }
    try {
      await apiJson("POST", `/api/v1/subject-pages/${pid}/annotations`, payload);
      await refreshAnnotations(pid);
      setAnnStatus("success", "Annotation created.");
      captured = null;
      $("ann_trigger").value = "";
      syncCreateAnnotationEnabled();
      // Keep offsets stable: do not auto-re-render the editor content here.
    } catch (e) {
      setAnnStatus("error", e && e.message ? e.message : String(e));
    } finally {
      setButtonLoading(createBtn, false);
      syncCreateAnnotationEnabled();
    }
  });

  const refreshAnnBtn = $("btn-refresh-ann");
  if (refreshAnnBtn) {
    refreshAnnBtn.addEventListener("click", async () => {
      const pid = getPageId();
      if (!pid) return;
      await refreshAnnotations(pid);
    });
  }

  // Enable preview/publish for edit page.
  if (isEdit) {
    $("btn-preview").disabled = false;
    $("btn-publish").disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initEditorPage().catch((e) => {
    const err = document.getElementById("ann_error");
    if (err) err.textContent = e.message || String(e);
    else console.error(e);
  });
});


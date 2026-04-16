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

function recaptureOffsetsFromTrigger(editorRoot, triggerText, preferredStart = null) {
  const trigger = (triggerText || "").trim();
  if (!trigger) return null;
  const mapping = buildPlainMapping(editorRoot);
  if (mapping.length === 0) return null;
  const chars = new Array(mapping.length);
  for (let i = 0; i < mapping.length; i++) {
    const m = mapping[i];
    const text = m.node.nodeValue || "";
    chars[i] = text[m.offset] || "";
  }
  const plain = chars.join("");
  if (!plain) return null;

  const positions = [];
  let idx = plain.indexOf(trigger);
  while (idx !== -1) {
    positions.push(idx);
    idx = plain.indexOf(trigger, idx + 1);
  }
  if (positions.length === 0) return null;

  let best = positions[0];
  if (typeof preferredStart === "number" && Number.isFinite(preferredStart)) {
    let bestDist = Math.abs(best - preferredStart);
    for (const p of positions) {
      const d = Math.abs(p - preferredStart);
      if (d < bestDist) {
        bestDist = d;
        best = p;
      }
    }
  }

  return { trigger, start_offset: best, end_offset: best + trigger.length };
}

function previewPlainSlice(editorRoot, start, end) {
  const mapping = buildPlainMapping(editorRoot);
  const safeStart = Math.max(0, Math.min(mapping.length, start));
  const safeEnd = Math.max(0, Math.min(mapping.length, end));
  const chars = [];
  for (let i = safeStart; i < safeEnd; i++) {
    const m = mapping[i];
    const text = m.node.nodeValue || "";
    chars.push(text[m.offset] || "");
  }
  return chars.join("");
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
  const isMedia = ["image", "audio", "video"].includes(type);
  const isYoutube = type === "youtube";
  const isText = type === "text";
  $("ann_body_wrap").hidden = !isText;
  $("ann_youtube_wrap").hidden = !isYoutube;
  $("ann_media_wrap").hidden = !isMedia;
  if (!isMedia) {
    const m = $("ann_media");
    const meta = $("ann_media_meta");
    const file = $("ann_media_file");
    if (m) m.value = "";
    if (meta) meta.textContent = "";
    if (file) file.value = "";
  }
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
    if (!("prevDisabled" in btn.dataset)) btn.dataset.prevDisabled = btn.disabled ? "1" : "0";
    btn.textContent = loadingLabel;
    btn.disabled = true;
    btn.setAttribute("aria-busy", "true");
    return;
  }
  btn.textContent = btn.dataset.originalLabel || btn.textContent || "";
  btn.removeAttribute("aria-busy");
  if ("prevDisabled" in btn.dataset) {
    btn.disabled = btn.dataset.prevDisabled === "1";
    delete btn.dataset.prevDisabled;
  } else {
    btn.disabled = false;
  }
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
  const mediaPickBtn = $("btn-ann-pick-media");
  const mediaFileInput = $("ann_media_file");
  if (annType) {
    annType.addEventListener("change", () => {
      toggleAnnFields(annType.value);
      if (mediaPickBtn && mediaFileInput) {
        const t = annType.value;
        const label =
          t === "image"
            ? "Select image"
            : t === "audio"
              ? "Select audio"
              : t === "video"
                ? "Select video"
                : "Select file";
        mediaPickBtn.textContent = label;
        mediaFileInput.accept =
          t === "image" ? "image/*" : t === "audio" ? "audio/*" : t === "video" ? "video/*" : "";
      }
    });
  }
  toggleAnnFields(annType.value);
  if (mediaPickBtn && mediaFileInput) {
    mediaPickBtn.textContent = "Select file";
    mediaPickBtn.addEventListener("click", () => {
      if (!annType) return;
      const t = annType.value;
      if (!["image", "audio", "video"].includes(t)) {
        setAnnStatus("info", "Select Image, Audio, or Video to upload a file.");
        return;
      }
      setAnnStatus("info", "");
      mediaFileInput.click();
    });

    mediaFileInput.addEventListener("change", async () => {
      if (!annType) return;
      const t = annType.value;
      const f = mediaFileInput.files && mediaFileInput.files[0] ? mediaFileInput.files[0] : null;
      if (!f) return;
      const mime = f.type || "";
      const ok =
        (t === "image" && mime.startsWith("image/")) ||
        (t === "audio" && mime.startsWith("audio/")) ||
        (t === "video" && mime.startsWith("video/"));
      if (!ok) {
        setAnnStatus("error", `Invalid file type (${mime || "unknown"}). Please choose a ${t} file.`);
        mediaFileInput.value = "";
        return;
      }

      const pid = getPageId();
      if (!pid) {
        setAnnStatus("info", "Save draft in this modal first (the page needs an id) before uploading media.");
        mediaFileInput.value = "";
        return;
      }

      const title = ($("ann_title") && $("ann_title").value.trim()) || f.name;
      const alt = t === "image" ? title : "";
      const fd = new FormData();
      fd.append("file", f);
      fd.append("asset_type", t);
      fd.append("title", title);
      if (alt) fd.append("alt_text", alt);

      setAnnStatus("info", "");
      setButtonLoading(mediaPickBtn, true, "Uploading…");
      try {
        const resp = await fetch("/api/v1/media-assets/upload", { method: "POST", body: fd, headers: { Accept: "application/json" } });
        const text = await resp.text();
        const payload = text ? JSON.parse(text) : null;
        if (!resp.ok) {
          const msg = payload && payload.detail ? payload.detail : `Upload failed (${resp.status})`;
          throw new Error(msg);
        }
        const m = $("ann_media");
        const meta = $("ann_media_meta");
        if (m) m.value = String(payload.id);
        if (meta) meta.textContent = `Uploaded: ${f.name}`;
        setAnnStatus("success", "Media uploaded.");
        syncCreateAnnotationEnabled();
      } catch (e) {
        setAnnStatus("error", e && e.message ? e.message : String(e));
        mediaFileInput.value = "";
      } finally {
        setButtonLoading(mediaPickBtn, false);
      }
    });
  }

  const annModal = $("ann_modal");
  const annModalOverlay = $("ann_modal_overlay");
  const annModalDialog = $("ann_modal_dialog");
  const annPanel = $("ann_panel");
  const annOpen = $("btn-ann-open");
  const annClose = $("btn-ann-close");

  function openAnnModal() {
    if (!annModal) return;
    annModal.hidden = false;
    setAnnStatus("info", "");
    if (annType) toggleAnnFields(annType.value);
    const focusEl = annModalDialog || $("ann_title");
    if (focusEl) focusEl.focus();
  }

  function closeAnnModal() {
    if (!annModal) return;
    annModal.hidden = true;
    setAnnStatus("info", "");
  }

  if (annOpen && annModal) {
    annOpen.addEventListener("click", () => {
      // Prefer capturing selection on open so the flow is: select text -> add annotation.
      const res = selectionOffsets(editorRoot);
      if (res && res.error) {
        openAnnModal();
        setAnnStatus("error", res.error);
        return;
      }
      captured = res;
      $("ann_trigger").value = captured ? captured.trigger : "";
      openAnnModal();
      if (annType) toggleAnnFields(annType.value);
      syncCreateAnnotationEnabled();
      if (!getPageId()) {
        setAnnStatus("info", "Save draft to enable annotations on this page.");
      }
    });
  }

  if (annClose && annModal) annClose.addEventListener("click", closeAnnModal);
  if (annModalOverlay && annModal) annModalOverlay.addEventListener("click", closeAnnModal);
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (annModal && !annModal.hidden) closeAnnModal();
  });

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
      if (window.toast) window.toast("success", "Saved", "Your changes were saved.");
      return updated;
    }
    const created = await apiJson("POST", "/api/v1/subject-pages/", gatherPagePayload());
    window.location.href = `/editor/pages/${created.id}`;
    return created;
  }

  $("btn-save").addEventListener("click", () => {
    saveDraft().catch((e) => {
      setAnnStatus("error", e.message);
      if (window.toast) window.toast("error", "Save failed", e.message || "Unable to save.");
    });
  });

  async function saveDraftInPlace() {
    setAnnStatus("info", "");
    const created = await apiJson("POST", "/api/v1/subject-pages/", gatherPagePayload());
    const pageIdEl = $("page_id");
    if (pageIdEl) pageIdEl.value = String(created.id);
    setAnnStatus("success", "Draft saved.");
    if (window.toast) window.toast("success", "Draft saved", "You can now publish or add annotations.");
    // Sync editor DOM to server-stored HTML to keep offset mapping consistent with backend.
    if (created && typeof created.raw_content === "string") {
      editorRoot.innerHTML = created.raw_content || "<p></p>";
    } else if (created && created.id) {
      try {
        const fresh = await apiGet(`/api/v1/subject-pages/${created.id}`);
        if (fresh && typeof fresh.raw_content === "string") {
          editorRoot.innerHTML = fresh.raw_content || "<p></p>";
        }
      } catch {
        // Ignore and keep current DOM if fetch fails.
      }
    }
    // After saving, re-capture offsets from trigger text to avoid stale/out-of-range offsets.
    if (captured && captured.trigger) {
      const rebuilt = recaptureOffsetsFromTrigger(editorRoot, captured.trigger, captured.start_offset);
      if (rebuilt) {
        captured = rebuilt;
        $("ann_trigger").value = rebuilt.trigger;
      }
    }
    // Enable preview/publish once we have an id.
    const publishBtn = $("btn-publish");
    if (publishBtn) publishBtn.disabled = false;
    syncCreateAnnotationEnabled();
    return created;
  }

  const annSaveDraftBtn = $("btn-ann-save-draft");
  if (annSaveDraftBtn) {
    annSaveDraftBtn.addEventListener("click", async () => {
      if (getPageId()) {
        setAnnStatus("info", "Draft already saved.");
        return;
      }
      setButtonLoading(annSaveDraftBtn, true, "Saving…");
      try {
        await saveDraftInPlace();
      } catch (e) {
        setAnnStatus("error", e && e.message ? e.message : String(e));
        if (window.toast) window.toast("error", "Save failed", e && e.message ? e.message : String(e));
      } finally {
        setButtonLoading(annSaveDraftBtn, false);
      }
    });
  }

  if (!isEdit) {
    $("btn-publish").disabled = true;
  }

  const publishBtn = $("btn-publish");
  if (publishBtn) {
    publishBtn.addEventListener("click", async () => {
      const pid = getPageId();
      if (!pid) return;
      try {
        const r = await apiJson("POST", `/api/v1/subject-pages/${pid}/publish`, {});
        currentPage = r;
        const viewBtn = $("btn-view");
        if (viewBtn) {
          viewBtn.hidden = false;
          viewBtn.href = `/pages/${r.slug}`;
        }
        setPreviewHtml(r.rendered_content);
        if (window.toast) window.toast("success", "Published", "Your page is now public.");
      } catch (e) {
        const msg = e && e.message ? e.message : String(e);
        setAnnStatus("error", msg);
        if (window.toast) window.toast("error", "Publish failed", msg);
      }
    });
  }

  $("btn-create-annotation").addEventListener("click", async () => {
    const pid = getPageId();
    if (!pid) {
      setAnnStatus("info", "Save draft in this modal first (the page needs an id).");
      return;
    }
    if (!captured) {
      setAnnStatus("info", "Use “Use current selection” to capture text before creating an annotation.");
      return;
    }
    // Defensive: ensure offsets still map into current content.
    const mappingLen = buildPlainMapping(editorRoot).length;
    if (captured.start_offset < 0 || captured.end_offset > mappingLen) {
      const rebuilt = recaptureOffsetsFromTrigger(editorRoot, captured.trigger, captured.start_offset);
      if (rebuilt) {
        captured = rebuilt;
        $("ann_trigger").value = rebuilt.trigger;
        syncCreateAnnotationEnabled();
      } else {
        setAnnStatus("error", "Selection is stale. Use “Use current selection” again, then create the annotation.");
        return;
      }
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
      body_text: type === "text" ? (body || null) : null,
      youtube_url: type === "youtube" ? ($("ann_youtube").value || null) : null,
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
    $("btn-publish").disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initEditorPage().catch((e) => {
    const err = document.getElementById("ann_error");
    if (err) err.textContent = e && e.message ? e.message : String(e);
    else console.error(e);
  });
});


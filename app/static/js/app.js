function getFocusableElements(root) {
  const selector =
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
  return Array.from(root.querySelectorAll(selector)).filter((el) => !el.hasAttribute("disabled") && !el.getAttribute("aria-hidden"));
}

function createEl(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k === "html") el.innerHTML = v;
    else el.setAttribute(k, v);
  }
  for (const child of children) el.appendChild(child);
  return el;
}

function toast(kind, title, message, { timeoutMs = 2400 } = {}) {
  const root = document.getElementById("toast-root");
  if (!root) return;
  const t = createEl("div", { class: `toast toast--${kind}` }, [
    createEl("div", { class: "toast__title", text: title || "" }),
    createEl("div", { class: "toast__msg", text: message || "" }),
  ]);
  root.appendChild(t);
  // Trigger transition on next frame.
  requestAnimationFrame(() => t.classList.add("toast--show"));
  window.setTimeout(() => {
    t.classList.remove("toast--show");
    window.setTimeout(() => t.remove(), 220);
  }, timeoutMs);
}

window.toast = toast;

function initAccordion() {
  const root = document.querySelector("[data-accordion]");
  if (!root) return;

  root.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-accordion-trigger]");
    if (!trigger) return;
    const panelId = trigger.getAttribute("aria-controls");
    const panel = panelId ? document.getElementById(panelId) : null;
    if (!panel) return;

    const expanded = trigger.getAttribute("aria-expanded") === "true";
    trigger.setAttribute("aria-expanded", expanded ? "false" : "true");
    if (expanded) panel.setAttribute("hidden", "");
    else panel.removeAttribute("hidden");
  });
}

function initModal() {
  const modalRoot = document.querySelector("[data-modal-root]");
  if (!modalRoot) return;

  const overlay = modalRoot.querySelector("[data-modal-overlay]");
  const dialog = modalRoot.querySelector("[data-modal-dialog]");
  const closeBtn = modalRoot.querySelector("[data-modal-close]");
  const titleEl = modalRoot.querySelector("[data-modal-title]");
  const descEl = modalRoot.querySelector("[data-modal-description]");
  const bodyEl = modalRoot.querySelector("[data-modal-body]");
  const footerEl = modalRoot.querySelector("[data-modal-footer]");

  let lastActive = null;
  let trapEnabled = false;

  function open() {
    lastActive = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    modalRoot.hidden = false;
    document.body.style.overflow = "hidden";
    trapEnabled = true;
    window.setTimeout(() => {
      closeBtn?.focus();
    }, 0);
  }

  function close() {
    trapEnabled = false;
    modalRoot.hidden = true;
    document.body.style.overflow = "";
    bodyEl.innerHTML = "";
    footerEl.hidden = true;
    footerEl.innerHTML = "";
    if (lastActive && document.contains(lastActive)) lastActive.focus();
  }

  function onKeyDown(e) {
    if (modalRoot.hidden) return;
    if (e.key === "Escape") {
      e.preventDefault();
      close();
      return;
    }
    if (e.key !== "Tab" || !trapEnabled) return;
    const focusables = getFocusableElements(dialog);
    if (focusables.length === 0) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;
    if (e.shiftKey) {
      if (active === first || active === dialog) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (active === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  async function fetchContent(contentId) {
    const resp = await fetch(`/api/content/${encodeURIComponent(contentId)}`, { headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(`Failed to load content (${resp.status})`);
    return resp.json();
  }

  function renderContent(item) {
    titleEl.textContent = item.title || "";
    descEl.textContent = item.description || "";
    bodyEl.innerHTML = "";
    footerEl.hidden = true;
    footerEl.innerHTML = "";

    if (item.type === "text") {
      bodyEl.appendChild(createEl("p", { text: item.body_text || "" }));
      return;
    }

    if (item.type === "link_note") {
      bodyEl.appendChild(createEl("p", { text: item.body_text || "" }));
      if (item.asset_url) {
        footerEl.hidden = false;
        const link = createEl("a", {
          href: item.asset_url,
          target: "_blank",
          rel: "noreferrer",
          class: "term term--inline",
        });
        link.textContent = item.link_label || "Open link";
        footerEl.appendChild(link);
      }
      return;
    }

    if (item.type === "image") {
      const img = createEl("img", {
        src: item.asset_url || "",
        alt: item.title || "Image",
        loading: "lazy",
      });
      bodyEl.appendChild(createEl("div", { class: "modal-media" }, [img]));
      return;
    }

    if (item.type === "audio") {
      const audio = createEl("audio", { controls: "true", src: item.asset_url || "" });
      bodyEl.appendChild(createEl("div", { class: "modal-media" }, [audio]));
      return;
    }

    if (item.type === "video") {
      const video = createEl("video", { controls: "true", src: item.asset_url || "" });
      bodyEl.appendChild(createEl("div", { class: "modal-media" }, [video]));
      return;
    }

    if (item.type === "youtube") {
      const embedUrl = item.embed_url || "";
      const watchUrl = item.asset_url || "";
      const iframe = createEl("iframe", {
        src: embedUrl,
        title: item.title || "YouTube video",
        allow: "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
        referrerpolicy: "strict-origin-when-cross-origin",
        allowfullscreen: "true",
      });
      bodyEl.appendChild(createEl("div", { class: "modal-media" }, [iframe]));

      footerEl.hidden = false;
      const link = createEl("a", { href: watchUrl, target: "_blank", rel: "noreferrer", class: "term term--inline" });
      link.textContent = "Open on YouTube";
      footerEl.appendChild(link);

      window.setTimeout(() => {
        if (!iframe.contentWindow) return;
      }, 1200);
      return;
    }

    if (item.type === "link_note") {
      bodyEl.appendChild(createEl("p", { text: item.body_text || "" }));
      const linkUrl = item.asset_url || "";
      if (linkUrl) {
        footerEl.hidden = false;
        const link = createEl("a", {
          href: linkUrl,
          target: "_blank",
          rel: "noreferrer",
          class: "term term--inline",
        });
        link.textContent = item.link_label || "Open link";
        footerEl.appendChild(link);
      }
      return;
    }

    bodyEl.appendChild(createEl("p", { text: "Unsupported content type." }));
  }

  async function openForContentId(contentId) {
    try {
      const item = await fetchContent(contentId);
      renderContent(item);
      open();
    } catch (err) {
      titleEl.textContent = "Error";
      descEl.textContent = "Unable to load content.";
      bodyEl.innerHTML = "";
      bodyEl.appendChild(createEl("p", { text: String(err?.message || err) }));
      open();
    }
  }

  function loadEmbeddedAnnotations() {
    const el = document.getElementById("edumedia-annotations");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "[]");
    } catch {
      return [];
    }
  }

  const embeddedAnnotations = loadEmbeddedAnnotations();
  if (embeddedAnnotations) {
    window.__EDUMEDIA_ANNOTATIONS__ = embeddedAnnotations;
  }

  function findAnnotationItem(id) {
    const items = window.__EDUMEDIA_ANNOTATIONS__ || [];
    return items.find((x) => String(x.id) === String(id));
  }

  document.addEventListener("click", (e) => {
    const annoTrigger = e.target.closest("[data-annotation-id]");
    if (annoTrigger) {
      e.preventDefault();
      const id = annoTrigger.getAttribute("data-annotation-id");
      const item = id ? findAnnotationItem(id) : null;
      if (item) {
        renderContent(item);
        open();
      }
      return;
    }

    const trigger = e.target.closest('[data-action="open-content"][data-content-id]');
    if (trigger) {
      e.preventDefault();
      openForContentId(trigger.getAttribute("data-content-id"));
      return;
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const active = document.activeElement;
    if (!active) return;
    const anno = active.closest && active.closest("[data-annotation-id]");
    if (!anno) return;
    e.preventDefault();
    const id = anno.getAttribute("data-annotation-id");
    const item = id ? findAnnotationItem(id) : null;
    if (item) {
      renderContent(item);
      open();
    }
  });

  closeBtn?.addEventListener("click", () => close());
  overlay?.addEventListener("click", () => close());
  document.addEventListener("keydown", onKeyDown);
}

async function loadPublishedPages() {
  const listEl = document.getElementById("landing-pages-list");
  const emptyEl = document.getElementById("landing-pages-empty");
  const errEl = document.getElementById("landing-pages-error");
  if (!listEl || !emptyEl || !errEl) return;

  errEl.textContent = "";
  listEl.innerHTML = "";
  emptyEl.hidden = true;

  try {
    const resp = await fetch("/api/v1/subject-pages/?status=published", { headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(`Failed to load pages (${resp.status})`);
    const pages = await resp.json();
    emptyEl.hidden = pages.length !== 0;
    for (const p of pages) {
      const row = createEl("div", { class: "landing__page-item" }, [
        createEl("div", { class: "landing__page-title", text: p.title || "" }),
        createEl("div", { class: "landing__page-summary", text: p.summary || "" }),
      ]);
      const actions = createEl("div", { class: "toolbar" }, [
        createEl("a", { class: "btn", href: `/pages/${p.slug}`, text: "Open" }),
      ]);
      row.appendChild(actions);
      listEl.appendChild(row);
    }
  } catch (e) {
    errEl.textContent = e && e.message ? e.message : String(e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initAccordion();
  initModal();
  loadPublishedPages();
});

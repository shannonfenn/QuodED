const BACKENDS = ["lean4", "rocq", "isabelle", "agda"];

const state = {
  docId: null,
  docs: [],
  manifest: null,
  layout: null,
  segments: [],
  tasks: [],
  runs: [],
  events: {},
  policy: {},
  activeSegmentId: null,
};

const $ = (id) => document.getElementById(id);

function setStatus(text) {
  $("status").textContent = text;
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${url}`);
  }
  return response.json();
}

async function safeFetch(url) {
  try {
    return await fetchJson(url);
  } catch (err) {
    return null;
  }
}

function getRequestedDoc() {
  const params = new URLSearchParams(window.location.search);
  return params.get("doc") || params.get("doc_id");
}

function renderDocSelect() {
  const select = $("doc-select");
  select.innerHTML = "";
  state.docs.forEach((docId) => {
    const option = document.createElement("option");
    option.value = docId;
    option.textContent = docId;
    select.appendChild(option);
  });
  if (state.docId) {
    select.value = state.docId;
  }
}

function summaryBadges(entries) {
  return entries
    .map(
      (entry) =>
        `<span class="badge">${entry.label}: ${entry.value}</span>`
    )
    .join("");
}

function renderManifest() {
  const meta = $("doc-meta");
  const manifestBox = $("manifest");
  if (!state.manifest) {
    meta.textContent = "Manifest not found. Run import-pdf first.";
    manifestBox.innerHTML = "";
    const openButton = $("open-pdf");
    if (openButton) {
      openButton.disabled = true;
    }
    return;
  }
  meta.textContent = `${state.manifest.doc_id} • ${state.manifest.page_count} pages`;
  const openButton = $("open-pdf");
  if (openButton) {
    openButton.disabled = false;
  }
  manifestBox.innerHTML = `
    <div class="item">
      <strong>Source</strong>
      <small>${state.manifest.source_path}</small>
    </div>
    <div class="item">
      <strong>Workspace</strong>
      <small>${state.manifest.segments_path}</small>
    </div>
    <div class="item">
      <strong>Created</strong>
      <small>${state.manifest.created_at}</small>
    </div>
  `;
}

function renderSegments() {
  const summary = $("segment-summary");
  const list = $("segments");
  if (!state.segments || state.segments.length === 0) {
    summary.innerHTML = "";
    list.innerHTML = '<div class="muted">No segments yet.</div>';
    return;
  }
  const counts = {};
  state.segments.forEach((segment) => {
    counts[segment.kind] = (counts[segment.kind] || 0) + 1;
  });
  const entries = Object.entries(counts).map(([label, value]) => ({
    label,
    value,
  }));
  const badges = [{ label: "Total", value: state.segments.length }, ...entries];
  if (state.activeSegmentId) {
    badges.push({ label: "Active", value: `#${state.activeSegmentId}` });
  }
  summary.innerHTML = summaryBadges(badges);
  list.innerHTML = state.segments
    .map(
      (segment) => `
      <div class="item segment-item ${
        state.activeSegmentId === Number(segment.segment_id) ? "active" : ""
      }" data-segment-id="${segment.segment_id}">
        <strong>${segment.kind} ${segment.segment_id}</strong>
        <div>${segment.title}</div>
        <small>Pages ${segment.start_page} - ${segment.end_page}</small>
      </div>
    `
    )
    .join("");
  list.querySelectorAll(".segment-item").forEach((item) => {
    item.addEventListener("click", () => {
      const segmentId = Number(item.dataset.segmentId);
      setActiveSegment(segmentId);
    });
  });
}

function renderTasks() {
  const summary = $("task-summary");
  const list = $("tasks-list");
  if (!state.tasks || state.tasks.length === 0) {
    summary.innerHTML = "";
    list.innerHTML = '<div class="muted">No tasks yet.</div>';
    return;
  }
  const visibleTasks = state.activeSegmentId
    ? state.tasks.filter(
        (task) => Number(task.segment_id) === state.activeSegmentId
      )
    : state.tasks;
  const counts = {};
  visibleTasks.forEach((task) => {
    counts[task.status] = (counts[task.status] || 0) + 1;
  });
  const entries = Object.entries(counts).map(([label, value]) => ({
    label,
    value,
  }));
  const badges = [
    { label: "Total", value: visibleTasks.length },
    ...entries,
  ];
  if (state.activeSegmentId) {
    badges.push({ label: "Filter", value: `Segment #${state.activeSegmentId}` });
  }
  summary.innerHTML = summaryBadges(badges);
  if (state.activeSegmentId) {
    summary.innerHTML += ' <button id="clear-filter" class="btn ghost">Clear filter</button>';
  }
  list.innerHTML = visibleTasks
    .map(
      (task) => `
      <div class="item task-item ${
        state.activeSegmentId === Number(task.segment_id) ? "active" : ""
      }" data-segment-id="${task.segment_id}">
        <strong>${task.kind} ${task.task_id}: ${task.title}</strong>
        <small>Status: ${task.status} | Backend: ${task.backend || "unassigned"}</small>
      </div>
    `
    )
    .join("");
  list.querySelectorAll(".task-item").forEach((item) => {
    item.addEventListener("click", () => {
      const segmentId = Number(item.dataset.segmentId);
      setActiveSegment(segmentId);
    });
  });
  const clearButton = $("clear-filter");
  if (clearButton) {
    clearButton.addEventListener("click", () => {
      setActiveSegment(null);
    });
  }
}

function renderPolicies() {
  const grid = $("policy-grid");
  grid.innerHTML = BACKENDS.map((backend) => {
    const policy = state.policy[backend];
    if (!policy) {
      return `
        <div class="card policy-card">
          <div class="policy-header">
            <h3>${backend}</h3>
            <button class="btn ghost policy-scan" data-backend="${backend}">Scan</button>
          </div>
          <div class="muted">No data yet.</div>
        </div>
      `;
    }
    const violations = policy.violations || [];
    const badgeClass = policy.ok ? "ok" : "warn";
    return `
      <div class="card policy-card">
        <div class="policy-header">
          <h3>${backend}</h3>
          <button class="btn ghost policy-scan" data-backend="${backend}">Scan</button>
        </div>
        <div class="summary">
          <span class="badge ${badgeClass}">${policy.ok ? "OK" : "Violations"}</span>
          <span class="badge">${violations.length} issues</span>
        </div>
        <div class="muted">${policy.note || "Scanned at " + policy.scanned_at}</div>
        <div class="list">
          ${violations
            .slice(0, 10)
            .map(
              (v) => `
              <div class="item">
                <strong>${v.rule}</strong>
                <small>${v.file}:${v.line}</small>
                <small>${v.text}</small>
              </div>
            `
            )
            .join("")}
          ${violations.length > 10 ? '<div class="muted">More violations not shown.</div>' : ""}
        </div>
      </div>
    `;
  }).join("");

  grid.querySelectorAll(".policy-scan").forEach((button) => {
    button.addEventListener("click", async () => {
      const backend = button.dataset.backend;
      await refreshPolicy(backend);
    });
  });
}

function renderRuns() {
  const list = $("runs-list");
  if (!state.runs || state.runs.length === 0) {
    list.innerHTML = '<div class="muted">No runs yet. Create one via CLI.</div>';
    return;
  }
  list.innerHTML = state.runs
    .map(
      (run) => `
      <div class="item run-item" data-run="${run.run_id}">
        <strong>${run.run_id}</strong>
        <small>${run.doc_id} • ${run.backend}</small>
        <small>Status: ${run.status} • Updated: ${run.updated_at}</small>
      </div>
    `
    )
    .join("");
  list.querySelectorAll(".run-item").forEach((item) => {
    item.addEventListener("click", async () => {
      const runId = item.dataset.run;
      await loadRunEvents(runId);
    });
  });
}

function renderRunDetail(runId) {
  const detail = $("run-detail");
  const events = state.events[runId] || [];
  if (!runId) {
    detail.innerHTML = '<div class="muted">Select a run to view events.</div>';
    return;
  }
  if (events.length === 0) {
    detail.innerHTML = '<div class="muted">No events logged yet.</div>';
    return;
  }
  detail.innerHTML = events
    .map(
      (event) => `
      <div class="item">
        <strong>${event.kind}</strong>
        <small>${event.created_at}</small>
        <div>${event.message}</div>
      </div>
    `
    )
    .join("");
}

async function loadDocs() {
  const data = await safeFetch("/api/docs");
  state.docs = data ? data.docs : [];
  const requested = getRequestedDoc();
  state.docId =
    (requested && state.docs.includes(requested) && requested) ||
    data?.default ||
    state.docs[0] ||
    null;
  renderDocSelect();
}

async function loadDocData() {
  if (!state.docId) {
    setStatus("No documents found. Import a PDF first.");
    return;
  }
  state.activeSegmentId = null;
  state.layout = null;
  const manifestUrl = `/api/docs/${state.docId}/manifest`;
  const segmentsUrl = `/api/docs/${state.docId}/segments`;
  const tasksUrl = `/api/docs/${state.docId}/tasks`;
  const [manifest, segments, tasks] = await Promise.all([
    safeFetch(manifestUrl),
    safeFetch(segmentsUrl),
    safeFetch(tasksUrl),
  ]);
  state.manifest = manifest;
  state.segments = segments || [];
  state.tasks = tasks || [];
  renderManifest();
  renderSegments();
  renderTasks();
  await loadLayout();
  await loadPolicies();
}

async function loadPolicies() {
  const results = await Promise.all(
    BACKENDS.map((backend) =>
      safeFetch(`/api/docs/${state.docId}/policy/${backend}`)
    )
  );
  results.forEach((policy, index) => {
    state.policy[BACKENDS[index]] = policy;
  });
  renderPolicies();
}

async function refreshPolicy(backend) {
  const policy = await safeFetch(`/api/docs/${state.docId}/policy/${backend}`);
  state.policy[backend] = policy;
  renderPolicies();
  setStatus(`Policy scan refreshed for ${backend}.`);
}

async function loadRuns() {
  const data = await safeFetch("/api/runs");
  state.runs = data ? data.runs : [];
  renderRuns();
}

async function loadRunEvents(runId) {
  const data = await safeFetch(`/api/runs/${runId}/events`);
  state.events[runId] = data ? data.events : [];
  renderRunDetail(runId);
}

async function loadLayout() {
  const layout = await safeFetch(`/api/docs/${state.docId}/layout`);
  state.layout = layout && !layout.note ? layout : null;
  renderPages(layout?.note);
}

function renderPages(note) {
  const container = $("pdf-pages");
  const empty = $("pdf-empty");
  container.innerHTML = "";
  const pages =
    state.layout?.pages ||
    (state.manifest
      ? Array.from({ length: state.manifest.page_count || 0 }, (_, idx) => ({
          page: idx + 1,
        }))
      : []);
  if (!pages.length) {
    empty.textContent = note || "Layout not available. Install pdfplumber and Poppler.";
    empty.classList.remove("hidden");
    return;
  }
  if (note) {
    empty.textContent = note;
    empty.classList.remove("hidden");
  } else {
    empty.classList.add("hidden");
  }
  pages.forEach((page) => {
    const pageEl = document.createElement("div");
    pageEl.className = "pdf-page";
    pageEl.dataset.page = page.page;
    pageEl.innerHTML = `
      <div class="page-label">Page ${page.page}</div>
      <img loading="lazy" src="/api/docs/${state.docId}/page/${page.page}.png" alt="Page ${page.page}" />
      <div class="page-overlay"></div>
    `;
    const img = pageEl.querySelector("img");
    img.addEventListener("load", () => updatePageHighlightPositions(pageEl));
    container.appendChild(pageEl);
  });
  renderHighlights();
}

function closeSidePanels() {
  $("segments-sidebar").classList.add("hidden");
  $("doc-info").classList.add("hidden");
}

function renderHighlights() {
  if (!state.layout) {
    return;
  }
  const highlightsByPage = new Map();
  (state.layout.highlights || []).forEach((highlight) => {
    const page = highlight.page;
    if (!highlightsByPage.has(page)) {
      highlightsByPage.set(page, []);
    }
    highlightsByPage.get(page).push(highlight);
  });
  document.querySelectorAll(".pdf-page").forEach((pageEl) => {
    const pageNum = Number(pageEl.dataset.page);
    const overlay = pageEl.querySelector(".page-overlay");
    overlay.innerHTML = "";
    const highlights = highlightsByPage.get(pageNum) || [];
    highlights.forEach((highlight) => {
      const segmentId = Number(highlight.segment_id);
      const box = document.createElement("div");
      box.className = `highlight${
        segmentId === state.activeSegmentId ? " active" : ""
      }`;
      box.dataset.segmentId = segmentId;
      box.dataset.x0 = highlight.x0;
      box.dataset.y0 = highlight.y0;
      box.dataset.x1 = highlight.x1;
      box.dataset.y1 = highlight.y1;
      box.title = `${highlight.kind} ${segmentId}: ${highlight.title}`;
      box.addEventListener("click", (event) => {
        event.stopPropagation();
        setActiveSegment(segmentId);
      });
      overlay.appendChild(box);
    });
    updatePageHighlightPositions(pageEl);
  });
}

function updatePageHighlightPositions(pageEl) {
  if (!state.layout) {
    return;
  }
  const pageNum = Number(pageEl.dataset.page);
  const pageMeta = (state.layout.pages || []).find((entry) => entry.page === pageNum);
  if (!pageMeta) {
    return;
  }
  const img = pageEl.querySelector("img");
  if (!img || !img.clientWidth) {
    return;
  }
  const scale = img.clientWidth / pageMeta.width;
  const overlay = pageEl.querySelector(".page-overlay");
  overlay.style.width = `${img.clientWidth}px`;
  overlay.style.height = `${img.clientHeight}px`;
  overlay.querySelectorAll(".highlight").forEach((box) => {
    const x0 = Number(box.dataset.x0);
    const y0 = Number(box.dataset.y0);
    const x1 = Number(box.dataset.x1);
    const y1 = Number(box.dataset.y1);
    box.style.left = `${x0 * scale}px`;
    box.style.top = `${y0 * scale}px`;
    box.style.width = `${(x1 - x0) * scale}px`;
    box.style.height = `${(y1 - y0) * scale}px`;
  });
}

function updateAllHighlightPositions() {
  document.querySelectorAll(".pdf-page").forEach((pageEl) => {
    updatePageHighlightPositions(pageEl);
  });
}

function scrollToSegment(segmentId) {
  const target = document.querySelector(
    `.highlight[data-segment-id="${segmentId}"]`
  );
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function setActiveSegment(segmentId) {
  state.activeSegmentId = segmentId;
  const segment = state.segments.find(
    (entry) => Number(entry.segment_id) === segmentId
  );
  renderSegments();
  renderTasks();
  renderHighlights();
  if (segment) {
    scrollToSegment(segment.segment_id);
    setStatus(`Selected segment #${segment.segment_id}.`);
    closeSidePanels();
  } else {
    setStatus("Cleared segment filter.");
  }
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      const target = tab.dataset.target;
      panels.forEach((panel) => {
        panel.style.display = panel.id === target ? "block" : "none";
      });
    });
  });
  if (tabs[0]) {
    tabs[0].click();
  }
}

function setupControls() {
  $("doc-select").addEventListener("change", async (event) => {
    state.docId = event.target.value;
    await reloadAll();
  });
  $("refresh-btn").addEventListener("click", async () => {
    await reloadAll();
  });
  $("segments-toggle").addEventListener("click", () => {
    $("segments-sidebar").classList.toggle("hidden");
  });
  $("segments-close").addEventListener("click", () => {
    $("segments-sidebar").classList.add("hidden");
  });
  $("doc-info-toggle").addEventListener("click", () => {
    $("doc-info").classList.toggle("hidden");
  });
  $("doc-info-close").addEventListener("click", () => {
    $("doc-info").classList.add("hidden");
  });
  $("open-pdf").addEventListener("click", () => {
    if (!state.manifest) {
      return;
    }
    window.open(`/api/docs/${state.docId}/pdf`, "_blank");
  });
}

async function reloadAll() {
  setStatus("Refreshing data...");
  await loadDocData();
  await loadRuns();
  setStatus(`Last updated ${new Date().toLocaleTimeString()}`);
}

async function init() {
  setupTabs();
  setupControls();
  window.addEventListener("resize", () => {
    updateAllHighlightPositions();
  });
  await loadDocs();
  await reloadAll();
}

document.addEventListener("DOMContentLoaded", init);

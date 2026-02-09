# Add page-rendered PDF view with segment highlights

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

We need the UI to support visual reasoning directly on the paper. After this change, the document view will render PDF pages as images and overlay segment highlights anchored to the actual header text. Clicking a segment or task will scroll to the highlighted region on the page and show the associated task, so users can read the paper and jump between the proof text and Lean tasks without leaving the UI.

## Progress

- [x] (2026-02-05 10:12Z) Add a PDF layout extractor that uses `pdfplumber` to capture header line bounding boxes for segments and stores the layout cache.
- [x] (2026-02-05 10:12Z) Add a page image renderer that uses `pdftoppm` on demand and serves cached page PNGs.
- [x] (2026-02-05 10:12Z) Replace the iframe PDF view with a scrollable page image view and overlay highlight boxes.
- [x] (2026-02-05 10:12Z) Wire segment/task clicks to scroll to highlights and keep the UI readable at full-page scale.
- [ ] (2026-02-05 10:12Z) Update docs and validate the UI by selecting a segment and seeing it highlighted on the page (completed: docs updates; remaining: validation).

## Surprises & Discoveries

- Observation: `uv add pdfplumber` failed due to missing network/DNS, so the dependency could not be downloaded in this environment.
  Evidence: `error: Request failed after 3 retries ... failed to lookup address information`.

- Observation: Early PDF pages failed to render because Poppler zero-padded output filenames (e.g., `page-01.png`) while the server requested `page-1.png`.
  Evidence: `pdftoppm -progress` reported output `/tmp/quoded-testpage-01.png` and `/api/docs/.../page/1.png` returned `{"note": "page render failed"}`.

## Decision Log

- Decision: Render PDF pages to PNGs using Poppler (`pdftoppm`) and overlay highlights in HTML instead of relying on the browser PDF viewer.
  Rationale: The browser PDF viewer cannot be reliably overlaid for precise highlights, while page images allow accurate positioning and interaction.
  Date/Author: 2026-02-05 / Codex

- Decision: Extract header line bounding boxes with `pdfplumber` and map them to segments in order.
  Rationale: This is the fastest way to connect segment metadata to visual locations without building a full PDF text region model.
  Date/Author: 2026-02-05 / Codex

## Outcomes & Retrospective

- Not started.

## Context and Orientation

The UI server lives in `src/quoded/ui/server.py` and serves static assets from `src/quoded/ui/assets/`. The document view currently embeds a PDF in an iframe and shows segments and tasks in side panels, but there is no precise visual linkage between the paper and the tasks. Segment metadata is stored in `.quoded/docs/<doc-id>/segments.json` with `segment_id`, `kind`, `title`, `start_page`, and `end_page`. The source PDF path is stored in `.quoded/docs/<doc-id>/manifest.json` as `source_path`.

A “highlight” in this plan means an overlay rectangle positioned on a rendered page image, anchored to the header line that starts a segment (for example, “Theorem 1.3”). When the user clicks a segment or task, we will scroll the page list to that highlight and show the highlight visually.

## Plan of Work

First, add `pdfplumber` as a dependency using `uv add` so we can extract text with bounding boxes. Create a new module under `src/quoded/ui/` that reads the PDF, walks pages in order, groups words into lines, and identifies segment header lines using the same `SEGMENT_PATTERN` as the segmenter. Map each detected header line to the next segment in `segments.json` and store the highlight list plus page size metadata in a cache file under `.quoded/docs/<doc-id>/layout.json`.

Second, implement a page rendering helper in the UI server to generate page PNGs on demand with `pdftoppm` and cache them under `.quoded/docs/<doc-id>/pages/page-<n>.png`. Add API endpoints to serve the layout JSON and the page PNGs.

Third, replace the iframe-based PDF view with a scrollable list of page images. Each page image should have a positioned overlay container where highlight rectangles are drawn. Use the cached layout metadata to convert PDF points to pixel coordinates with the render scale so the highlights align with the page image. Add click handlers on highlight boxes to select the segment and update the task list, and keep segment/task list clicks scrolling to the highlight.

Finally, update documentation and verify manually by selecting a segment and confirming that the highlight appears on the correct page and the task list filters accordingly.

## Concrete Steps

Run all commands from the repository root: `/Users/shannon/dev/src/codex/QuodED`.

1) Add `pdfplumber` dependency:

   - Run `uv add pdfplumber`.

2) Add layout extraction and cache:

   - Create `src/quoded/ui/pdf_layout.py` with functions to build and read `layout.json` for a document.
   - Use `pdfplumber` to extract words, group lines, match `SEGMENT_PATTERN`, and record header line bounding boxes.

3) Add page rendering and API endpoints:

   - Update `src/quoded/ui/server.py` with a `/api/docs/<doc-id>/layout` endpoint.
   - Add `/api/docs/<doc-id>/page/<n>.png` that renders with `pdftoppm` when needed.

4) Update UI assets:

   - Replace the iframe in `src/quoded/ui/assets/index.html` with a page image list and overlay containers.
   - Update `src/quoded/ui/assets/styles.css` to style pages and highlight boxes.
   - Update `src/quoded/ui/assets/app.js` to render pages and highlights, and wire click/scroll behavior.

5) Update docs and validate:

   - Update `docs/UI.md` and `STATUS.md`.
   - Run `uv run quoded ui --doc-id hodge-1` and confirm that selecting a segment scrolls to a visible highlight on the page.

## Validation and Acceptance

The change is accepted when:

- The document view shows rendered page images for `hodge-1` without relying on the browser PDF viewer.
- Clicking a segment in the list scrolls to a highlight rectangle positioned over the header line on the page.
- Clicking the highlight filters the task list to the associated segment.

## Idempotence and Recovery

The page rendering cache can be regenerated at any time by deleting `.quoded/docs/<doc-id>/pages/`. The layout cache can be regenerated by deleting `.quoded/docs/<doc-id>/layout.json`. The UI server regenerates missing caches on demand.

## Artifacts and Notes

Expected layout cache fields in `.quoded/docs/<doc-id>/layout.json`:

    {
      "doc_id": "hodge-1",
      "dpi": 144,
      "scale": 2.0,
      "pages": [{"page": 1, "width": 612.0, "height": 792.0}],
      "highlights": [{"segment_id": 1, "page": 5, "x0": 72.1, "y0": 144.3, "x1": 410.2, "y1": 162.0}]
    }

## Interfaces and Dependencies

Add `pdfplumber` to project dependencies. `pdftoppm` from Poppler must be available on PATH to render page images.

Create the following functions in `src/quoded/ui/pdf_layout.py`:

    def build_layout(doc_id: str, root: Path | None = None, dpi: int = 144) -> dict: ...
    def load_layout(doc_id: str, root: Path | None = None) -> dict | None: ...

The UI server must add:

- `GET /api/docs/<doc-id>/layout`
- `GET /api/docs/<doc-id>/page/<n>.png`

Plan update (2026-02-05 10:18Z): Marked implementation steps complete, recorded the offline dependency fetch failure, and left validation pending.

Plan update (2026-02-05 10:28Z): Fixed page rendering by forcing pdftoppm to output per-page filenames without zero padding, and noted the root cause for missing early pages.

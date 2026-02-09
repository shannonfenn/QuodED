# UI Sketch

## Primary Views
- **Document view**: Rendered page images with clickable header highlights tied to segments and tasks.
- **Task view**: Status list for each segment (todo/in-progress/verified/failed).
- **Verification view**: Policy results and axiom reports per backend.
- **Orchestration view**: Active/previous agent runs with logs, artifacts, and user intervention controls.

## Key Interactions
- Open the Segments sidebar to jump from artifacts to page locations.
- Click a segment or task to scroll to the highlight and filter tasks.
- Inspect policy violations inline.
- Restart or fork an orchestration from a failed step.

## Running the UI
Use the local UI server to explore documents and orchestration runs:
```bash
uv run quoded ui --doc-id <doc-id>
```

The document view renders page images with Poppler (`pdftoppm`) and draws header-line highlights using `pdfplumber`.

Create runs for the orchestration view:
```bash
uv run quoded run create --doc-id <doc-id> --backend lean4 --label "First run"
uv run quoded run log <run-id> --kind step --message "Imported segments"
```

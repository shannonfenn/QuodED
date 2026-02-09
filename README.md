# QuodED

QuodED is a proof-verification pipeline that turns large documents into structured formalization tasks and enforces integrity policies across multiple proof assistants (Lean4, Rocq, Isabelle, Agda).

## Goals
- Ingest large PDFs and split them into formalization-sized chunks.
- Produce a reproducible verification record with explicit axiom reporting.
- Enforce integrity policies (no `sorry`/`admit`/unsafe escapes).
- Support agent-first workflows (CLI + skills) with a user-facing UI.

## Quickstart
```bash
uv sync

uv run quoded import-pdf "data/hodge-1/hodge_conjecture_pass17_complete (2).pdf" --doc-id hodge-1
uv run quoded segment hodge-1
uv run quoded plan hodge-1
```

## CLI
- `uv run quoded import-pdf <pdf> [--doc-id <id>]`
- `uv run quoded segment <doc-id>`
- `uv run quoded plan <doc-id>`
- `uv run quoded verify --backend <lean4|rocq|isabelle|agda> [--doc-id <id> | --path <dir>]`

## UI
Start the local UI (documents, tasks, verification, orchestration):
```bash
uv run quoded ui --doc-id <doc-id>
```

Note: The document view renders PDF pages via Poppler (`pdftoppm`) and uses `pdfplumber` for header highlights.

Create and log orchestration runs (for the UI view):
```bash
uv run quoded run create --doc-id <doc-id> --backend lean4 --label "First run"
uv run quoded run log <run-id> --kind step --message "Imported segments"
```

## Workspace Layout
```
.quoded/
  docs/<doc-id>/
    manifest.json
    pages.jsonl
    segments.json
    tasks.json
    formal/<backend>/
```

## Notes
- The current backend adapters implement integrity policy checks only. Compilation hooks and axiom reporting are the next milestone.

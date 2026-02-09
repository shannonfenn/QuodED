# Deliver runnable UI + orchestration view

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

After this change, we can start a local UI that reads the existing `.quoded` workspace and shows document, task, verification, and orchestration views in one place. We can create and update orchestration runs from the CLI and see them appear in the UI without any external services. The UI will be runnable via a single `uv run quoded ui --doc-id <id>` command and is intentionally lightweight so we can experiment quickly.

## Progress

- [x] (2026-02-05 17:35Z) Define an orchestration run data model, on-disk layout, and CLI commands to create/list/update runs and append events.
- [x] (2026-02-05 17:35Z) Add a lightweight UI server with JSON API endpoints for docs, segments, tasks, policy scans, and orchestration runs.
- [x] (2026-02-05 17:35Z) Implement a bold static UI (HTML/CSS/JS) for document, task, verification, and orchestration views.
- [x] (2026-02-05 17:35Z) Update README and STATUS with run instructions and milestone status.
- [ ] (2026-02-05 17:35Z) Validate by running the UI and creating a sample run that appears in the orchestration view.

## Surprises & Discoveries

- None yet.

## Decision Log

- Decision: Implement the UI as a lightweight local HTTP server serving static assets and JSON APIs, with no external framework.
  Rationale: Keeps the stack simple and fast to iterate while still providing a runnable UI for experimentation.
  Date/Author: 2026-02-05 / Codex

- Decision: Store orchestration runs under `.quoded/runs/<run-id>/run.json` with events in `.quoded/runs/<run-id>/events.jsonl`.
  Rationale: Keeps run metadata colocated with append-only event logs while staying consistent with the existing `.quoded` workspace layout.
  Date/Author: 2026-02-05 / Codex

## Outcomes & Retrospective

- Implemented the UI server, static assets, and run storage. Validation of the running UI and orchestration view is still pending.

## Context and Orientation

The current CLI lives in `src/quoded/cli.py` and exposes `import-pdf`, `segment`, `plan`, `verify`, `ui`, and `run` commands. The workspace is stored under `.quoded/docs/<doc-id>/` and includes `manifest.json`, `segments.json`, and `tasks.json` produced by the pipeline. Orchestration runs are stored under `.quoded/runs/<run-id>/` with `run.json` and `events.jsonl`. The UI server is implemented in `src/quoded/ui/server.py` and serves static assets from `src/quoded/ui/assets/`. The verification policy logic is implemented in `src/quoded/verify/policy.py` and can scan a backend-specific directory of formalization files.

An “orchestration run” in this plan means a record of a pipeline attempt (for a given document and backend), plus a log of events (steps, notes, errors). The UI must display these runs and their events so we can track agent activity.

## Plan of Work

We will add a small orchestration storage module under `src/quoded/orchestration/` that writes run metadata to `.quoded/runs/<run-id>/run.json` and appends events to `.quoded/runs/<run-id>/events.jsonl`. We will extend the CLI with a `run` subcommand group to create runs, list them, update status, and append events.

We will implement a UI server in `src/quoded/ui/server.py` that serves static assets from `src/quoded/ui/assets/` and exposes JSON endpoints for:

- Listing documents and loading `manifest.json`, `segments.json`, and `tasks.json`.
- Running or reading policy scans for the selected backend.
- Listing orchestration runs and reading run event logs.

We will implement static UI assets (`index.html`, `styles.css`, `app.js`) that render the four views (document, tasks, verification, orchestration). The UI will include a document selector, section navigation, and a refresh control. It will handle empty states gracefully.

Finally, we will update `README.md` with UI usage instructions and `STATUS.md` to reflect the milestone. We will validate by starting the UI server and creating a sample run that shows up in the orchestration view.

## Concrete Steps

Run all commands from the repository root: `/Users/shannon/dev/src/codex/QuodED`.

1) Add orchestration storage and CLI commands.

   - Create `src/quoded/orchestration/store.py` with run and event helpers.
   - Update `src/quoded/cli.py` with a `run` subcommand group.

2) Add the UI server and API endpoints.

   - Create `src/quoded/ui/server.py` to serve static assets and JSON APIs.
   - Add a `ui` command in `src/quoded/cli.py`.

3) Add UI assets.

   - Create `src/quoded/ui/assets/index.html`, `styles.css`, and `app.js`.
   - Implement document, task, verification, and orchestration views.

4) Update docs.

   - Update `README.md` with `quoded ui` instructions.
   - Update `STATUS.md` to record the milestone.

5) Validate end-to-end.

   - Run `uv run quoded ui --doc-id hodge-1` and open the URL it prints.
   - Run `uv run quoded run create --doc-id hodge-1 --backend lean4 --label "First run"` and `uv run quoded run log <run-id> --kind step --message "Imported segments"`.
   - Verify the run appears in the UI orchestration view.

## Validation and Acceptance

The change is accepted when:

- Running `uv run quoded ui --doc-id hodge-1` prints a local URL and serves a UI that loads the manifest, segments, and tasks for `hodge-1`.
- The UI shows a verification section that can display policy scan results for at least one backend (even if empty).
- Creating a run and adding an event via the CLI makes that run appear in the orchestration view with its event log.

## Idempotence and Recovery

All commands are safe to re-run. Creating runs always creates a new `run-id` directory. If the UI server is running, it can be stopped with Ctrl+C and restarted without side effects. If a run is created accidentally, deleting `.quoded/runs/<run-id>` removes it cleanly.

## Artifacts and Notes

Expected sample output when starting the UI server:

    $ uv run quoded ui --doc-id hodge-1
    UI running at http://127.0.0.1:8000 (doc: hodge-1)

Expected sample output when creating a run:

    $ uv run quoded run create --doc-id hodge-1 --backend lean4 --label "First run"
    run_id: run-20260205-173800-ab12cd34

## Interfaces and Dependencies

Use only the existing Python dependencies (Typer, Rich, Pydantic, PyPDF). No frontend frameworks. The new modules and functions must exist with these names:

In `src/quoded/orchestration/store.py`:

    @dataclass(frozen=True)
    class RunRecord:
        run_id: str
        doc_id: str
        backend: str
        status: str
        created_at: str
        updated_at: str
        label: str | None
        notes: str | None

    @dataclass(frozen=True)
    class RunEvent:
        event_id: str
        run_id: str
        created_at: str
        kind: str
        message: str
        meta: dict

    def create_run(doc_id: str, backend: str, label: str | None = None, status: str = "running", root: Path | None = None) -> RunRecord: ...
    def list_runs(root: Path | None = None) -> list[RunRecord]: ...
    def get_run(run_id: str, root: Path | None = None) -> RunRecord: ...
    def update_run_status(run_id: str, status: str, root: Path | None = None) -> RunRecord: ...
    def append_event(run_id: str, kind: str, message: str, meta: dict | None = None, root: Path | None = None) -> RunEvent: ...
    def list_events(run_id: str, root: Path | None = None) -> list[RunEvent]: ...

In `src/quoded/ui/server.py`:

    def serve_ui(host: str, port: int, doc_id: str | None = None) -> None: ...

The CLI must expose:

- `quoded ui --doc-id <id> --host <host> --port <port>`
- `quoded run create --doc-id <id> --backend <name> [--label <label>] [--status <status>]`
- `quoded run list`
- `quoded run status <run-id> --status <status>`
- `quoded run log <run-id> --kind <kind> --message <message>`

Plan update (2026-02-05 17:50Z): Marked completed implementation steps, recorded the run storage decision, and refreshed context/outcomes to reflect the UI and orchestration code now in the repo. Validation remains pending.

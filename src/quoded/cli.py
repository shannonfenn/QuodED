from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print

from quoded.ingest.pdf import import_pdf
from quoded.orchestration.store import append_event, create_run, list_runs, update_run_status
from quoded.paths import doc_root
from quoded.plan.task_planner import build_tasks
from quoded.segment.segmenter import segment_pages
from quoded.storage import read_json
from quoded.utils import normalize_path
from quoded.verify.runner import run_policy_check

app = typer.Typer(add_completion=False, no_args_is_help=True)
runs_app = typer.Typer(add_completion=False, no_args_is_help=True, help="Manage orchestration runs.")


@app.command("import-pdf")
def import_pdf_cmd(
    pdf_path: str = typer.Argument(..., help="Path to PDF."),
    doc_id: str | None = typer.Option(None, help="Optional document id."),
):
    """Import a PDF into the QuodED workspace."""
    manifest = import_pdf(Path(pdf_path), doc_id=doc_id)
    print("[bold green]Imported[/bold green]", manifest.source_path)
    print(f"doc_id: {manifest.doc_id}")
    print(f"pages: {manifest.page_count}")
    print(f"workspace: {doc_root(manifest.doc_id)}")


@app.command("segment")
def segment_cmd(
    doc_id: str = typer.Argument(..., help="Document id."),
):
    """Segment an imported document into theorem/lemma chunks."""
    root = doc_root(doc_id)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise typer.BadParameter(f"Manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    segments = segment_pages(Path(manifest["pages_path"]), Path(manifest["segments_path"]))
    print(f"[bold green]Segments:[/bold green] {len(segments)}")
    if segments:
        preview = segments[:5]
        for segment in preview:
            print(f"- {segment.kind} {segment.segment_id}: {segment.title}")


@app.command("plan")
def plan_cmd(
    doc_id: str = typer.Argument(..., help="Document id."),
):
    """Create a formalization task list from segments."""
    root = doc_root(doc_id)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise typer.BadParameter(f"Manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    tasks = build_tasks(Path(manifest["segments_path"]), Path(manifest["tasks_path"]))
    print(f"[bold green]Tasks:[/bold green] {len(tasks)}")


@app.command("verify")
def verify_cmd(
    backend: str = typer.Option(..., help="Backend name: lean4, rocq, isabelle, agda."),
    doc_id: str | None = typer.Option(None, help="Document id for default path."),
    path: str | None = typer.Option(None, help="Override formalization path."),
):
    """Run integrity policy checks on formalization sources."""
    if path:
        formal_root = normalize_path(path)
    elif doc_id:
        formal_root = doc_root(doc_id) / "formal" / backend
    else:
        raise typer.BadParameter("Provide --doc-id or --path.")

    result = run_policy_check(backend, formal_root)
    if result.note:
        print(f"[bold red]{result.note}[/bold red]")
        raise typer.Exit(code=1)

    if result.ok:
        print(f"[bold green]Policy check passed[/bold green] for {backend}.")
        return

    print(f"[bold red]Policy violations[/bold red] ({len(result.violations)})")
    for violation in result.violations:
        print(f"- {violation['file']}:{violation['line']} {violation['rule']} :: {violation['text']}")
    raise typer.Exit(code=1)


@app.command("ui")
def ui_cmd(
    doc_id: str | None = typer.Option(None, help="Document id to preselect."),
    host: str = typer.Option("127.0.0.1", help="Host to bind the UI server."),
    port: int = typer.Option(8000, help="Port for the UI server."),
):
    """Start the local UI server for documents and orchestration."""
    from quoded.ui.server import serve_ui

    serve_ui(host, port, doc_id=doc_id)


@runs_app.command("create")
def run_create_cmd(
    doc_id: str = typer.Option(..., help="Document id."),
    backend: str = typer.Option(..., help="Backend name."),
    label: str | None = typer.Option(None, help="Optional label."),
    status: str = typer.Option("running", help="Initial status."),
):
    """Create a new orchestration run."""
    record = create_run(doc_id=doc_id, backend=backend, label=label, status=status)
    print(f"run_id: {record.run_id}")


@runs_app.command("list")
def run_list_cmd():
    """List orchestration runs."""
    runs = list_runs()
    if not runs:
        print("[bold yellow]No runs found[/bold yellow]")
        return
    for run in runs:
        print(f"{run.run_id} {run.doc_id} {run.backend} {run.status} {run.updated_at}")


@runs_app.command("status")
def run_status_cmd(
    run_id: str = typer.Argument(..., help="Run id."),
    status: str = typer.Option(..., help="New status."),
):
    """Update a run status."""
    record = update_run_status(run_id, status)
    print(f"updated {record.run_id} -> {record.status}")


@runs_app.command("log")
def run_log_cmd(
    run_id: str = typer.Argument(..., help="Run id."),
    kind: str = typer.Option("note", help="Event kind."),
    message: str = typer.Option(..., help="Event message."),
    meta: str | None = typer.Option(None, help="Optional JSON metadata."),
):
    """Append an event to a run."""
    payload = None
    if meta:
        try:
            payload = json.loads(meta)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"Invalid JSON for --meta: {exc}") from exc
    event = append_event(run_id, kind=kind, message=message, meta=payload)
    print(f"event_id: {event.event_id}")


app.add_typer(runs_app, name="run")

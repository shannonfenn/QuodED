from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
from urllib.parse import parse_qs, urlparse

from quoded.orchestration.store import get_run, list_events, list_runs
from quoded.paths import doc_root, docs_root, repo_root
from quoded.storage import read_json
from quoded.ui.pdf_layout import build_layout, load_layout
from quoded.verify.policy import POLICIES, scan_policy


ASSETS_DIR = Path(__file__).parent / "assets"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: object) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _text_response(handler: BaseHTTPRequestHandler, status: int, text: str) -> None:
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _serve_file(handler: BaseHTTPRequestHandler, path: Path) -> None:
    if not path.exists():
        _text_response(handler, 404, "Not found")
        return
    suffix = path.suffix.lower()
    content_type = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")
    data = path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def _serve_pdf(handler: BaseHTTPRequestHandler, path: Path) -> None:
    if not path.exists():
        _text_response(handler, 404, "PDF not found")
        return
    data = path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/pdf")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def _list_docs(root: Path) -> list[str]:
    base = docs_root(root)
    if not base.exists():
        return []
    return sorted([path.name for path in base.iterdir() if path.is_dir()])


def _load_json(path: Path) -> object | None:
    if not path.exists():
        return None
    return read_json(path)


def _load_manifest(doc_id: str, root: Path) -> dict | None:
    payload = _load_json(doc_root(doc_id, root) / "manifest.json")
    if isinstance(payload, dict):
        return payload
    return None


def _layout_or_build(doc_id: str, root: Path) -> dict | None:
    layout = load_layout(doc_id, root)
    if layout:
        return layout
    try:
        return build_layout(doc_id, root=root)
    except Exception as exc:
        return {"note": f"layout build failed: {exc}"}


def _render_page_image(doc_id: str, page_num: int, root: Path, dpi: int) -> Path | None:
    pages_dir = doc_root(doc_id, root) / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    target = pages_dir / f"page-{page_num}.png"
    if target.exists():
        return target

    manifest = _load_manifest(doc_id, root)
    if not manifest:
        return None
    source_path = Path(str(manifest.get("source_path", "")))
    if not source_path.exists():
        return None
    if shutil.which("pdftoppm") is None:
        return None

    prefix = pages_dir / f"page-{page_num}"
    command = [
        "pdftoppm",
        "-png",
        "-r",
        str(dpi),
        "-f",
        str(page_num),
        "-l",
        str(page_num),
        "-singlefile",
        str(source_path),
        str(prefix),
    ]
    subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if target.exists():
        return target
    for width in (2, 3, 4):
        candidate = pages_dir / f"page-{page_num:0{width}d}.png"
        if candidate.exists():
            candidate.rename(target)
            return target
    return None


def _policy_payload(doc_id: str, backend: str, root: Path) -> dict:
    if backend not in POLICIES:
        return {
            "backend": backend,
            "ok": False,
            "violations": [],
            "note": f"Unknown backend: {backend}",
            "scanned_at": _now_iso(),
        }
    formal_root = doc_root(doc_id, root) / "formal" / backend
    if not formal_root.exists():
        return {
            "backend": backend,
            "ok": False,
            "violations": [],
            "note": f"Formalization path not found: {formal_root}",
            "scanned_at": _now_iso(),
            "root": str(formal_root),
            "policy": POLICIES[backend],
        }
    violations = scan_policy(formal_root, backend)
    return {
        "backend": backend,
        "ok": len(violations) == 0,
        "violations": [violation.__dict__ for violation in violations],
        "note": None,
        "scanned_at": _now_iso(),
        "root": str(formal_root),
        "policy": POLICIES[backend],
    }


class UIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, root: Path, default_doc_id: str | None, **kwargs):
        self._root = root
        self._default_doc_id = default_doc_id
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api(parsed)
        else:
            self._handle_static(parsed)

    def _handle_static(self, parsed) -> None:
        path = parsed.path
        if path == "/":
            path = "/index.html"
        if path.startswith("/assets/"):
            asset_path = ASSETS_DIR / path.removeprefix("/assets/")
        else:
            asset_path = ASSETS_DIR / path.lstrip("/")
        _serve_file(self, asset_path)

    def _handle_api(self, parsed) -> None:
        parts = parsed.path.strip("/").split("/")
        query = parse_qs(parsed.query)
        if parts == ["api", "health"]:
            _json_response(self, 200, {"ok": True, "time": _now_iso()})
            return
        if parts == ["api", "docs"]:
            docs = _list_docs(self._root)
            _json_response(self, 200, {"docs": docs, "default": self._default_doc_id})
            return
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "docs":
            doc_id = parts[2]
            section = parts[3] if len(parts) >= 4 else None
            if section == "manifest":
                payload = _load_manifest(doc_id, self._root)
                if payload is None:
                    _json_response(self, 404, {"note": "manifest not found"})
                    return
                _json_response(self, 200, payload)
                return
            if section == "segments":
                payload = _load_json(doc_root(doc_id, self._root) / "segments.json")
                if payload is None:
                    _json_response(self, 404, {"note": "segments not found"})
                    return
                _json_response(self, 200, payload)
                return
            if section == "tasks":
                payload = _load_json(doc_root(doc_id, self._root) / "tasks.json")
                if payload is None:
                    _json_response(self, 404, {"note": "tasks not found"})
                    return
                _json_response(self, 200, payload)
                return
            if section == "layout":
                payload = _layout_or_build(doc_id, self._root)
                if payload is None:
                    _json_response(self, 404, {"note": "layout not found"})
                    return
                _json_response(self, 200, payload)
                return
            if section == "page" and len(parts) >= 5:
                page_token = parts[4]
                if page_token.endswith(".png"):
                    page_token = page_token[:-4]
                try:
                    page_num = int(page_token)
                except ValueError:
                    _json_response(self, 400, {"note": "invalid page number"})
                    return
                layout = _layout_or_build(doc_id, self._root) or {}
                dpi = int(layout.get("dpi", 144)) if isinstance(layout, dict) else 144
                image_path = _render_page_image(doc_id, page_num, self._root, dpi)
                if not image_path:
                    _json_response(self, 404, {"note": "page render failed"})
                    return
                _serve_file(self, image_path)
                return
            if section == "pdf":
                manifest = _load_manifest(doc_id, self._root)
                if not manifest:
                    _json_response(self, 404, {"note": "manifest not found"})
                    return
                source_path = Path(manifest.get("source_path", ""))
                if not source_path.exists():
                    _json_response(
                        self,
                        404,
                        {"note": "pdf source not found", "path": str(source_path)},
                    )
                    return
                _serve_pdf(self, source_path)
                return
            if section == "policy" and len(parts) >= 5:
                backend = parts[4]
                payload = _policy_payload(doc_id, backend, self._root)
                _json_response(self, 200, payload)
                return
        if parts == ["api", "runs"]:
            runs = [asdict(run) for run in list_runs(self._root)]
            _json_response(self, 200, {"runs": runs})
            return
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "runs":
            run_id = parts[2]
            if len(parts) == 3:
                try:
                    run = get_run(run_id, self._root)
                except FileNotFoundError:
                    _json_response(self, 404, {"note": "run not found"})
                    return
                _json_response(self, 200, asdict(run))
                return
            if len(parts) == 4 and parts[3] == "events":
                events = [asdict(event) for event in list_events(run_id, self._root)]
                _json_response(self, 200, {"events": events})
                return
        _json_response(self, 404, {"note": "unknown endpoint", "path": parsed.path, "query": query})


def serve_ui(host: str, port: int, doc_id: str | None = None) -> None:
    root = repo_root()

    def handler(*args, **kwargs):
        UIHandler(*args, root=root, default_doc_id=doc_id, **kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(f"UI running at http://{host}:{port} (doc: {doc_id or 'auto'})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

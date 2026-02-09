# Lessons Learned / Insights

Append-only: add new entries at the end. Do not edit or reorder prior entries unless a conflict arises. If a conflict arises, ask the user to clarify.

## 2026-02-05

- The sandbox can block `uv` cache access; set `[tool.uv].cache-dir = ".uv-cache"` in `pyproject.toml` to keep `uv` working reliably inside the repo.
- Poppler (`pdftoppm`) is required for visual QA of PDF segmentation; text extraction alone misses layout errors.
- Naive header detection produced false positives (e.g., “theorem of Cattani–Deligne–Kaplan” in prose). Tightening header patterns to require labels reduces false positives.
- Randomized page sampling increases confidence in segmentation quality and should be part of the QA routine.

## 2026-02-06

- Poppler page output naming can be zero-padded (`page-01.png`) depending on invocation; cache and serving logic must normalize filenames to a canonical page key to avoid partial render failures on early pages.
- Cache invalidation remains a recurring risk in the PDF rendering path; cache schema/version metadata should be included so stale naming or geometry artifacts can be detected and rebuilt automatically.

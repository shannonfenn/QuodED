# Project Status

Last updated: 2026-02-06

## Completed

- Scaffolded the QuodED CLI (`import-pdf`, `segment`, `plan`, `verify`) and core pipeline modules.
- Imported and segmented the hodge-1 PDF; generated tasks from segments.
- Improved segmentation to reduce false positives and include `Remark`, `Assumption`, and `Step` kinds.
- Performed randomized visual QA on PDF pages using Poppler.
- Added a local UI server with document/task/verification/orchestration views plus CLI-managed run logs.
- Embedded PDF viewing in the UI with segment/task-linked navigation and highlighting.
- Added rendered page images with header-line highlights to link segments directly to the paper.
- Added a specification-first `fresh start` scaffold with isolated outer-run directories and run templates.

## In Progress

- None explicitly tracked at the project level.

## Postponed

- Extend segmentation to capture `Statement`, `Proof`, `Notation`, `Section`, and `Part` headings and decide how they affect task planning.

## Next

- Implement backend compilation hooks and axiom reporting for Lean4, Rocq, Isabelle, and Agda.
- Build the orchestration view in the UI and define the data model for agent runs.
- Define and implement the integrity guard policy enforcement per backend.

# Improve PDF Segmentation Coverage and QA

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `/.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

We need higher-confidence segmentation of large proof PDFs so the task list is trustworthy for formalization. After this change, running `uv run quoded segment <doc-id>` will capture additional structural headings (Statement, Proof, Notation, Section, Part) without false positives, and we will validate the result by randomly sampling rendered pages and confirming the segments align to the page content.

## Progress

- [ ] (2026-02-05 08:26Z) Extend segmentation to capture Statement/Proof/Notation/Section/Part headings and record them in the output.
- [ ] (2026-02-05 08:26Z) Decide how Section/Part segments affect task planning (task vs. metadata) and update the planner accordingly.
- [ ] (2026-02-05 08:26Z) Re-run segmentation on `hodge-1` and refresh tasks.
- [ ] (2026-02-05 08:26Z) Perform randomized visual QA on at least 5 pages and record the outcomes.
- [ ] (2026-02-05 08:26Z) Update documentation to reflect new segment kinds and QA expectations.

## Surprises & Discoveries

- None yet.

## Decision Log

- Decision: Defer additional segment kinds (Statement/Proof/Notation/Section/Part) to this plan instead of adding them immediately.
  Rationale: Keep the current milestone focused and avoid unverified heuristics before defining QA and acceptance criteria.
  Date/Author: 2026-02-05 / Codex

## Outcomes & Retrospective

- Not started.

## Context and Orientation

Segmentation is implemented in `src/quoded/segment/segmenter.py` and writes output to `.quoded/docs/<doc-id>/segments.json`. Task creation is handled by `src/quoded/plan/task_planner.py`, which currently creates one task per segment. The PDF import pipeline lives in `src/quoded/ingest/pdf.py`. The CLI entry point is `src/quoded/cli.py` and should be run via `uv run` to ensure the project environment is correct.

Segment kinds currently recognized are Theorem, Lemma, Definition, Corollary, Proposition, Claim, Remark, Assumption, and Step. We observed that Statement/Proof/Notation/Section/Part headings appear in the PDF but are not captured. We also require randomized visual verification using Poppler (`pdftoppm`) to reduce false positives.

## Plan of Work

Update the segmenter to recognize Statement, Proof, Notation, Section, and Part headers with strict label patterns that minimize false positives. Decide whether Section/Part should become tasks or serve as metadata that groups later tasks; implement the chosen behavior in `src/quoded/plan/task_planner.py`. Re-run segmentation and task planning on `hodge-1`. Validate by rendering at least five random pages via Poppler, compare the headings on those pages to the segments produced, and record the results in this plan under `Surprises & Discoveries` or `Outcomes & Retrospective`. Update README or related docs to describe the new segment kinds and the QA process.

## Concrete Steps

Run all commands from the repository root.

1) Sync the environment:

    uv sync

2) Re-run segmentation and task planning:

    uv run quoded segment hodge-1
    uv run quoded plan hodge-1

3) Render randomized pages for QA (replace the page list with randomly selected pages each run):

    mkdir -p tmp/pdfs/hodge-1-rand
    pdftoppm -png -f <page> -l <page> "data/hodge-1/hodge_conjecture_pass17_complete (2).pdf" tmp/pdfs/hodge-1-rand/page-<page>

Record which pages were checked and the observed alignment between headings and segments.

## Validation and Acceptance

The change is accepted when:

- `uv run quoded segment hodge-1` produces segments that include Statement/Proof/Notation/Section/Part where those headings appear in the PDF.
- No new false positives are introduced on the randomized QA sample (headings in PDF correspond to segments, and prose lines are not misclassified).
- The QA sample results are recorded in this plan with page numbers and short notes about alignment.

## Idempotence and Recovery

The segmentation and planning commands are safe to re-run; they overwrite `.quoded/docs/<doc-id>/segments.json` and `tasks.json`. If a segmentation change causes regressions, restore the prior `segmenter.py` and re-run the pipeline to return to the previous output.

## Artifacts and Notes

Keep rendered QA images in `tmp/pdfs/hodge-1-rand/` and clean them up after review if disk usage becomes an issue.

## Interfaces and Dependencies

- Poppler `pdftoppm` must be available on PATH for visual QA.
- `uv` is the Python toolchain and should be used for all project commands.
- `src/quoded/segment/segmenter.py` must expose the updated segmentation behavior.
- `src/quoded/plan/task_planner.py` must reflect the chosen task/metadata handling for Section/Part segments.

Note: This ExecPlan was created to capture deferred segmentation improvements and QA requirements.

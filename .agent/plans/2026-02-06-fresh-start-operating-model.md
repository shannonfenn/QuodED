# Establish Spec-First Operating Model and Fresh Start Scaffold

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

We need to shift from code-first iteration to specification-first experimentation. After this change, the repository will contain a `fresh start` workspace that defines loop terminology, swarm operating rules, and isolated outer-run folders so future experimentation starts from a clean, repeatable structure. This lets us run fast requirement loops while preserving evidence and reducing ambiguity about lifecycle decisions.

## Progress

- [x] (2026-02-06 10:45Z) Create this ExecPlan for the operating-model/fresh-start initiative.
- [x] (2026-02-06 10:45Z) Finalize loop terminology and decision rules (re-entry, transfer policy, default discard behavior).
- [x] (2026-02-06 10:45Z) Create `fresh start` directory structure and seed it with initial specification/workflow docs.
- [x] (2026-02-06 10:45Z) Update project-level logs (PRD/LESSONS/STATUS) only where needed and summarize the resulting operating model.

## Surprises & Discoveries

- The first outer run needed additional baseline files (`SPEC.md`, `SWARM_LOG.md`, `EVALUATION.md`, `LESSONS.md`, `TRANSFER.md`) at creation time to avoid setup friction.
  Evidence: Added these files directly under `fresh start/outer-runs/OR-0001-initial/` instead of leaving only a placeholder README.

## Decision Log

- Decision: Build a new isolated scaffold in `fresh start` instead of refactoring in-place.
  Rationale: The user explicitly wants a sanitized reset workspace while retaining this repo as a reference history.
  Date/Author: 2026-02-06 / Codex

- Decision: Lock canonical terms as `Outer Run (OR)` and `Swarm Session (SS)` and encode user-owned transfer/re-entry approvals.
  Rationale: Removes ambiguity between macro and micro loops and enforces explicit decision ownership.
  Date/Author: 2026-02-06 / Codex

## Outcomes & Retrospective

- Completed: `fresh start` scaffold, operating model docs, templates, and seeded first outer run artifacts.
- Completed: main `PRD.md` updated with operating model lock decisions.
- Completed: `STATUS.md` updated with fresh-start milestone.
- Remaining: start the first `SS` inside `OR-0001-initial` and test the loop in practice.

## Context and Orientation

This repository already contains active prototype code, multiple design changes, and append-only logs (`PRD.md`, `LESSONS.md`, `STATUS.md`). The user now wants to operate in a specification-first mode where outer loops drive swarm implementation/evaluation and each outer loop is isolated in a fresh subdirectory. The `fresh start` folder will become that baseline environment.

The user also clarified key operating constraints:
- Inner swarm loops can be re-initiated after termination if continuing current code is chosen.
- Each outer loop should run in its own subdirectory.
- Code transfer between outer loops is explicit user choice; default is no transfer.
- Terminology must be fixed now to avoid later confusion.

## Plan of Work

First, define canonical terms for program lifecycle, outer-loop runs, inner swarm runs, and restart/re-entry semantics. Include explicit state transitions and ownership of decisions (especially code transfer).

Second, create a `fresh start` directory with a small but complete operating kit: a fresh PRD, lessons log, status tracker, workflow/terminology doc, and templates for outer-run spec, swarm brief, and evaluation report. Also create an `outer-runs/` directory with naming conventions and a placeholder for the first run.

Third, seed the fresh PRD with distilled current learnings from this repo (mapping cardinality model, editable authoritative regions/units, suggestor provenance requirement, cache hygiene risk) so the next project starts with the strongest validated insights.

Finally, update this plan progress and summarize what to use next.

## Concrete Steps

Run all commands from `/Users/shannon/dev/src/codex/QuodED`.

1) Write and maintain this ExecPlan in `.agent/plans/2026-02-06-fresh-start-operating-model.md`.

2) Create the directory scaffold:

    mkdir -p "fresh start"/templates
    mkdir -p "fresh start"/outer-runs

3) Create seed docs in `fresh start`:

- `README.md`
- `PRD.md`
- `LESSONS.md`
- `STATUS.md`
- `OPERATING_MODEL.md`
- `templates/OUTER_RUN_SPEC.md`
- `templates/SWARM_BRIEF.md`
- `templates/EVALUATION_REPORT.md`

4) Create initial outer-run placeholder:

- `outer-runs/OR-0001-initial/README.md`

5) Validate by listing the new tree and ensuring docs are present and coherent.

## Validation and Acceptance

Accepted when:
- `fresh start` exists with the documented structure and templates.
- Terminology and governance rules explicitly encode re-entry and user-controlled transfer decisions.
- The fresh PRD contains distilled lessons from current experiments so a new project can start without losing insight.

## Idempotence and Recovery

All created files are additive and safe to re-run. Re-running scaffold commands should not destroy data. If any doc content needs revision, append new dated entries rather than rewriting history in append-only logs.

## Artifacts and Notes

Primary artifacts are the new markdown files in `fresh start/` and this plan.

## Interfaces and Dependencies

No new runtime dependencies are required. This is a documentation and workflow-structure change.

Plan update (2026-02-06 10:55Z): Marked all planned steps complete, logged the baseline-file discovery, and captured final outcomes to make this plan restartable without additional context.

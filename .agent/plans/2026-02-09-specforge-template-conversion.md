# Consolidate PRD and Convert Fresh Start into Generic Specforge Template

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

We need a reusable repository template for requirements-first development loops. After this change, the root `PRD.md` will be consolidated from the current fresh-start product PRD, and `fresh start/` will become a generic, portable template that any team can copy into a new repo. The template will include explicit guidance for both Codex and Claude Code with agent teams.

## Progress

- [x] (2026-02-09 00:00Z) Create this ExecPlan.
- [x] (2026-02-09 00:00Z) Consolidate root `PRD.md` by replacing it with the fresh-start product-focused PRD content.
- [x] (2026-02-09 00:00Z) Genericize `fresh start/` so product-specific content is removed and template content is neutral.
- [x] (2026-02-09 00:00Z) Add Codex and Claude Code (agent team) usage guidance in template docs.
- [x] (2026-02-09 00:00Z) Validate final structure and summarize handoff.

## Surprises & Discoveries

- The template needed an explicit runbook file for agent-launch prompts rather than embedding long prompts in `AGENTS.md`.
  Evidence: Added `.specforge/AGENT_RUNBOOK.md` and kept `AGENTS.md` minimal and pointer-based.

## Decision Log

- Decision: Keep `.specforge` as the operating-model directory and keep root docs product-only.
  Rationale: Aligns with the user’s requirement to separate “what to build” from “how to run loops”.
  Date/Author: 2026-02-09 / Codex

## Outcomes & Retrospective

- Completed: root PRD consolidation with operating-model decisions removed.
- Completed: fresh-start template genericized for arbitrary projects.
- Completed: Codex and Claude Code agent-team guidance added in `.specforge/AGENT_RUNBOOK.md`.
- Completed: portability checks confirmed no stale QuodED-specific references in template docs.

Plan update (2026-02-09 00:15Z): Marked all steps complete and recorded the runbook separation decision for maintainability.

## Context and Orientation

`fresh start/` currently contains a good structural baseline, but includes project-specific product content and references that reduce portability as a cross-project template. The root `PRD.md` in this repository still mixes product and operating-model decisions from prior experiments.

The target state is:
- Root `PRD.md`: consolidated product-only decisions.
- `fresh start/`: generic template for arbitrary projects.
- `.specforge/`: contains all operating-model machinery.
- Guidance for using the template with both Codex and Claude Code agent teams.

## Plan of Work

First, replace root `PRD.md` with consolidated product decisions from `fresh start/PRD.md`, expanded only with relevant product decisions previously present in root PRD.

Second, rewrite `fresh start/PRD.md` and `fresh start/LESSONS.md` as neutral templates (placeholders, no QuodED-specific domain assumptions).

Third, add explicit operator guidance for Codex and Claude Code swarms, likely in `fresh start/README.md` and a dedicated `.specforge/AGENT_RUNBOOK.md`.

Fourth, ensure RL-0001 operating-model artifacts remain as a generic validation run and that all paths/references are relative and portable.

## Concrete Steps

Run commands from `/Users/shannon/dev/src/codex/QuodED`.

1) Update root `PRD.md` with consolidated product-only content.
2) Rewrite template docs under `fresh start/` for generic use.
3) Add Codex and Claude runbook guidance.
4) Validate with `find` and `rg` scans for stale project-specific references.

## Validation and Acceptance

Accepted when:
- Root `PRD.md` contains consolidated product decisions only.
- `fresh start/` can be copied to a new repo and still make sense.
- Operating-model details live under `fresh start/.specforge/`.
- Template docs include clear usage guidance for Codex and Claude Code agent-team workflows.

## Idempotence and Recovery

All changes are documentation-only and can be reapplied safely. If any wording conflict appears, append clarifications in relevant template docs.

## Artifacts and Notes

Primary artifacts are updated markdown files in root and `fresh start/`.

## Interfaces and Dependencies

No runtime dependencies are required for this change.

# Finalize Specforge Template as Portable Control Plane

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

The template should be repository-portable, user-facing from a single README, and free of temporary validation artifacts. After this change, the template will keep operating-model internals under `.specforge`, remove RL-0001/bootstrap leftovers, and define a per-RL implementation workspace model so generated code is isolated from root control-plane docs.

## Progress

- [x] (2026-02-09 00:25Z) Create this ExecPlan.
- [x] (2026-02-09 01:05Z) Move user-facing runbook content into `fresh start/README.md` and simplify `AGENTS.md`.
- [x] (2026-02-09 01:08Z) Remove temporary RL-0001/bootstrap artifacts from the template.
- [x] (2026-02-09 01:11Z) Add explicit RL workspace conventions for where implementation code lives and how to extract successful outputs.
- [x] (2026-02-09 01:14Z) Validate final template structure and references.

## Surprises & Discoveries

- Observation: The original templates did not include dedicated files for RL-local `LESSONS.md`, `TRANSFER.md`, and `IMPLEMENTATION_LOG.md`, which made bootstrap commands ambiguous.
  Evidence: README bootstrap commands had to reuse an unrelated evaluation template before dedicated templates were added.

## Decision Log

- Decision: Keep root as control plane only (`README.md`, `AGENTS.md`, `PRD.md`, `LESSONS.md`) and require implementation code under RL-local workspace directories.
  Rationale: Preserves isolation between loops and prevents accidental contamination of template root.
  Date/Author: 2026-02-09 / Codex
- Decision: Remove seeded RL and bootstrap artifacts from the shipping template.
  Rationale: They are test-run residue and should not bias or constrain first use in a new repository.
  Date/Author: 2026-02-09 / Codex
- Decision: Move Codex/Claude runbook prompts into root README and keep `.specforge` primarily agent-control context.
  Rationale: End users should only need one entrypoint document.
  Date/Author: 2026-02-09 / Codex

## Outcomes & Retrospective

- Template is now clean and portable: no seeded RL, no bootstrap file, no separate runbook dependency.
- README is now the primary operator guide and includes Codex and Claude kickoff prompts.
- RL-local workspace conventions are explicit in both user and agent docs, including subagent context boundaries.

## Context and Orientation

Current template state still includes temporary validation artifacts (`RL-0001` and bootstrap file) and places agent invocation guidance in a separate runbook file under `.specforge`. The user requested a simpler UX where README is sufficient for operators, while `.specforge` remains operational context for agents and loop mechanics.

## Plan of Work

First, fold the Codex/Claude invocation guidance into README and remove separate runbook dependency from AGENTS instructions.

Second, remove temporary RL/bootstrap artifacts and leave `.specforge/requirements-loops/` as a clean directory (with a keep file).

Third, update `.specforge/INSTRUCTIONS.md` and templates so each RL has an explicit `workspace/` directory for implementation outputs and optional `artifacts/` for evidence.

Finally, verify that no stale references to removed files remain.

## Concrete Steps

Run from `/Users/shannon/dev/src/codex/QuodED`.

1) Update `fresh start/README.md` with full user-facing run instructions and prompts.
2) Simplify `fresh start/AGENTS.md` to point only to `.specforge/INSTRUCTIONS.md`.
3) Remove `.specforge/AGENT_RUNBOOK.md`, `.specforge/BOOTSTRAP.md`, and `.specforge/requirements-loops/RL-0001-operating-model/`.
4) Add workspace conventions in `.specforge/INSTRUCTIONS.md` and template files.
5) Validate with `find`/`rg`.

## Validation and Acceptance

Accepted when:
- README alone is sufficient for user setup and first RL launch with Codex or Claude.
- `.specforge` contains operating-model context only.
- No temporary test-loop/bootstrap artifacts remain.
- RL workspace location and extraction workflow are explicitly documented.

## Idempotence and Recovery

All changes are documentation/template structure edits. Deletions remove only temporary template artifacts.

## Artifacts and Notes

Primary artifacts are updated docs under `fresh start/`.

## Interfaces and Dependencies

No runtime dependencies required.

Revision note (2026-02-09): Marked all milestones complete after template cleanup, added decisions and discoveries, and recorded final outcomes to keep this plan restart-safe.

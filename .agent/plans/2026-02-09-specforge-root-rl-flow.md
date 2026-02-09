# Align Specforge Template to Root-Agent Orchestrated RL Flow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan is maintained according to `.agent/PLANS.md` and must remain self-contained.

## Purpose / Big Picture

Specforge should operate with a clear separation of responsibilities: the user collaborates with a root orchestration agent in repository root, and RL execution happens in loop-local contexts via a dedicated RL agent (single agent or team). After this change, users will no longer be instructed to manually create RL folders. Instead, the root agent will scaffold RLs through a script, then hand off a concise run brief for RL execution.

## Progress

- [x] (2026-02-09 01:28Z) Create this ExecPlan.
- [x] (2026-02-09 01:44Z) Rewrite `fresh start/README.md` around the intended user flow and role ownership.
- [x] (2026-02-09 01:48Z) Add RL initialization script under `.specforge/scripts/` and wire it into instructions.
- [x] (2026-02-09 01:52Z) Update `.specforge/INSTRUCTIONS.md` and template files for root-agent handoff and RL-agent closure behavior.
- [x] (2026-02-09 01:56Z) Validate template consistency and stale-reference cleanup.

## Surprises & Discoveries

- Observation: Running setup/copy/check commands in parallel introduced a race during validation.
  Evidence: RL bootstrap command failed once because `/tmp/specforge-template-check` was not ready; sequential rerun succeeded.

## Decision Log

- Decision: Keep RL scaffolding agent-driven through a script invoked by the root agent, not user-driven manual file creation.
  Rationale: This enforces the control model, reduces user cognitive load, and avoids drift in RL artifact structure.
  Date/Author: 2026-02-09 / Codex
- Decision: Add `RUN_BRIEF.md` as a required RL artifact created at scaffold time.
  Rationale: Gives root agent a stable, low-context handoff contract to RL agent sessions.
  Date/Author: 2026-02-09 / Codex
- Decision: Add `.specforge/requirements-loops/INDEX.md` and auto-append entries from `init_rl.sh`.
  Rationale: Maintains a lightweight source of truth for RL state without reintroducing root-level status clutter.
  Date/Author: 2026-02-09 / Codex
- Decision: Provide separate prompt packs for Codex and Claude for both root-agent and RL-agent contexts.
  Rationale: Reduces ambiguity when handing off between tools and improves copy-paste reliability.
  Date/Author: 2026-02-09 / Codex

## Outcomes & Retrospective

- Template now matches root-agent orchestration semantics: users request runs, root agent scaffolds RLs, RL agent executes loop-local work, and closure updates to root docs require user confirmation.
- Manual RL folder creation instructions were removed from README.
- RL scaffolding is script-driven and validated via throwaway-copy execution.
- README and RUN_BRIEF now include explicit Codex/Claude prompt variants for both root and RL execution roles.
- Remaining future work is optional refinement of prompt wording or additional automation wrappers, not core model correctness.

## Context and Orientation

The current template in `fresh start/` already moved runbook details into README and removed RL-0001 bootstrap residue. However, README still contains shell commands that tell users to create RL directories manually, which conflicts with the intended workflow. The desired flow is:

1. User and root agent iterate on PRD and identify spec questions.
2. Root agent asks visibility preference and decides whether to initiate an RL.
3. Root agent creates RL directory and artifacts (via script), then gives handoff instructions.
4. User launches RL agent separately (for now) and runs ILs inside RL workspace.
5. RL agent closes loop by proposing and applying PRD/LESSONS updates with user confirmation.
6. User resumes with root agent for further refinement or next RL.

Key files to update are:
- `fresh start/README.md`
- `fresh start/AGENTS.md`
- `fresh start/.specforge/INSTRUCTIONS.md`
- `fresh start/.specforge/templates/*`
- new script: `fresh start/.specforge/scripts/init_rl.sh`

## Plan of Work

First, rewrite README to be a concise operator guide that describes roles and the flow in chronological order, with explicit mention that users should ask the root agent to initiate RLs rather than creating directories manually.

Second, add `init_rl.sh` to create a numbered RL folder, workspace/artifacts directories, and seeded RL files from templates. Include a generated handoff brief file for the RL agent.

Third, update operating instructions and templates to encode closure mechanics: RL agent updates root `PRD.md`/`LESSONS.md` only after user confirmation and only when closing or checkpointing the RL.

Finally, validate all references and ensure no stale docs refer to old bootstrap/test-loop behavior.

## Concrete Steps

Run from `/Users/shannon/dev/src/codex/QuodED`.

1) Add script `fresh start/.specforge/scripts/init_rl.sh`.
2) Update README and instructions files.
3) Update templates to include root-to-RL handoff context.
4) Run `rg` and `find` for consistency checks.

## Validation and Acceptance

Accepted when:
- README describes the user flow exactly as root agent orchestration plus separate RL agent execution.
- No README section instructs users to manually create RL directories.
- RL scaffold can be created by script with predictable RL id and files.
- Instructions clearly define who writes root PRD/LESSONS updates and when.

## Idempotence and Recovery

Documentation edits are additive/replace-in-place and safe to rerun. Script creation is additive. If script-created RL directory collides with an existing one, script must fail with a clear message.

## Artifacts and Notes

Main artifacts are updated template docs and one new setup script under `.specforge/scripts/`.

## Interfaces and Dependencies

No external dependencies. Script will use POSIX shell plus standard utilities available on macOS (`find`, `sort`, `sed`, `tr`, `mkdir`, `cp`).

Revision note (2026-02-09): Added explicit Codex/Claude kickoff prompt variants in README and RUN_BRIEF after initial completion to improve handoff quality across tools.

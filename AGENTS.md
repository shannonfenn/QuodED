# Repository Guidelines

## Project Structure & Module Organization
- This is an experimental greenfield project, treat structure, module, language, framework etc. as fungible until the user confirms a hard decision, then update instructions here if so.

## Build, Test, and Development Commands
- If python is required then use uv for any and all python related execution, virtualenv/dependency management, etc. via your uv skill (inform the user if you detect no such skill)
- Do not use pip etc. unless the user confirms that is what they wish.
- Treat all other factors as fungible until the user confirms a hard decision, then update instructions here if so.

## Coding Style & Naming Conventions
- As above.

## Testing Guidelines
- No testing framework or coverage target is configured yet.
- Confirm such with the user when it becomes necessary and update instructions here.

## Commit & Pull Request Guidelines
- The git history is empty, so no established commit message convention exists.
- Confirm such with the user when it becomes necessary and update instructions here.

## Planning / Task Management
- For large, complex units of work write an ExecPlan first and keep it updated while implementing.
  - Plan standard: `.agent/PLANS.md`.
  - New plans: `.agent/plans/YYYY-MM-DD-<slug>.md` (one plan per initiative).
  - Archive completed/abandoned plans in `.agents/plans/archive/` and append the reason to the filename.
- For small changes, skip the plan and just implement + validate.

## Documentation Conventions
- `PRD.md` captures the goal and decisions over time. Append-only: add new entries at the end. Do not edit or reorder prior entries unless a conflict arises; ask the user to clarify conflicts.
- `LESSONS.md` captures lessons learned/insights. Append-only: add new entries at the end. Do not edit or reorder prior entries unless a conflict arises; ask the user to clarify conflicts.
- `STATUS.md` captures project level progress. Keep it updated when reaching milestones.
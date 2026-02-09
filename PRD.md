# Product Requirements Document (PRD)

Append-only: add new entries at the end. Do not edit or reorder prior entries unless a conflict arises. If a conflict arises, ask the user to clarify.

## Goal

Build an agent-first system to verify or refute large mathematical proofs with high integrity and captured insight. The system must produce artifacts acceptable to the mathematical community: explicit axiom sets, reproducible builds, and no hidden escape hatches.

## Decisions Log

2026-02-05
- Decision: Primary interface is CLI + skills for agents, with a user-facing UI.
- Decision: UI must include an orchestration view showing agent runs, artifacts, and intervention controls.
- Decision: Support PDF import (from AI-generated PDFs), with structured segmentation into theorem/lemma-sized tasks.
- Decision: Target multiple formal verification backends: Lean4, Rocq, Isabelle, Agda.
- Decision: Add a deterministic integrity guard that forbids `sorry`/`admit`/`axiom`/unsafe escapes and reports axioms used; LLMs must not be authoritative for validation.
- Decision: Accept classical axioms if explicitly reported.
- Decision: Local execution is acceptable for the initial use case.
- Decision: The initial proof can be tackled as a subset-first strategy; any weakness invalidates the overall proof until addressed.
- Decision: Python is acceptable for the initial pipeline (fast PDF ingestion + tooling), but is not a hard commitment.
- Decision: LLM-assisted workflows should eventually leverage OpenAI, GoogleAI, Anthropic, and Perplexity.

2026-02-06
- Decision: Highlights are not only visual cues; they are paper-region references used to connect paper content to external reasoning units.
- Decision: Replace strict 1:1 mapping with a typed link model that can represent 1:1, m:1, 1:n, and m:n between `PaperRegion` and `ReasoningUnit`.
- Decision: UX default remains one primary region per reasoning unit for readability, with optional supporting/context links.
- Decision: Auto-segmentation output is suggestive, not authoritative. Authoritative regions/links are editable and versioned.
- Decision: Region geometry must be explicit and stable (page plus PDF-coordinate boxes) so visual and model-facing views remain faithful.
- Decision: Later milestone includes a Gemini 3-based region suggestor as a pluggable provider alongside deterministic heuristics.
- Decision: Suggestor outputs must carry provenance and confidence and pass review before promotion to authoritative data.

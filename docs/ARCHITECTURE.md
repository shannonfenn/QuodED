# Architecture

## Pipeline
1. **Import**: PDF → page-aligned text.
2. **Segmentation**: Detect theorem/lemma/definition blocks and chunk.
3. **Task Planning**: Convert chunks into formalization tasks.
4. **Formalization**: Agents produce proof assistant files.
5. **Verification**: Deterministic backends compile and enforce integrity policy.
6. **Insight Capture**: Summaries and rationale are stored alongside tasks.

## Backend Adapter Contract
Each backend should provide:
- `compile`: build the formalization artifacts.
- `assumptions`: list axioms/postulates per theorem.
- `policy_check`: enforce forbidden constructs.
- `trace`: optional dependency graph.

## Integrity Policy (Initial)
- Lean4: forbid `sorry`, `admit`, `axiom`, `unsafe`.
- Rocq: forbid `Admitted`, `Axiom`, `admit`.
- Isabelle: forbid `sorry`, `axiomatization`.
- Agda: forbid `postulate`, `{-# TERMINATING #-}`.

These will be expanded as we learn more about the proof corpus.

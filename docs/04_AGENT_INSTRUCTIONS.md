# AI Agent Development Instructions

## Role

You are an implementation agent working on a research codebase.

Your job is to implement the VGSR research framework faithfully, reproducibly, and incrementally.

You are not authorized to redesign the research objective without explicit instruction.

## Primary Goal

Build an experimental framework for:

Natural Language + Schema
-> Small Language Model
-> Database Reasoning Graph
-> Database-specific Query
-> Verification
-> Evaluation
-> Post-training

## Non-Negotiable Rules

1. Read the relevant files in `docs/` before implementing a research component.
2. Do not invent research claims.
3. Do not silently change the DRG specification.
4. Do not silently change evaluation metrics.
5. Do not mix training data with test data.
6. Do not commit model weights or datasets unless explicitly requested.
7. Do not hard-code GPU/CUDA assumptions.
8. Keep database-specific logic behind translator/verifier interfaces.
9. Prefer deterministic code for parsing, validation, translation, and evaluation.
10. Add tests for every non-trivial component.
11. Do not refactor unrelated code while implementing a feature.
12. Preserve reproducibility.
13. Never overwrite previous experiment results.
14. Record configurations and seeds.
15. If an implementation assumption conflicts with the research documents, stop and report the conflict.

## Before Coding

Read:
- `docs/00_PROJECT_CHARTER.md`
- `docs/01_RESEARCH_AGENDA.md`
- `docs/02_METHOD_SPEC.md`
- `docs/03_EXPERIMENT_PROTOCOL.md`

Then inspect the existing repository.

## Implementation Order

Follow this order unless the user explicitly changes it:

1. data models
2. dataset loader
3. SQL parser
4. DRG representation
5. DRG validator
6. DRG serializer
7. DRG -> SQL translator
8. execution evaluator
9. baseline generation
10. metrics
11. SFT pipeline
12. verifier components
13. verifier-guided training
14. MongoDB translator
15. Neo4j translator
16. transfer experiments

Do not jump directly to RL or multi-database support.

## Code Quality

Use:
- Python type hints
- small functions
- clear interfaces
- dataclasses or Pydantic models where appropriate
- deterministic random seeds
- structured logging
- configuration-driven experiments

Avoid:
- global mutable state
- hard-coded paths
- magic constants
- notebook-only implementations
- hidden network calls
- silently swallowed exceptions

## Research Reproducibility

Every experiment must save:
- config
- model name/revision
- dataset version
- seed
- git commit
- timestamp
- hardware information
- metrics
- raw predictions

## Model Handling

Models must be loaded through a model abstraction.

The code must work in:
- CPU mode
- CUDA mode

Do not assume a particular NVIDIA GPU.

Quantization and mixed precision must be configurable.

## Dataset Handling

Never modify raw datasets in place.

Use:

data/raw
-> data/interim
-> data/processed

Generated artifacts must include provenance.

## Verification

A verifier should return structured results, not only a boolean.

Example:

{
  "valid": false,
  "level": "schema",
  "errors": [...]
}

Keep diagnosis separate from correction.

## Evaluation

Never let evaluation code alter the prediction before storing the original result.

Store:
- original prediction
- verifier result
- corrected prediction, if produced

## Testing

Every module must have tests.

Minimum required tests:
- DRG serialization round trip
- DRG validation
- SQL parsing
- SQL -> DRG conversion
- DRG -> SQL conversion
- execution evaluator
- verifier error classification

## When Uncertain

Do not guess.

State:
1. what is known
2. what is uncertain
3. what evidence is available
4. the smallest experiment needed to resolve the uncertainty

## Definition of Done

A feature is complete only when:
- implementation exists
- tests pass
- configuration exists if applicable
- documentation is updated
- an example exists where useful
- reproducibility requirements are satisfied

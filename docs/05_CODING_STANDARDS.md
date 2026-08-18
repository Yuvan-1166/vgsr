# Coding and Research Standards

## Architecture

Keep the project modular:

data
  -> models
  -> reasoning
  -> translation
  -> verification
  -> evaluation

Do not place research logic in notebooks.

Notebooks are for:
- exploration
- visualization
- analysis

Reusable logic belongs in `src/vgsr`.

## Naming

Use explicit names.

Prefer:
- `DatabaseReasoningGraph`
- `DRGNode`
- `VerificationResult`
- `ExecutionResult`

Avoid:
- `Thing`
- `Data`
- `Helper`
- `Manager`

## Interfaces

Use protocols or abstract interfaces when multiple implementations are expected.

Examples:
- `Translator`
- `Verifier`
- `DatasetLoader`
- `ModelGenerator`

## Errors

Fail loudly for invalid research states.

For example:
- malformed DRG
- unknown operation
- missing schema field
- unavailable database
- invalid experiment configuration

Do not silently return empty results.

## Logging

Use structured logging.

Logs should include:
- experiment ID
- sample ID
- stage
- error type

Avoid excessive debug output during large inference runs.

## Data Integrity

Never mutate:
- raw benchmark data
- gold SQL
- gold DRG
- test predictions

Create derived artifacts instead.

## Performance

Do not prematurely optimize.

First establish correctness.

Then profile:
- parsing
- model inference
- translation
- database execution
- verifier runtime

Optimize only after identifying a real bottleneck.

## Security

Never execute arbitrary model-generated database commands against production systems.

Experiments must use isolated/local databases with read-only or controlled permissions.

## Reproducibility

Set seeds for:
- Python
- NumPy
- PyTorch
- dataset shuffling

Record the final effective configuration.

## Scientific Integrity

A model that performs worse is not a failed experiment.

It is evidence.

Do not:
- remove inconvenient examples
- cherry-pick runs
- change metrics after seeing results
- tune on test data
- hide failed experiments

Record failures in experiment notes.

# Research Data Contract

## Purpose

All examples entering the training/evaluation pipeline should conform to a normalized internal schema.

## Normalized Example

```json
{
  "id": "unique-example-id",
  "question": "natural language question",
  "schema": {},
  "database_type": "sql",
  "database_id": "database-name",
  "gold_query": "SELECT ...",
  "gold_drg": {},
  "metadata": {}
}
```

## Prediction Record

```json
{
  "experiment_id": "E00",
  "example_id": "unique-example-id",
  "model": "model-id",
  "input": {},
  "prediction": {},
  "verifier_result": {},
  "execution_result": {},
  "metrics": {}
}
```

## Training Record

A training record may contain:

```json
{
  "prompt": {},
  "target": {},
  "feedback": {},
  "source": "gold|synthetic|verified|corrected",
  "quality": {}
}
```

## Provenance

Every generated training example should record:
- source example
- generation model
- generation configuration
- verifier version
- timestamp
- validation status

## Synthetic Data

Synthetic examples must never automatically become trusted ground truth.

They must pass the relevant validation pipeline before inclusion.

## Test Data

Test data must never be used to:
- generate training examples
- tune prompts
- select checkpoints
- modify DRG grammar
- select verifier thresholds

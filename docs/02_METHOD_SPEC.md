# Method Specification

## 1. System Concept

VGSR separates three concerns:

1. Reasoning
2. Query translation
3. Verification

Conceptually:

Natural Language + Schema
        |
        v
    SLM Reasoner
        |
        v
       DRG
        |
        v
 Database Translator
        |
        v
Executable Query
        |
        v
     Verifier
        |
        v
Feedback / Evaluation

## 2. Database Reasoning Graph

DRG is an intermediate representation intended to encode database-independent query intent.

### Initial operation vocabulary

- SCAN
- FILTER
- JOIN / CONNECT
- GROUP
- AGGREGATE
- PROJECT
- SORT
- LIMIT
- COMPUTE

Additional operations may be introduced only when required by real datasets.

Potential future operations:
- SET_UNION
- SET_INTERSECTION
- SET_DIFFERENCE
- DISTINCT
- EXISTS
- SUBQUERY
- HAVING

Do not expand the vocabulary unnecessarily.

## 3. DRG Design Requirements

A DRG must be:

- database-independent
- structurally valid
- serializable
- deterministic where generated from a gold query
- translatable
- executable through a target database language
- sufficiently expressive for the evaluation benchmark

## 4. DRG Is a Hypothesis

The DRG representation is not assumed to be optimal.

The implementation must allow us to test:
- whether a graph is better than a sequence
- whether the operation vocabulary is sufficient
- whether graph supervision improves learning
- whether the representation preserves semantics

## 5. Verifier Architecture

The verifier should be decomposed into independent checks.

### Syntax Verifier
Checks:
- valid DRG structure
- valid operation names
- required fields
- graph connectivity
- operation constraints

### Schema Verifier
Checks:
- referenced entities exist
- referenced fields exist
- field types are compatible
- relationships are valid

### Semantic Verifier
Checks:
- operation ordering
- aggregation logic
- grouping compatibility
- projection dependencies
- logical consistency

### Execution Verifier
Checks:
- query execution
- runtime errors
- output compatibility
- result equivalence against a reference where available

## 6. Feedback Format

Prefer structured feedback:

{
  "valid": false,
  "errors": [
    {
      "level": "schema",
      "node": "n4",
      "type": "unknown_field",
      "message": "..."
    }
  ]
}

Do not make free-form natural-language feedback the only verifier output.

## 7. Translation

The translator maps:

DRG -> target query language

Initial target:
- SQL

Later:
- MongoDB Aggregation Pipeline
- Neo4j Cypher

The translator should be deterministic where feasible.

The model should not be asked to translate a DRG during the first reconstruction experiments. This isolates representation quality from model generation.

## 8. Semantic Preservation

For every translator, test:

Gold query -> DRG -> generated query

The generated query should be semantically equivalent to the gold query on the evaluation database.

Exact string equality is not required.

Execution equivalence is the preferred criterion when safe and deterministic.

## 9. Important Engineering Rule

Never allow the verifier to silently modify a prediction during evaluation.

Evaluation should distinguish:
- original prediction
- verifier diagnosis
- corrected prediction

Otherwise the measured metric becomes ambiguous.

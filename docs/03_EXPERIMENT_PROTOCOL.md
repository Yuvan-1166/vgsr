# Experimental Protocol

## 1. Objective

The experimental system must determine which components of VGSR actually contribute to performance.

## 2. Baseline Hierarchy

### B0 — Random / trivial sanity checks
Used only for pipeline validation.

### B1 — Pretrained SLM
Question + schema -> query

No fine-tuning.

### B2 — Direct SFT
Question + schema -> query

This is the principal learning baseline.

### B3 — DRG SFT
Question + schema -> DRG

Then deterministic DRG -> query translation.

### B4 — DRG + verifier
DRG prediction is checked before translation.

### B5 — Verifier-guided post-training
Verifier feedback contributes to new training examples or preference/reward signals.

## 3. Main Comparisons

### Experiment A — Representation
B2 vs B3

Question:
Does structured reasoning improve performance?

### Experiment B — Verification
B3 vs B4/B5

Question:
Does verification improve reasoning?

### Experiment C — Transfer
Train on SQL and evaluate DRG/query generation on MongoDB and Cypher where equivalent data/tasks exist.

### Experiment D — Ablation
Remove one component at a time:
- no DRG
- no syntax verification
- no schema verification
- no semantic verification
- no execution verification
- no verifier feedback

## 4. Metrics

Primary:
- Execution Accuracy

Secondary:
- Exact Match where meaningful
- Valid Query Rate
- DRG Structural Accuracy
- Operation-level precision/recall/F1
- Translation Success Rate
- Semantic Equivalence
- Error-category distribution
- Latency
- Peak memory
- Training time

## 5. Evaluation Rules

Never use only Exact Match for semantic claims.

For database queries:
- parseability is not correctness
- execution success is not necessarily semantic correctness
- string equality is not semantic equality

Use execution-based evaluation and controlled databases whenever possible.

## 6. Repeated Runs

Final comparative experiments should use multiple random seeds.

At minimum:
- seed 42
- seed 123
- seed 2024

If compute is limited, pilot experiments may use one seed, but final claims should disclose this limitation.

## 7. Data Splits

Never tune against the test set.

Maintain:
- train
- validation/dev
- test

For transfer experiments, explicitly document whether the target database is:
- unseen during training
- partially observed
- represented by schema-only examples
- represented by paired cross-database examples

## 8. Error Analysis

Every failed prediction should be assigned one or more categories:

- schema misunderstanding
- operation omission
- operation ordering
- incorrect join/traversal
- aggregation error
- grouping error
- projection error
- filter error
- translation error
- syntax error
- execution error
- semantic error

Use this analysis to guide later experiments, not to retroactively alter the evaluation.

## 9. Statistical Reporting

Report:
- mean
- standard deviation
- number of runs

For important comparisons, consider confidence intervals or significance testing where sample size permits.

Do not report a percentage improvement without reporting the underlying scores.

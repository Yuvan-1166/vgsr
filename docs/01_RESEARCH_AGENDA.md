# Research Agenda

## 1. Overall Experimental Strategy

The project must be developed incrementally:

1. Reproducible environment
2. Dataset ingestion
3. SQL baseline
4. DRG representation
5. DRG reconstruction validation
6. Direct SQL SFT baseline
7. DRG SFT
8. Verifier implementation
9. Verifier-guided post-training
10. Cross-database translation
11. Cross-database transfer
12. Ablation and error analysis

Do not skip directly to the final architecture.

## 2. Milestones

### M0 — Environment
- Python environment
- dependency lock
- repository structure
- deterministic seed handling
- experiment configuration

### M1 — SQL Foundation
- Spider loader
- normalized example schema
- SQL parser
- SQL -> DRG converter
- DRG validator
- DRG -> SQL translator
- execution evaluator

### M2 — Baselines
- pretrained zero-shot SLM
- direct SQL SFT
- evaluation harness

### M3 — DRG Learning
- question/schema -> DRG training format
- DRG SFT
- DRG -> SQL translation
- comparison against direct SQL SFT

### M4 — Verification
- syntax verifier
- schema verifier
- semantic verifier
- execution verifier
- structured error representation

### M5 — Verifier-Guided Learning
Compare candidate learning strategies:
- verifier-generated correction + SFT
- preference-based learning
- reward-based learning, if compute permits

Do not assume one mechanism is superior before experimentation.

### M6 — Cross-Database
- MongoDB translator
- Neo4j translator
- equivalent-query validation
- cross-database datasets

### M7 — Transfer
Train on one database paradigm and evaluate on another.

### M8 — Final Experiments
- ablations
- seed variation
- error analysis
- statistical analysis
- efficiency analysis

## 3. Experimental Ladder

E00: pretrained SLM -> SQL

E01: SQL SFT -> SQL

E02: SLM -> DRG -> SQL

E03: DRG SFT -> SQL

E04: DRG + constrained validation

E05: verifier-guided post-training

E06: cross-database translation

E07: cross-database transfer

E08: ablations

## 4. Required Experimental Discipline

Every experiment must have:
- unique experiment ID
- configuration file
- git commit hash
- model identifier
- dataset identifier/version
- random seed
- hardware information
- training duration
- inference settings
- raw predictions
- computed metrics

## 5. Stop Conditions

Stop and revisit the design if:
- DRG cannot represent common queries reliably.
- DRG -> query translation is not semantically faithful.
- verifier labels are inconsistent.
- baseline evaluation is not reproducible.
- improvements occur only on training data.
- a proposed contribution is already demonstrated by a directly comparable prior method.

A failed hypothesis is a valid research result.

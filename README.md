# Verifier-Guided Structured Reasoning for Cross-Database Query Generation

A research project exploring whether **Small Language Models (SLMs)** can achieve improved database reasoning and cross-database query generation through **structured intermediate representations and verifier-guided post-training**.

## Overview

Current natural-language database query generation systems often treat the task as a direct translation problem:

```text
Natural Language → Database Query
```

This tightly couples reasoning with the syntax of a particular query language. As a result, a model trained for one database paradigm may struggle to generalize to others.

This project investigates an alternative approach:

```text
Natural Language
       ↓
Database Reasoning Graph (DRG)
       ↓
Database-specific Query
```

The **Database Reasoning Graph (DRG)** acts as an intermediate, database-agnostic representation of the reasoning required to answer a query. The same reasoning structure can then be translated into different query paradigms such as **SQL, MongoDB, and Neo4j Cypher**.

The project further investigates whether **verifier-guided feedback** can improve the performance of small language models by identifying structural, schema, semantic, and execution-level errors during post-training.

## Research Objective

The primary objective is to investigate whether explicit structured reasoning and verifier-guided learning can improve the performance of SLMs on database query generation while enabling better transfer across heterogeneous database paradigms.

The research focuses on three major questions:

1. **Does an intermediate reasoning representation improve query generation compared with direct translation?**
2. **Can verifier-guided feedback improve the reasoning capabilities of small language models?**
3. **Can database-independent reasoning learned from one query paradigm transfer to other database paradigms?**

## Proposed Framework

The proposed **Verifier-Guided Structured Reasoning (VGSR)** framework consists of three major components:

```text
                    ┌─────────────────────┐
                    │ Natural Language    │
                    │ Question + Schema   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Small Language      │
                    │ Model               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Database Reasoning  │
                    │ Graph (DRG)          │
                    └──────────┬──────────┘
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
               SQL          MongoDB       Cypher
                  │            │            │
                  └────────────┼────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Multi-Level         │
                    │ Verification        │
                    └─────────────────────┘
```

### Database Reasoning Graph

The DRG represents database operations independently of query-language syntax.

The current representation includes operations such as:

- `FROM`
- `WHERE`
- `JOIN`
- `GROUP`
- `AGGREGATE`
- `SELECT`
- `ORDER`
- `LIMIT`

These operations form a structured representation of the intended query reasoning before translation into a specific database language.

### Verifier

The framework investigates multiple levels of verification:

- **Syntax verification** — validates the structure of the generated DRG.
- **Schema verification** — checks tables, collections, fields, and type compatibility.
- **Semantic verification** — checks whether operations form a logically coherent query.
- **Execution verification** — executes the translated query and evaluates its result.

The verifier is intended to provide more informative feedback than a simple correct/incorrect signal.

## Experimental Direction

The experimentation is designed incrementally.

### Baseline

```text
Question + Schema
       ↓
     SLM
       ↓
      SQL
```

### Structured Reasoning

```text
Question + Schema
       ↓
     SLM
       ↓
      DRG
       ↓
      SQL
```

### Verifier-Guided Reasoning

```text
Question + Schema
       ↓
     SLM
       ↓
      DRG
       ↓
   Verification
       ↓
   Feedback
       ↓
  Post-training
```

### Cross-Database Transfer

```text
                 DRG
              /   |   \
             /    |    \
           SQL  MongoDB Cypher
```

The experimental framework will compare direct query generation, DRG-based generation, and verifier-guided approaches using quantitative evaluation and error analysis.

## Evaluation

The project will evaluate query-generation performance using metrics including:

- Exact Match
- Execution Accuracy
- Test Suite Accuracy
- Cross-Database Transfer Accuracy
- Component-level accuracy
- Error-type analysis

The evaluation will focus not only on whether the generated query matches a reference string, but also on whether it produces the correct result when executed.

## Research Status

This repository is under active research and experimentation.

The implementation will progressively cover:

- [ ] Dataset preparation
- [ ] DRG representation
- [ ] SQL → DRG conversion
- [ ] DRG validation
- [ ] Database-specific translators
- [ ] SLM baseline
- [ ] DRG supervised fine-tuning
- [ ] Verifier implementation
- [ ] Verifier-guided post-training
- [ ] MongoDB translation
- [ ] Neo4j translation
- [ ] Cross-database experiments
- [ ] Ablation studies
- [ ] Final evaluation and analysis

## Research Scope

The project primarily investigates **small language model performance, structured reasoning, verifier-guided learning, and cross-database generalization**.

The goal is not simply to build another natural-language-to-database-query application. Instead, the project investigates whether explicitly separating **database reasoning from query-language syntax** can provide a more effective training paradigm for small language models.

## Project Structure

The repository will be organized around four major components:

```text
data/          → datasets and processed research data
src/           → framework implementation
experiments/   → experimental configurations and runs
results/       → evaluation results and analysis
```

Detailed implementation and experimental documentation will be added as the research progresses.

## Status

**Research / Experimental**

The architecture and experimental methodology are being implemented and evaluated incrementally.

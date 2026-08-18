# VGSR Project Charter

## Project

**Verifier-Guided Structured Reasoning (VGSR) for Cross-Database Query Generation using Small Language Models**

## Purpose

This repository contains the implementation and experimental infrastructure for a research project investigating whether Small Language Models (SLMs) can improve database reasoning when reasoning is represented explicitly through a Database Reasoning Graph (DRG) and improved using verifier-guided post-training.

The project is a research implementation, not merely a database chatbot or Text-to-SQL application.

## Core Research Problem

Direct natural-language-to-query systems couple reasoning with database-specific syntax:

Natural Language -> SQL / MQL / Cypher

VGSR investigates:

Natural Language -> Database Reasoning Graph -> Database-specific Query

The central hypothesis is that an explicit database-independent reasoning representation can improve reasoning quality, cross-database transfer, interpretability, and robustness of SLMs.

## Research Questions

### RQ1
Does structured reasoning through a Database Reasoning Graph improve query-generation performance compared with direct query generation?

### RQ2
Does verifier-guided feedback improve the quality of structured reasoning and query generation in SLMs?

### RQ3
Can database-independent reasoning learned in one database paradigm transfer to other paradigms such as MongoDB and Neo4j?

## Primary Research Hypothesis

Explicit supervision of a database-independent structured reasoning representation will improve the generalization of SLMs compared with direct syntax-oriented fine-tuning.

## Secondary Hypotheses

1. Verifier feedback will improve reasoning quality beyond ordinary supervised fine-tuning.
2. Execution-aware verification will identify useful errors that string-level evaluation cannot capture.
3. DRG-based training will provide better cross-database transfer than database-specific query supervision alone.
4. Structured reasoning will make model errors easier to classify and analyze.

## Research Principles

1. Do not claim novelty without evidence.
2. Do not hide negative results.
3. Every experiment must answer a research question or validate an engineering assumption.
4. Separate baseline, proposed method, and ablation experiments.
5. Keep all experiments reproducible.
6. Never overwrite experimental results.
7. Record model, dataset version, seed, configuration, and code revision for every run.
8. Prefer deterministic and programmatic validation over LLM judgment where possible.
9. Do not use generated reasoning as ground truth without validation.
10. Do not optimize metrics before the evaluation protocol is frozen.

## Current Scope

Initial database:
- SQL / relational databases

Target cross-database extensions:
- MongoDB Aggregation Pipeline
- Neo4j Cypher

Initial SLM:
- Qwen/Qwen2.5-Coder-1.5B-Instruct

The model and database choices are experimental defaults and may be revised after pilot experiments.

## Out of Scope Initially

- Building a production database assistant
- Supporting every database engine
- Training a foundation model from scratch
- Assuming the proposed DRG is correct before validation
- Implementing all RL methods before establishing SFT baselines
- Claiming self-improvement without controlled experiments

## Definition of Success

The project succeeds scientifically if experiments can establish, with statistically and methodologically defensible evidence, whether DRG and verifier-guided post-training contribute independently and jointly to SLM performance.

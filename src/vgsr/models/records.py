"""Research data record models.

Defines the normalized data contracts for examples, predictions, and training
records as specified in docs/06_DATA_SCHEMA.md.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from vgsr.models.drg import DatabaseReasoningGraph
from vgsr.models.schema import DatabaseSchema


class NormalizedExample(BaseModel):
    """A single normalized training/evaluation example.

    All examples entering the pipeline must conform to this schema.
    """

    id: str = Field(description="Unique example identifier")
    question: str = Field(description="Natural language question")
    db_schema: DatabaseSchema = Field(
        serialization_alias="schema", description="Database schema context"
    )
    database_type: str = Field(default="sql", description="Database paradigm")
    database_id: str = Field(default="", description="Database identifier")
    gold_query: str = Field(description="Gold-standard query string")
    gold_drg: DatabaseReasoningGraph | None = Field(default=None, description="Gold DRG if available")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class PredictionRecord(BaseModel):
    """Record of a model prediction for one example.

    Stored separately from the original example to preserve evaluation integrity.
    """

    experiment_id: str = Field(description="Experiment identifier")
    example_id: str = Field(description="NormalizedExample.id")
    model: str = Field(description="Model identifier")
    input: dict[str, Any] = Field(default_factory=dict, description="Model input")
    prediction: dict[str, Any] = Field(default_factory=dict, description="Raw model prediction")
    predicted_drg: DatabaseReasoningGraph | None = Field(default=None)
    predicted_query: str | None = Field(default=None)
    verifier_result: dict[str, Any] | None = Field(default=None)
    execution_result: dict[str, Any] | None = Field(default=None)
    metrics: dict[str, Any] = Field(default_factory=dict)
    corrected_prediction: dict[str, Any] | None = Field(
        default=None, description="Post-verifier corrected prediction, if produced"
    )

    model_config = {"extra": "forbid"}


class TrainingRecord(BaseModel):
    """A single training example for SFT or verifier-guided training."""

    prompt: dict[str, Any] = Field(default_factory=dict, description="Model input")
    target: dict[str, Any] = Field(default_factory=dict, description="Target output")
    feedback: dict[str, Any] | None = Field(default=None, description="Verifier feedback")
    source: str = Field(
        default="gold",
        description="Provenance: gold, synthetic, verified, or corrected",
    )
    quality: dict[str, Any] = Field(default_factory=dict, description="Quality metadata")

    model_config = {"extra": "forbid"}


class ExperimentConfig(BaseModel):
    """Configuration for a single experiment run."""

    experiment_id: str = Field(description="Unique experiment ID (e.g. E00, E01)")
    name: str = Field(description="Human-readable experiment name")
    description: str = Field(default="")
    model_name: str = Field(default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    dataset_id: str = Field(default="spider")
    dataset_version: str = Field(default="")
    seed: int = Field(default=42)
    git_commit: str = Field(default="")
    hardware: dict[str, str] = Field(default_factory=dict)
    training: dict[str, Any] = Field(default_factory=dict)
    generation: dict[str, Any] = Field(default_factory=dict)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}

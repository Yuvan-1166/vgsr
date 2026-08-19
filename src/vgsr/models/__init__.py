"""Core data models for the VGSR framework."""

from vgsr.models.drg import (
    AggregationFunction,
    DatabaseReasoningGraph,
    DRGEdge,
    DRGNode,
    DRGNodeParams,
    EdgeType,
    JoinType,
    OperationType,
    SortDirection,
)
from vgsr.models.records import (
    ExperimentConfig,
    NormalizedExample,
    PredictionRecord,
    TrainingRecord,
)
from vgsr.models.schema import (
    Column,
    ColumnType,
    DatabaseSchema,
    ForeignKey,
    Table,
)
from vgsr.models.verification import (
    ErrorSeverity,
    VerificationError,
    VerificationLevel,
    VerificationResult,
)

__all__ = [
    "AggregationFunction",
    "Column",
    "ColumnType",
    "DRGEdge",
    "DRGNode",
    "DRGNodeParams",
    "DatabaseReasoningGraph",
    "DatabaseSchema",
    "EdgeType",
    "ErrorSeverity",
    "ExperimentConfig",
    "ForeignKey",
    "JoinType",
    "NormalizedExample",
    "OperationType",
    "PredictionRecord",
    "SortDirection",
    "Table",
    "TrainingRecord",
    "VerificationError",
    "VerificationLevel",
    "VerificationResult",
]

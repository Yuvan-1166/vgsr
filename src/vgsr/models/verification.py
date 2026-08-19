"""Verification result models.

Structured output from the multi-level verifier. Each verifier level returns
a VerificationResult that can be composed or consumed independently.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field


class VerificationLevel(str, enum.Enum):
    """Verifier hierarchy levels."""

    SYNTAX = "syntax"
    SCHEMA = "schema"
    SEMANTIC = "semantic"
    EXECUTION = "execution"


class ErrorSeverity(str, enum.Enum):
    """Severity of a verification error."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class VerificationError(BaseModel):
    """A single error detected by a verifier."""

    level: VerificationLevel = Field(description="Which verifier detected this")
    error_type: str = Field(description="Error category (e.g. 'unknown_table', 'invalid_order')")
    node_id: str | None = Field(default=None, description="DRG node where error occurred")
    entity: str | None = Field(default=None, description="Entity that caused the error")
    message: str = Field(description="Human-readable error description")
    suggestions: list[str] = Field(default_factory=list, description="Suggested corrections")
    severity: ErrorSeverity = Field(default=ErrorSeverity.ERROR)

    model_config = {"extra": "forbid"}


class VerificationResult(BaseModel):
    """Aggregate result from all verifier levels for a single DRG or query."""

    valid: bool = Field(description="Overall validity (True only if no errors)")
    errors: list[VerificationError] = Field(default_factory=list)
    level: VerificationLevel = Field(
        default=VerificationLevel.SYNTAX,
        description="Highest level that was checked",
    )
    details: dict[str, Any] = Field(default_factory=dict, description="Level-specific details")

    model_config = {"extra": "forbid"}

    def errors_at_level(self, level: VerificationLevel) -> list[VerificationError]:
        """Return errors from a specific verifier level."""
        return [e for e in self.errors if e.level == level]

    def has_errors_at_level(self, level: VerificationLevel) -> bool:
        """Check if any errors exist at a given level."""
        return any(e.level == level for e in self.errors)

    def to_feedback_dict(self) -> dict[str, Any]:
        """Convert to a structured feedback dict suitable for training signals."""
        return {
            "valid": self.valid,
            "errors": [
                {
                    "level": e.level.value,
                    "error_type": e.error_type,
                    "node_id": e.node_id,
                    "entity": e.entity,
                    "message": e.message,
                    "suggestions": e.suggestions,
                    "severity": e.severity.value,
                }
                for e in self.errors
            ],
        }

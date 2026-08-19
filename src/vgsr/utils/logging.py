"""Structured logging for VGSR experiments.

Provides experiment-aware logging with consistent formatting.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, ClassVar, Self

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Configure root logger for the VGSR project.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path to a log file for file output.

    Returns:
        The configured root logger.
    """
    root = logging.getLogger("vgsr")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    if root.handlers:
        return root

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(root.level)
    console.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(console)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(root.level)
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        root.addHandler(file_handler)

    return root


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the 'vgsr' namespace."""
    return logging.getLogger(f"vgsr.{name}")


class ExperimentContext:
    """Context manager that adds experiment metadata to all log records.

    Usage:
        with ExperimentContext(experiment_id="E00", sample_id="s123"):
            logger.info("processing")
            # Output includes experiment_id and sample_id
    """

    _context: ClassVar[dict[str, Any]] = {}

    def __init__(self, **context: Any) -> None:
        self.new_context = context

    def __enter__(self) -> Self:
        ExperimentContext._context.update(self.new_context)
        return self

    def __exit__(self, *args: object) -> None:
        for key in self.new_context:
            ExperimentContext._context.pop(key, None)

    @classmethod
    def get_context(cls) -> dict[str, Any]:
        return dict(cls._context)


class ExperimentFilter(logging.Filter):
    """Logging filter that injects experiment context into records."""

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in ExperimentContext.get_context().items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True

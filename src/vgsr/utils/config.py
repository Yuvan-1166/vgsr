"""Configuration loading utilities.

Loads YAML experiment configs with sensible defaults and seed propagation.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Top-level project settings."""

    name: str = "vgsr"
    version: str = "0.1.0"
    seed: int = 42


class PathsConfig(BaseModel):
    """Filesystem paths relative to project root."""

    data: str = "data"
    raw_data: str = "data/raw"
    processed_data: str = "data/processed"
    results: str = "results"
    checkpoints: str = "results/checkpoints"


class ModelConfig(BaseModel):
    """Model loading settings."""

    name: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    torch_dtype: str = "auto"
    trust_remote_code: bool = False


class GenerationConfig(BaseModel):
    """Inference generation settings."""

    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False


class LoggingConfig(BaseModel):
    """Logging settings."""

    level: str = "INFO"


class VGSRConfig(BaseModel):
    """Complete VGSR project configuration."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    evaluation: dict[str, Any] = Field(default_factory=lambda: {"batch_size": 1})
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    git_commit: str = Field(default="", description="Git commit hash, injected at load time")
    extra: dict[str, Any] = Field(default_factory=dict)


def get_git_commit_hash(project_root: Path) -> str:
    """Return the short git commit hash for the project."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def set_global_seed(seed: int) -> None:
    """Set deterministic seeds for reproducibility across libraries."""
    import random

    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def load_config(config_path: Path, project_root: Path | None = None) -> VGSRConfig:
    """Load a YAML configuration file into VGSRConfig.

    Merges the base config with an experiment-specific config if provided.
    """
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent.parent

    with open(config_path) as f:
        raw = yaml.safe_load(f) or {}

    raw["git_commit"] = get_git_commit_hash(project_root)

    return VGSRConfig(**raw)

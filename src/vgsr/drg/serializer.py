"""DRG serialization utilities.

Handles JSON serialization and deserialization of DatabaseReasoningGraph objects,
including file I/O for persistence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vgsr.models.drg import DatabaseReasoningGraph


def drg_to_json(drg: DatabaseReasoningGraph, indent: int = 2) -> str:
    """Serialize a DRG to a JSON string."""
    return json.dumps(drg.model_dump(), indent=indent, default=str)


def drg_from_json(json_str: str) -> DatabaseReasoningGraph:
    """Deserialize a DRG from a JSON string."""
    data = json.loads(json_str)
    return DatabaseReasoningGraph(**data)


def save_drg(drg: DatabaseReasoningGraph, path: Path) -> None:
    """Write a DRG to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(drg_to_json(drg))


def load_drg(path: Path) -> DatabaseReasoningGraph:
    """Read a DRG from a JSON file."""
    return drg_from_json(path.read_text())


def drg_to_compact(drg: DatabaseReasoningGraph) -> list[dict[str, Any]]:
    """Serialize a DRG to a compact list-of-dicts for LLM prompts.

    Each element is {"op": "FROM", "params": {...}}.
    """
    result = []
    for node in drg.nodes:
        entry: dict[str, Any] = {"op": node.operation.value}
        params = node.params.model_dump(exclude_none=True)
        if params:
            entry["params"] = params
        result.append(entry)
    return result


def drg_from_compact(operations: list[dict[str, Any]]) -> DatabaseReasoningGraph:
    """Deserialize a DRG from the compact list-of-dicts format."""
    return DatabaseReasoningGraph.from_sequence(
        [{"id": f"n{i+1}", "operation": op["op"], "params": op.get("params", {})} for i, op in enumerate(operations)]
    )


def drg_to_text(drg: DatabaseReasoningGraph) -> str:
    """Render a DRG as a human-readable text representation for prompts.

    Example output:
        1. FROM employees
        2. WHERE department = 'Sales'
        3. GROUP [department]
        4. AGGREGATE SUM(salary) AS total_salary
        5. SELECT [department, total_salary]
        6. ORDER total_salary DESC
    """
    lines: list[str] = []
    for i, node in enumerate(drg.nodes, 1):
        p = node.params
        op = node.operation.value

        if op == "FROM":
            detail = p.table or "?"
        elif op == "WHERE":
            detail = f"{p.column} {p.operator} {p.value!r}" if p.column else p.value or ""
        elif op == "JOIN":
            detail = f"{p.join_table} ON {p.left_column} = {p.right_column}" if p.join_table else "?"
        elif op == "GROUP":
            cols = ", ".join(p.columns) if p.columns else "?"
            detail = f"[{cols}]"
        elif op == "AGGREGATE":
            func = p.function.value if p.function else "?"
            col = p.aggregate_column or "*"
            alias = f" AS {p.alias}" if p.alias else ""
            detail = f"{func}({col}){alias}"
        elif op == "SELECT":
            cols = ", ".join(p.select_columns) if p.select_columns else "*"
            detail = f"[{cols}]"
        elif op == "ORDER":
            d = p.sort_direction.value if p.sort_direction else "ASC"
            detail = f"{p.sort_column} {d}" if p.sort_column else "?"
        elif op == "LIMIT":
            detail = str(p.limit_value) if p.limit_value is not None else "?"
        else:
            detail = ""

        lines.append(f"{i}. {op} {detail}")

    return "\n".join(lines)

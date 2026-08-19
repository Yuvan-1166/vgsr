"""Database Reasoning Graph data models.

Defines the core DRG representation: operations, nodes, edges, and the graph itself.
The DRG is a database-agnostic intermediate representation of query reasoning.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class OperationType(str, enum.Enum):
    """Core database-independent operations supported by DRG."""

    FROM = "FROM"
    WHERE = "WHERE"
    JOIN = "JOIN"
    GROUP = "GROUP"
    AGGREGATE = "AGGREGATE"
    SELECT = "SELECT"
    ORDER = "ORDER"
    LIMIT = "LIMIT"


class EdgeType(str, enum.Enum):
    """Relationship types between DRG nodes."""

    SEQUENCE = "sequence"
    CONDITION = "condition"
    REFERENCE = "reference"


class AggregationFunction(str, enum.Enum):
    """Supported aggregation functions."""

    SUM = "SUM"
    COUNT = "COUNT"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"


class SortDirection(str, enum.Enum):
    """Sort direction for ORDER operations."""

    ASC = "ASC"
    DESC = "DESC"


class JoinType(str, enum.Enum):
    """Join types."""

    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class DRGNodeParams(BaseModel):
    """Parameters for a DRG operation node.

    Different operation types use different subsets of these fields.
    """

    # FROM / JOIN
    table: str | None = None
    table_alias: str | None = None

    # WHERE
    column: str | None = None
    operator: str | None = None
    value: Any = None
    values: list[Any] | None = None

    # JOIN
    join_table: str | None = None
    join_type: JoinType | None = None
    join_condition: str | None = None
    left_column: str | None = None
    right_column: str | None = None

    # GROUP
    columns: list[str] | None = None

    # AGGREGATE
    function: AggregationFunction | None = None
    aggregate_column: str | None = None
    alias: str | None = None

    # SELECT
    select_columns: list[str] | None = None

    # ORDER
    sort_column: str | None = None
    sort_direction: SortDirection | None = None

    # LIMIT
    limit_value: int | None = None

    model_config = {"extra": "forbid"}


class DRGNode(BaseModel):
    """A single operation node in a Database Reasoning Graph."""

    id: str = Field(description="Unique node identifier (e.g. 'n1', 'n2')")
    operation: OperationType = Field(description="The operation type for this node")
    params: DRGNodeParams = Field(
        default_factory=DRGNodeParams,
        description="Operation-specific parameters",
    )

    model_config = {"extra": "forbid"}


class DRGEdge(BaseModel):
    """A directed edge between two DRG nodes representing data flow."""

    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    edge_type: EdgeType = Field(default=EdgeType.SEQUENCE)

    model_config = {"extra": "forbid"}


class DatabaseReasoningGraph(BaseModel):
    """A Database Reasoning Graph — the core intermediate representation.

    A DAG where nodes are database operations and edges represent data flow.
    Must satisfy composition constraints:
        FROM -> WHERE* -> JOIN* -> GROUP? -> AGGREGATE* -> SELECT -> ORDER? -> LIMIT?
    """

    nodes: list[DRGNode] = Field(default_factory=list, description="Ordered list of operation nodes")
    edges: list[DRGEdge] = Field(default_factory=list, description="Directed edges between nodes")

    @model_validator(mode="after")
    def _assign_sequential_ids(self) -> DatabaseReasoningGraph:
        """Auto-assign sequential IDs if nodes lack them."""
        for i, node in enumerate(self.nodes):
            if not node.id:
                node.id = f"n{i + 1}"
        return self

    def node_by_id(self, node_id: str) -> DRGNode | None:
        """Look up a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def operation_sequence(self) -> list[OperationType]:
        """Return the operation types in node order."""
        return [node.operation for node in self.nodes]

    def topological_sort(self) -> list[str]:
        """Return node IDs in topological order (BFS from sources)."""
        adj: dict[str, list[str]] = {node.id: [] for node in self.nodes}
        in_degree: dict[str, int] = {node.id: 0 for node in self.nodes}
        for edge in self.edges:
            adj[edge.source].append(edge.target)
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order: list[str] = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for neighbor in adj.get(nid, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order

    def to_sequence(self) -> list[dict[str, Any]]:
        """Serialize to a flat list of operation dicts for LLM consumption."""
        sorted_ids = self.topological_sort()
        node_map = {n.id: n for n in self.nodes}
        result = []
        for nid in sorted_ids:
            node = node_map[nid]
            result.append(
                {
                    "id": node.id,
                    "operation": node.operation.value,
                    "params": node.params.model_dump(exclude_none=True),
                }
            )
        return result

    @classmethod
    def from_sequence(cls, operations: list[dict[str, Any]]) -> DatabaseReasoningGraph:
        """Deserialize from a flat list of operation dicts."""
        nodes: list[DRGNode] = []
        edges: list[DRGEdge] = []

        for i, op in enumerate(operations):
            node_id = op.get("id", f"n{i + 1}")
            nodes.append(
                DRGNode(
                    id=node_id,
                    operation=OperationType(op["operation"]),
                    params=DRGNodeParams(**op.get("params", {})),
                )
            )
            if i > 0:
                edges.append(
                    DRGEdge(
                        source=f"n{i}",
                        target=node_id,
                        edge_type=EdgeType.SEQUENCE,
                    )
                )

        return cls(nodes=nodes, edges=edges)

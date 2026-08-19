"""Deterministic DRG to SQL translator.

Converts a valid DatabaseReasoningGraph into a SQL SELECT statement.
The translation is purely deterministic — no model inference involved.
"""

from __future__ import annotations

from vgsr.models.drg import (
    AggregationFunction,
    DatabaseReasoningGraph,
    DRGNode,
    OperationType,
)


def _agg_to_sql(func: AggregationFunction, col: str) -> str:
    """Render an aggregation as SQL: SUM(col), COUNT(*), etc."""
    col_ref = col if col else "*"
    return f"{func.value}({col_ref})"


def drg_to_sql(drg: DatabaseReasoningGraph) -> str:
    """Translate a valid DRG into a SQL SELECT string.

    Follows the standard SQL clause ordering:
        SELECT ... FROM ... WHERE ... GROUP BY ... ORDER BY ... LIMIT ...

    The DRG nodes are processed in topological order and mapped to SQL clauses.
    """
    # Categorize nodes by operation
    from_nodes: list[DRGNode] = []
    where_nodes: list[DRGNode] = []
    join_nodes: list[DRGNode] = []
    group_node: DRGNode | None = None
    agg_nodes: list[DRGNode] = []
    select_node: DRGNode | None = None
    order_nodes: list[DRGNode] = []
    limit_node: DRGNode | None = None

    for node in drg.nodes:
        match node.operation:
            case OperationType.FROM:
                from_nodes.append(node)
            case OperationType.WHERE:
                where_nodes.append(node)
            case OperationType.JOIN:
                join_nodes.append(node)
            case OperationType.GROUP:
                group_node = node
            case OperationType.AGGREGATE:
                agg_nodes.append(node)
            case OperationType.SELECT:
                select_node = node
            case OperationType.ORDER:
                order_nodes.append(node)
            case OperationType.LIMIT:
                limit_node = node

    parts: list[str] = []

    # SELECT clause
    if select_node and select_node.params.select_columns:
        cols = list(select_node.params.select_columns)
        # Replace alias references with actual aggregation expressions
        agg_alias_map: dict[str, str] = {}
        for agg in agg_nodes:
            alias = agg.params.alias or f"{agg.params.function.value}_{agg.params.aggregate_column}"
            sql_agg = _agg_to_sql(agg.params.function, agg.params.aggregate_column)
            agg_alias_map[alias] = f"{sql_agg} AS {alias}"

        resolved: list[str] = []
        for c in cols:
            if c in agg_alias_map:
                resolved.append(agg_alias_map[c])
            else:
                resolved.append(c)

        # Append any aggregations not yet referenced in SELECT
        for agg in agg_nodes:
            alias = agg.params.alias or f"{agg.params.function.value}_{agg.params.aggregate_column}"
            sql_agg = _agg_to_sql(agg.params.function, agg.params.aggregate_column)
            if not any(alias in r for r in resolved):
                resolved.append(f"{sql_agg} AS {alias}")

        select_str = ", ".join(resolved)
    else:
        # Default SELECT with aggregations
        select_parts = []
        if group_node and group_node.params.columns:
            select_parts.extend(group_node.params.columns)
        for agg in agg_nodes:
            alias = agg.params.alias or f"{agg.params.function.value}_{agg.params.aggregate_column}"
            sql_agg = _agg_to_sql(agg.params.function, agg.params.aggregate_column)
            select_parts.append(f"{sql_agg} AS {alias}")
        select_str = ", ".join(select_parts) if select_parts else "*"

    parts.append(f"SELECT {select_str}")

    # FROM clause
    if from_nodes:
        table = from_nodes[0].params.table or "?"
        alias = from_nodes[0].params.table_alias
        if alias:
            parts.append(f"FROM {table} AS {alias}")
        else:
            parts.append(f"FROM {table}")

    # JOIN clauses
    for join in join_nodes:
        jt = join.params.join_type.value if join.params.join_type else "INNER"
        table = join.params.join_table or "?"
        left = join.params.left_column or ""
        right = join.params.right_column or ""
        parts.append(f"{jt} JOIN {table} ON {left} = {right}")

    # WHERE clause
    if where_nodes:
        conditions: list[str] = []
        for w in where_nodes:
            p = w.params
            if p.operator == "EXPRESSION" and p.value or p.operator == "OR" and p.value:
                conditions.append(str(p.value))
            elif p.operator == "IN":
                vals = ", ".join(_sql_literal(v) for v in (p.values or []))
                conditions.append(f"{p.column} IN ({vals})")
            elif p.operator == "BETWEEN" and p.values and len(p.values) == 2:
                conditions.append(f"{p.column} BETWEEN {_sql_literal(p.values[0])} AND {_sql_literal(p.values[1])}")
            elif p.column:
                conditions.append(f"{p.column} {p.operator} {_sql_literal(p.value)}")
        if conditions:
            parts.append(f"WHERE {' AND '.join(conditions)}")

    # GROUP BY clause
    if group_node and group_node.params.columns:
        cols = ", ".join(group_node.params.columns)
        parts.append(f"GROUP BY {cols}")

    # ORDER BY clause
    if order_nodes:
        order_parts: list[str] = []
        for ob in order_nodes:
            col = ob.params.sort_column or ""
            direction = ob.params.sort_direction.value if ob.params.sort_direction else "ASC"
            order_parts.append(f"{col} {direction}")
        parts.append(f"ORDER BY {', '.join(order_parts)}")

    # LIMIT clause
    if limit_node and limit_node.params.limit_value is not None:
        parts.append(f"LIMIT {limit_node.params.limit_value}")

    return " ".join(parts) + ";"


def _sql_literal(value: object) -> str:
    """Format a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)

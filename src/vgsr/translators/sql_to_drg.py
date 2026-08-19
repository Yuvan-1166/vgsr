"""SQL to Database Reasoning Graph converter.

Converts parsed SQL (via sqlglot) into a DatabaseReasoningGraph.
This is the SQL -> DRG direction used for generating gold DRGs from Spider data.
"""

from __future__ import annotations

from vgsr.drg.parser import ParsedSQL
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


def _agg_name_to_enum(name: str) -> AggregationFunction:
    """Map sqlglot aggregate function names to our enum."""
    name = name.upper()
    mapping = {
        "SUM": AggregationFunction.SUM,
        "COUNT": AggregationFunction.COUNT,
        "AVG": AggregationFunction.AVG,
        "MIN": AggregationFunction.MIN,
        "MAX": AggregationFunction.MAX,
    }
    return mapping.get(name, AggregationFunction.COUNT)


def _sort_direction(d: str) -> SortDirection:
    return SortDirection.DESC if d.upper() == "DESC" else SortDirection.ASC


def parsed_sql_to_drg(parsed: ParsedSQL) -> DatabaseReasoningGraph:
    """Convert a ParsedSQL structure into a DatabaseReasoningGraph.

    Follows the canonical operation order:
        FROM -> WHERE* -> JOIN* -> GROUP? -> AGGREGATE* -> SELECT -> ORDER? -> LIMIT?
    """
    nodes: list[DRGNode] = []
    edges: list[DRGEdge] = []
    node_counter = 0

    def _next_id() -> str:
        nonlocal node_counter
        node_counter += 1
        return f"n{node_counter}"

    def _add_node(op: OperationType, params: DRGNodeParams | None = None) -> str:
        nid = _next_id()
        nodes.append(DRGNode(id=nid, operation=op, params=params or DRGNodeParams()))
        if len(nodes) > 1:
            edges.append(DRGEdge(source=nodes[-2].id, target=nid, edge_type=EdgeType.SEQUENCE))
        return nid

    # 1. FROM
    if parsed.from_table:
        _add_node(
            OperationType.FROM,
            DRGNodeParams(table=parsed.from_table, table_alias=parsed.from_alias or None),
        )

    # 2. WHERE
    for cond in parsed.where_conditions:
        if cond.operator == "EXPRESSION":
            # Fallback: store raw expression as value
            _add_node(
                OperationType.WHERE,
                DRGNodeParams(column="", operator="EXPRESSION", value=cond.value),
            )
        elif cond.operator == "OR":
            _add_node(
                OperationType.WHERE,
                DRGNodeParams(column="", operator="OR", value=cond.value),
            )
        elif cond.operator == "IN":
            _add_node(
                OperationType.WHERE,
                DRGNodeParams(column=cond.column, operator="IN", values=cond.values),
            )
        elif cond.operator == "BETWEEN":
            _add_node(
                OperationType.WHERE,
                DRGNodeParams(column=cond.column, operator="BETWEEN", values=cond.values),
            )
        else:
            _add_node(
                OperationType.WHERE,
                DRGNodeParams(column=cond.column, operator=cond.operator, value=cond.value),
            )

    # 3. JOINs
    for join in parsed.joins:
        jt = JoinType.LEFT if join.join_type.upper() == "LEFT" else JoinType.INNER
        _add_node(
            OperationType.JOIN,
            DRGNodeParams(
                join_table=join.table,
                join_type=jt,
                left_column=join.on_left,
                right_column=join.on_right,
            ),
        )

    # 4. GROUP BY
    if parsed.group_by_columns:
        _add_node(
            OperationType.GROUP,
            DRGNodeParams(columns=parsed.group_by_columns),
        )

    # 5. AGGREGATE
    for agg in parsed.aggregations:
        func = _agg_name_to_enum(agg["function"])
        _add_node(
            OperationType.AGGREGATE,
            DRGNodeParams(
                function=func,
                aggregate_column=agg.get("column", ""),
                alias=agg.get("alias"),
            ),
        )

    # 6. SELECT
    select_cols = parsed.select_columns if parsed.select_columns else ["*"]
    # Filter out columns that are just the aggregation alias or duplicated
    clean_cols: list[str] = []
    for col in select_cols:
        if col not in clean_cols:
            clean_cols.append(col)
    _add_node(
        OperationType.SELECT,
        DRGNodeParams(select_columns=clean_cols),
    )

    # 7. ORDER BY
    for ob in parsed.order_by:
        if ob["column"]:
            _add_node(
                OperationType.ORDER,
                DRGNodeParams(
                    sort_column=ob["column"],
                    sort_direction=_sort_direction(ob["direction"]),
                ),
            )

    # 8. LIMIT
    if parsed.limit is not None:
        _add_node(
            OperationType.LIMIT,
            DRGNodeParams(limit_value=parsed.limit),
        )

    return DatabaseReasoningGraph(nodes=nodes, edges=edges)


def sql_to_drg(sql: str, dialect: str = "sqlite") -> DatabaseReasoningGraph:
    """Parse SQL and convert directly to a DRG.

    Convenience function combining parse_sql and parsed_sql_to_drg.
    """
    from vgsr.drg.parser import parse_sql

    parsed = parse_sql(sql, dialect=dialect)
    return parsed_sql_to_drg(parsed)

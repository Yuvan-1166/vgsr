"""DRG structural and semantic validator.

Validates that a DatabaseReasoning Graph satisfies the composition constraints
defined in docs/02_METHOD_SPEC.md.
"""

from __future__ import annotations

from vgsr.models.drg import (
    AggregationFunction,
    DatabaseReasoningGraph,
    OperationType,
)
from vgsr.models.schema import DatabaseSchema
from vgsr.models.verification import (
    ErrorSeverity,
    VerificationError,
    VerificationLevel,
    VerificationResult,
)

# Valid operation ordering per the method spec:
# FROM -> WHERE* -> JOIN* -> GROUP? -> AGGREGATE* -> SELECT -> ORDER? -> LIMIT?
_VALID_ORDER: list[tuple[OperationType, str]] = [
    (OperationType.FROM, "1"),       # exactly once
    (OperationType.WHERE, "*"),      # zero or more
    (OperationType.JOIN, "*"),       # zero or more
    (OperationType.GROUP, "?"),      # zero or one
    (OperationType.AGGREGATE, "*"),  # zero or more
    (OperationType.SELECT, "1"),     # exactly once
    (OperationType.ORDER, "?"),      # zero or one
    (OperationType.LIMIT, "?"),      # zero or one
]

# Maps operation to its allowed position range
_OP_MIN_INDEX: dict[OperationType, int] = {}
_OP_MAX_INDEX: dict[OperationType, int] = {}

for i, (op, _card) in enumerate(_VALID_ORDER):
    _OP_MIN_INDEX[op] = i
    for j in range(i, len(_VALID_ORDER)):
        if _VALID_ORDER[j][0] == op:
            _OP_MAX_INDEX[op] = j
            break


def _get_op_index(op: OperationType) -> int:
    """Return the position index of an operation in the valid ordering."""
    for i, (valid_op, _) in enumerate(_VALID_ORDER):
        if valid_op == op:
            return i
    return -1


def validate_syntax(drg: DatabaseReasoningGraph) -> list[VerificationError]:
    """Level 1: Validate DRG graph structure and operation ordering."""
    errors: list[VerificationError] = []

    if not drg.nodes:
        errors.append(
            VerificationError(
                level=VerificationLevel.SYNTAX,
                error_type="empty_graph",
                message="DRG has no nodes",
            )
        )
        return errors

    # Check acyclicity via topological sort
    topo = drg.topological_sort()
    if len(topo) != len(drg.nodes):
        errors.append(
            VerificationError(
                level=VerificationLevel.SYNTAX,
                error_type="cycle_detected",
                message="DRG contains a cycle",
            )
        )
        return errors

    # Check FROM is first
    ops = drg.operation_sequence()
    if ops and ops[0] != OperationType.FROM:
        errors.append(
            VerificationError(
                level=VerificationLevel.SYNTAX,
                error_type="invalid_order",
                node_id=drg.nodes[0].id,
                message=f"First operation must be FROM, got {ops[0].value}",
                suggestions=["Move FROM to the beginning"],
            )
        )

    # Check SELECT exists
    if OperationType.SELECT not in ops:
        errors.append(
            VerificationError(
                level=VerificationLevel.SYNTAX,
                error_type="missing_mandatory",
                message="SELECT operation is missing",
                suggestions=["Add a SELECT node"],
            )
        )

    # Check FROM exists
    if OperationType.FROM not in ops:
        errors.append(
            VerificationError(
                level=VerificationLevel.SYNTAX,
                error_type="missing_mandatory",
                message="FROM operation is missing",
                suggestions=["Add a FROM node"],
            )
        )

    # Validate ordering constraints
    node_map = {n.id: n for n in drg.nodes}
    last_valid_index = -1
    for node_id in topo:
        if node_id not in node_map:
            continue
        node = node_map[node_id]
        op_index = _get_op_index(node.operation)
        if op_index == -1:
            errors.append(
                VerificationError(
                    level=VerificationLevel.SYNTAX,
                    error_type="unknown_operation",
                    node_id=node.id,
                    message=f"Unknown operation: {node.operation.value}",
                )
            )
            continue

        # Check max cardinality for single-occurrence operations
        op = node.operation
        card = None
        for valid_op, c in _VALID_ORDER:
            if valid_op == op:
                card = c
                break

        if card == "1":
            count = sum(1 for n in drg.nodes if n.operation == op)
            if count > 1:
                errors.append(
                    VerificationError(
                        level=VerificationLevel.SYNTAX,
                        error_type="duplicate_operation",
                        node_id=node.id,
                        message=f"Operation {op.value} must appear exactly once, found {count}",
                    )
                )

        if card == "?":
            count = sum(1 for n in drg.nodes if n.operation == op)
            if count > 1:
                errors.append(
                    VerificationError(
                        level=VerificationLevel.SYNTAX,
                        error_type="duplicate_operation",
                        node_id=node.id,
                        message=f"Operation {op.value} must appear at most once, found {count}",
                    )
                )

        last_valid_index = max(last_valid_index, op_index)

    # Check edge references
    node_ids = {n.id for n in drg.nodes}
    for edge in drg.edges:
        if edge.source not in node_ids:
            errors.append(
                VerificationError(
                    level=VerificationLevel.SYNTAX,
                    error_type="invalid_edge_source",
                    node_id=edge.source,
                    message=f"Edge references non-existent source node: {edge.source}",
                )
            )
        if edge.target not in node_ids:
            errors.append(
                VerificationError(
                    level=VerificationLevel.SYNTAX,
                    error_type="invalid_edge_target",
                    node_id=edge.target,
                    message=f"Edge references non-existent target node: {edge.target}",
                )
            )

    return errors


def validate_schema(drg: DatabaseReasoningGraph, schema: DatabaseSchema) -> list[VerificationError]:
    """Level 2: Validate that referenced entities exist in the database schema."""
    errors: list[VerificationError] = []

    for node in drg.nodes:
        params = node.params

        # Check FROM table
        if node.operation == OperationType.FROM and params.table and not schema.has_table(params.table):
            suggestions = [t for t in schema.all_table_names() if t.lower() == params.table.lower()]
            errors.append(
                VerificationError(
                    level=VerificationLevel.SCHEMA,
                    error_type="unknown_table",
                    node_id=node.id,
                    entity=params.table,
                    message=f"Table '{params.table}' not found in schema",
                    suggestions=suggestions,
                )
            )

        # Check JOIN table
        if node.operation == OperationType.JOIN and params.join_table and not schema.has_table(params.join_table):
            suggestions = [t for t in schema.all_table_names() if t.lower() == params.join_table.lower()]
            errors.append(
                VerificationError(
                    level=VerificationLevel.SCHEMA,
                    error_type="unknown_table",
                    node_id=node.id,
                    entity=params.join_table,
                    message=f"Table '{params.join_table}' not found in schema",
                    suggestions=suggestions,
                )
            )

        # Check columns
        table_for_col = params.table or params.table_alias
        if table_for_col and node.operation == OperationType.WHERE and params.column:
            table = schema.table_by_name(table_for_col)
            if table and not table.has_column(params.column):
                suggestions = [c.name for c in table.columns if params.column.lower() in c.name.lower()]
                errors.append(
                    VerificationError(
                        level=VerificationLevel.SCHEMA,
                        error_type="unknown_column",
                        node_id=node.id,
                        entity=params.column,
                        message=f"Column '{params.column}' not found in table '{table_for_col}'",
                        suggestions=suggestions,
                    )
                )

        # Check GROUP columns
        if node.operation == OperationType.GROUP and params.columns:
            for col in params.columns:
                if table_for_col:
                    table = schema.table_by_name(table_for_col)
                    if table and not table.has_column(col):
                        suggestions = [c.name for c in table.columns if col.lower() in c.name.lower()]
                        errors.append(
                            VerificationError(
                                level=VerificationLevel.SCHEMA,
                                error_type="unknown_column",
                                node_id=node.id,
                                entity=col,
                                message=f"Column '{col}' not found in table '{table_for_col}'",
                                suggestions=suggestions,
                            )
                        )

        # Check SELECT columns
        if node.operation == OperationType.SELECT and params.select_columns:
            for col in params.select_columns:
                if table_for_col and col != "*":
                    table = schema.table_by_name(table_for_col)
                    if table and not table.has_column(col):
                        suggestions = [c.name for c in table.columns if col.lower() in c.name.lower()]
                        errors.append(
                            VerificationError(
                                level=VerificationLevel.SCHEMA,
                                error_type="unknown_column",
                                node_id=node.id,
                                entity=col,
                                message=f"Column '{col}' not found in table '{table_for_col}'",
                                suggestions=suggestions,
                            )
                        )

        # Check AGGREGATE column type compatibility
        if node.operation == OperationType.AGGREGATE and params.function and params.aggregate_column:
            numeric_funcs = {AggregationFunction.SUM, AggregationFunction.AVG}
            if params.function in numeric_funcs and table_for_col:
                table = schema.table_by_name(table_for_col)
                if table:
                    col = table.column_by_name(params.aggregate_column)
                    if col and col.dtype.value not in ("INTEGER", "REAL"):
                        errors.append(
                            VerificationError(
                                level=VerificationLevel.SCHEMA,
                                error_type="type_mismatch",
                                node_id=node.id,
                                entity=params.aggregate_column,
                                message=(
                                    f"Aggregation {params.function.value} on non-numeric column "
                                    f"'{params.aggregate_column}' (type: {col.dtype.value})"
                                ),
                            )
                        )

    return errors


def validate_semantic(drg: DatabaseReasoningGraph) -> list[VerificationError]:
    """Level 3: Validate logical coherence of operations."""
    errors: list[VerificationError] = []
    ops = drg.operation_sequence()

    # GROUP-SELECT consistency: non-aggregated columns in SELECT must appear in GROUP
    if OperationType.GROUP in ops and OperationType.SELECT in ops:
        group_node = next(
            (n for n in drg.nodes if n.operation == OperationType.GROUP), None
        )
        select_node = next(
            (n for n in drg.nodes if n.operation == OperationType.SELECT), None
        )
        agg_node = next(
            (n for n in drg.nodes if n.operation == OperationType.AGGREGATE), None
        )

        if group_node and select_node and select_node.params.select_columns:
            group_cols = set(group_node.params.columns or [])
            agg_alias = agg_node.params.alias if agg_node and agg_node.params.alias else None

            for col in select_node.params.select_columns:
                if col == "*":
                    continue
                if col not in group_cols and col != agg_alias:
                    errors.append(
                        VerificationError(
                            level=VerificationLevel.SEMANTIC,
                            error_type="group_select_mismatch",
                            node_id=select_node.id,
                            entity=col,
                            message=(
                                f"Column '{col}' in SELECT is not in GROUP BY and is not aggregated"
                            ),
                            suggestions=[
                                f"Add '{col}' to GROUP BY or wrap in aggregation",
                            ],
                        )
                    )

    # WHERE before SELECT
    if OperationType.WHERE in ops and OperationType.SELECT in ops:
        where_idx = ops.index(OperationType.WHERE)
        select_idx = ops.index(OperationType.SELECT)
        if where_idx > select_idx:
            errors.append(
                VerificationError(
                    level=VerificationLevel.SEMANTIC,
                    error_type="operation_ordering",
                    message="WHERE appears after SELECT, which is unusual",
                    suggestions=["Move WHERE before SELECT"],
                )
            )

    # JOIN should have join parameters
    for node in drg.nodes:
        if node.operation == OperationType.JOIN and not node.params.join_table:
            errors.append(
                VerificationError(
                    level=VerificationLevel.SEMANTIC,
                    error_type="missing_join_target",
                    node_id=node.id,
                    message="JOIN node has no join_table specified",
                )
            )

    return errors


def validate_drg(
    drg: DatabaseReasoningGraph,
    schema: DatabaseSchema | None = None,
    check_syntax: bool = True,
    check_schema: bool = True,
    check_semantic: bool = True,
) -> VerificationResult:
    """Run all applicable verification levels and return aggregate result.

    Args:
        drg: The DRG to validate.
        schema: Optional database schema for schema-level checks.
        check_syntax: Whether to run syntax verification.
        check_schema: Whether to run schema verification.
        check_semantic: Whether to run semantic verification.

    Returns:
        VerificationResult with all detected errors.
    """
    all_errors: list[VerificationError] = []
    highest_level = VerificationLevel.SYNTAX

    if check_syntax:
        all_errors.extend(validate_syntax(drg))

    if check_schema and schema:
        all_errors.extend(validate_schema(drg, schema))
        if len(all_errors) == 0 or any(e.level == VerificationLevel.SCHEMA for e in all_errors):
            highest_level = VerificationLevel.SCHEMA

    if check_semantic:
        all_errors.extend(validate_semantic(drg))
        if any(e.level == VerificationLevel.SEMANTIC for e in all_errors):
            highest_level = VerificationLevel.SEMANTIC

    has_errors = any(e.severity == ErrorSeverity.ERROR for e in all_errors)

    return VerificationResult(
        valid=not has_errors,
        errors=all_errors,
        level=highest_level,
    )

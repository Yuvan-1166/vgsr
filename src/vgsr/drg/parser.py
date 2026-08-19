"""SQL parser using sqlglot.

Parses SQL strings into structured intermediate representations that can be
converted into Database Reasoning Graphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sqlglot
import sqlglot.expressions as exp


@dataclass
class ParsedJoin:
    """A parsed JOIN clause."""

    table: str
    alias: str
    join_type: str = "INNER"
    on_left: str = ""
    on_right: str = ""


@dataclass
class ParsedWhereCondition:
    """A single WHERE condition."""

    column: str
    operator: str
    value: Any = None
    values: list[Any] = field(default_factory=list)


@dataclass
class ParsedSQL:
    """Structured representation of a parsed SQL SELECT statement.

    Extracts the key components needed for DRG conversion.
    """

    select_columns: list[str] = field(default_factory=list)
    select_aliases: list[str] = field(default_factory=list)
    from_table: str = ""
    from_alias: str = ""
    joins: list[ParsedJoin] = field(default_factory=list)
    where_conditions: list[ParsedWhereCondition] = field(default_factory=list)
    group_by_columns: list[str] = field(default_factory=list)
    aggregations: list[dict[str, str]] = field(default_factory=list)
    order_by: list[dict[str, str]] = field(default_factory=list)
    limit: int | None = None
    raw_sql: str = ""

    def is_valid(self) -> bool:
        """Check if the parsed SQL has at minimum a FROM clause."""
        return bool(self.from_table)


def _normalize_col_ref(col_str: str) -> str:
    """Strip table aliases from column references: 'e.salary' -> 'salary'."""
    if "." in col_str:
        return col_str.split(".")[-1]
    return col_str


def _extract_literal_value(expr: exp.Expression) -> Any:
    """Extract a Python value from a sqlglot literal expression."""
    if isinstance(expr, exp.Literal):
        if expr.is_string:
            return expr.this.strip("'").strip('"')
        try:
            return int(expr.this)
        except ValueError:
            try:
                return float(expr.this)
            except ValueError:
                return expr.this
    if isinstance(expr, exp.Null):
        return None
    if isinstance(expr, exp.Neg) and isinstance(expr.this, exp.Literal):
        val = _extract_literal_value(expr.this)
        if isinstance(val, (int, float)):
            return -val
    return expr.sql()


def _parse_condition(condition: exp.Expression) -> ParsedWhereCondition:
    """Parse a single WHERE condition expression."""
    if isinstance(condition, exp.EQ):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator="=",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.NEQ):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator="!=",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.GT):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator=">",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.GTE):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator=">=",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.LT):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator="<",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.LTE):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator="<=",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.In):
        col = _normalize_col_ref(condition.left.sql())
        vals = [_extract_literal_value(e) for e in condition.expressions]
        return ParsedWhereCondition(column=col, operator="IN", values=vals)
    if isinstance(condition, exp.Like):
        return ParsedWhereCondition(
            column=_normalize_col_ref(condition.left.sql()),
            operator="LIKE",
            value=_extract_literal_value(condition.right),
        )
    if isinstance(condition, exp.Between):
        col = _normalize_col_ref(condition.this.sql())
        low = _extract_literal_value(condition.args["low"])
        high = _extract_literal_value(condition.args["high"])
        return ParsedWhereCondition(
            column=col, operator="BETWEEN", values=[low, high]
        )
    # Fallback: store raw
    return ParsedWhereCondition(
        column="",
        operator="EXPRESSION",
        value=condition.sql(),
    )


def _collect_conditions(expr: exp.Expression) -> list[ParsedWhereCondition]:
    """Recursively collect conditions from AND/OR trees."""
    if isinstance(expr, exp.And):
        return _collect_conditions(expr.left) + _collect_conditions(expr.right)
    if isinstance(expr, exp.Or):
        # OR conditions treated as a single expression-level condition
        return [ParsedWhereCondition(column="", operator="OR", value=expr.sql())]
    return [_parse_condition(expr)]


def parse_sql(sql: str, dialect: str = "sqlite") -> ParsedSQL:
    """Parse a SQL SELECT statement into a ParsedSQL structure.

    Args:
        sql: SQL SELECT string.
        dialect: sqlglot dialect (default: sqlite).

    Returns:
        ParsedSQL with extracted components.
    """
    try:
        parsed = sqlglot.parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError:
        return ParsedSQL(raw_sql=sql)

    if not isinstance(parsed, exp.Select):
        return ParsedSQL(raw_sql=sql)

    result = ParsedSQL(raw_sql=sql)

    # SELECT columns
    for expr in parsed.expressions:
        if isinstance(expr, exp.Alias):
            col = expr.this.sql()
            alias = expr.alias
            if isinstance(expr.this, exp.AggFunc):
                col_node = expr.this.find(exp.Column)
                result.aggregations.append(
                    {
                        "function": type(expr.this).__name__,
                        "column": _normalize_col_ref(col_node.sql()) if col_node else "",
                        "alias": alias,
                    }
                )
            # For aggregations, use alias as the select column reference
            if isinstance(expr.this, exp.AggFunc) and alias:
                result.select_columns.append(alias)
            else:
                result.select_columns.append(_normalize_col_ref(col))
            result.select_aliases.append(alias)
        elif isinstance(expr, exp.Column):
            result.select_columns.append(_normalize_col_ref(expr.sql()))
            result.select_aliases.append("")
        elif isinstance(expr, exp.Star):
            result.select_columns.append("*")
            result.select_aliases.append("")
        else:
            result.select_columns.append(_normalize_col_ref(expr.sql()))
            result.select_aliases.append("")

    # FROM
    from_expr = parsed.find(exp.From)
    if from_expr and from_expr.this:
        table_expr = from_expr.this
        if isinstance(table_expr, exp.Table):
            result.from_table = table_expr.name
            result.from_alias = table_expr.alias
        elif isinstance(table_expr, exp.Alias):
            result.from_table = table_expr.this.name if isinstance(table_expr.this, exp.Table) else table_expr.sql()
            result.from_alias = table_expr.alias

    # JOINs
    for join in parsed.find_all(exp.Join):
        jtable = join.find(exp.Table)
        if jtable:
            on_expr = join.args.get("on")
            left_col = ""
            right_col = ""
            if on_expr and isinstance(on_expr, exp.EQ):
                left_col = _normalize_col_ref(on_expr.left.sql())
                right_col = _normalize_col_ref(on_expr.right.sql())
            result.joins.append(
                ParsedJoin(
                    table=jtable.name,
                    alias=jtable.alias or jtable.name,
                    join_type=join.args.get("side") or "INNER",
                    on_left=left_col,
                    on_right=right_col,
                )
            )

    # WHERE
    where_expr = parsed.find(exp.Where)
    if where_expr and where_expr.this:
        result.where_conditions = _collect_conditions(where_expr.this)

    # GROUP BY
    group_expr = parsed.find(exp.Group)
    if group_expr:
        for col in group_expr.expressions:
            result.group_by_columns.append(_normalize_col_ref(col.sql()))

    # ORDER BY
    order_expr = parsed.find(exp.Order)
    if order_expr:
        for o in order_expr.expressions:
            is_desc = o.args.get("desc", False)
            direction = "DESC" if is_desc else "ASC"
            col = _normalize_col_ref(o.this.sql()) if o.this else ""
            result.order_by.append({"column": col, "direction": direction})

    # LIMIT
    limit_expr = parsed.find(exp.Limit)
    if limit_expr and limit_expr.expression:
        try:
            result.limit = int(limit_expr.expression.this)
        except (ValueError, AttributeError):
            pass

    return result

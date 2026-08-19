"""Database schema representation models.

Provides a normalized, database-agnostic schema format used across all
components (DRG, translators, verifiers, evaluation).
"""

from __future__ import annotations

import enum

from pydantic import BaseModel, Field


class ColumnType(str, enum.Enum):
    """Supported column data types."""

    TEXT = "TEXT"
    INTEGER = "INTEGER"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DATETIME = "DATETIME"
    BLOB = "BLOB"


class Column(BaseModel):
    """A single column/field in a table or collection."""

    name: str = Field(description="Column name")
    dtype: ColumnType = Field(default=ColumnType.TEXT, description="Data type")
    primary_key: bool = Field(default=False, description="Whether this column is a primary key")
    nullable: bool = Field(default=True, description="Whether NULL is allowed")
    description: str | None = Field(default=None, description="Human-readable description")

    model_config = {"extra": "forbid"}


class ForeignKey(BaseModel):
    """A foreign key constraint between two tables."""

    columns: list[str] = Field(description="Columns in this table")
    ref_table: str = Field(description="Referenced table name")
    ref_columns: list[str] = Field(description="Referenced columns")

    model_config = {"extra": "forbid"}


class Table(BaseModel):
    """A table or collection definition within a database schema."""

    name: str = Field(description="Table/collection name")
    columns: list[Column] = Field(default_factory=list)
    foreign_keys: list[ForeignKey] = Field(default_factory=list)
    description: str | None = Field(default=None)

    model_config = {"extra": "forbid"}

    def column_by_name(self, name: str) -> Column | None:
        """Look up a column by name (case-insensitive)."""
        lower = name.lower()
        for col in self.columns:
            if col.name.lower() == lower:
                return col
        return None

    def has_column(self, name: str) -> bool:
        """Check if a column exists (case-insensitive)."""
        return self.column_by_name(name) is not None


class DatabaseSchema(BaseModel):
    """Complete database schema used for a set of queries.

    Encompasses all tables, their columns, relationships, and metadata.
    """

    database_id: str = Field(description="Unique database identifier")
    database_type: str = Field(default="sql", description="Database paradigm: sql, mongodb, neo4j")
    tables: list[Table] = Field(default_factory=list)
    description: str | None = Field(default=None)

    model_config = {"extra": "forbid"}

    def table_by_name(self, name: str) -> Table | None:
        """Look up a table by name (case-insensitive)."""
        lower = name.lower()
        for table in self.tables:
            if table.name.lower() == lower:
                return table
        return None

    def has_table(self, name: str) -> bool:
        """Check if a table exists."""
        return self.table_by_name(name) is not None

    def all_table_names(self) -> list[str]:
        """Return all table names."""
        return [t.name for t in self.tables]

    def all_columns_for_table(self, table_name: str) -> list[str]:
        """Return column names for a given table."""
        table = self.table_by_name(table_name)
        if table is None:
            return []
        return [c.name for c in table.columns]

    def to_prompt_text(self) -> str:
        """Render schema as a compact text suitable for LLM prompts."""
        lines: list[str] = []
        for table in self.tables:
            col_parts = []
            for col in table.columns:
                pk = " PRIMARY KEY" if col.primary_key else ""
                col_parts.append(f"  {col.name} {col.dtype.value}{pk}")
            cols_str = "\n".join(col_parts)
            lines.append(f"TABLE {table.name} (\n{cols_str}\n)")
        return "\n\n".join(lines)

    @classmethod
    def from_spider(cls, db_id: str, table_names: list[str], column_names: list[list[str]], column_types: list[str]) -> DatabaseSchema:
        """Build a DatabaseSchema from Spider-format metadata.

        Args:
            db_id: Database identifier.
            table_names: List of table names.
            column_names: For each column: [table_name, column_name].
            column_types: For each column: a type string (text/number/etc).
        """
        type_map: dict[str, ColumnType] = {
            "text": ColumnType.TEXT,
            "number": ColumnType.REAL,
            "integer": ColumnType.INTEGER,
            "boolean": ColumnType.BOOLEAN,
            "date": ColumnType.DATE,
            "time": ColumnType.DATETIME,
            "others": ColumnType.BLOB,
        }
        tables: dict[str, list[Column]] = {name: [] for name in table_names}
        for (tbl, col), ctype in zip(column_names, column_types):
            if tbl in tables:
                tables[tbl].append(
                    Column(
                        name=col,
                        dtype=type_map.get(ctype.lower(), ColumnType.TEXT),
                    )
                )
        return cls(
            database_id=db_id,
            tables=[Table(name=tname, columns=cols) for tname, cols in tables.items()],
        )

"""Spring Boot CRUD project generator."""

from .generator import (
    ColumnDefinition,
    SpringBootCrudGenerator,
    TableDefinition,
    table_definition_from_connection,
)

__all__ = [
    "ColumnDefinition",
    "SpringBootCrudGenerator",
    "TableDefinition",
    "table_definition_from_connection",
]

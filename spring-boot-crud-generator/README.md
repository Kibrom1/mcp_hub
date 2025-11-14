# Spring Boot CRUD Generator

A small Python library that produces a ready-to-run Spring Boot CRUD project
from a structured table definition. The generator creates a Maven project with
an entity, repository, service, and controller layer wired together for a
single table.

## Features

- Validates table metadata and primary keys before generation.
- Creates a Maven project layout with an application entry point.
- Generates Spring Data JPA repository, service, and REST controller classes.
- Supports common SQL types with sensible Java type mappings.

## Usage

```python
from pathlib import Path
from spring_boot_crud_generator import (
    ColumnDefinition,
    SpringBootCrudGenerator,
    TableDefinition,
)

columns = [
    ColumnDefinition(name="id", data_type="bigint", primary_key=True),
    ColumnDefinition(name="name", data_type="varchar", nullable=False, length=255),
]

generator = SpringBootCrudGenerator(
    base_package="com.example.demo",
    table=TableDefinition(name="customer", columns=columns),
)

generator.generate(Path("./customer-crud"), overwrite=True)
```

## Development

Create a virtual environment and install dependencies using `pip` and the
included `pyproject.toml`. Run tests with `pytest`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

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

### Using the generator from another service

If you want to call the generator from an existing service (for example a
FastAPI or Flask application that exposes a CRUD scaffolding endpoint), install
this package as a dependency and reuse the same API that is shown above.

```bash
pip install spring-boot-crud-generator
```

Inside your service you can wrap the generator call in whatever orchestration
logic you need. Below is a simplified FastAPI example that accepts table
metadata over HTTP, generates the Spring Boot project on demand, and streams it
back as a zip file.

```python
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from spring_boot_crud_generator import (
    ColumnDefinition,
    SpringBootCrudGenerator,
    TableDefinition,
)
import shutil
import tempfile

app = FastAPI()


@app.post("/generate-crud")
async def generate_crud(table: dict) -> Response:
    try:
        columns = [
            ColumnDefinition(**column)
            for column in table["columns"]
        ]
        generator = SpringBootCrudGenerator(
            base_package=table["base_package"],
            table=TableDefinition(name=table["name"], columns=columns),
        )
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing field: {exc}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / table["name"]
        generator.generate(output_dir, overwrite=True)

        buffer = BytesIO()
        archive_path = shutil.make_archive(str(output_dir), "zip", output_dir)
        buffer.write(Path(archive_path).read_bytes())

    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=crud.zip"},
    )
```

Your service can adjust validation, authentication, and storage as needed while
delegating the Spring Boot project generation to this package.

## Development

Create a virtual environment and install dependencies using `pip` and the
included `pyproject.toml`. Run tests with `pytest`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

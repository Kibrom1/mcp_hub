from pathlib import Path

import pytest

from app.services.spring_boot_crud_generator import (
    ColumnDefinition,
    SpringBootCrudGenerator,
    TableDefinition,
)


def test_generate_crud_project(tmp_path: Path) -> None:
    table = TableDefinition(
        name="user_account",
        columns=[
            ColumnDefinition(name="id", data_type="bigint", primary_key=True, nullable=False),
            ColumnDefinition(name="email", data_type="varchar", length=120, unique=True, nullable=False),
            ColumnDefinition(name="created_at", data_type="timestamp", nullable=False),
        ],
    )

    generator = SpringBootCrudGenerator(
        base_package="com.example.demo",
        table=table,
        project_name="UserAccount",
    )

    generator.generate(tmp_path)

    project_root = tmp_path
    entity_file = project_root / "src" / "main" / "java" / "com" / "example" / "demo" / "entity" / "UserAccount.java"
    controller_file = project_root / "src" / "main" / "java" / "com" / "example" / "demo" / "controller" / "UserAccountController.java"
    pom_file = project_root / "pom.xml"

    assert entity_file.exists()
    assert controller_file.exists()
    assert pom_file.exists()

    entity_contents = entity_file.read_text(encoding="utf-8")
    controller_contents = controller_file.read_text(encoding="utf-8")

    assert "@Entity" in entity_contents
    assert "@Table(name = \"user_account\")" in entity_contents
    assert "private Long id;" in entity_contents
    assert "public Long getId()" in entity_contents

    assert "@RestController" in controller_contents
    assert "@RequestMapping(\"/api/user-account\")" in controller_contents
    assert "getById(@PathVariable Long id)" in controller_contents
    assert "delete(@PathVariable Long id)" in controller_contents


@pytest.mark.parametrize(
    "table, expected_error",
    [
        (TableDefinition(name="empty", columns=[]), "table must contain at least one column"),
        (
            TableDefinition(
                name="no_pk",
                columns=[ColumnDefinition(name="id", data_type="bigint")],
            ),
            "table must define at least one primary key column",
        ),
    ],
)
def test_generator_validation(table: TableDefinition, expected_error: str) -> None:
    with pytest.raises(ValueError) as exc:
        SpringBootCrudGenerator(base_package="com.example.demo", table=table)
    assert expected_error in str(exc.value)

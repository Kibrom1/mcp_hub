"""Utilities for generating Spring Boot CRUD scaffolding from table definitions.

This module exposes a high-level :class:`SpringBootCrudGenerator` that can take a
:class:`TableDefinition` and write a minimal Spring Boot CRUD project structure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


JAVA_TYPE_DEFAULTS: Dict[str, Tuple[str, Optional[str]]] = {
    "bigdecimal": ("BigDecimal", "java.math.BigDecimal"),
    "bigint": ("Long", None),
    "boolean": ("Boolean", None),
    "date": ("LocalDate", "java.time.LocalDate"),
    "datetime": ("LocalDateTime", "java.time.LocalDateTime"),
    "double": ("Double", None),
    "float": ("Float", None),
    "integer": ("Integer", None),
    "int": ("Integer", None),
    "long": ("Long", None),
    "numeric": ("BigDecimal", "java.math.BigDecimal"),
    "smallint": ("Short", None),
    "text": ("String", None),
    "time": ("LocalTime", "java.time.LocalTime"),
    "timestamp": ("Instant", "java.time.Instant"),
    "uuid": ("UUID", "java.util.UUID"),
    "varchar": ("String", None),
}


@dataclass
class ColumnDefinition:
    """Represents a column in a database table."""

    name: str
    data_type: str
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    length: Optional[int] = None
    java_type: Optional[str] = None
    java_import: Optional[str] = None
    annotations: Sequence[str] = field(default_factory=tuple)

    def resolved_java_type(self) -> Tuple[str, Optional[str]]:
        """Return the Java type and optional import for this column."""

        if self.java_type:
            return self.java_type, self.java_import

        default = JAVA_TYPE_DEFAULTS.get(self.data_type.lower())
        if default:
            return default

        # fall back to raw data type as a Java class name
        return self.data_type, None


@dataclass
class TableDefinition:
    """Container describing a database table."""

    name: str
    columns: List[ColumnDefinition]

    def primary_key_columns(self) -> List[ColumnDefinition]:
        return [column for column in self.columns if column.primary_key]


class SpringBootCrudGenerator:
    """Generate Spring Boot CRUD projects from table definitions."""

    def __init__(
        self,
        base_package: str,
        table: TableDefinition,
        project_name: Optional[str] = None,
    ) -> None:
        if not base_package:
            raise ValueError("base_package is required")
        if not table.columns:
            raise ValueError("table must contain at least one column")
        if not table.primary_key_columns():
            raise ValueError("table must define at least one primary key column")

        self.base_package = base_package
        self.table = table
        self.project_name = project_name or f"{self._pascal_case(table.name)}Crud"

    @classmethod
    def from_connection(
        cls,
        base_package: str,
        connection: Any,
        table_name: str,
        project_name: Optional[str] = None,
    ) -> "SpringBootCrudGenerator":
        """Construct a generator by introspecting a database table.

        Args:
            base_package: Java package for the generated project.
            connection: A DB-API compatible connection object.
            table_name: Name of the table to introspect.
            project_name: Optional custom project name.

        Returns:
            A :class:`SpringBootCrudGenerator` instance configured with a
            :class:`TableDefinition` derived from the live database schema.
        """

        table_definition = table_definition_from_connection(connection, table_name)
        return cls(
            base_package=base_package,
            table=table_definition,
            project_name=project_name,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self, output_directory: Path | str, overwrite: bool = False) -> None:
        """Generate the project structure inside ``output_directory``.

        Args:
            output_directory: Directory where the project will be written.
            overwrite: Whether to overwrite existing files. If ``False`` and a
                file already exists, a :class:`FileExistsError` is raised.
        """

        project_root = Path(output_directory).resolve()
        src_main_java = project_root / "src" / "main" / "java"
        src_main_resources = project_root / "src" / "main" / "resources"

        package_path = Path(*self.base_package.split("."))
        java_root = src_main_java / package_path
        entity_dir = java_root / "entity"
        repository_dir = java_root / "repository"
        service_dir = java_root / "service"
        controller_dir = java_root / "controller"

        for directory in [
            project_root,
            src_main_java,
            src_main_resources,
            java_root,
            entity_dir,
            repository_dir,
            service_dir,
            controller_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        files_to_render = {
            project_root / "pom.xml": self._generate_pom_xml(),
            java_root / f"{self.project_name}Application.java": self._generate_application_class(),
            entity_dir / f"{self._entity_class_name()}.java": self._generate_entity_class(),
            repository_dir / f"{self._entity_class_name()}Repository.java": self._generate_repository_interface(),
            service_dir / f"{self._entity_class_name()}Service.java": self._generate_service_class(),
            controller_dir / f"{self._entity_class_name()}Controller.java": self._generate_controller_class(),
            src_main_resources / "application.properties": self._generate_application_properties(),
        }

        for path, content in files_to_render.items():
            if path.exists() and not overwrite:
                raise FileExistsError(f"{path} already exists. Use overwrite=True to replace it.")
            path.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # File generators
    # ------------------------------------------------------------------
    def _generate_pom_xml(self) -> str:
        return f"""<project xmlns=\"http://maven.apache.org/POM/4.0.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
    xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd\">
    <modelVersion>4.0.0</modelVersion>
    <groupId>{self.base_package}</groupId>
    <artifactId>{self.project_name.lower()}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>{self.project_name}</name>
    <description>CRUD service for {self.table.name}</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""

    def _generate_application_class(self) -> str:
        class_name = f"{self.project_name}Application"
        return f"""package {self.base_package};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {class_name} {{

    public static void main(String[] args) {{
        SpringApplication.run({class_name}.class, args);
    }}
}}
"""

    def _generate_entity_class(self) -> str:
        lines = [
            f"package {self.base_package}.entity;\n",
            "import jakarta.persistence.*;\n",
        ]

        imports = self._collect_entity_imports()
        if imports:
            lines.extend(sorted({f"import {imp};\n" for imp in imports if imp}))

        lines.append("\n@Entity\n")
        lines.append(f"@Table(name = \"{self.table.name}\")\n")
        lines.append(f"public class {self._entity_class_name()} {{\n\n")

        for column in self.table.columns:
            lines.extend(self._generate_column_declaration(column))

        lines.append("}\n")
        return "".join(lines)

    def _collect_entity_imports(self) -> Iterable[str | None]:
        for column in self.table.columns:
            java_type, java_import = column.resolved_java_type()
            if java_import:
                yield java_import

    def _generate_column_declaration(self, column: ColumnDefinition) -> List[str]:
        annotations = list(column.annotations)
        if column.primary_key:
            annotations.insert(0, "@Id")
            annotations.insert(1, "@GeneratedValue(strategy = GenerationType.IDENTITY)")
        if column.unique:
            annotations.append("@Column(unique = true)")
        elif column.nullable:
            annotations.append("@Column(nullable = true)")

        if column.length is not None:
            annotations.append(f"@Column(length = {column.length})")

        java_type, _ = column.resolved_java_type()
        field_declaration = f"    private {java_type} {column.name};\n\n"

        return [f"    {annotation}\n" for annotation in annotations] + [field_declaration]

    def _generate_repository_interface(self) -> str:
        entity_class = self._entity_class_name()
        pk_types = self._primary_key_java_types()
        if len(pk_types) > 1:
            raise NotImplementedError("Composite primary keys are not supported yet")
        pk_type = pk_types[0]

        return f"""package {self.base_package}.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import {self.base_package}.entity.{entity_class};

public interface {entity_class}Repository extends JpaRepository<{entity_class}, {pk_type}> {{
}}
"""

    def _generate_service_class(self) -> str:
        entity_class = self._entity_class_name()
        pk_types = self._primary_key_java_types()
        if len(pk_types) > 1:
            raise NotImplementedError("Composite primary keys are not supported yet")
        pk_type = pk_types[0]

        return f"""package {self.base_package}.service;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import {self.base_package}.entity.{entity_class};
import {self.base_package}.repository.{entity_class}Repository;

@Service
public class {entity_class}Service {{

    private final {entity_class}Repository repository;

    public {entity_class}Service({entity_class}Repository repository) {{
        this.repository = repository;
    }}

    public {entity_class} create({entity_class} entity) {{
        return repository.save(entity);
    }}

    public List<{entity_class}> findAll() {{
        return repository.findAll();
    }}

    public Optional<{entity_class}> findById({pk_type} id) {{
        return repository.findById(id);
    }}

    public {entity_class} update({entity_class} entity) {{
        return repository.save(entity);
    }}

    public void deleteById({pk_type} id) {{
        repository.deleteById(id);
    }}
}}
"""

    def _generate_controller_class(self) -> str:
        entity_class = self._entity_class_name()
        pk_types = self._primary_key_java_types()
        if len(pk_types) > 1:
            raise NotImplementedError("Composite primary keys are not supported yet")
        pk_type = pk_types[0]

        return f"""package {self.base_package}.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import {self.base_package}.entity.{entity_class};
import {self.base_package}.service.{entity_class}Service;

@RestController
@RequestMapping("/api/{self.table.name}")
public class {entity_class}Controller {{

    private final {entity_class}Service service;

    public {entity_class}Controller({entity_class}Service service) {{
        this.service = service;
    }}

    @PostMapping
    public ResponseEntity<{entity_class}> create(@RequestBody {entity_class} entity) {{
        return ResponseEntity.ok(service.create(entity));
    }}

    @GetMapping
    public ResponseEntity<List<{entity_class}>> findAll() {{
        return ResponseEntity.ok(service.findAll());
    }}

    @GetMapping("/{'{'}id{'}'}")
    public ResponseEntity<{entity_class}> findById(@PathVariable {pk_type} id) {{
        return service.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }}

    @PutMapping
    public ResponseEntity<{entity_class}> update(@RequestBody {entity_class} entity) {{
        return ResponseEntity.ok(service.update(entity));
    }}

    @DeleteMapping("/{'{'}id{'}'}")
    public ResponseEntity<Void> deleteById(@PathVariable {pk_type} id) {{
        service.deleteById(id);
        return ResponseEntity.noContent().build();
    }}
}}
"""

    def _generate_application_properties(self) -> str:
        return """spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

spring.jpa.hibernate.ddl-auto=update
spring.h2.console.enabled=true
"""

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _entity_class_name(self) -> str:
        return self._pascal_case(self.table.name)

    def _pascal_case(self, name: str) -> str:
        return "".join(part.capitalize() for part in name.replace("_", " ").split())

    def _primary_key_java_types(self) -> List[str]:
        java_types = []
        for column in self.table.primary_key_columns():
            java_type, _ = column.resolved_java_type()
            java_types.append(java_type)
        return java_types


def table_definition_from_connection(connection: Any, table_name: str) -> TableDefinition:
    """Build a :class:`TableDefinition` by introspecting a live database table.

    The current implementation supports :mod:`sqlite3` connections. A
    :class:`TypeError` is raised if the provided connection type is not
    supported.
    """

    module_name = type(connection).__module__
    if module_name.startswith("sqlite3"):
        return _table_definition_from_sqlite(connection, table_name)

    raise TypeError(
        "Unsupported connection type. Only sqlite3 connections are currently supported."
    )


def _table_definition_from_sqlite(connection: Any, table_name: str) -> TableDefinition:
    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"Table '{table_name}' does not exist or has no columns")

    unique_columns: set[str] = set()
    index_cursor = connection.execute(f"PRAGMA index_list({table_name})")
    for _, index_name, index_unique, *_ in index_cursor.fetchall():
        if bool(index_unique):
            info_cursor = connection.execute(f"PRAGMA index_info({index_name})")
            for _, _, column_name in info_cursor.fetchall():
                unique_columns.add(column_name)

    columns: List[ColumnDefinition] = []
    for _, name, col_type, notnull, _, pk in rows:
        base_type, length = _parse_sqlite_type(col_type)
        is_nullable = not bool(notnull)
        if pk:
            is_nullable = False
        columns.append(
            ColumnDefinition(
                name=name,
                data_type=base_type,
                primary_key=bool(pk),
                nullable=is_nullable,
                unique=name in unique_columns,
                length=length,
            )
        )

    return TableDefinition(name=table_name, columns=columns)


def _parse_sqlite_type(col_type: Optional[str]) -> Tuple[str, Optional[int]]:
    if not col_type:
        return "text", None

    match = re.match(r"^(?P<type>[a-zA-Z]+)(?:\((?P<length>\d+)\))?", col_type.strip())
    if not match:
        return col_type.lower(), None

    base_type = match.group("type").lower()
    length_str = match.group("length")
    length = int(length_str) if length_str else None
    return base_type, length


__all__ = [
    "ColumnDefinition",
    "SpringBootCrudGenerator",
    "TableDefinition",
    "table_definition_from_connection",
]

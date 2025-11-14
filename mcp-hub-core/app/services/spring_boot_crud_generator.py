"""Utilities for generating Spring Boot CRUD scaffolding from table definitions.

This module exposes a high-level :class:`SpringBootCrudGenerator` that can take a
:class:`TableDefinition` and write a minimal Spring Boot CRUD project structure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


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
        return f"""package {self.base_package};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {self.project_name}Application {{

    public static void main(String[] args) {{
        SpringApplication.run({self.project_name}Application.class, args);
    }}
}}
"""

    def _generate_entity_class(self) -> str:
        imports = {
            "jakarta.persistence.*",
        }

        field_declarations = []
        getter_setters = []
        for column in self.table.columns:
            java_type, java_import = column.resolved_java_type()
            if java_import:
                imports.add(java_import)

            annotations = list(column.annotations)
            if column.primary_key:
                annotations.append("@Id")
                if java_type in {"Long", "Integer", "Short"}:
                    annotations.append("@GeneratedValue(strategy = GenerationType.IDENTITY)")
                    imports.add("jakarta.persistence.GenerationType")
            column_annotations = self._column_annotation(column)
            if column_annotations:
                annotations.append(column_annotations)

            annotation_block = "\n    ".join(annotations)
            if annotation_block:
                annotation_block = f"    {annotation_block}\n"

            field_declarations.append(
                f"{annotation_block}    private {java_type} {self._camel_case(column.name)};"
            )

            getter_setters.extend(
                self._generate_getter_setter(java_type, self._camel_case(column.name))
            )

        imports_text = "\n".join(f"import {imp};" for imp in sorted(imports))
        class_body = "\n\n".join(field_declarations + getter_setters)

        return f"""package {self.base_package}.entity;

{imports_text}

@Entity
@Table(name = \"{self.table.name}\")
public class {self._entity_class_name()} {{

{class_body}
}}
"""

    def _generate_repository_interface(self) -> str:
        pk_type, _ = self.table.primary_key_columns()[0].resolved_java_type()
        return f"""package {self.base_package}.repository;

import {self.base_package}.entity.{self._entity_class_name()};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {self._entity_class_name()}Repository extends JpaRepository<{self._entity_class_name()}, {pk_type}> {{
}}
"""

    def _generate_service_class(self) -> str:
        entity_name = self._entity_class_name()
        pk_type, _ = self.table.primary_key_columns()[0].resolved_java_type()
        return f"""package {self.base_package}.service;

import {self.base_package}.entity.{entity_name};
import {self.base_package}.repository.{entity_name}Repository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class {entity_name}Service {{

    private final {entity_name}Repository repository;

    public {entity_name}Service({entity_name}Repository repository) {{
        this.repository = repository;
    }}

    public List<{entity_name}> findAll() {{
        return repository.findAll();
    }}

    public Optional<{entity_name}> findById({pk_type} id) {{
        return repository.findById(id);
    }}

    public {entity_name} save({entity_name} entity) {{
        return repository.save(entity);
    }}

    public void deleteById({pk_type} id) {{
        repository.deleteById(id);
    }}
}}
"""

    def _generate_controller_class(self) -> str:
        entity_name = self._entity_class_name()
        pk_column = self.table.primary_key_columns()[0]
        pk_type, _ = pk_column.resolved_java_type()
        pk_field = self._camel_case(pk_column.name)
        pk_pascal = pk_field[0].upper() + pk_field[1:]
        variable_name = self._camel_case(entity_name)
        lines = [
            f"package {self.base_package}.controller;",
            "",
            f"import {self.base_package}.entity.{entity_name};",
            f"import {self.base_package}.service.{entity_name}Service;",
            "import org.springframework.http.ResponseEntity;",
            "import org.springframework.web.bind.annotation.*;",
            "",
            "import java.util.List;",
            "",
            "@RestController",
            f'@RequestMapping("/api/{self._kebab_case(entity_name)}")',
            f"public class {entity_name}Controller {{",
            "",
            f"    private final {entity_name}Service service;",
            "",
            f"    public {entity_name}Controller({entity_name}Service service) {{",
            "        this.service = service;",
            "    }",
            "",
            "    @GetMapping",
            f"    public List<{entity_name}> getAll() {{",
            "        return service.findAll();",
            "    }",
            "",
            f'    @GetMapping("/{pk_field}")',
            f"    public ResponseEntity<{entity_name}> getById(@PathVariable {pk_type} {pk_field}) {{",
            f"        return service.findById({pk_field})",
            "            .map(ResponseEntity::ok)",
            "            .orElseGet(() -> ResponseEntity.notFound().build());",
            "    }",
            "",
            "    @PostMapping",
            f"    public {entity_name} create(@RequestBody {entity_name} {variable_name}) {{",
            f"        return service.save({variable_name});",
            "    }",
            "",
            f'    @PutMapping("/{pk_field}")',
            f"    public ResponseEntity<{entity_name}> update(",
            f"            @PathVariable {pk_type} {pk_field},",
            f"            @RequestBody {entity_name} {variable_name}) {{",
            f"        return service.findById({pk_field})",
            "            .map(existing -> {",
            f"                {variable_name}.set{pk_pascal}(existing.get{pk_pascal}());",
            f"                return ResponseEntity.ok(service.save({variable_name}));",
            "            })",
            "            .orElseGet(() -> ResponseEntity.notFound().build());",
            "    }",
            "",
            f'    @DeleteMapping("/{pk_field}")',
            f"    public ResponseEntity<Void> delete(@PathVariable {pk_type} {pk_field}) {{",
            f"        service.deleteById({pk_field});",
            "        return ResponseEntity.noContent().build();",
            "    }",
            "}",
            "",
            "}",
        ]
        return "\n".join(lines) + "\n"

    def _generate_application_properties(self) -> str:
        return """spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

spring.jpa.hibernate.ddl-auto=update
spring.h2.console.enabled=true
"""

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _entity_class_name(self) -> str:
        return self._pascal_case(self.table.name)

    @staticmethod
    def _camel_case(value: str) -> str:
        parts = [part for part in SpringBootCrudGenerator._split_identifier(value) if part]
        if not parts:
            return value
        first, *rest = parts
        return first.lower() + "".join(word.title() for word in rest)

    @staticmethod
    def _pascal_case(value: str) -> str:
        parts = [part for part in SpringBootCrudGenerator._split_identifier(value) if part]
        return "".join(word.title() for word in parts)

    @staticmethod
    def _kebab_case(value: str) -> str:
        parts = [part.lower() for part in SpringBootCrudGenerator._split_identifier(value) if part]
        return "-".join(parts)

    @staticmethod
    def _split_identifier(value: str) -> Iterable[str]:
        import re

        cleaned = value.replace("-", "_")
        parts: List[str] = []
        for fragment in cleaned.split("_"):
            if not fragment:
                continue
            matches = re.finditer(
                r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9]|$)",
                fragment,
            )
            for match in matches:
                parts.append(match.group(0).lower())
        return parts

    def _column_annotation(self, column: ColumnDefinition) -> Optional[str]:
        params = [f"name = \"{column.name}\""]
        if column.length is not None:
            params.append(f"length = {column.length}")
        if column.nullable:
            params.append("nullable = true")
        else:
            params.append("nullable = false")
        if column.unique:
            params.append("unique = true")
        params_text = ", ".join(params)
        return f"@Column({params_text})"

    def _generate_getter_setter(self, java_type: str, field_name: str) -> List[str]:
        pascal_field = field_name[0].upper() + field_name[1:]
        getter = (
            f"    public {java_type} get{pascal_field}() {{\n"
            f"        return {field_name};\n"
            "    }"
        )
        setter = (
            f"    public void set{pascal_field}({java_type} {field_name}) {{\n"
            f"        this.{field_name} = {field_name};\n"
            "    }"
        )
        return [getter, setter]


__all__ = [
    "ColumnDefinition",
    "TableDefinition",
    "SpringBootCrudGenerator",
]

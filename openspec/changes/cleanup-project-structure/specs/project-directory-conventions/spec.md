## ADDED Requirements

### Requirement: Directory naming convention
All project directories SHALL use lowercase letters with hyphens or underscores as word separators. Chinese characters SHALL NOT be used in directory or file names.

#### Scenario: New directory created
- **WHEN** a new directory is added to the project root
- **THEN** its name MUST be lowercase with hyphens (e.g., `my-feature/`) or underscores (e.g., `my_feature/`)

#### Scenario: Chinese directory detected
- **WHEN** a directory with Chinese characters exists in the project
- **THEN** it MUST be renamed to an English equivalent

### Requirement: Source code in src/ directory
All Python application source code SHALL reside in the `src/` directory.

#### Scenario: Python source file location
- **WHEN** a new Python module is added to the project
- **THEN** it SHALL be placed under `src/` or its subdirectories

### Requirement: SQL files in sql/ directory
All database DDL, DML, and utility SQL files SHALL reside in the `sql/` directory.

#### Scenario: SQL file location
- **WHEN** a new SQL file is added to the project
- **THEN** it SHALL be placed under `sql/`

### Requirement: Documentation in document/ directory
All project documentation SHALL reside under the `document/` directory, organized by category.

#### Scenario: Document subdirectory structure
- **WHEN** documentation is added
- **THEN** it SHALL be placed in the appropriate subdirectory: `submission/` (final deliverables), `report/` (course report), `notes/` (development notes), `references/` (external references), `images/` (document images), `dev-log/` (development log)

### Requirement: No redundant nested directories
Directory structures SHALL NOT contain redundant single-child nesting where the parent and child directories serve the same purpose.

#### Scenario: Redundant nesting detected
- **WHEN** a directory contains only one subdirectory with the same or equivalent name (e.g., `notes/notes/`)
- **THEN** the content SHALL be flattened to eliminate the redundancy

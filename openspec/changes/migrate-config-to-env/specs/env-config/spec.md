## ADDED Requirements

### Requirement: Database config read from environment

The system SHALL read MySQL database configuration from environment variables via `os.getenv`, falling back to default values when no `.env` file is present.

#### Scenario: .env file exists
- **WHEN** `.env` file is present in the project root with `DB_HOST=192.168.1.100`
- **THEN** `core.config.DB["host"]` SHALL be `"192.168.1.100"` instead of the default

#### Scenario: .env file missing
- **WHEN** `.env` file does not exist
- **THEN** all config values SHALL fall back to their defaults (`host=127.0.0.1`, `user=root`, `password=""`, `database="db_sms"`)

#### Scenario: Single source of config
- **WHEN** `import_data.py` needs database connection parameters
- **THEN** it SHALL import `DB` from `core.config` instead of defining its own `DB_CONFIG`

### Requirement: .env.example template committed

The project SHALL include an `.env.example` file committed to git as a reference for all required environment variables.

#### Scenario: New developer clones project
- **WHEN** a new developer clones the repository
- **THEN** they SHALL see `.env.example` in the root as a template to create their own `.env`

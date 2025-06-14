# Master AI Rules for SpeechDown


## Common Guidelines for All AI Assistants

**Note:** For detailed architectural decisions and rationale, refer as needed to the [current ADRs](../../adrs/current/) listed below. These records provide essential context and guidance for all guidelines in this document.

### Architecture (ADR 008)
- Follow Domain-Driven Design with four layers: **domain**, **application**, **infrastructure**, **presentation**.
- Domain layer (`src/speechdown/domain/`) contains entities and value objects only. No external dependencies.
- Application layer (`src/speechdown/application/`) defines ports (interfaces) under `application/ports/` and orchestrates use cases in `application/services/`.
- Infrastructure layer (`src/speechdown/infrastructure/`) implements adapters for ports in `infrastructure/adapters/` and may contain database code.
- Presentation layer (`src/speechdown/presentation/`) handles CLI and output.
- Dependencies point inward: infrastructure depends on application and domain, application depends on domain, and domain depends on nothing.

### Naming Conventions
- Interfaces end with `Port` (e.g., `TranscriptionPort`).
- Implementations end with `Adapter` (e.g., `WhisperTranscriberAdapter`).
- Service classes end with `Service`.
- Prefer `Service` classes in the application layer for orchestrating use cases.
- Prefer `Adapter` classes in the infrastructure layer for implementing ports.

### Testing Requirements (ADRs 002, 004, 005)
- All new code must include unit tests using **pytest**.
- Prefer function-based tests.
- Use the Arrange-Act-Assert (AAA) pattern.
- Place unit tests under `tests/unit/` and integration tests under `tests/integration/`.
- Mirror the `src` directory structure in test directories.
- Use naming convention: `test_<source_file_name>.py` for standard tests.

### Coding Standards & Security
- Use Python 3.11+ syntax with type hints and f-strings.
- Ensure PEP8 compliance; use `make format` and `make lint` for code formatting and linting.
- Use `make mypy` for type checking.
- Run `make ci` before completing feature development to ensure all checks pass.
- Never commit credentials or secrets.

### Documentation (ADR 010)
- Significant features should have a design doc in `docs/design/current/`.
- Record architectural decisions as ADRs in `docs/adrs/current/`.
- Use format `YYYY-MM-DD-feature-name.md` for design documents.

## GitHub Copilot Specific Instructions
- Copilot Chat and code completion should respect SpeechDown's layered architecture and naming conventions.
- When suggesting new classes or functions, use the proper suffixes (`Port`, `Adapter`, `Service`).
- Suggest tests for all new functionality and assume pytest and AAA style.
- Follow the security and coding standards above. No secrets or insecure patterns.

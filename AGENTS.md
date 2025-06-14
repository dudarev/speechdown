# Master AI Rules for SpeechDown

## Common Guidelines for All AI Assistants

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

### Testing Requirements (ADR 004)
- All new code must include unit tests using **pytest**.
- Prefer function-based tests.
- Use the Arrange-Act-Assert (AAA) pattern.
- Place unit tests under `tests/unit/` and integration tests under `tests/integration/`.

### Coding Standards & Security
- Use Python 3.12+ syntax with type hints and f-strings.
- Ensure PEP8 compliance; lint with `ruff` and type-check with `mypy --strict`.
- Never commit credentials or secrets.

### Documentation
- Significant features should have a design doc in `docs/design/current/`.
- Record architectural decisions as ADRs in `docs/adrs/current/`.

## GitHub Copilot Specific Instructions
- Copilot Chat and code completion should respect SpeechDown's layered architecture and naming conventions.
- When suggesting new classes or functions, use the proper suffixes (`Port`, `Adapter`, `Service`).
- Suggest tests for all new functionality and assume pytest and AAA style.
- Follow the security and coding standards above. No secrets or insecure patterns.

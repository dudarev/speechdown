# ADR 008: Project Architecture

**Date:** 2024-03-08  
**Status:** Accepted  
**Last Updated:** 2025-06-10

## Context

The SpeechDown project is evolving, and we need to formally document the overall architectural approach. We need to define clear boundaries between components, establish consistent naming conventions, and leverage established design patterns to promote modularity, testability, and extensibility.

## Decision

We will adopt a layered architecture based on **Domain-Driven Design (DDD)** principles and the **Ports and Adapters** pattern (also known as Hexagonal Architecture).

### 1. Architectural Layers

* **Domain Layer**: Contains the core business logic, entities, value objects, and domain-specific rules. Independent of any specific framework or technology.
* **Application Layer**: Orchestrates use cases through services that coordinate domain and infrastructure interactions. Defines ports (interfaces) for external dependencies.
* **Infrastructure Layer**: Provides concrete adapter implementations that fulfill the ports defined in the application layer.
* **Presentation Layer**: Handles user interaction, including CLI commands and output formatting.

### 2. Ports and Adapters Pattern

* **Ports**: Abstract interfaces defined in `application/ports/`. Each represents a capability required by the application.
* **Adapters**: Concrete implementations of ports in `infrastructure/adapters/`. Each connects a specific technology to its corresponding port.

### 3. Directory Structure

```
src/speechdown/
├── __init__.py
├── py.typed
├── main.py                # Entry point
├── presentation/         # User interface layer
│   └── cli/             # CLI implementation
│       └── commands/    # CLI command handlers
├── application/         # Use cases and business logic orchestration
│   ├── ports/          # Interfaces for external dependencies
│   └── services/       # Application services implementing use cases
├── domain/             # Core business logic and rules
│   ├── entities.py
│   └── value_objects.py
└── infrastructure/     # External dependencies implementations
    ├── database.py    # Database connectivity
    ├── schema.py      # Database schema
    └── adapters/      # Concrete implementations of ports
```

### 4. Naming Conventions

* **Ports**: Descriptive names ending in `Port` (e.g., `TranscriptionCachePort`, `TimestampPort`)
* **Adapters**: Names indicating technology and implemented port, with all adapters consistently ending in `Adapter` (e.g., `FileSystemTranscriptionCacheAdapter`, `WhisperTranscriberAdapter`, `FileTimestampAdapter`)
* **Domain Entities**: Nouns representing core concepts (e.g., `AudioFile`, `Transcription`)
* **Value Objects**: Nouns representing immutable data (e.g., `Language`, `TranscriptionMetrics`)
* **Services**: Names reflecting use cases (e.g., `TranscriptionService`)

### 5. Dependencies

* **Domain**: No external dependencies
* **Application**: Depends only on domain layer and its own ports
* **Infrastructure**: Depends on application layer (to implement ports) and domain layer
* **Presentation**: Depends on application layer

### 6. Protocol-Based Interfaces

All ports should be defined using Python's `Protocol` class to enable structural typing and improve type safety. This approach:
* Provides better IDE support and static type checking
* Allows for duck typing while maintaining explicit contracts
* Enables easier mocking in tests
* Follows modern Python typing best practices

Example:
```python
from typing import Protocol
from pathlib import Path
from datetime import datetime

class TimestampPort(Protocol):
    def get_timestamp(self, path: Path) -> datetime: ...
```

### 7. Infrastructure Layer Organization

The infrastructure layer is organized into:
* **adapters/**: Implementations of application ports
* **database.py**: Database connectivity
* **schema.py**: Database schema definitions

All concrete implementations should be adapters that implement their corresponding port interfaces to ensure consistency.

## Consequences

### Positive

* **Improved Modularity**: Clear separation of concerns for easier understanding and maintenance
* **Increased Testability**: Easy port mocking for isolated testing
* **Flexibility**: Simple to swap implementations or add new features
* **Reduced Coupling**: Dependencies point inward, protecting core domain logic
* **Clearer Boundaries**: Enforced separation between system parts
* **Better Onboarding**: Self-documenting structure for new developers
* **Naming Consistency**: Consistent naming patterns make the codebase more intuitive to navigate

### Negative

* **Initial Complexity**: More upfront design and coding effort
* **Indirection**: Slightly harder code tracing due to abstraction layers
* **Possible Overhead**: May be excessive for very small projects, though SpeechDown's size justifies this approach
* **Refactoring Effort**: Need to rename some existing files for consistency

### Additional Considerations (Updated 2025-06-10)

* **Protocol Usage**: Using `Protocol` for all ports provides better type safety and development experience
* **Consistent Adapter Pattern**: All infrastructure implementations should be adapters that implement ports, avoiding separate "service" concepts in the infrastructure layer
* **Dependency Injection**: All dependencies should be explicitly injected rather than using default factories, ensuring testability and flexibility

### Technical Debt Identified

1. **Naming Improvements**: 
   - Some adapters have TODO comments suggesting naming improvements (e.g., `AudioFileAdapter`)
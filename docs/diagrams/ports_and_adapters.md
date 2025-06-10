# Application Ports and Adapters

This diagram details the interfaces (Ports) defined within the Application Layer and their corresponding implementations (Adapters) in the Infrastructure Layer. It illustrates how the application's core logic interacts with external concerns like file systems, configuration, transcription services, and data storage through these defined contracts.

```mermaid
graph LR
    subgraph "Application Layer"
        direction TB
        P1[AudioFilePort]
        P2[ConfigPort]
        P3[OutputPort]
        P4[TranscriberPort]
        P5[TranscriptionModelPort]
        P6[TranscriptionRepositoryPort]
        P7[TimestampPort]
    end

    subgraph "Infrastructure Layer"
        direction TB
        A1[AudioFileAdapter]
        A2[ConfigAdapter]
        A3[FileOutputAdapter]
        A3b[MarkdownOutputAdapter] 
        A4[WhisperTranscriberAdapter]
        A5[WhisperModelAdapter]
        A6[SQLiteRepositoryAdapter]
        A7[FileTimestampAdapter]
    end

    P1 --> A1
    P2 --> A2
    P3 --> A3
    P3 --> A3b
    P4 --> A4
    P5 --> A5
    P6 --> A6
    P7 --> A7

    %% Dependencies between adapters
    A1 -.-> A7
    A6 -.-> A7
    A3 --> A2

    classDef portStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef adapterStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class P1,P2,P3,P4,P5,P6,P7 portStyle
    class A1,A2,A3,A3b,A4,A5,A6,A7 adapterStyle
```

## Port Descriptions

### Application Layer Ports

- **AudioFilePort**: Interface for collecting and processing audio files from the file system
- **ConfigPort**: Interface for application configuration management (languages, output directories, model settings)
- **OutputPort**: Interface for outputting transcription results in various formats  
- **TranscriberPort**: Interface for audio transcription operations
- **TranscriptionModelPort**: Interface for loading and managing transcription models
- **TranscriptionRepositoryPort**: Interface for persisting and retrieving transcription data
- **TimestampPort**: Interface for extracting timestamps from filenames or file metadata

### Infrastructure Layer Adapters

- **AudioFileAdapter**: Collects audio files from directories and creates domain entities
- **ConfigAdapter**: Manages configuration through JSON files with validation and defaults
- **FileOutputAdapter**: Outputs transcription results to markdown files
- **MarkdownOutputAdapter**: Alternative output adapter for markdown format to stdout
- **WhisperTranscriberAdapter**: Implements transcription using OpenAI Whisper
- **WhisperModelAdapter**: Manages Whisper model loading and lifecycle
- **SQLiteRepositoryAdapter**: Persists transcription data using SQLite database
- **FileTimestampAdapter**: Extracts timestamps from filenames using pattern matching

## Dependency Relationships

The diagram shows several types of relationships:

1. **Port Implementation** (solid arrows): Each adapter implements its corresponding port interface
2. **Adapter Dependencies** (dotted arrows): Some adapters depend on other adapters:
   - `AudioFileAdapter` depends on `FileTimestampAdapter` for timestamp extraction
   - `SQLiteRepositoryAdapter` depends on `FileTimestampAdapter` for file timestamp operations
   - `FileOutputAdapter` depends on `ConfigAdapter` for output configuration

## Key Architectural Benefits

- **Testability**: Each port can be easily mocked for unit testing
- **Flexibility**: Multiple implementations of the same port (e.g., different output formats)
- **Separation of Concerns**: Business logic (application layer) is isolated from technical details (infrastructure layer)
- **Dependency Inversion**: Application layer depends only on abstractions, not concrete implementations
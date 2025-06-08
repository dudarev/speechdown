# Application Ports and Adapters

This diagram details the interfaces (Ports) defined within the Application Layer and their corresponding implementations (Adapters) in the Infrastructure Layer. It illustrates how the application's core logic interacts with external concerns like file systems, configuration, transcription services, and data storage through these defined contracts.

```mermaid
graph LR
    subgraph Application Layer
        direction LR
        P1[AudioFilePort]
        P2[ConfigPort]
        P3[OutputPort]
        P4[TranscriberPort]
        P5[TranscriptionModelPort]
        P6[TranscriptionRepositoryPort]
    end

    subgraph Infrastructure Layer
        direction LR
        A1[AudioFileAdapter]
        A2[ConfigAdapter]
        A3[FileOutputAdapter]
        A3b[OutputAdapter] 
        A4[WhisperTranscriberAdapter]
        A5[WhisperModelAdapter]
        A6[SQLiteRepositoryAdapter]
    end

    P1 --> A1
    P2 --> A2
    P3 --> A3
    P3 --> A3b
    P4 --> A4
    P5 --> A5
    P6 --> A6
```
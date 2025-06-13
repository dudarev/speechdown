# AI Collaborators and Coding Assistants

This document provides quick access links and configuration information for AI coding assistants used in SpeechDown development.

## Quick Access Links

### ChatGPT (Deep Research Mode)

Comprehensive research and analysis with Linear/GitHub integration

- **Link**: [https://chatgpt.com/](https://chatgpt.com/)
- **Best for**: Research, analysis, and complex problem-solving

### Claude Code

Anthropic's coding assistant with GitHub integration

- **Link**: [https://www.anthropic.com/claude](https://www.anthropic.com/claude)
- **Best for**: Code reviews and GitHub integration tasks

### GitHub Copilot

AI pair programmer integrated with VS Code

- **Link**: [https://github.com/features/copilot](https://github.com/features/copilot)
- **Best for**: Real-time coding assistance in VS Code

### Jules (Google)

Autonomous coding agent for complex tasks

- **Link**: [https://jules.google/](https://jules.google/)
- **Best for**: Multi-file refactoring and autonomous implementation

### OpenAI Codex

Advanced coding agent with repository understanding

- **Link**: [https://chatgpt.com/codex](https://chatgpt.com/codex)
- **Best for**: Complex coding tasks with repository context

### Cursor IDE

AI-powered code editor with integrated assistance

- **Link**: [https://cursor.sh/](https://cursor.sh/)
- **Best for**: AI-powered IDE for intensive coding sessions

### Additional Resources

- **OpenAI Platform**: [https://platform.openai.com/](https://platform.openai.com/)
- **Anthropic Documentation**: [https://docs.anthropic.com/](https://docs.anthropic.com/)

## Configuration Files and Rules

Each AI assistant uses specific configuration files to understand SpeechDown's architecture and coding standards:

### Claude Code

- **Configuration File**: `CLAUDE.md`
- **Location**: Repository root
- **Purpose**: Project guidelines and commands

### OpenAI Codex

- **Configuration File**: `AGENTS.md`
- **Location**: Repository root
- **Purpose**: Agent instructions and testing requirements

### GitHub Copilot

- **Configuration File**: `copilot-instructions.md`
- **Location**: `.github/` directory
- **Purpose**: Repository-specific coding guidelines

### Cursor IDE

- **Configuration File**: `.cursorrules`
- **Location**: Repository root
- **Purpose**: IDE-specific AI behavior rules

### Jules (Google)

- **Configuration**: Prompt-based (no file)
- **Location**: N/A
- **Purpose**: Instructions included in task descriptions

### GitHub Actions Integration

- **Claude Code Action**: `.github/workflows/claude.yml` - Enables `@claude` mentions in PRs and issues
- **Copilot PR Reviews**: Automatically enabled for repository code reviews

## Architecture Guidelines for AI Assistants

All AI collaborators should follow SpeechDown's Domain-Driven Design (DDD) architecture:

### Layer Structure

- **Domain** (`src/speechdown/domain/`): Core business logic, no external dependencies
- **Application** (`src/speechdown/application/`): Use cases and port interfaces
- **Infrastructure** (`src/speechdown/infrastructure/`): Adapter implementations
- **Presentation** (`src/speechdown/presentation/`): CLI and output formatting

### Naming Conventions

- Interfaces: Suffix with `Port` (e.g., `TranscriptionPort`)
- Implementations: Suffix with `Adapter` (e.g., `WhisperTranscriberAdapter`)
- Services: Suffix with `Service` (e.g., `TranscriptionService`)

### Testing Requirements

- All new code must include unit tests using pytest
- Follow Arrange-Act-Assert (AAA) pattern
- Run `make ci` to ensure all checks pass before finalizing changes

## Usage Guidelines

### Choosing the Right Tool

#### ChatGPT

- **Use for**: Research, analysis, and complex problem-solving
- **When**: Need comprehensive research or Linear/GitHub integration

#### Claude Code

- **Use for**: Code reviews and GitHub integration tasks
- **When**: Working with PRs or need code analysis

#### GitHub Copilot

- **Use for**: Real-time coding assistance in VS Code
- **When**: Active development and need inline suggestions

#### Jules

- **Use for**: Multi-file refactoring and autonomous implementation
- **When**: Complex tasks requiring multiple file changes

#### Cursor

- **Use for**: AI-powered IDE for intensive coding sessions
- **When**: Need comprehensive AI assistance throughout development

### Development Best Practices

1. **Always specify architecture context** when working with AI assistants
2. **Review AI-generated code** for compliance with project standards
3. **Run tests** after AI-assisted changes using `make ci`

### Security Considerations

- Never include actual secrets or API keys in prompts
- Review AI suggestions for security best practices
- Use placeholder values in examples
- Ensure compliance with dependency security policies

## Maintenance

This document and associated configuration files should be updated when:

- New AI tools are adopted
- Architecture decisions change (update ADRs accordingly)
- New coding standards are established
- Security policies are modified

For detailed implementation and rule specifics, see: [`docs/research/2025-06-03-copilot-jules-claude-rules.md`](../research/2025-06-03-copilot-jules-claude-rules.md)

---

_Last updated: 2025-06-12_

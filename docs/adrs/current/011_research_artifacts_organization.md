# ADR 011: Organizing Research Artifacts

**Date:** 2025-05-19  
**Status:** Accepted

## Context

SpeechDown regularly spawns short, self-contained research exercises (e.g., evaluating algorithms, testing metadata parsing strategies, measuring performance). These tasks generate Markdown notes, throw-away scripts, and sample data. Without a clear convention, such artifacts drift into ad-hoc folders, lowering discoverability and hindering knowledge transfer.

## Decision

We will organize research artifacts with the following structure and conventions:

1. **Location**
   - All research material will live under `docs/research/`

2. **Research Document Naming**
   - Format: `docs/research/YYYY-MM-DD-brief-slug.md`
   - Prefixed with ISO date for chronological sorting in directory listings

3. **Document Template**
   ```markdown
   # <Title>
   *Status*: Active | Finished | Archived
   *Date*: <ISO date>

   ## Problem
   <why this investigation exists>

   ## Approach
   <methods, tools, hypotheses>

   ## Findings
   <results, evidence, links to scripts>

   ## Next steps
   <actions or final outcome>
   ```

4. **Scripts Directory**
   - Executable artifacts will be placed at repo root `scripts/` with matching date-prefixed folder:
   - Format: `scripts/YYYY-MM-DD-brief-slug/`
   - This keeps docs build clean
   - Mirrors the Markdown filename for 1-to-1 traceability
   - Optional `data/` subfolder for generated outputs, excluded via `.gitignore`

5. **Cross-linking**
   - The research Markdown links to its sibling scripts folder
   - Each script folder contains a README.md pointing back to the doc

## Consequences

- One predictable place to locate every experiment—developers can run `ls docs/research` or `grep` to discover prior work
- Chronological naming plus status (Active/Finished/Archived) clarifies relevance at a glance
- Docs tooling (MkDocs, GitHub Pages) automatically renders research pages, while scripts remain runnable from the CLI
- `.gitignore` prevents large or throw-away data files from bloating the repository
- Research artifacts will be more organized and accessible, improving knowledge sharing and preventing duplication of effort

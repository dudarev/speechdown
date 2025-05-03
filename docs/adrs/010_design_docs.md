# ADR 010: Introduce Markdown Design Documents for Feature Implementation

**Date:** 2025-05-03  
**Status:** Accepted

## Context

ADRs work well for recording _why_ we choose a particular architecture option, but they stay intentionally brief.  
For each non-trivial feature in SpeechDown, we still need a place to capture the detailed _how_ it works—  
UX, API shapes, data flows, edge-case handling, etc.  
Keeping that information scattered across commits or issue threads makes future maintenance harder, even for a solo developer.

## Decision

We will add **Design Documents** (DDs) to the repository with the following conventions:

- **Location** `docs/design/current/` for active work, `docs/design/archive/` for completed features
- **File naming** `YYYY-MM-DD-feature-name.md` (e.g., `2025-05-03-file-output.md`)
- **Format** lightweight Markdown template that may contain
  1. **Product Requirements** (objective, use cases, success metrics)
  2. **UX Design** (user flows, accessibility considerations)
  3. **Technical Design** (architecture diagram, data model, APIs, trade-offs)
  4. **Testing & Rollout** (validation plan, migration steps, feature flags)
  5. **Open Questions / References** (links to related ADRs, issues, research)
- **Process** Design Docs live in Git and follow the same PR/MR review workflow as code and ADRs.
- **Linkage** Design Docs reference relevant ADRs, and ADRs can point back to the Design Doc that triggered them.

## Consequences

- **Single source of truth** for feature-level details; no hunting through tickets or wikis.
- **Better change history**—reviews and edits show up in Git alongside code.
- **Clear separation of concerns**—ADRs capture long-term architecture rationale; Design Docs capture implementation specifics that may evolve.
- **Easier onboarding**—future contributors can read one file to understand both the _why_ (ADR link) and the _how_ (Design Doc).
- **Minimal overhead**—Markdown in the repo keeps the workflow simple; no extra tooling required.

## Conclusion

Design Documents complement ADRs by documenting feature-scale decisions in a structured, version-controlled way.  
Starting today, new substantial features in SpeechDown will include a Design Doc under `docs/design/`, and existing work may add one retroactively where beneficial.

# ADR 013: Use a Changelog

**Date:** 2025-06-11
**Status:** Accepted

## Context

We need a simple way to record notable changes and release information. A changelog helps users and contributors understand project history.

## Decision

Maintain a `CHANGELOG.md` file in the project root following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Update it with each change that affects users.

## References

- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- [ADR 0001 from the ytt project](https://github.com/dudarev/ytt/blob/main/docs/adrs/0001-use-changelog.md)

## Summary of Keep a Changelog 1.1.0

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) promotes clear, human-friendly release notes aligned with [Semantic Versioning](https://semver.org/). Key points:

- Changelogs list **notable changes** for each version in reverse chronological order.
- Categorize entries under headings such as **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, and **Security**.
- Every version has its own dated entry, while an **Unreleased** section tracks upcoming changes.
- Avoid raw commit logs and keep formatting consistent.


## Consequences

- Contributors must add relevant entries to the changelog as part of their pull requests.
- Release preparation becomes easier with a clear list of changes.

## Conclusion

Keeping a structured changelog improves communication and provides a single source of truth for release notes.

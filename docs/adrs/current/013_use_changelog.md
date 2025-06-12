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

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) is a standardized approach to writing changelogs that promotes clarity, consistency, and usefulness for both users and developers. It encourages a human-readable format aligned with [Semantic Versioning](https://semver.org/).

### Purpose

A changelog is a curated, chronologically ordered list of **notable changes** for each project version. Its key goals are:

- **Transparency** – Clearly communicate what has changed.
- **User awareness** – Help users and contributors understand the impact of changes.
- **Upgrade support** – Make transitions between versions smoother.

### Core Principles

- Changelogs are **for humans**, not machines.
- **Every version** should have its own entry with meaningful detail.
- **Categorize changes** by type (e.g. Added, Fixed, Changed).
- Use **reverse chronological order** – newest versions at the top.
- Include the **release date** for each version.
- Maintain a clear and consistent format across entries.
- Recommend using **Semantic Versioning**.

### Standard Change Categories

Use the following headings to classify changes:

- **Added** – for new features.
- **Changed** – for changes in existing functionality.
- **Deprecated** – for soon-to-be-removed features.
- **Removed** – for now-removed features.
- **Fixed** – for any bug fixes.
- **Security** – for vulnerabilities addressed.

### Use of the `Unreleased` Section

Include an `Unreleased` section at the top to:

- Track upcoming changes.
- Make release preparation easier.
- Offer transparency about what’s planned or being worked on.

### What to Avoid

- **Raw commit logs** – they are noisy and not user-friendly.
- **Unnoted deprecations** – always inform users about features that will be removed.
- **Inconsistent formatting or missing entries** – these reduce trust in the changelog.

### Benefits

Adopting the _Keep a Changelog_ format results in:

- Better communication across teams and with users.
- More maintainable and professional documentation.
- Fewer upgrade surprises due to clearly described changes.

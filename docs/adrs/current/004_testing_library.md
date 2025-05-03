# ADR 004: Decision on Testing Library

**Date:** 2025-03-02
**Status:** Accepted

## Context

To ensure the reliability and maintainability of the SpeechDown project, we need to select a suitable testing library for unit testing. We want to promote modularity and readability in our tests.

## Decision

We will use pytest as our testing library. We will favor:
- Functions over classes for test organization.
- Modularized asserts to improve readability.
- Organizing tests by files to enhance maintainability.
- Following the Arrange-Act-Assert (AAA) pattern in our tests.

## Consequences

- More readable and maintainable unit tests.
- Easier collaboration and understanding of test logic.
- Consistent testing approach across the project.

## Conclusion

pytest, combined with our preferred testing style, will provide a robust and maintainable testing framework for the SpeechDown project.

## Links

- [Arrange-Act-Assert: A Pattern for Writing Good Tests | Automation Panda](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/)
- [Unit Testing and the Arrange, Act and Assert (AAA) Pattern | by Paulo Gomes | Medium](https://medium.com/@pjbgf/title-testing-code-ocd-and-the-aaa-pattern-df453975ab80)
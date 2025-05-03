# ADR 005: Integration Test Structure

**Date:** 2025-03-04
**Status:** Accepted  

## Context

While unit tests (as defined in [ADR 002](002_unit_test_structure.md)) focus on testing individual components in isolation by mocking external dependencies, integration tests serve a different purpose. We need to establish a clear structure for integration tests that:

1. Tests the interaction between multiple modules or components
2. Verifies that integrated components work together as expected
3. May include actual calls to external dependencies rather than mocks
4. Remains discoverable and follows a consistent pattern

Integration tests differ from unit tests in that they verify behavior across component boundaries, which can include:
- Integration between multiple internal modules
- Integration with external systems and dependencies
- End-to-end workflows that span multiple components

## Decision

We will adopt a structure for integration tests that mirrors our approach for unit tests:

1. Place all integration tests under `tests/integration` directory
2. Mirror the `src` directory structure in `tests/integration`
3. Use the following naming conventions:
   - Standard tests: `test_<primary_module>_integration.py`
   - Specific integration scenario tests: `test_<primary_module>_integration__<scenario>.py`
4. Each test will primarily focus on a "main module under test," even though multiple modules may be involved
5. Create a dedicated Makefile command `test-integration` to run integration tests
6. Integration tests will not be executed as part of the standard `ci` command unless explicitly specified

## Consequences

### Positive
- Maintains consistency with our unit testing structure
- Provides a clear location for tests that cross module boundaries
- Allows developers to easily find integration tests for specific modules
- Supports the testing of real external dependencies when appropriate
- Enables testing of module interactions without excessive mocking
- Separating integration tests from the CI pipeline ensures faster CI runs
- Developers can explicitly run integration tests when needed

### Negative
- May require additional test infrastructure to handle external dependencies
- Some tests might be slower due to actual external calls
- Could require maintenance when external dependencies change
- Integration boundaries might not always clearly map to a single primary module
- Manual execution of integration tests might lead to them being run less frequently

## Conclusion

This structured approach to integration testing complements our unit testing strategy while addressing the distinct needs of testing component interactions. By maintaining a parallel structure to unit tests, we ensure consistency and discoverability while acknowledging the different scope and purpose of integration tests. The separate Makefile command provides developers control over when to run these potentially slower tests.

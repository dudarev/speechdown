"""
To enable tests discovery in VSCODE, we need to add the following to settings.json:
```json
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests", "--run-integration", "--run-slow"],
```
"""

import pytest


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as a slow test")


def pytest_addoption(parser):
    """Add command line options for test selection."""
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")
    parser.addoption(
        "--run-integration", action="store_true", default=False, help="run integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration and slow tests unless explicitly requested."""
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")

    # Skip slow tests if --run-slow not provided
    if not config.getoption("--run-slow"):
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    # Skip integration tests if --run-integration not provided
    if not config.getoption("--run-integration"):
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

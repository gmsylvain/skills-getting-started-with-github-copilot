"""
Pytest configuration and shared fixtures for the test suite.

This module provides common test fixtures and configuration
that can be used across all test modules.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="session")
def test_client():
    """
    Create a test client for the FastAPI application.
    Session-scoped to avoid creating multiple clients.
    """
    return TestClient(app)


# Pytest configuration
pytest_plugins = []

# Configure test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def api_key_header() -> dict[str, str]:
    """Standard API key header for gateway tests."""
    return {"X-Api-Key": "dev-api-key-change-in-prod"}


@pytest.fixture
def api_key() -> str:
    """API key value."""
    return "dev-api-key-change-in-prod"

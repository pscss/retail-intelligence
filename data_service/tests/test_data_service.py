"""Unit tests for data service."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health() -> None:
    """Health endpoint returns healthy status."""
    with (
        patch(
            "data_service.main.SeedProducts", return_value=AsyncMock(run=AsyncMock())
        ),
        patch("data_service.main.SeedFaqs", return_value=AsyncMock(run=AsyncMock())),
        patch("data_service.main.command.upgrade"),
    ):
        from data_service.main import app

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "data-service"
    assert response.json()["status"] == "healthy"
